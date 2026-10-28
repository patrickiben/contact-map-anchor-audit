#!/usr/bin/env python3
"""Synthetic equivalence and lock-failure controls for the two-phase engine."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / 'scripts'), str(ROOT / 'anchor_method')]
import phased_engine as engine
import prospective_engine as reference


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix='anchor_portability_controls_') as temporary:
        folder = Path(temporary)
        inputs = folder / 'inputs'
        output = folder / 'phased'
        inputs.mkdir()
        cycle = np.array([[0, 1, 2, 1], [1, 0, 1, 2],
                          [2, 1, 0, 1], [1, 2, 1, 0]], dtype=float)
        mask = ~np.eye(4, dtype=bool)
        ref0 = -cycle
        alt0 = np.stack([ref0 + shift * mask for shift in (0.0, 0.25, 2.0)])
        alt1 = np.stack([ref0.copy(), ref0.copy(), ref0.copy()])
        alt1[0, 0, 2] = alt1[0, 2, 0] = -10.0
        alt1[1] = -np.ones((4, 4))
        np.fill_diagonal(alt1[1], 0.0)
        alt1[2, 0, 2] = alt1[2, 2, 0] = -3.0
        fixtures = [(ref0, alt0), (ref0, alt1), (np.zeros((4, 4)), np.zeros((3, 4, 4)))]
        manifest = {'schema_version': 1, 'data_type': 'spatial_log_enrichment_maps',
                    'input_kind': 'synthetic', 'units': 'native_log_enrichment',
                    'track': 'SYNTHETIC_LOCK_CONTROL', 'biosample': 'SYNTHETIC', 'sites': []}
        for i, (ref, alt) in enumerate(fixtures):
            coords = np.arange(4) * 2048
            npz = inputs / f'site_{i:03d}.npz'
            np.savez(npz, ref=ref, alt=alt, bin_coordinates=coords)
            metadata = inputs / f'site_{i:03d}.json'
            site_id = f'synthetic_{i}'
            engine.dump(metadata, {'site_id': site_id, 'npz_sha256': engine.sha(npz)})
            manifest['sites'].append({'site_index': i, 'site_id': site_id, 'gene': 'SYNTHETIC',
                'npz_path': npz.name, 'metadata_path': metadata.name, 'alleles': ['A', 'C', 'G'],
                'selected_allele_index': i, 'bin_coordinates': coords.tolist()})
        manifest_path = inputs / 'manifest.json'
        engine.dump(manifest_path, manifest)
        engine.dump(inputs / 'acquisition_complete.json', {'status': 'synthetic_complete'})
        midpoints = inputs / 'midpoints.json'
        engine.dump(midpoints, {'site_ids': [s['site_id'] for s in manifest['sites']]})
        protocol = inputs / 'protocol.md'
        protocol.write_text('Synthetic implementation checks only. No genomic observations.\n')
        command = [sys.executable, str(HERE / 'phased_engine.py'), '--manifest', str(manifest_path),
            '--output-dir', str(output), '--protocol', str(protocol), '--midpoint-site-ids', str(midpoints),
            '--workers', '2', '--expected-sites', '3', '--expected-midpoint-sites', '3']

        def run(phase, success=True):
            result = subprocess.run(command + ['--phase', phase], capture_output=True, text=True)
            if (result.returncode == 0) != success:
                raise AssertionError({'phase': phase, 'returncode': result.returncode,
                                      'stdout': result.stdout, 'stderr': result.stderr})
            return result

        run('centered', success=False)
        checks.append('centered_phase_rejects_missing_lock')
        run('native')
        native_summary = engine.load(output / 'native_predictions.json')
        assert native_summary['centered_bottleneck_evaluations'] == 0
        assert all(set(r['representations']) == {'native'} for r in native_summary['records'])
        assert not list((output / 'site_analysis').glob('*.json'))
        checks.append('native_phase_contains_no_centered_endpoints')
        lock_before = (output / 'native_predictions_lock.json').read_bytes()
        run('native')
        assert (output / 'native_predictions_lock.json').read_bytes() == lock_before
        checks.append('repeat_native_phase_preserves_lock')
        native_file = output / 'native/site_000.json'
        original = native_file.read_bytes()
        native_file.write_bytes(original + b' ')
        run('centered', success=False)
        native_file.write_bytes(original)
        checks.append('centered_phase_rejects_changed_native_artifact')
        original_protocol = protocol.read_bytes()
        protocol.write_bytes(original_protocol + b'Changed protocol\n')
        run('centered', success=False)
        protocol.write_bytes(original_protocol)
        checks.append('centered_phase_rejects_changed_protocol')
        run('centered')
        result = engine.load(output / 'anchor_replication_summary.json')
        assert result['n_complete_sites'] == 3 and result['n_failed_sites'] == 0
        assert result['summary']['locked_prediction_validation_failures'] == 0
        assert result['summary']['midpoint_checks'] == 9
        assert result['summary']['midpoint_tube_failures'] == 0
        assert (output / 'native_predictions_lock.json').read_bytes() == lock_before
        checks.append('centered_phase_preserves_lock_and_validates_bounds')
        for site in manifest['sites']:
            i = site['site_index']
            legacy = reference.process((site, str(inputs), str(folder / 'reference'), {}, True))
            assert legacy['status'] == 'complete'
            phased = engine.load(output / f'site_analysis/site_{i:03d}.json')
            assert phased['means'] == legacy['means']
            assert phased['baselines'] == legacy['baselines']
            assert phased['lifetime_summaries_ref_then_alts'] == legacy['lifetime_summaries_ref_then_alts']
            assert phased['representations'] == legacy['representations']
            for a, b in zip(phased['pair_diagnostics'], legacy['pair_diagnostics']):
                assert a['native_distance'] == b['native_distance']
                assert a['centered_distance'] == b['centered_distance']
                assert a['midpoint_check'] == b['midpoint_check']
        checks.append('three_synthetic_sites_match_original_scientific_engine')
        assert result['summary']['non_tiny_nonsaturated_pairs'] > 0
        assert result['summary']['midpoint_affine_failures'] > 0
        checks.append('nonsaturation_and_nonaffine_controls_are_detected')
        # A plausible false predicted winner must be rejected by the validator.
        wrong = {'possible_top_members': [2], 'necessary_top_members': [2], 'guaranteed_unique_leaders': [2]}
        assert not engine.validate_prediction(wrong, [3.0, 2.0, 1.0], 1e-6)['passed']
        checks.append('wrong_leader_prediction_is_rejected')
    print(json.dumps({'status': 'PASS', 'checks': checks, 'count': len(checks),
        'scope': 'Synthetic implementation and freeze controls; no new genomic data acquired or inspected.'}, indent=2))


if __name__ == '__main__':
    main()
