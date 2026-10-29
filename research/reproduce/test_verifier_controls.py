#!/usr/bin/env python3
"""Exercise scalar-verifier failure modes without model calls or PH recomputation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    if sys.flags.optimize:
        raise SystemExit('Run these controls without Python optimization.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    checks = []
    clean_env = os.environ.copy()
    clean_env.pop('PYTHONOPTIMIZE', None)

    def run(data_dir, flags=(), optimize_env=None, output=None):
        env = clean_env.copy()
        isolation = ['-I']
        if optimize_env is not None:
            env['PYTHONOPTIMIZE'] = optimize_env
            isolation = []
        command = [sys.executable, *isolation, *flags, str(ROOT / 'verify_derived_results.py'),
                   '--data-dir', str(data_dir)]
        if output is not None:
            command += ['--output', str(output)]
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, env=env)

    def endpoint(name, mutate):
        return (name, 'endpoint_scalars.json', mutate)

    def path(name, mutate):
        return (name, 'exploratory_path_scalars.json', mutate)

    with tempfile.TemporaryDirectory(prefix='anchor-scalar-controls-') as temp:
        temp = Path(temp)
        output = temp / 'positive.json'
        positive = run(ROOT / 'data', output=output)
        if positive.returncode != 0:
            raise RuntimeError('Unmodified data failed: ' + positive.stderr)
        expected_bytes = (ROOT / 'DERIVED_VERIFICATION.json').read_bytes()
        if output.read_bytes() != expected_bytes:
            raise RuntimeError('Result changed from the preserved scalar-verification receipt.')
        positive_sha = hashlib.sha256(output.read_bytes()).hexdigest()
        mutations = [
            endpoint('centered_score_outside_interval', lambda d: d['records'][0]['centered'].__setitem__(0, 100.0)),
            endpoint('missing_site', lambda d: d['records'].pop()),
            endpoint('wrong_selected_label', lambda d: d['records'][0].__setitem__('selected_allele_index', (d['records'][0]['selected_allele_index'] + 1) % 3)),
            endpoint('wrong_witness', lambda d: d['records'][0]['shifted_hausdorff'].__setitem__(0, 100.0)),
            ('wrong_expected_count', 'expected_results.json', lambda d: d['by_tolerance']['1e-06']['summary'].__setitem__('simple_unique_leaders', -999)),
            endpoint('extra_delta', lambda d: d['records'][0]['deltas'].append(0.0)),
            endpoint('extra_witness', lambda d: d['records'][0]['shifted_hausdorff'].append(0.0)),
            endpoint('extra_baseline_score', lambda d: d['records'][0]['baselines']['native_rms'].append(0.0)),
            endpoint('nonfinite_score', lambda d: d['records'][0]['native'].__setitem__(0, float('nan'))),
            path('unlinked_path_delta', lambda d: d['comparisons'][0].__setitem__('delta', 1.0)),
            path('unlinked_path_native_endpoint', lambda d: d['comparisons'][0].__setitem__('native_distance', 1.0)),
            path('unlinked_path_centered_endpoint', lambda d: d['comparisons'][0].__setitem__('centered_distance', 1.0)),
            path('changed_path_start_sample', lambda d: d['comparisons'][0]['grid'][0].__setitem__('distance', 1.0)),
            path('changed_path_end_sample', lambda d: d['comparisons'][0]['grid'][-1].__setitem__('distance', 1.0)),
        ]
        for name, filename, mutate in mutations:
            data_dir = temp / name
            shutil.copytree(ROOT / 'data', data_dir)
            value = json.loads((data_dir / filename).read_text())
            mutate(value)
            (data_dir / filename).write_text(json.dumps(value))
            result = run(data_dir)
            if result.returncode == 0 or 'PASS_DERIVED_RESULTS_ONLY' in result.stdout:
                raise RuntimeError('Corrupted input was not rejected: ' + name)
            checks.append({'name': name, 'rejected': True, 'exit_code': result.returncode})
        for name, flags, optimize_env in [('python_O', ['-O'], None),
                                          ('python_OO', ['-OO'], None),
                                          ('inherited_PYTHONOPTIMIZE', [], '1')]:
            result = run(ROOT / 'data', flags, optimize_env)
            if result.returncode == 0 or 'Verification requires assertions' not in result.stderr:
                raise RuntimeError('Optimized mode did not fail safely: ' + name)
            checks.append({'name': name, 'rejected': True, 'exit_code': result.returncode})
    receipt = {'status': 'PASS_SCALAR_VERIFIER_CONTROLS', 'python_version': sys.version.split()[0],
               'positive_matches_preserved_result_byte_for_byte': True,
               'positive_result_sha256': positive_sha, 'negative_controls': checks,
               'negative_control_count': len(checks),
               'scope': 'Scalar-verifier regression controls only; no model calls, PH, witness recomputation or new statistical inference.'}
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': receipt['status'], 'negative_control_count': len(checks),
                      'positive_matches_preserved_result_byte_for_byte': True}))


if __name__ == '__main__':
    main()
