#!/usr/bin/env python3
"""Export a private review bundle; no network requests or raw-map copies."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study-root', type=Path, required=True)
    args = parser.parse_args()
    root = args.study_root.resolve()
    source = root / 'portability_imr90_2026-10-28'
    output = Path(__file__).resolve().parent
    records = []
    origins = []
    for path in sorted((source / 'site_analysis').glob('site_*.json')):
        item = json.loads(path.read_text())
        predictions = item['native_prediction']
        records.append({
            'site_index': item['site_index'], 'gene': item['gene'],
            'selected_allele_index': item['selected_allele_index'],
            'native': item['representations']['native']['distances'],
            'centered': item['representations']['centered']['distances'],
            'deltas': [x['delta'] for x in item['pair_diagnostics']],
            'shifted_hausdorff': [x['shifted_hausdorff_lower_bound'] for x in predictions['witnesses']],
            'baselines': item['baselines'],
            'locked_lower': predictions['lower'],
            'locked_strengthened_lower': predictions['strengthened_lower'],
            'locked_upper': predictions['upper'],
            'locked_rank_sets': predictions['by_tolerance'],
            'midpoint_checks': [dict(alternate_index=x['alternate_index'], **x['midpoint_check'])
                                for x in item['pair_diagnostics'] if 'midpoint_check' in x],
            'original_site_artifact_sha256': digest(path),
        })
        origins.append({'relative_source': str(path.relative_to(root)), 'sha256': digest(path)})
    write(output / 'data/endpoint_scalars.json', {
        'scope': 'Derived endpoint scalars; no maps, diagrams, sequences or genomic coordinates. Not a full PH dataset.',
        'biosample': 'IMR-90', 'track': '4dn:4DNFIJTOIGOI',
        'model_alias': 'ALL_FOLDS', 'practical_allowance': 1e-12,
        'publication_status': 'Private review candidate; applicable output derivative terms require confirmation before release.',
        'records': records,
    })
    summary = json.loads((source / 'portability_summary.json').read_text())
    write(output / 'data/expected_results.json', {
        'by_tolerance': {k: {'summary': v['summary'], 'criteria': v['criteria'],
                            'per_gene': v['per_gene'], 'leave_one_gene_out': v['leave_one_gene_out']}
                         for k, v in summary['by_tolerance'].items()},
        'secondary': summary['secondary'],
        'source_summary_sha256': digest(source / 'portability_summary.json'),
    })
    paths = json.loads((source / 'post_result_path_diagnostics.json').read_text())
    clean_paths = []
    for record in paths['comparisons']:
        clean_paths.append({k: record[k] for k in ('site_index', 'alternate_index', 'gene', 'delta',
            'native_distance', 'centered_distance', 'sampled_shape', 'maximum_absolute_chord_departure')})
        clean_paths[-1]['grid'] = [{'lambda': row['lambda'], 'distance': row['distance']} for row in record['grid']]
    write(output / 'data/exploratory_path_scalars.json', {
        'scope': 'Post-result exploratory diagnostic of all three saturation exceptions; not confirmatory.',
        'comparisons': clean_paths, 'source_sha256': digest(source / 'post_result_path_diagnostics.json')})
    source_files = [
        'scripts/analyze_spatial_maps.py', 'anchor_method/certify_increasing_branch.py',
        'anchor_method/prospective_engine.py',
    ]
    source_files += ['portability_imr90_2026-10-28/scripts/' + name for name in (
        'phased_engine.py', 'test_phased_engine.py', 'summarize_portability.py',
        'compare_reference_replay.py', 'diagnose_nonsaturation.py', 'audit_portability_acquisition.py')]
    for relative in source_files:
        origin = root / relative
        target = output / 'analysis_source' / relative.replace('portability_imr90_2026-10-28/', 'portability/')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, target)
        origins.append({'relative_source': relative, 'bundle_file': str(target.relative_to(output)),
                        'source_sha256': digest(origin), 'bundle_sha256': digest(target), 'adaptation': None})
    origin = source / 'scripts/acquire_portability.py'
    text = origin.read_text()
    text = text.replace("OUT = Path(__file__).resolve().parents[1]", "OUT = Path(os.environ.get('ANCHOR_ACQUISITION_DIR', str(Path(__file__).resolve().parents[1]))).resolve()")
    text = text.replace("LEGACY = REWORK / 'anchor_method' / 'replication'", "LEGACY = Path(os.environ.get('ANCHOR_LEGACY_DIR', str(REWORK / 'anchor_method' / 'replication')))")
    old = next(line for line in text.splitlines() if line.startswith('PROJECT = '))
    text = text.replace(old, '# Acquisition credentials are supplied by the caller, never packaged.')
    text = text.replace("(PROJECT / 'secrets' / 'atlas_api_key.txt').read_text().strip()", "os.environ['ALPHAGENOME_API_KEY']")
    target = output / 'analysis_source/portability/scripts/acquire_portability.py'
    target.write_text(text)
    origins.append({'relative_source': str(origin.relative_to(root)), 'bundle_file': str(target.relative_to(output)),
                    'source_sha256': digest(origin), 'bundle_sha256': digest(target),
                    'adaptation': 'Replace author-specific project/credential location with environment variables; add output/legacy environment overrides. Historical freeze cannot authorize this different script hash; a fresh acquisition must freeze it explicitly.'})
    for name in ('PORTABILITY_PROTOCOL_FROZEN.md', 'POST_RESULT_PATH_PROTOCOL.md', 'candidate_cohort.json',
                 'midpoint_selection.json', 'freeze_record.json', 'analysis_code_freeze.json', 'native_predictions_lock.json'):
        origin = source / name
        target = output / 'provenance' / name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(origin, target)
        origins.append({'relative_source': str(origin.relative_to(root)), 'bundle_file': str(target.relative_to(output)),
                        'source_sha256': digest(origin), 'bundle_sha256': digest(target), 'adaptation': None})
    for name in ('requirements_final.lock', 'requirements.hashed.lock'):
        origin = root / 'full_validation_2026-10-28/reproduction' / name
        target = output / name
        if name == 'requirements.hashed.lock':
            target.write_text('\n'.join(line for line in origin.read_text().splitlines()
                                        if '/Users/' not in line and '/home/' not in line) + '\n')
        else:
            shutil.copy2(origin, target)
        origins.append({'relative_source': str(origin.relative_to(root)), 'bundle_file': str(target.relative_to(output)),
                        'source_sha256': digest(origin), 'bundle_sha256': digest(target),
                        'adaptation': 'Remove machine-specific generation-command comment only.' if name == 'requirements.hashed.lock' else None})
    write(output / 'SOURCE_PROVENANCE.json', {'sources': origins,
        'raw_prediction_maps_included': False, 'persistence_diagrams_included': False,
        'historical_locks_are_evidence_not_replay_authorization': True})


if __name__ == '__main__':
    main()
