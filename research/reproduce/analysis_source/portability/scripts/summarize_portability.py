#!/usr/bin/env python3
"""Summarize locked cross-track endpoint predictions without new hypothesis tests."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import statistics
import tempfile

TOLERANCES = (0.0, 1e-6, 1e-5)
PRIMARY = 1e-6


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def top(values, tolerance):
    threshold = max(values) - tolerance
    return [i for i, value in enumerate(values) if value >= threshold]


def credit(values, selected, tolerance):
    winners = top(values, tolerance)
    return Fraction(int(selected in winners), len(winners))


def ranks(lower, upper, tolerance):
    return {
        'possible_top_members': [i for i in range(3) if upper[i] >= max(lower) - tolerance],
        'necessary_top_members': [i for i in range(3)
            if lower[i] >= max(upper[j] for j in range(3) if j != i) - tolerance],
        'guaranteed_unique_leaders': [i for i in range(3)
            if lower[i] > max(upper[j] for j in range(3) if j != i) + tolerance],
    }


def assess_prediction(prediction, actual_top):
    possible = set(prediction['possible_top_members'])
    necessary = set(prediction['necessary_top_members'])
    unique = prediction['guaranteed_unique_leaders']
    contradiction = bool(unique) and unique != actual_top
    return {'unique_leader_contradicted': contradiction,
            'possible_top_set_failure': not set(actual_top) <= possible,
            'necessary_top_set_failure': not necessary <= set(actual_top),
            'any_failure': contradiction or not set(actual_top) <= possible or not necessary <= set(actual_top)}


def analyze_site(record, comparator, tolerance):
    native = record['representations']['native']['distances']
    centered = record['representations']['centered']['distances']
    prediction = record['native_prediction']
    stored = prediction['by_tolerance'][str(tolerance)]
    low = prediction['lower']
    strong_low = prediction['strengthened_lower']
    high = prediction['upper']
    actual_top = top(centered, tolerance)
    native_top = top(native, tolerance)
    derived = {'simple': ranks(low, high, tolerance),
               'strengthened': ranks(strong_low, high, tolerance)}
    formula_agrees = derived == stored
    validations = {name: assess_prediction(value, actual_top) for name, value in stored.items()}
    simple = stored['simple']['guaranteed_unique_leaders']
    strong = stored['strengthened']['guaranteed_unique_leaders']
    gain = bool(strong) and not simple
    loss = bool(simple) and strong != simple
    interval_failures = [i for i in range(3) if not (low[i] <= centered[i] <= high[i]
                                                    and strong_low[i] <= centered[i] <= high[i])]
    scores = {'native': native, 'centered': centered, **record['baselines']}
    selected = record['selected_allele_index']
    credits = {name: credit(value, selected, tolerance) for name, value in scores.items()}
    old_native = comparator['representations']['native']['distances']
    old_centered = comparator['representations']['centered']['distances']
    old_scores = {'native': old_native, 'centered': old_centered, **comparator['baselines']}
    return {
        'site_id': record['site_id'], 'site_index': record['site_index'], 'gene': record['gene'],
        'native_top_set': native_top, 'centered_top_set': actual_top,
        'simple_predicted_unique_leader': simple, 'strengthened_predicted_unique_leader': strong,
        'additional_leader': gain, 'lost_simple_decision': loss,
        'strengthened_possible_top_set': stored['strengthened']['possible_top_members'],
        'strengthened_necessary_top_set': stored['strengthened']['necessary_top_members'],
        'prediction_formula_agrees': formula_agrees,
        'interval_failure_alternate_indices': interval_failures,
        'prediction_validation': validations,
        'any_validation_failure': bool(interval_failures) or not formula_agrees
            or any(v['any_failure'] for v in validations.values()),
        'native_tied': len(native_top) > 1, 'centered_tied': len(actual_top) > 1,
        'tie_resolved': len(native_top) > 1 and len(actual_top) == 1,
        'tie_introduced': len(native_top) == 1 and len(actual_top) > 1,
        'strict_native_leader_preserved': len(native_top) == 1 and native_top == actual_top,
        'strict_native_leader_replaced': len(native_top) == 1 and len(actual_top) == 1 and native_top != actual_top,
        'strict_native_leader_loses_top_membership': len(native_top) == 1 and native_top[0] not in actual_top,
        'centered_leader_outside_native_top': not set(actual_top) <= set(native_top),
        'selected_credit_fractions': {name: str(value) for name, value in credits.items()},
        'baseline_top_set_agreement_with_centered': {name: top(value, tolerance) == actual_top for name, value in scores.items()},
        'cross_track_native_top_agreement': native_top == top(old_native, tolerance),
        'cross_track_centered_top_agreement': actual_top == top(old_centered, tolerance),
        'cross_track_baseline_top_agreement': {name: top(value, tolerance) == top(old_scores[name], tolerance)
                                             for name, value in scores.items() if name in old_scores},
        'comparator_credit_fractions': {name: str(credit(value, comparator['selected_allele_index'], tolerance))
                                       for name, value in old_scores.items()},
    }


def aggregate(rows, n_planned):
    n = len(rows)
    result = {'n_observed_sites': n, 'n_planned_sites': n_planned, 'missing_sites': n_planned - n}
    if n == 0:
        return {**result, 'status': 'no_observed_sites'}
    names = list(rows[0]['selected_credit_fractions'])
    old_names = list(rows[0]['comparator_credit_fractions'])
    sums = {name: sum((Fraction(r['selected_credit_fractions'][name]) for r in rows), Fraction(0)) for name in names}
    old_sums = {name: sum((Fraction(r['comparator_credit_fractions'][name]) for r in rows), Fraction(0)) for name in old_names}
    for key in ('additional_leader', 'lost_simple_decision', 'any_validation_failure',
                'native_tied', 'centered_tied', 'tie_resolved', 'tie_introduced',
                'strict_native_leader_preserved', 'strict_native_leader_replaced',
                'strict_native_leader_loses_top_membership', 'centered_leader_outside_native_top',
                'cross_track_native_top_agreement', 'cross_track_centered_top_agreement'):
        result[key + '_sites'] = sum(bool(r[key]) for r in rows)
    simple = sum(bool(r['simple_predicted_unique_leader']) for r in rows)
    strong = sum(bool(r['strengthened_predicted_unique_leader']) for r in rows)
    missing = n_planned - n
    result.update({
        'simple_unique_leaders': simple, 'strengthened_unique_leaders': strong,
        'net_coverage_increment_sites': strong - simple,
        'additional_leader_genes': sorted({r['gene'] for r in rows if r['additional_leader']}),
        'unresolved_observed_sites': n - strong,
        'simple_coverage_all_planned': simple / n_planned if n_planned else None,
        'strengthened_coverage_all_planned': strong / n_planned if n_planned else None,
        'additional_coverage_all_planned': result['additional_leader_sites'] / n_planned if n_planned else None,
        'missingness_coverage_bounds': {
            'simple': [simple / n_planned, (simple + missing) / n_planned],
            'strengthened': [strong / n_planned, (strong + missing) / n_planned],
            'additional': [result['additional_leader_sites'] / n_planned,
                           (result['additional_leader_sites'] + missing) / n_planned]},
        'interval_failure_pairs': sum(len(r['interval_failure_alternate_indices']) for r in rows),
        'prediction_formula_mismatch_sites': sum(not r['prediction_formula_agrees'] for r in rows),
        'simple_unique_leader_contradictions': sum(r['prediction_validation']['simple']['unique_leader_contradicted'] for r in rows),
        'strengthened_unique_leader_contradictions': sum(r['prediction_validation']['strengthened']['unique_leader_contradicted'] for r in rows),
        'top_set_validation_failures': sum(v['possible_top_set_failure'] or v['necessary_top_set_failure']
                                         for r in rows for v in r['prediction_validation'].values()),
        'strengthened_possible_set_size_counts': {str(k): sum(len(r['strengthened_possible_top_set']) == k for r in rows) for k in (0, 1, 2, 3)},
        'strengthened_necessary_set_size_counts': {str(k): sum(len(r['strengthened_necessary_top_set']) == k for r in rows) for k in (0, 1, 2, 3)},
        'baseline_mean_selected_credit': {name: float(value / n) for name, value in sums.items()},
        'baseline_mean_selected_credit_exact_fractions': {name: str(value / n) for name, value in sums.items()},
        'comparator_baseline_mean_selected_credit': {name: float(value / n) for name, value in old_sums.items()},
        'paired_centered_minus_native_credit': float((sums['centered'] - sums['native']) / n),
        'paired_centered_minus_native_credit_exact_fraction': str((sums['centered'] - sums['native']) / n),
        'baseline_top_set_agreement_with_centered': {name: sum(r['baseline_top_set_agreement_with_centered'][name] for r in rows) for name in names},
        'cross_track_baseline_top_agreement': {name: sum(r['cross_track_baseline_top_agreement'].get(name, False) for r in rows)
                                             for name in rows[0]['cross_track_baseline_top_agreement']},
    })
    return result


def criteria(summary, full_cohort):
    no_failure = summary.get('any_validation_failure_sites') == 0
    positive = summary.get('additional_leader_sites', 0) > 0
    no_loss = summary.get('lost_simple_decision_sites') == 0
    genes = len(summary.get('additional_leader_genes', []))
    technical = full_cohort and no_failure and positive
    operational = technical and summary['additional_leader_sites'] >= 17 and genes >= 4 and no_loss
    return {
        'full_planned_cohort_complete': full_cohort,
        'technical_nontrivial_transfer': 'INCOMPLETE' if not full_cohort else ('PASS' if technical else 'FAIL'),
        'technical_components': {'zero_validation_failures': no_failure, 'positive_additional_coverage': positive},
        'operational_utility_benchmark': 'INCOMPLETE' if not full_cohort else ('PASS' if operational else 'FAIL'),
        'operational_components': {'at_least_17_additional_leaders': summary.get('additional_leader_sites', 0) >= 17,
                                   'gains_in_at_least_4_genes': genes >= 4, 'no_lost_simple_decisions': no_loss,
                                   'zero_validation_failures': no_failure},
        'threshold_origin': '17 sites is half the earlier GM12878 34-site increment; frozen utility benchmark, not a statistical or clinical threshold.',
    }


def quantiles(values):
    if not values:
        return {}
    import numpy as np
    return {str(q): float(np.quantile(values, q)) for q in (0, .5, .9, .95, .99, 1)}


def secondary(records, full_cohort):
    pairs = [p for r in records for p in r['pair_diagnostics']]
    residuals = [abs(abs(p['centered_distance'] - p['native_distance']) - abs(p['delta'])) for p in pairs]
    shifts = [abs(p['delta']) for p in pairs]
    tiny = [i for i, s in enumerate(shifts) if s <= 1e-10]
    non_tiny = [i for i, s in enumerate(shifts) if s > 1e-10]
    failures = [i for i in non_tiny if residuals[i] > 1e-10]
    midpoints = [p['midpoint_check'] for p in pairs if 'midpoint_check' in p]
    return {
        'n_pairs': len(pairs), 'saturated_pairs_1e10': sum(x <= 1e-10 for x in residuals),
        'saturated_pairs_1e12': sum(x <= 1e-12 for x in residuals),
        'zero_shift_pairs': sum(x == 0 for x in shifts), 'tiny_shift_pairs_1e10': len(tiny),
        'non_tiny_pairs': len(non_tiny), 'non_tiny_nonsaturated_pairs_1e10': len(failures),
        'universal_non_tiny_saturation': 'FAIL' if failures else ('PASS' if full_cohort and non_tiny else 'INCOMPLETE'),
        'residual_quantiles': quantiles(residuals), 'absolute_shift_quantiles': quantiles(shifts),
        'increasing_pairs': sum(p['centered_distance'] > p['native_distance'] for p in pairs),
        'decreasing_pairs': sum(p['centered_distance'] < p['native_distance'] for p in pairs),
        'unchanged_pairs': sum(p['centered_distance'] == p['native_distance'] for p in pairs),
        'direct_midpoint_checks': len(midpoints),
        'midpoint_affine_failures': sum(not p['affine_agreement_passed'] for p in midpoints),
        'midpoint_tube_failures': sum(not p['endpoint_tube_passed'] for p in midpoints),
        'maximum_midpoint_chord_error': max((p['absolute_error'] for p in midpoints), default=None),
        'maximum_ph_input_rounding_bound': max((p['per_distance_ph_input_rounding_bound'] for p in pairs), default=None),
        'interpretation': 'Only endpoints and the frozen direct midpoint checks are evaluated; no intermediate ranking is inferred from a chord.',
    }


def verify_inputs(directory, comparator_path, comparator_manifest_path):
    source_path = directory / 'anchor_replication_summary.json'
    source = read(source_path)
    lock_path = directory / 'native_predictions_lock.json'
    lock = read(lock_path)
    if source['native_predictions_lock_sha256'] != sha(lock_path):
        raise ValueError('Source native-lock digest mismatch')
    for artifact in lock['artifacts']:
        if sha(directory / artifact['path']) != artifact['sha256']:
            raise ValueError('Changed locked native artifact: ' + artifact['path'])
    native = read(directory / 'native_predictions.json')
    native_lookup = {r['site_id']: r for r in native['records']}
    for record in source['records']:
        frozen = native_lookup[record['site_id']]
        if record['native_prediction'] != frozen['native_prediction']:
            raise ValueError('Centered record differs from frozen prediction: ' + record['site_id'])
        if record['representations']['native'] != frozen['representations']['native'] or record['means'] != frozen['means']:
            raise ValueError('Native quantities changed after lock: ' + record['site_id'])
        full = record['full_diagram_artifact']
        path = Path(full['path'])
        path = path if path.is_absolute() else directory / path
        if sha(path) != full['sha256']:
            raise ValueError('Centered per-site artifact digest mismatch')
    manifest_path = directory / 'manifest.json'
    manifest = read(manifest_path)
    if sha(manifest_path) != source['provenance']['manifest_sha256']:
        raise ValueError('Acquisition manifest changed')
    comparator = read(comparator_path)
    comparator_manifest = read(comparator_manifest_path)
    new_sites = {s['site_id']: s for s in manifest['sites']}
    old_sites = {s['site_id']: s for s in comparator_manifest['sites']}
    if not set(new_sites) <= set(old_sites):
        raise ValueError('Comparator is missing planned paired sites')
    for site_id, new in new_sites.items():
        old = old_sites[site_id]
        for key in ('alleles', 'selected_allele_index', 'bin_coordinates', 'gene'):
            if new[key] != old[key]:
                raise ValueError('Paired comparator ' + key + ' mismatch at ' + site_id)
    return source, manifest, comparator, comparator_manifest, lock


def summarize(source, manifest, comparator):
    records = source['records']
    old_lookup = {r['site_id']: r for r in comparator['records']}
    if any(r['site_id'] not in old_lookup for r in records):
        raise ValueError('Missing paired comparator record')
    n_planned = len(manifest['sites'])
    if source['n_planned_sites'] != n_planned:
        raise ValueError('Planned count mismatch')
    genes = sorted({s['gene'] for s in manifest['sites']})
    planned_by_gene = Counter(s['gene'] for s in manifest['sites'])
    full = len(records) == n_planned and source['n_failed_sites'] == 0
    by_tolerance = {}
    for tolerance in TOLERANCES:
        rows = [analyze_site(r, old_lookup[r['site_id']], tolerance) for r in records]
        totals = aggregate(rows, n_planned)
        by_tolerance[str(tolerance)] = {
            'summary': totals, 'criteria': criteria(totals, full),
            'per_gene': {g: aggregate([r for r in rows if r['gene'] == g], planned_by_gene[g]) for g in genes},
            'leave_one_gene_out': {g: aggregate([r for r in rows if r['gene'] != g], n_planned - planned_by_gene[g]) for g in genes},
            'sites': rows,
        }
    return {
        'artifact_type': 'paired_cross_track_portability_summary',
        'scope': 'Descriptive, prospectively locked AlphaGenome cross-track audit on already studied loci; not an independent-model or new-locus validation.',
        'track': manifest['track'], 'biosample': manifest.get('biosample'),
        'primary_tie_tolerance': PRIMARY, 'n_planned_sites': n_planned, 'n_observed_sites': len(records),
        'n_genes': len(genes), 'primary': by_tolerance[str(PRIMARY)], 'by_tolerance': by_tolerance,
        'secondary': secondary(records, full), 'inferential_tests_added': 0,
        'clinical_discrimination_or_runtime_superiority_claimed': False,
        'uncompleted_by_this_script': ['Acquisition and metadata audit', 'Server-drift comparator adjudication',
                                      'Cross-track map differences and input-grid precision diagnostics',
                                      'Independent biological/clinical validation'],
    }


def markdown(result):
    summary = result['primary']['summary']
    fixed = result['primary']['criteria']
    second = result['secondary']
    n = result['n_observed_sites']
    planned = result['n_planned_sites']
    lines = ['# Paired cross-track portability results', '',
        f"Track: {result['biosample']} ({result['track']}); {n}/{planned} planned sites across {result['n_genes']} previously studied loci.", '',
        f"Frozen technical nontrivial-transfer criterion: **{fixed['technical_nontrivial_transfer']}**. Frozen operational utility benchmark: **{fixed['operational_utility_benchmark']}**.", '',
        f"At the primary 1e-6 tie tolerance, simple bounds identify {summary['simple_unique_leaders']} leaders and strengthened bounds identify {summary['strengthened_unique_leaders']}. The witness adds {summary['additional_leader_sites']} decisions across {len(summary['additional_leader_genes'])} genes, loses {summary['lost_simple_decision_sites']} simple decisions, and leaves {summary['unresolved_observed_sites']} observed sites unresolved. There are {summary['any_validation_failure_sites']} sites with interval, top-set or unique-leader validation failures.", '',
        'The operational benchmark was fixed before acquisition: at least 17 additional decisions, gains in at least four genes, no lost simple decisions and no validation failures, with the full planned cohort complete. It is a selected utility benchmark, not a clinical threshold or powered hypothesis test.', '',
        '| Tie tolerance | Simple leaders | Strengthened leaders | Additional | Gains across genes | Contradicted strengthened leaders | Unresolved |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for tolerance, row in result['by_tolerance'].items():
        s = row['summary']
        lines.append(f"| {tolerance} | {s['simple_unique_leaders']} | {s['strengthened_unique_leaders']} | {s['additional_leader_sites']} | {len(s['additional_leader_genes'])} | {s['strengthened_unique_leader_contradictions']} | {s['unresolved_observed_sites']} |")
    lines += ['', '| Gene | Sites | Simple leaders | Strengthened leaders | Additional | Centered minus native selected credit |', '|---|---:|---:|---:|---:|---:|']
    for gene, s in result['primary']['per_gene'].items():
        if s['n_observed_sites']:
            lines.append(f"| {gene} | {s['n_observed_sites']} | {s['simple_unique_leaders']} | {s['strengthened_unique_leaders']} | {s['additional_leader_sites']} | {s['paired_centered_minus_native_credit']:.6f} |")
    loo = result['primary']['leave_one_gene_out']
    increments = [x['additional_leader_sites'] for x in loo.values() if x['n_observed_sites']]
    lines += ['', f"Leave-one-gene-out additional-leader counts range from {min(increments)} to {max(increments)}.", '',
        f"Native ties: {summary['native_tied_sites']}; centered ties: {summary['centered_tied_sites']}; ties resolved: {summary['tie_resolved_sites']}; ties introduced: {summary['tie_introduced_sites']}. Strict native leaders preserved: {summary['strict_native_leader_preserved_sites']}; replaced by a different strict leader: {summary['strict_native_leader_replaced_sites']}; sites with any centered leader outside the native top set: {summary['centered_leader_outside_native_top_sites']}.", '',
        '| Fixed score | New-track selected credit | Comparator selected credit | Top-set agreement with new centered endpoint |', '|---|---:|---:|---:|']
    for name, value in summary['baseline_mean_selected_credit'].items():
        old = summary['comparator_baseline_mean_selected_credit'].get(name)
        old_text = f'{old:.6f}' if old is not None else 'not available'
        lines.append(f"| {name} | {value:.6f} | {old_text} | {summary['baseline_top_set_agreement_with_centered'][name]}/{n} |")
    lines += ['', f"New-track centered-minus-native selected credit is {summary['paired_centered_minus_native_credit']:.6f}. Paired cross-track top sets agree at {summary['cross_track_native_top_agreement_sites']}/{n} sites for native scores and {summary['cross_track_centered_top_agreement_sites']}/{n} sites for centered scores. These are descriptive results, not clinical-accuracy estimates or independent-sample significance tests.", '',
        f"Numerical endpoint saturation: {second['saturated_pairs_1e10']}/{second['n_pairs']} at 1e-10 and {second['saturated_pairs_1e12']}/{second['n_pairs']} at 1e-12. There are {second['tiny_shift_pairs_1e10']} tiny shifts, including {second['zero_shift_pairs']} exact zero shifts; {second['non_tiny_nonsaturated_pairs_1e10']} non-tiny comparisons fail saturation. Universal non-tiny saturation status: {second['universal_non_tiny_saturation']}.", '',
        f"The frozen direct midpoint set supplies {second['direct_midpoint_checks']} checks: {second['midpoint_affine_failures']} chord discrepancies and {second['midpoint_tube_failures']} endpoint-envelope failures. Maximum chord discrepancy: {second['maximum_midpoint_chord_error']}. No unmeasured intermediate ranking is inferred from an affine chord.", '',
        'The native predictions were locked before centered bottleneck distances were evaluated. Numerical guarantees remain conditional on practical arithmetic allowances. Successful transfer concerns another output track of the same model, not a new architecture, untouched clinical holdout or physical chromatin validation. Runtime is recorded for reproduction; no speed advantage is claimed.', '',
        'The paired comparator must be selected according to the contemporaneous GM12878 drift audit. Raw-map differences, repeated-reference checks and input-grid diagnostics are separate audit artifacts; this summary does not certify them.', '']
    return '\n'.join(lines)


def figure(result, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    s = result['primary']['summary']
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    blue, orange = '#286b9a', '#bf672c'
    axes[0].bar(['Simple\nbounds', 'Strengthened\nbounds'],
                [s['simple_unique_leaders'], s['strengthened_unique_leaders']], color=[blue, orange])
    axes[0].set(ylabel='Unique leaders identified', ylim=(0, result['n_planned_sites']),
                title='A  Locked audit predictions')
    x = [0, 1]
    old = s['comparator_baseline_mean_selected_credit']
    new = s['baseline_mean_selected_credit']
    axes[1].bar([v-.18 for v in x], [old['native'], old['centered']], width=.36, color=blue, label='GM12878 comparator')
    axes[1].bar([v+.18 for v in x], [new['native'], new['centered']], width=.36, color=orange, label=result['biosample'])
    axes[1].set(xticks=x, xticklabels=['Native', 'Centered'], ylabel='Descriptive selected-allele credit',
                ylim=(0, 1), title='B  Selected-allele agreement')
    axes[1].legend(frameon=False, fontsize=8)
    axes[2].bar(['Native', 'Centered'], [s['native_tied_sites'], s['centered_tied_sites']], color=[blue, orange])
    axes[2].set(ylabel='Sites with tied top alternatives', ylim=(0, result['n_planned_sites']),
                title='C  Ranking decisiveness')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis='y', alpha=.18)
    fig.suptitle(f"Paired cross-track portability: {result['n_observed_sites']}/{result['n_planned_sites']} sites; tolerance 10⁻⁶", fontsize=12)
    fig.text(.5, .015, 'Numerical model-output audit; no clinical or independent biological validation.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .045, 1, .94))
    fig.savefig(path, dpi=200, bbox_inches='tight')
    fig.savefig(Path(path).with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)


def self_test():
    # The following controls test interpretation rules without inspecting genomic outputs.
    assert top([1, 1, 0], 0) == [0, 1]
    assert credit([1, 1, 0], 1, 0) == Fraction(1, 2)
    assert ranks([0, 0, 0], [1, 1, 1], 1e-6)['guaranteed_unique_leaders'] == []
    assert ranks([2, 0, 0], [3, 1, 1], 1e-6)['guaranteed_unique_leaders'] == [0]
    wrong = {'possible_top_members': [2], 'necessary_top_members': [2], 'guaranteed_unique_leaders': [2]}
    assert assess_prediction(wrong, [0])['any_failure']
    base = {'any_validation_failure_sites': 0, 'additional_leader_sites': 17,
            'lost_simple_decision_sites': 0, 'additional_leader_genes': ['a', 'b', 'c', 'd']}
    assert criteria(base, True)['operational_utility_benchmark'] == 'PASS'
    assert criteria({**base, 'additional_leader_sites': 16}, True)['operational_utility_benchmark'] == 'FAIL'
    assert criteria({**base, 'additional_leader_genes': ['a', 'b', 'c']}, True)['operational_utility_benchmark'] == 'FAIL'
    assert criteria({**base, 'any_validation_failure_sites': 1}, True)['technical_nontrivial_transfer'] == 'FAIL'
    assert criteria({**base, 'additional_leader_sites': 0}, True)['technical_nontrivial_transfer'] == 'FAIL'
    assert criteria(base, False)['technical_nontrivial_transfer'] == 'INCOMPLETE'
    assert criteria(base, False)['operational_utility_benchmark'] == 'INCOMPLETE'
    print(json.dumps({'status': 'PASS', 'checks': 12,
                      'scope': 'Known-answer ranking and frozen criterion boundary controls; no genomic outputs read.'}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory', type=Path)
    p.add_argument('--comparator', type=Path)
    p.add_argument('--comparator-manifest', type=Path)
    p.add_argument('--figure', action='store_true')
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.directory or not args.comparator:
        p.error('--directory and --comparator are required')
    comparator_manifest = args.comparator_manifest or args.comparator.parent / 'manifest.json'
    source, manifest, comparator, old_manifest, lock = verify_inputs(args.directory, args.comparator, comparator_manifest)
    result = summarize(source, manifest, comparator)
    result['comparator_track'] = old_manifest['track']
    result['comparator_biosample'] = old_manifest.get('biosample')
    result['provenance'] = {'script_sha256': sha(__file__),
        'source_summary_sha256': sha(args.directory / 'anchor_replication_summary.json'),
        'native_predictions_sha256': sha(args.directory / 'native_predictions.json'),
        'native_lock_sha256': sha(args.directory / 'native_predictions_lock.json'),
        'native_locked_utc': lock['frozen_utc'], 'manifest_sha256': sha(args.directory / 'manifest.json'),
        'comparator_summary_path': str(args.comparator.resolve()), 'comparator_summary_sha256': sha(args.comparator),
        'comparator_manifest_sha256': sha(comparator_manifest), 'protocol_sha256': source['provenance']['protocol_sha256']}
    dump(args.directory / 'portability_summary.json', result)
    (args.directory / 'PORTABILITY_RESULTS.md').write_text(markdown(result))
    if args.figure:
        figure(result, args.directory / 'portability_results.png')
    print(json.dumps({'primary': result['primary']['summary'], 'criteria': result['primary']['criteria'],
                      'secondary': result['secondary']}, indent=2))
    if result['primary']['summary'].get('any_validation_failure_sites', 0):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
