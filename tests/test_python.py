"""Independent partial-matching oracle and behavioral tests; no dependencies."""

from copy import deepcopy
from fractions import Fraction
from itertools import combinations_with_replacement
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from anchor_audit import (
    MAX_DIAGRAM_POINTS, audit_site, bottleneck, endpoint_bounds,
    hausdorff, interval_ranking, top_set,
)

ROOT = Path(__file__).resolve().parents[1]


def partial_matching_oracle(D, E):
    """Exhaust every partial real-real matching using exact rational arithmetic.

    Unpaired real points independently go to the diagonal. This algorithm does
    not build or search the production augmented bipartite matching graph.
    """
    D = [tuple(Fraction(x) for x in point) for point in D]
    E = [tuple(Fraction(x) for x in point) for point in E]

    def recurse(index, available, maximum):
        if index == len(D):
            return max([maximum] + [(E[j][1]-E[j][0])/2 for j in available])
        b, d = D[index]
        result = recurse(index+1, available, max(maximum, (d-b)/2))
        for j in available:
            cost = max(abs(b-E[j][0]), abs(d-E[j][1]))
            result = min(result, recurse(index+1, tuple(k for k in available if k != j), max(maximum, cost)))
        return result

    return recurse(0, tuple(range(len(E))), Fraction(0))


def translate(D, t):
    return [[b+t, d+t] for b, d in D]


class BottleneckTests(unittest.TestCase):
    def test_exhaustive_small_rational_diagrams(self):
        points = [(0, 0), (0, Fraction(1, 2)), (0, 2), (1, 2)]
        diagrams = [list(d) for size in range(3) for d in combinations_with_replacement(points, size)]
        for D in diagrams:
            for E in diagrams:
                expected = float(partial_matching_oracle(D, E))
                # The public API accepts ordinary JSON-compatible numbers.
                actual = bottleneck([[float(x) for x in p] for p in D], [[float(x) for x in p] for p in E])
                self.assertEqual(actual, expected, (D, E))

    def test_seeded_larger_random_against_oracle(self):
        rng = random.Random(71831)
        for _ in range(180):
            diagrams = []
            for _ in range(2):
                diagram = []
                for _ in range(rng.randrange(5)):
                    birth = rng.randrange(-8, 9)/4
                    diagram.append([birth, birth+rng.randrange(9)/4])
                diagrams.append(diagram)
            D, E = diagrams
            actual = bottleneck(D, E)
            self.assertEqual(actual, float(partial_matching_oracle(D, E)))
            self.assertEqual(actual, bottleneck(E, D))
            self.assertEqual(actual, bottleneck(translate(D, 16), translate(E, 16)))
            self.assertEqual(2*actual, bottleneck([[2*b, 2*d] for b, d in D], [[2*b, 2*d] for b, d in E]))
            self.assertLessEqual(hausdorff(D, E), actual)
            self.assertEqual(0, bottleneck(D, D))
            self.assertEqual(actual, bottleneck(D+[[27, 27]], E))

    def test_nondyadic_float_inputs_against_rational_oracle(self):
        cases = [([[0.1, 0.7]], [[0.2, 0.8]]),
                 ([[0.1, 0.8], [0.1, 0.8]], [[0.1, 0.8]]),
                 ([[-0.3, 1.2], [0.7, 2.2]], [[0.2, 1.6], [0.4, 0.9]])]
        for D, E in cases:
            self.assertAlmostEqual(bottleneck(D, E), float(partial_matching_oracle(D, E)), places=14)

    def test_multiplicity_empty_and_diagonal(self):
        self.assertEqual(bottleneck([[0, 4], [0, 4]], [[0, 4]]), 2)
        self.assertEqual(hausdorff([[0, 4], [0, 4]], [[0, 4]]), 0)
        self.assertEqual(bottleneck([], []), 0)
        self.assertEqual(bottleneck([], [[0, 4]]), 2)
        self.assertEqual(hausdorff([], [[0, 4]]), 2)
        self.assertEqual(bottleneck([[1, 1]], [[100, 100]]), 0)

    def test_reject_invalid_diagrams_and_overflow(self):
        for invalid in (None, "diagram", [[0]], [[0, 1, 2]], [[2, 1]], [[0, float("inf")]], [[float("nan"), 1]], [[False, 1]], [[0, "1"]], [[0, 1]]*(MAX_DIAGRAM_POINTS+1), [[-1e308, 1e308]]):
            for operation in (bottleneck, hausdorff):
                with self.assertRaises(ValueError, msg=repr(invalid)):
                    operation(invalid, [])
        with self.assertRaises(ValueError):
            bottleneck([[-1e308, -1e308]], [[1e308, 1e308]])


