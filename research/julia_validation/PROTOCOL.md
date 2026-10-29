# Targeted independent persistence implementation check

Declared 28 October 2026 before any Julia genomic persistence calculation. This is targeted validation of existing calculations, not a new prospective biological cohort or model test. The current manuscript remains v0.2.3, source SHA-256 05b28b1bcc1b3a715152beb5e07567afc628632851dba5d54e5301ea69483b5d.

## Fixed target

Reuse the previously frozen smallest-hash site per replication gene (indices 7,21,34,44,59,70,75), and include every known IMR-90 nonsaturation exception (48/ALT2,51/ALT1,59/ALT0). The union is nine sites [7,21,34,44,48,51,59,70,75]. Evaluate both historical GM12878 and paired IMR-90 maps, each REF and all three ALTs: 18 site-track combinations, 72 full diagrams, 54 REF/ALT pairs. Include all 512 bins and all 130816 unordered edges per map. No Julia-outcome-based substitutions or exclusions. Missing inputs, errors and discrepancies remain reported.

## Independence and exact comparison target

Ripserer.jl is a separate Julia implementation based on the Ripser algorithm; it is not an unrelated algorithm or independent prediction model. The Julia process must not import/call Python Ripser, GUDHI or saved expected diagrams. Python is used to export raw saved contact-map values and independently compare results afterwards.

For each raw map L loaded as Float64, independently reconstruct w=-L on off-diagonal entries and c=max(0,1-min(w)). Cast shifted off-diagonal w+c to Float32, set the diagonal to zero, and run dense complete weighted-flag H1 over F2. In Ripserer explicitly set threshold=Inf, dim_max=1, modulus=2, cutoff=0, reps=false, alg=:cohomology. No requirement that the supplied symmetric weights satisfy the triangle inequality. All vertices enter before edges. Off-diagonal zeros cannot occur after the declared offset. Convert output interval coordinates to Float64 before subtracting the original Float64 offset c. Ignore only zero-lifetime bars, as in the reference output; preserve all finite positive intervals with multiplicity. Do not deduplicate, thin bins, truncate filtration, round endpoints for comparison, or select a different tolerance after seeing results.

Primary success requires exact equality of complete lexicographically sorted (birth,death) multisets for all 72 diagrams on identical effective Float32 filtration inputs. Independently compare the effective input SHA-256, interval counts, offset, and finite/positive status. A mismatch remains a mismatch; separately diagnose rounding, convention or algorithm causes without quietly relaxing the primary criterion.

## Known-answer foundation

Before genomic execution, run ten named small controls: a filled triangle; a negative-birth four-cycle; a zero-birth four-cycle; an all-tied clique; two equal-lifetime cycles preserving multiplicity; a nonmetric four-cycle; a topology-inactive diagonal perturbation; a Float32 near-tie collapse; a translated negative-birth cycle; and ignored diagonal values. Add twelve fixed-seed small random weighted complete graphs (seed20261028), including negative, zero and tied births. Independently compute their expected H1 using explicit GF2 boundary-matrix reduction on all vertices, edges and triangles with a faces-first tie order. Primary diagrams and effective input bytes must agree. Named controls carry hand-derived expected outputs too.

Mutation checks must show that the comparison rejects a missing duplicate interval, a changed endpoint, an unremoved offset and a corrupted input hash. No production-target mismatch may be suppressed by this checker.

## Downstream propagation

Using the Julia diagrams, recompute native/centered distances with the already-used GUDHI/Hera zero-approximation solver, and reconstruct top sets/fractional credits at tolerances 0,1e-6,1e-5. Independently brute-force the shifted Hausdorff witness where tractable, with a blockwise implementation retaining diagonal alternatives and multiplicity; reconstruct interval/ranking bounds with allowance1e-12. Compare stored endpoints, predictions and nonsaturation status. This is downstream propagation through a shared matching solver, not a second independent bottleneck implementation. Saved original means define the identical comparison target; independently recomputed means are checked separately with declared absolute tolerance1e-12.

## Reporting and stopping

Record exact sources, input/protocol/software/environment hashes, all failures, stdout, wall times and package versions. A setup or API repair is recorded separately and reruns affected controls before genomic execution. Use pinned environment and offline replayable scripts. Stop publication claims if controls or primary targets fail; preserve evidence and diagnose. This finite targeted check does not certify all204 GM12878 sites/all84 IMR90 sites, universal mathematical statements, exact real-arithmetic error budgets, independent-model transfer, biological validity or clinical superiority.
