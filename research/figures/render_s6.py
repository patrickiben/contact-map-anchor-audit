#!/usr/bin/env python3
"""Fixed input-order site 0; linear contrast view plus unclipped control."""
from pathlib import Path
import json, hashlib, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--data-dir',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--summary-file',type=Path,required=True)
args=parser.parse_args()
DATA=args.data_dir.resolve()
OUTPUT=args.output_dir.resolve()
OUTPUT.mkdir(parents=True,exist_ok=True)
for name in ['figure_s6_first_genomic_site.png','figure_s6_first_genomic_site.pdf','figure_s6_first_genomic_site.svg','figure_s6_print_preview.png','figure_s6_display.json']:
    if (OUTPUT/name).exists(): raise FileExistsError('Refusing to overwrite: '+str(OUTPUT/name))
manifest=DATA/'manifest.json'
summary=args.summary_file.resolve()
s=next(x for x in json.loads(manifest.read_text())['sites'] if x['site_index']==0)
r=next(x for x in json.loads(summary.read_text())['records'] if x['site_index']==0)
npz=DATA/'sites'/Path(s['npz_path']).name
if not npz.is_file(): raise FileNotFoundError(f'Missing site file within data directory: {npz.name}')
with np.load(npz,allow_pickle=False) as a:
    ref=a['ref'].astype(float); alt=a['alt'][s['selected_allele_index']].astype(float)
diff=alt-ref
mask=np.eye(ref.shape[0],dtype=bool)
v=diff[~mask]
lim=float(np.percentile(np.abs(v),99))
full=float(np.max(np.abs(v)))
nclip=int(np.count_nonzero(np.abs(v)>lim))
clippct=100*nclip/v.size
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(6.5,7.0),layout='constrained')
extent=[-524.288,524.288,524.288,-524.288]
for ax in axes.flat[:3]:
    ax.set(xlabel='Position from variant (kb)',ylabel='Position from variant (kb)',xticks=[-400,0,400],yticks=[-400,0,400])
def heat(ax,arr,cmap,lo,hi,label,extend='neither'):
    cmap=plt.get_cmap(cmap).copy();cmap.set_bad('#bdbdbd')
    im=ax.imshow(np.ma.array(arr,mask=mask),cmap=cmap,vmin=lo,vmax=hi,extent=extent,interpolation='nearest',rasterized=True)
    cb=fig.colorbar(im,ax=ax,orientation='horizontal',pad=.02,fraction=.055,extend=extend)
    cb.set_label(label,fontsize=10)
    return cb
cb=heat(axes[0,0],ref,'viridis',float(ref[~mask].min()),float(ref[~mask].max()),'Predicted log-enrichment')
cb.set_ticks([-.5,0,.5,1,1.5])
axes[0,0].set_title('A  Reference map',loc='left')
cb=heat(axes[0,1],diff,'RdBu_r',-lim,lim,'ALT − REF (log-enrichment)', 'both')
cb.set_ticks([-lim,0,lim]);cb.set_ticklabels([f'−{lim:.5f}','0',f'+{lim:.5f}'])
axes[0,1].set_title('B  Difference: contrast',loc='left')
cb=heat(axes[1,0],diff,'RdBu_r',-full,full,'ALT − REF (log-enrichment)')
cb.set_ticks([-full,0,full]);cb.set_ticklabels([f'−{full:.5f}','0',f'+{full:.5f}'])
axes[1,0].set_title('C  Difference: full range',loc='left')
ax=axes[1,1];x=np.arange(3)
for j,(rep,label,col) in enumerate([('native','Native','#3265a8'),('centered','Mean-centered','#c56b24')]):
    ax.bar(x+(j-.5)*.32,r['representations'][rep]['distances'],width=.32,label=label,color=col)
ax.set(xticks=x,xticklabels=[a+(' *' if i==s['selected_allele_index'] else '') for i,a in enumerate(s['alleles'])],ylabel=r'$H_1$ bottleneck distance',xlabel='Alternate allele (* selected)',ylim=(0,.022))
ax.set_title('D  Three allele contrasts',loc='left');ax.legend(frameon=False,fontsize=10,loc='upper right')
fig.suptitle(f"Site 0: {r['site_id']} · {r['gene'].upper()} · ALT T",fontsize=11)
fig.supxlabel(f'B: symmetric 99th-percentile limit; {clippct:.3f}% of off-diagonal cells clipped.\nC: same difference, full range; no clipping. Gray diagonal excluded.',fontsize=10)
for ext in ['png','svg','pdf']:
    fig.savefig(OUTPUT/f'figure_s6_first_genomic_site.{ext}',dpi=300)
# Same canvas rendered at normal printed width for visual QA.
fig.savefig(OUTPUT/'figure_s6_print_preview.png',dpi=100)
plt.close(fig)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stats={'site_index':0,'site_id':r['site_id'],'selected_allele':s['alleles'][s['selected_allele_index']],'shape':list(diff.shape),'off_diagonal_cells':v.size,'difference_min':float(v.min()),'difference_max':float(v.max()),'absolute_difference_percentiles':{str(q):float(np.percentile(abs(v),q)) for q in [50,90,95,98,99,99.5,100]},'B_linear_symmetric_limit':lim,'B_strictly_clipped_cells':nclip,'B_clipped_percent':clippct,'C_linear_symmetric_limit':full,'C_clipped_cells':0,'zero_difference_cells':int(np.count_nonzero(v==0)),'source_files':{'data/manifest.json':sha(manifest),'summary/'+summary.name:sha(summary),'data/sites/'+npz.name:sha(npz)},'script_sha256':sha(Path(__file__)),'original_bar_values':{rep:r['representations'][rep]['distances'] for rep in ['native','centered']},'note':'Both triangles counted; these are display cells, not independent observations. No smoothing, interpolation, aggregation, nonlinear transform, or new scientific calculation. Diagonal masked only for display.'}
(OUTPUT/'figure_s6_display.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats,indent=2))
