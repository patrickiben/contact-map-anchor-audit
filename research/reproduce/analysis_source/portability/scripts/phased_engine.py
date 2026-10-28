#!/usr/bin/env python3
"""Freeze native-only audit predictions before evaluating centered endpoints.

This script deliberately never acquires predictions. Both phases operate on a
declared manifest of cached maps; all outputs are in a separate directory.
"""
from __future__ import annotations

import argparse
import copy
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

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'anchor_method')]
import analyze_spatial_maps as core
import certify_increasing_branch as witness
import gudhi
from gudhi import hera

TOLERANCES = (0.0, 1e-6, 1e-5)
ALLOWANCE = 1e-12


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    tmp.replace(path)


def load(path):
    return json.loads(Path(path).read_text())


def source_hashes():
    return {
        'driver_sha256': sha(__file__),
        'core_sha256': sha(core.__file__),
        'hausdorff_source_sha256': sha(witness.__file__),
    }


def environment():
    return {'python': platform.python_version(), **{
        name: importlib.metadata.version(name)
        for name in ('numpy', 'scipy', 'ripser', 'persim', 'gudhi')}}


def distance(left, right):
    return 0.0 if np.array_equal(left, right) else float(
        hera.bottleneck_distance(left, right, delta=0.0))


def edge_error(matrix):
    values = -matrix[np.triu_indices(len(matrix), 1)]
    offset = max(0.0, 1.0 - float(values.min()))
    return float(np.max(np.abs(
        (values + offset).astype(np.float32).astype(float) - offset - values)))


def top(values, tolerance):
    values = np.asarray(values)
    return np.flatnonzero(values >= values.max() - tolerance).tolist()


def rank_bounds(lower, upper, tolerance):
    return {
        'possible_top_members': [i for i in range(3)
                                 if upper[i] >= max(lower) - tolerance],
        'necessary_top_members': [i for i in range(3)
                                  if lower[i] >= max(upper[j] for j in range(3) if j != i) - tolerance],
        'guaranteed_unique_leaders': [i for i in range(3)
                                     if lower[i] > max(upper[j] for j in range(3) if j != i) + tolerance],
    }


def resolve(path, parent):
    path = Path(path)
    return path if path.is_absolute() else Path(parent) / path


