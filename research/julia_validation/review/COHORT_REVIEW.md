# Independent cohort review for targeted Julia persistence check

28 October 2026. Read-only review of existing site selection, stored map schemas and prior diagram/results records. No Julia outcomes were inspected or used for selection. No source maps, manuscript, clinical endpoint or historical protocol was changed.

## Fixed target set

Reuse `anchor_method/replication/midpoint_selection.json`: the smallest frozen SHA-256 within each gene, with site-ID tie breaker. Add all three known IMR-90 nonsaturating comparison sites from `portability_imr90_2026-10-28/POST_RESULT_PATH_PROTOCOL.md`. Site59 is already among the seven midpoint sites, so the union contains nine distinct sites.

| Index | Gene | Site ID | ALT order, zero-based indexing | Reason |
|---:|---|---|---|---|
| 7 | ASS1 | chr9:130489343:G | A, C, T | frozen smallest hash for gene |
| 21 | BAP1 | chr3:52408597:A | C, G, T | frozen smallest hash for gene |
| 34 | BRCA2 | chr13:32370560:A | C, G, T | frozen smallest hash for gene |
| 44 | HFE | chr6:26092780:A | C, G, T | frozen smallest hash for gene |
| 48 | RB1 | chr13:48303721:G | A, C, T | known IMR-90 exception |
| 51 | RB1 | chr13:48307406:G | A, C, T | known IMR-90 exception |
| 59 | RB1 | chr13:48465370:T | A, C, G | frozen smallest hash for gene; known IMR-90 exception |
| 70 | SCN5A | chr3:38606689:A | C, G, T | frozen smallest hash for gene |
| 75 | TSC1 | chr9:132900839:T | A, C, G | frozen smallest hash for gene |

This means 9 sites × 2 tracks × (REF + 3 ALTs) = **72 full H1 diagrams**, over all 512 bins. The complete union is fixed before Julia calculations. Seven-site selection is inherited and deterministic; inclusion of the extra exception sites is deliberately outcome-enriched from the prior analysis. This is a targeted implementation check, not a new prospective biological sample or an estimate of population failure rates.

The exact exceptions are site48/ALT2 (chr13:48303721:G→T), site51/ALT1 (chr13:48307406:G→C), and site59/ALT0 (chr13:48465370:T→A). All are in RB1. The selected clinical alternate must not be used to choose comparisons or parameters.

## Exact inputs and reference outputs

Use `anchor_method/replication/sites/site_NNN.npz` for GM12878 and `portability_imr90_2026-10-28/sites/site_NNN.npz` for IMR-90. Each has `ref` shape(512,512), `alt` shape(3,512,512), plus the three repeated references; map arrays are Float32. Loader conventions and production rounding still need explicit review before a Julia comparison.

The corresponding `site_analysis/site_NNN.json` beneath each root carries `representations.native.h1_diagrams_ref_then_alts`, four diagrams ordered REF then ALTs in the manifest's order. The same records contain native/centered distances, map means, credits at all three tolerances, lifetime summaries, and pair saturation diagnostics. For IMR-90, the `native/site_NNN.json` copies are the records saved before centered validation; they additionally carry bounds, witnesses, prediction sets and the lock identity.

`COHORT_SOURCE_INVENTORY.json` in this review directory lists every map and reference-output path, SHA-256, allele order, map schema and expected diagram cardinality. These are source expectations, not Julia results. The inventory totals 847288 positive-persistence intervals across the 72 reference diagrams.

Contemporary GM12878 control arrays are also available in `portability_imr90_2026-10-28/control_gm12878/sites/`; the retained drift audit reports exact decoded-array equality with historical GM12878. If those are used instead, hash those actual files and state that the reference diagrams are the historical counterpart. Do not equate different NPZ archive bytes with unequal decoded arrays.

## Recommended success criteria and downstream scope

1. Match full positive-persistence diagram multisets, preserving multiplicities. Compare counts and lexicographically sorted birth/death coordinates; a set comparison would miss repeated intervals. With exactly the same effective binary filtration values, exact equality should be the primary target. Diagnose any discrepancy before relaxing tolerance.
2. Independently recompute all four off-diagonal map means; preserve the float-conversion/offset contract and distinguish mean differences from filtration rounding. Compute centered diagrams by the declared exact translation convention, rather than mean-centering maps before a new Float32 cast, which would change the numerical target.
3. On each of 18 site-track combinations, compare all three native and centered distances, native/centered top sets and fractional credits at tolerances0,1e-6,1e-5. If downstream matching reuses Hera, say so explicitly: this independently checks diagram construction, not the matching solver.
4. Reconstruct the diagonal-augmented nearest-neighbor witnesses and the simple/strengthened interval leader, possible-member and necessary-member sets. Compare IMR-90 with the previously locked native predictions. GM12878 reference witness/ranking files are `hausdorff_branch_certificate.json` and `native_interval_ranking.json` under the replication root (the latter records primary1e-6).
5. Report all three previously nonsaturating pairs and whether both bounds remain unresolved there. Retain all other 51 site-track/ALT comparisons too; do not report only the known exceptions. The target contains54 REF/ALT comparisons, not72 comparisons:72 counts diagrams.
6. Optional midpoint checks should use the original frozen seven sites, producing42 REF/ALT midpoint comparisons over both tracks. If all nine are evaluated, label the six additional site-track pairs as newly targeted diagnostics. A new path grid or new clinical hypothesis test is not needed for this implementation check.

Success would strengthen reproducibility of the selected stored-input diagram computations. It would not certify all84 sites, prove a universal theorem, establish a complete real-arithmetic error enclosure, create an independent model architecture, or provide experimental genomic validation.
