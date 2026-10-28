#!/usr/bin/env python3
"""Frozen IMR-90 acquisition with contemporaneous GM12878 control.

No request is made until the script, cohort, protocol and midpoint selection
match freeze_record.json. Credentials and raw exception messages are never
written. Both track channels are requested together and selected by name.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import time

import grpc
import numpy as np
from alphagenome.data import genome
from alphagenome.models import dna_client


OUT = Path(os.environ.get('ANCHOR_ACQUISITION_DIR', str(Path(__file__).resolve().parents[1]))).resolve()
REWORK = OUT.parent
LEGACY = Path(os.environ.get('ANCHOR_LEGACY_DIR', str(REWORK / 'anchor_method' / 'replication')))
# Acquisition credentials are supplied by the caller, never packaged.
COHORT_SHA256 = 'b58bcab74e54c5f1626f9e5a3d07d87665b2e10af6553933d1a488e2a06cb34c'
N_SITES = 84
MAX_ATTEMPTS = 5
TRACKS = {
    'imr90': {'name': '4dn:4DNFIJTOIGOI', 'ontology': 'EFO:0001196',
              'biosample': 'IMR-90', 'directory': OUT},
    'gm12878': {'name': '4dn:4DNFIXP4QG5B', 'ontology': 'EFO:0002784',
                 'biosample': 'GM12878', 'directory': OUT / 'control_gm12878'},
}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temp.replace(path)


def write_fixed(path, data):
    if Path(path).exists():
        if read(path) != data:
            raise ValueError('Existing immutable acquisition record differs')
    else:
        write(path, data)


def safe_error(error):
    return {'error_type': type(error).__name__,
            'grpc_status': error.code().name if isinstance(error, grpc.RpcError) else None}


def log(data):
    data = {'utc': now(), **data}
    line = json.dumps(data, allow_nan=False)
    print(line, flush=True)
    with (OUT / 'acquisition_events.jsonl').open('a') as stream:
        stream.write(line + '\n')


def guarded_inputs():
    if importlib.metadata.version('alphagenome') != '0.9.0':
        raise ValueError('Acquisition requires the documented AlphaGenome client 0.9.0')
    freeze_path = OUT / 'freeze_record.json'
    freeze = read(freeze_path)
    protocol = freeze.get('protocol_file', 'ANALYSIS_PROTOCOL_FROZEN.md')
    required = {'scripts/acquire_portability.py', 'candidate_cohort.json',
                'midpoint_selection.json', protocol}
    files = freeze.get('files', {})
    if not required.issubset(files):
        raise ValueError('Required pre-acquisition freeze entries missing')
    for relative, digest in files.items():
        path = (OUT / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(OUT):
            raise ValueError('Freeze entry outside experiment directory')
        if not isinstance(digest, str) or len(digest) != 64 or sha(path) != digest:
            raise ValueError('Frozen file hash mismatch')
    if sha(OUT / 'candidate_cohort.json') != COHORT_SHA256:
        raise ValueError('Cohort differs from original fixed 84-site cohort')
    cohort = read(OUT / 'candidate_cohort.json')
    sites = cohort['sites']
    mids = read(OUT / 'midpoint_selection.json')['site_ids']
    if len(sites) != N_SITES or len({s['site_id'] for s in sites}) != N_SITES:
        raise ValueError('Unexpected cohort count or duplicates')
    if len(mids) != 7 or len(set(mids)) != 7 or not set(mids).issubset(s['site_id'] for s in sites):
        raise ValueError('Unexpected frozen midpoint selection')
    for index, site in enumerate(sites):
        if site['site_index'] != index or site['alleles'] != [a for a in 'ACGT' if a != site['ref']]:
            raise ValueError('Cohort indexing or allele order mismatch')
        if site['window_end_0based_exclusive'] - site['window_start_0based'] != 2**20:
            raise ValueError('Unexpected frozen window width')
    return freeze, protocol, cohort


def make_manifest(track, protocol, cohort):
    sites = []
    for source in cohort['sites']:
        index = source['site_index']
        cv = source['clinvar_record']
        start = source['window_start_0based']
        original = {'id': f"{source['site_id']}>{source['selected_allele']}",
                    'gene': source['gene'], 'chr': source['chromosome'],
                    'pos': source['position_1based'], 'ref': source['ref'],
                    'alt': source['selected_allele'], 'classification': cv['classification'],
                    'variation_id': cv['variation_id']}
        sites.append({'site_index': index, 'site_id': source['site_id'],
                      'gene': source['gene'], 'hash_sha256': source['hash_sha256'],
                      'original_variant': original,
                      'npz_path': f'sites/site_{index:03d}.npz',
                      'metadata_path': f'sites/site_{index:03d}.json',
                      'alleles': source['alleles'],
                      'selected_allele_index': source['selected_allele_index'],
                      'chromosome': source['chromosome'], 'start': start,
                      'end': source['window_end_0based_exclusive'],
                      'bin_coordinates': [start + j * 2048 for j in range(512)],
                      'selected_consequence': source['selected_consequence']})
    return {'schema_version': 1, 'data_type': 'spatial_log_enrichment_maps',
            'input_kind': 'model_predictions', 'units': 'native_log_enrichment',
            'track': track['name'], 'biosample': track['biosample'],
            'ontology': track['ontology'], 'assay': 'in situ Hi-C',
            'organism': 'HOMO_SAPIENS', 'assembly': 'GRCh38',
            'model_version': 'ALL_FOLDS',
            'model_version_note': 'Explicit API alias; immutable server weight revision unavailable',
            'client_version': importlib.metadata.version('alphagenome'),
            'candidate_sha256': sha(OUT / 'candidate_cohort.json'),
            'protocol_sha256': sha(OUT / protocol),
            'freeze_record_sha256': sha(OUT / 'freeze_record.json'),
            'midpoint_selection_sha256': sha(OUT / 'midpoint_selection.json'),
            'bin_resolution_bp': 2048, 'window_bp': 2**20,
            'coordinate_convention': '0-based half-open genomic bins; variant positions are 1-based',
            'sites': sites}


def validate_call(ref, alt, names):
    if ref.shape != alt.shape or ref.shape != (512, 512, len(names)):
        raise ValueError('Contact output shape mismatch')
    if len(names) != len(set(names)) or set(names) != {t['name'] for t in TRACKS.values()}:
        raise ValueError('Requested contact track set mismatch')
    if not np.isfinite(ref).all() or not np.isfinite(alt).all():
        raise ValueError('Nonfinite contact outputs')
    if not np.array_equal(ref, ref.transpose(1, 0, 2)) or not np.array_equal(alt, alt.transpose(1, 0, 2)):
        raise ValueError('Asymmetric contact outputs')


def acquire_call(client, site, allele):
    index = site['site_index']
    path = OUT / 'calls' / f'site_{index:03d}_{allele}.npz'
    meta_path = path.with_suffix('.json')
    attempts_path = path.with_suffix('.attempts.json')
    history = read(attempts_path) if attempts_path.exists() else []
    variant_id = f"{site['site_id']}>{allele}"
    while not (path.exists() and meta_path.exists()) and len(history) < MAX_ATTEMPTS:
        attempt = len(history) + 1
        history.append({'attempt': attempt, 'started_utc': now(), 'status': 'started'})
        write(attempts_path, history)
        try:
            started = time.monotonic()
            result = client.predict_variant(
                interval=genome.Interval(chromosome=site['chromosome'], start=site['start'], end=site['end']),
                variant=genome.Variant.from_str(variant_id),
                ontology_terms=[t['ontology'] for t in TRACKS.values()],
                requested_outputs=[dna_client.OutputType.CONTACT_MAPS])
            r, a = result.reference.contact_maps, result.alternate.contact_maps
            names = list(r.metadata['name'])
            if names != list(a.metadata['name']) or r.interval != a.interval or r.resolution != 2048 or a.resolution != 2048:
                raise ValueError('REF/ALT track/interval/resolution mismatch')
            if (r.interval.chromosome, r.interval.start, r.interval.end) != (site['chromosome'], site['start'], site['end']):
                raise ValueError('Returned interval differs from frozen interval')
            ref, alt = np.asarray(r.values, dtype=np.float32), np.asarray(a.values, dtype=np.float32)
            validate_call(ref, alt, names)
            temp = path.with_suffix('.tmp.npz')
            np.savez_compressed(temp, ref=ref, alt=alt)
            temp.replace(path)
            write(meta_path, {'variant_id': variant_id, 'completed_utc': now(),
                              'seconds': time.monotonic() - started, 'attempt': attempt,
                              'npz_sha256': sha(path), 'shape': list(ref.shape),
                              'track_names': names, 'model_version': 'ALL_FOLDS',
                              'client_version': importlib.metadata.version('alphagenome'),
                              'interval': {'chromosome': site['chromosome'], 'start': site['start'], 'end': site['end']},
                              'resolution_bp': 2048,
                              'freeze_record_sha256': sha(OUT / 'freeze_record.json')})
            history[-1].update(status='complete', completed_utc=now())
            write(attempts_path, history)
        except Exception as error:
            history[-1].update(status='failed', completed_utc=now(), **safe_error(error))
            write(attempts_path, history)
            log({'status': 'call_retry' if attempt < MAX_ATTEMPTS else 'call_failed',
                 'site_index': index, 'allele': allele, 'attempt': attempt, **safe_error(error)})
            if attempt < MAX_ATTEMPTS:
                time.sleep(2**(attempt - 1))
    if not (path.exists() and meta_path.exists()):
        return None
    meta = read(meta_path)
    if meta['npz_sha256'] != sha(path) or meta['variant_id'] != variant_id or meta['freeze_record_sha256'] != sha(OUT / 'freeze_record.json'):
        raise ValueError('Cached call integrity/protocol mismatch')
    with np.load(path, allow_pickle=False) as data:
        ref, alt = data['ref'], data['alt']
    validate_call(ref, alt, meta['track_names'])
    return ref, alt, meta


def write_site(track, site, calls):
    index = site['site_index']
    path = track['directory'] / site['npz_path']
    metadata_path = track['directory'] / site['metadata_path']
    refs, alts = [], []
    for ref, alt, meta in calls:
        channel = meta['track_names'].index(track['name'])
        refs.append(ref[..., channel])
        alts.append(alt[..., channel])
    arrays = {'ref': refs[0], 'alt': np.stack(alts), 'ref_repeats': np.stack(refs)}
    if path.exists() and metadata_path.exists():
        metadata = read(metadata_path)
        if metadata['npz_sha256'] != sha(path) or metadata['site_id'] != site['site_id'] or metadata['track'] != track['name']:
            raise ValueError('Existing site metadata/hash mismatch')
        with np.load(path, allow_pickle=False) as old:
            if any(not np.array_equal(old[key], value) for key, value in arrays.items()):
                raise ValueError('Existing site differs from its cached calls')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.tmp.npz')
        np.savez_compressed(temp, **arrays)
        temp.replace(path)
        write(metadata_path, {'site_id': site['site_id'], 'gene': site['gene'],
                              'original_variant': site['original_variant'], 'alleles': site['alleles'],
                              'selected_allele_index': site['selected_allele_index'],
                              'npz_sha256': sha(path), 'track': track['name'],
                              'reference_repeat_max_abs_difference': max(float(np.max(np.abs(x - refs[0]))) for x in refs),
                              'calls': [item[2] for item in calls], 'completed_utc': now(),
                              'freeze_record_sha256': sha(OUT / 'freeze_record.json')})
    return arrays


def compare_control(site, fresh):
    old_path = LEGACY / 'sites' / f"site_{site['site_index']:03d}.npz"
    old_meta_path = old_path.with_suffix('.json')
    old_meta = read(old_meta_path)
    if old_meta['npz_sha256'] != sha(old_path) or old_meta['site_id'] != site['site_id']:
        raise ValueError('Historical control input integrity mismatch')
    details = {}
    with np.load(old_path, allow_pickle=False) as old:
        for key in ('ref', 'ref_repeats', 'alt'):
            if old[key].shape != fresh[key].shape:
                raise ValueError('Historical/fresh control shape mismatch')
            delta = fresh[key].astype(np.float64) - old[key].astype(np.float64)
            per_map = [float(np.max(np.abs(value))) for value in delta] if key != 'ref' else [float(np.max(np.abs(delta)))]
            details[key] = {'array_equal': bool(np.array_equal(old[key], fresh[key])),
                            'maximum_absolute_difference': float(np.max(np.abs(delta))),
                            'per_map_maximum_absolute_difference': per_map,
                            'different_elements': int(np.count_nonzero(delta))}
    return {'site_index': site['site_index'], 'site_id': site['site_id'],
            'historical_npz_sha256': sha(old_path),
            'fresh_npz_sha256': sha(TRACKS['gm12878']['directory'] / site['npz_path']),
            'arrays': details, 'all_arrays_equal': all(x['array_equal'] for x in details.values()),
            'maximum_absolute_difference': max(x['maximum_absolute_difference'] for x in details.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Check frozen inputs and exit without network access or writing manifests.')
    args = parser.parse_args()
    freeze, protocol, cohort = guarded_inputs()
    if args.check_only:
        print(json.dumps({'status': 'frozen_inputs_valid', 'n_sites': N_SITES,
                          'protocol': protocol, 'network_requests': 0}))
        return 0
    manifests = {}
    for key, track in TRACKS.items():
        track['directory'].mkdir(parents=True, exist_ok=True)
        manifests[key] = make_manifest(track, protocol, cohort)
        write_fixed(track['directory'] / 'manifest.json', manifests[key])
    (OUT / 'calls').mkdir(exist_ok=True)
    provenance_path = OUT / 'acquisition_provenance.json'
    if not provenance_path.exists():
        write(provenance_path, {'started_utc': now(), 'pid': os.getpid(),
                               'client_version': importlib.metadata.version('alphagenome'),
                               'model_alias': 'ALL_FOLDS', 'immutable_server_revision_available': False,
                               'acquisition_script_sha256': sha(__file__),
                               'freeze_record_sha256': sha(OUT / 'freeze_record.json'),
                               'track_selection': {key: {k: v for k, v in track.items() if k != 'directory'} for key, track in TRACKS.items()},
                               'max_attempts_per_allele': MAX_ATTEMPTS, 'request_timeout_seconds': 60,
                               'retry_delays_seconds': [1, 2, 4, 8],
                               'raw_errors_logged': False})
    client = dna_client.create(os.environ['ALPHAGENOME_API_KEY'],
                               model_version=dna_client.ModelVersion.ALL_FOLDS, timeout=60)
    failed, drift = [], []
    for site in manifests['imr90']['sites']:
        calls = []
        for allele in site['alleles']:
            call = acquire_call(client, site, allele)
            if call is None:
                failed.append({'site_id': site['site_id'], 'allele': allele})
            else:
                calls.append(call)
        if len(calls) != 3:
            log({'status': 'site_incomplete', 'site_index': site['site_index']})
            continue
        for key, track in TRACKS.items():
            arrays = write_site(track, site, calls)
            if key == 'gm12878':
                drift.append(compare_control(site, arrays))
        log({'status': 'site_complete', 'site_index': site['site_index'], 'site_id': site['site_id'],
             'gm12878_arrays_equal_to_historical': drift[-1]['all_arrays_equal'],
             'gm12878_maximum_absolute_difference': drift[-1]['maximum_absolute_difference']})
    complete = len(drift) == N_SITES and not failed
    any_drift = any(not row['all_arrays_equal'] for row in drift)
    write(OUT / 'gm12878_drift_control.json', {
        'status': 'complete' if complete else 'incomplete', 'n_sites_compared': len(drift),
        'all_arrays_equal': complete and not any_drift,
        'n_sites_with_differences': sum(not row['all_arrays_equal'] for row in drift),
        'maximum_absolute_difference': max((row['maximum_absolute_difference'] for row in drift), default=None),
        'comparison_covers': ['site_ref', 'all_three_ref_repeats', 'all_three_alternates'],
        'historical_comparator_valid_without_rerun': complete and not any_drift,
        'fresh_control_analysis_required': any_drift,
        'interpretation': 'Decoded array equality checks contemporary delivered outputs; it does not identify immutable server weights.',
        'sites': drift, 'completed_utc': now()})
    for key, track in TRACKS.items():
        write(track['directory'] / 'acquisition_complete.json', {
            'status': 'complete' if complete else 'incomplete', 'n_sites': len(drift),
            'n_alternate_maps': 3 * len(drift), 'n_stored_ref_maps': 3 * len(drift),
            'n_unique_site_references': len(drift), 'n_planned_variant_calls': 252,
            'n_tracks_per_variant_call': 2, 'track': track['name'], 'failed_calls': failed,
            'manifest_sha256': sha(track['directory'] / 'manifest.json'), 'completed_utc': now()})
    log({'status': 'complete' if complete else 'incomplete', 'n_sites': len(drift),
         'n_failed_calls': len(failed), 'gm12878_any_drift': any_drift})
    return 0 if complete else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        log({'status': 'fatal_failure', **safe_error(error)})
        raise SystemExit(1)
