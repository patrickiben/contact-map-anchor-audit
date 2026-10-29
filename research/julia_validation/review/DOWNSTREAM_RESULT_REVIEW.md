# Targeted Julia downstream result review

Reviewed the completed primary and downstream artifacts and every downstream per-site result. No manuscript or public repository was modified by this reviewer.

## Findings

The primary comparator reports exact complete interval-multiset agreement for all **72 diagrams**, comprising **847,288 positive-persistence intervals**, across the frozen nine-site/two-track target. All 22 independent small-graph Julia controls passed. The downstream script hash agrees with the hash frozen before execution: `a491a0ca846f55d91a97626fd4cd3214ef9cf1da131c8218f45760449b1f29a0`.

I checked the SHA-256 of every one of the 18 per-site downstream result files against the aggregate manifest and inspected all their check flags. All **2,565 recorded checks passed**, with no failed site or suppressed discrepancy. The downstream run took 221.12 seconds with three workers.

- All **108 recomputed native/centered bottleneck distances** matched their stored values exactly: maximum absolute difference **0.0**.
- All **54 independently brute-forced shifted Hausdorff lower bounds** matched their stored values exactly: maximum absolute difference **0.0**. The check explicitly examined **8,483,894,259 off-diagonal point pairs**, retaining diagonal alternatives and every interval occurrence.
- The simple and strengthened numeric score bounds also matched exactly: maximum absolute difference **0.0**.
- The independently recomputed raw-map means and Julia receipt means matched the saved means exactly in this target: maximum absolute difference **0.0**.
- Top sets and fractional credits agreed at each declared tolerance: 0, 1e-6 and 1e-5. All available stored native-only ranking predictions agreed, and all reconstructed predictions contained the observed centered top sets as required. GM12878 stored ranking predictions are available at 1e-6; the script's other two GM12878 ranking-bound checks are new reconstructions, not comparisons to nonexistent recorded predictions.
- All endpoint directions, branch predictions, tiny-shift indicators and saturation classifications agreed, including the 1e-12 sensitivity threshold.

The only nonsaturating pairs at the primary 1e-10 threshold remained the three previously declared IMR90 cases:

| Site | Alternate index | Allele | Absolute saturation residual |
| --- | --- | --- | --- |
| chr13:48303721:G | 2 | G>T | 0.001204502435174145 |
| chr13:48307406:G | 1 | G>C | 0.002583775381601489 |
| chr13:48465370:T | 0 | T>A | 0.00014162732143801343 |

Four additional hand-derived downstream fixtures passed. They cover an empty-diagram diagonal match, a translated single interval, a repeated interval with unequal multiplicity, and a case where matching to the diagonal is cheaper than matching the other point. In particular, the duplicate fixture correctly gives Hausdorff lower bound 0 but bottleneck distance 2, confirming that the lower-bound calculation is not being confused with bijective bottleneck matching. Details are in `DOWNSTREAM_HAND_CONTROLS.json`.

## Interpretation and limitations

These checks strengthen computational reproducibility without changing any of the scientific endpoints, selected-allele credits, rankings or exception cases. The target was fixed before Julia genomic computation, including previously selected one-per-gene sites and all three known exceptions. It was deliberately enriched with those exceptions and is not a newly drawn prospective biological cohort.

Ripserer supplies a separate Julia persistence implementation in the same Ripser algorithm family. The downstream matching solver is still GUDHI/Hera with zero approximation parameter; the result does not constitute a second independent implementation of bottleneck matching. The Hausdorff verification is independently implemented with exhaustive blockwise pair comparisons instead of the original tree query. The 1e-12 numerical comparisons are practical checks, not real-arithmetic enclosures or Lean certification. The exercise does not establish independent-model transfer, biological validity or clinical superiority, and it does not cover every genomic site in the full study.

## Portable replay check

The replay capsule contains 38 exact original study files: 18 NPZs, 18 per-site analyses and two GM12878 witness/ranking reference artifacts. The portable driver copies verified inputs and fixed code into a new workspace, exports the 22 controls and 72 genomic targets, and gates downstream execution on actual successful control and primary-comparison artifacts. Existing workspaces are refused.

Preparation-only replay succeeded in a separate temporary directory; all copied hashes were verified, the outputs directory was empty, and status was correctly `PREPARED_NOT_EXECUTED`. Repeating preparation against the existing destination was rejected with exit code 2 without changing its status artifact. This preparation test is not a second full 72-diagram genomic replay. See `REPLAY_PREPARATION_CHECK.json` and `REPLAY.md`.

No computational discrepancy requiring a manuscript-results change was identified. A concise methods/validation addition should report the exact scope and preserve the limitations above.
