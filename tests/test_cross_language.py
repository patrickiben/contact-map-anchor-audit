"""Cross-language behavior plus an independent rational partial-matching oracle.

Run with ``python3 -m unittest discover -s tests -p test_cross_language.py -v``.
Node is a development test dependency only. No test outputs are persisted.
The browser's smaller resource caps are intentional and tested separately.
"""

from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import unittest

from anchor_audit import audit_site, bottleneck, endpoint_bounds, interval_ranking, top_set

ROOT = Path(__file__).resolve().parents[1]
NODE_RUNNER = r"""
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
const core = await import(pathToFileURL(process.argv[1]).href);
const calls = JSON.parse(fs.readFileSync(0, 'utf8'));
const answers = calls.map(({op,args=[],options={}}) => {
  try {
    let result;
    if(op==='auditSite') result=core.auditSite(args[0], options);
    else if(op==='nonfinite') result=core.bottleneck([[0,Number.NaN]], []);
    else result=core[op](...args);
    return {ok:true,result};
  } catch(error) { return {ok:false,error:String(error.message)}; }
});
process.stdout.write(JSON.stringify(answers));
"""


def javascript(calls):
    run = subprocess.run(
        [shutil.which("node"), "--input-type=module", "-e", NODE_RUNNER, str(ROOT/"docs/core.mjs")],
        input=json.dumps(calls, allow_nan=False), text=True, capture_output=True,
        cwd=ROOT, timeout=60,
    )
    if run.returncode:
        raise AssertionError(run.stderr)
    return json.loads(run.stdout)


def rational_oracle(D, E):
    """Enumerate choices of paired subsets and bijections, never a graph solver."""
    D, E = [[tuple(map(Fraction, point)) for point in points] for points in (D, E)]
    best = None
    for size in range(min(len(D), len(E))+1):
        for left in itertools.combinations(range(len(D)), size):
            for right in itertools.permutations(range(len(E)), size):
                costs = [(d-b)/2 for i, (b, d) in enumerate(D) if i not in left]
                costs += [(d-b)/2 for j, (b, d) in enumerate(E) if j not in right]
                costs += [max(abs(D[i][0]-E[j][0]), abs(D[i][1]-E[j][1])) for i, j in zip(left, right)]
                candidate = max(costs, default=Fraction(0))
                best = candidate if best is None else min(best, candidate)
    return float(best)


