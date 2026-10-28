#!/usr/bin/env python3
"""Offline, conditional comparison of explicitly labelled spatial predictions.

CLI (use the AlphaGenome project's existing .venv):
  python scripts/analyze_spatial_maps.py --manifest spatial_manifest.json \
      --output outputs/spatial_analysis.json --seed 20261028 --permutations 9999
Exact equality defines primary ties by default. Reproduce the synthetic demo
with its separately declared numerical tolerance by adding --tie-tolerance 1e-6.

Required manifest:
  {"schema_version": 1, "data_type": "spatial_log_enrichment_maps",
   "input_kind": "synthetic", "units": "native_log_enrichment",
   "track": "one declared track", "sites": [
     {"site_id": "s1", "npz_path": "s1.npz", "alleles": ["A","C","T"],
      "selected_allele_index": 0, "bin_coordinates": [0,2048,4096,6144],
      "null_probabilities": [0.3333333333333333,0.3333333333333333,
                             0.3333333333333333]}]}
input_kind is either synthetic or model_predictions. Each NPZ must contain
ref (n,n) and alt (3,n,n), with finite exactly symmetric entries. Coordinates
are shared, ordered integer starts, or n nonoverlapping [start,end] intervals.
Optional NPZ bin_coordinates/ref_bin_coordinates/alt_bin_coordinates and
optional manifest alt_bin_coordinates must agree with the declared support.
No scorer vectors, API access, biological validation or acquisition is supplied.

The three representation-enrichment tests form a new family of size three,
reported with BH and BY q-values. The paired centred-minus-native contrast is
a separately reported secondary, unadjusted test. All maps and null label
probabilities are conditioned on; independent site-label draws define the
chosen product null and do not establish biological independence of sites.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform

import numpy as np
from persim import bottleneck
from ripser import ripser
from scipy.stats import false_discovery_control, rankdata

REPRESENTATIONS = ("native", "centered", "rank")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_coordinates(value: object, n: int) -> np.ndarray:
    coords = np.asarray(value)
    if not np.issubdtype(coords.dtype, np.integer):
        raise ValueError("bin_coordinates must be integer genomic coordinates")
    if coords.shape == (n,):
        valid = np.all(coords >= 0) and np.all(np.diff(coords) > 0)
    elif coords.shape == (n, 2):
        valid = (np.all(coords >= 0) and np.all(coords[:, 1] > coords[:, 0])
                 and np.all(coords[1:, 0] >= coords[:-1, 1]))
    else:
        raise ValueError("bin_coordinates must have shape (n,) or (n,2)")
    if not valid:
        raise ValueError("bin_coordinates must be ordered, unique and nonoverlapping")
    return coords


def load_site(site: dict, manifest_dir: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    source = Path(site["npz_path"])
    source = source if source.is_absolute() else manifest_dir / source
    source = source.resolve()
    with np.load(source, allow_pickle=False) as data:
        if not {"ref", "alt"}.issubset(data.files):
            raise ValueError("Spatial NPZ requires ref and alt maps; scorer profiles are not maps")
        ref = np.array(data["ref"], dtype=float, copy=True)
        alt = np.array(data["alt"], dtype=float, copy=True)
        if ref.ndim != 2 or ref.shape[0] != ref.shape[1] or ref.shape[0] < 2:
            raise ValueError("ref must be square (n,n), n>=2; scorer-profile schemas are rejected")
        n = len(ref)
        if alt.shape != (3, n, n):
            raise ValueError("alt must have shape (3,n,n) on the same bin support as ref")
        coords = checked_coordinates(site["bin_coordinates"], n)
        for name in ("bin_coordinates", "ref_bin_coordinates"):
            if name in data.files and not np.array_equal(data[name], coords):
                raise ValueError(f"{name} disagrees with declared bin support")
        if "alt_bin_coordinates" in data.files:
            if not np.array_equal(data["alt_bin_coordinates"], np.stack([coords] * 3)):
                raise ValueError("Alternate-map coordinates disagree with reference support")
    if "alt_bin_coordinates" in site:
        if not np.array_equal(np.asarray(site["alt_bin_coordinates"]), np.stack([coords] * 3)):
            raise ValueError("Manifest alternate-map coordinates disagree with reference support")
    for name, matrix in [("ref", ref)] + [(f"alt[{a}]", alt[a]) for a in range(3)]:
        if not np.all(np.isfinite(matrix)):
            raise ValueError(f"{name} contains nonfinite entries")
        if not np.array_equal(matrix, matrix.T):
            raise ValueError(f"{name} is not exactly symmetric")
    provenance = {"npz_path": str(source), "npz_sha256": sha256(source),
                  "n_bins": n, "unordered_edges": n * (n - 1) // 2,
                  "bin_coordinates_sha256": hashlib.sha256(coords.astype("<i8").tobytes()).hexdigest()}
    return ref, alt, provenance


def h1(edge_births: np.ndarray) -> np.ndarray:
    """Full H1 flag persistence; all vertices precede all edges, diagonal ignored."""
    n = len(edge_births)
    if n < 4:
        return np.empty((0, 2), dtype=float)
    matrix = np.array(edge_births, dtype=float, copy=True)
    mask = ~np.eye(n, dtype=bool)
    offset = max(0.0, 1.0 - float(np.min(matrix[mask])))
    matrix[mask] += offset
    np.fill_diagonal(matrix, 0.0)
    with np.errstate(over="ignore"):
        if not np.all(np.isfinite(matrix.astype(np.float32))):
            raise ValueError("Edge weights exceed the finite range of Ripser's float32 input")
    diagram = ripser(matrix, distance_matrix=True, maxdim=1, coeff=2, thresh=np.inf)["dgms"][1].astype(float)
    if not np.all(np.isfinite(diagram)):
        raise ValueError("Unexpected essential/nonfinite H1 intervals on complete finite support")
    diagram -= offset
    return diagram[np.lexsort((diagram[:, 1], diagram[:, 0]))] if len(diagram) else diagram.reshape(0, 2)


def db(left: np.ndarray, right: np.ndarray) -> float:
    if not len(left) and not len(right):
        return 0.0
    if not len(left):
        return float(np.max(right[:, 1] - right[:, 0]) / 2)
    if not len(right):
        return float(np.max(left[:, 1] - left[:, 0]) / 2)
    return float(bottleneck(left, right))


def fractional_top(values: np.ndarray, tolerance: float) -> np.ndarray:
    maxima = values >= float(np.max(values)) - tolerance
    return maxima.astype(float) / int(np.sum(maxima))


def representations(log_map: np.ndarray) -> tuple[dict[str, np.ndarray], float]:
    n = len(log_map)
    upper = np.triu_indices(n, 1)
    mean = float(np.mean(log_map[upper]))
    native = h1(-log_map)
    ranks = (rankdata(-log_map[upper], method="min") - 1) / len(upper[0])
    rank_births = np.zeros((n, n), dtype=float)
    rank_births[upper] = ranks
    rank_births[(upper[1], upper[0])] = ranks
    # Exact full-filtration identity; avoids a second float32 computation.
    return {"native": native, "centered": native + mean, "rank": h1(rank_births)}, mean


def mc_summary(exceedances: int, draws: int) -> dict:
    p = (exceedances + 1) / (draws + 1)
    return {"p_value": p, "exceedances": exceedances, "draws": draws,
            "mc_standard_error_approx": math.sqrt(p * (1 - p) / (draws + 1)),
            "p_method": "plus-one Monte Carlo tail probability; plug-in MC standard error"}


def analyze(manifest_path: Path, *, permutations: int = 9999, seed: int = 20261028,
            tie_tolerance: float = 0.0) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema_version") != 1 or manifest.get("data_type") != "spatial_log_enrichment_maps":
        raise ValueError("Require schema_version=1 and explicitly labelled spatial_log_enrichment_maps")
    if manifest.get("input_kind") not in ("synthetic", "model_predictions"):
        raise ValueError("Explicit input_kind must be synthetic or model_predictions")
    if manifest.get("units") != "native_log_enrichment" or not isinstance(manifest.get("track"), str) or not manifest["track"].strip():
        raise ValueError("Declare native_log_enrichment units and one nonempty track")
    if not isinstance(manifest.get("sites"), list) or not manifest["sites"]:
        raise ValueError("Require at least one explicitly labelled site")
    if permutations < 1 or seed < 0 or not np.isfinite(tie_tolerance) or tie_tolerance < 0:
        raise ValueError("Require positive permutations, nonnegative seed and finite nonnegative tie tolerance")
    records, all_credits, probabilities, selected, ids = [], [], [], [], set()
    for site in manifest["sites"]:
        site_id = site.get("site_id")
        if not isinstance(site_id, str) or not site_id or site_id in ids:
            raise ValueError("Each site needs a unique nonempty site_id")
        ids.add(site_id)
        alleles = site.get("alleles")
        if not isinstance(alleles, list) or len(alleles) != 3 or len(set(alleles)) != 3 or not all(isinstance(a, str) and a for a in alleles):
            raise ValueError("Declare three distinct ordered alternate-allele labels")
        chosen = site.get("selected_allele_index")
        if isinstance(chosen, bool) or not isinstance(chosen, int) or chosen not in range(3):
            raise ValueError("selected_allele_index must be 0, 1 or 2")
        probs = np.asarray(site.get("null_probabilities", [1 / 3] * 3), dtype=float)
        if probs.shape != (3,) or not np.all(np.isfinite(probs)) or np.any(probs < 0) or not np.isclose(probs.sum(), 1, atol=1e-12, rtol=0):
            raise ValueError("null_probabilities must be three finite nonnegative values summing to one")
        if probs[chosen] <= 0:
            raise ValueError("Selected allele has zero probability under the declared conditional null")
        probs = probs / probs.sum()
        ref, alt, provenance = load_site(site, manifest_path.parent)
        map_results = [representations(matrix) for matrix in [ref, *alt]]
        per_rep, credits = {}, []
        for rep in REPRESENTATIONS:
            diagrams = [result[0][rep] for result in map_results]
            distances = np.array([db(diagrams[0], diagram) for diagram in diagrams[1:]])
            top = fractional_top(distances, tie_tolerance)
            credits.append(top)
            per_rep[rep] = {"distances": distances.tolist(), "fractional_top_credits": top.tolist(),
                            "selected_credit": float(top[chosen]), "number_tied_maxima": int(np.sum(top > 0)),
                            "h1_diagrams_ref_then_alts": [diagram.tolist() for diagram in diagrams],
                            "empty_diagrams_ref_then_alts": [len(diagram) == 0 for diagram in diagrams],
                            "total_persistence_ref_then_alts": [float(np.diff(diagram, axis=1).sum()) for diagram in diagrams]}
        means = [result[1] for result in map_results]
        records.append({"site_id": site_id, "gene": site.get("gene"), "alleles": alleles,
                        "selected_allele_index": chosen, "null_probabilities": probs.tolist(),
                        "provenance": provenance, "log_enrichment_means_ref_then_alts": means,
                        "representations": per_rep})
        all_credits.append(credits)
        probabilities.append(probs)
        selected.append(chosen)

    credits = np.asarray(all_credits)  # site, representation, alternate
    probs = np.asarray(probabilities)
    chosen = np.asarray(selected)
    n = len(records)
    observed = credits[np.arange(n), :, chosen].mean(axis=0)
    expected = (credits * probs[:, None, :]).sum(axis=2).mean(axis=0)
    rng = np.random.default_rng(seed)
    uniforms = rng.random((permutations, n))
    labels = ((uniforms >= probs[None, :, 0]).astype(np.int8)
              + (uniforms >= probs[None, :, :2].sum(axis=2)).astype(np.int8))
    null = np.stack([credits[np.arange(n)[None, :], r, labels].mean(axis=1)
                     for r in range(3)], axis=1)
    tests = []
    for r, rep in enumerate(REPRESENTATIONS):
        item = {"representation": rep, "observed_mean_top_credit": float(observed[r]),
                "conditional_null_mean_exact": float(expected[r]),
                "excess_over_conditional_null": float(observed[r] - expected[r]),
                "simulated_null_mean": float(null[:, r].mean()),
                **mc_summary(int(np.sum(null[:, r] >= observed[r] - 1e-12)), permutations),
                "tail": "one-sided enrichment"}
        tests.append(item)
    p_values = [test["p_value"] for test in tests]
    for test, bh, by in zip(tests, false_discovery_control(p_values, method="bh"), false_discovery_control(p_values, method="by")):
        test.update(bh_q_value=float(bh), by_q_value=float(by))
    observed_pair = float(observed[1] - observed[0])
    expected_pair = float(expected[1] - expected[0])
    centered_pair = observed_pair - expected_pair
    null_pairs = null[:, 1] - null[:, 0] - expected_pair
    pair = {"contrast": "centered minus native fractional top credit",
            "observed_difference": observed_pair, "conditional_null_difference_exact": expected_pair,
            "difference_centered_on_its_conditional_null": centered_pair,
            "tail": "two-sided around exact conditional-null expectation",
            **mc_summary(int(np.sum(np.abs(null_pairs) >= abs(centered_pair) - 1e-12)), permutations),
            "multiplicity_scope": "Secondary unadjusted test; excluded from the three-test representation-enrichment family"}
    diagnostics = {}
    for rep in REPRESENTATIONS:
        entries = [record["representations"][rep] for record in records]
        diagnostics[rep] = {"empty_maps": sum(sum(item["empty_diagrams_ref_then_alts"]) for item in entries),
                            "maps_evaluated": 4 * n, "sites_with_tied_maximum": sum(item["number_tied_maxima"] > 1 for item in entries),
                            "sites_with_all_three_distances_zero": sum(all(value == 0 for value in item["distances"]) for item in entries)}
    return {"artifact_type": "offline_spatial_map_conditional_analysis",
            "biological_data_used": manifest["input_kind"] != "synthetic",
            "input_kind": manifest["input_kind"], "track": manifest["track"], "units": manifest["units"],
            "manifest_path": str(manifest_path), "manifest_sha256": sha256(manifest_path),
            "script_sha256": sha256(Path(__file__)), "sites": records,
            "n_sites": n, "seed": seed, "permutations": permutations,
            "tie_rule": {"absolute_distance_tolerance": tie_tolerance, "rule": "Equal fractional credit among alternate distances within tolerance of the maximum"},
            "filtration": {"type": "complete weighted flag, full H1 over F2", "diagonal": "ignored", "native_edge_birth": "minus native log enrichment",
                           "centered_method": "Translate each native diagram by that map's upper-off-diagonal mean; exact full-filtration identity",
                           "rank_method": "Fraction of unordered edges with strictly greater log enrichment; equal values enter together",
                           "numerics": "Ripser uses float32; signed edge offsets are undone separately for each map"},
            "enrichment_family": {"size": 3, "members": list(REPRESENTATIONS), "tests": tests,
                                  "scope": "One declared track; three representation-enrichment endpoints, not the retained 66-test profile family",
                                  "adjustments": "BH assumes independence or appropriate positive dependence; BY provides general dependence protection for valid marginal p-values"},
            "secondary_paired_contrast": pair, "diagnostics": diagnostics,
            "inference_scope": ["Conditional label-model comparison of fixed model outputs, not causal randomization of pathogenicity or physical architectural validation",
                                "Joint draws independently sample each site's declared probabilities; the same pseudolabels are used across all representations",
                                "Site and gene sampling independence is not established; these sites are not independent biological replicates for population-wide generalization",
                                "Default probabilities are uniform; consequence restrictions and mutation-aware probabilities must be explicitly supplied",
                                "BH/BY values inherit Monte Carlo uncertainty; no clinical or biological interpretation is automated"],
            "environment": {"python": platform.python_version(), **{name: importlib.metadata.version(name) for name in ("numpy", "scipy", "ripser", "persim")}}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261028)
    parser.add_argument("--permutations", type=int, default=9999)
    parser.add_argument("--tie-tolerance", type=float, default=0.0,
                        help="Absolute tolerance for a separately declared numerical sensitivity; default 0 means exact ties")
    args = parser.parse_args()
    result = analyze(args.manifest, permutations=args.permutations, seed=args.seed, tie_tolerance=args.tie_tolerance)
    forbidden = {args.manifest.resolve(), Path(__file__).resolve(),
                 *(Path(site["provenance"]["npz_path"]).resolve() for site in result["sites"])}
    if args.output.resolve() in forbidden:
        raise ValueError("Output must not overwrite the manifest, an input NPZ or this script")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(f"Analyzed {result['n_sites']} {result['input_kind']} sites; wrote {args.output}")


if __name__ == "__main__":
    main()
