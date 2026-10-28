import {auditSite,bottleneck,shiftDiagram,endpointBounds,PRESETS} from './core.mjs';

const $ = id => document.getElementById(id);
const COLORS = ['#177d78','#c96347','#b17a24','#776b9d','#487fa3','#a15d79','#688340','#755f49'];
const MAX_BYTES = 2*1024*1024;
const state = {site:null,report:null,preset:null,lambda:0.5,tolerance:1e-6,inspected:null,custom:false,quiz:[],attempts:0};
const escape = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const clone = value => JSON.parse(JSON.stringify(value));
const fmt = (value,precision=4) => {
  if(value===null||value===undefined||!Number.isFinite(Number(value)))return '—';
  const n=Number(value);if(n===0)return '0';
  if(Math.abs(n)<1e-4||Math.abs(n)>=1e5)return n.toExponential(2);
  return n.toFixed(precision).replace(/\.?0+$/,'');
};
const fixedCredit = value => value===null||value===undefined?'—':Number(value).toFixed(3);
const words = ids => ids?.length ? ids.join(' · ') : 'none';
const members = scores => {
  const best=Math.max(...scores.map(x=>x.value));
  return scores.filter(x=>x.value>=best-state.tolerance).map(x=>x.id);
};
const credit = ids => state.site?.selected==null ? null : ids.includes(state.site.selected)?1/ids.length:0;
const svgTitle = (title,description) => `<title>${escape(title)}</title><desc>${escape(description)}</desc>`;
function setStatus(message,isError=false){$('loading-status').textContent=message;$('loading-status').classList.toggle('error',isError);}
function inputStatus(message,isError=false){$('input-status').textContent=message;$('input-status').classList.toggle('error',isError);}
function colorOf(id){const index=state.site.alternates.findIndex(a=>a.id===id);return COLORS[(index+COLORS.length)%COLORS.length];}
function inputLimit(site){
  if(!site||typeof site!=='object'||Array.isArray(site))throw new Error('The input must be one site object.');
  if(!Array.isArray(site.reference))throw new Error('Supply reference as an array of [birth, death] pairs.');
  if(!Array.isArray(site.alternates)||site.alternates.length<1||site.alternates.length>8)throw new Error('Supply between 1 and 8 alternates.');
  if(site.reference.length>20||site.alternates.some(a=>Array.isArray(a.diagram)&&a.diagram.length>20))throw new Error('The browser accepts at most 20 points in each diagram. Use the Python toolkit for larger diagrams.');
}
function installSite(site,{preset=null,custom=false}={}){
  inputLimit(site);
  const candidate=clone(site);
  const report=auditSite(candidate,{steps:21,tolerance:state.tolerance,allowance:1e-12});
  state.site=candidate;state.report=report;state.preset=preset;state.custom=custom;state.inspected=candidate.alternates[0].id;
  $('inspected-allele').replaceChildren(...candidate.alternates.map(a=>new Option(a.id,a.id)));
  $('data-badge').textContent=custom?'Your supplied diagrams':'Synthetic example';
  $('data-badge').classList.toggle('neutral',custom);
  $('diagram-input').value=JSON.stringify(candidate,null,2);
  if(custom){
    let option=$('preset').querySelector('option[value="__custom"]');
    if(!option){option=new Option('Your supplied diagrams','__custom');$('preset').append(option);}
    $('preset').value='__custom';$('preset-description').textContent='An audit of your supplied finite diagrams and declared shifts. Their data provenance is not verified by this tool.';
  }else{
    $('preset').value=preset.id;$('preset-description').textContent=preset.description||'';
  }
  setStatus('');render();
}
function recompute(){
  state.report=auditSite(state.site,{steps:21,tolerance:state.tolerance,allowance:1e-12});render();
}
function atLambda(){return state.site.alternates.map(a=>({id:a.id,value:bottleneck(state.site.reference,shiftDiagram(a.diagram,state.lambda*a.delta))}));}
function render(){
  try{renderView();setStatus('');}
  catch(error){
    state.lambda=0;
    try{renderView();}catch{}
    setStatus(`The requested view could not be evaluated safely: ${error.message} The native endpoint is shown where possible.`,true);
  }
}
function renderView(){
  if(!state.site||!state.report)return;
  const scores=atLambda();const top=members(scores);const native=state.report.rankings.native;const currentCredit=credit(top);const nativeCredit=state.report.credits?.native??credit(native);
  $('lambda-value').textContent=state.lambda.toFixed(2);$('table-lambda').textContent=state.lambda.toFixed(2);$('lambda').value=String(state.lambda);
  $('native-count').textContent=`${native.length} ${native.length===1?'allele':'alleles'}`;$('native-members').textContent=words(native);
  $('current-count').textContent=`${top.length} ${top.length===1?'allele':'alleles'}`;$('current-members').textContent=words(top);
  $('current-credit').textContent=fixedCredit(currentCredit);$('credit-detail').textContent=state.site.selected==null?'No selected label supplied':`Native ${fixedCredit(nativeCredit)} · selected ${state.site.selected}`;
  document.querySelectorAll('[data-lambda]').forEach(b=>{const active=Number(b.dataset.lambda)===state.lambda;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  $('score-subtitle').textContent=state.site.selected==null?'No selected label supplied. Distances and ranking bounds do not require one.':`${state.custom?'Supplied':'Illustrative'} selected label: ${state.site.selected}. Ties share fractional credit.`;
  const informative=state.report.alternatives.filter(a=>a.absolute_shift>2*state.report.allowance);
  const nSaturated=informative.filter(a=>a.near_saturated).length;
  $('saturation-label').textContent=informative.length?`${nSaturated}/${informative.length} near saturation`:'No resolved shift';
  $('saturation-label').title='Counts only paths whose absolute shift exceeds twice the numerical allowance. Zero or unresolved shifts do not provide an informative saturation check.';
  const body=$('score-table').querySelector('tbody');body.innerHTML=state.report.alternatives.map((a,i)=>{
    const current=scores.find(s=>s.id===a.id).value;const isTop=top.includes(a.id);
    return `<tr><td><span class="allele-marker" style="background:${COLORS[i%COLORS.length]}"></span>${escape(a.id)}${state.site.selected===a.id?'<span class="selected-marker">selected label</span>':''}</td><td>${escape(fmt(a.delta))}</td><td>${escape(fmt(a.native))}</td><td><strong>${escape(fmt(current))}</strong></td><td>${escape(fmt(a.centered))}</td><td>${isTop?'<span class="top-marker">'+(top.length>1?'Shared top':'Unique top')+'</span>':'—'}</td></tr>`;
  }).join('');
  const r=state.report.rankings;
  $('decision-note').innerHTML=`<p><strong>At the centered endpoint (λ = 1):</strong> native-diagram bounds leave ${escape(words(r.possible_centered))} as possible top members. ${r.guaranteed_unique_centered.length?`They identify ${escape(words(r.guaranteed_unique_centered))} as the unique leader.`:'They do not identify a unique leader.'}</p><p><strong>Across the whole path:</strong> ${r.native_margin_leaders.length?`${escape(words(r.native_margin_leaders))} passes the native-margin check.`:'No alternate passes the simple native-margin check.'} These numerical bounds use the declared allowance; a floating-point check is not a formal arithmetic certificate.</p><details class="numerical-details"><summary>Numerical scope &amp; diagnostics</summary><ul>${(state.report.warnings||[]).map(w=>`<li>${escape(w)}</li>`).join('')}${informative.length!==state.report.alternatives.length?'<li>The saturation badge excludes zero shifts and shifts no larger than twice the numerical allowance.</li>':''}</ul></details>`;
  $('interpretation').textContent=state.custom?'A unique top score does not establish a biologically correct choice. This audit checks the supplied diagrams and shifts, not the quality of their source data.':'A more decisive ranking does not establish better clinical discrimination. Every example here is synthetic; its selected label is illustrative.';
  drawDistance(scores);drawDiagram();
  $('curve-legend').innerHTML=state.site.alternates.map((a,i)=>`<button type="button" class="curve-key" data-allele="${escape(a.id)}" aria-pressed="${a.id===state.inspected}"><span style="background:${COLORS[i%COLORS.length]}"></span>${escape(a.id)}</button>`).join('');
  $('curve-legend').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{state.inspected=b.dataset.allele;$('inspected-allele').value=state.inspected;render();}));
}
function ticks(min,max,count=4){
  const span=max-min;if(!(span>0))return [min];
  const raw=span/count;if(!(raw>0)||!Number.isFinite(raw))return [min,max];const power=10**Math.floor(Math.log10(raw));const factor=raw/power;const step=(factor<=1?1:factor<=2?2:factor<=5?5:10)*power;if(!(step>0)||!Number.isFinite(step))return [min,max];
  const values=[];const start=Math.ceil(min/step)*step;
  for(let i=0;i<20;i++){const x=start+i*step;if(x>max+step*1e-8)break;values.push(Math.abs(x)<step*1e-8?0:x);}return values;
}
function envelopePoints(alternative){
  const A=alternative.native,C=alternative.centered,T=Math.abs(alternative.delta),error=state.report.allowance;
  const fractions=[0,1];
  // The envelope is the max/min of endpoint cones. Include every possible kink;
  // connecting a coarse grid alone can wrongly exclude the true distance path.
  if(T>0)fractions.push((A-error)/T,1-(C-error)/T,0.5+((A-C)/T)/2,0.5+((C-A)/T)/2);
  return [...new Set(fractions.filter(v=>Number.isFinite(v)&&v>=0&&v<=1))].sort((a,b)=>a-b).map(lambda=>{
    const [lower,upper]=endpointBounds(A,C,alternative.delta,lambda,error);
    return {lambda,lower,upper};
  });
}
function drawDistance(current){
  const alternatives=state.report.alternatives;const inspected=alternatives.find(a=>a.id===state.inspected);
  const envelope=envelopePoints(inspected);const paths=alternatives.flatMap(a=>a.path);const maximum=Math.max(...paths.map(p=>p.distance),...envelope.map(p=>p.upper),...current.map(p=>p.value),0);
  // Normalize plotting coordinates before adding headroom; the audit remains in its original units.
  const scale=maximum>1e6||(maximum>0&&maximum<1e-4)?(10**Math.floor(Math.log10(maximum))||Number.MIN_VALUE):1;
  const scaledMaximum=maximum/scale;const yMax=scaledMaximum>0?scaledMaximum*1.13:1;const box={x:57,y:20,w:442,h:245};const x=v=>box.x+v*box.w;const ys=v=>box.y+box.h-(v/yMax)*box.h;const y=v=>ys(v/scale);
  const axisSuffix=scale===1?'':` / ${fmt(scale,2)}`;
  let content=svgTitle('Bottleneck distances along the anchor path',`Directly evaluated samples for ${alternatives.map(a=>a.id).join(', ')}. Current centering fraction ${state.lambda}. Shading encloses the inspected alternate ${state.inspected} using endpoint bounds.`);
  const yTicks=ticks(0,yMax,4);for(const v of yTicks)content+=`<line x1="${box.x}" x2="${box.x+box.w}" y1="${ys(v)}" y2="${ys(v)}" stroke="#e2e7dc"/><text x="${box.x-9}" y="${ys(v)+4}" text-anchor="end" fill="#63746b" font-size="10">${escape(fmt(v,3))}</text>`;
  for(const v of [0,.25,.5,.75,1])content+=`<line x1="${x(v)}" x2="${x(v)}" y1="${box.y}" y2="${box.y+box.h}" stroke="#eef0e8"/><text x="${x(v)}" y="${box.y+box.h+20}" text-anchor="middle" fill="#63746b" font-size="10">${fmt(v,2)}</text>`;
  const polygon=[...envelope.map(p=>`${x(p.lambda)},${y(Math.max(0,p.lower))}`),...envelope.slice().reverse().map(p=>`${x(p.lambda)},${y(p.upper)}`)].join(' ');
  content+=`<polygon points="${polygon}" fill="${colorOf(state.inspected)}" fill-opacity="0.10" stroke="none"/>`;
  for(const boundary of ['lower','upper'])content+=`<polyline points="${envelope.map(p=>`${x(p.lambda)},${y(Math.max(0,p[boundary]))}`).join(' ')}" fill="none" stroke="${colorOf(state.inspected)}" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="4 4"/>`;
  content+=`<line x1="${x(state.lambda)}" x2="${x(state.lambda)}" y1="${box.y}" y2="${box.y+box.h}" stroke="#85958b" stroke-width="1" stroke-dasharray="3 4"/>`;
  alternatives.forEach((a,i)=>{
    const color=COLORS[i%COLORS.length];const selected=a.id===state.inspected;
    content+=`<polyline points="${a.path.map(p=>`${x(p.lambda)},${y(p.distance)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="${selected?2.8:1.8}" stroke-linejoin="round" stroke-linecap="round" stroke-opacity="${selected?1:.8}"/>`;
    a.path.forEach((p,j)=>{if(j===0||j===a.path.length-1)content+=`<circle cx="${x(p.lambda)}" cy="${y(p.distance)}" r="2.5" fill="${color}"/>`;});
    const value=current.find(s=>s.id===a.id).value;content+=`<circle cx="${x(state.lambda)}" cy="${y(value)}" r="4.5" fill="${color}" stroke="#fffefa" stroke-width="1.7"><title>${escape(a.id)}: ${fmt(value,8)}</title></circle>`;
  });
  content+=`<line x1="${box.x}" x2="${box.x+box.w}" y1="${box.y+box.h}" y2="${box.y+box.h}" stroke="#aab6a7"/><text x="${box.x+box.w/2}" y="310" text-anchor="middle" fill="#53635e" font-size="11">Centering fraction λ</text><text transform="translate(14,145) rotate(-90)" text-anchor="middle" fill="#53635e" font-size="11">Bottleneck distance${escape(axisSuffix)}</text>`;
  $('distance-chart').innerHTML=`<svg viewBox="0 0 520 330" role="img" xmlns="http://www.w3.org/2000/svg">${content}</svg>`;
}
function groupPoints(diagram){
  const map=new Map();for(const [birth,death] of diagram){const key=`${birth}|${death}`;const row=map.get(key)||{birth,death,count:0};row.count++;map.set(key,row);}return [...map.values()];
}
function drawDiagram(){
  const a=state.site.alternates.find(a=>a.id===state.inspected);const moved=shiftDiagram(a.diagram,state.lambda*a.delta);const endpoint=shiftDiagram(a.diagram,a.delta);const all=[...state.site.reference,...a.diagram,...endpoint];
  const maxAbsolute=all.length?Math.max(...all.flat().map(Math.abs)):0;
  const scale=maxAbsolute>1e6||(maxAbsolute>0&&maxAbsolute<1e-4)?(10**Math.floor(Math.log10(maxAbsolute))||Number.MIN_VALUE):1;
  const normalized=all.flat().map(v=>v/scale);
  let low=normalized.length?Math.min(...normalized):0;let high=normalized.length?Math.max(...normalized):1;
  const span=high-low||1;low-=span*.13;high+=span*.13;
  const box={x:115,y:15,w:270,h:270};const xs=v=>box.x+(v-low)/(high-low)*box.w;const ys=v=>box.y+box.h-(v-low)/(high-low)*box.h;const x=v=>xs(v/scale);const y=v=>ys(v/scale);const color=colorOf(a.id);
  const axisSuffix=scale===1?'':` / ${fmt(scale,2)}`;
  let content=svgTitle(`Reference and ${a.id} birth–death diagrams`,`The ${a.id} alternate is translated by ${fmt(state.lambda*a.delta,8)} in both coordinates. Empty diagrams and repeated points are retained; multiplicities are annotated.`);
  content+=`<rect x="${box.x}" y="${box.y}" width="${box.w}" height="${box.h}" fill="#fbfcf7"/>`;
  for(const v of ticks(low,high,4))content+=`<line x1="${xs(v)}" x2="${xs(v)}" y1="${box.y}" y2="${box.y+box.h}" stroke="#e5e9df"/><line x1="${box.x}" x2="${box.x+box.w}" y1="${ys(v)}" y2="${ys(v)}" stroke="#e5e9df"/><text x="${xs(v)}" y="${box.y+box.h+18}" text-anchor="middle" fill="#63746b" font-size="10">${fmt(v,2)}</text><text x="${box.x-10}" y="${ys(v)+4}" text-anchor="end" fill="#63746b" font-size="10">${fmt(v,2)}</text>`;
  content+=`<line x1="${xs(low)}" y1="${ys(low)}" x2="${xs(high)}" y2="${ys(high)}" stroke="#b9c5b8" stroke-dasharray="5 4"/><text x="${xs(high)-9}" y="${ys(high)+14}" text-anchor="end" fill="#89988c" font-size="9">birth = death</text>`;
  for(let i=0;i<a.diagram.length;i++)content+=`<line x1="${x(a.diagram[i][0])}" y1="${y(a.diagram[i][1])}" x2="${x(moved[i][0])}" y2="${y(moved[i][1])}" stroke="${color}" stroke-width="1.2" stroke-opacity=".5"/>`;
  const draw=(diagram,kind)=>{
    for(const p of groupPoints(diagram)){
      const reference=kind==='Reference';const native=kind==='Native alternate';const stroke=reference?'#6b7d72':color;const radius=reference?7:native?5.5:4;
      content+=`<circle cx="${x(p.birth)}" cy="${y(p.death)}" r="${radius}" fill="${reference||native?'#fffefa':color}" stroke="${stroke}" stroke-width="${reference?1.8:1.5}" ${native?'stroke-dasharray="2 2" opacity=".6"':''}><title>${kind}: (${fmt(p.birth,8)}, ${fmt(p.death,8)}), multiplicity ${p.count}</title></circle>`;
      if(p.count>1)content+=`<text x="${x(p.birth)+9}" y="${y(p.death)-9}" fill="${stroke}" font-size="11" font-weight="600">×${p.count}</text>`;
    }
  };
  draw(state.site.reference,'Reference');draw(a.diagram,'Native alternate');draw(moved,'Shifted alternate');
  if(!all.length)content+=`<text x="250" y="147" text-anchor="middle" fill="#63746b" font-size="12">Both diagrams are empty</text>`;
  content+=`<text x="250" y="322" text-anchor="middle" fill="#53635e" font-size="11">Birth${escape(axisSuffix)}</text><text transform="translate(70,150) rotate(-90)" text-anchor="middle" fill="#53635e" font-size="11">Death${escape(axisSuffix)}</text>`;
  $('diagram-chart').innerHTML=`<svg viewBox="0 0 520 330" role="img" xmlns="http://www.w3.org/2000/svg">${content}</svg>`;
  $('diagram-subtitle').textContent=`Alternate ${a.id} · current shift ${fmt(state.lambda*a.delta,6)}`;
  const lifetimes=a.diagram.map(([b,d])=>d-b);const range=lifetimes.length?`${fmt(Math.min(...lifetimes))}${Math.min(...lifetimes)!==Math.max(...lifetimes)?'–'+fmt(Math.max(...lifetimes)):''}`:'no intervals';
  $('lifetime-caption').textContent=`${a.diagram.length} alternate ${a.diagram.length===1?'interval':'intervals'}; native lifetime ${range}. Translating birth and death together preserves these lengths. Diagram intervals are not identified genomic loops.`;
  document.querySelector('.symbol.native').style.borderColor=color;const symbol=document.querySelector('.symbol.shifted');symbol.style.background=color;symbol.style.borderColor=color;
}
function parseInput(text){
  if(new TextEncoder().encode(text).length>MAX_BYTES)throw new Error('The JSON input exceeds the 2 MB browser limit.');
  let parsed;try{parsed=JSON.parse(text);}catch{throw new Error('This is not valid JSON. Check quotes, commas and brackets.');}
  const site=parsed?.input??parsed?.site??parsed;
  if(site?.sites)throw new Error('The browser inspects one site at a time. Supply a single site, or use the Python toolkit for a batch.');
  return site;
}
function runInput(text){
  try{const site=parseInput(text);installSite(site,{custom:true});inputStatus(`Loaded ${state.site.id}. ${state.site.alternates.length} alternates audited locally.`);}
  catch(e){inputStatus(e.message||String(e),true);}
}
function exportAudit(){
  const payload={...clone(state.report),input:clone(state.site),view:{lambda:state.lambda,inspected_alternate:state.inspected,current_distances:atLambda(),current_top_set:members(atLambda())},provenance:{application:'Anchor Audit Lab',version:'0.1.0',source:state.custom?'user-supplied diagrams':'synthetic teaching example',exported_at:new Date().toISOString(),scope:'Finite-diagram numerical audit. No biological validation or formal real-arithmetic certificate.'}};
  const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}));const anchor=document.createElement('a');anchor.href=url;anchor.download=`anchor-audit-${state.site.id.replace(/[^a-zA-Z0-9_-]/g,'_').slice(0,70)}.json`;anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function attachEvents(){
  $('preset').addEventListener('change',()=>{const preset=PRESETS.find(p=>p.id===$('preset').value);if(!preset)return;try{installSite(preset.site,{preset});inputStatus('');}catch(e){setStatus(e.message,true);}});
  $('lambda').addEventListener('input',()=>{state.lambda=Number($('lambda').value);render();});
  document.querySelectorAll('[data-lambda]').forEach(b=>b.addEventListener('click',()=>{state.lambda=Number(b.dataset.lambda);render();}));
  $('tolerance').addEventListener('change',()=>{state.tolerance=Number($('tolerance').value);try{recompute();}catch(e){setStatus(e.message,true);}});
  $('inspected-allele').addEventListener('change',()=>{state.inspected=$('inspected-allele').value;render();});
  $('reset-view').addEventListener('click',()=>{state.lambda=.5;state.tolerance=1e-6;$('tolerance').value='0.000001';state.inspected=state.site.alternates[0].id;$('inspected-allele').value=state.inspected;recompute();});
  $('copy-example').addEventListener('click',()=>{$('diagram-input').value=JSON.stringify(state.site,null,2);inputStatus('Current input copied into the editor.');});
  $('run-input').addEventListener('click',()=>runInput($('diagram-input').value));
  $('diagram-file').addEventListener('change',async()=>{const file=$('diagram-file').files?.[0];if(!file)return;if(file.size>MAX_BYTES){inputStatus('The selected file exceeds the 2 MB browser limit.',true);return;}try{const text=await file.text();$('diagram-input').value=text;runInput(text);}catch{inputStatus('The selected file could not be read.',true);}});
  $('export-audit').addEventListener('click',()=>{try{exportAudit();}catch(error){setStatus(`Export could not be completed: ${error.message}`,true);}});
}
function renderStudy(data){
  if(!Array.isArray(data.cohorts))throw new Error('The study summary has no cohort records.');
  $('study-content').innerHTML=`<div class="cohort-grid">${data.cohorts.map((c,i)=>{
    const preserved=c.preserved_strict_leaders;const resolved=c.resolved_ties;const tied=c.centered_ties;
    return `<article class="cohort-card ${i>0?'replication':''}"><div class="cohort-title"><h3>${escape(c.label)}</h3><p>${escape(c.sites)} sites · ${escape(c.loci)} loci${c.scope_note?`<br>${escape(c.scope_note)}`:""}</p></div><div class="cohort-hero"><strong>${escape(c.simple_bound_leaders)} → ${escape(c.witness_leaders)}</strong><span>centered leaders: simple → strengthened bounds</span></div><div class="cohort-bar" role="img" aria-label="${escape(preserved)} strict native leaders preserved, ${escape(resolved)} ties resolved, ${escape(tied)} centered ties"><span class="preserved" style="width:${preserved/c.sites*100}%"></span><span class="resolved" style="width:${resolved/c.sites*100}%"></span><span class="tied" style="width:${tied/c.sites*100}%"></span></div><div class="cohort-legend"><span><i></i>${escape(preserved)} strict leaders preserved</span><span><i class="resolved"></i>${escape(resolved)} ties resolved</span><span><i class="tied"></i>${escape(tied)} still tied</span></div><div class="study-metrics"><div><span class="small-label">Selected-allele credit</span><strong>${Number(c.native_credit).toFixed(3)} → ${Number(c.centered_credit).toFixed(3)}</strong><p>Native → centered; descriptive</p></div><div><span class="small-label">Added witness resolutions</span><strong>+${escape(c.additional_witness_leaders)}</strong><p>${escape(c.sites-c.witness_leaders)} sites remain unresolved</p></div></div></article>`;
  }).join('')}</div><p class="study-finding">${escape(data.findings?.[0]||'More unique rankings did not establish a consistent improvement in selected-allele credit.')}</p><ul class="scope-list study-results">${(data.findings||[]).slice(1).map(s=>`<li>${escape(s)}</li>`).join('')}</ul><h3 class="small-label">Interpretation boundaries</h3><ul class="scope-list">${(data.limits||[]).map(s=>`<li>${escape(s)}</li>`).join('')}</ul><p class="small-note">${escape(data.scope||'Reported results on predicted contact maps.')} The full study inputs are provided separately in the versioned research archive.</p>`;
}
function renderLearning(data){
  $('lessons').innerHTML=(data.lessons||[]).map((lesson,i)=>`<details class="lesson" ${i===0?'open':''}><summary><span class="lesson-index">${String(i+1).padStart(2,'0')}</span>${escape(lesson.title)}</summary><div class="lesson-content"><p class="lesson-summary">${escape(lesson.summary)}</p>${(lesson.body||[]).map(p=>`<p>${escape(p)}</p>`).join('')}<div class="lesson-boundary"><p><strong>Keep the boundary:</strong> ${escape(lesson.boundary)}</p></div><p class="lesson-exercise">Try it: ${escape(lesson.try_it)}</p>${lesson.source_lines?`<p class="source-range">Source manuscript lines ${escape(lesson.source_lines.join('–'))}</p>`:''}</div></details>`).join('');
  $('glossary').innerHTML=(data.glossary||[]).map(entry=>`<div class="glossary-entry"><dt>${escape(entry.term)}</dt><dd>${escape(entry.definition)}</dd></div>`).join('');
  state.quiz=data.quiz||[];
  $('quiz-items').innerHTML=state.quiz.map((q,i)=>`<fieldset class="question" id="question-${i}"><legend><span class="question-meta">${String(i+1).padStart(2,'0')} / ${escape(q.kind||'Practice')}</span>${escape(q.prompt)}</legend><div class="question-options">${q.choices.map((choice,j)=>`<label><input type="radio" name="question-${i}" value="${j}" aria-describedby="feedback-${i}"><span>${escape(choice)}</span></label>`).join('')}</div><div class="question-feedback" id="feedback-${i}" hidden></div></fieldset>`).join('');
  $('quiz-form').addEventListener('change',()=>{const answered=state.quiz.filter((_,i)=>$('quiz-form').querySelector(`input[name="question-${i}"]:checked`)).length;$('practice-progress').textContent=`${answered} / ${state.quiz.length} answered`;});
  $('quiz-form').addEventListener('submit',event=>{
    event.preventDefault();let correct=0;let answered=0;state.attempts++;
    state.quiz.forEach((q,i)=>{const selected=$('quiz-form').querySelector(`input[name="question-${i}"]:checked`);const feedback=$(`feedback-${i}`);const right=selected&&Number(selected.value)===q.answer_index;if(selected)answered++;if(right)correct++;feedback.hidden=false;feedback.classList.toggle('incorrect',!right);feedback.innerHTML=`<strong>${!selected?'No answer selected.':right?'Correct.':'Try this distinction.'}</strong>${escape(q.explanation)}${right?'':`<p>Answer: ${escape(q.choices[q.answer_index])}</p>`}`;});
    $('quiz-result').textContent=`${correct} / ${state.quiz.length} correct · ${answered} answered · practice attempt ${state.attempts}. Review the explanations and try again.`;
  });
  $('reset-quiz').addEventListener('click',()=>{$('quiz-form').reset();document.querySelectorAll('.question-feedback').forEach(x=>{x.hidden=true;x.textContent='';});$('quiz-result').textContent='';$('practice-progress').textContent=`0 / ${state.quiz.length} answered`;});
  $('practice-progress').textContent=`0 / ${state.quiz.length} answered`;
}
async function loadContent(){
  const jobs=[['./study-summary.json',renderStudy,'study-content','embedded-study-summary'],['./learning.json',renderLearning,'lessons','embedded-learning']];
  await Promise.all(jobs.map(async([url,render,target,embeddedId])=>{
    try{
      const embedded=$(embeddedId);
      if(embedded?.type==='application/json'){render(JSON.parse(embedded.textContent));return;}
      const response=await fetch(url,{cache:'no-cache'});if(!response.ok)throw new Error(`HTTP ${response.status}`);render(await response.json());
    }catch(e){$(target).innerHTML='<p class="unavailable">The packaged content could not be loaded. Serve this folder over HTTP, or read the teaching materials in the GitHub repository.</p>';console.warn(`Packaged content unavailable (${url}):`,e.message);}
  }));
}
try{
  if(!PRESETS.length)throw new Error('No synthetic examples are available.');
  $('preset').replaceChildren(...PRESETS.map(p=>new Option(p.title,p.id)));
  attachEvents();installSite(PRESETS[0].site,{preset:PRESETS[0]});
  await loadContent();
  // Read-only diagnostic snapshot for smoke checks; no uploaded data is transmitted.
  Object.defineProperty(window,'anchorAuditLab',{value:{snapshot:()=>clone({site:state.site,report:state.report,lambda:state.lambda,tolerance:state.tolerance,inspected:state.inspected,custom:state.custom,current:atLambda(),envelope:envelopePoints(state.report.alternatives.find(a=>a.id===state.inspected))})},writable:false});
}catch(error){setStatus(`The audit could not start: ${error.message}`,true);console.error(error);}
