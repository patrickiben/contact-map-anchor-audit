# Reproduce the Figure S6.1 display

This plotting-only revision uses the fixed first GM12878 site, chr9:128203567:C (DNM1), and the original selected alternate T. It does not change saved predictions, persistence diagrams, distances or scientific results.

Download and reassemble the unchanged [v0.2.0 full study archive](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0), then unpack it. With NumPy and Matplotlib available, run from the repository root:

```sh
python research/figures/render_s6.py   --data-dir /path/to/full_release/legacy/astra_genomic   --summary-file /path/to/full_release/legacy/compact_summary_fixture.json   --output-dir /path/to/new_figure_directory
```

The output directory must not already contain the generated files. The script resolves the fixed site's NPZ within the supplied data directory; it does not follow the historical machine-specific manifest path. Figure production has optional scientific dependencies; the reference audit CLI remains dependency-free.

Panels A, B and C use all 512 bins and mask the diagonal only for display. Panel B uses a signed linear scale of ±0.00390625 (99th percentile of absolute off-diagonal differences). Exactly 788/261632 display cells (0.301%) are colour-clipped; extension triangles and the caption disclose this. Panel C shows the same difference at its full ±0.01171875 linear range with no clipping. Both matrix triangles count toward the display-cell percentage, not independent observations. Panel D retains the three original allele distances.

No smoothing, aggregation, nonlinear transform or effect-selected site is used. Over half the off-diagonal differences are exactly zero. The full-range panel preserves the original amplitude context.

`figure_s6_display.json` records the inputs, selected site, limits, clipped count, original bar values and generator hash. Regeneration from the unpacked release reproduced the adopted PNG byte-for-byte (SHA-256 `4113b99e7102886cc2ae94f71b2fa999f9964c2cf41f623e9cabc58ebdb81d59`). PDF/SVG metadata can differ between executions; reproducibility of the plotted values is recorded separately from output byte identity. The final 6.5 × 7-inch figure and caption were inspected together on page 3 of Additional file 6.

[Provider Output Terms](../OUTPUT_TERMS_NOTICE.md) apply to output-derived figures.
