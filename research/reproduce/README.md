# Research verification and computational source

This is the public v0.2.0 scalar-verification bundle for the BMC Bioinformatics preparation draft. The full raw-map/diagram archive is separately downloadable from [release v0.2.0](https://github.com/patrickiben/contact-map-anchor-audit/releases/tag/v0.2.0).

**AlphaGenome outputs and substantial derivatives are subject to [legally binding provider terms](OUTPUT_TERMS_NOTICE.md).** Original computational code has a separate MIT license. The data are not blanket MIT or unrestricted CC BY material.

Run `python3 verify_derived_results.py --output verification.json` from this directory. Python 3.10 or later suffices; no third-party packages or API key are required. The output reconstructs 495 aggregate comparisons over 84 sites/252 pairs, including 7 versus 49 centered leaders, 42 added decisions and 249/252 saturation. This independently recalculates bounds, ranking sets and credits from saved scalar inputs; it does not regenerate PH or model predictions.

`analysis_source/` contains the scientific engine, acquisition adapter and tests. Full replay uses the maps and instructions in the complete release archive. Frozen protocols and timing records remain historical evidence; a rerun must make a fresh lock instead of pretending to recreate the original timing.

[PREPARATION_README.md](PREPARATION_README.md) preserves the original packaging-time methods and checks. Its private/unresolved-access wording is a dated historical record, superseded by the actual v0.2.0 release and current output-terms notice. The scientific code and scalar results are unchanged. `PREPARATION_BUNDLE_MANIFEST.json` preserves the earlier file hashes; `BUNDLE_MANIFEST.json` binds this public package including the added notices.