class BoundsAndRankingTests(unittest.TestCase):
    def test_exact_oracle_path_with_endpoint_cones(self):
        D, E, delta = [[0, 4]], [[-0.5, 3.5]], 1
        A, C = float(partial_matching_oracle(D, E)), float(partial_matching_oracle(D, translate(E, delta)))
        for i in range(17):
            lam = i/16
            low, high = endpoint_bounds(A, C, delta, lam)
            exact = float(partial_matching_oracle(D, translate(E, lam*delta)))
            self.assertLessEqual(low, exact)
            self.assertLessEqual(exact, high)
            self.assertEqual([d-b for b, d in E], [d-b for b, d in translate(E, lam*delta)])
        self.assertEqual(endpoint_bounds(1, 1.25, 0.25, 0.5), (1.125, 1.125))
        self.assertEqual(endpoint_bounds(1, 0.75, 0.25, 0.5), (0.875, 0.875))
        with self.assertRaises(ValueError):
            endpoint_bounds(1, 2, 0.25, 0.5)
        for error in (-1, float("nan")):
            with self.assertRaises(ValueError):
                endpoint_bounds(1, 1, 0, 0.5, error)

    def test_inclusive_top_tolerance(self):
        self.assertEqual(top_set({"a": 1, "b": 0.75}, 0.25), ["a", "b"])
        self.assertEqual(top_set({"a": 1, "b": 0.75}, 0.249), ["a"])
        with self.assertRaises(ValueError):
            top_set({"a": 1}, -1)

    def test_interval_membership_exhaustive_corner_vectors(self):
        from itertools import product
        keys = ("a", "b", "c")
        lower = {"a": 0, "b": 0.5, "c": 2}
        upper = {"a": 1, "b": 2, "c": 2.5}
        for tau in (0, 0.5, 1):
            result = interval_ranking(lower, upper, tau)
            top_sets = [set(top_set(dict(zip(keys, vector)), tau)) for vector in product(*[(lower[k], upper[k]) for k in keys])]
            self.assertEqual(set(result["possible"]), set.union(*top_sets))
            self.assertEqual(set(result["guaranteed"]), set.intersection(*top_sets))
            unique = [k for k in keys if all(top == {k} for top in top_sets)]
            self.assertEqual(result["guaranteed_unique"], unique)
        self.assertEqual(interval_ranking({"a": 0}, {"a": 1})["guaranteed_unique"], ["a"])
        with self.assertRaises(ValueError):
            interval_ranking({"a": 2}, {"a": 1})


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.sites = json.loads((ROOT/"examples/synthetic.json").read_text())["sites"]

    def test_known_synthetic_controls(self):
        reports = {site["id"]: audit_site(site, steps=5) for site in self.sites}
        split = reports["tie-split"]
        self.assertEqual(split["rankings"]["native"], ["A", "B", "C"])
        self.assertEqual(split["rankings"]["centered"], ["A"])
        self.assertEqual(split["credits"], {"native": 1/3, "centered": 0})
        opposite = reports["opposite-slopes"]["alternatives"]
        self.assertEqual([a["centered"] for a in opposite], [1.25, 0.75])
        self.assertTrue(all(a["near_saturated"] for a in opposite))
        turn = reports["turning-path"]["alternatives"][0]
        self.assertEqual([p["distance"] for p in turn["path"]], [1, 0.5, 0, 0.5, 1])
        self.assertFalse(turn["near_saturated"])
        cap = reports["diagonal-cap"]["alternatives"][0]
        self.assertEqual([p["distance"] for p in cap["path"]], [0, 0.5, 1, 1, 1])
        multiplicity = reports["multiplicity"]["alternatives"][0]
        self.assertEqual((multiplicity["hausdorff"], multiplicity["native"]), (0.25, 2))
        for report in reports.values():
            for alt in report["alternatives"]:
                self.assertLessEqual(alt["lower"], alt["centered"])
                self.assertLessEqual(alt["centered"], alt["upper"])
                for point in alt["path"]:
                    self.assertLessEqual(point["lower"], point["distance"])
                    self.assertLessEqual(point["distance"], point["upper"])

    def test_no_input_mutation_and_label_does_not_choose_scores(self):
        site = deepcopy(self.sites[0])
        original = deepcopy(site)
        first = audit_site(site)
        self.assertEqual(site, original)
        site["selected"] = "C"
        second = audit_site(site)
        self.assertEqual(first["alternatives"], second["alternatives"])
        self.assertEqual(first["rankings"], second["rankings"])

    def test_random_audit_bounds_and_conditional_rankings(self):
        rng = random.Random(217)
        for trial in range(40):
            def diagram():
                result = []
                for _ in range(rng.randrange(4)):
                    birth = rng.randrange(-4, 5)/4
                    result.append([birth, birth+rng.randrange(9)/4])
                return result
            site = {"id": str(trial), "reference": diagram(), "alternates": [
                {"id": str(i), "diagram": diagram(), "delta": rng.randrange(-4, 5)/4}
                for i in range(3)]}
            report = audit_site(site, steps=9, tolerance=0.125, allowance=0)
            observed_top = set(report["rankings"]["centered"])
            self.assertTrue(observed_top <= set(report["rankings"]["possible_centered"]))
            self.assertTrue(set(report["rankings"]["guaranteed_centered"]) <= observed_top)
            for alternate, result in zip(site["alternates"], report["alternatives"]):
                for point in result["path"]:
                    exact = float(partial_matching_oracle(site["reference"], translate(alternate["diagram"], point["lambda"]*alternate["delta"])))
                    self.assertEqual(point["distance"], exact)
                    self.assertLessEqual(point["lower"], exact)
                    self.assertLessEqual(exact, point["upper"])
            for leader in report["rankings"]["native_margin_leaders"]:
                for index in range(9):
                    scores = {a["id"]: a["path"][index]["distance"] for a in report["alternatives"]}
                    self.assertEqual(top_set(scores, 0.125), [leader])

    def test_validation(self):
        bad = [dict(self.sites[0], alternates=[]), dict(self.sites[0], selected="absent"),
               dict(self.sites[0], alternates=[self.sites[0]["alternates"][0]]*2),
               dict(self.sites[0], id=" "), dict(self.sites[0], reference=None)]
        for site in bad:
            with self.assertRaises(ValueError):
                audit_site(site)
        for options in ({"steps": 1}, {"steps": 2.5}, {"steps": True}, {"tolerance": -1}, {"allowance": -1}):
            with self.assertRaises(ValueError):
                audit_site(self.sites[0], **options)

    def test_translation_rounding_diagnostic(self):
        site = {"id": "lifetime-loss", "reference": [], "alternates": [
            {"id": "A", "diagram": [[0, 4]], "delta": 1e20}]}
        with self.assertRaisesRegex(ValueError, "Translation.*rescale"):
            audit_site(site, steps=3)
        # A declared larger budget permits these stored-coordinate results;
        # this does not prove that every numerical error fits that budget.
        permitted = audit_site(site, steps=3, allowance=8)
        self.assertEqual(permitted["alternatives"][0]["centered"], 0)
        site["alternates"][0] = {"id": "A", "diagram": [[1e20, 1e20]], "delta": 4}
        # The lifetime stays zero, but the intended common addition is lost.
        with self.assertRaisesRegex(ValueError, "Translation rounding"):
            audit_site(site, steps=3)
        audit_site(site, steps=3, allowance=4)
        ordinary = audit_site(self.sites[0], steps=21)
        self.assertAlmostEqual(ordinary["alternatives"][2]["centered"], 1.1)

    def test_translation_residual_against_exact_rational_addition(self):
        rng = random.Random(4192)
        for index in range(100):
            coordinate = rng.randrange(-20, 21)/10 * 10**rng.randrange(-12, 13)
            shift = rng.randrange(-20, 21)/10 * 10**rng.randrange(-12, 13)
            exact_residual = abs(Fraction(coordinate)+Fraction(shift)-Fraction(coordinate+shift))
            site = {"id": str(index), "reference": [], "alternates": [
                {"id": "A", "diagram": [[coordinate, coordinate]], "delta": shift}]}
            if exact_residual:
                with self.assertRaisesRegex(ValueError, "Translation rounding"):
                    audit_site(site, steps=2, allowance=0)
            else:
                audit_site(site, steps=2, allowance=0)
            audit_site(site, steps=2, allowance=float(exact_residual))

    def test_tiny_shift_warns_about_low_information_saturation(self):
        site = {"id": "tiny", "reference": [], "alternates": [{"id": "A", "diagram": [], "delta": 1e-13}]}
        self.assertTrue(any("low-information" in warning for warning in audit_site(site, steps=2)["warnings"]))
        site["alternates"][0]["delta"] = 0
        self.assertFalse(any("low-information" in warning for warning in audit_site(site, steps=2)["warnings"]))

    def test_cli_batch_single_and_no_overwrite(self):
        command = [sys.executable, "-m", "anchor_audit"]
        run = subprocess.run(command+[str(ROOT/"examples/synthetic.json"), "--steps", "3"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(len(json.loads(run.stdout)["sites"]), 5)
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory)/"input.json", Path(directory)/"report.json"
            source.write_text(json.dumps(self.sites[0]))
            before = source.read_bytes()
            good = subprocess.run(command+[str(source), "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(output.read_text())["id"], "tie-split")
            for destination in (source, output):
                rejected = subprocess.run(command+[str(source), "--output", str(destination)], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(rejected.returncode, 2)
            self.assertEqual(source.read_bytes(), before)
            source.write_text('{"id":"a","id":"b"}')
            rejected = subprocess.run(command+[str(source)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("Duplicate JSON", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