@unittest.skipUnless(shutil.which("node"), "Node is needed for optional browser/Python parity checks")
class CrossLanguageTests(unittest.TestCase):
    def assertNestedClose(self, actual, expected, path="report"):
        if isinstance(expected, bool) or expected is None or isinstance(expected, str):
            self.assertEqual(actual, expected, path)
        elif isinstance(expected, (int, float)):
            self.assertTrue(math.isfinite(actual), path)
            self.assertTrue(math.isclose(actual, expected, rel_tol=2e-14, abs_tol=2e-14), f"{path}: {actual} != {expected}")
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected), path)
            for i, (left, right) in enumerate(zip(actual, expected)):
                self.assertNestedClose(left, right, f"{path}[{i}]")
        elif isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected), path)
            for key in expected:
                self.assertNestedClose(actual[key], expected[key], f"{path}.{key}")
        else:
            raise AssertionError(f"Unsupported comparison type: {type(expected)}")

    def test_matching_against_independent_rational_enumeration(self):
        rng = random.Random(819231)
        pairs = [([], []), ([[0, 4], [0, 4]], [[0, 4]]), ([[0, 0]], [[1, 1]]),
                 ([[0.1, 0.7]], [[0.2, 0.8]])]
        for _ in range(100):
            diagrams = []
            for _ in range(2):
                diagram = []
                for _ in range(rng.randrange(5)):
                    birth = rng.randrange(-10, 11)/10
                    diagram.append([birth, birth+rng.randrange(15)/10])
                diagrams.append(diagram)
            pairs.append(tuple(diagrams))
        answers = javascript([{"op": "bottleneck", "args": pair} for pair in pairs])
        for (D, E), answer in zip(pairs, answers):
            self.assertTrue(answer["ok"], answer)
            exact = rational_oracle(D, E)
            self.assertAlmostEqual(answer["result"], exact, places=13)
            self.assertAlmostEqual(bottleneck(D, E), exact, places=13)

    def test_random_full_reports_and_hostile_identifiers(self):
        rng = random.Random(1073)
        sites = json.loads((ROOT/"examples/synthetic.json").read_text())["sites"]
        # Object prototype names must remain ordinary IDs, and integer-like
        # strings must preserve the input order in published top-set arrays.
        sites.append({"id": "constructor", "reference": [], "selected": "__proto__",
                      "alternates": [{"id": key, "diagram": [], "delta": 0}
                                     for key in ("10", "2", "__proto__", "constructor", "nan")]})
        for index in range(70):
            def diagram():
                result = []
                for _ in range(rng.randrange(5)):
                    birth = rng.randrange(-10, 11)/10
                    result.append([birth, birth+rng.randrange(21)/10])
                return result
            site = {"id": f"random-{index}", "reference": diagram(), "alternates": [
                {"id": key, "diagram": diagram(), "delta": rng.randrange(-10, 11)/10}
                for key in ("A", "B", "C")]}
            if index % 2:
                site["selected"] = "B"
            sites.append(site)
        options = {"steps": 7, "tolerance": 0.03, "allowance": 1e-12}
        answers = javascript([{"op": "auditSite", "args": [site], "options": options} for site in sites])
        for site, answer in zip(sites, answers):
            self.assertTrue(answer["ok"], (site["id"], answer))
            expected = audit_site(site, **options)
            actual = answer["result"]
            # Human-readable wording can differ; scientific fields cannot.
            for report in (expected, actual):
                del report["warnings"]
                del report["numeric_scope"]
            self.assertNestedClose(actual, expected, site["id"])

    def test_tolerance_boundaries_and_interval_membership(self):
        scores = {"high": 0.8, "low": 0.3}
        lower, upper = {"__proto__": 0, "constructor": 1}, {"__proto__": 2, "constructor": 1}
        calls = [{"op": "topSet", "args": [scores, 0.5]},
                 {"op": "topSet", "args": [{"high": 1, "low": 0.8}, 0.2]},
                 {"op": "intervalRanking", "args": [lower, upper, 0.1]},
                 {"op": "endpointBounds", "args": [1, 1.25, 0.25, 0.3, 1e-12]}]
        expected = [top_set(scores, 0.5), top_set({"high": 1, "low": 0.8}, 0.2),
                    interval_ranking(lower, upper, 0.1), list(endpoint_bounds(1, 1.25, 0.25, 0.3, 1e-12))]
        for answer, value in zip(javascript(calls), expected):
            self.assertTrue(answer["ok"], answer)
            self.assertNestedClose(answer["result"], value)

    def test_rejection_contract_and_intentional_resource_caps(self):
        valid = {"id": "valid", "reference": [], "alternates": [{"id": "A", "diagram": [], "delta": 0}]}
        calls = [
            {"op": "bottleneck", "args": [[[False, 1]], []]},
            {"op": "bottleneck", "args": [[[-1e308, 1e308]], []]},
            {"op": "bottleneck", "args": [[[-1e308, -1e308]], [[1e308, 1e308]]]},
            {"op": "nonfinite"},
            {"op": "auditSite", "args": [dict(valid, id=" ")]},
            {"op": "auditSite", "args": [{k: v for k, v in valid.items() if k != "id"}]},
            {"op": "auditSite", "args": [dict(valid, selected="missing")]},
            {"op": "auditSite", "args": [valid], "options": {"allowance": 1e308}},
            {"op": "auditSite", "args": [dict(valid, alternates=[{"id": "A", "diagram": [[0, 4]], "delta": 1e20}])]},
            {"op": "auditSite", "args": [dict(valid, alternates=[{"id": "A", "diagram": [[1e20, 1e20]], "delta": 4}])]},
            {"op": "endpointBounds", "args": [1, 1.0000000000000002, 0, 0.5, 0]},
            {"op": "bottleneck", "args": [[[0, 1]]*21, []]},
            {"op": "auditSite", "args": [valid], "options": {"steps": 202}},
        ]
        for call, answer in zip(calls, javascript(calls)):
            self.assertFalse(answer["ok"], (call, answer))
        # Python deliberately supports larger workloads than the UI.
        self.assertEqual(bottleneck([[0, 1]]*21, []), 0.5)
        self.assertEqual(len(audit_site(valid, steps=202)["alternatives"][0]["path"]), 202)

    def test_numerical_magnitude_and_rounding_parity(self):
        cases = [
            ("bottleneck", [[], [[0, 5e-324]]], bottleneck),
            ("bottleneck", [[[1e16, 1e16+4]], [[1e16+2, 1e16+6]]], bottleneck),
            ("endpointBounds", [0, 0, 1e308, 1, 0], endpoint_bounds),
            ("endpointBounds", [1e308, 1e308, 1e308, 0.5, 1e308], endpoint_bounds),
            ("endpointBounds", [5e-324, 0, 5e-324, 0.5, 0], endpoint_bounds),
            ("topSet", [{"a": -1e308}, 1e308], top_set),
            ("intervalRanking", [{"a": 1e308, "b": 0}, {"a": 1e308, "b": 0}, 1e308], interval_ranking),
        ]
        answers = javascript([{"op": op, "args": args} for op, args, _ in cases])
        for (op, args, function), answer in zip(cases, answers):
            try:
                expected = function(*args)
            except ValueError:
                self.assertFalse(answer["ok"], (op, args, answer))
            else:
                self.assertTrue(answer["ok"], (op, args, answer))
                if isinstance(expected, tuple):
                    expected = list(expected)
                self.assertNestedClose(answer["result"], expected)


if __name__ == "__main__":
    unittest.main()
