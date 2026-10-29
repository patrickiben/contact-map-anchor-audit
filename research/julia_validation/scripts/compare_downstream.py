#!/usr/bin/env python3
"""Propagate Julia diagrams through the declared downstream checks.

This is an independently written comparison driver. It imports no production
analysis code. GUDHI/Hera is deliberately the shared matching solver: this is
not independent validation of the bottleneck algorithm itself. Only start after
the separately reported primary persistence and controls gates have succeeded.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
from gudhi import hera
from scipy.spatial.distance import cdist

J = Path(__file__).resolve().parents[1]
B = J.parent
TOLERANCES = (0.0, 1e-6, 1e-5)
ALLOWANCE = 1e-12
SITE_INDICES = (7, 21, 34, 44, 48, 51, 59, 70, 75)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True,
                                    allow_nan=False) + '\n')
    temporary.replace(path)


def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else J / path


class Checks:
    def __init__(self):
        self.rows = []

    def exact(self, name, actual, expected):
        passed = actual == expected
        self.rows.append({'name': name, 'passed': bool(passed),
                          'actual': actual, 'expected': expected,
                          'comparison': 'exact'})
        return passed

    def close(self, name, actual, expected, tolerance=ALLOWANCE):
        actual_array = np.asarray(actual, dtype=float)
        expected_array = np.asarray(expected, dtype=float)
        shape_ok = actual_array.shape == expected_array.shape
        finite = bool(np.isfinite(actual_array).all()
                      and np.isfinite(expected_array).all())
        error = (float(np.max(np.abs(actual_array - expected_array)))
                 if shape_ok and actual_array.size and finite else
                 0.0 if shape_ok and not actual_array.size else None)
        passed = shape_ok and finite and error is not None and error <= tolerance
        self.rows.append({'name': name, 'passed': bool(passed),
                          'actual': actual_array.tolist(),
                          'expected': expected_array.tolist(),
                          'maximum_absolute_error': error,
                          'absolute_tolerance': tolerance})
        return passed

    @property
    def passed(self):
        return all(row['passed'] for row in self.rows)


def top_and_credit(scores, tolerance):
    highest = max(scores)
    members = [index for index, score in enumerate(scores)
               if score >= highest - tolerance]
    fractions = [1.0 / len(members) if i in members else 0.0
                 for i in range(len(scores))]
    return members, fractions


def interval_ranking(lower, upper, tolerance):
    possible, necessary, unique = [], [], []
    for i in range(len(lower)):
        other_lower = [lower[j] for j in range(len(lower)) if j != i]
        other_upper = [upper[j] for j in range(len(lower)) if j != i]
        if upper[i] >= max(other_lower) - tolerance:
            possible.append(i)
        if lower[i] >= max(other_upper) - tolerance:
            necessary.append(i)
        if lower[i] > max(other_upper) + tolerance:
            unique.append(i)
    return {'possible_top_members': possible,
            'necessary_top_members': necessary,
            'guaranteed_unique_leaders': unique}


def validate_ranking(prediction, actual):
    possible_ok = set(actual) <= set(prediction['possible_top_members'])
    necessary_ok = set(prediction['necessary_top_members']) <= set(actual)
    unique = prediction['guaranteed_unique_leaders']
    unique_ok = not unique or unique == actual
    return {'actual_top_set': actual, 'possible_contains_actual': possible_ok,
            'necessary_contained_in_actual': necessary_ok,
            'unique_agrees': unique_ok,
            'passed': possible_ok and necessary_ok and unique_ok}


def bottleneck(left, right):
    if np.array_equal(left, right):
        return 0.0
    return float(hera.bottleneck_distance(left, right, delta=0.0))


def brute_hausdorff(left, right, block_size):
    """Symmetric L-infinity nearest-neighbor lower bound, including diagonal.

    Every pair of off-diagonal points is explicitly compared once. The full
    multiset is retained. A point can match its own orthogonal projection onto
    the diagonal at cost half its lifetime. No tree or production witness code
    is used. This lower bound ignores bijective matching constraints.
    """
    left_nearest = np.full(len(left), np.inf)
    right_nearest = np.full(len(right), np.inf)
    for start in range(0, len(left), block_size):
        stop = min(start + block_size, len(left))
        if not len(right):
            break
        distances = cdist(left[start:stop], right, metric='chebyshev')
        left_nearest[start:stop] = np.min(distances, axis=1)
        np.minimum(right_nearest, np.min(distances, axis=0), out=right_nearest)
    left_cost = np.minimum(left_nearest, (left[:, 1] - left[:, 0]) / 2)
    right_cost = np.minimum(right_nearest, (right[:, 1] - right[:, 0]) / 2)
    left_max = float(np.max(left_cost)) if len(left_cost) else 0.0
    right_max = float(np.max(right_cost)) if len(right_cost) else 0.0
    side = 'reference' if left_max >= right_max else 'shifted_alternate'
    costs, points = (left_cost, left) if side == 'reference' else (right_cost, right)
    index = int(np.argmax(costs)) if len(costs) else None
    return max(left_max, right_max), {
        'source': side, 'index_in_sorted_diagram': index,
        'point': points[index].tolist() if index is not None else None,
        'reference_directed_maximum': left_max,
        'shifted_alternate_directed_maximum': right_max,
        'off_diagonal_point_pairs_compared': len(left) * len(right),
        'block_size': block_size,
    }


def preflight(record, expected, checks):
    key = record['key']
    path = J / 'outputs/genomic' / (key + '.f64')
    receipt_path = path.with_suffix('.json')
    receipt = load(receipt_path)
    data = np.fromfile(path, dtype='<f8')
    if data.size % 2:
        raise ValueError('Odd number of interval coordinates: ' + key)
    diagram = data.reshape((-1, 2), order='F')
    reference = np.asarray(expected['representations']['native']
                           ['h1_diagrams_ref_then_alts']
                           [record['expected_diagram_index']], dtype=float).reshape(-1, 2)
    reference = reference[np.lexsort((reference[:, 1], reference[:, 0]))]
    checks.exact(key + '.receipt_status', receipt['status'], 'completed')
    checks.exact(key + '.receipt_key', receipt['key'], key)
    checks.exact(key + '.n', receipt['n'], record['n'])
    checks.exact(key + '.raw_sha256', receipt['raw_sha256'], record['raw_sha256'])
    checks.exact(key + '.raw_file_sha256', sha(resolve(record['raw_path'])), record['raw_sha256'])
    checks.exact(key + '.effective_sha256', receipt['effective_sha256'], record['expected_effective_sha256'])
    checks.exact(key + '.offset', receipt['offset'], record['expected_offset'])
    checks.exact(key + '.output_sha256', sha(path), receipt['output_sha256'])
    checks.exact(key + '.interval_count_receipt', len(diagram), receipt['interval_count'])
    checks.exact(key + '.interval_count_reference', len(diagram), record['expected_interval_count'])
    checks.exact(key + '.finite_positive', bool(np.isfinite(diagram).all()
                 and np.all(diagram[:, 1] > diagram[:, 0])), True)
    checks.exact(key + '.lexicographic_sort', bool(np.array_equal(diagram,
                 diagram[np.lexsort((diagram[:, 1], diagram[:, 0]))])), True)
    checks.exact(key + '.complete_multiset_equal', bool(np.array_equal(diagram, reference)), True)
    raw = np.fromfile(resolve(record['raw_path']), dtype='<f8').reshape((record['n'], record['n']), order='F')
    mean = float(np.mean(raw[np.triu_indices(record['n'], 1)], dtype=np.float64))
    expected_mean = record['means'][record['expected_diagram_index']]
    checks.close(key + '.independent_mean', mean, expected_mean)
    checks.close(key + '.julia_receipt_mean', receipt['mean'], expected_mean)
    return diagram, {'key': key, 'path': str(path), 'sha256': sha(path),
                     'receipt_path': str(receipt_path), 'receipt_sha256': sha(receipt_path),
                     'interval_count': len(diagram), 'independently_recomputed_mean': mean}


def compare_site(task):
    records, output, block_size, gm_witness, gm_ranking = task
    started = time.monotonic()
    key = records[0]['track'] + '_site_' + f"{records[0]['site_index']:03d}"
    outpath = Path(output) / 'sites' / (key + '.json')
    checks = Checks()
    result = {'key': key, 'track': records[0]['track'],
              'site_index': records[0]['site_index'], 'started_utc': utc()}
    try:
        print('Downstream starting ' + key, flush=True)
        expected_path = resolve(records[0]['expected_diagram'])
        expected = load(expected_path)
        result.update({'site_id': expected['site_id'], 'gene': expected['gene'],
                       'reference_result_path': str(expected_path),
                       'reference_result_sha256': sha(expected_path)})
        for r in records:
            checks.exact(r['key'] + '.reference_result_hash', sha(resolve(r['expected_diagram'])),
                         r['expected_diagram_sha256'])
            checks.exact(r['key'] + '.means_in_manifest', r['means'], expected['means'])
            checks.exact(r['key'] + '.reference_path', r['expected_diagram'], records[0]['expected_diagram'])
        diagrams, inputs = [], []
        for r in records:
            d, provenance = preflight(r, expected, checks)
            diagrams.append(d)
            inputs.append(provenance)
        result['julia_diagrams'] = inputs
        if not checks.passed:
            raise ValueError('Input, receipt or primary-diagram preflight failed; no matching performed')

        means = expected['means']
        native = [bottleneck(diagrams[0], diagram) for diagram in diagrams[1:]]
        centered_diagrams = [diagram + mean for diagram, mean in zip(diagrams, means)]
        centered = [bottleneck(centered_diagrams[0], diagram) for diagram in centered_diagrams[1:]]
        result['native_distances'] = native
        result['centered_distances'] = centered
        scores_by_representation = {'native': native, 'centered': centered}
        result['ranking_and_credit'] = {}
        for name, scores in scores_by_representation.items():
            recorded = expected['representations'][name]
            checks.close(name + '.distances', scores, recorded['distances'])
            result['ranking_and_credit'][name] = {}
            for tolerance in TOLERANCES:
                t = str(tolerance)
                actual_top, credit = top_and_credit(scores, tolerance)
                expected_top, _ = top_and_credit(recorded['distances'], tolerance)
                checks.exact(name + '.top_set.' + t, actual_top, expected_top)
                checks.exact(name + '.fractional_credit.' + t, credit, recorded['credits_by_tolerance'][t])
                selected = expected['selected_allele_index']
                result['ranking_and_credit'][name][t] = {
                    'top_set': actual_top, 'fractional_credit': credit,
                    'selected_allele_index': selected, 'selected_allele_credit': credit[selected]}

        shifts = [means[i + 1] - means[0] for i in range(3)]
        witness_values, witness_rows, diagnostics = [], [], []
        for i in range(3):
            magnitude = abs(shifts[i])
            witness_value, detail = brute_hausdorff(diagrams[0], diagrams[i + 1] + shifts[i], block_size)
            witness_values.append(witness_value)
            increasing = magnitude > 1e-10 and abs(witness_value - native[i] - magnitude) <= ALLOWANCE
            reference_witness = (expected['native_prediction']['witnesses'][i]
                                 if records[0]['track'] == 'imr90' else gm_witness[i])
            checks.close(f'pair{i}.shifted_hausdorff', witness_value,
                         reference_witness['shifted_hausdorff_lower_bound'])
            branch_key = ('increasing_branch_predicted' if records[0]['track'] == 'imr90'
                          else 'increasing_branch_certified_before_comparison')
            checks.exact(f'pair{i}.increasing_branch_prediction', increasing, reference_witness[branch_key])
            checks.exact(f'pair{i}.hausdorff_below_centered_distance', witness_value <= centered[i] + ALLOWANCE, True)
            witness_rows.append({'alternate_index': i, 'shifted_hausdorff_lower_bound': witness_value,
                                 'increasing_branch_predicted': increasing, 'brute_force_detail': detail})
            change = centered[i] - native[i]
            direction = 1 if change >= 0 else -1
            residual = abs(magnitude - abs(change))
            deficit = magnitude - direction * change
            row = {'alternate_index': i, 'delta': shifts[i], 'native_distance': native[i],
                   'centered_distance': centered[i], 'absolute_saturation_residual': residual,
                   'signed_saturation_deficit': deficit, 'endpoint_direction': direction,
                   'numerically_saturated_at_1e12': residual <= 1e-12,
                   'numerically_saturated_at_primary_1e10': residual <= 1e-10,
                   'tiny_shift_at_1e10': magnitude <= 1e-10,
                   'conservative_deficit_upper_bound': max(0.0, deficit + 2e-12)}
            reference_pair = expected['pair_diagnostics'][i]
            for field in ('delta', 'native_distance', 'centered_distance',
                          'absolute_saturation_residual', 'signed_saturation_deficit',
                          'conservative_deficit_upper_bound'):
                checks.close(f'pair{i}.' + field, row[field], reference_pair[field])
            for field in ('endpoint_direction', 'numerically_saturated_at_1e12',
                          'numerically_saturated_at_primary_1e10', 'tiny_shift_at_1e10'):
                checks.exact(f'pair{i}.' + field, row[field], reference_pair[field])
            diagnostics.append(row)
        result['shifted_hausdorff_witnesses'] = witness_rows
        result['pair_diagnostics'] = diagnostics

        simple_lower = [max(0.0, native[i] - abs(shifts[i])) - ALLOWANCE for i in range(3)]
        upper = [native[i] + abs(shifts[i]) + ALLOWANCE for i in range(3)]
        strong_lower = [max(0.0, native[i] - abs(shifts[i]), witness_values[i]) - ALLOWANCE for i in range(3)]
        result['bounds'] = {'lower': simple_lower, 'upper': upper, 'strengthened_lower': strong_lower}
        if records[0]['track'] == 'imr90':
            stored = expected['native_prediction']
            for field in ('lower', 'upper', 'strengthened_lower'):
                checks.close('interval_bounds.' + field, result['bounds'][field], stored[field])
        else:
            for name, field in [('lower', 'native_only_lower'), ('upper', 'native_only_upper'),
                                ('strengthened_lower', 'hausdorff_strengthened_lower')]:
                checks.close('interval_bounds.' + name, result['bounds'][name], gm_ranking[field])
        score_bounds_passed = all(strong_lower[i] <= centered[i] <= upper[i] for i in range(3))
        checks.exact('interval_bounds.contain_centered_scores', score_bounds_passed, True)
        result['bound_rankings'] = {}
        for tolerance in TOLERANCES:
            t = str(tolerance)
            actual_top, _ = top_and_credit(centered, tolerance)
            result['bound_rankings'][t] = {}
            for method, lower in [('simple', simple_lower), ('strengthened', strong_lower)]:
                prediction = interval_ranking(lower, upper, tolerance)
                validation = validate_ranking(prediction, actual_top)
                result['bound_rankings'][t][method] = {'prediction': prediction, 'validation': validation}
                checks.exact('ranking_bound_valid.' + t + '.' + method, validation['passed'], True)
                if records[0]['track'] == 'imr90':
                    reference_prediction = expected['native_prediction']['by_tolerance'][t][method]
                    checks.exact('recorded_ranking_prediction.' + t + '.' + method, prediction, reference_prediction)
                    checks.exact('locked_prediction_validation.' + t + '.' + method, validation,
                                 expected['locked_prediction_validation']['by_tolerance'][t][method])
                elif tolerance == 1e-6:
                    field = ('stability_only_partial_ranking' if method == 'simple'
                             else 'hausdorff_strengthened_partial_ranking')
                    checks.exact('recorded_ranking_prediction.' + t + '.' + method, prediction, gm_ranking[field])
            if records[0]['track'] == 'gm12878' and tolerance == 1e-6:
                checks.exact('gm_stored_centered_top_set', actual_top, gm_ranking['centered_top_set_for_validation'])
        result['status'] = 'passed' if checks.passed else 'failed'
    except Exception as exc:
        result.update({'status': 'failed', 'error_type': type(exc).__name__,
                       'error': str(exc), 'traceback': traceback.format_exc()})
    result.update({'checks': checks.rows, 'checks_count': len(checks.rows),
                   'failed_checks': [c for c in checks.rows if not c['passed']],
                   'elapsed_seconds': time.monotonic() - started, 'completed_utc': utc()})
    dump(outpath, result)
    print('Downstream ' + result['status'] + ' ' + key, flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=J / 'inputs/genomic_manifest.json')
    parser.add_argument('--output-dir', type=Path, default=J / 'outputs/downstream')
    parser.add_argument('--study-root', type=Path, default=B,
                        help='Root containing original anchor_method and portability_imr90 artifacts.')
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--block-size', type=int, default=256)
    parser.add_argument('--primary-success-confirmed', action='store_true', required=True,
                        help='Explicit gate: separately reviewed primary controls and genomic diagrams passed.')
    args = parser.parse_args()
    started = time.monotonic()
    declaration = load(args.manifest)
    records = declaration if isinstance(declaration, list) else declaration['records']
    groups = {}
    for record in records:
        groups.setdefault((record['track'], record['site_index']), []).append(record)
    expected_groups = {(track, index) for track in ('gm12878', 'imr90') for index in SITE_INDICES}
    if set(groups) != expected_groups or len(records) != 72:
        raise ValueError('Manifest differs from frozen nine-site/two-track/72-diagram target')
    if len({r['key'] for r in records}) != 72:
        raise ValueError('Duplicate diagram key')
    for group in groups.values():
        group.sort(key=lambda r: r['allele_index'])
        if [r['allele_index'] for r in group] != [-1, 0, 1, 2]:
            raise ValueError('REF/ALT group incomplete')
        if [r['expected_diagram_index'] for r in group] != [0, 1, 2, 3]:
            raise ValueError('Unexpected reference diagram indices')
    gm_witness_path = args.study_root / 'anchor_method/replication/hausdorff_branch_certificate.json'
    gm_rank_path = args.study_root / 'anchor_method/replication/native_interval_ranking.json'
    gm_pairs = load(gm_witness_path)['pairs']
    gm_sites = load(gm_rank_path)['sites']
    witness_lookup = {(p['site_id'], p['alternate_index']): p for p in gm_pairs}
    rank_lookup = {s['site_id']: s for s in gm_sites}
    metadata = {
        'started_utc': utc(), 'command': sys.argv, 'python_executable': sys.executable,
        'script_sha256': sha(__file__), 'protocol_sha256': sha(J / 'PROTOCOL.md'),
        'manifest_sha256': sha(args.manifest),
        'gm_witness_reference_sha256': sha(gm_witness_path),
        'gm_ranking_reference_sha256': sha(gm_rank_path),
        'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                        'numpy': importlib.metadata.version('numpy'),
                        'scipy': importlib.metadata.version('scipy'),
                        'gudhi': importlib.metadata.version('gudhi')},
        'shared_matching_solver': {'name': 'gudhi.hera.bottleneck_distance', 'delta': 0.0,
            'scope': 'Recomputed on Julia-produced diagrams. This is the same matching solver used in the original analysis, not an independent bottleneck algorithm.'},
        'hausdorff_implementation': 'Independent explicit blockwise all-pairs L-infinity nearest neighbors with diagonal alternatives; no production witness implementation imported.',
        'floating_comparison_absolute_tolerance': ALLOWANCE,
        'top_set_tolerances': list(TOLERANCES),
        'rank_bound_allowance': ALLOWANCE, 'saturation_primary_tolerance': 1e-10,
        'saturation_sensitivity_tolerance': 1e-12, 'means_absolute_tolerance': ALLOWANCE,
        'rank_comparisons': 'GM12878 recorded interval/ranking predictions are available at 1e-6 only; all three top-set/credit tolerances and independently reconstructed interval predictions are evaluated. IMR90 recorded predictions are compared at all three tolerances.',
        'workers': args.workers, 'block_size': args.block_size,
    }
    dump(args.output_dir / 'run_metadata.json', metadata)
    tasks = []
    for (_, _), group in sorted(groups.items()):
        site = group[0]['site_id']
        witness = [witness_lookup[(site, i)] for i in range(3)] if group[0]['track'] == 'gm12878' else None
        rank = rank_lookup[site] if group[0]['track'] == 'gm12878' else None
        tasks.append((group, str(args.output_dir), args.block_size, witness, rank))
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(compare_site, task) for task in tasks]
        for future in as_completed(futures):
            results.append(future.result())
            dump(args.output_dir / 'progress.json', {
                'completed_sites': len(results), 'expected_sites': 18,
                'failed_sites': [r['key'] for r in results if r['status'] != 'passed'], 'utc': utc()})
    results.sort(key=lambda r: r['key'])
    nonsaturated = [{'track': r['track'], 'site_index': r['site_index'],
                    'site_id': r['site_id'], 'alternate_index': p['alternate_index'],
                    'absolute_saturation_residual': p['absolute_saturation_residual']}
                   for r in results for p in r.get('pair_diagnostics', [])
                   if not p['numerically_saturated_at_primary_1e10']]
    observed_exceptions = sorted((r['track'], r['site_index'], r['alternate_index']) for r in nonsaturated)
    expected_exceptions = [('imr90', 48, 2), ('imr90', 51, 1), ('imr90', 59, 0)]
    passed = all(r['status'] == 'passed' for r in results) and observed_exceptions == expected_exceptions
    summary = {
        **metadata, 'status': 'passed' if passed else 'failed',
        'site_track_count': len(results), 'diagram_count': sum(len(r.get('julia_diagrams', [])) for r in results),
        'ref_alt_pair_count': sum(len(r.get('pair_diagnostics', [])) for r in results),
        'checks_count': sum(r['checks_count'] for r in results),
        'failed_sites': [r['key'] for r in results if r['status'] != 'passed'],
        'nonsaturated_pairs': nonsaturated,
        'all_and_only_three_declared_exceptions': observed_exceptions == expected_exceptions,
        'maximum_distance_absolute_error': max((c['maximum_absolute_error']
            for r in results for c in r['checks']
            if c['name'] in ('native.distances', 'centered.distances')
            and c['maximum_absolute_error'] is not None), default=None),
        'maximum_shifted_hausdorff_absolute_error': max((c['maximum_absolute_error']
            for r in results for c in r['checks'] if c['name'].endswith('.shifted_hausdorff')
            and c['maximum_absolute_error'] is not None), default=None),
        'results': [{'key': r['key'], 'status': r['status'],
                     'result_path': str(args.output_dir / 'sites' / (r['key'] + '.json')),
                     'result_sha256': sha(args.output_dir / 'sites' / (r['key'] + '.json')),
                     'failed_checks_count': len(r['failed_checks'])} for r in results],
        'elapsed_seconds': time.monotonic() - started, 'completed_utc': utc(),
    }
    dump(args.output_dir / 'summary.json', summary)
    print(json.dumps({k: summary[k] for k in ('status', 'site_track_count', 'diagram_count',
          'ref_alt_pair_count', 'checks_count', 'failed_sites', 'all_and_only_three_declared_exceptions',
          'maximum_distance_absolute_error', 'maximum_shifted_hausdorff_absolute_error', 'elapsed_seconds')}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
