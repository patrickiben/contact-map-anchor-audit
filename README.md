# Anchor Audit Toolkit

**Inspect how a declared change of diagram origin changes distances, ties and rankings.** This repository combines a reusable Python auditor, a local browser lab and a source-linked educational companion.

Mean centering can translate persistence intervals without changing their lifetimes. If reference and alternate diagrams translate by different amounts, their bottleneck distance can still change. A tied ranking may then become unique. The toolkit makes that mechanism inspectable and distinguishes a more decisive ranking from evidence of better clinical discrimination.

## Choose a starting point

- **Explore:** [open the interactive lab](https://patrickiben.github.io/contact-map-anchor-audit/). Move the centering slider, compare synthetic controls, inspect unresolved winners and export an audit report.
- **Use your diagrams:** run the Python command on finite persistence-diagram JSON, with an optional accelerated backend for larger inputs.
- **Learn:** follow the [educational companion](education/README.md), [worked examples](education/WORKED_EXAMPLES.md) and [practice questions](education/PRACTICE.md).
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

The toolkit accompanies Patrick Iben's author-review manuscript *Auditing allele rankings in genomic predictions: consequence controls and contact-map anchoring*, dated 28 October 2026. Its exact source hash and educational line mappings are in [the source map](education/SOURCE_MAP.json). The manuscript is not copied into this repository; no journal acceptance or new DOI is claimed.

The research contribution is an executable audit of a specified preprocessing path, its ranking consequences and its observed behavior in predicted contact maps. Bottleneck distance, elementary stability bounds and shift-invariant comparisons have established precedents; this is not a claim to a new generic metric.

The browser separates three evidence classes:

1. **Synthetic presets:** constructed examples of tie splitting, opposite slopes, turning paths, diagonal caps and multiplicity.
2. **Study summary:** aggregate author analysis results from the predicted-map cohorts, bound to named source artifacts and the manuscript hash.
3. **User imports:** diagrams supplied by the user, with provenance and interpretation determined by their own upstream workflow.

No raw AlphaGenome maps, model weights or per-site genomic diagram dataset is packaged here. The package does not generate persistence diagrams from contact maps, locate genomic loops, infer pathogenicity or establish physical chromatin remodeling. The study's sharper rankings did not establish a consistent improvement in clinically selected-allele credit.

For the earlier background-profile audit, see the separate [Same-Site Allele Explorer](https://github.com/patrickiben/alphagenome-allele-demo). Its endpoint differs from the direct reference-versus-alternate diagram comparison used here.

## Educational companion

The companion has ten lessons, a glossary, six worked examples and twelve interactive practice questions with feedback. The [aggregate-value map](education/STUDY_VALUE_MAP.json) and [source map](education/SOURCE_MAP.json) make the adaptation inspectable.

The quiz is practice, not the original locked human transfer test. Human learner validation and author approval are not certified by a software check. No educational effectiveness or learner pass rate is claimed.

## Development disclosure

OpenAI Codex assisted with implementation, educational adaptation, mathematical review and automated verification. AI-assisted review and passing software tests do not constitute independent human review, human learner certification or clinical validation. Patrick Iben is the named project author; author review of the complete revised research manuscript and its interpretations remains pending.

## Verification

Python numerical tests include small-diagram matching oracles, boundary cases and metamorphic checks. The browser core has separate numerical tests; the browser suite exercises interactions and accessibility checks. The optional-backend tests skip when its dependencies are absent. The default CI job does not certify every optional platform/backend combination.

```sh
python -m unittest discover -s tests -p 'test_*.py'
python scripts/build_education.py --check --self-test
python scripts/build_standalone.py --check
npm ci
npm run test:core
npx playwright install --with-deps chromium
npm test
```

Educational checks can additionally verify the frozen manuscript and retained research artifacts when those are available locally:

```sh
python scripts/build_education.py --check --self-test --source path/to/PROPOSED_contact_channel_3d_VALIDATED.md --research-root path/to/contact3d_rework_2026-10-28
```

These checks support implementation, content and source correspondence. They do not replace mathematical proof, formal floating-point certification, biological validation or a human review of scientific interpretation.

## Citation and licensing

Use [CITATION.cff](CITATION.cff) to cite software version 0.1.0, and record the exact commit used for an analysis. No DOI has been assigned in this file.

Original project code and educational text are licensed under [MIT](LICENSE), copyright 2026 Patrick Iben. Third-party libraries and user-supplied data retain their own licenses and terms. The code license does not relicense AlphaGenome assets or outputs, which are not bundled as a raw or per-site dataset in this package.
