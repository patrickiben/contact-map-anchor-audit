# Use the toolkit in a research workflow

The toolkit audits **finite persistence diagrams and a declared relative shift**. It does not generate AlphaGenome predictions, construct diagrams from maps, identify genomic loops, or predict variant pathogenicity.

## 1. Define the upstream comparison

Before calculating diagrams, record the map representation, genomic window, bin support, track, excluded entries, filtration direction, homology degree and coefficient field. Reference and alternate diagrams need compatible conventions.

For the study's full flag filtration with native edge births `w = -L`, subtracting a scalar `a(L)` from every map entry adds `a(L)` to both diagram coordinates. Use `delta = a(L_alt) - a(L_ref)`. For mean centering, compute each mean over the same declared off-diagonal support. Other scalar anchors can be audited by supplying their corresponding delta.

Censoring, infinite intervals, different support, pseudocounts and nonlinear transformations require their own analysis. Do not silently delete essential intervals merely to fit this input format.

## 2. Prepare a finite-diagram record

A single-site JSON record has a reference diagram, a list of alternate diagrams and one shift per alternate. `selected` is optional and only labels descriptive top credit.

```json
{
  "id": "synthetic-example",
  "reference": [[0, 4]],
  "alternates": [
    {"id": "A", "diagram": [[1, 5]], "delta": 0.25},
    {"id": "B", "diagram": [[-1, 3]], "delta": 0.25},
    {"id": "C", "diagram": [[0.5, 4.5]], "delta": 0.25}
  ],
  "selected": "B"
}
```

Coordinates must be finite, with death at least birth. Empty diagrams are valid. Preserve duplicate points because multiplicity affects matching. Use unique alternate identifiers. The browser deliberately limits diagram size for responsiveness; the Python command has a separate documented limit.

The declared delta is an input assumption. The toolkit cannot reconstruct or validate a map mean from diagram coordinates alone.

## 3. Run the audit

For the browser lab, select a synthetic preset or load a local JSON file. Inspect the directly computed distance curve, endpoint envelope, diagram shift, tolerance-defined top sets and unresolved bounds. Importing a file does not make it part of the packaged research dataset.

For Python, from a checkout:

```sh
python -m anchor_audit path/to/site.json --output path/to/report.json
```

The command also accepts a batch object containing a `sites` array. Use the command's `--help` output for path resolution, size limits, path sampling, tolerance and numerical-allowance options. Treat input and output as different files.

For a prospective study, save and hash native-only decisions before evaluating centered distances. The research IMR-90 protocol did this; a browser demonstration of both endpoints is not itself a prospectively locked experiment. Use both-endpoint envelopes for the retrospective whole-path audit and native-only intervals for prospective centered-leader decisions.

## 4. Interpret the report

| Report element | What it answers | What it does not establish |
|---|---|---|
| Native and centered distances | How the specified shift changes the computed comparison | Physical contact change or a clinical effect |
| Direct path samples | Values recomputed at the recorded fractions | Every unsampled point without an additional theorem or enclosure |
| Endpoint envelope | A path bound under the stated endpoint-error assumptions | Automatically validated floating-point error |
| Near-saturation diagnostic | Whether the computed endpoint change nearly reaches its shift bound | Exact equality for inaccessible real-valued source outputs |
| Native-margin leader | A sufficient whole-path ranking condition under the stated bounds | That the leader is biologically correct |
| Hausdorff-strengthened endpoint bounds | Whether a centered leader can be identified without using its computed centered distance for selection | A universal substitute for bottleneck matching or a measured runtime speedup |
| Selected credit | The selected label's share of the tolerance-defined top set | Predictive accuracy against independent clinical truth |
| Warnings | Invalid or unresolved parts of the supplied analysis | Permission to omit unfavorable sites |

The audit's main score is bottleneck distance. A larger score means a larger diagram discrepancy under the declared representation. It is not intrinsically a “better allele.” Choose the scientific interpretation separately.

## 5. Report enough for someone else to check it

Retain the input JSON, audit output, software version or commit, coordinate units, upstream diagram producer, delta convention, tolerance, numerical allowance and any errors. Record how sites were selected and whether comparisons were planned before outcomes were inspected.

Scale tolerance and numerical allowances whenever coordinate units change. Check more than one defensible tolerance when apparent decisiveness is the finding. Keep a fixed primary rule; label later checks as sensitivity analyses.

For larger cohorts, report the sites left unresolved, strict leaders replaced, ties introduced or resolved, alternate baselines and every failed planned evaluation. Do not choose the centering fraction to favor selected labels and then call the result predeclared.

## 6. Keep evidence classes separate

Synthetic presets verify and explain mathematical behavior. The study panel reports aggregate results from selected predicted maps. User imports are a third evidence source and must carry their own provenance.

A reusable computation helps make the method inspectable. It does not establish independence from model training, biological exchangeability, calibrated clinical performance or experimental chromosome architecture. Those require different evidence.

The paired IMR-90 study illustrates why abstention and added coverage need separate reporting: both methods abstained at all three saturation-exception sites, while strengthened bounds added 42 decisions elsewhere. The full v0.2.0 study archive supplies the map inputs separately from small scalar-verification records, with provider output notices retained.

The targeted Julia addendum checks 72 full diagrams from nine replication sites on both tracks using Ripserer. Exact agreement concerns identical effective float32 inputs; downstream Hera matching remains shared. The full-study replay, targeted separate-implementation check and compact scalar verifier answer different reproducibility questions. None supplies Lean formalization, biological validation or human author approval.
