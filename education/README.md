# Educational companion

Choose the depth you need, using the same printable and browser-readable editions as the other research projects:

- **Concise study guide:** [Markdown](STUDY_GUIDE.md) or [PDF](STUDY_GUIDE.pdf), for the research question, principal findings and interpretation.
- **Complete companion:** [Markdown](COMPANION.md) or [PDF](COMPANION.pdf), covering the frozen main manuscript and all six current additional files, with worked explanations and answered checks.
- **Coverage and versions:** [Source-to-unit coverage](COMPLETE_COVERAGE.md) and [artifact hashes](ARTIFACTS.json) make the printable editions inspectable.

For an interactive route, use the [Anchor Audit Lab](https://patrickiben.github.io/contact-map-anchor-audit/) and its ten [guided lessons](GUIDE.md). The central question is concrete: how can centering make an allele ranking more decisive while leaving every interval lifetime unchanged?

- [Guided lessons and glossary](GUIDE.md): ten linked steps from data objects to interpretation.
- [Worked synthetic examples](WORKED_EXAMPLES.md): tie splitting, opposite responses, a turning path, diagonal caps, multiplicity and unresolved rankings.
- [Practice with explained answers](PRACTICE.md): twelve questions, also offered interactively in the lab.
- [Researcher workflow](RESEARCHER_WORKFLOW.md): prepare diagrams, declare a shift, inspect results and report limitations.
- [Source and coverage map](SOURCE_MAP.json): exact manuscript hash, line ranges, excerpt hashes and educational asset hashes.
- [Aggregate-value map](STUDY_VALUE_MAP.json): the study-summary numbers and their generating artifact selectors.

The manuscript basis is the 28 October 2026 author-review candidate, *Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps*, SHA256 `fdaa582b89b89651f0629162b94acacdb6cfdab93c0696e7029e9a5676be1969`. That public draft is supplied with the versioned study release; no journal acceptance or new DOI is implied.

The current rework has not been submitted. The [earlier AlphaGenome audit's teaching materials](https://github.com/patrickiben/alphagenome-allele-demo/tree/main/education) remain tied to its preprint v3 and five earlier supplements. They explain that prior version; the new companion covers the current rework and Additional files 1–6. The [research map](https://github.com/patrickiben/patrickiben/blob/main/RESEARCH_MAP.md) connects both versions to their respective code and demonstrations.

The synthetic presets and teaching examples are not genomic observations. The study panel separately presents aggregate author analysis of predicted maps. Imported data are supplied by the user and require their own provenance.

The original source-linked reading guide passed mechanical checks but retained pending human reviews and an unscored human transfer assessment. This expanded companion is a new adaptation. Its multiple-choice quiz is **practice with feedback**, not the original locked test. No human learner pass rate, educational effectiveness, author approval or release verdict is fabricated.

To check the local content and hashes:

```sh
python scripts/build_education.py --check
```

If you have the frozen manuscript and research bundle, additionally verify the exact source excerpts and aggregate producer values:

```sh
python scripts/build_education.py --check --source path/to/PROPOSED_BMC_BIOINFORMATICS.md --research-root path/to/contact3d_rework_2026-10-28
```

The public check can detect content drift without the manuscript. Only the optional source check verifies against the actual source bytes. Human clarity, accessibility and transfer testing remain separate tasks.

The full study archive is released with [v0.2.0](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0), alongside the public manuscript, code, protocols and verification records. Toolkit code is MIT-licensed; provider model outputs retain their separate terms and attribution notices. Public availability supports reproduction, not clinical validity, author journal approval or human learner effectiveness.

AlphaGenome outputs and substantial derivatives, including the genomic numerical results discussed here, remain subject to the AlphaGenome Output Terms, separate from the MIT software license. The study release includes the binding terms, required attribution, modification record, and three-part archive checksums/reassembly instructions. Saved raw maps retain their original bytes; mean centering, persistence analysis, ranking and visualization are documented processing steps.