def native_task(task):
    site, manifest_dir, output, common, midpoint = task
    started = time.monotonic()
    index = site['site_index']
    path = Path(output) / 'native' / f'site_{index:03d}.json'
    try:
        npz = resolve(site['npz_path'], manifest_dir)
        metadata = resolve(site['metadata_path'], manifest_dir)
        deadline = time.monotonic() + 3600
        while not (npz.exists() and metadata.exists()):
            if time.monotonic() > deadline:
                raise TimeoutError('Input readiness timeout: ' + site['site_id'])
            time.sleep(1)
        meta = load(metadata)
        digest = sha(npz)
        if meta['npz_sha256'] != digest or meta['site_id'] != site['site_id']:
            raise ValueError('Input acquisition metadata/hash mismatch')
        key = {**common, 'site_metadata_sha256': hashlib.sha256(
            json.dumps(site, sort_keys=True).encode()).hexdigest(),
            'npz_sha256': digest, 'acquisition_metadata_sha256': sha(metadata),
            'midpoint_validation': midpoint}
        if path.exists():
            old = load(path)
            if old.get('status') == 'complete' and old.get('cache_key') == key:
                return old
        print('Native starting', index, site['site_id'], flush=True)
        ref, alt, provenance = core.load_site(site, Path(manifest_dir))
        maps = [ref, *alt]
        upper_index = np.triu_indices(len(ref), 1)
        means = [float(matrix[upper_index].mean()) for matrix in maps]
        diagrams = [core.h1(-matrix) for matrix in maps]
        errors = [edge_error(matrix) for matrix in maps]
        native = np.array([distance(diagrams[0], d) for d in diagrams[1:]])
        shifts = np.array(means[1:]) - means[0]
        magnitude = abs(shifts)
        witnesses = []
        for i, diagram in enumerate(diagrams[1:]):
            native_h, native_w = witness.hausdorff(diagrams[0], diagram)
            shifted_h, shifted_w = witness.hausdorff(diagrams[0], diagram + shifts[i])
            if native_h > native[i] + 1e-10:
                raise AssertionError('Native Hausdorff lower bound violation')
            if shifted_h > native[i] + magnitude[i] + 1e-10:
                raise AssertionError('Shifted lower/upper bounds disagree')
            witnesses.append({'alternate_index': i,
                'native_hausdorff_lower_bound': native_h,
                'shifted_hausdorff_lower_bound': shifted_h,
                'native_witness': native_w, 'shifted_witness': shifted_w,
                'increasing_branch_predicted': bool(magnitude[i] > 1e-10
                    and abs(shifted_h - native[i] - magnitude[i]) <= ALLOWANCE)})
        lower = np.maximum(0.0, native - magnitude) - ALLOWANCE
        upper = native + magnitude + ALLOWANCE
        strengthened = np.maximum(np.maximum(0.0, native - magnitude),
                                  [w['shifted_hausdorff_lower_bound'] for w in witnesses]) - ALLOWANCE
        predictions = {str(t): {
            'simple': rank_bounds(lower, upper, t),
            'strengthened': rank_bounds(strengthened, upper, t),
        } for t in TOLERANCES}
        diffs = alt[:, upper_index[0], upper_index[1]] - ref[upper_index]
        lifetimes = [d[:, 1] - d[:, 0] for d in diagrams]
        counts = [len(d) for d in diagrams]
        totals = [float(v.sum()) for v in lifetimes]
        maxima = [float(v.max()) if len(v) else 0.0 for v in lifetimes]
        baselines = {
            'absolute_mean_change': magnitude.tolist(),
            'native_rms': np.sqrt(np.mean(diffs ** 2, axis=1)).tolist(),
            'centered_rms': np.sqrt(np.mean((diffs - diffs.mean(axis=1, keepdims=True)) ** 2, axis=1)).tolist(),
            'max_absolute': np.max(np.abs(diffs), axis=1).tolist(),
            'lifetime_count_absolute_change': np.abs(np.array(counts[1:]) - counts[0]).tolist(),
            'total_persistence_absolute_change': np.abs(np.array(totals[1:]) - totals[0]).tolist(),
            'maximum_persistence_absolute_change': np.abs(np.array(maxima[1:]) - maxima[0]).tolist(),
            'native_plus_absolute_mean_change': (native + magnitude).tolist(),
            'native_minus_absolute_mean_change': (native - magnitude).tolist(),
        }
        record = {
            'status': 'complete', 'phase': 'native_only', 'site_id': site['site_id'],
            'site_index': index, 'gene': site.get('gene'), 'means': means,
            'provenance': provenance, 'cache_key': key,
            'native_float32_edge_errors_ref_then_alts': errors,
            'representations': {'native': {'distances': native.tolist(),
                'credits_by_tolerance': {str(t): core.fractional_top(native, t).tolist() for t in TOLERANCES},
                'h1_diagrams_ref_then_alts': [d.tolist() for d in diagrams]}},
            'baselines': baselines,
            'lifetime_summaries_ref_then_alts': {'count': counts, 'total': totals, 'maximum': maxima},
            'native_prediction': {'lower': lower.tolist(), 'upper': upper.tolist(),
                'strengthened_lower': strengthened.tolist(), 'by_tolerance': predictions,
                'witnesses': witnesses, 'centered_bottleneck_evaluations': 0,
                'allowance_status': 'Practical 1e-12 numerical allowance; no rigorous arithmetic enclosure.'},
            'bottleneck_solver': {'name': 'gudhi.hera.bottleneck_distance', 'delta': 0,
                                  'version': gudhi.__version__},
            'selected_allele_index': site.get('selected_allele_index'),
            'selected_labels_used': False,
            'selected_label_note': 'Index stored for later descriptive reporting; no predictions use clinical labels.',
            'elapsed_seconds_native': time.monotonic() - started,
            'completed_utc': utc(),
        }
        dump(path, record)
        print('Native complete', index, flush=True)
        return record
    except Exception as error:
        failure = {'status': 'failed', 'phase': 'native_only', 'site_index': index,
                   'site_id': site['site_id'], 'error_type': type(error).__name__,
                   'error': str(error), 'traceback': traceback.format_exc(), 'utc': utc()}
        dump(Path(output) / 'failures' / f'native_{index:03d}_{time.time_ns()}.json', failure)
        print('Native FAILED', index, str(error), flush=True)
        return failure


