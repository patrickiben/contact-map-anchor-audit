#!/usr/bin/env python3
"""Independent explicit GF(2) boundary reduction controls for the Julia PH check.

Uses NumPy for input construction and byte conversion; no PH library is imported.
All simplices of dimensions 0, 1 and 2 are reduced with a faces-first tie order.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261028

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')

def canonical(intervals):
    data = np.asarray(intervals, dtype=np.float64).reshape(-1, 2)
    if not np.all(np.isfinite(data)):
        raise AssertionError('Nonfinite interval endpoint')
    if len(data) and not np.all(data[:, 1] > data[:, 0]):
        raise AssertionError('Nonpositive interval included')
    return sorted(map(list, data.tolist()))

def effective_filtration(raw_L):
    matrix = np.asarray(raw_L, dtype=np.float64)
    n = len(matrix)
    assert matrix.shape == (n, n) and n >= 2
    assert np.array_equal(matrix, matrix.T) and np.all(np.isfinite(matrix))
    mask = ~np.eye(n, dtype=bool)
    w = -matrix
    offset = max(0.0, 1.0 - float(w[mask].min()))
    effective = np.zeros((n, n), dtype='<f4', order='F')
    effective[mask] = (w[mask] + offset).astype(np.float32)
    assert np.all(np.isfinite(effective)) and np.all(effective[mask] > 0)
    raw = effective.tobytes(order='F')
    return effective, offset, digest(raw)

def explicit_h1(effective, offset):
    """Standard persistence reduction using integer bitsets for GF(2) columns."""
    n = len(effective)
    simplices = []
    for dimension in range(3):
        for vertices in itertools.combinations(range(n), dimension + 1):
            birth = (float(effective[vertices[0], vertices[0]]) if dimension == 0
                     else max(float(effective[u, v]) for u, v in itertools.combinations(vertices, 2)))
            simplices.append((birth, dimension, vertices))
    simplices.sort(key=lambda row: (row[0], row[1], row[2]))
    index = {vertices: i for i, (_, _, vertices) in enumerate(simplices)}
    reduced_at_pivot = {}
    h1_births, paired_h1 = set(), set()
    pairs = []
    for column_index, (death, dimension, vertices) in enumerate(simplices):
        column = 0
        if dimension:
            for face in itertools.combinations(vertices, dimension):
                row = index[face]
                assert row < column_index, 'Face must precede coface'
                column ^= 1 << row
        while column:
            low = column.bit_length() - 1
            if low not in reduced_at_pivot:
                break
            column ^= reduced_at_pivot[low]
        if not column:
            if dimension == 1:
                h1_births.add(column_index)
            continue
        low = column.bit_length() - 1
        assert low not in reduced_at_pivot
        reduced_at_pivot[low] = column
        birth, birth_dimension, _ = simplices[low]
        assert birth_dimension == dimension - 1
        if birth_dimension == 1:
            assert low in h1_births
            paired_h1.add(low)
            assert death >= birth
            if death > birth:
                pairs.append([birth - offset, death - offset])
    assert h1_births == paired_h1, 'Unexpected essential H1 in complete filtration'
    return canonical(pairs)

def cycle(perimeter, diagonal):
    w = np.full((4, 4), float(diagonal), dtype=np.float64)
    np.fill_diagonal(w, 0.0)
    for u, v in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        w[u, v] = w[v, u] = perimeter
    return w

def named_controls():
    triangle = np.array([[0, -3, 2], [-3, 0, 0], [2, 0, 0]], dtype=float)
    tied = np.full((5, 5), -0.5); np.fill_diagonal(tied, 0)
    double = np.full((8, 8), 20.0); np.fill_diagonal(double, 0)
    double[:4, :4] = cycle(1, 4); double[4:, 4:] = cycle(1, 4)
    inactive = cycle(0, 1); inactive[0, 2] = inactive[2, 0] = 10
    ignored = cycle(-1.8, -0.8); np.fill_diagonal(ignored, [-999, 53, 0, -5])
    c = max(0.0, 1.0 - (-1.8))
    return [
        ('filled_triangle', triangle, [], 'Three vertices have no positive H1 interval.'),
        ('negative_birth_cycle', cycle(-2, -1), [[-2, -1]], 'One four-cycle appears at -2 and is filled at -1.'),
        ('zero_birth_cycle', cycle(0, 1), [[0, 1]], 'Zero raw edge births survive the positive input shift.'),
        ('all_tied_clique', tied, [], 'All simplices enter together; no positive-lifetime H1.'),
        ('duplicate_cycles', double, [[1, 4], [1, 4]], 'Two cycles with identical intervals; multiplicity must remain two.'),
        ('nonmetric_cycle', cycle(1, 10), [[1, 10]], 'Diagonal10 exceeds a two-edge perimeter route2; no metric repair is permitted.'),
        ('inactive_diagonal', inactive, [[0, 1]], 'The other diagonal still fills H1 at1 despite this diagonal moving to10.'),
        ('float32_near_tie_collapse', cycle(0, 2.0**-25), [], 'Adding offset1 then Float32 rounds both edge levels to1.'),
        ('translated_negative_cycle', cycle(-1.5, -0.5), [[-1.5, -0.5]], 'Translate both finite interval endpoints by0.5.'),
        ('ignored_diagonal_values', ignored, [[float(np.float32(1)) - c, float(np.float32(2)) - c]], 'Ignore arbitrary finite diagonal map entries; restore nonbinary Float64 offset.'),
    ]

def random_controls():
    rng = np.random.default_rng(SEED)
    levels = np.array([-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0])
    rows = []
    for i in range(12):
        n = 4 + i % 4
        w = np.zeros((n, n), dtype=float)
        upper = np.triu_indices(n, 1)
        values = rng.choice(levels, size=len(upper[0]))
        values[0], values[1], values[2] = -1.0, 0.0, -1.0
        w[upper] = values; w[(upper[1], upper[0])] = values
        rows.append((f'random_{i:02d}', w, None,
                     'Fixed-seed complete graph; mandatory negative/zero/tied births.'))
    return rows

def verify_result(record, intervals, receipt):
    actual = canonical(intervals)
    if actual != record['expected_intervals']:
        raise AssertionError('Complete interval multiset mismatch')
    if receipt['effective_sha256'] != record['expected_effective_sha256']:
        raise AssertionError('Effective input hash mismatch')
    if float(receipt['offset']) != record['expected_offset']:
        raise AssertionError('Offset mismatch')
    if int(receipt['interval_count']) != len(actual):
        raise AssertionError('Interval count mismatch')
    return True

def mutation_checks(records):
    duplicate = next(x for x in records if x['key'] == 'duplicate_cycles')
    shifted = next(x for x in records if x['key'] == 'negative_birth_cycle')
    rows = []
    for name in ['missing_duplicate', 'changed_endpoint', 'unremoved_offset', 'corrupted_input_hash']:
        rec = shifted if name == 'unremoved_offset' else duplicate
        intervals = copy.deepcopy(rec['expected_intervals'])
        receipt = {'effective_sha256': rec['expected_effective_sha256'],
                   'offset': rec['expected_offset'], 'interval_count': len(intervals)}
        if name == 'missing_duplicate':
            intervals.pop(); receipt['interval_count'] -= 1
        elif name == 'changed_endpoint':
            intervals[0][1] += 0.25
        elif name == 'unremoved_offset':
            intervals = [[b + rec['expected_offset'], d + rec['expected_offset']] for b, d in intervals]
        else:
            receipt['effective_sha256'] = '0' * 64
        try:
            verify_result(rec, intervals, receipt)
        except AssertionError as error:
            rows.append({'name': name, 'rejected': True, 'reason': str(error)})
        else:
            raise AssertionError('Mutation was not rejected: ' + name)
    for rec in records:
        verify_result(rec, rec['expected_intervals'], {'effective_sha256': rec['expected_effective_sha256'],
                      'offset': rec['expected_offset'], 'interval_count': len(rec['expected_intervals'])})
    return rows

def export_controls():
    records = []
    for key, w, hand_expected, reason in named_controls() + random_controls():
        raw_L = np.asfortranarray(-w, dtype='<f8')
        effective, offset, effective_hash = effective_filtration(raw_L)
        intervals = explicit_h1(effective, offset)
        if hand_expected is not None:
            assert intervals == canonical(hand_expected), (key, intervals, hand_expected)
        path = ROOT/'inputs'/'controls'/f'{key}.f64'
        path.parent.mkdir(parents=True, exist_ok=True)
        raw_bytes = raw_L.tobytes(order='F'); path.write_bytes(raw_bytes)
        record = {'key': key, 'n': len(w), 'raw_path': str(path.relative_to(ROOT)),
                  'raw_sha256': digest(raw_bytes), 'expected_effective_sha256': effective_hash,
                  'expected_offset': offset, 'expected_intervals': intervals,
                  'description': reason, 'kind': 'named' if hand_expected is not None else 'seeded_random'}
        if hand_expected is not None:
            record['hand_expected'] = canonical(hand_expected)
        records.append(record)
    assert len(records) == 22
    mutations = mutation_checks(records)
    protocol = ROOT/'PROTOCOL.md'
    manifest = {'records': records, 'schema': 'anchor-julia-controls-v1',
                'algorithm': 'Explicit GF2 boundary-column reduction on every vertex, edge and triangle; faces-first tie order.',
                'random_seed': SEED, 'numpy_version': np.__version__,
                'script_sha256': digest(Path(__file__).read_bytes()),
                'protocol_sha256': digest(protocol.read_bytes()),
                'named_controls': 10, 'seeded_random_controls': 12,
                'named_hand_expected_agreement': True,
                'input_byte_format': 'Little-endian Float64 contact map L=-w, column-major n*n.',
                'effective_byte_format': 'Little-endian Float32 shifted edge births with diagonal0, column-major n*n.',
                'mutation_controls': mutations}
    dump(ROOT/'inputs/control_manifest.json', manifest)
    # The Julia process gets raw inputs and provenance only, never oracle answers.
    dump(ROOT/'inputs/control_runner_manifest.json', {'records': [
        {name: record[name] for name in ('key', 'n', 'raw_path', 'raw_sha256')}
        for record in records]})
    dump(ROOT/'review/CONTROL_ORACLE_SELF_CHECK.json', {'status': 'PASS', 'records': len(records),
          'named_hand_expected_agreement': True, 'mutations': mutations,
          'valid_fixture_acceptances': len(records), 'source_sha256': manifest['script_sha256'],
          'scope': 'Independent small-graph exact GF2 reduction and comparator calibration; no Julia genomic validation inferred.'})
    print(json.dumps({'status': 'PASS', 'controls': len(records), 'named': 10, 'random': 12,
                      'mutations_rejected': len(mutations)}, indent=2))

def compare_outputs(mode):
    manifest = json.loads((ROOT/'inputs/control_manifest.json').read_text())
    checks = []
    for record in manifest['records']:
        base = ROOT/'outputs'/mode/record['key']
        binary, receipt_path = base.with_suffix('.f64'), base.with_suffix('.json')
        receipt = json.loads(receipt_path.read_text())
        assert receipt['key'] == record['key'], 'Receipt key mismatch'
        assert receipt['n'] == record['n'], 'Receipt dimension mismatch'
        assert receipt['raw_sha256'] == record['raw_sha256'], 'Raw input hash mismatch'
        data = binary.read_bytes()
        assert digest(data) == receipt['output_sha256'], 'Output file hash mismatch: ' + record['key']
        intervals = np.frombuffer(data, dtype='<f8').reshape((-1, 2), order='F')
        verify_result(record, intervals, receipt)
        checks.append({'key': record['key'], 'pass': True, 'interval_count': len(intervals)})
    result = {'status': 'PASS', 'mode': mode, 'checks': checks,
              'manifest_sha256': digest((ROOT/'inputs/control_manifest.json').read_bytes()),
              'scope': 'Exact control barcode/effective-input correspondence only.'}
    dump(ROOT/'review'/f'CONTROL_JULIA_COMPARISON_{mode}.json', result)
    print(json.dumps({'status': 'PASS', 'mode': mode, 'controls': len(checks)}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare-mode')
    args = parser.parse_args()
    if args.compare_mode:
        compare_outputs(args.compare_mode)
    else:
        export_controls()

if __name__ == '__main__':
    main()
