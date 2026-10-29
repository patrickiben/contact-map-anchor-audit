# Independent filtration-semantics review for the targeted Julia check

28 October 2026. Read-only source and documentation review; no Julia run was performed by this reviewer. This report specifies comparison semantics and controls. It does not certify that the pending Julia execution passes.

## Exact target implemented by the retained Python analysis

The acquisition loader preserves all 512 ordered bins, checks finite exactly symmetric maps, and converts the arrays to NumPy float64. For each map, native off-diagonal edge births are w = −L. The h1 helper computes c = max(0, 1 − min off-diagonal w), adds c to off-diagonal entries, and replaces every diagonal by zero. All vertices therefore precede every shifted edge. It calls Ripser with `distance_matrix=True, maxdim=1, coeff=2, thresh=Inf`.

The installed ripser 0.6.15 Python wrapper explicitly converts the condensed edge values to float32 before its compiled call. Thus the retained target is the full H1 barcode of the shifted, float32-rounded weighted flag filtration. It is not the exact barcode of unrounded float64 −L. The helper widens returned endpoints to float64, subtracts the original float64 c, rejects essential/nonfinite H1 intervals and sorts by birth, then death. Multiplicities are retained. Centered diagrams are translations of these saved native diagrams by each map's original off-diagonal mean; centering does not run PH again on a newly rounded map.

Reviewed source hashes:

- `scripts/analyze_spatial_maps.py`: `929df5588fd2cb4ed7e0dc385630a828e117216d7bd24744c29ccfb4e9423f78`
- `anchor_method/prospective_engine.py`: `edf4895cecf0f7ad30c84df6c21fb416c79b984ccdb451f97b5d4112b2359a0d`
- `portability_imr90_2026-10-28/scripts/phased_engine.py`: `9139528795303ccede7fcd9c3dd73c098e29ffec2ad51e1330a02441c490a761`

## Julia conventions to fix explicitly

Use the matrix constructor, not the point-cloud constructor. A matrix is interpreted directly as weighted edges; computing Euclidean distances between its rows would create another object. Preserve all 130,816 unordered edges and 512 vertices. Export/hash the exact effective float32 matrix with diagonal zero and record c separately as float64. Dense input avoids any sparse zero-as-missing ambiguity.

Recommended call contract: dense `Rips(matrix; threshold=Inf)`, followed by `ripserer(...; dim_max=1, modulus=2, cutoff=0, alg=:cohomology, reps=false)`, and select the second returned diagram. Explicitly convert each endpoint to Float64 before subtracting c. A Float64 matrix containing exactly widened Float32 values has the same edge-value target, but the chosen representation must be recorded.

Ripserer's documented matrix convention uses the diagonal as vertex births. Source checks reject an off-diagonal zero and an edge preceding an endpoint vertex; diagonal zeros are allowed. Its source constructs each higher simplex at the maximum of its edges and does not impose a triangle-inequality validation. The default threshold is the input radius; specify infinity to match the declared full-filtration request. Default cutoff zero excludes zero-persistence intervals, matching the retained positive-lifetime barcode. All multiplicities remain significant. Different tie-breaking may change representative simplices, but should not change this barcode multiset.

Primary sources: [Ripserer API](https://mtsch.github.io/Ripserer.jl/stable/api/) and [versioned Rips implementation linked by that API](https://github.com/mtsch/Ripserer.jl/blob/9def962dbc2a0bc9798509bdb15cc7002944a400/src/filtrations/rips.jl). Record and inspect the actually installed package version/source before treating these semantics as verified for the executed version.

## Controls recommended before genomic interpretation

These are analytical expected answers, not execution outcomes from this review. Define symmetric complete edge-birth matrices and ignore/reset their diagonal as above.

| Control | Expected positive H1 intervals | Defect detected |
|---|---|---|
| Two or three vertices, arbitrary finite edges | Empty | Wrong dimension/empty handling |
| Four-cycle perimeter −2, diagonals −1 | One copy (−2, −1) | Sign and signed-birth restoration |
| Four-cycle perimeter 0, diagonals 1 | One copy (0, 1) | Zero raw edges must survive the shift |
| All off-diagonal weights equal | Empty | Tie handling and spurious zero-length bars |
| Four-cycle perimeter 1, diagonals 10 | One copy (1, 10) | Accidentally enforcing a metric or changing weights |
| Two separate four-cycles on eight vertices; perimeter1, within-cycle diagonals4, all inter-cycle edges20 | Two copies (1, 4) | Lost multiplicity/deduplication |
| Four-cycle perimeter −1.8, diagonals −0.8 | (Float64(1)−c, Float64(2)−c), with original float64 c | Subtracting a rounded Float32 offset |
| Four-cycle perimeter0, diagonals 2^-25 | Empty after the required shift and Float32 rounding, although unrounded H1 is nonempty | Quietly testing a different precision target |

Repeat selected controls under vertex permutation; canonical multisets should remain equal. Add a deliberately truncated threshold below a known death as a negative control: it must not be accepted as a full, finite barcode. A wrong-sign construction and deliberate dropped duplicate should also fail the comparison. Do not infer an implementation defect from comparing unrounded Julia Float64 input against the intentionally rounded retained Python input.

## Comparison and downstream interpretation

For the primary same-effective-input test, require matching interval count and exact equality of lexicographically sorted Float64 birth/death arrays after identical offset restoration. Sorting must preserve duplicate rows. Report any mismatch, nonfinite endpoint or missing planned map; do not change tolerances or select replacement maps after results. If exact equality fails, preserve both outputs before investigating input conversion, truncation, cutoff, coefficient field, sorting and package behavior. A secondary bottleneck residual can help diagnose a mismatch, but must not silently replace the predeclared exact comparison.

Saved IMR-90 records expose these arrays at `representations.native.h1_diagrams_ref_then_alts`, ordered reference then three alternates, and record map/source digests. Site48 has 16,047/16,371/16,333/16,235 intervals. A naive dense independent bottleneck implementation would create very large cost matrices. Exact diagram equality is sufficient for the targeted PH implementation comparison; recalculating scores from identical diagrams with the existing Hera solver is a downstream propagation check, not a separate bottleneck-solver validation.

A second exploratory run on unrounded Float64 edge values would address a different numerical question and must be labeled separately. Neither run would certify a complete real-arithmetic error budget, establish an independent-model replication, or validate experimental chromatin structure. Ripserer is a separate Julia implementation of the Ripser algorithm; describe independence at the implementation level, not as an unrelated mathematical algorithm.
