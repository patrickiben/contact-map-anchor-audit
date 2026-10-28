# Input, API and report contracts

Version 0.1.0. This page describes the implemented finite-diagram audit. It does not define an upstream contact-map or persistent-homology pipeline.

## Single-site input

```json
{
  "id": "opposite-slopes",
  "reference": [[0, 4]],
  "alternates": [
    {"id": "increasing", "diagram": [[1, 5]], "delta": 0.25},
    {"id": "decreasing", "diagram": [[-1, 3]], "delta": 0.25}
  ],
  "selected": "increasing"
}
```

`id` and alternate IDs must be nonempty strings. Alternate IDs are unique within a site. Each diagram is an array of `[birth, death]` pairs with finite numeric coordinates and `birth <= death`. Empty diagrams, repeated points and diagonal points are valid. Infinite/essential intervals are unsupported. Booleans are not numeric coordinates.

`delta` is the declared alternate-minus-reference anchor difference. For the manuscript's mean-centered contact-map construction, it is the difference of the two means over their shared off-diagonal support. The toolkit trusts the supplied shift; diagrams alone cannot verify that map-level mean.

`selected` may be omitted or null. If present, it names one alternate and enables descriptive fractional top credit. It does not affect distance computation, anchor selection or bound-based ranking.

The Python CLI also accepts `{ "sites": [site, ...] }`, with a nonempty array and unique site IDs. The browser import accepts one site at a time. Both reject invalid data rather than silently repairing coordinates. The Python CLI also rejects nonstandard `NaN`/`Infinity` constants and duplicate object keys.

## Python entry points

```python
from anchor_audit import (
    audit_site, bottleneck, hausdorff, endpoint_bounds,
    top_set, interval_ranking,
)

score = bottleneck([[0, 4]], [[1, 5]])
report = audit_site(site, steps=21, tolerance=1e-6, allowance=1e-12)
```

| Function | Meaning |
|---|---|
| `bottleneck(D, E, *, backend="reference")` | Finite persistence bottleneck distance, allowing unlimited diagonal matching. |
| `hausdorff(D, E, *, backend="reference")` | Bidirectional nearest-point-or-diagonal lower witness; multiplicity can make it strictly smaller than bottleneck distance. |
| `endpoint_bounds(A, C, delta, lam, error=0)` | Returns `(lower, upper)` from the two endpoint cones, using a common supplied endpoint-error budget. |
| `top_set(scores, tolerance=1e-6)` | IDs within the inclusive tolerance of the maximum; `scores` is a nonempty mapping. |
| `interval_ranking(lower, upper, tolerance=1e-6)` | Possible, guaranteed-top and guaranteed-unique ID lists for compatible score-interval mappings. |
| `audit_site(site, steps=21, tolerance=1e-6, allowance=1e-12, *, backend="reference")` | Computes both endpoints, direct path samples, witnesses, bounds, ranks and optional credit. |

The base package supports Python 3.10+. The optional `hera` backend requires the pinned `fast` extra and Python 3.12+ on a compatible platform. Install it from the repository with `python -m pip install '.[fast]'`.

Default matching uses all finite candidate thresholds and an augmented bipartite matching test in binary64 arithmetic. The reference implementation is bounded at 128 points per diagram; Hera raises this to 20,000. Python allows up to 32 alternates and 2–1,001 path samples. These are resource limits, not assurances of prompt completion on every allowed input.

The browser core separately implements the audit for up to 20 points per diagram, 8 alternates and 2–201 path samples. Its camel-case functions correspond to the Python operations: `auditSite`, `bottleneck`, `hausdorff`, `endpointBounds`, `topSet` and `intervalRanking`. Browser options use an object, for example `auditSite(site, {steps: 21, tolerance: 1e-6, allowance: 1e-12})`.

## CLI

```sh
anchor-audit input.json --output report.json --steps 21 --tolerance 1e-6 --allowance 1e-12 --backend reference
```

The module form is `python -m anchor_audit`. Without `--output`, results go to standard output. Output creation is exclusive: the command refuses an existing path and refuses input/output identity. Invalid inputs and file errors exit with code 2. A successful run exits with code 0.

## Report

The single-site schema identifier is `anchor-audit/report-v1`; a Python batch uses `anchor-audit/batch-v1` and a `sites` array of single-site reports.

Top-level fields include `id`, `numeric_scope`, `tolerance`, `allowance`, `selected`, `alternatives`, `rankings`, `credits` and `warnings`. Python also records backend name and dependency versions when applicable. No patient or variant-classification result is implied by the schema.

Each alternate contains:

| Field | Interpretation |
|---|---|
| `id`, `delta` | Alternate identifier and declared shift. |
| `native`, `centered` | Separately evaluated distances at lambda 0 and 1. |
| `change`, `absolute_shift` | Centered-minus-native distance and absolute delta. |
| `saturation_residual` | `abs(delta) - abs(centered - native)` on the computed values. |
| `near_saturated` | Whether the absolute residual is within twice the supplied allowance. |
| `hausdorff` | Diagonal-augmented lower witness at the shifted endpoint. |
| `lower`, `upper` | Centered-score prediction bounds from the native distance, shift and witness. |
| `path` | Direct sample records containing `lambda`, `distance`, `lower`, `upper`; the bounds use both computed endpoints. |

The native-diagram endpoint bounds are

```text
lower = max(0, native - abs(delta) - allowance, hausdorff - allowance)
upper = native + abs(delta) + allowance
```

They do not select a leader using the computed centered bottleneck distance. The directly computed endpoint is retained to check the resulting decision separately.

`rankings` contains `native`, `centered`, `possible_centered`, `guaranteed_centered`, `guaranteed_unique_centered` and `native_margin_leaders`. Guaranteed top membership permits ties; guaranteed unique membership requires a strict gap exceeding the tolerance. Every guarantee is conditional on valid input bounds. A whole-path native-margin leader satisfies, against every competitor, a native gap exceeding both absolute shifts, the tolerance and the two supplied native error allowances.

If `selected` is absent, `credits` is null. Otherwise it contains native and centered fractional top credit: one divided by the top-set size when the label belongs to it, or zero. This is descriptive agreement with a supplied label, not clinical validation.

## Numerical and scientific scope

The reference solver has no approximation tolerance in its candidate-threshold matching decisions, and Hera is requested with zero approximation parameter. Both still use finite arithmetic. Neither statement constitutes an interval-arithmetic proof for real-valued source maps.

`allowance` is supplied by the caller. For a rigorous enclosure it must cover the relevant input, shift, translation and solver errors. The implementation checks some numerical failure conditions and reports warnings, but does not establish a universal valid allowance. A tiny or zero shift can make near-saturation uninformative.

Changing coordinate units requires co-scaling delta, tolerance and allowance. Overflow, invalid order, unsupported size and some insufficient-budget translation cases produce errors. Do not increase the allowance merely to suppress an unexplained numerical failure; investigate the inputs and intended units.

The path follows a specified translation. It neither optimizes a shift-invariant distance nor chooses a centering fraction using labels. A sampled plot does not prove every unsampled point lies on a straight line. Independent physical or clinical evidence is required for those interpretations of the underlying genomic problem.
