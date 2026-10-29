# Targeted Julia persistence validation

28 October 2026 (America/New_York; execution receipts use UTC on 29 October).

**PASS for the fixed targeted check.** Ripserer 0.17.0 under Julia 1.13.0 independently reconstructed all 72 full H1 diagrams from saved contact maps. All 847,288 intervals agreed exactly with the stored Python Ripser results, including repeated intervals. All effective Float32 input hashes, offsets and independently computed map means also agreed. The downstream calculations reproduced every checked value and decision, including the three known IMR-90 nonsaturation exceptions. No scientific result was corrected.

This addendum validates computations underlying manuscript v0.2.3, source SHA-256 `05b28b1bcc1b3a715152beb5e07567afc628632851dba5d54e5301ea69483b5d`. It does not silently replace that manuscript or imply final author approval.

## Fixed sample and comparison

The sample contains nine sites in seven replication genes on both GM12878 and IMR-90 tracks: sites 7, 21, 34, 44, 48, 51, 59, 70 and 75. Seven are the previously frozen smallest-hash site per gene; the union additionally contains every site with a known IMR-90 nonsaturation exception. REF and all three ALTs give 72 diagrams and 54 REF–ALT pairs. Each map retains all 512 bins and 130,816 unordered edges. The selection preceded Julia outcomes but deliberately included known earlier exceptions; it is targeted computational validation, not a prospective biological sample.

The frozen [protocol](PROTOCOL.md) specifies a complete weighted flag filtration over F2, dense inputs, infinite filtration threshold, no positive-lifetime censoring and no thinning. Julia independently reconstructs shifted edge births from the raw maps, rounds to Float32 as in the original Ripser input, then restores the original Float64 offset after converting output endpoints to Float64. It receives no saved expected diagrams. The exact comparison preserves multiplicity and does not relax endpoint equality to a tolerance.

| Check | Result |
|---|---|
| Small known-answer foundation | 22/22 Julia diagrams exactly match explicit GF2 boundary reduction; ten also match hand-derived answers |
| Deliberately corrupted comparisons | All four rejected: missing duplicate, changed endpoint, unrestored offset, corrupted input hash |
| Full genomic persistence diagrams | 72/72 exact multiset matches; 847,288 intervals |
| Effective filtration inputs, offsets and means | All match; maximum mean discrepancy zero |
| Native and centered bottleneck distances | 108/108 exactly match stored values |
| Shifted Hausdorff witnesses | 54/54 exactly match, using independent blockwise all-pairs comparisons |
| Downstream record checks | 2,565/2,565 passed across 18 site-track records; maximum numerical discrepancy zero |
| Ranking and credit checks | Top sets and fractional credits match at tolerances 0, 10^-6 and 10^-5; stored GM12878 bound predictions checked at 10^-6 and IMR-90 predictions at all three tolerances |
| Known IMR-90 exceptions | All and only the three declared nonsaturation exceptions remain |

The small controls cover negative and zero births, ties, duplicate intervals, nonmetric weights, an inactive edge, Float32 near-tie collapse, translation and ignored matrix diagonals. Twelve graphs use the fixed seed 20261028. The independent small-graph oracle explicitly reduces the boundary matrix over F2 on all vertices, edges and triangles; it imports no persistence library.

## Downstream interpretation

The downstream driver imports no original analysis code. It uses Julia-produced diagrams and the recorded means to recompute bottleneck distances with the original GUDHI/Hera solver at approximation parameter zero. Thus matching remains a shared component; this is not a second independent bottleneck implementation. The shifted Hausdorff calculation explicitly evaluates 8,483,894,259 off-diagonal point pairs in bounded memory and includes diagonal alternatives. No deduplication is used.

At the primary tie tolerance, simple and strengthened bounds identify respectively 1 and 5 of the nine GM12878 leaders, and 0 and 5 of the nine IMR-90 leaders. These deliberately selected subset counts are not new estimates of general performance. The full-study headline remains 7 versus 49 of 84 IMR-90 leaders, 42 added decisions, 35 unresolved sites and zero observed contradictions.

The three exceptional IMR-90 comparisons are site 48/ALT index 2, site 51/ALT index 1 and site 59/ALT index 0. Their absolute saturation residuals are respectively 0.001204502435174145, 0.002583775381601489 and 0.00014162732143801343. Both bound methods continue to abstain at these sites. Their persistence under a separate implementation strengthens the evidence that they are features of the supplied computational inputs rather than a discrepancy specific to the original PH implementation.

## What this adds, and what it does not

Ripserer is a separate Julia implementation based on the Ripser algorithm family; its software publication is [Čufar (2020), JOSS 5(54):2614](https://doi.org/10.21105/joss.02614). The check addresses an implementation-dependence gap in the previous full replay, which reused Python Ripser. A separate Counter-based review also confirmed the complete multisets, including 197,071 repeated intervals beyond distinct coordinate pairs.

Agreement is exact for the effective Float32 filtration inputs and restored coordinates. It does not certify unrounded real-valued maps, the complete floating-point error budget, all 204 GM12878 or 84 IMR-90 sites, universal theorems, independent-model transfer, biological validity or clinical superiority. No Lean proof was produced. The downstream per-allele credit checks do not repeat the separate exact-rational conditional label tests. AI-assisted source and result reviews are not independent human peer review. Final author proof and submission approval remain pending.

## Evidence and execution history

- [Primary results](outputs/PRIMARY_COMPARISON.json), [downstream summary](outputs/downstream/summary.json) and per-site records bind the findings to inputs and outputs.
- [Control comparison](review/CONTROL_JULIA_COMPARISON_controls.json), [oracle and mutation checks](review/CONTROL_ORACLE_SELF_CHECK.json), and the review notes document calibration and scope.
- `environment/Project.toml` and `environment/Manifest.toml` pin the Julia environment. Python 3.14.7, NumPy 2.5.3, SciPy 1.18.1 and GUDHI 3.13.0 were used for export/comparison.
- `EXECUTION_FREEZE.json` records the pre-genomic source/input identities. The protocol, Julia runner, genomic inputs and primary comparator remained unchanged during the genomic run.
- After the first freeze, the control comparator gained three receipt identity/hash assertions and a corrected explanatory docstring. Expected intervals and input values did not change. The stricter comparison passed all controls again. Exact original files and the complete diff are retained in `review/initial_freeze/`; `DOWNSTREAM_EXECUTION_FREEZE.json` records the amendment and the driver hash before downstream execution.
- All Julia and downstream scientific executions completed successfully. This is a targeted addendum to the earlier validation harness, not a new full 15-gate pass. Rendered-proof approval and human educational assessment are not supplied by this check.

Original software is MIT-licensed. Saved AlphaGenome maps and substantial derived outputs remain subject to the separately supplied provider terms and notices.
