# Anchor audit: concise study guide

A short introduction to *Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps* by Patrick Iben.

This guide is for a numerate reader with one statistics course and no assumed expertise in persistent homology. It is the shorter of two editions. The [complete companion](COMPANION.md) explains the main manuscript and Additional files 1–6, including the proofs, all result tables, all four figure-reading tasks, worked examples and practice questions. Both editions have matching PDFs.

**Exact basis:** the final-proof manuscript, six PDF supplements and scalar-verification archive dated 28 October 2026. This rework is not yet submitted. It incorporates the earlier AlphaGenome audit, whose journal submissions were desk rejected for fit. The earlier preprint remains a separate, historical version; its DOI is not a DOI for this rework. Source hashes are in [ARTIFACTS.json](ARTIFACTS.json).

## The problem in one picture

Imagine three possible DNA substitutions at the same position. A model predicts a contact map for each, and a mathematical summary gives three discrepancy scores. Two changes may tie for the largest score. After subtracting each map's own mean, one becomes the unique leader.

The arithmetic can be correct while the interpretation remains uncertain. Did the operation reveal a biologically better choice, or did moving the origins of two summaries break a tie? The paper makes that distinction observable. Its clearest prospective result is 42 additional centered-leader decisions in the paired IMR-90 test, even though universal endpoint saturation failed. The earlier GM12878 cohorts also showed tie resolution while preserving strict leaders and interval lifetimes. The selected clinical label did not consistently receive more credit.

This is an audit of a representation choice. It does not introduce a new generic distance, measure experimental chromosome changes or establish clinical prediction.

## Two evidence streams, two endpoints

**The retained profile audit** compares all three non-reference substitutions at selected ClinVar positions. It asks whether the chosen substitution lies farther from a background profile than its two rivals, and how that result changes after controlling for molecular consequence. The retained seven-gene AVI counts rank Euclidean distances from a background centroid, not raw AVI values.

**The spatial anchor audit** compares reference and alternate persistence diagrams built from actual predicted 512-bin contact maps. It asks how a specified mean-centering operation changes their bottleneck distance and the ranking among alternate substitutions. It uses a different endpoint and a separate statistical family. The earlier variant-by-track contact scores were not spatial matrices.

Holding position fixed removes a coordinate shortcut. It does not remove consequence differences, clinical ascertainment, model-training overlap or dependence among nearby genomic windows.

## The vocabulary you need

| Term | Meaning here |
|---|---|
| Contact map | Values for pairs of genomic bins; the analyzed values are predicted log enrichment, not observed read counts. |
| Persistence interval | A feature's birth and death thresholds in a weighted flag filtration. It is not automatically a located chromosome loop. |
| Lifetime | Death minus birth. Adding the same scalar to both coordinates preserves it. |
| Bottleneck distance | The smallest possible largest matching cost, allowing an interval to match the diagonal at half its lifetime. |
| Anchor | A scalar used to set the origin of a map's diagram coordinates. |
| Top set | Every alternate whose score is within a declared tolerance of the maximum. |
| Selected-allele credit | One divided by top-set size if the selected allele belongs to it, otherwise zero. |
| Numerical saturation | A computed endpoint change approximately equals the translation bound; exact equality is a distinct mathematical claim. |

## Follow the anchor

The study uses native edge births `w = -L`, where L is predicted log enrichment. Subtracting a map mean from L adds that mean to every diagram coordinate. A common shift of two diagrams cancels. Their relative shift is therefore:

`delta = mean(L_alternate) - mean(L_reference)`

The path is:

`f(lambda) = bottleneck(D_reference, D_alternate + lambda * delta)`

Here lambda runs from zero to one. It is a preprocessing fraction, not a sequence interpolation or a biological trajectory. The path starts at the native comparison and ends at the independently mean-centered comparison. A declared scalar anchor other than the mean can be audited in the same way, provided the support and filtration assumptions remain valid.

