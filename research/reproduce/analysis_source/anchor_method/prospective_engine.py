#!/usr/bin/env python3
"""Label-blind native/centered full-PH replication engine with frozen midpoint checks."""
from pathlib import Path
import argparse,hashlib,importlib.metadata,json,sys,time,traceback
from concurrent.futures import ProcessPoolExecutor
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'scripts'))
sys.path.insert(0,str(HERE.parent/'astra_genomic/vendor'))
import analyze_spatial_maps as core
import gudhi
from gudhi import hera

def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');tmp.replace(path)

def edge_error(matrix):
    w=-matrix[np.triu_indices(len(matrix),1)];offset=max(0.,1.-float(w.min()))
    return float(np.max(np.abs((w+offset).astype(np.float32).astype(float)-offset-w)))

def distance(a,b):
    return 0. if np.array_equal(a,b) else float(hera.bottleneck_distance(a,b,delta=0.))

def _process(task):
    site,manifest_dir,output,key_common,midpoint=task;started=time.monotonic();index=site['site_index']
    cache=Path(output)/'site_analysis'/f'site_{index:03d}.json'
    npz=Path(site['npz_path']);npz=npz if npz.is_absolute() else Path(manifest_dir)/npz
    metadata=Path(site['metadata_path']);metadata=metadata if metadata.is_absolute() else Path(manifest_dir)/metadata
    deadline=time.monotonic()+3600
    while not (npz.exists() and metadata.exists()):
        if time.monotonic()>deadline:raise TimeoutError(f'Input readiness timeout for {site["site_id"]}')
        time.sleep(1)
    meta=json.loads(metadata.read_text());npz_digest=core.sha256(npz)
    if meta['npz_sha256']!=npz_digest or meta['site_id']!=site['site_id']:raise ValueError('Acquired input metadata/hash mismatch')
    key={**key_common,'site_metadata_sha256':hashlib.sha256(json.dumps(site,sort_keys=True).encode()).hexdigest(),
        'npz_sha256':npz_digest,'acquisition_metadata_sha256':core.sha256(metadata),'midpoint_validation':midpoint}
    if cache.exists():
        prior=json.loads(cache.read_text())
        if prior.get('cache_key')==key:return prior
    print('Starting',index,site['site_id'],flush=True)
    try:
        ref,alt,provenance=core.load_site(site,Path(manifest_dir));maps=[ref,*alt];upper=np.triu_indices(len(ref),1)
        means=[float(x[upper].mean()) for x in maps];diagrams=[core.h1(-x) for x in maps];errors=[edge_error(x) for x in maps]
        centered=[d+m for d,m in zip(diagrams,means)];bs=[];cs=[];checks=[]
        print('PH complete',index,'intervals',[len(d) for d in diagrams],flush=True)
        for i in range(3):
            before=time.monotonic();b=distance(diagrams[0],diagrams[i+1]);c=distance(centered[0],centered[i+1]);bs.append(b);cs.append(c)
            delta=means[i+1]-means[0];T=abs(delta);change=c-b;direction=1 if change>=0 else -1
            row={'alternate_index':i,'delta':delta,'native_distance':b,'centered_distance':c,
                'signed_saturation_deficit':T-direction*change,'absolute_saturation_residual':abs(T-abs(change)),
                'numerically_saturated_at_1e12':abs(T-abs(change))<=1e-12,
                'numerically_saturated_at_primary_1e10':abs(T-abs(change))<=1e-10,
                'tiny_shift_at_1e10':T<=1e-10,
                'endpoint_direction':direction,'endpoint_error_allowance':1e-12,
                'endpoint_allowance_status':'Practical numerical allowance; not a proved error bound for solver floating-point arithmetic.',
                'conservative_deficit_upper_bound':max(0.,T-direction*change+2e-12),
                'per_distance_ph_input_rounding_bound':errors[0]+errors[i+1]}
            if midpoint:
                actual=distance(diagrams[0],diagrams[i+1]+.5*delta);predicted=.5*(b+c)
                lo=max(b-.5*T,c-.5*T)-1e-12;hi=min(b+.5*T,c+.5*T)+1e-12
                tolerance=max(1e-10,1e-10*max(abs(actual),abs(predicted)))
                row['midpoint_check']={'lambda':.5,'direct_exact_solver_distance':actual,'affine_interpolation':predicted,
                    'absolute_error':abs(actual-predicted),'tolerance':tolerance,
                    'affine_agreement_passed':abs(actual-predicted)<=tolerance,'lipschitz_endpoint_tube':[lo,hi],
                    'endpoint_tube_passed':lo<=actual<=hi}
            checks.append(row);print('Pair complete',index,i,f'{time.monotonic()-before:.2f}s',flush=True)
        result={'status':'complete','site_id':site['site_id'],'site_index':index,'gene':site.get('gene',site.get('original_variant',{}).get('gene')),
            'means':means,'provenance':provenance,'cache_key':key,'pair_diagnostics':checks,
            'native_float32_edge_errors_ref_then_alts':errors,'representations':{},
            'bottleneck_solver':{'name':'gudhi.hera.bottleneck_distance','delta':0,'version':gudhi.__version__},
            'selected_labels_used':False,'elapsed_seconds':time.monotonic()-started}
        diffs=alt[:,upper[0],upper[1]]-ref[upper]
        lifetimes=[d[:,1]-d[:,0] for d in diagrams]
        counts=[len(d) for d in diagrams];totals=[float(v.sum()) for v in lifetimes];maxima=[float(v.max()) if len(v) else 0. for v in lifetimes]
        result['lifetime_summaries_ref_then_alts']={'count':counts,'total':totals,'maximum':maxima}
        result['baselines']={'absolute_mean_change':np.abs(np.array(means[1:])-means[0]).tolist(),
            'native_rms':np.sqrt(np.mean(diffs**2,axis=1)).tolist(),'centered_rms':np.sqrt(np.mean((diffs-diffs.mean(axis=1,keepdims=True))**2,axis=1)).tolist(),
            'max_absolute':np.max(np.abs(diffs),axis=1).tolist(),
            'lifetime_count_absolute_change':np.abs(np.array(counts[1:])-counts[0]).tolist(),
            'total_persistence_absolute_change':np.abs(np.array(totals[1:])-totals[0]).tolist(),
            'maximum_persistence_absolute_change':np.abs(np.array(maxima[1:])-maxima[0]).tolist(),
            'native_plus_absolute_mean_change':(np.array(bs)+np.abs(np.array(means[1:])-means[0])).tolist(),
            'native_minus_absolute_mean_change':(np.array(bs)-np.abs(np.array(means[1:])-means[0])).tolist()}
        result['selected_allele_index']=site.get('selected_allele_index')
        result['selected_label_note']='Retained for protocol-declared descriptive reporting only; not used to set parameters, select branches or choose examples.'
        for rep,scores in [('native',bs),('centered',cs)]:
            result['representations'][rep]={'distances':scores,'credits_by_tolerance':{str(t):core.fractional_top(np.array(scores),t).tolist() for t in (0.,1e-6,1e-5)}}
        result['representations']['native']['h1_diagrams_ref_then_alts']=[d.tolist() for d in diagrams]
        dump(cache,result);print('Completed site',index,flush=True);return result
    except Exception as error:
        failure={'status':'failed','site_id':site['site_id'],'site_index':index,'cache_key':key,'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()}
        dump(cache,failure);print('FAILED site',index,str(error),flush=True);return failure

def process(task):
    try:return _process(task)
    except Exception as error:
        site,_,output,common,_=task
        failure={'status':'failed','site_id':site['site_id'],'site_index':site['site_index'],
            'failure_stage':'input_readiness_or_metadata_validation','cache_key':common,
            'error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()}
        dump(Path(output)/'site_analysis'/f"site_{site['site_index']:03d}.json",failure)
        print('FAILED input',site['site_index'],str(error),flush=True);return failure

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--protocol',type=Path,required=True);parser.add_argument('--midpoint-site-ids',type=Path,required=True)
    parser.add_argument('--expected-sites',type=int,default=84);parser.add_argument('--expected-midpoint-sites',type=int,default=7);parser.add_argument('--workers',type=int,default=10)
    parser.add_argument('--allow-streaming',action='store_true')
    args=parser.parse_args();manifest=json.loads(args.manifest.read_text());sites=manifest['sites'];mid=json.loads(args.midpoint_site_ids.read_text());mid=mid['site_ids'] if isinstance(mid,dict) else mid
    if len(sites)!=args.expected_sites or len(set(mid))!=args.expected_midpoint_sites:raise ValueError('Frozen cohort/midpoint count mismatch')
    if not set(mid).issubset({s['site_id'] for s in sites}):raise ValueError('Midpoint IDs outside cohort')
    if not args.allow_streaming and not (args.manifest.parent/'acquisition_complete.json').exists():raise ValueError('Acquisition completion gate missing')
    common={'driver_sha256':core.sha256(Path(__file__)),'core_sha256':core.sha256(Path(core.__file__)),
        'manifest_sha256':core.sha256(args.manifest),'protocol_sha256':core.sha256(args.protocol),
        'midpoint_selection_sha256':core.sha256(args.midpoint_site_ids),'gudhi_version':gudhi.__version__,
        'environment':{p:importlib.metadata.version(p) for p in ('numpy','scipy','ripser')}}
    tasks=[(s,str(args.manifest.parent),str(args.output_dir),common,s['site_id'] in mid) for s in sites]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:records=list(pool.map(process,tasks))
    failures=[r for r in records if r['status']=='failed'];complete=[r for r in records if r['status']=='complete']
    compact=[]
    for r in complete:
        path=args.output_dir/'site_analysis'/f"site_{r['site_index']:03d}.json"
        r['full_diagram_artifact']={'path':str(path.resolve()),'sha256':core.sha256(path)}
        ds=r['representations']['native'].pop('h1_diagrams_ref_then_alts');r['representations']['native']['h1_interval_counts_ref_then_alts']=[len(d) for d in ds];compact.append(r)
    pairs=[p for r in complete for p in r['pair_diagnostics']];checks=[p['midpoint_check'] for p in pairs if 'midpoint_check'in p]
    out={'artifact_type':'label_blind_prospective_anchor_replication','status':'complete' if not failures else 'complete_with_failures','provenance':common,
        'n_planned_sites':len(sites),'n_complete_sites':len(complete),'n_failed_sites':len(failures),'failures':failures,'records':compact,
        'summary':{'pairs_evaluated':len(pairs),'numerically_saturated_pairs_primary_1e10':sum(p['numerically_saturated_at_primary_1e10'] for p in pairs),
            'numerically_saturated_pairs_sensitivity_1e12':sum(p['numerically_saturated_at_1e12'] for p in pairs),
            'tiny_shift_pairs':sum(p['tiny_shift_at_1e10'] for p in pairs),
            'non_tiny_nonsaturated_pairs':sum(not p['tiny_shift_at_1e10'] and not p['numerically_saturated_at_primary_1e10'] for p in pairs),
            'maximum_absolute_saturation_residual':max((p['absolute_saturation_residual'] for p in pairs),default=None),
            'midpoint_checks':len(checks),'midpoint_affine_failures':sum(not c['affine_agreement_passed'] for c in checks),
            'midpoint_tube_failures':sum(not c['endpoint_tube_passed'] for c in checks),
            'maximum_midpoint_absolute_error':max((c['absolute_error'] for c in checks),default=None)},
        'selected_labels_used':False,'inferential_tests_added':0,'caution':'Finite precision endpoint residuals and tubes are reported; no exact-real equality or clinical validation claim.'}
    dump(args.output_dir/'anchor_replication_summary.json',out);print(json.dumps(out['summary'],indent=2))

if __name__=='__main__':main()
