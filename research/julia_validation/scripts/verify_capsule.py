"""Verify every listed file in an extracted targeted-validation capsule."""
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
manifest = json.loads((base / "CAPSULE_MANIFEST.json").read_text())
failures = []
for record in manifest["files"]:
    relative = Path(record["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Invalid manifest path")
    path = base / relative
    if not path.is_file():
        failures.append({"path": str(relative), "error": "missing"})
        continue
    raw = path.read_bytes()
    if len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        failures.append({"path": str(relative), "error": "size/hash mismatch"})
print(json.dumps({"status": "PASS" if not failures else "FAIL", "files_checked": len(manifest["files"]), "failures": failures}, indent=2))
raise SystemExit(bool(failures))
