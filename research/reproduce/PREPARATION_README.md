# Private reproducibility review bundle

Prepared 28 October 2026 for the BMC Bioinformatics candidate. This is a concrete, tested review bundle, not a claim that the study dataset has already been publicly deposited. It makes no network requests by default. Original research sources and frozen experiment files remain unchanged.

## What can be reproduced here

Run with Python 3.10 or later and no third-party packages:

```sh
python verify_derived_results.py --output DERIVED_VERIFICATION.json
```

The independent scalar verifier reconstructs simple and strengthened score bounds, all rank sets, exact fractional selected-allele credit, gene and leave-one-gene-out summaries at all three fixed tolerances, endpoint saturation and the seven-point exploratory path envelopes. It compares 495 aggregate values, all 84 sites and 252 pairs. The result is 7 versus 49 bound-supported leaders at tolerance 1e-6, 42 additional leaders, 35 unresolved sites and 249/252 numerically saturated endpoints. It validates predictions against stored centered scores. The original native lock is evidence of the timing of those predictions; running this verifier does not recreate that timing independently.

`data/endpoint_scalars.json` contains derived native/centered distances, mean differences, numerical witness values, interval predictions and baseline scores, with opaque site indices and gene names. It contains no raw contact maps, sequences, genomic coordinates, persistence-diagram points or credentials. Cohort input coordinates are separately preserved in `provenance/candidate_cohort.json` so a full replay can use the declared inputs. These are public-variant study inputs, not patient records collected for this study.

The scalar verifier does **not** recompute model outputs, persistent homology, bottleneck distances, nearest-neighbor witnesses or matrix baselines. Those scalar inputs must be independently checked using the saved maps/diagrams. The full 84-site reference replay and independent 252-witness audit were completed in the research workspace; this compact bundle does not replace them. No performance benchmark or biological validation is implied.

## Analysis source and environment

`analysis_source/` preserves the imported dependency layout of the scientific engine. Original scientific sources are copied byte-for-byte. `SOURCE_PROVENANCE.json` records original and bundled hashes. The only acquisition adaptation removes an author-specific credential path, allows externally supplied output and historical-control directories, and reads `ALPHAGENOME_API_KEY` from the environment. No key is stored. A different acquisition-source hash requires a new replay freeze; the historical freeze must never be silently modified to accommodate it.

The analysis environment used Python 3.14.7. `requirements_final.lock` records package versions; `requirements.hashed.lock` pins distributions by hash. Its author-specific generation-command comment was removed; package/hash entries are unchanged. The new layout was tested in the previously created clean analysis environment. This turn did not install these dependencies into another clean environment or rerun the full genomic cohort again.

```sh
python -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.hashed.lock
.venv/bin/python analysis_source/portability/scripts/test_phased_engine.py
.venv/bin/python analysis_source/portability/scripts/summarize_portability.py --self-test
```

The copied nine phased-engine controls and twelve frozen-summary boundary controls pass. They cover lock tampering/missing locks, synthetic agreement with the reference engine, non-saturation/non-affine controls, wrong-leader rejection, incomplete data and operational thresholds. See `PHASED_SOURCE_CONTROLS.log` and `SUMMARY_SOURCE_CONTROLS.json`.

To rerun PH from the original saved maps, supply the original external manifest and its corresponding files. The manifest supports paths relative to its own location. Use a **new** output directory:

```sh
.venv/bin/python analysis_source/portability/scripts/phased_engine.py \
  --manifest /path/to/original/manifest.json \
  --protocol provenance/PORTABILITY_PROTOCOL_FROZEN.md \
  --midpoint-site-ids provenance/midpoint_selection.json \
  --output-dir new_ph_replay --phase native --workers 6
.venv/bin/python analysis_source/portability/scripts/phased_engine.py \
  --manifest /path/to/original/manifest.json \
  --protocol provenance/PORTABILITY_PROTOCOL_FROZEN.md \
  --midpoint-site-ids provenance/midpoint_selection.json \
  --output-dir new_ph_replay --phase centered --workers 6
```

The paths above are deliberate user-supplied placeholders, not machine-specific executable assumptions. A rerun regenerates locks with its own source/input provenance; the retained historical locks are not substituted for that rerun.

## Re-acquisition, if needed

Re-acquisition is optional and is not needed to replay stored data. It requires authorized AlphaGenome API access, client version 0.9.0 and the recorded acquisition environment (`acquisition_environment.lock`). The latter is an installed-package snapshot, not a hash-pinned cross-platform resolver lock. Keep acquisition separate from the PH analysis environment.

```sh
python prepare_acquisition_replay.py --output new_acquisition
ANCHOR_ACQUISITION_DIR="$PWD/new_acquisition" \
  python new_acquisition/scripts/acquire_portability.py --check-only
```

The second command requires the acquisition environment but makes no requests. The environment must separately provide `ALPHAGENOME_API_KEY` and `ANCHOR_LEGACY_DIR` (the historical GM12878 replication directory) before actual acquisition without `--check-only`. Do not print a key, embed it in scripts, or put it in shell history. `prepare_acquisition_replay.py` refuses an existing destination, preserves the historical freeze and labels the new run as replay. Server output equality is an empirical control, not identification of immutable model weights.

## Required data for complete public replay

For the new experiment, a release must add, with applicable terms and stable access:

- IMR-90 `manifest.json`, all 84 `sites/site_NNN.npz` map arrays and companion metadata;
- paired-call metadata/arrays sufficient to verify all 252 channel selections, repeated REF equality and request provenance, plus contemporaneous GM12878 control arrays and historical 84-site comparators;
- full 84 native diagrams, saved centered validations, native-prediction lock and the files it hashes, or a complete map replay that regenerates them;
- frozen cohort/protocols, complete acquisition logs with credential/error sanitization, analysis versions and all scripts needed for summary and exploratory paths;
- the older discovery, replication and Atlas component datasets/code already enumerated in the previous full-validation capsule, because the integrated article makes claims about all those components.

Raw maps and diagrams remain private in the research workspace. `FULL_DATA_INVENTORY.json` records the exact relative files/hashes/sizes needed for the new experiment without copying them. The full earlier capsule has 750 versioned files and is separate. API re-acquisition alone cannot guarantee the exact historical arrays if the service changes.

## Licensing and release status

The existing public Anchor Audit Toolkit is MIT licensed: https://github.com/patrickiben/contact-map-anchor-audit (release version 0.1.0 at commit `f59d0a64afd0923bc8357da0fb41a55923301093`; subsequent main commit `7a5b929dd2577002531b098a3bbd99555d424731`). That software license does not relicense provider outputs or derived study data. This private bundle is not being assigned a blanket license over third-party material.

The provider's retained December 2025 model-parameters terms permit sharing subject to conditions and separate output terms; this does not establish that API output sharing is prohibited, nor does it settle the currently applicable API terms. The official current API README states noncommercial/output-use restrictions except for expressly designated permissive artifacts. The full current output terms were not accessible in this audit. Confirm the applicable terms and notices for maps **and substantial derivatives**, then deposit the reproducibility material or document a justified access restriction compatible with the journal. Do not label this private preparation as an existing public archive or attach an invented DOI.

Public study-guide/companion editions remain tied to the pre-portability manuscript. Source-bound portability teaching material is a separate proposed addition; no human learner validation has been completed.
