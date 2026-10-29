"""Export fixed raw contact maps. No persistence calculation or PH library imports."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-root", type=Path, default=BASE.parent,
                        help="Extracted full-study archive root containing anchor_method/ and portability_imr90_2026-10-28/")
    args = parser.parse_args()
    inventory = json.loads((BASE / "review/COHORT_SOURCE_INVENTORY.json").read_text())
    out = BASE / "inputs/genomic"
    out.mkdir(exist_ok=True)
    records = []
    for site in inventory["records"]:
        subdir = "anchor_method/replication" if site["track"] == "GM12878" else "portability_imr90_2026-10-28"
        study_dir = args.study_root.resolve() / subdir
        source = study_dir / "sites" / f"site_{site['site_index']:03d}.npz"
        reference = study_dir / "site_analysis" / f"site_{site['site_index']:03d}.json"
        assert digest(source.read_bytes()) == site["map_npz_sha256"]
        assert digest(reference.read_bytes()) == site["reference_output_sha256"]
        saved = json.loads(reference.read_text())
        with np.load(source, allow_pickle=False) as data:
            maps = [data["ref"].astype(np.float64)] + list(data["alt"].astype(np.float64))
        track = "gm12878" if site["track"] == "GM12878" else "imr90"
        for index, raw in enumerate(maps):
            n = raw.shape[0]
            assert raw.shape == (512, 512) and np.array_equal(raw, raw.T) and np.isfinite(raw).all()
            key = f"{track}_site_{site['site_index']:03d}_{'ref' if index == 0 else f'alt{index-1}'}"
            raw_path = out / f"{key}.f64"
            data_bytes = raw.astype("<f8").tobytes(order="F")
            raw_path.write_bytes(data_bytes)
            offdiag = ~np.eye(n, dtype=bool)
            weights = -raw
            offset = max(0.0, 1.0 - float(weights[offdiag].min()))
            weights[offdiag] += offset
            np.fill_diagonal(weights, 0.0)
            effective = weights.astype("<f4")
            assert np.isfinite(effective).all() and (effective[offdiag] > 0).all()
            records.append({
                "key": key, "track": track, "site_index": site["site_index"],
                "site_id": site["site_id"], "gene": site["gene"],
                "allele_index": index - 1, "expected_diagram_index": index,
                "n": n, "raw_path": str(raw_path.relative_to(BASE)),
                "raw_sha256": digest(data_bytes),
                "source_npz": str(source), "source_npz_sha256": site["map_npz_sha256"],
                "expected_effective_sha256": digest(effective.tobytes(order="F")),
                "expected_offset": offset, "expected_diagram": str(reference),
                "expected_diagram_sha256": site["reference_output_sha256"],
                "expected_interval_count": site["diagram_counts"][index],
                "means": saved["means"], "alleles": site["alleles"],
                "selected_allele_index": site["selected_allele_index"],
            })
    assert len(records) == 72 and len({r["key"] for r in records}) == 72
    path = BASE / "inputs/genomic_manifest.json"
    path.write_text(json.dumps({"records": records}, indent=2) + "\n")
    # Julia receives only raw inputs and identifiers, never expected diagrams or endpoints.
    julia_fields = ("key", "n", "raw_path", "raw_sha256")
    (BASE / "inputs/genomic_runner_manifest.json").write_text(json.dumps({
        "records": [{k: r[k] for k in julia_fields} for r in records]
    }, indent=2) + "\n")
    print(json.dumps({"records": len(records), "manifest_sha256": digest(path.read_bytes())}))

if __name__ == "__main__":
    main()
