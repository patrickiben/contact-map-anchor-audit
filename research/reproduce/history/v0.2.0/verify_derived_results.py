#!/usr/bin/env python3
"""Independent standard-library reconstruction of scalar-derived study claims.

Does not rerun persistent homology, nearest-neighbor witnesses or model inference.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def leaders(lower, upper, tolerance):
    return [i for i in range(3) if all(lower[i] > upper[j] + tolerance for j in range(3) if i != j)]


def top(scores, tolerance):
    return [i for i, x in enumerate(scores) if x >= max(scores) - tolerance]


def fractional(scores, selected, tolerance):
    winners = top(scores, tolerance)
    return Fraction(int(selected in winners), len(winners))


def reconstruct(records, tolerance, allowance):
    rows = []
    for r in records:
        low = [max(0.0, b - abs(d)) - allowance for b, d in zip(r['native'], r['deltas'])]
        high = [b + abs(d) + allowance for b, d in zip(r['native'], r['deltas'])]
        strong = [max(max(0.0, b - abs(d)), h) - allowance
                  for b, d, h in zip(r['native'], r['deltas'], r['shifted_hausdorff'])]
        assert low == r['locked_lower'] and high == r['locked_upper'] and strong == r['locked_strengthened_lower']
        assert all(l <= s <= u for l, s, u in zip(strong, r['centered'], high))
        native_top, centered_top = top(r['native'], tolerance), top(r['centered'], tolerance)
        simple, strengthened = leaders(low, high, tolerance), leaders(strong, high, tolerance)
        stored = r['locked_rank_sets'][str(tolerance)]
        for name, lower, unique in [('simple', low, simple), ('strengthened', strong, strengthened)]:
            possible = [i for i in range(3) if high[i] >= max(lower) - tolerance]
            necessary = [i for i in range(3) if lower[i] >= max(high[j] for j in range(3) if j != i) - tolerance]
            assert stored[name] == dict(possible_top_members=possible, necessary_top_members=necessary, guaranteed_unique_leaders=unique)
            assert set(centered_top).issubset(possible) and set(necessary).issubset(centered_top)
            assert not unique or unique == centered_top
        assert not simple or simple == strengthened
        scores = dict(native=r['native'], centered=r['centered'], **r['baselines'])
        credits = {name: fractional(value, r['selected_allele_index'], tolerance) for name, value in scores.items()}
        rows.append(dict(gene=r['gene'], simple=bool(simple), strong=bool(strengthened),
                         gain=bool(strengthened) and not simple, native_tie=len(native_top)>1,
                         centered_tie=len(centered_top)>1, resolved=len(native_top)>1 and len(centered_top)==1,
                         preserved=len(native_top)==1 and native_top==centered_top, credits=credits))
    return rows


def aggregate(rows):
    result = {'n_observed_sites': len(rows), 'simple_unique_leaders': sum(r['simple'] for r in rows),
        'strengthened_unique_leaders': sum(r['strong'] for r in rows),
        'additional_leader_sites': sum(r['gain'] for r in rows),
        'additional_leader_genes': sorted({r['gene'] for r in rows if r['gain']}),
        'native_tied_sites': sum(r['native_tie'] for r in rows),
        'centered_tied_sites': sum(r['centered_tie'] for r in rows),
        'tie_resolved_sites': sum(r['resolved'] for r in rows),
        'strict_native_leader_preserved_sites': sum(r['preserved'] for r in rows)}
    result['baseline_mean_selected_credit_exact_fractions'] = {
        key: str(sum((r['credits'][key] for r in rows), Fraction()) / len(rows)) for key in rows[0]['credits']}
    result['paired_centered_minus_native_credit_exact_fraction'] = str(
        sum((r['credits']['centered']-r['credits']['native'] for r in rows), Fraction()) / len(rows))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    args = parser.parse_args()
    data = read(args.data_dir / 'endpoint_scalars.json')
    expected = read(args.data_dir / 'expected_results.json')
    records = data['records']
    assert len(records) == 84 and sorted(r['site_index'] for r in records) == list(range(84))
    allowance = data['practical_allowance']
    results = {}
    checks = 0
    for tol in [0.0, 1e-6, 1e-5]:
        rows = reconstruct(records, tol, allowance)
        summary = aggregate(rows)
        exp = expected['by_tolerance'][str(tol)]
        for key, value in summary.items():
            assert exp['summary'][key] == value, (tol, key)
            checks += 1
        for gene in sorted({r['gene'] for r in rows}):
            for selection, scope in [([r for r in rows if r['gene']==gene], 'per_gene'),
                                     ([r for r in rows if r['gene']!=gene], 'leave_one_gene_out')]:
                for key, value in aggregate(selection).items():
                    assert exp[scope][gene][key] == value, (tol, scope, gene, key)
                    checks += 1
        results[str(tol)] = summary
    residuals = [abs(abs(c-b)-abs(d)) for r in records for b,c,d in zip(r['native'],r['centered'],r['deltas'])]
    assert sum(x <= 1e-10 for x in residuals) == 249
    assert max(residuals) == expected['secondary']['residual_quantiles']['1']
    exceptions = [(r['site_index'],i) for r in records for i,(b,c,d) in enumerate(zip(r['native'],r['centered'],r['deltas'])) if abs(abs(c-b)-abs(d))>1e-10]
    path_data = read(args.data_dir / 'exploratory_path_scalars.json')['comparisons']
    assert sorted(exceptions) == sorted((r['site_index'],r['alternate_index']) for r in path_data)
    path_results = []
    for path in path_data:
        magnitude = abs(path['delta'])
        b, c = path['native_distance'], path['centered_distance']
        departures = []
        assert [r['lambda'] for r in path['grid']] == [0.0, .1, .25, .5, .75, .9, 1.0]
        for point in path['grid']:
            lam, value = point['lambda'], point['distance']
            lower = max(0., b-lam*magnitude, c-(1-lam)*magnitude)-allowance
            upper = min(b+lam*magnitude,c+(1-lam)*magnitude)+allowance
            assert lower <= value <= upper
            departures.append(abs(value-((1-lam)*b+lam*c)))
        # Algebraically equivalent chord expressions can differ by an ulp.
        assert abs(max(departures) - path['maximum_absolute_chord_departure']) <= 1e-14
        path_results.append({'site_index':path['site_index'],'maximum_chord_departure':max(departures)})
    output = {'status':'PASS_DERIVED_RESULTS_ONLY', 'aggregate_value_comparisons':checks,
              'sites':84,'pairs':252,'tolerances':3,'saturated_pairs':249,'nonsaturated_pairs':3,
              'by_tolerance':results,'exploratory_paths':path_results,
              'scope':'Reconstructs bound arithmetic, rank sets, rational credits, gene sensitivity and sampled envelopes from scalar inputs; no PH, witness-distance or model inference recomputation.',
              'input_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(args.data_dir.glob('*.json'))}}
    rendered=json.dumps(output,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(rendered)
    print(json.dumps({'status':output['status'],'aggregate_value_comparisons':checks,'sites':84,'pairs':252,'primary_simple':7,'primary_strengthened':49,'additional':42,'saturated':249}))


if __name__ == '__main__':
    main()
