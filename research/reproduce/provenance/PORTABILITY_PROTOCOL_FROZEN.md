# Prospective paired cross-track portability of the anchor audit

Specification dated 28 October 2026, to be hashed before acquiring any new prediction outputs. This is a pre-acquisition local protocol, not an externally registered clinical study. It was developed with knowledge of the existing GM12878 results, but without new IMR-90 predictions or results. The prior manuscript remains unchanged.

## Question, target and design

Does the native-diagram Hausdorff-strengthened anchor audit provide correct, nontrivial additional centered-leader decisions on a second AlphaGenome contact track, without tuning to its centered endpoints or clinical labels?

Use IMR-90 in situ Hi-C, ontology EFO:0001196, track 4dn:4DNFIJTOIGOI. This is chosen from output metadata: a unique contact track from a distinct fibroblast context, retaining the assay and resolution of the original GM12878 track. This is paired cross-track portability within one model, not independent-model validation, a new-locus holdout or experimental confirmation. No alternate track will replace it on the basis of outcomes.

Reuse all 84 sites across seven loci in candidate_cohort.json, SHA256 b58bcab74e54c5f1626f9e5a3d07d87665b2e10af6553933d1a488e2a06cb34c. Preserve all three alternate SNVs, their order, the existing 1,048,576-bp windows, 512 bins and 2,048-bp bin resolution. The selected sites are already known under GM12878; only the new track outputs are uninspected. Overlapping windows and purposively selected genes prevent treating 84 sites or 252 pairs as independent population draws.

## Acquisition, provenance and missingness

Use the existing AlphaGenome client and explicit ALL_FOLDS alias. Request IMR-90 and GM12878 (EFO:0002784, track 4dn:4DNFIXP4QG5B) together in each of 252 variant calls. Identify channels by exact returned metadata names. Store separate track caches, all REF repeats and ALT maps, coordinates, returned metadata, versions, hashes, timestamps and sanitized request histories. Never write credentials into artifacts. Check shape, finite values, symmetry, resolution and genomic coordinates. Use a 60-second request timeout and at most five attempts per allele with bounded increasing delays; preserve failures and do not replace sites or stop based on results.

The contemporaneous GM12878 outputs control for possible model-server drift because immutable server weight identifiers are unavailable. Compare every new GM12878 REF/ALT array with its existing counterpart. If all are identical, existing GM12878 analysis is the paired comparator. If any differ, retain and report the differences and rerun the contemporaneous GM12878 maps in a distinct analysis lane; do not overwrite historical outputs or attribute all cross-track differences to cell context. Equal outputs at these queried inputs do not prove globally unchanged weights.

The full planned cohort is required to declare definitive technical transfer or the fixed operational benchmark met. Missing sites make those conclusions incomplete; report observed-case descriptions and worst-case coverage bounds without replacing sites or redefining the denominator. Execution or metadata failures trigger debugging with a dated deviation record, not silent exclusion.

## Mathematical object and numerical conventions

For the complete shared unordered off-diagonal support, use signed edge weights -L for native log-enrichment map L, full finite H1 over F2, and no persistence truncation. For native REF/ALT diagrams D_R,D_A and delta=mean(L_A)-mean(L_R), audit f(lambda)=d_B(D_R,D_A+lambda*delta), 0<=lambda<=1. Addition translates both birth and death coordinates. All map means use precisely the same support. Preserve the established PH implementation and its input-rounding diagnostics. Use GUDHI/Hera with delta=0 on delivered floating-point diagrams; that setting is not validated real arithmetic.

Primary top-set tolerance is 1e-6 in native output units; fixed sensitivities are computed equality (0) and 1e-5. The practical solver allowance is 1e-12, explicitly not a proved floating-point enclosure. Let A be native distance, T=abs(delta) and H the diagonal-augmented Hausdorff bound on D_R,D_A+delta. The simple endpoint interval is [max(0,A-T)-epsilon,A+T+epsilon]; the strengthened lower endpoint is max(0,A-T,H)-epsilon. Use the existing exact Cartesian possible/necessary membership formulas and strict unique-leader gap greater than the top tolerance. All purported guarantees are conditional numerical checks on the stored coordinates and practical allowance.

## Prospective prediction separation

Phase 1 computes native PH diagrams, native bottleneck distances, mean shifts, fixed baselines and simple/strengthened ranking bounds. It writes predictions and abstentions for every site at all three tolerances. It must not compute centered bottleneck distances. Hash the complete Phase-1 prediction manifest and per-site artifacts before Phase 2 starts. The clinical selected-allele labels do not select bounds, parameters, examples or endpoints.

