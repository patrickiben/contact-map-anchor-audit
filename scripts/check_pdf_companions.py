#!/usr/bin/env python3
"""Check the frozen PDF editions and coverage manifest with only the standard library.

Optionally verify the main manuscript and all six additional files with --source-root DIR.
PDF byte/hash checks do not replace rendering or human learner evaluation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check(source_root=None):
    manifest = json.loads((ROOT/'education/ARTIFACTS.json').read_text())
    assert len(manifest['sources'])==7, 'Expected main manuscript plus six additional files'
    assert {x['id'] for x in manifest['sources']}=={'MAIN','AF1','AF2','AF3','AF4','AF5','AF6'}
    for item in manifest['assets']:
        content = (ROOT/item['path']).read_bytes()
        assert digest(content) == item['sha256'], 'Asset drift: '+item['path']
        assert len(content) == item['bytes'], 'Byte count changed: '+item['path']
    receipt = json.loads((ROOT/'education/pdf_build_metadata.json').read_text())
    for edition in receipt['editions']:
        for kind in ('markdown','pdf'):
            item=edition[kind]
            assert digest((ROOT/item['path']).read_bytes())==item['sha256']
        content=(ROOT/edition['pdf']['path']).read_bytes()
        assert content.startswith(b'%PDF-') and b'%%EOF' in content[-1024:]
        assert len(re.findall(rb'/Type\s*/Page\b',content))==edition['pages']
    companion=(ROOT/'education/COMPANION.md').read_text()
    units=set(re.findall(r'^#{2,3} ((?:P|R|S|W|T)\d{2})(?:[ .·])',companion,re.M))
    expected={f'{prefix}{i:02d}' for prefix,n in [('P',10),('R',10),('S',7),('W',6),('T',12)] for i in range(1,n+1)}
    assert units==expected, 'Teaching unit inventory changed'
    for name in ('STUDY_GUIDE','COMPANION'):
        content=(ROOT/'education'/f'{name}.md').read_text()
        for token in ('42','249','252','35','0.517857','v0.2.0'):
            assert token in content, (name,'Missing current-edition claim',token)
    coverage=(ROOT/'education/COMPLETE_COVERAGE.md').read_text()
    for row in manifest['coverage']:
        assert set(row['units'])<=units|{'INTRO'}, row['id']
        assert row['id'] in coverage, 'Missing visible coverage row: '+row['id']
    if source_root:
        source_root=Path(source_root)
        for source in manifest['sources']:
            content=(source_root/source['file']).read_bytes()
            assert digest(content)==source['sha256'], 'Source changed: '+source['file']
            lines=content.decode().splitlines()
            assert len(lines)==source['lines']
            covered=set()
            for row in manifest['coverage']:
                if row['source']!=source['id']: continue
                a,b=row['lines'];covered.update(range(a,b+1))
                assert digest('\n'.join(lines[a-1:b]).encode())==row['excerpt_sha256'],row['id']
            missing=[i for i,line in enumerate(lines,1) if line.strip() and i not in covered]
            assert not missing, (source['id'],missing)
    return {'status':'PASS_MECHANICAL_CHECKS','editions':{x['name']:x['pages'] for x in receipt['editions']},'teaching_units':len(units),'coverage_rows':len(manifest['coverage']),'source_files_checked':bool(source_root),'human_learner_validation':'NOT_PERFORMED','limits':'Hashes, PDF structure signatures and source coverage do not certify educational efficacy, biological validity or a formal mathematical proof.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path)
    args=parser.parse_args()
    print(json.dumps(check(args.source_root),indent=2))


if __name__=='__main__': main()
