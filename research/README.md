# Manuscript and research artifacts

The **v0.2.5 author-approved submission edition** is *Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps*, submitted to BMC Bioinformatics on **29 October 2026**. The portal confirmed receipt and the **Technical Check** stage; see [current submission status](SUBMISSION_STATUS.md). The v0.2.5 release preserves the author-approved files frozen immediately before submission. On 29 October 2026, Patrick Iben approved the consolidated manuscript and Additional files 1–7 for submission and confirmed that the rework was not under consideration elsewhere. See the [approval-edition record](AUTHOR_APPROVED_EDITION_2026-10-29.md).

[Main manuscript PDF](manuscript.pdf) · [Markdown source](manuscript.md) · [LaTeX source](manuscript.tex) · [Study guide](../education/STUDY_GUIDE.pdf) · [Complete companion](../education/COMPANION.pdf) · [Live demo](https://patrickiben.github.io/contact-map-anchor-audit/)

The article has 23 pages and 31 references. The [final-proof revision record](FINAL_PROOF_REVISION_2026-10-28.md) records the accepted clarifications and integrated Julia check. Scientific inputs and results remain unchanged. The [validation summary](VALIDATION.md) separates scientific replay, independent checks and current packaging verification.

## Supporting files

| File | Content |
|---|---|
| [Additional file 1](Additional_file_1.pdf) | Vertex-thinning scope and finite-bin argument |
| [Additional file 2](Additional_file_2.pdf) | Anchor-path mathematics, witnesses, ranking bounds and counterexamples |
| [Additional file 3](Additional_file_3.pdf) | Retained Monte Carlo results and precision limits |
| [Additional file 4](Additional_file_4.pdf) | Paired-track portability, sensitivity checks and exceptional paths |
| [Additional file 5](Additional_file_5.pdf) | Incorporated eleven-gene within-site audit |
| [Additional file 6](Additional_file_6.pdf) | Reproduction, targeted Julia validation and the fixed-site figure |
| [Additional file 7](Additional_file_7.zip) | Compact scalar-verification archive; [browse its contents](reproduce/) |

Each PDF has matching Markdown and LaTeX source. Figures retain their predicted/synthetic evidence labels. The earlier AlphaGenome preprint and reproduction DOI remain separate immutable records; they do not contain the later spatial and IMR-90 study.

## Choose the appropriate reproduction level

The **compact verifier** uses standard-library Python to reconstruct 495 aggregate comparisons from stored scalar endpoints, witnesses and baseline scores. It checks bounds, ranking sets, exact fractional credits, gene summaries and sampled path envelopes. Its strengthened input/execution checks and 17 failure controls are documented in [its README](reproduce/README.md). It cannot regenerate persistence diagrams, witness distances or model outputs from these scalars.

The **full study archive** in [v0.2.0](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0) contains saved maps, all paired calls, full diagrams, original protocols/locks, source, dependencies, verification records and the earlier 750-file capsule. Download all three parts with `REASSEMBLY_MANIFEST.json` and `reassemble.py`, then follow `README_REASSEMBLY.md`. The script verifies hashes and refuses overwrites. Offline replay requires the specified scientific environment but no API access. Re-acquisition is separate and cannot guarantee unchanged server outputs.

The **targeted Julia capsule** is a separate [v0.2.3 addendum](julia_validation/README.md). It reconstructs 72 full diagrams on nine selected sites across both tracks. The current article and Additional file 6 incorporate its findings and limitations. Its preserved report describes the earlier manuscript state; the downloadable capsule and original commit are unchanged.

These reproduction levels have different scopes. Current package checks do not imply another full scientific replay, formal arithmetic certification or biological validation.

## Terms and interpretation

**Legally binding AlphaGenome Output Terms apply to model outputs and substantial derivatives, including output-derived figures and tables.** Read [OUTPUT_TERMS_NOTICE.md](OUTPUT_TERMS_NOTICE.md). Dated provider terms and modification notices accompany the archives. The original-code MIT license does not relicense provider outputs or grant unrestricted commercial/model-training rights.

The manuscript audits computational representations. It does not establish clinical predictive superiority, physical chromatin validity, transfer to an independent model architecture, a measured runtime advantage or complete real-arithmetic numerical enclosures. Public release does not certify author submission approval or human learner validation.