def validate_prediction(prediction, scores, tolerance):
    actual = top(scores, tolerance)
    possible = prediction['possible_top_members']
    necessary = prediction['necessary_top_members']
    unique = prediction['guaranteed_unique_leaders']
    return {'actual_top_set': actual,
            'possible_contains_actual': set(actual) <= set(possible),
            'necessary_contained_in_actual': set(necessary) <= set(actual),
            'unique_agrees': not unique or unique == actual,
            'passed': set(actual) <= set(possible) and set(necessary) <= set(actual)
                      and (not unique or unique == actual)}


def centered_task(task):
    native_path, output, midpoint, lock_sha = task
    started = time.monotonic()
    record = load(native_path)
    index = record['site_index']
    try:
        print('Centered starting', index, flush=True)
        diagrams = [np.asarray(d, dtype=float).reshape(-1, 2)
                    for d in record['representations']['native']['h1_diagrams_ref_then_alts']]
        means = record['means']
        native = record['representations']['native']['distances']
        centered_diagrams = [d + m for d, m in zip(diagrams, means)]
        centered = [distance(centered_diagrams[0], d) for d in centered_diagrams[1:]]
        diagnostics = []
        for i, (before, after) in enumerate(zip(native, centered)):
            delta = means[i + 1] - means[0]
            magnitude = abs(delta)
            change = after - before
            direction = 1 if change >= 0 else -1
            row = {'alternate_index': i, 'delta': delta, 'native_distance': before,
                   'centered_distance': after, 'signed_saturation_deficit': magnitude - direction * change,
                   'absolute_saturation_residual': abs(magnitude - abs(change)),
                   'numerically_saturated_at_1e12': abs(magnitude - abs(change)) <= 1e-12,
                   'numerically_saturated_at_primary_1e10': abs(magnitude - abs(change)) <= 1e-10,
                   'tiny_shift_at_1e10': magnitude <= 1e-10, 'endpoint_direction': direction,
                   'endpoint_error_allowance': ALLOWANCE,
                   'endpoint_allowance_status': 'Practical numerical allowance, not a proved roundoff bound.',
                   'conservative_deficit_upper_bound': max(0.0, magnitude - direction * change + 2e-12),
                   'per_distance_ph_input_rounding_bound': record['native_float32_edge_errors_ref_then_alts'][0]
                       + record['native_float32_edge_errors_ref_then_alts'][i + 1]}
            if midpoint:
                actual = distance(diagrams[0], diagrams[i + 1] + 0.5 * delta)
                chord = (before + after) / 2
                low = max(before - 0.5 * magnitude, after - 0.5 * magnitude) - ALLOWANCE
                high = min(before + 0.5 * magnitude, after + 0.5 * magnitude) + ALLOWANCE
                tolerance = max(1e-10, 1e-10 * max(abs(actual), abs(chord)))
                row['midpoint_check'] = {'lambda': 0.5, 'direct_exact_solver_distance': actual,
                    'affine_interpolation': chord, 'absolute_error': abs(actual - chord), 'tolerance': tolerance,
                    'affine_agreement_passed': abs(actual - chord) <= tolerance,
                    'lipschitz_endpoint_tube': [low, high], 'endpoint_tube_passed': low <= actual <= high}
            diagnostics.append(row)
        checks = {str(t): {name: validate_prediction(prediction, centered, t)
                          for name, prediction in record['native_prediction']['by_tolerance'][str(t)].items()}
                  for t in TOLERANCES}
        bounds = record['native_prediction']
        score_bounds_pass = all(bounds['strengthened_lower'][i] <= centered[i] <= bounds['upper'][i]
                                for i in range(3))
        checks_pass = score_bounds_pass and all(v['passed'] for check in checks.values() for v in check.values())
        record.update({'phase': 'centered_validation', 'pair_diagnostics': diagnostics,
            'locked_native_prediction_sha256': sha(native_path), 'native_predictions_lock_sha256': lock_sha,
            'locked_prediction_validation': {'by_tolerance': checks, 'score_bounds_passed': score_bounds_pass,
                                             'passed': checks_pass},
            'elapsed_seconds_centered': time.monotonic() - started,
            'completed_centered_utc': utc()})
        record['elapsed_seconds'] = record['elapsed_seconds_native'] + record['elapsed_seconds_centered']
        record['representations']['centered'] = {'distances': centered,
            'credits_by_tolerance': {str(t): core.fractional_top(np.array(centered), t).tolist() for t in TOLERANCES}}
        dump(Path(output) / 'site_analysis' / f'site_{index:03d}.json', record)
        print('Centered complete', index, 'bound_validation', checks_pass, flush=True)
        return record
    except Exception as error:
        failure = {'status': 'failed', 'phase': 'centered_validation', 'site_index': index,
                   'site_id': record['site_id'], 'error_type': type(error).__name__,
                   'error': str(error), 'traceback': traceback.format_exc(), 'utc': utc()}
        dump(Path(output) / 'failures' / f'centered_{index:03d}_{time.time_ns()}.json', failure)
        print('Centered FAILED', index, str(error), flush=True)
        return failure


