# Manuscript, study data and reproducibility

**Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps**  
Patrick Iben · Public draft, 28 October 2026  
**In preparation for BMC Bioinformatics; not submitted or accepted.**

[Manuscript PDF](manuscript.pdf) · [Editable source](manuscript.md) · [LaTeX](manuscript.tex) · [Full study archive](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0) · [Live demo](https://patrickiben.github.io/contact-map-anchor-audit/) · [Study guide](../education/STUDY_GUIDE.pdf) · [Complete companion](../education/COMPANION.pdf)

The prospective IMR-90 test increased centered-leader coverage from **7/84 to 49/84**, adding 42 decisions across six genes without observed contradictions; 35 sites remained unresolved. Universal numerical saturation failed in three comparisons. Both simple and strengthened bounds abstained at those sites. The paired test uses the same 84 replication sites and a second output track within one AlphaGenome model. Clinical-credit changes were mixed across tracks, and RMS baselines remained stronger than centered H1 credit.

## Supporting files

| File | Content |
|---|---|
| [Additional file 1](Additional_file_1.pdf) | Vertex-thinning scope and finite-bin argument |
| [Additional file 2](Additional_file_2.pdf) | Anchor-path mathematics, witnesses, ranking bounds and counterexamples |
| [Additional file 3](Additional_file_3.pdf) | Retained Monte Carlo results and precision limits |
| [Additional file 4](Additional_file_4.pdf) | Portability, gene summaries, sensitivity checks and exceptional paths |
| [Additional file 5](Additional_file_5.pdf) | Incorporated eleven-gene within-site audit |
| [Additional file 6](Additional_file_6.pdf) | Reproduction and verification details |
| [Additional file 7](Additional_file_7.zip) | Compact data/code verification package; [browse its contents](reproduce/) |

Each PDF has a matching Markdown and LaTeX source in this directory. Figures retain their predicted/synthetic evidence labels. The earlier AlphaGenome preprint and reproduction DOI remain separate immutable records; they are not claimed to contain the later spatial and IMR-90 study.

## Choose the appropriate reproduction level

The **compact verifier** runs with standard-library Python and reconstructs 495 aggregate comparisons from stored scalar endpoints, witnesses and baseline scores. See [its README](reproduce/README.md). It checks rank-set bounds, exact rational credits, sensitivities and gene summaries. It cannot regenerate persistence diagrams from those scalars.

The **full study archive** in [v0.2.0](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0) contains saved maps, all paired calls, full diagrams, original protocols/locks, source, dependencies, verification records and the earlier 750-file capsule. Download all three parts with `REASSEMBLY_MANIFEST.json` and `reassemble.py`, then follow `README_REASSEMBLY.md`. The script verifies hashes and refuses overwrites. The archive's offline replay commands require the specified scientific environment but no API access. Re-acquisition is separate and cannot guarantee unchanged server outputs.

The public toolkit checkout stays small; full research inputs are release assets. Independent full PH reruns, independent witness/count checks and current packaging checks have distinct scopes. [Validation summary](VALIDATION.md) records what was actually executed.

## Terms and interpretation

**Legally binding AlphaGenome Output Terms apply to the model outputs and substantial derivatives, including output-derived figures and tables.** Read [OUTPUT_TERMS_NOTICE.md](OUTPUT_TERMS_NOTICE.md); dated provider terms and modification notices accompany the archive. The MIT license for original software does not relicense provider outputs. Public accessibility does not grant unrestricted commercial or model-training rights.

The manuscript is an audit of computational representations. It does not establish clinical predictive superiority, physical chromatin validity, transfer to an independent model architecture, a measured runtime advantage or complete real-arithmetic numerical enclosures. Public release does not certify final author approval for journal submission or human learner validation.
