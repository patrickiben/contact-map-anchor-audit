#!/usr/bin/env python3
"""Generate and check the educational adaptation without inventing human verdicts."""
from __future__ import annotations
import argparse, collections, copy, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE = '05b28b1bcc1b3a715152beb5e07567afc628632851dba5d54e5301ea69483b5d'
EXPECTED_IDS = {'OBJECT','STABILITY','ANCHOR','RANKING','CONSEQUENCE','NULL','DISCOVERY','REPLICATION','PRECISION','SCOPE'}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load(path: str):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def rendered_documents(learning):
    lines = ['# Understand the Anchor Audit', '', 'A guided route from diagram translation to a defensible ranking interpretation. Start with the browser presets, then use the worked examples and research workflow.', '', '**Status:** educational adaptation prepared; human learner validation and author approval are not certified. The interactive questions are practice, not the original locked human transfer assessment.', '']
    for lesson in learning['lessons']:
        lines += [f"## {lesson['title']}", '', lesson['summary'], '']
        for paragraph in lesson['body']: lines += [paragraph, '']
        lines += [f"**Try it:** {lesson['try_it']}", '', f"**Boundary:** {lesson['boundary']}", '', f"Source: current BMC manuscript lines {lesson['source_lines'][0]}–{lesson['source_lines'][1]}; see [source map](SOURCE_MAP.json).", '']
    lines += ['## Glossary', '']
    for item in learning['glossary']: lines += [f"- **{item['term']}:** {item['definition']}"]
    lines += ['', '## Keep these distinctions', ''] + ['- '+x for x in learning['nonclaims']]
    guide='\n'.join(lines)+'\n'
    quiz=['# Practice questions and explained answers', '', learning['assessment_scope'], '', 'Try each question before reading its answer. Correct feedback explains the distinction; a score is not evidence of educational effectiveness. Retrying is encouraged.', '']
    for q in learning['quiz']:
        quiz += [f"## {q['id']} · {q['kind'].title()}", '', q['prompt'], '']
        quiz += [f"{i+1}. {c}" for i,c in enumerate(q['choices'])]
        quiz += ['', f"**Answer: {q['answer_index']+1}.** {q['explanation']}", '']
    return {'education/GUIDE.md':guide,'education/PRACTICE.md':'\n'.join(quiz).rstrip()+'\n'}

def validate(learning, study, mapping, source_path=None, research_root=None):
    assert learning['source']['sha256'] == study['source_sha256'] == mapping['source']['sha256'] == EXPECTED_SOURCE
    assert len(learning['lessons']) == 10
    combined=' '.join(' '.join(x['body']) for x in learning['lessons'])
    for fact in ('42 additional decisions','35 unresolved','249 of 252','Both simple and strengthened bounds','same 84','same AlphaGenome architecture','0.517857','before centered matching','full validated-arithmetic enclosure'):
        assert fact in combined, 'Missing portability teaching boundary: '+fact
    assert {c['id'] for c in study['cohorts']} == {'discovery','replication','imr90'}
    ids={x['id'] for x in learning['lessons']};assert ids==EXPECTED_IDS
    assert len(learning['quiz'])==12
    assert collections.Counter(q['kind'] for q in learning['quiz'])=={'CORE':4,'BOUNDARY':4,'TRANSFER':4}
    for q in learning['quiz']:
        assert 0<=q['answer_index']<len(q['choices']) and len(set(q['choices']))==len(q['choices'])
        assert set(q['coverage_ids'])<=ids and q['coverage_ids'] and q['explanation']
    assert len({q['id'] for q in learning['quiz']})==12
    assert {x['id'] for x in mapping['lessons']}==ids
    for l in learning['lessons']:
        assert l['body'] and l['try_it'] and l['boundary'] and l['summary']
        mapped=next(x for x in mapping['lessons'] if x['id']==l['id'])
        assert mapped['source_lines']==l['source_lines']
    assert all(v is None for v in mapping['human_reviews'].values())
    for c in study['cohorts']:
        assert c['sites']==c['native_ties']+c['strict_leaders']
        assert c['native_ties']-c['resolved_ties']==c['centered_ties']
        assert c['strict_leaders']==c['preserved_strict_leaders']
        assert c['simple_bound_leaders']<=c['preserved_strict_leaders']
        assert c['witness_leaders']-c['simple_bound_leaders']==c['additional_witness_leaders']
        assert c['comparisons']==3*c['sites']
        assert 0<=c['native_credit']<=1 and 0<=c['centered_credit']<=1
    value_map=load('education/STUDY_VALUE_MAP.json')
    for row in value_map['checks']:
        cohort=next(c for c in study['cohorts'] if c['id']==row['cohort'])
        assert abs(cohort[row['field']]-row['value'])<1e-14
    if source_path:
        content=Path(source_path).read_bytes();assert digest(content)==EXPECTED_SOURCE,'Source manuscript changed'
        source_lines=content.decode().splitlines()
        for l in mapping['lessons']:
            a,b=l['source_lines'];assert digest('\n'.join(source_lines[a-1:b]).encode())==l['source_excerpt_sha256']
        covered={i for l in mapping['lessons'] for i in range(l['source_lines'][0],l['source_lines'][1]+1)}
        for l in mapping['structural_exclusions']+mapping['introductory_synthesis']:
            covered.update(range(l['source_lines'][0],l['source_lines'][1]+1))
        assert all(i in covered for i,s in enumerate(source_lines,1) if s.strip())
    if research_root:
        for name,meta in value_map['sources'].items():
            assert digest((Path(research_root)/name).read_bytes())==meta['sha256'], name
        sources={p:json.loads((Path(research_root)/p).read_text()) for p in value_map['sources']}
        for row in value_map['checks']:
            obj=sources[row['source']]
            for key in row['keys']:obj=obj[key]
            if row['operation']=='length':obj=len(obj)
            elif row['operation']=='subtract':obj=obj-row['subtract']
            assert abs(obj-row['value'])<1e-14, row
    return {'status':'PASS_MECHANICAL_SCOPE_ONLY','lessons':10,'quiz_items':12,'quiz_kinds':dict(collections.Counter(q['kind'] for q in learning['quiz'])),'source_file_checked':bool(source_path),'research_sources_checked':bool(research_root),'aggregate_value_checks':len(value_map['checks']),'human_learner_validation':'NOT_PERFORMED','author_approval':'NOT_CERTIFIED','scope':'Source/coverage/value/hash checks; no educational efficacy or formal theorem certification.'}


