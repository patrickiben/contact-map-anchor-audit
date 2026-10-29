# Targeted Julia persistence-check replay

This capsule validates a fixed subset of previously generated contact maps: nine sites across seven genes, both GM12878 and IMR90 tracks, and REF plus all three ALTs. It contains 72 full persistence-diagram targets and 54 REF/ALT comparisons. The three previously known IMR90 nonsaturation exceptions are included deliberately. This is a targeted implementation check, not a new cohort, an independent prediction model or a formal proof.

The included `study_inputs/` directory contains exact copies of 18 original NPZ files, their 18 original site-analysis JSON files and two GM12878 witness/ranking reference files. `BUNDLED_INPUT_MANIFEST.json` records their hashes. Historical absolute paths inside original provenance are retained unchanged; the replay exports new manifests using the selected runtime study root. Those historical paths are not runtime dependencies. No original analysis code or prediction service is called.

## Requirements

The original check used Python **3.14.7**, NumPy **2.5.3**, SciPy **1.18.1** and GUDHI **3.13.0**. The Python package pins are in `environment/requirements-python.txt`. The Julia dependency versions and Julia version used to resolve them are recorded in `environment/Manifest.toml`. Install Julia and ensure the executable is on `PATH`, or provide `--julia /path/to/julia`.

From the capsule directory, prepare a Python environment:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r environment/requirements-python.txt
```

Do not use `python -O`: the frozen comparison scripts use assertions as validation gates. Dependency installation and Julia `Pkg.instantiate()` may require network access unless the pinned packages are already cached. The scientific replay uses the included original maps and requires no AlphaGenome credentials, new predictions or original filesystem paths.

## Prepare only

Choose a new destination that does not exist:

```sh
.venv/bin/python scripts/replay.py --output /tmp/anchor-julia-preparation
```

The driver refuses an existing destination. It copies the fixed scripts, Julia environment, protocol, cohort inventory and selected original study inputs, verifies hashes, and exports 22 small controls and 72 raw genomic inputs. It also runs the small explicit GF2 control oracle and its hand-answer/mutation checks. It does **not** invoke Julia, calculate genomic persistent homology, or claim new persistence validation. `REPLAY_STATUS.json` ends with `PREPARED_NOT_EXECUTED` and `genomic_persistence_executed: false`.

Preparation is an inspection mode, not a resumable half-run. For a complete replay choose another new destination and use `--execute`.

## Full replay

```sh
.venv/bin/python scripts/replay.py \
  --output /tmp/anchor-julia-full-replay \
  --execute --workers 4
```

The `--execute` flag is required for Julia calculations. The driver instantiates the pinned Julia environment, runs and compares all 22 controls, then executes the 72 genomic diagrams in four independent Julia shards. Only after all 72 primary comparisons pass does it invoke the downstream driver with `--primary-success-confirmed`. The downstream check recomputes 108 native/centered bottleneck distances, all top sets and fractional credits at three tolerances, the shifted Hausdorff witnesses, score/ranking bounds and nonsaturation flags.

Use `--genomic-shards 1` to run Julia serially; `--workers` also controls downstream parallelism. Use `--study-root /path/to/original-study-root` to source the same selected files from the original study directory layout. Every required file must match the bundled hashes, and the driver copies those selected inputs into the new workspace before execution.

## Results and limits

Inspect `REPLAY_STATUS.json` and the per-stage receipts/logs in `logs/`. The actual gate artifacts are:

- `review/CONTROL_ORACLE_SELF_CHECK.json`: 22 explicit small-graph controls and mutation checks.
- `review/CONTROL_JULIA_COMPARISON_controls.json`: Julia correspondence for all 22 controls.
- `outputs/PRIMARY_COMPARISON.json`: exact complete interval-multiset comparisons for all 72 diagrams.
- `outputs/downstream/summary.json` and `outputs/downstream/sites/`: downstream propagation and any discrepancies.

A successful full replay ends with `PASS`. A failed stage preserves its evidence and stops subsequent stages. Preparation alone must never be described as a passed replay. Existing original-run outputs are not copied into the fresh workspace and are never modified.

Primary comparison requires exact effective Float32 filtration inputs and exact sorted Float64 interval multisets after removing the declared offset; positive intervals retain multiplicity. Downstream numeric comparisons use the frozen practical allowance of 1e-12, top tolerances 0/1e-6/1e-5, and saturation thresholds 1e-10 with 1e-12 sensitivity. These are numerical comparisons rather than certified real-arithmetic error bounds.

Ripserer is a separate Julia implementation in the same Ripser algorithm family. Downstream bottleneck matching uses the original GUDHI/Hera solver with `delta=0`, so this is not a second independent bottleneck implementation. The brute-force shifted Hausdorff implementation differs from the original tree-based witness calculation, but it remains a lower bound rather than a bijective matching algorithm. The check does not certify every site, universal mathematical statements, biological validity or clinical superiority. See `PROTOCOL.md` for the frozen scientific scope.
