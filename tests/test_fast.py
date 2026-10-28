"""Optional Hera/cKDTree parity checks; skipped without the fast extra."""

import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

from anchor_audit import MAX_FAST_DIAGRAM_POINTS, audit_site, bottleneck, hausdorff

ROOT = Path(__file__).resolve().parents[1]
HAS_FAST = all(importlib.util.find_spec(name) is not None for name in ("gudhi", "numpy", "scipy"))


class BackendSelectionTests(unittest.TestCase):
    def test_reject_unknown_backend(self):
        for operation in (bottleneck, hausdorff):
            with self.assertRaisesRegex(ValueError, "backend"):
                operation([], [], backend="unknown")

    def test_reference_backend_metadata(self):
        site = {"id": "empty", "reference": [], "alternates": [{"id": "A", "diagram": [], "delta": 0}]}
        self.assertEqual(audit_site(site, steps=2)["backend"], {"name": "reference", "libraries": {}})


@unittest.skipUnless(HAS_FAST, "Optional fast dependencies are not installed")
class FastBackendTests(unittest.TestCase):
    def test_twenty_random_pairs_and_known_controls(self):
        rng = random.Random(95172)
        pairs = [([], []), ([], [[0, 4]]), ([[0, 4]], []),
                 ([[0, 4], [0, 4]], [[0, 4]]),
                 ([[1, 1], [0, 4]], [[0, 4], [10, 10]])]
        for _ in range(20):
            diagrams = []
            for _ in range(2):
                diagram = []
                for _ in range(rng.randrange(1, 8)):
                    birth = rng.randrange(-16, 17)/8
                    diagram.append([birth, birth+rng.randrange(17)/8])
                diagrams.append(diagram)
            pairs.append(tuple(diagrams))
        for D, E in pairs:
            self.assertAlmostEqual(bottleneck(D, E, backend="hera"), bottleneck(D, E), places=12)
            self.assertAlmostEqual(hausdorff(D, E, backend="hera"), hausdorff(D, E), places=12)

    def test_audit_and_cli_metadata(self):
        data = json.loads((ROOT/"examples/synthetic.json").read_text())
        for site in data["sites"]:
            reference, fast = audit_site(site, steps=5), audit_site(site, steps=5, backend="hera")
            self.assertEqual(reference["rankings"], fast["rankings"])
            for a, b in zip(reference["alternatives"], fast["alternatives"]):
                self.assertAlmostEqual(a["centered"], b["centered"], places=12)
                self.assertAlmostEqual(a["native"], b["native"], places=12)
                self.assertAlmostEqual(a["hausdorff"], b["hausdorff"], places=12)
            self.assertEqual(fast["backend"]["name"], "hera")
            self.assertEqual(set(fast["backend"]["libraries"]), {"gudhi", "numpy", "scipy"})
        command = [sys.executable, "-m", "anchor_audit", str(ROOT/"examples/minimal.json"), "--backend", "hera", "--steps", "3"]
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["backend"]["name"], "hera")

    def test_larger_diagrams_and_resource_limit(self):
        D = [[i/8, i/8+1] for i in range(512)]
        self.assertEqual(bottleneck(D, D, backend="hera"), 0)
        self.assertEqual(hausdorff(D, D, backend="hera"), 0)
        self.assertEqual(bottleneck([[0, 4]]*8_000, [], backend="hera"), 2)
        for operation in (bottleneck, hausdorff):
            with self.assertRaises(ValueError):
                operation([[0, 1]]*(MAX_FAST_DIAGRAM_POINTS+1), [], backend="hera")
            with self.assertRaises(ValueError):
                operation([[-1e308, -1e308]], [[1e308, 1e308]], backend="hera")


if __name__ == "__main__":
    unittest.main()