def mutation_controls(learning, study, mapping):
    controls = [
        ('missing_lesson', lambda a,b,c: a['lessons'].pop()),
        ('duplicate_quiz_id', lambda a,b,c: a['quiz'][0].update(id=a['quiz'][1]['id'])),
        ('bad_answer_index', lambda a,b,c: a['quiz'][0].update(answer_index=99)),
        ('wrong_study_credit', lambda a,b,c: b['cohorts'][0].update(native_credit=.9)),
        ('invented_human_approval', lambda a,b,c: c['human_reviews'].update(author_approval='invented')),
        ('removed_portability_boundary', lambda a,b,c: next(x for x in a['lessons'] if x['id']=='DISCOVERY')['body'].pop()),
        ('changed_source_binding', lambda a,b,c: a['source'].update(sha256='0'*64)),
    ]
    result = []
    for name, mutate in controls:
        a,b,c = copy.deepcopy(learning), copy.deepcopy(study), copy.deepcopy(mapping)
        mutate(a,b,c)
        try:
            validate(a,b,c)
        except AssertionError:
            result.append({'name': name, 'detected': True})
        else:
            raise RuntimeError('Missed mutation: ' + name)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--self-test',action='store_true');ap.add_argument('--source',type=Path);ap.add_argument('--research-root',type=Path);args=ap.parse_args()
    learning=load('docs/learning.json');study=load('docs/study-summary.json');mapping=load('education/SOURCE_MAP.json')
    result=validate(learning,study,mapping,args.source,args.research_root)
    if args.self_test: result['mutation_controls']=mutation_controls(learning,study,mapping)
    docs=rendered_documents(learning)
    if args.check:
        for rel,content in docs.items():assert (ROOT/rel).read_text()==content,'Generated content drift: '+rel
        for rel,meta in mapping['assets'].items():assert digest((ROOT/rel).read_bytes())==meta['sha256'],'Asset drift: '+rel
    else:
        for rel,content in docs.items():(ROOT/rel).write_text(content,encoding='utf-8')
        paths=['docs/learning.json','docs/study-summary.json','docs/provenance.json','education/GUIDE.md','education/PRACTICE.md','education/WORKED_EXAMPLES.md','education/RESEARCHER_WORKFLOW.md','education/README.md','education/STUDY_VALUE_MAP.json','scripts/build_education.py']
        mapping['assets']={rel:{'sha256':digest((ROOT/rel).read_bytes()),'bytes':(ROOT/rel).stat().st_size} for rel in paths}
        (ROOT/'education/SOURCE_MAP.json').write_text(json.dumps(mapping,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
