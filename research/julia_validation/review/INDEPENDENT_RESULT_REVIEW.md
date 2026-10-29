# Independent review of targeted Julia persistence validation

28 October 2026 (results completed 29 October UTC). Scoped source and artifact review by a separate agent; this is not human author approval or external peer review. No manuscript changes were made by this review.

## Result

No unresolved functional defect or result discrepancy was found in the reviewed target. All 72 Julia diagram outputs match the saved Python Ripser barcodes exactly as finite coordinate multisets. An independent Counter-based comparison, separate from compare_genomic.py, reproduced this result across 847,288 intervals. These include 197,071 repeated intervals beyond the distinct coordinate-pair counts, demonstrating that the check retains multiplicity rather than comparing sets. Receipt identities, dimensions and cohomology/F2/infinite-threshold/zero-cutoff settings agree with the declared run.

The downstream summary covers 18 site-track combinations, 54 reference/alternate pairs and 2,565 checks. I independently verified all per-site file hashes against the summary, recounted the comparisons, and recomputed each recorded exact or tolerance-based comparison verdict from its actual and expected values. All passed. The 108 native/centered distances and 54 shifted Hausdorff witnesses are exactly equal to their recorded references, beyond merely meeting the declared tolerance. The three and only three primary nonsaturation exceptions remain IMR-90 site48/ALT2, site51/ALT1 and site59/ALT0.

## Implementation and information separation

The primary comparator lexicographically sorts reference intervals and requires exact equality of complete coordinate arrays, alongside counts, finite positive intervals, offset and effective-input hashes. It does not round endpoints, discard duplicate intervals or relax its equality rule for discrepancies.

The Julia manifest contains exactly key, n, raw_path and raw_sha256. Its 72 rows exactly match the corresponding filtered exporter records. The Julia runner reads raw maps and reconstructs its Float32 filtration inputs; its source does not import Python Ripser, GUDHI or saved expected diagrams, means or endpoint results. The expected diagram fields exist only in the Python-side comparison manifest. The selected set is the declared nine-site union on both tracks, with every reference and alternate map.

The downstream driver imports no production analysis module. Its blockwise Chebyshev comparisons explicitly evaluate point-to-point distances, include each point's diagonal alternative, and retain both directed maxima. Its native/centered distances intentionally use shared GUDHI/Hera. Saved original means define the comparison target; independent Python and Julia mean reconstructions are checked separately and agree exactly in this run. The interval bounds, strict unique-leader rule, inclusive top-membership rules, saturation tolerances and branch criterion agree with the recorded analysis. The historical GM12878 possible-member expression includes the focal lower bound, while this driver uses competitors only; these are equivalent for valid intervals and nonnegative tolerance. GM12878 stored interval predictions are compared at the available primary tolerance only; IMR-90 stored predictions are compared at all three tolerances, as declared.

## Frozen sources and documented amendment

Protocol, Julia runner, genomic manifests and both primary/downstream comparison scripts match EXECUTION_FREEZE.json. The control comparator and its source-hash metadata changed after the original freeze: a docstring was made accurate and receipt key/dimension/raw-hash assertions were added. These did not alter control inputs, expected intervals, effective hashes, offset or interval comparison rules. The raw-only runner manifest is unchanged and the controls were compared again successfully.

I verified the reconstructed original control_oracle.py and control_manifest.json under review/initial_freeze/ against their original EXECUTION_FREEZE.json SHA-256 values; both match exactly. The original freeze remains preserved, and DOWNSTREAM_EXECUTION_FREEZE.json plus the reconstruction note record the amendment. No primary genomic target or equality threshold changed.

## Scope

This is a targeted independent implementation check using the same Ripser algorithm family. It is not a different prediction model, an unrelated persistence algorithm, a full-cohort rerun or experimental biological validation. Exact barcode agreement concerns the identical effective Float32 filtration inputs and restored stored coordinates; it does not certify unrounded real-valued source maps or the manuscript's practical numerical error allowance. Downstream agreement uses a shared bottleneck solver. Per-allele fractional credits are checked as stored floating values derived from top-set sizes; this is not a new exact-rational recertification of the sixteen label tests. Selection included known exceptions before this implementation run, so the result is targeted validation rather than a new prospective biological test. No runtime advantage or stronger journal-acceptance probability follows from this check alone.

## Reviewed result identities

- `outputs/PRIMARY_COMPARISON.json`: `1e3febd9205270ec36d90f090d3e3133a138d01ef9734eca12ba8188fef2a190`
- `outputs/downstream/summary.json`: `a7c1afc7c01442323e020b77d7c780380cb3dd85d8dfc19b897829c8469f1089`
- `EXECUTION_FREEZE.json`: `b67aca7a23ceee383d7bffb491d7acb8c8e0e009bfb71964940230b96a4119a6`
- `DOWNSTREAM_EXECUTION_FREEZE.json`: `26910bc804e680a1e5e3c395a5af03b3c77dd1a4984cdc7072467e187e8bb54b`
- `scripts/compare_genomic.py`: `c720bb4462ec344f6e99a0ddeed031e4ac81349b48539c80933ea9b9956417a8`
- `scripts/compare_downstream.py`: `a491a0ca846f55d91a97626fd4cd3214ef9cf1da131c8218f45760449b1f29a0`
