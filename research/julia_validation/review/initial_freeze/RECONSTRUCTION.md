# Initial-freeze reconstruction and later source changes

Reconstructed without changing the current script or manifest. Exact SHA-256 agreement with EXECUTION_FREEZE.json verifies the archived initial bytes.

## Preserved initial files

- control_oracle.py: `c0dbb4368da4f4f208dec5e5af54f13f5a179cf44c6ede4662d8c3a804462bb2`
- control_manifest.json: `65139a72b4679e87bc455f746404c2b6b83d7a6edd2e50ce98c9016f9ff37c58`

## Complete post-freeze differences

1. Module docstring corrected from “Uses NumPy for byte conversion only; no persistent-homology library is imported.” to “Uses NumPy for input construction and byte conversion; no PH library is imported.” The original description understated NumPy's input-construction role.
2. Three comparator assertions added for receipt key, matrix dimension n, and raw input SHA-256. These strengthen receipt provenance; they do not change inputs, oracle calculations, interval expectations, effective input hashes, offsets, endpoint comparison, or mutations.
3. Re-running the exporter updated control_manifest.json's script_sha256 field to identify the changed source. Restoring that single field reconstructs the entire original manifest byte-for-byte. The raw-only runner manifest and all binary control inputs are unchanged.

The control_runner_manifest exporter was already present in the initially frozen source. It was not a post-freeze change. The exact unified source diff is preserved as control_oracle_changes.diff. The current source remains in place; no initial evidence has replaced current evidence.

Current script SHA-256: `8dfe551ac3d107083eed84a596e18a084ab0d4e2cb31f649e4f9c78a96b41994`.
Current expected-manifest SHA-256: `8408619cb369bba3c1db3dd9f33e539ccff824d41c2e3ff0a13472f9b792f349`.
