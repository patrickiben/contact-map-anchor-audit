#!/usr/bin/env python3
"""Check public artifact bindings and independently derived IMR-90 results."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
research=root/'research'
manifest=json.loads((research/'ARTIFACTS.json').read_text())
for entry in manifest['files']:
    path=research/entry['path']
    assert path.is_file(),entry['path']
    assert path.stat().st_size==entry['bytes'],entry['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],entry['path']
digest=hashlib.sha256((research/'manuscript.md').read_bytes()).hexdigest()
assert digest==manifest['manuscript_source_sha256']
assert digest==json.loads((root/'docs/provenance.json').read_text())['source']['sha256']
study=json.loads((root/'docs/study-summary.json').read_text())
assert digest==study['source_sha256']
with tempfile.TemporaryDirectory(prefix='anchor-public-check-') as tmp:
    out=Path(tmp)/'derived.json'
    subprocess.run([sys.executable,str(research/'reproduce/verify_derived_results.py'),'--output',str(out)],check=True)
    results=json.loads(out.read_text())['by_tolerance']['1e-06']
    row=next(c for c in study['cohorts'] if c['id']=='imr90')
    assert row['simple_bound_leaders']==results['simple_unique_leaders']
    assert row['witness_leaders']==results['strengthened_unique_leaders']
    assert row['additional_witness_leaders']==results['additional_leader_sites']
    assert row['sites']-row['witness_leaders']==row['unresolved_sites']
print(json.dumps({'status':'PASS_PUBLIC_BINDINGS_AND_DERIVED_RESULTS','files':len(manifest['files']),'source_sha256':digest}))
