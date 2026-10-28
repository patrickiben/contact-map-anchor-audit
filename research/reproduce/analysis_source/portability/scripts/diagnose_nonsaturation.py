#!/usr/bin/env python3
"""Post-result direct path queries for every frozen nonsaturation exception."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time

import numpy as np
from gudhi import hera

ROOT = Path(__file__).resolve().parents[1]
GRID = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)
ALLOWANCE = 1e-12
EXPECTED = [(48, 2), (51, 1), (59, 0)]


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def envelope(a, c, magnitude, lam):
    return [max(a-lam*magnitude, c-(1-lam)*magnitude)-ALLOWANCE,
            min(a+lam*magnitude, c+(1-lam)*magnitude)+ALLOWANCE]


def evaluate(task):
    record, alternate, lock_sha = task
    native_path = ROOT / 'native' / f"site_{record['site_index']:03d}.json"
    native = read(native_path)
    ds = native['representations']['native']['h1_diagrams_ref_then_alts']
    ref = np.asarray(ds[0], dtype=float).reshape(-1, 2)
    alt = np.asarray(ds[alternate+1], dtype=float).reshape(-1, 2)
    delta = native['means'][alternate+1] - native['means'][0]
    magnitude = abs(delta)
    a = record['representations']['native']['distances'][alternate]
    c = record['representations']['centered']['distances'][alternate]
    points = []
    for lam in GRID:
        started = time.monotonic()
        stamp = utc()
        shifted = alt + lam*delta
        actual = 0.0 if np.array_equal(ref, shifted) else float(hera.bottleneck_distance(ref, shifted, delta=0.0))
        chord = a + lam*(c-a)
        low, high = envelope(a, c, magnitude, lam)
        points.append({'lambda': lam, 'distance': actual, 'endpoint_chord': chord,
                       'signed_chord_departure': actual-chord,
                       'absolute_chord_departure': abs(actual-chord),
                       'lipschitz_lower': low, 'lipschitz_upper': high,
                       'envelope_passed': low <= actual <= high,
                       'queried_utc': stamp, 'elapsed_seconds': time.monotonic()-started})
    changes = [b['distance']-a['distance'] for a, b in zip(points, points[1:])]
    positive = any(x > ALLOWANCE for x in changes)
    negative = any(x < -ALLOWANCE for x in changes)
    shape = ('sampled_direction_change' if positive and negative else
             'nondecreasing_on_sampled_grid' if positive else
             'nonincreasing_on_sampled_grid' if negative else 'flat_on_sampled_grid_at_1e12')
    maximum = max(x['absolute_chord_departure'] for x in points)
    start_error = abs(points[0]['distance']-a)
    end_error = abs(points[-1]['distance']-c)
    locked = native['native_prediction']['by_tolerance']
    vertices = [0.0, 1.0]
    if magnitude:
        vertices += [x for x in ((a-c+magnitude)/(2*magnitude), (c+magnitude-a)/(2*magnitude)) if 0 < x < 1]
    vertices = sorted(set(vertices))
    return {
        'site_id': record['site_id'], 'site_index': record['site_index'], 'gene': record['gene'],
        'alternate_index': alternate, 'native_distance': a, 'centered_distance': c,
        'delta': delta, 'endpoint_saturation_residual': abs(magnitude-abs(c-a)),
        'native_artifact_sha256': sha(native_path), 'native_predictions_lock_sha256': lock_sha,
        'grid': points, 'sampled_step_changes': changes, 'sampled_shape': shape,
        'maximum_absolute_chord_departure': maximum,
        'chord_departure_detected_at_1e10': maximum > 1e-10,
        'chord_departure_detected_at_1e12': maximum > 1e-12,
        'endpoint_agreement_errors': {'lambda0': start_error, 'lambda1': end_error},
        'endpoint_agreement_passed': start_error <= ALLOWANCE and end_error <= ALLOWANCE,
        'envelope_failures': sum(not p['envelope_passed'] for p in points),
        'locked_predictions_by_tolerance': locked,
        'abstention_by_tolerance': {t: {name: not bool(prediction['guaranteed_unique_leaders'])
                                      for name, prediction in predictions.items()}
                                   for t, predictions in locked.items()},
        'analytical_envelope_vertices': [{'lambda': x, 'lower': envelope(a, c, magnitude, x)[0],
                                           'upper': envelope(a, c, magnitude, x)[1]} for x in vertices],
        'interpretation': 'Post-result sampled-path diagnostic; no statement about every unmeasured lambda or matching identity.'}


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, record in zip(axes, result['comparisons']):
        vertices = record['analytical_envelope_vertices']
        ax.fill_between([p['lambda'] for p in vertices], [p['lower'] for p in vertices],
                        [p['upper'] for p in vertices], color='#c6ddec', alpha=.7, label='Endpoint envelope')
        ax.plot([0, 1], [record['native_distance'], record['centered_distance']], '--', color='#888888', label='Endpoint chord')
        ax.scatter([p['lambda'] for p in record['grid']], [p['distance'] for p in record['grid']],
                   color='#a14824', s=28, zorder=3, label='Direct path queries')
        ax.set(xlabel='Anchor interpolation λ', ylabel='Bottleneck distance', xlim=(0, 1),
               title=f"{record['site_id']}\nAlternate index {record['alternate_index']}")
        ax.ticklabel_format(axis='y', style='plain', useOffset=False)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].legend(frameon=False, fontsize=7, loc='best')
    fig.suptitle('Post-result diagnostic: all three IMR-90 nonsaturation exceptions', fontsize=12)
    fig.text(.5, .015, 'Exploratory selection after endpoint results; dots are direct evaluations, not a measured continuous trajectory.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, .92))
    fig.savefig(ROOT / 'post_result_path_diagnostics.png', dpi=200, bbox_inches='tight')
    fig.savefig(ROOT / 'post_result_path_diagnostics.pdf', bbox_inches='tight')
    plt.close(fig)


def markdown(result):
    lines = ['# Post-result path diagnostic', '',
        '**Exploratory analysis selected after the primary endpoint results.** All three nonsaturating comparisons were included; no extremes-only subset was selected. The main protocol, cohort, predictions and pass/fail criteria were unchanged.', '',
        'Direct GUDHI/Hera evaluations used λ = 0, 0.1, 0.25, 0.5, 0.75, 0.9, 1 on the previously locked native diagrams.', '',
        '| Site | Alternate index | Sampled shape | Maximum chord departure | Endpoint agreement | Envelope failures | Simple / strengthened abstain at 1e-6 |',
        '|---|---:|---|---:|---|---:|---|']
    for record in result['comparisons']:
        abstain = record['abstention_by_tolerance']['1e-06']
        lines.append(f"| {record['site_id']} | {record['alternate_index']} | {record['sampled_shape']} | {record['maximum_absolute_chord_departure']:.9g} | {record['endpoint_agreement_passed']} | {record['envelope_failures']} | {abstain['simple']} / {abstain['strengthened']} |")
    lines += ['', 'Each case retained its previously locked possible/necessary/unique-leader predictions. The diagnostic did not retune the audit or turn an abstention into a claimed decision.', '',
        'Nonsaturation is distinct from nonlinearity: a nearly constant path can fail endpoint saturation while agreeing with its endpoint chord. A direction change observed on this grid establishes a change among the sampled values, but the exact breakpoint and behavior between samples are not identified.', '',
        'The plotted envelopes use their analytical line-intersection vertices, avoiding interpolation artifacts. Numerical agreement is conditional on the stated practical 1e-12 allowance; this is not a formal real-arithmetic certificate.', '']
    for record in result['comparisons']:
        lines += [f"## {record['site_id']}, alternate index {record['alternate_index']}", '',
                  '| λ | Direct distance | Signed chord departure | Envelope passed |', '|---:|---:|---:|---|']
        for point in record['grid']:
            lines.append(f"| {point['lambda']} | {point['distance']:.12g} | {point['signed_chord_departure']:.9g} | {point['envelope_passed']} |")
        lines.append('')
    return '\n'.join(lines)


def main():
    source_path = ROOT / 'anchor_replication_summary.json'
    protocol = ROOT / 'POST_RESULT_PATH_PROTOCOL.md'
    source = read(source_path)
    lock_path = ROOT / 'native_predictions_lock.json'
    lock = read(lock_path)
    for artifact in lock['artifacts']:
        if sha(ROOT / artifact['path']) != artifact['sha256']:
            raise ValueError('Changed locked native artifact')
    selected = [(r, q['alternate_index']) for r in source['records'] for q in r['pair_diagnostics']
                if abs(q['delta']) > 1e-10 and q['absolute_saturation_residual'] > 1e-10]
    if [(r['site_index'], a) for r, a in selected] != EXPECTED:
        raise ValueError('All-exception selection differs from written post-result protocol')
    freeze_path = ROOT / 'post_result_path_execution_freeze.json'
    fixed = {'protocol_sha256': sha(protocol), 'script_sha256': sha(__file__),
             'source_summary_sha256': sha(source_path), 'native_predictions_lock_sha256': sha(lock_path),
             'selected_pairs': EXPECTED, 'lambda_grid': GRID,
             'environment': {p: importlib.metadata.version(p) for p in ('numpy', 'gudhi')},
             'post_result_exploratory': True}
    if freeze_path.exists():
        prior = read(freeze_path)
        normalized = json.loads(json.dumps(fixed))
        if {k: prior[k] for k in fixed} != normalized:
            raise ValueError('Existing diagnostic freeze differs; document changes instead of overwriting')
    else:
        dump(freeze_path, {**fixed, 'frozen_before_grid_queries_utc': utc()})
    with ProcessPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(evaluate, [(r, a, sha(lock_path)) for r, a in selected]))
    failures = sum(not r['endpoint_agreement_passed'] or r['envelope_failures'] > 0 for r in records)
    result = {'artifact_type': 'post_result_all_nonsaturation_path_diagnostic',
              'status': 'PASS_NUMERICAL_CHECKS' if not failures else 'FAIL_NUMERICAL_CHECKS',
              'post_result_exploratory': True, 'provenance': fixed, 'completed_utc': utc(),
              'n_comparisons': len(records), 'n_direct_queries': sum(len(r['grid']) for r in records),
              'comparisons': records, 'new_api_calls': 0, 'new_persistence_computations': 0,
              'primary_protocol_or_predictions_changed': False,
              'scope': 'Descriptive diagnostics of all three known exceptions; no confirmatory or biological claim.'}
    dump(ROOT / 'post_result_path_diagnostics.json', result)
    (ROOT / 'post_result_path_diagnostics.md').write_text(markdown(result))
    plot(result)
    print(json.dumps({'status': result['status'], 'post_result_exploratory': True,
                     'comparisons': [{k: r[k] for k in ('site_id', 'alternate_index', 'sampled_shape',
                         'maximum_absolute_chord_departure', 'endpoint_agreement_passed', 'envelope_failures',
                         'abstention_by_tolerance')} for r in records]}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
