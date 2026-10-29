# Anchor Audit Toolkit

**Inspect how a declared change of diagram origin changes distances, ties and rankings.** This repository combines a reusable Python auditor, a local browser lab and a source-linked educational companion.

Mean centering can translate persistence intervals without changing their lifetimes. If reference and alternate diagrams translate by different amounts, their bottleneck distance can still change. A tied ranking may then become unique. The toolkit makes that mechanism inspectable and distinguishes a more decisive ranking from evidence of better clinical discrimination.

**Manuscript:** *Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps*. In preparation for **BMC Bioinformatics**, not submitted (28 October 2026). The earlier AlphaGenome audit received editorial desk decisions for journal fit; its preprint and archived data remain separate versioned records.

[Latest manuscript](research/manuscript.pdf) · [Code and toolkit](https://github.com/patrickiben/contact-map-anchor-audit) · [Live demo](https://patrickiben.github.io/contact-map-anchor-audit/) · [Study guide PDF](education/STUDY_GUIDE.pdf) · [Complete companion PDF](education/COMPANION.pdf) · [Manuscript → code → demo map](https://github.com/patrickiben/patrickiben/blob/main/RESEARCH_MAP.md)

## Choose a starting point

- **Explore:** [open the interactive lab](https://patrickiben.github.io/contact-map-anchor-audit/). Move the centering slider, compare synthetic controls, inspect unresolved winners and export an audit report.
- **Use your diagrams:** run the Python command on finite persistence-diagram JSON, with an optional accelerated backend for larger inputs.
- **Learn:** choose the [concise study guide](education/STUDY_GUIDE.pdf) or [complete companion](education/COMPANION.pdf), with [Markdown editions and coverage records](education/README.md). The interactive lessons, [worked examples](education/WORKED_EXAMPLES.md) and [practice questions](education/PRACTICE.md) provide additional routes into the material.
- **Integrate:** see [API and input/output contracts](docs/API.md) and the [researcher workflow](education/RESEARCHER_WORKFLOW.md).

For an offline copy, download this repository and open `standalone/AnchorAuditLab.html` in a browser. Its scripts, styles, teaching material and synthetic presets are embedded in one file; no server is needed. The standalone file is generated from the same sources as the hosted lab.

To serve the individual assets from a checkout:

```sh
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. The application uses local assets, processes imported JSON in the browser and needs no AlphaGenome API key or server-side analysis service. The Python toolkit runs locally as well.

## Python quick start

The reference implementation requires **Python 3.10 or newer** and has no runtime dependencies. Install from this checkout; no PyPI release is implied.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install .
anchor-audit examples/minimal.json --output report.json
```

The equivalent module command is:

```sh
python -m anchor_audit examples/minimal.json --output report.json
```

`report.json` must be a new file. The CLI refuses to overwrite an existing output or its input. For a batch of synthetic controls:

```sh
anchor-audit examples/synthetic.json --steps 21 --tolerance 0.000001 --allowance 0.000000000001
```

Without `--output`, JSON is printed to standard output. `selected` is optional; supplying it adds descriptive fractional top credit, not a clinical accuracy estimate.

### Larger diagrams

The optional pinned stack needs **Python 3.12 or newer** and compatible platform wheels:

```sh
python -m pip install '.[fast]'
anchor-audit path/to/diagrams.json --backend hera --steps 21 --output larger-audit.json
```

The accelerated backend uses GUDHI Hera with zero approximation parameter and SciPy nearest-neighbor queries. This is an algorithm setting, not formal exact-real certification or a measured speedup claim.

| Route | Points per diagram | Alternates per site | Main use |
|---|---:|---:|---|
| Browser reference implementation | 20 | 8 | Teaching, small controls and inspection |
| Python reference implementation | 128 | 32 | Transparent dependency-free audits |
| Python optional Hera backend | 20,000 | 32 | Larger user-supplied diagrams on a compatible environment |

These are input limits, not runtime guarantees. The reference matching implementation uses quadratic memory and cubic-order matching work at candidate thresholds. Path sampling repeats matching; reduce the sample count deliberately when exploring larger inputs, and record the choice.

## What the audit returns

For every alternate, the report records native and centered distances, the declared shift, numerical saturation residual, a diagonal-augmented Hausdorff witness, native-diagram endpoint bounds and directly computed path samples. It also reports native and centered top sets, possible and guaranteed endpoint members, bound-supported unique leaders and whole-path native-margin leaders.

The centered endpoint is independently evaluated for comparison. The native-diagram bounds do not use that centered distance or the selected label to choose their leader. They can return an unresolved set.

A small numerical residual is **near-saturation on computed inputs**. The supplied allowance is a practical error budget; the software does not prove it encloses every input, shift, translation and solver error. Ranking guarantees remain conditional on valid bounds.

## Research basis and boundaries

The toolkit accompanies Patrick Iben's author-review manuscript *Auditing preprocessing-sensitive allele rankings in predicted chromatin contact maps*, dated 28 October 2026. Its exact source hash and educational line mappings are in [the source map](education/SOURCE_MAP.json). The [current public draft and six supplements](research/README.md) are included here. No journal acceptance or new DOI is claimed.

The prospective IMR-90 test identified **49/84 centered leaders versus 7/84 with simple bounds**, adding 42 decisions across six genes with no observed contradictions and 35 unresolved sites. Universal numerical saturation failed in three comparisons; both bounds abstained at those sites. This paired test uses the same 84 replication sites and a second output track of one model. RMS baselines still exceeded centered H1 selected-allele credit.

A subsequent [targeted Julia check](research/julia_validation/REPORT.md) reproduced **72 full diagrams and all 847,288 intervals exactly**, including multiplicities, and preserved all three known IMR-90 exceptions. Its 22 controls and 2,565 downstream checks passed. This adds separate-implementation evidence within the Ripser algorithm family; matching still uses Hera. The current manuscript and teaching editions remain at v0.2.3 while the new verification wording awaits final author review.

The research contribution is an executable audit of a specified preprocessing path, its ranking consequences and its observed behavior in predicted contact maps. Bottleneck distance, elementary stability bounds and shift-invariant comparisons have established precedents; this is not a claim to a new generic metric.

The browser separates three evidence classes:

1. **Synthetic presets:** constructed examples of tie splitting, opposite slopes, turning paths, diagonal caps and multiplicity.
2. **Study summary:** aggregate author analysis results from the predicted-map cohorts, bound to named source artifacts and the manuscript hash.
3. **User imports:** diagrams supplied by the user, with provenance and interpretation determined by their own upstream workflow.

The small toolkit checkout does not contain model weights or raw genomic map arrays. The [full study archive in release v0.2.0](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0) supplies the stored maps, paired calls, diagrams, source and offline replay instructions as three checksum-verified download parts. [Provider output terms and modification notices](research/OUTPUT_TERMS_NOTICE.md) apply separately to the model outputs and substantial derivatives. The audit CLI and browser lab take diagrams as input; the separate Julia validation capsule regenerates the selected full diagrams from saved maps. Neither locates genomic loops, infers pathogenicity or establishes physical chromatin remodeling. The study's sharper rankings did not establish a consistent improvement in clinically selected-allele credit.

For the earlier background-profile audit, see the separate [Same-Site Allele Explorer](https://github.com/patrickiben/alphagenome-allele-demo). Its endpoint differs from the direct reference-versus-alternate diagram comparison used here.

## Educational companion

The printable editions follow the same structure as the other research repositories: [STUDY_GUIDE](education/STUDY_GUIDE.pdf) for a concise introduction, and [COMPANION](education/COMPANION.pdf) for the main manuscript and all six current supplementary files. Both also have Markdown editions. The [complete coverage map](education/COMPLETE_COVERAGE.md) and [artifact manifest](education/ARTIFACTS.json) identify their scope and versions.

The browser companion has ten lessons, a glossary, six worked examples and twelve interactive practice questions with feedback. The [aggregate-value map](education/STUDY_VALUE_MAP.json) and [source map](education/SOURCE_MAP.json) make that adaptation inspectable.

The quiz is practice, not the original locked human transfer test. Human learner validation and author approval are not certified by a software check. No educational effectiveness or learner pass rate is claimed.

## Development disclosure

OpenAI Codex assisted with implementation, educational adaptation, mathematical review and automated verification. Qwen3.8 assisted earlier manuscript drafting; Qwen3.8-Max generated author-supplied QC reports checked against retained artifacts. AI-assisted review and passing software tests do not constitute independent human review, human learner certification or clinical validation. Patrick Iben is the named project author; the section-by-section edits are accepted, while final proof and submission approval remain pending.

## Verification

Python numerical tests include small-diagram matching oracles, boundary cases and metamorphic checks. The browser core has separate numerical tests; the browser suite exercises interactions and accessibility checks. The optional-backend tests skip when its dependencies are absent. The default CI job does not certify every optional platform/backend combination.

```sh
python -m unittest discover -s tests -p 'test_*.py'
python scripts/build_education.py --check --self-test
python scripts/check_pdf_companions.py
python scripts/build_standalone.py --check
npm ci
npm run test:core
npx playwright install --with-deps chromium
npm test
```

Educational checks can additionally verify the frozen manuscript and retained research artifacts when those are available locally:

```sh
python scripts/build_education.py --check --self-test --source research/manuscript.md --research-root path/to/contact3d_rework_2026-10-28
```

These checks support implementation, content and source correspondence. They do not replace mathematical proof, formal floating-point certification, biological validation or a human review of scientific interpretation.

The printable editions use the portfolio's Georgia/Arial typography and Letter page layout. To rebuild them, install ReportLab and pypdf, make Pandoc available, and run `python scripts/build_pdf_companions.py`. The renderer uses the macOS Supplemental fonts by default; set `ANCHOR_PDF_FONT_DIR` to a directory containing the documented font files on another system. After any change, inspect the rendered pages before refreshing the artifact manifest. The standard-library PDF check verifies the released files without requiring those authoring dependencies.

## Citation and licensing

Use [CITATION.cff](CITATION.cff) to cite software version 0.2.3, and record the exact commit used for an analysis. The complete study data remain archived in v0.2.0. Version 0.2.3 incorporates the author-approved read-through edits, adds the Holm citation, clarifies slope units and updates the teaching materials; see the [revision record](research/AUTHOR_READTHROUGH_REVISION_2026-10-28.md). The preceding [v0.2.2 QC revision](research/QC_REVISION_2026-10-28.md) improved the S6 figure and disclosures. These revisions leave the archived scientific data and calculations unchanged. Final proof and submission approval remain pending. No DOI has been assigned in this file.

Original project code and educational text are licensed under [MIT](LICENSE), copyright 2026 Patrick Iben. Third-party libraries and user-supplied data retain their own licenses and terms. The code license does not relicense AlphaGenome assets or outputs, which are included only in the separately identified study archive under the provider terms. See the [output terms notice](research/OUTPUT_TERMS_NOTICE.md).
