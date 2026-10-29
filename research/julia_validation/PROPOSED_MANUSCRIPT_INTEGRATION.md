# Proposed integration for final author proof review

Status: proposed wording; not yet inserted into the frozen v0.2.3 manuscript or supplements. The numerical check is complete. This text adds verification evidence without changing the scientific conclusions or the cohort-level results.

## Main manuscript: Computation, verification and AI assistance

Keep the accurate description of the earlier full replay and its shared PH implementation. Immediately after that description, insert:

> A targeted check with Ripserer 0.17.0 in Julia 1.13.0 separately reconstructed 72 full H1 diagrams from nine replication sites on both tracks, including every known IMR-90 nonsaturation exception. All 847,288 intervals matched the original results exactly on identical effective float32 filtration inputs, with multiplicity preserved. Twenty-two small-graph controls matched an explicit boundary-matrix reduction. Recalculation from the Julia diagrams preserved the checked distances, ranking decisions and all three exceptions. This is agreement between separate implementations in the Ripser algorithm family; downstream bottleneck matching still used Hera, and the check does not establish biological validity or full-cohort cross-implementation agreement.

Add the Ripserer reference at first use and renumber later references consistently:

Čufar M. Ripserer.jl: flexible and efficient persistent homology computation in Julia. Journal of Open Source Software. 2020;5(54):2614. doi:10.21105/joss.02614.

## Additional file 6: new targeted Julia-check subsection

Integrate the fixed sampling rule, full-filtration/Float32 contract, 22 controls, four mutations, 72 diagrams/847,288 intervals, 108 matching distances, 54 witnesses, 2,565 downstream checks and unchanged exceptions from REPORT.md. State the shared Hera solver and algorithm-family limitation. Link the independently versioned validation capsule and its checksum. Preserve the earlier full-replay record as historical evidence.

## After author acceptance of wording

Rebuild the main and Additional file 6 PDFs; inspect affected pages and reference pagination. Refresh the manuscript hash, private submission package, public manuscript files, artifact manifests and teaching-source bindings together. The existing v0.2.3 PDF and source remain the current final-proof baseline until that rebuild. Final author scientific and submission approval remains a separate, pending attestation.
