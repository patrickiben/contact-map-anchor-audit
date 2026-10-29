# Targeted independent persistence check in Julia

**Completed: 72/72 full diagrams agree exactly; 847,288 intervals; all 2,565 downstream checks pass.** All three previously known IMR-90 nonsaturation exceptions remain. The full-study scientific conclusions are unchanged.

[Validation findings](REPORT.md) · [Frozen protocol](PROTOCOL.md) · [Replay instructions](REPLAY.md) · [Primary results](outputs/PRIMARY_COMPARISON.json) · [Downstream results](outputs/downstream/summary.json) · [Independent result review](review/INDEPENDENT_RESULT_REVIEW.md) · [Proposed manuscript integration](PROPOSED_MANUSCRIPT_INTEGRATION.md)

This is a validation addendum to manuscript/software version 0.2.3, dated 28 October 2026. The main manuscript, six supplements and educational editions remain at their existing frozen versions pending the author's final proof review. The addendum is not a new model, cohort, clinical validation or Lean formalization.

Ripserer 0.17.0 in Julia 1.13.0 provides a separate implementation in the Ripser algorithm family. The target is identical effective Float32 filtration input, not an unrounded real-arithmetic calculation. Downstream bottleneck matching deliberately retains the original Hera solver. The protocol and reports specify these limits.

The repository view contains source, pinned environments, protocols and compact results. The downloadable **JULIA_PERSISTENCE_VALIDATION_2026-10-28.zip** capsule additionally contains all selected original study inputs, exported matrices and produced interval files, so replay requires no full-study download or prediction API. See the manuscript's [v0.2.3 release](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.3). The addendum asset does not modify the existing v0.2.3 tag or the immutable full-study v0.2.0 archive.

After extracting the capsule, run `python scripts/verify_capsule.py` to verify its file hashes, then follow REPLAY.md in a new destination. Historical original-run paths are retained as provenance; the replay driver creates new runtime paths. The original scientific execution passed. Capsule preparation and relocated control execution were additionally tested; those packaging checks are distinct from a second full end-to-end replay.

Original software is MIT-licensed. AlphaGenome maps and substantial derived results retain the provider's legally binding output terms; see [OUTPUT_TERMS_NOTICE.md](OUTPUT_TERMS_NOTICE.md), `MODIFICATIONS.md` and `terms/`. The software license does not relicense those outputs.
