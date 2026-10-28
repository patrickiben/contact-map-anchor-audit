# Practice questions and explained answers

These multiple-choice practice items adapt the source reading guide. They are not the locked free-response human transfer test used in the manuscript validation harness. No learner pass rate or educational effectiveness is claimed.

Try each question before reading its answer. Correct feedback explains the distinction; a score is not evidence of educational effectiveness. Retrying is encouraged.

## T01 · Core

What input does this toolkit directly audit?

1. Finite persistence diagrams plus a declared shift
2. Raw sequencing reads
3. A list of pathogenicity labels

**Answer: 1.** The toolkit starts from diagram coordinates. Map acquisition and persistent-homology construction are upstream steps.

## T02 · Core

What stays unchanged when both coordinates of each interval receive the same shift?

1. Every distance between two independently shifted diagrams
2. Each interval’s lifetime
3. Every allele ranking

**Answer: 2.** Death minus birth is unchanged. Different shifts of the two diagrams can still change their distance and the resulting ranks.

## T03 · Core

For a valid 1-Lipschitz anchor path, what does exact endpoint saturation imply?

1. The selected allele is pathogenic
2. The same matching remains optimal everywhere
3. The path is affine on that segment

**Answer: 3.** The endpoint envelopes coincide. This conclusion does not require a fixed matching or extend beyond the segment.

## T04 · Core

Which statement describes the GM12878 new-locus replication?

1. More ties resolved, while selected-allele credit decreased descriptively
2. Every clinical metric improved
3. An experimental loop perturbation was validated

**Answer: 1.** Tie resolution and selected-label credit are different outcomes. More unique ranks did not establish improved clinical discrimination.

## T05 · Boundary

A floating-point saturation residual is very small. What has been established?

1. Exact equality for unseen real-valued model outputs
2. Numerical near-saturation on the computed inputs
3. The biological model has no error

**Answer: 2.** A tiny computed residual is numerical evidence. A formal enclosure needs justified error bounds for every relevant operation.

## T06 · Boundary

What does an exact conditional label test guarantee?

1. The clinically selected labels are exchangeable
2. Overlapping windows are biologically independent
3. The specified finite-label probabilities were computed without simulation error

**Answer: 3.** Exact arithmetic addresses the calculation, not the truth of the label model or biological independence.

## T07 · Boundary

A mean margin is negative but exceeds its conditional-null mean. A significant test supports which reading?

1. Enrichment relative to that null
2. A positive average lead over the strongest alternative
3. Validated clinical accuracy

**Answer: 1.** A statistic can be negative yet unusually large under a more-negative null. The observed and null-relative effects must both be reported.

## T08 · Boundary

Does this model-output audit establish physical chromatin remodeling?

1. Yes, whenever the diagram distance changes
2. No, independent structural evidence is still needed
3. Yes, if all ties disappear

**Answer: 2.** Predicted maps and abstract intervals are not direct experimental evidence of a located chromosome change.

## T09 · Transfer

All coordinates and shifts are multiplied by ten. How should a fixed-unit ranking rule be transported?

1. Keep the tolerance unchanged
2. Divide the tolerance by ten
3. Multiply the tolerance and numerical allowance by ten

**Answer: 3.** Distances scale with the coordinate unit. Co-scaling thresholds preserves the intended comparisons.

## T10 · Transfer

A finite simulation produces zero exceedances. What should be reported?

1. The plus-one estimate, draw count and Monte Carlo uncertainty
2. A true tail probability of exactly zero
3. An adjusted-value standard error obtained by rescaling a raw-p error

**Answer: 1.** Finite simulation has a resolution floor. Raw-p uncertainty cannot simply be relabeled as adjusted-q uncertainty.

## T11 · Transfer

A new analysis deletes genomic bins. Can the same-support stability statement be used unchanged?

1. Yes, because all topological summaries ignore support
2. No, deletion changes the object and needs its own analysis
3. Yes, provided the diagrams have the same number of points

**Answer: 2.** The theorem requires common support. Equal point counts do not restore deleted bins or the original filtration.

## T12 · Transfer

On the same 84 sites in a second AlphaGenome track, strengthened bounds add 42 decisions while three saturation tests fail. Both bounds abstain at those exceptional sites. What is supported?

1. A new model architecture and clinical superiority were validated
2. Useful additional decision coverage transferred within one model; universal saturation did not
3. Only strengthened bounds detected all three exceptions

**Answer: 2.** The 42 added decisions occur elsewhere. Both bounds abstained at the three exceptions. The same sites and architecture prevent an independent-model or new-locus claim.
