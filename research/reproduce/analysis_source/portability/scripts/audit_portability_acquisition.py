#!/usr/bin/env python3
"""Independent, read-only numerical audit of frozen two-track acquisition.

Imports no acquisition/analysis production modules and makes no network calls.
Writes aggregate evidence only; no clinical records or credentials are read.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TRACKS = {'imr90': ('4dn:4DNFIJTOIGOI', 'EFO:0001196', ROOT),
          'gm12878': ('4dn:4DNFIXP4QG5B', 'EFO:0002784', ROOT / 'control_gm12878')}
OLD = ROOT.parent / 'anchor_method' / 'replication'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def stamp(value):
    result = datetime.datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError('Timestamp missing timezone')
    return result


def check(condition, label):
    if not condition:
        raise ValueError(label)


def same_path_array(left, right):
    check(left.shape == right.shape, 'Array shape mismatch')
    return bool(np.array_equal(left, right))


def bf16_counts(array):
    check(array.dtype == np.dtype('float32'), 'Decoded output is not float32')
    words = np.ascontiguousarray(array).view(np.uint32)
    return int(np.count_nonzero((words & np.uint32(0xFFFF)) != 0)), int(array.size)


def audit():
    complete = load(ROOT / 'acquisition_complete.json')
    check(complete['status'] == 'complete' and complete['n_sites'] == 84,
          'Acquisition is not complete for all 84 sites')
    freeze = load(ROOT / 'freeze_record.json')
    frozen_at = stamp(freeze['frozen_at_utc'])
    freeze_sha = digest(ROOT / 'freeze_record.json')
    frozen = {}
    for relative, expected in freeze['files'].items():
        path = (ROOT / relative).resolve()
        check(path.is_relative_to(ROOT), 'Freeze path outside experiment')
        frozen[relative] = digest(path)
        check(frozen[relative] == expected, 'Frozen local hash mismatch')
    external = {}
    for relative, expected in freeze.get('external_scientific_sources', {}).items():
        path = (ROOT.parent / relative).resolve()
        check(path.is_relative_to(ROOT.parent), 'External source outside rework')
        external[relative] = digest(path)
        check(external[relative] == expected, 'External scientific-source hash mismatch')
    check(digest(ROOT / 'candidate_cohort.json') == digest(OLD / 'candidate_cohort.json'),
          'Portability cohort differs from original cohort')
    check(digest(ROOT / 'midpoint_selection.json') == digest(OLD / 'midpoint_selection.json'),
          'Midpoint selection differs from original selection')
    provenance = load(ROOT / 'acquisition_provenance.json')
    check(provenance['freeze_record_sha256'] == freeze_sha, 'Provenance freeze mismatch')
    check(provenance['acquisition_script_sha256'] == digest(ROOT / 'scripts/acquire_portability.py'),
          'Provenance acquisition script mismatch')
    check(stamp(provenance['started_utc']) >= frozen_at, 'Acquisition provenance predates freeze')
    check(provenance['client_version'] == '0.9.0' and provenance['model_alias'] == 'ALL_FOLDS',
          'Unexpected client version/model alias')
    source = load(ROOT / 'candidate_cohort.json')['sites']
    check(len(source) == 84 and len({s['site_id'] for s in source}) == 84, 'Invalid cohort')
    manifests = {key: load(directory / 'manifest.json') for key, (_, _, directory) in TRACKS.items()}
    for key, (track, ontology, directory) in TRACKS.items():
        manifest = manifests[key]
        status = load(directory / 'acquisition_complete.json')
        check(status['status'] == 'complete' and status['n_sites'] == 84 and status['n_alternate_maps'] == 252,
              'Per-track completion mismatch')
        check(status['manifest_sha256'] == digest(directory / 'manifest.json'), 'Completion manifest mismatch')
        check(manifest['track'] == track and manifest['ontology'] == ontology, 'Manifest track mismatch')
        check(manifest['freeze_record_sha256'] == freeze_sha, 'Manifest freeze mismatch')
        check(manifest['candidate_sha256'] == digest(ROOT / 'candidate_cohort.json'), 'Manifest cohort mismatch')
        check(manifest['protocol_sha256'] == digest(ROOT / freeze['protocol_file']), 'Manifest protocol mismatch')
        check(manifest['midpoint_selection_sha256'] == digest(ROOT / 'midpoint_selection.json'), 'Manifest midpoint mismatch')
        check(manifest['client_version'] == '0.9.0' and manifest['model_version'] == 'ALL_FOLDS', 'Manifest model mismatch')
        check(len(manifest['sites']) == 84, 'Manifest site count mismatch')
    history_counts, error_counts = Counter(), Counter()
    attempts_total = 0
    successful_calls = 0
    expected_paths = set()
    earliest_attempt = None
    latest_completion = None
    per_track = {key: {'output_float32_values_checked': 0, 'not_bfloat16_representable_values': 0,
                       'ref_repeat_max_abs_difference': 0., 'sites_with_ref_repeat_differences': 0,
                       'decoded_map_count': 0, 'site_call_array_equal_checks': 0}
                 for key in TRACKS}
    channel_nonidentity = {'paired_ref_maps': 0, 'paired_alt_maps': 0,
                           'nonidentical_ref_maps': 0, 'nonidentical_alt_maps': 0}
    drift_rows = []
    per_site_integrity = []
    for index, origin in enumerate(source):
        check(origin['site_index'] == index, 'Nonsequential frozen index')
        site_paths = {}
        for key, (_, _, directory) in TRACKS.items():
            site = manifests[key]['sites'][index]
            check(site['site_id'] == origin['site_id'] and site['site_index'] == index, 'Site indexing differs')
            check(site['alleles'] == origin['alleles'], 'Allele order differs')
            check(site['selected_allele_index'] == origin['selected_allele_index'], 'Selected label changed')
            check(not Path(site['npz_path']).is_absolute() and not Path(site['metadata_path']).is_absolute(),
                  'Manifest paths are not portable')
            check(site['start'] == origin['window_start_0based'] and site['end'] == origin['window_end_0based_exclusive'],
                  'Window coordinates differ')
            check(site['end'] - site['start'] == 1048576 and site['bin_coordinates'] == [site['start'] + j * 2048 for j in range(512)],
                  'Bin coordinates differ')
            path = directory / site['npz_path']
            metadata_path = directory / site['metadata_path']
            meta = load(metadata_path)
            check(meta['site_id'] == origin['site_id'] and meta['npz_sha256'] == digest(path), 'Site metadata/hash mismatch')
            check(meta['track'] == TRACKS[key][0] and meta['freeze_record_sha256'] == freeze_sha,
                  'Site metadata provenance mismatch')
            with np.load(path, allow_pickle=False) as values:
                arrays = {name: values[name] for name in ('ref', 'alt', 'ref_repeats')}
            check(arrays['ref'].shape == (512, 512) and arrays['alt'].shape == arrays['ref_repeats'].shape == (3, 512, 512),
                  'Unexpected stored site dimensions')
            check(same_path_array(arrays['ref'], arrays['ref_repeats'][0]), 'Canonical reference differs from first repeat')
            repeat_diff = float(np.max(np.abs(arrays['ref_repeats'].astype(np.float64) - arrays['ref'].astype(np.float64))))
            check(meta['reference_repeat_max_abs_difference'] == repeat_diff, 'Reference-repeat statistic mismatch')
            per_track[key]['ref_repeat_max_abs_difference'] = max(per_track[key]['ref_repeat_max_abs_difference'], repeat_diff)
            per_track[key]['sites_with_ref_repeat_differences'] += int(repeat_diff != 0)
            site_paths[key] = (arrays, path, metadata_path)
        for allele_index, allele in enumerate(origin['alleles']):
            call_path = ROOT / 'calls' / f'site_{index:03d}_{allele}.npz'
            expected_paths.add(call_path.name)
            meta = load(call_path.with_suffix('.json'))
            attempts = load(call_path.with_suffix('.attempts.json'))
            check(1 <= len(attempts) <= 5 and [a['attempt'] for a in attempts] == list(range(1, len(attempts) + 1)),
                  'Attempt sequence invalid')
            attempts_total += len(attempts)
            for item in attempts:
                history_counts[item['status']] += 1
                started = stamp(item['started_utc'])
                check(started >= frozen_at, 'Logged prediction attempt predates freeze')
                earliest_attempt = started if earliest_attempt is None else min(earliest_attempt, started)
                if item['status'] == 'failed':
                    error_counts[f"{item.get('error_type')}:{item.get('grpc_status')}"] += 1
                if 'completed_utc' in item:
                    check(stamp(item['completed_utc']) >= started, 'Attempt completion predates start')
            check(attempts[-1]['status'] == 'complete' and attempts[-1]['attempt'] == meta['attempt'],
                  'Final successful attempt mismatch')
            check(sum(a['status'] == 'complete' for a in attempts) == 1, 'Not exactly one complete attempt')
            ended = stamp(meta['completed_utc'])
            check(ended >= stamp(attempts[-1]['started_utc']) and ended >= frozen_at, 'Call completion predates start/freeze')
            latest_completion = ended if latest_completion is None else max(latest_completion, ended)
            check(meta['npz_sha256'] == digest(call_path), 'Call checksum mismatch')
            check(meta['variant_id'] == f"{origin['site_id']}>{allele}", 'Call allele identity mismatch')
            check(meta['freeze_record_sha256'] == freeze_sha and meta['client_version'] == '0.9.0' and meta['model_version'] == 'ALL_FOLDS',
                  'Call model/freeze mismatch')
            check(meta['interval'] == {'chromosome': origin['chromosome'], 'start': origin['window_start_0based'],
                                      'end': origin['window_end_0based_exclusive']} and meta['resolution_bp'] == 2048,
                  'Call interval/resolution mismatch')
            names = meta['track_names']
            check(len(names) == 2 and set(names) == {t[0] for t in TRACKS.values()}, 'Call track names invalid')
            with np.load(call_path, allow_pickle=False) as values:
                reference, alternate = values['ref'], values['alt']
            check(reference.shape == alternate.shape == (512, 512, 2) and meta['shape'] == [512, 512, 2],
                  'Call dimensions invalid')
            check(np.isfinite(reference).all() and np.isfinite(alternate).all(), 'Nonfinite call array')
            check(np.array_equal(reference, reference.transpose(1, 0, 2)) and np.array_equal(alternate, alternate.transpose(1, 0, 2)),
                  'Asymmetric call array')
            channels = {}
            for key, (track, _, _) in TRACKS.items():
                channel = names.index(track)
                r, a = reference[..., channel], alternate[..., channel]
                channels[key] = (r, a)
                site_arrays = site_paths[key][0]
                check(same_path_array(r, site_arrays['ref_repeats'][allele_index]), 'Call REF does not match site REF repeat')
                check(same_path_array(a, site_arrays['alt'][allele_index]), 'Call ALT does not match site alternate')
                per_track[key]['site_call_array_equal_checks'] += 2
                per_track[key]['decoded_map_count'] += 2
                for array in (r, a):
                    bad, n = bf16_counts(array)
                    per_track[key]['not_bfloat16_representable_values'] += bad
                    per_track[key]['output_float32_values_checked'] += n
            channel_nonidentity['paired_ref_maps'] += 1
            channel_nonidentity['paired_alt_maps'] += 1
            channel_nonidentity['nonidentical_ref_maps'] += int(not np.array_equal(channels['imr90'][0], channels['gm12878'][0]))
            channel_nonidentity['nonidentical_alt_maps'] += int(not np.array_equal(channels['imr90'][1], channels['gm12878'][1]))
            successful_calls += 1
        historical_path = OLD / 'sites' / f'site_{index:03d}.npz'
        historical_meta = load(historical_path.with_suffix('.json'))
        check(historical_meta['npz_sha256'] == digest(historical_path) and historical_meta['site_id'] == origin['site_id'],
              'Historical GM input integrity mismatch')
        details = {}
        with np.load(historical_path, allow_pickle=False) as old:
            for name in ('ref', 'ref_repeats', 'alt'):
                current = site_paths['gm12878'][0][name]
                check(old[name].shape == current.shape, 'Historical GM shape mismatch')
                absolute = np.abs(current.astype(np.float64) - old[name].astype(np.float64))
                details[name] = {'equal': bool(np.array_equal(current, old[name])),
                                 'maximum_absolute_difference': float(absolute.max()),
                                 'different_elements': int(np.count_nonzero(absolute))}
        drift_rows.append({'site_index': index, 'all_arrays_equal': all(d['equal'] for d in details.values()),
                           'arrays': details})
        per_site_integrity.append({'site_index': index,
                                   'imr90_npz_sha256': digest(site_paths['imr90'][1]),
                                   'gm12878_npz_sha256': digest(site_paths['gm12878'][1]),
                                   'historical_gm12878_npz_sha256': digest(historical_path)})
    check(successful_calls == 252, 'Expected 252 complete calls')
    check({p.name for p in (ROOT / 'calls').glob('*.npz')} == expected_paths, 'Unexpected or missing call NPZ files')
    check(len(list((ROOT / 'calls').glob('*.attempts.json'))) == 252, 'Unexpected attempts-file count')
    for key, (_, _, directory) in TRACKS.items():
        check(len(list((directory / 'sites').glob('*.npz'))) == 84, 'Unexpected site NPZ count')
    reported = load(ROOT / 'gm12878_drift_control.json')
    equal = all(row['all_arrays_equal'] for row in drift_rows)
    maximum_drift = max(d['maximum_absolute_difference'] for row in drift_rows for d in row['arrays'].values())
    check(reported['all_arrays_equal'] == equal and reported['maximum_absolute_difference'] == maximum_drift,
          'Independent drift audit disagrees with acquisition report')
    for computed, saved in zip(drift_rows, reported['sites'], strict=True):
        check(computed['site_index'] == saved['site_index'] and computed['all_arrays_equal'] == saved['all_arrays_equal'],
              'Per-site drift report differs')
        for key, item in computed['arrays'].items():
            check(item['equal'] == saved['arrays'][key]['array_equal'] and item['maximum_absolute_difference'] == saved['arrays'][key]['maximum_absolute_difference']
                  and item['different_elements'] == saved['arrays'][key]['different_elements'], 'Per-array drift report differs')
    return {'status': 'PASS_INDEPENDENT_ACQUISITION_AUDIT',
            'audit_script_sha256': digest(__file__),
            'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'n_sites': 84, 'n_variant_calls': successful_calls, 'n_tracks': 2,
            'frozen_at_utc': frozen_at.isoformat(), 'first_recorded_prediction_attempt_utc': earliest_attempt.isoformat(),
            'last_recorded_prediction_completion_utc': latest_completion.isoformat(),
            'freeze_precedes_first_recorded_attempt_seconds': (earliest_attempt - frozen_at).total_seconds(),
            'freeze_record_sha256': freeze_sha, 'frozen_file_hashes_verified': frozen,
            'external_scientific_source_hashes_verified': external,
            'attempt_count': attempts_total, 'attempt_status_counts': dict(history_counts),
            'failed_attempt_types': dict(error_counts), 'per_track': per_track,
            'imr90_vs_gm12878': channel_nonidentity,
            'historical_gm12878_drift': {'all_arrays_equal': equal,
                                       'n_sites_with_differences': sum(not row['all_arrays_equal'] for row in drift_rows),
                                       'maximum_absolute_difference': maximum_drift,
                                       'independent_comparison_matches_acquisition_report': True,
                                       'sites': drift_rows},
            'site_input_hashes': per_site_integrity,
            'scope': ['No production acquisition/analysis modules imported; no network requests.',
                      'Checked delivered float32 array values and logged chronology; no server weights or pre-decoding arithmetic certified.',
                      'Exact bfloat16 representability is a property of delivered coordinates, not proof of why rounding occurred.',
                      'Distinct track matrices do not establish biological independence or prediction accuracy.',
                      'Freeze is a local pre-acquisition record, not external preregistration.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reports')
    args = parser.parse_args()
    try:
        result = audit()
    except Exception as error:
        # Labels are fixed internal checks, never API/credential responses.
        result = {'status': 'FAIL_ACQUISITION_AUDIT', 'error_type': type(error).__name__,
                  'error': str(error), 'audit_script_sha256': digest(__file__)}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / 'ACQUISITION_AUDIT.json'
    path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    if result['status'].startswith('PASS'):
        lines = ['# Independent portability acquisition audit', '', f"**{result['status']}**", '',
                 'The audit imports no production acquisition or analysis modules and makes no network requests.', '',
                 f"All {result['n_sites']} frozen sites, {result['n_variant_calls']} REF–ALT calls and both named tracks were checked.",
                 f"The local protocol freeze preceded the first logged prediction attempt by {result['freeze_precedes_first_recorded_attempt_seconds']:.6f} seconds.",
                 'All frozen inputs and named external scientific sources retain their frozen hashes.',
                 'Call/site checks cover hashes, coordinates, allele order, exact track names, array shapes, symmetry, finite values and channel-to-site extraction.', '',
                 f"Attempt statuses: `{json.dumps(result['attempt_status_counts'], sort_keys=True)}`.", '',
                 '| Track | Decoded maps | Float32 values checked | Values not exactly bfloat16-representable | Maximum repeated-REF difference |',
                 '|---|---:|---:|---:|---:|']
        for key, values in result['per_track'].items():
            lines.append(f"| {key} | {values['decoded_map_count']} | {values['output_float32_values_checked']} | {values['not_bfloat16_representable_values']} | {values['ref_repeat_max_abs_difference']} |")
        nonident = result['imr90_vs_gm12878']
        drift = result['historical_gm12878_drift']
        lines += ['', f"IMR-90 and GM12878 differ in {nonident['nonidentical_ref_maps']}/{nonident['paired_ref_maps']} paired REF maps and {nonident['nonidentical_alt_maps']}/{nonident['paired_alt_maps']} paired ALT maps.",
                  f"Independent historical GM12878 comparison: all arrays equal = **{drift['all_arrays_equal']}**; maximum absolute difference = **{drift['maximum_absolute_difference']}**; sites with differences = **{drift['n_sites_with_differences']}**.",
                  'The independent per-array comparison agrees with the acquisition drift report.', '', '## Scope', '']
        lines += [f'- {item}' for item in result['scope']]
        lines += ['', f"Audit script SHA256: `{result['audit_script_sha256']}`", '']
        (args.output_dir / 'ACQUISITION_AUDIT.md').write_text('\n'.join(lines))
    else:
        (args.output_dir / 'ACQUISITION_AUDIT.md').write_text('# Independent portability acquisition audit\n\n' + json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'n_sites', 'n_variant_calls', 'error') if key in result}))
    return 0 if result['status'].startswith('PASS') else 1


if __name__ == '__main__':
    raise SystemExit(main())
