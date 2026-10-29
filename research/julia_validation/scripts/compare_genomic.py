"""Compare every Julia interval with the saved Python Ripser output exactly."""
import hashlib
import json
import platform
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]
def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    manifest_path = BASE / "inputs/genomic_manifest.json"
    records = json.loads(manifest_path.read_text())["records"]
    checks = []
    reference_cache = {}
    for record in records:
        row = {"key": record["key"], "pass": False}
        try:
            path = BASE / "outputs/genomic" / (record["key"] + ".f64")
            receipt = json.loads(path.with_suffix(".json").read_text())
            data = path.read_bytes()
            assert digest(data) == receipt["output_sha256"], "Output hash mismatch"
            assert receipt["status"] == "completed", "Incomplete run"
            assert receipt["raw_sha256"] == record["raw_sha256"], "Raw map hash mismatch"
            assert receipt["effective_sha256"] == record["expected_effective_sha256"], "Effective input mismatch"
            assert receipt["offset"] == record["expected_offset"], "Offset mismatch"
            actual = np.frombuffer(data, dtype="<f8").reshape((-1, 2), order="F")
            reference_path = record["expected_diagram"]
            if reference_path not in reference_cache:
                raw = Path(reference_path).read_bytes()
                assert digest(raw) == record["expected_diagram_sha256"], "Stored reference hash mismatch"
                reference_cache[reference_path] = json.loads(raw)
            expected = np.asarray(reference_cache[reference_path]["representations"]["native"][
                "h1_diagrams_ref_then_alts"][record["expected_diagram_index"]], dtype=np.float64).reshape((-1, 2))
            assert np.isfinite(actual).all() and np.all(actual[:, 1] > actual[:, 0]), "Invalid interval"
            assert np.array_equal(actual, actual[np.lexsort((actual[:,1], actual[:,0]))]), "Unsorted output"
            expected = expected[np.lexsort((expected[:,1], expected[:,0]))]
            assert len(actual) == receipt["interval_count"] == record["expected_interval_count"], "Count mismatch"
            row["interval_count"] = len(actual)
            row["mean_absolute_difference"] = abs(receipt["mean"] - record["means"][record["expected_diagram_index"]])
            assert row["mean_absolute_difference"] <= 1e-12, "Mean mismatch"
            row["exact_multiset_equal"] = bool(np.array_equal(actual, expected))
            row["max_endpoint_difference"] = float(np.max(np.abs(actual - expected))) if actual.shape == expected.shape and actual.size else None
            assert row["exact_multiset_equal"], "Complete interval multiset mismatch"
            row["output_sha256"] = receipt["output_sha256"]
            row["ph_seconds"] = receipt["ph_seconds"]
            row["pass"] = True
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        checks.append(row)
    result = {
        "status": "PASS" if len(checks) == 72 and all(r["pass"] for r in checks) else "FAIL",
        "diagrams_tested": len(checks), "diagrams_passed": sum(r["pass"] for r in checks),
        "intervals_compared": sum(r.get("interval_count", 0) for r in checks),
        "max_mean_absolute_difference": max(r.get("mean_absolute_difference", 0) for r in checks),
        "protocol_sha256": digest((BASE / "PROTOCOL.md").read_bytes()),
        "manifest_sha256": digest(manifest_path.read_bytes()),
        "comparator_sha256": digest(Path(__file__).read_bytes()),
        "python": platform.python_version(), "numpy": np.__version__, "checks": checks,
        "scope": "Targeted independent implementation, same Ripser algorithm family; exact effective Float32 inputs and interval multisets."
    }
    (BASE / "outputs/PRIMARY_COMPARISON.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k != "checks"}, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
