#!/usr/bin/env python3
"""Prepare or execute this targeted validation in a new, isolated workspace.

No existing run is overwritten. Preparation exports inputs and small control
oracles but does not invoke Julia or perform genomic persistent homology.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import traceback

CAPSULE = Path(__file__).resolve().parents[1]
SCRIPT_NAMES = ('control_oracle.py', 'export_genomic.py', 'run_persistence.jl',
                'compare_genomic.py', 'compare_downstream.py', 'replay.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def utc():
    return datetime.now(timezone.utc).isoformat()


def dump(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temporary.replace(path)


def checked_copy(source, target, expected_sha=None):
    actual = sha(source)
    if expected_sha is not None and actual != expected_sha:
        raise ValueError('Source hash mismatch: ' + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if sha(target) != actual:
        raise ValueError('Copy hash mismatch: ' + str(target))
    return actual


def command(workspace, stage, argv):
    started = time.monotonic()
    log = workspace / 'logs' / (stage + '.log')
    with log.open('w') as stream:
        stream.write(json.dumps({'command': [str(a) for a in argv], 'started_utc': utc()}) + '\n')
        stream.flush()
        proc = subprocess.run([str(a) for a in argv], cwd=workspace, stdout=stream,
                              stderr=subprocess.STDOUT, check=False)
    result = {'stage': stage, 'command': [str(a) for a in argv], 'returncode': proc.returncode,
              'log': str(log.relative_to(workspace)), 'log_sha256': sha(log),
              'elapsed_seconds': time.monotonic() - started, 'completed_utc': utc()}
    dump(workspace / 'logs' / (stage + '.receipt.json'), result)
    if proc.returncode:
        raise RuntimeError(f'{stage} failed with exit {proc.returncode}; see {log}')
    print(stage + ': completed', flush=True)
    return result


def require(condition, description):
    if not condition:
        raise ValueError(description)


def validate_export(workspace):
    controls = load(workspace / 'inputs/control_manifest.json')
    genomics = load(workspace / 'inputs/genomic_manifest.json')
    runner_controls = load(workspace / 'inputs/control_runner_manifest.json')
    runner_genomics = load(workspace / 'inputs/genomic_runner_manifest.json')
    require(len(controls['records']) == 22, 'Expected exactly 22 controls')
    require(controls['named_controls'] == 10 and controls['seeded_random_controls'] == 12,
            'Control composition mismatch')
    require(len(genomics['records']) == 72, 'Expected exactly 72 genomic diagrams')
    require(len(runner_controls['records']) == 22 and len(runner_genomics['records']) == 72,
            'Julia-only manifest count mismatch')
    fields = {'key', 'n', 'raw_path', 'raw_sha256'}
    for manifest in (runner_controls, runner_genomics):
        require(all(set(r) == fields for r in manifest['records']),
                'Julia-only manifest contains unexpected fields or oracle results')
        require(len({r['key'] for r in manifest['records']}) == len(manifest['records']),
                'Duplicate runner key')
        for record in manifest['records']:
            require(sha(workspace / record['raw_path']) == record['raw_sha256'],
                    'Exported raw-input hash mismatch: ' + record['key'])
    oracle = load(workspace / 'review/CONTROL_ORACLE_SELF_CHECK.json')
    require(oracle['status'] == 'PASS' and oracle['records'] == 22,
            'Control oracle self-check did not pass')
    return {'controls': 22, 'genomic_diagrams': 72,
            'control_manifest_sha256': sha(workspace / 'inputs/control_manifest.json'),
            'genomic_manifest_sha256': sha(workspace / 'inputs/genomic_manifest.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path,
                        help='New workspace directory; must not already exist.')
    parser.add_argument('--study-root', type=Path, default=CAPSULE / 'study_inputs',
                        help='Bundled selected study inputs or the full original study root.')
    parser.add_argument('--execute', action='store_true',
                        help='Run Julia controls, full target persistence and downstream checks after preparation.')
    parser.add_argument('--julia', default='julia', help='Julia executable or path.')
    parser.add_argument('--workers', type=int, default=4,
                        help='Parallel genomic shards and downstream workers (default 4).')
    parser.add_argument('--genomic-shards', type=int,
                        help='Override genomic shard count; use 1 for serial Julia execution.')
    args = parser.parse_args()
    if sys.flags.optimize:
        parser.error('Do not use python -O: the frozen comparators include assertion gates.')
    if args.workers < 1 or (args.genomic_shards is not None and args.genomic_shards < 1):
        parser.error('Workers and shards must be positive integers.')
    workspace = args.output.expanduser().resolve()
    if workspace.exists():
        parser.error('--output must be a new directory; existing workspaces are never overwritten.')
    source = args.study_root.expanduser().resolve()
    bundled_manifest_path = CAPSULE / 'study_inputs/BUNDLED_INPUT_MANIFEST.json'
    bundled_manifest = load(bundled_manifest_path)
    require(len(bundled_manifest['files']) == 38, 'Expected 38 bundled original study files')
    # Check all sources before creating the new destination.
    for record in bundled_manifest['files']:
        require(sha(source / record['path']) == record['sha256'],
                'Selected study input mismatch: ' + record['path'])
    workspace.mkdir(parents=True, exist_ok=False)
    for name in ('scripts', 'environment', 'review', 'inputs', 'outputs', 'logs', 'study_inputs'):
        (workspace / name).mkdir()
    state = {'status': 'PREPARING', 'started_utc': utc(), 'execute_requested': args.execute,
             'source_capsule': str(CAPSULE), 'source_study_root': str(source),
             'workspace': str(workspace), 'driver_sha256': sha(__file__),
             'python': platform.python_version(), 'python_executable': sys.executable,
             'tested_python': '3.14.7', 'stages': [], 'genomic_persistence_executed': False,
             'genomic_persistence_completed': False,
             'scope': 'Fresh targeted replay; preparation alone does not establish a new Julia persistence result.'}
    started = time.monotonic()
    try:
        copied = {}
        for name in SCRIPT_NAMES:
            relative = Path('scripts') / name
            copied[str(relative)] = checked_copy(CAPSULE / relative, workspace / relative)
        for relative in (Path('PROTOCOL.md'), Path('review/COHORT_SOURCE_INVENTORY.json'),
                         Path('environment/Project.toml'), Path('environment/Manifest.toml'),
                         Path('environment/requirements-python.txt')):
            copied[str(relative)] = checked_copy(CAPSULE / relative, workspace / relative)
        if (CAPSULE / 'REPLAY.md').exists():
            checked_copy(CAPSULE / 'REPLAY.md', workspace / 'REPLAY.md')
        for record in bundled_manifest['files']:
            relative = Path('study_inputs') / record['path']
            copied[str(relative)] = checked_copy(source / record['path'], workspace / relative,
                                               record['sha256'])
        checked_copy(bundled_manifest_path, workspace / 'study_inputs/BUNDLED_INPUT_MANIFEST.json')
        state['copied_file_sha256'] = copied
        state['python_packages'] = {name: importlib.metadata.version(name)
                                    for name in ('numpy', 'scipy', 'gudhi')}
        dump(workspace / 'REPLAY_STATUS.json', state)
        py = sys.executable
        scripts = workspace / 'scripts'
        state['stages'].append(command(workspace, '01_export_controls', [py, scripts / 'control_oracle.py']))
        state['stages'].append(command(workspace, '02_export_genomic',
                                      [py, scripts / 'export_genomic.py', '--study-root', workspace / 'study_inputs']))
        state['export_validation'] = validate_export(workspace)
        state['status'] = 'PREPARED_NOT_EXECUTED'
        dump(workspace / 'REPLAY_STATUS.json', state)
        if args.execute:
            julia = shutil.which(args.julia)
            require(julia is not None, 'Julia executable not found: ' + args.julia)
            julia_base = [julia, '--startup-file=no', '--project=' + str(workspace / 'environment')]
            state['stages'].append(command(workspace, '03_instantiate_julia',
                                           julia_base + ['-e', 'using Pkg; Pkg.instantiate()']))
            state['stages'].append(command(workspace, '04_julia_controls',
                                           julia_base + [scripts / 'run_persistence.jl', 'controls']))
            state['stages'].append(command(workspace, '05_compare_controls',
                                           [py, scripts / 'control_oracle.py', '--compare-mode', 'controls']))
            control_result = load(workspace / 'review/CONTROL_JULIA_COMPARISON_controls.json')
            require(control_result['status'] == 'PASS' and len(control_result['checks']) == 22
                    and all(r['pass'] for r in control_result['checks']),
                    'Actual Julia control gate did not pass all 22 controls')
            state['controls_passed'] = 22
            state['status'] = 'RUNNING_GENOMIC_PERSISTENCE'
            # True once genomic execution is invoked, even if a later shard fails.
            state['genomic_persistence_executed'] = True
            dump(workspace / 'REPLAY_STATUS.json', state)
            shards = args.genomic_shards or args.workers
            with ThreadPoolExecutor(max_workers=min(args.workers, shards)) as pool:
                futures = [pool.submit(command, workspace, f'06_julia_genomic_shard_{i:02d}',
                            julia_base + [scripts / 'run_persistence.jl', 'genomic', str(i), str(shards)])
                           for i in range(1, shards + 1)]
                for future in as_completed(futures):
                    state['stages'].append(future.result())
            state['genomic_persistence_completed'] = True
            state['stages'].append(command(workspace, '07_compare_genomic',
                                           [py, scripts / 'compare_genomic.py']))
            primary = load(workspace / 'outputs/PRIMARY_COMPARISON.json')
            require(primary['status'] == 'PASS' and primary['diagrams_tested'] == 72
                    and primary['diagrams_passed'] == 72 and len(primary['checks']) == 72
                    and all(r['pass'] and r['exact_multiset_equal'] for r in primary['checks']),
                    'Actual primary persistence gate did not pass all 72 diagrams')
            state['primary_diagrams_passed'] = 72
            state['status'] = 'RUNNING_DOWNSTREAM'
            dump(workspace / 'REPLAY_STATUS.json', state)
            state['stages'].append(command(workspace, '08_downstream',
                [py, scripts / 'compare_downstream.py', '--study-root', workspace / 'study_inputs',
                 '--workers', str(args.workers), '--primary-success-confirmed']))
            downstream = load(workspace / 'outputs/downstream/summary.json')
            require(downstream['status'] == 'passed' and downstream['site_track_count'] == 18
                    and downstream['diagram_count'] == 72 and downstream['ref_alt_pair_count'] == 54,
                    'Downstream stage did not pass the full target')
            state['downstream_site_tracks_passed'] = 18
            state['status'] = 'PASS'
        state['elapsed_seconds'] = time.monotonic() - started
        state['completed_utc'] = utc()
        dump(workspace / 'REPLAY_STATUS.json', state)
        print(json.dumps({k: state[k] for k in ('status', 'workspace', 'genomic_persistence_executed',
                                               'elapsed_seconds')}, indent=2))
        return 0
    except Exception as exc:
        state.update({'status': 'FAIL', 'error_type': type(exc).__name__, 'error': str(exc),
                      'traceback': traceback.format_exc(), 'completed_utc': utc(),
                      'elapsed_seconds': time.monotonic() - started})
        dump(workspace / 'REPLAY_STATUS.json', state)
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