Phase 2 verifies the locked hashes, computes centered distances independently from the stored diagrams, and tests every previously written interval, possible/necessary top set and unique-leader prediction. Retain both phases and their timestamps. Discovery of disagreement is a reportable finding; a repaired implementation requires a documented deviation and rerun, without claiming that the repaired run preceded the observed discrepancy.

## Primary endpoints and fixed interpretation criteria

Report simple and strengthened unique-leader coverage, their paired site-level increment, losses, contradictions, unresolved sets, gene-specific counts and leave-one-gene-out increments. Coverage uses all 84 planned sites. The strengthened lower bound is no weaker by construction; preserving simple-bound decisions is a consistency check. The empirical contribution is the amount and distribution of additional useful coverage, not a statistical test of an algebraically guaranteed direction of improvement.

Technical transfer requires zero contradicted unique-leader predictions and zero interval/top-set validation failures, with strictly positive additional coverage. Zero useful gain is technically valid abstention but fails the nontrivial-transfer criterion; any contradicted result fails the implementation-validation criterion until explained. A frozen, more demanding operational utility benchmark requires at least 17 additional leaders (17/84=20.24 percentage points), gains in at least four of seven genes, no lost simple-bound decisions, and no validation failures. The 17-site threshold is half the earlier 34-site witness increment on the same panel under GM12878. It is an explicitly selected utility benchmark, not a powered statistical hypothesis or clinically meaningful threshold. Report results whether either, both or neither criterion is met; do not substitute an after-the-fact favorable threshold.

## Secondary endpoints and stronger alternatives

Retain the previous numerical saturation criterion abs(abs(f(1)-f(0))-abs(delta))<=1e-10, with 1e-12 sensitivity, zero/tiny shifts (T<=1e-10), signed changes and full residual distribution. Universal non-tiny saturation fails if any completed non-tiny pair violates the criterion. Saturation is secondary because ordinary affine matching regions can produce it; nonsaturation does not invalidate the general audit or translation bound.

Evaluate direct f(1/2) for all three alleles at the fixed minimum-selection-hash site in each gene, using the copied midpoint_selection.json (21 checks). Test the two-endpoint Lipschitz envelopes and describe chord discrepancies. Do not infer unmeasured intermediate rankings by an affine chord for nonsaturated pairs. Report endpoint ranks directly; intermediate path descriptions remain qualified approximations unless directly computed.

Fixed baselines: native bottleneck, absolute mean shift, native-plus/minus-absolute-shift, native and centered RMS edge difference, maximum absolute edge difference, and count/total/maximum lifetime differences. Compare top sets and descriptive selected-allele credit, not only aggregate performance. Report cross-track agreement, native and centered ties, ties resolved/introduced, strict leaders retained/replaced and centered leaders outside the native top set. Include gene-specific and leave-one-gene-out descriptions. No new clinical-enrichment p-values or independence-based confidence intervals are introduced; all previous testing families remain unchanged.

Repeat-REF equality is execution consistency, not biological measurement precision. Input-grid diagnostics do not identify unexposed model error or uncertainty. Compare cross-track maps directly and report whether this is a nonidentical numerical input test. Runtime is logged for reproducibility; no speedup is claimed without a separate fair performance benchmark.

## Controls, execution freeze and reporting

Before interpreting new outputs, run known-answer controls for zero shift, REF=ALT, increasing/decreasing affine paths, a nonaffine path, multiplicity where Hausdorff is not bottleneck, and overlapping bounds that force abstention. Test lock tampering and a deliberately wrong prediction. Reuse prior valid mathematical controls and supplement them for the phase boundary.

Freeze this protocol, cohort, midpoint list, acquisition script and core numerical source hashes before launching acquisition. New experiment orchestration code may be implemented/tested while acquisition runs, but must be locked before Phase 1 and must not be tuned from new outcomes; document its version. Report any implementation changes, failures or departures in PROTOCOL_DEVIATIONS.md, preserving the original protocol.

Deliver separate proposed manuscript and supplementary updates, an exact integration map, a claim-to-output validation record, source hashes and a journal reassessment. A successful result strengthens evidence for portability of the witness audit across two AlphaGenome tracks. It does not establish transfer to independent architectures, physical chromosome organization, improved pathogenicity prediction or guaranteed acceptance at a higher-impact journal.
