# Post-result diagnostic of all nonsaturating IMR-90 comparisons

Dated 28 October 2026, 19:40 UTC. This protocol is written after the complete paired cross-track analysis showed three of 252 comparisons failing its frozen numerical endpoint-saturation criterion. It precedes the additional path-grid evaluations below. This is an exploratory diagnostic of known exceptions, not a confirmatory replication, new cohort, revised primary endpoint, or new clinical analysis.

## Selection and fixed computation

Include every comparison with a non-tiny shift (abs(delta)>1e-10) and endpoint saturation residual above 1e-10 in the completed original portability summary. There are exactly three: site index 48, chr13:48303721:G, alternate index 2; site index 51, chr13:48307406:G, alternate index 1; and site index 59, chr13:48465370:T, alternate index 0. All are in RB1. Do not choose an extreme subset or substitute cases after computing paths.

Load the previously locked native diagrams and shifts. Evaluate f(lambda)=d_B(D_REF,D_ALT+lambda*delta) directly with GUDHI/Hera delta=0 at lambda=0,0.1,0.25,0.5,0.75,0.9,1 for every selected comparison. Use the existing numerical environment. No API calls, new persistence computation, alternative model output, parameter tuning or clinical-label inference is involved.

Verify lambda=0 and lambda=1 against their previously computed endpoints within 1e-12. At every grid point check the two-endpoint Lipschitz envelope [max(A-lambda*T,C-(1-lambda)*T)-1e-12, min(A+lambda*T,C+(1-lambda)*T)+1e-12], with T=abs(delta). The allowance is practical, not a formal floating-point enclosure. Report every discrepancy and retain failed calculations.

Report signed and absolute departure from the endpoint chord at each sampled lambda, with the previous 1e-10 chord threshold and a 1e-12 sensitivity. Classify only the sampled values: effectively flat (all successive differences within 1e-12), nondecreasing, nonincreasing, or a sampled direction change. Do not infer unobserved breakpoints, a fixed matching, or global path shape from seven points. Nonsaturation alone does not imply nonlinearity; a flat path can fail endpoint saturation while agreeing with its chord.

For every selected site report the already locked simple and strengthened possible/necessary/unique-leader sets at all three original tie tolerances. Record whether each method abstained. Do not revise predictions or reoptimize bounds using these new grid evaluations.

## Reporting and figure

Write the protocol digest and computation-source digest before launching direct grid evaluations. Retain input and per-site lock hashes, query times, actual numerical results and exact selected IDs. The diagnostic is a separate post-result artifact and does not alter the original protocol, frozen predictions, primary pass/fail outcomes or testing families.

If a figure is produced, show all three selected cases, actual sampled points, endpoint chords and analytical endpoint envelopes. Construct envelope vertices from their true line intersections, rather than linear interpolation of sampled upper/lower bounds. Lines joining actual grid points would be visual guides only; prefer separate points to avoid implying a measured continuous trajectory.
