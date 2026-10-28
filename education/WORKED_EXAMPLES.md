# Worked examples: what an anchor can change

Every example here is synthetic. Coordinates describe finite persistence intervals, not genomic positions or experimentally measured contacts. They can be checked by hand. The browser evaluates the sampled path directly; the endpoint lines are not assumed to be correct for every example.

## 1. Break a native tie without changing any lifetime

Use a reference diagram `D = {(0, 4)}` and three alternates:

| Alternate | Native diagram | Declared shift delta | Native distance |
|---|---|---:|---:|
| A | {(1, 5)} | 0.25 | 1 |
| B | {(-1, 3)} | 0.25 | 1 |
| C | {(0.5, 4.5)} | 0.25 | 0.5 |

Every interval has lifetime 4. Shifting both coordinates preserves that lifetime.

At centering fraction lambda, the three distances on this segment are:

- A: `1 + 0.25 lambda`
- B: `1 - 0.25 lambda`
- C: `0.5 + 0.25 lambda`

The real-point matching is cheaper than sending the points to the diagonal throughout this segment. At lambda = 1, the distances are 1.25, 0.75 and 0.75. The native top set `{A, B}` becomes the unique leader `{A}`.

If B is the selected label, its top credit falls from 1/2 to zero. That label is an illustrative choice; it does not make B clinically correct. The example shows that a more decisive ranking need not improve selected-label credit.

With tie tolerance 0.1, A and B remain in the same top set through lambda = 0.2, including the boundary in exact arithmetic. They separate only when `0.5 lambda > 0.1`. Numerical implementations also have finite-precision limits near a boundary.

**Try it:** keep the diagrams fixed and change the tolerance. Which changes come from the distance, and which come from the rank rule?

## 2. The same scalar information can have opposite effects

Against `D = {(0,4)}`, compare `E+ = {(1,5)}` and `E- = {(-1,3)}`. Both start at distance 1. Both receive the same shift 0.25.

The first distance becomes 1.25; the second becomes 0.75. Thus the native distance and scalar shift alone cannot universally reconstruct the centered distance. Relative diagram location supplies directional information that those two numbers omit.

**Try it:** explain why “the mean shift determines the response” is stronger than the evidence permits.

## 3. Endpoints alone need not trace a straight line

Use `D = {(0,4)}`, `E = {(-1,3)}` and delta = 2. The distance along the segment is `|2 lambda - 1|`.

It starts at 1, reaches zero at lambda = 1/2, then returns to 1. Its endpoint change is zero although the allowed shift magnitude is 2. The endpoint envelopes contain the path, but a straight interpolation between the endpoints would miss the turn.

The exact-saturation theorem is conditional: only when the absolute endpoint difference equals the shift bound do the envelopes collapse to a line. A useful audit must include nonsaturating controls such as this one.

## 4. Diagonal matching creates a flat cap

Use `D = E = {(0,2)}` and delta = 2. Direct point-to-point matching costs `2 lambda`. Matching each interval to the diagonal costs 1. Therefore the bottleneck distance is `min(2 lambda, 1)`.

The path rises and then becomes flat. This is another reason not to infer a straight full path merely because some short segment looks linear.

## 5. A nearest-neighbor bound can miss multiplicity

Let `D` contain **two copies** of `(0,4)` and `E` contain one copy. Every real point has an identical nearest point in the other diagram, so the diagonal-augmented Hausdorff bound is zero.

A matching cannot use the single E point twice. One D point must go to the diagonal at cost 2. The bottleneck distance is therefore 2. Keep repeated points in imported data; deduplication changes the object.

## 6. Strong versus inconclusive ranking bounds

Suppose an audit supplies valid centered-score intervals A: `[1.2,1.3]`, B: `[0.6,0.8]`, C: `[0.7,0.9]`, with tolerance 0.1. A is always more than 0.1 above the other scores, so A is a bound-supported unique leader.

If A instead has interval `[0.8,1.3]`, the same conclusion is no longer secured. An unresolved result is useful: it identifies where another matching calculation or a tighter error bound could change the decision.

These are statements conditional on the validity of the input bounds. A practical floating-point allowance is not automatically a proof that every numerical operation is enclosed.

## Source and scope

The translation, endpoint, opposite-slope, multiplicity and ranking arguments correspond to Sections 3.1–3.4 of the author-review manuscript identified in [SOURCE_MAP.json](SOURCE_MAP.json). The three-alternate tie example and interval-ranking exercise are teaching constructions. They are not additional genomic findings or a claim of new generic persistence theory.