def compact(record, path):
    result = copy.deepcopy(record)
    diagrams = result['representations']['native'].pop('h1_diagrams_ref_then_alts')
    result['representations']['native']['h1_interval_counts_ref_then_alts'] = [len(d) for d in diagrams]
    result['full_diagram_artifact'] = {'path': str(Path(path).resolve()), 'sha256': sha(path)}
    return result


def verify_lock(output, common):
    lock_path = output / 'native_predictions_lock.json'
    if not lock_path.exists():
        raise ValueError('Centered phase requires a completed native-prediction lock')
    lock = load(lock_path)
    if lock['provenance'] != common:
        raise ValueError('Native lock provenance mismatch: protocol, inputs, sources or environment changed')
    for row in lock['artifacts']:
        if sha(output / row['path']) != row['sha256']:
            raise ValueError('Native lock artifact mismatch: ' + row['path'])
    return lock


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase', required=True, choices=('native', 'centered'))
    p.add_argument('--manifest', required=True, type=Path)
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--protocol', required=True, type=Path)
    p.add_argument('--midpoint-site-ids', required=True, type=Path)
    p.add_argument('--workers', type=int, default=10)
    p.add_argument('--expected-sites', type=int, default=84)
    p.add_argument('--expected-midpoint-sites', type=int, default=7)
    p.add_argument('--allow-streaming', action='store_true')
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load(args.manifest)
    sites = manifest['sites']
    mid = load(args.midpoint_site_ids)
    mid = mid['site_ids'] if isinstance(mid, dict) else mid
    if len(sites) != args.expected_sites or len(set(mid)) != args.expected_midpoint_sites:
        raise ValueError('Frozen site/midpoint counts mismatch')
    if len({s['site_id'] for s in sites}) != len(sites) or len({s['site_index'] for s in sites}) != len(sites):
        raise ValueError('Duplicate site identifiers or indices')
    if not set(mid) <= {s['site_id'] for s in sites}:
        raise ValueError('Midpoint selection outside cohort')
    if manifest.get('schema_version') != 1 or manifest.get('data_type') != 'spatial_log_enrichment_maps':
        raise ValueError('Require declared spatial-map schema')
    if manifest.get('units') != 'native_log_enrichment' or not manifest.get('track'):
        raise ValueError('Require declared map units and track')
    if not args.allow_streaming and not (args.manifest.parent / 'acquisition_complete.json').exists():
        raise ValueError('Acquisition completion gate missing')
    common = {**source_hashes(), 'manifest_sha256': sha(args.manifest),
              'protocol_sha256': sha(args.protocol), 'midpoint_selection_sha256': sha(args.midpoint_site_ids),
              'environment': environment(), 'track': manifest['track'],
              'biosample': manifest.get('biosample'), 'n_planned_sites': len(sites)}
    started = time.monotonic()
    if args.phase == 'native':
        if (args.output_dir / 'native_predictions_lock.json').exists():
            verify_lock(args.output_dir, common)
            print('Native lock already complete and verified; no mutation.')
            return
        if list((args.output_dir / 'site_analysis').glob('site_*.json')):
            raise ValueError('Refusing native freeze after centered artifacts already exist')
        tasks = [(s, str(args.manifest.parent), str(args.output_dir), common, s['site_id'] in mid) for s in sites]
        function = native_task
    else:
        lock = verify_lock(args.output_dir, common)
        if lock['n_complete_sites'] != len(sites):
            raise ValueError('Incomplete native lock')
        lock_sha = sha(args.output_dir / 'native_predictions_lock.json')
        tasks = [(str(args.output_dir / 'native' / f"site_{s['site_index']:03d}.json"),
                  str(args.output_dir), s['site_id'] in mid, lock_sha) for s in sites]
        function = centered_task
    records = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(function, task) for task in tasks]
        for future in as_completed(futures):
            records.append(future.result())
            dump(args.output_dir / f'{args.phase}_progress.json', {
                'phase': args.phase, 'complete': sum(r['status'] == 'complete' for r in records),
                'failed': sum(r['status'] != 'complete' for r in records), 'planned': len(sites),
                'elapsed_seconds': time.monotonic() - started, 'utc': utc()})
    records.sort(key=lambda r: r['site_index'])
    failures = [r for r in records if r['status'] != 'complete']
    complete = [r for r in records if r['status'] == 'complete']
    if args.phase == 'native':
        result = {'artifact_type': 'locked_native_only_portability_predictions', 'provenance': common,
                  'n_planned_sites': len(sites), 'n_complete_sites': len(complete), 'failures': failures,
                  'centered_bottleneck_evaluations': 0, 'selected_labels_used': False,
                  'records': [compact(r, args.output_dir / 'native' / f"site_{r['site_index']:03d}.json")
                              for r in complete]}
        dump(args.output_dir / 'native_predictions.json', result)
        if failures:
            raise SystemExit('Native failures retained; no prediction lock written')
        artifacts = [Path('native_predictions.json')] + [Path('native') / f"site_{r['site_index']:03d}.json" for r in complete]
        lock = {'artifact_type': 'native_prediction_lock_before_centered_evaluation',
                'frozen_utc': utc(), 'provenance': common, 'n_complete_sites': len(complete),
                'centered_bottleneck_evaluations_before_freeze': 0,
                'artifacts': [{'path': str(path), 'sha256': sha(args.output_dir / path)} for path in artifacts]}
        dump(args.output_dir / 'native_predictions_lock.json', lock)
        print('Native predictions LOCKED', len(complete), 'sites', flush=True)
        return
    # Verify immutable native artifacts again after every centered evaluation.
    verify_lock(args.output_dir, common)
    pairs = [q for r in complete for q in r['pair_diagnostics']]
    checks = [q['midpoint_check'] for q in pairs if 'midpoint_check' in q]
    violations = sum(not r['locked_prediction_validation']['passed'] for r in complete)
    summary = {'pairs_evaluated': len(pairs),
        'numerically_saturated_pairs_primary_1e10': sum(q['numerically_saturated_at_primary_1e10'] for q in pairs),
        'numerically_saturated_pairs_sensitivity_1e12': sum(q['numerically_saturated_at_1e12'] for q in pairs),
        'tiny_shift_pairs': sum(q['tiny_shift_at_1e10'] for q in pairs),
        'non_tiny_nonsaturated_pairs': sum(not q['tiny_shift_at_1e10'] and not q['numerically_saturated_at_primary_1e10'] for q in pairs),
        'maximum_absolute_saturation_residual': max((q['absolute_saturation_residual'] for q in pairs), default=None),
        'midpoint_checks': len(checks), 'midpoint_affine_failures': sum(not q['affine_agreement_passed'] for q in checks),
        'midpoint_tube_failures': sum(not q['endpoint_tube_passed'] for q in checks),
        'maximum_midpoint_absolute_error': max((q['absolute_error'] for q in checks), default=None),
        'locked_prediction_validation_failures': violations}
    result = {'artifact_type': 'prospectively_locked_cross_track_portability',
        'status': 'complete' if not failures else 'complete_with_failures', 'provenance': common,
        'n_planned_sites': len(sites), 'n_complete_sites': len(complete), 'n_failed_sites': len(failures),
        'failures': failures, 'records': [compact(r, args.output_dir / 'site_analysis' / f"site_{r['site_index']:03d}.json") for r in complete],
        'summary': summary, 'selected_labels_used': False, 'inferential_tests_added': 0,
        'native_predictions_lock_sha256': lock_sha,
        'caution': 'Same-model cross-track transfer; numerical allowances are not rigorous arithmetic certificates.'}
    dump(args.output_dir / 'anchor_replication_summary.json', result)
    print(json.dumps(summary, indent=2))
    if failures or violations:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
