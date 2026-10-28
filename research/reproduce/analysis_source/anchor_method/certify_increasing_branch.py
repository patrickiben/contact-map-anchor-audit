#!/usr/bin/env python3
"""Native-diagram-only Hausdorff lower certificate, checked against stored centered scores."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
from scipy.spatial import cKDTree

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'astra_genomic/genomic_summary.json'
TOL=1e-12
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def directed(points,other,tree):
    if not len(points):return 0.,None
    diag=(points[:,1]-points[:,0])/2
    if len(other):nearest,indices=tree.query(points,k=1,p=np.inf)
    else:nearest=np.full(len(points),np.inf);indices=np.full(len(points),-1)
    costs=np.minimum(diag,nearest);i=int(np.argmax(costs));j=int(indices[i])
    witness={'point_index':i,'point':points[i].tolist(),'nearest_opposite_index':j,'nearest_opposite':other[j].tolist() if j>=0 else None,
        'distance_to_diagonal':float(diag[i]),'distance_to_nearest_opposite':float(nearest[i]) if np.isfinite(nearest[i]) else None,
        'nearest_augmented_distance':float(costs[i])}
    return float(costs[i]),witness

def hausdorff(left,right,lefttree=None):
    left=np.asarray(left,float).reshape(-1,2);right=np.asarray(right,float).reshape(-1,2)
    lt=lefttree if lefttree is not None else (cKDTree(left) if len(left) else None)
    rt=cKDTree(right) if len(right) else None;a,wa=directed(left,right,rt);b,wb=directed(right,left,lt)
    return max(a,b),{'direction':'ref_to_alt' if a>=b else 'alt_to_ref','critical_point':wa if a>=b else wb}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=SOURCE);parser.add_argument('--output',type=Path,default=HERE/'hausdorff_branch_certificate.json');parser.add_argument('--plan',type=Path,default=HERE/'LOWER_BOUND_CERTIFICATE_PLAN.md');args=parser.parse_args()
    source=json.loads(args.source.read_text());rows=[];started=time.monotonic()
    for record in source['records']:
        path=Path(record['full_diagram_artifact']['path']);raw=json.loads(path.read_text())
        diagrams=[np.array(d).reshape(-1,2) for d in raw['representations']['native']['h1_diagrams_ref_then_alts']]
        ref=diagrams[0];reftree=cKDTree(ref) if len(ref) else None
        for i,alt in enumerate(diagrams[1:]):
            native=record['representations']['native']['distances'][i]
            delta=record['means'][i+1]-record['means'][0];magnitude=abs(delta)
            hn,wn=hausdorff(ref,alt,reftree);hs,ws=hausdorff(ref,alt+delta,reftree)
            upper=native+magnitude;lower=max(0.,native-magnitude)
            # This decision uses no centered distance or selected label.
            certified=magnitude>1e-10 and abs(hs-upper)<=TOL
            predicted=upper if certified else None
            centered=record['representations']['centered']['distances'][i]
            error=abs(predicted-centered) if certified else None
            rows.append({'site_id':record['site_id'],'alternate_index':i,'gene':record['gene'],'native_bottleneck':native,
                'mean_shift':delta,'native_hausdorff_lower_bound':hn,'shifted_hausdorff_lower_bound':hs,
                'stability_lower_bound':lower,'stability_upper_bound':upper,
                'increasing_branch_certified_before_comparison':certified,'predicted_centered_score':predicted,
                'tiny_shift_direction_abstention':magnitude<=1e-10,
                'stored_centered_score_for_validation':centered,'certificate_absolute_error':error,
                'native_hausdorff_bottleneck_gap':native-hn,'centered_hausdorff_bottleneck_gap':centered-hs,
                'native_critical_point_witness':wn,'shifted_critical_point_witness':ws})
            if hn>native+1e-10 or hs>centered+1e-10:raise AssertionError('Hausdorff lower bound violation')
            if certified and error>1e-10:raise AssertionError('Increasing certificate failure')
        print('Processed native-diagram site',record['site_index'],flush=True)
    cert=[r for r in rows if r['increasing_branch_certified_before_comparison']]
    summary={'pairs':len(rows),'increasing_branch_certified_pairs':len(cert),
        'actual_increasing_pairs':sum(r['stored_centered_score_for_validation']>r['native_bottleneck'] for r in rows),
        'certificate_failures':sum(r['certificate_absolute_error']>1e-10 for r in cert),
        'maximum_certificate_absolute_error':max((r['certificate_absolute_error'] for r in cert),default=0.),
        'native_hausdorff_equals_bottleneck_pairs':sum(abs(r['native_hausdorff_bottleneck_gap'])<=TOL for r in rows),
        'centered_hausdorff_equals_bottleneck_pairs':sum(abs(r['centered_hausdorff_bottleneck_gap'])<=TOL for r in rows),
        'max_native_hausdorff_bottleneck_gap':max(r['native_hausdorff_bottleneck_gap'] for r in rows),
        'max_centered_hausdorff_bottleneck_gap':max(r['centered_hausdorff_bottleneck_gap'] for r in rows)}
    result={'artifact_type':'native_diagram_hausdorff_branch_certificate','selected_labels_used':False,'new_persistence_computations':0,
        'new_bottleneck_evaluations':0,'source_summary_sha256':sha(args.source),'script_sha256':sha(Path(__file__)),
        'plan_sha256':sha(args.plan),'numeric_certificate_tolerance':TOL,
        'elapsed_seconds':time.monotonic()-started,'summary':summary,'pairs':rows,
        'scope':'Numerical native-diagram witness for the increasing branch, not a new clinical endpoint; equality of lower and upper bounds under stated tolerance. Decreasing branch abstains.'}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
