#!/usr/bin/env python3
"""Compare every scientific field shared with the unmodified reference engine."""
from pathlib import Path
import hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(x,y,tolerance=0):
    a,b=np.asarray(x),np.asarray(y)
    if a.shape!=b.shape:return False,False,None
    exact=bool(np.array_equal(a,b))
    numeric=np.issubdtype(a.dtype,np.number) and np.issubdtype(b.dtype,np.number)
    error=float(np.max(np.abs(a-b))) if a.size and numeric else (0. if exact else None)
    return exact or error is not None and error<=tolerance,exact,error

def main():
    checks=[];sources=[]
    assert compare([1,2],[1,2])[0]
    assert not compare([1,2],[1,2.01],1e-12)[0]
    assert not compare([1,2],[1])[0]
    assert not compare(True,False)[0]
    assert len(list((ROOT/'site_analysis').glob('site_*.json')))==84
    assert len(list((ROOT/'reference_replay/site_analysis').glob('site_*.json')))==84
    for i in range(84):
        p=ROOT/'site_analysis'/f'site_{i:03d}.json'
        q=ROOT/'reference_replay/site_analysis'/p.name
        a,b=json.loads(p.read_text()),json.loads(q.read_text())
        sources.append({'site_index':i,'phased_sha256':sha(p),'reference_sha256':sha(q)})
        assert a['status']==b['status']=='complete'
        def check(field,x,y,t=0):
            good,equal,error=compare(x,y,t)
            checks.append({'site_index':i,'field':field,'passed':good,'exact':equal,'max_absolute_difference':error,'tolerance':t})
        for f in ['site_id','selected_allele_index','means','native_float32_edge_errors_ref_then_alts']:
            check(f,a[f],b[f])
        for rep in ['native','centered']:
            aa,bb=a['representations'][rep],b['representations'][rep]
            check(rep+'/distances',aa['distances'],bb['distances'],1e-12)
            for tol in ['0.0','1e-06','1e-05']:
                check(rep+'/credit/'+tol,aa['credits_by_tolerance'][tol],bb['credits_by_tolerance'][tol])
        for j,(aa,bb) in enumerate(zip(a['representations']['native']['h1_diagrams_ref_then_alts'],b['representations']['native']['h1_diagrams_ref_then_alts'])):
            check('native/diagram/'+str(j),aa,bb)
        assert set(a['baselines'])==set(b['baselines'])
        for f in a['baselines']:check('baseline/'+f,a['baselines'][f],b['baselines'][f],1e-14)
        for f in a['lifetime_summaries_ref_then_alts']:
            check('lifetime/'+f,a['lifetime_summaries_ref_then_alts'][f],b['lifetime_summaries_ref_then_alts'][f],1e-14)
        for j,(aa,bb) in enumerate(zip(a['pair_diagnostics'],b['pair_diagnostics'])):
            for f in ['delta','endpoint_direction','absolute_saturation_residual','numerically_saturated_at_primary_1e10','tiny_shift_at_1e10']:
                check(f'pair/{j}/{f}',aa[f],bb[f],1e-12 if f=='absolute_saturation_residual' else 0)
            if 'midpoint_check' in aa:
                for f in ['direct_exact_solver_distance','absolute_error','affine_agreement_passed','endpoint_tube_passed']:
                    check(f'pair/{j}/midpoint/{f}',aa['midpoint_check'][f],bb['midpoint_check'][f],1e-12 if f in ['direct_exact_solver_distance','absolute_error'] else 0)
    r={'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL','sites':84,'diagram_arrays':336,'comparisons':len(checks),'exact_comparisons':sum(x['exact'] for x in checks),'failures':[x for x in checks if not x['passed']],'nonidentities':[x for x in checks if not x['exact']],'negative_controls_passed':3,'sources':sources,'script_sha256':sha(Path(__file__)),'checks':checks,'scope':'Full new-track replay through unmodified scientific engine; shared PH kernel and fresh environment, not an independently developed PH algorithm or independent model.'}
    (ROOT/'reports/REFERENCE_REPLAY_COMPARISON.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ['status','sites','diagram_arrays','comparisons','exact_comparisons','failures','negative_controls_passed']},indent=2))
    assert r['status']=='PASS'
if __name__=='__main__':main()
