# Independent Julia runner and small-control review

28 October 2026. Static source review and Python explicit-reduction self-check; this reviewer did not execute Julia.

## Result

No blocking discrepancy identified between the frozen protocol and `scripts/run_persistence.jl`. The runner independently reads raw Float64 L, checks input SHA-256/symmetry/finite values, computes the off-diagonal offset, creates dense Float32 shifted weights with diagonal zero, hashes the exact effective bytes, runs full H1 over F2, widens endpoints before restoring the original Float64 offset, preserves multiplicities, and writes sorted Float64 intervals in column-major order. It does not read saved Python diagrams or oracle endpoints. The raw-only control manifest has four fields per record: key, n, raw_path, raw_sha256.

Installed Ripserer 0.17.0 source was checked, in addition to the primary documentation linked in FILTRATION_REVIEW.md. Its matrix constructor does not impose a triangle inequality; diagonal entries are vertex births; positive off-diagonal entries represent edges; each simplex enters at the maximum edge birth. The explicit infinite threshold and cutoff zero match the protocol. The source retains intervals iff death_time - birth_time > cutoff. The pinned Manifest records Ripserer git-tree SHA-1 96b0e3fead28f7f627f51608cf977080b0e4e967.

## Independent controls

`control_oracle.py` uses explicit GF2 boundary-column reduction of every vertex, edge and triangle, in ascending (birth, dimension, vertex tuple) order. Columns are standard-library integer bitsets reduced with XOR. The oracle is algorithmically distinct from Ripserer cohomology and uses no PH package. NumPy constructs deterministic small inputs and serializes the agreed floating-point values. All cycle births are checked to pair; zero-length bars are excluded only after reduction.

Export and self-check completed successfully: ten named hand-derived expectations agree with explicit reduction; twelve seeded random complete graphs add negative/zero/tied births; all 22 legitimate fixtures are accepted by the comparator. Four injected mutations are rejected: a missing duplicate, a changed endpoint, an unremoved offset, and a corrupted effective-input hash. Full expected manifest is `inputs/control_manifest.json`; the runner sees only `inputs/control_runner_manifest.json`. Self-check receipt is `review/CONTROL_ORACLE_SELF_CHECK.json`.

The executable comparator is `python scripts/control_oracle.py --compare-mode controls`. It verifies each output-file hash, receipt identity/raw hash, exact complete endpoint multiset, effective-input hash, offset and interval count. It writes `review/CONTROL_JULIA_COMPARISON_controls.json` only on successful comparison. Main execution and any failures remain the coordinating agent's responsibility. This static review and the oracle self-check do not themselves establish genomic replication.

## Reviewed hashes

- `/Users/patrickiben/Documents/contact3d_rework_2026-10-28/julia_persistence_check_2026-10-28/scripts/run_persistence.jl`: `6f7146fae2b7803ec0f922782e62a6a180e7386589b99f8c119337e00870a537`
- `/Users/patrickiben/Documents/contact3d_rework_2026-10-28/julia_persistence_check_2026-10-28/scripts/control_oracle.py`: `8dfe551ac3d107083eed84a596e18a084ab0d4e2cb31f649e4f9c78a96b41994`
- `/Users/patrickiben/Documents/contact3d_rework_2026-10-28/julia_persistence_check_2026-10-28/PROTOCOL.md`: `224dd1162cb36e1fde53c88e09ec66ffb17960d092d21a7b9c7a1fafce580f5d`
- `/Users/patrickiben/Documents/contact3d_rework_2026-10-28/julia_persistence_check_2026-10-28/environment/Manifest.toml`: `d95d1206c0500fafd74a1965fe87eaa9f8d6633d93f68b1533e258f264dc6b5e`
- `/Users/patrickiben/.julia/packages/Ripserer/SoXCe/src/filtrations/rips.jl`: `ede8e97b661c444e07adf7e7417f8f343277235597f327dc4adea3f81206cdf0`
- `/Users/patrickiben/.julia/packages/Ripserer/SoXCe/src/computation/cohomology.jl`: `9afb3c15b23e3fc02e4133b466b5dd3b69eb51ab5073afee6fcc7db813699d53`