Write A for the native distance, C for the centered distance and T for the absolute relative shift. Standard matching geometry gives `|C - A| <= T`. Applying that bound from both endpoints encloses the whole path. Exact equality forces a straight path on the segment. Numerical near-equality alone does not certify hidden higher-precision outputs or every floating-point operation.

A practical counterexample is reference interval (0,4), alternate (-1,3), and shift 2. The distance is 1 at both endpoints but zero halfway through. The browser includes this turning path so that endpoint interpolation is not mistaken for a general theorem.

## Read the genomic findings with their denominators

| Result | Discovery | New-locus replication |
|---|---:|---:|
| Sites / loci | 120 / 4 | 84 / 7 |
| Reference-alternate comparisons | 360 | 252 |
| Numerically saturated comparisons | 360 / 360 | 252 / 252 |
| Native ties resolved by centering | 72 of 75 | 66 of 66 |
| Strict native leaders preserved | 45 of 45 | 18 of 18 |
| Selected-allele credit: native to centered | 0.368056 to 0.375000 | 0.359127 to 0.321429 |
| Centered leaders identified by native-diagram bounds | 89 of 120 | 52 of 84 |

The primary tie tolerance was 0.000001. At 0.00001, eleven replication sites still tied after centering. A ranking's apparent decisiveness therefore depends on the declared tolerance as well as the distance.

The discovery credit increase was small and not significant after the declared corrections. None of the sixteen main and sensitivity tests survived the additional Holm adjustment. Replication credit comparisons were descriptive, with no new confirmatory clinical-enrichment tests. Its sharper ranks accompanied a decrease in selected-allele credit.

The replication cohort and protocol were fixed before new spatial-map acquisition. The seven genes were ASS1, BAP1, BRCA2, HFE, RB1, SCN5A and TSC1. Their windows overlapped within genes. These are seven new locus regions, not 84 independent biological regions. Prospective spatial outcomes do not establish independence from model training or an immutable server checkpoint.

## The paired IMR-90 test: useful coverage despite exceptions

The same 84 sites in seven loci were evaluated on a second contact track within AlphaGenome. Native-only predictions were locked before centered matching. Simple bounds identified 7 leaders; strengthened bounds identified 49, adding 42 decisions across six genes with zero observed contradictions and 35 unresolved sites. The earlier GM12878 increments were compared after those outcomes; this was the prospective test of added coverage. Unresolved by the bounds does not necessarily mean that the directly computed centered scores are tied.

Numerical saturation passed in 249 of 252 comparisons. Three RB1 exceptions falsified universal saturation. Both simple and strengthened bounds abstained at all three sites, so that abstention is not a witness-only advantage. Later outcome-selected samples showed two paths changing direction and one effectively flat path; samples do not locate exact breakpoints.

IMR-90 selected credit increased from 0.335317 to 0.398810, but RMS baselines remained higher (0.500000 native; 0.517857 centered). GM12878 replication credit decreased, and its RMS baselines were also higher. These descriptive results establish neither clinical superiority nor experimental validity. Reusing sites and one architecture is not independent-model replication.

Whole-path envelopes require both endpoint distances. Native-only witness bounds predict selected centered leaders before centered matching. Keep those information settings separate; the endpoint witness does not automatically guarantee every intermediate ranking.

## What the earlier AlphaGenome result adds

In the retained expanded-panel analysis, AVI background-distance rankings placed the ClinVar allele first at 1,095 of 1,238 nonsense/start-loss positions and 94 of 246 missense positions: about 88% and 38%. This large consequence contrast motivates controls. It does not establish that all remaining enrichment is explained by consequence.

The frozen coding criterion required at most one quarter as many significant matched-null comparisons as uniform-null comparisons. The retained counts were ten and 37; ten is greater than 37/4, so that criterion was not met. Monte Carlo uncertainty around the counts remains relevant, and eligibility also changed between analyses.

The highlighted missense mean selected-minus-largest-other distance was negative, about -0.0128, while the simulated matched-null mean was more negative, about -0.0829. A significant null-relative result is therefore compatible with a negative average margin. Neither quantity is interchangeable with first-rank frequency or clinical accuracy.

## A useful decision can remain unresolved

Native-distance margins can sometimes guarantee that a strict leader remains above its rivals throughout the whole anchor path. A nearest-neighbor lower bound, called a diagonal-augmented Hausdorff witness, can identify additional unique leaders at the centered endpoint. The reported gain was 44 discovery and 34 replication sites beyond the simple margin rule.

The remaining sites stay unresolved. That is useful information about which calculations or error bounds are still needed. The witness cannot replace complete matching in general because it can miss repeated intervals: two copies of (0,4) versus one have witness zero but bottleneck distance two. No measured runtime speedup was claimed in the research analysis.

## The supporting files and their role

- **S1, vertex thinning:** deleting bins can extinguish degree-one features for a fixed finite bin set, but this is distinct from reducing sequencing depth; deletion can also reveal a cycle at intermediate thinning.
- **S2, anchor theory:** proves path envelopes, local slope and ranking statements, supplies counterexamples, and explains why the individual mathematical ingredients have established precedents.
- **S3, Monte Carlo scope:** explains the precision floor of the retained profile tests and separates exact conditional arithmetic from the validity of the scientific null.

- **Additional file 4, paired track test:** records the frozen coverage comparison, all genes, tolerances, stronger baselines and exploratory exception paths.
- **Additional file 5, retained audit:** preserves the earlier within-site methods, adverse consequence controls and clinical-ascertainment limitations.
- **Additional file 6, reproducibility:** distinguishes full original-implementation replay from the targeted Julia check.
- **Additional file 7, compact verification:** reconstructs scalar-derived bounds, rankings and credits; it does not recompute PH or model outputs.

## What the Julia check adds

Ripserer in Julia separately reconstructed 72 full diagrams from nine replication sites on both tracks, including all known IMR-90 exceptions. All 847,288 intervals matched exactly, with duplicates preserved. Twenty-two small controls agreed with explicit boundary reduction. This tests another implementation in the Ripser algorithm family on identical effective float32 inputs; downstream matching still used Hera. It strengthens computational evidence for that sample, not every site, an independent model or clinical validity. No Lean proof was produced.

## Five self-checks

1. **If a tie disappears, what has improved?** Ranking decisiveness under the chosen representation and tolerance. Biological discrimination needs separate evidence.
2. **Does equal lifetime imply equal distance?** No. Interval location can change while lifetime stays fixed.
3. **Does an exact solver prove a real-valued biological claim?** No. Its setting concerns supplied finite coordinates; model error and quantization remain.
4. **Does zero exceedance in 9,999 null draws imply p = 0?** No. The plus-one estimate is 0.0001, with remaining Monte Carlo uncertainty.
5. **Does bin deletion simulate lower read depth?** No. It changes the support; thinning reads and deleting vertices are different operations.

## Try the method and keep its scope

Open the [Anchor Audit Lab](https://patrickiben.github.io/contact-map-anchor-audit/) for five synthetic controls, a centering slider, bounds, local diagram import and JSON audit export. The Python toolkit accepts larger finite diagrams. Neither route constructs diagrams from a contact map or chooses the biological anchor for you.

The [complete companion](COMPANION.pdf) supplies the detailed reading route, six worked examples, twelve practice questions and a research workflow. These are teaching adaptations, not biological replications or validated learner assessments. Whole-package author approval, human semantic review and learner testing remain pending. Codex assisted development and verification, Qwen3.8 earlier drafting, and Qwen3.8-Max author-supplied QC. Checks do not replace final author approval.

The [v0.2.0 release](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0) supplies the full study archive; the Julia check has a separate capsule. Original software is MIT-licensed. AlphaGenome outputs and substantial derivatives retain provider terms and notices. Saved raw maps retain their bytes; centering, persistence analysis, ranking and visualization are documented modifications. Public access does not establish clinical validity, author approval or learner effectiveness.
