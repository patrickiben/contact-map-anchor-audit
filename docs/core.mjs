/** Finite-diagram anchor audits. Numerical calculations, not validated real arithmetic. */
export const MAX_DIAGRAM_POINTS = 20;
export const MAX_ALTERNATES = 8;
export const VERSION = '0.1.0';
const finite = (x, name) => {
  if (typeof x !== 'number' || !Number.isFinite(x)) throw new Error(`${name} must be a finite number.`);
  return x;
};
const nonnegative = (x, name) => {
  finite(x, name); if (x < 0) throw new Error(`${name} must be nonnegative.`); return x;
};
function diagram(value, name = 'Diagram') {
  if (!Array.isArray(value) || value.length > MAX_DIAGRAM_POINTS) throw new Error(`${name} must be an array of at most ${MAX_DIAGRAM_POINTS} [birth, death] pairs. Use the Python toolkit for larger diagrams.`);
  return value.map((p, i) => {
    if (!Array.isArray(p) || p.length !== 2) throw new Error(`${name}, point ${i + 1}: expected [birth, death].`);
    const b = finite(p[0], `${name} birth`), d = finite(p[1], `${name} death`);
    if (d < b) throw new Error(`${name}, point ${i + 1}: death must be at least birth.`);
    finite(d - b, `${name} lifetime`);
    return [b, d];
  });
}
const linf = (x, y) => finite(Math.max(Math.abs(x[0] - y[0]), Math.abs(x[1] - y[1])), 'Coordinate difference');
export function shiftDiagram(D, t, allowance=1e-12) {
  finite(t, 'Shift'); nonnegative(allowance,'Numerical allowance');
  const twiceAllowance=finite(2*allowance,'Twice the numerical allowance');
  function checkedAdd(x) {
    const sum=finite(x+t,'Shifted coordinate');
    const virtualShift=finite(sum-x,'Translation residual');
    const virtualX=finite(sum-virtualShift,'Translation residual');
    const residual=finite((x-virtualX)+(t-virtualShift),'Translation residual');
    if(Math.abs(residual)>allowance)throw new Error('Translation rounding exceeds allowance; rescale coordinates or justify a larger error budget.');
    return sum;
  }
  return diagram(D).map(([b,d])=>{
    const shifted=[checkedAdd(b),checkedAdd(d)];
    const difference=finite(finite(shifted[1]-shifted[0],'Translated lifetime')-finite(d-b,'Original lifetime'),'Lifetime difference');
    if(Math.abs(difference)>twiceAllowance)throw new Error('Translation rounding changes a lifetime beyond allowance; rescale coordinates or justify a larger error budget.');
    return shifted;
  });
}
/** Augmented finite matching includes each point's own diagonal copy. */
export function bottleneck(D, E) {
  D = diagram(D); E = diagram(E);
  const n = D.length, m = E.length, N = n + m;
  if (!N) return 0;
  const costs = Array.from({length:N}, () => Array(N).fill(Infinity));
  for (let i=0; i<n; i++) {
    for(let j=0;j<m;j++) costs[i][j] = linf(D[i],E[j]);
    costs[i][m+i] = (D[i][1]-D[i][0])/2;
  }
  for(let j=0;j<m;j++) {
    costs[n+j][j] = (E[j][1]-E[j][0])/2;
    for(let i=0;i<n;i++) costs[n+j][m+i] = 0;
  }
  const levels = [...new Set(costs.flat().filter(Number.isFinite))].sort((a,b)=>a-b);
  function feasible(threshold) {
    const match = Array(N).fill(-1);
    function augment(left, seen) {
      for(let right=0;right<N;right++) {
        if (costs[left][right] > threshold || seen[right]) continue;
        seen[right] = true;
        if(match[right] === -1 || augment(match[right],seen)) {match[right]=left; return true;}
      }
      return false;
    }
    for(let left=0;left<N;left++) if(!augment(left,Array(N).fill(false))) return false;
    return true;
  }
  let lo=0, hi=levels.length-1;
  while(lo<hi) {const mid=Math.floor((lo+hi)/2);if(feasible(levels[mid]))hi=mid;else lo=mid+1;}
  return levels[lo];
}
/** Diagonal-augmented nearest-neighbor lower bound; does not respect multiplicity. */
export function hausdorff(D,E) {
  D=diagram(D);E=diagram(E);
  const directed = (a,b) => a.reduce((v,p)=>Math.max(v,Math.min((p[1]-p[0])/2,...b.map(q=>linf(p,q)))),0);
  return Math.max(directed(D,E),directed(E,D));
}
export function endpointBounds(A,C,delta,lambda,error=0) {
  nonnegative(A,'Native score');nonnegative(C,'Centered score');finite(delta,'Shift');finite(lambda,'Lambda');nonnegative(error,'Error allowance');
  if(lambda<0||lambda>1)throw new Error('Lambda must be between zero and one.');
  const T=Math.abs(delta),u=lambda*T,v=(1-lambda)*T;
  const lower=Math.max(0,finite(A-error-u,'Endpoint lower bound'),finite(C-error-v,'Endpoint lower bound'));
  const upper=Math.min(finite(A+error+u,'Endpoint upper bound'),finite(C+error+v,'Endpoint upper bound'));
  if(lower>upper)throw new Error('Endpoint values and error allowance are inconsistent with the translation bound.');
  return [lower,upper];
}
export function topSet(scores,tolerance=1e-6) {
  nonnegative(tolerance,'Tie tolerance');const entries=Object.entries(scores);
  if(!entries.length)throw new Error('At least one score is required.');
  for(const [id,v] of entries)finite(v,`Score ${id}`);
  const maximum=Math.max(...entries.map(x=>x[1]));const cutoff=finite(maximum-tolerance,'Rank cutoff');return entries.filter(([,v])=>v>=cutoff).map(([id])=>id);
}
export function intervalRanking(lower,upper,tolerance=1e-6) {
  nonnegative(tolerance,'Tie tolerance');const ids=Object.keys(lower);
  if(!ids.length||ids.length!==Object.keys(upper).length||ids.some(id=>!Object.hasOwn(upper,id)))throw new Error('Lower and upper interval keys must match and be nonempty.');
  for(const id of ids){finite(lower[id],'Lower bound');finite(upper[id],'Upper bound');if(lower[id]>upper[id])throw new Error('Lower bound exceeds upper bound.');}
  if(ids.length===1)return {possible:[...ids],guaranteed:[...ids],guaranteed_unique:[...ids]};
  const maxOther=(object,id)=>Math.max(...ids.filter(b=>b!==id).map(b=>object[b]));
  return {
    possible:ids.filter(id=>upper[id]>=finite(maxOther(lower,id)-tolerance,'Possible rank cutoff')),
    guaranteed:ids.filter(id=>lower[id]>=finite(maxOther(upper,id)-tolerance,'Guaranteed rank cutoff')),
    guaranteed_unique:ids.filter(id=>lower[id]>finite(maxOther(upper,id)+tolerance,'Unique rank cutoff'))
  };
}
export function auditSite(site,{steps=21,tolerance=1e-6,allowance=1e-12}={}) {
  nonnegative(tolerance,'Tie tolerance');nonnegative(allowance,'Numerical allowance');
  if(!Number.isInteger(steps)||steps<2||steps>201)throw new Error('Path samples must be an integer from 2 to 201.');
  if(!site||typeof site!=='object'||Array.isArray(site))throw new Error('Input must be a site object.');
  const reference=diagram(site.reference,'Reference');
  if(!Array.isArray(site.alternates)||!site.alternates.length||site.alternates.length>MAX_ALTERNATES)throw new Error(`Supply between 1 and ${MAX_ALTERNATES} alternates.`);
  const ids = site.alternates.map(a=>a?.id);
  if(ids.some(id=>typeof id!=='string'||!id.trim()||id.length>100)||new Set(ids).size!==ids.length)throw new Error('Alternate IDs must be unique, nonempty strings of at most 100 characters.');
  if(site.selected!=null&&!ids.includes(site.selected))throw new Error('Selected ID must identify an alternate.');
  if(typeof site.id!=='string'||!site.id.trim()||site.id.length>200)throw new Error('Site ID must be a nonempty string of at most 200 characters.');
  const twiceAllowance=finite(2*allowance,'Twice the numerical allowance');
  const alternatives=site.alternates.map(a=>{
    const E=diagram(a.diagram,`Alternate ${a.id}`),delta=finite(a.delta,`Shift for ${a.id}`),shifted=shiftDiagram(E,delta,allowance);
    const native=bottleneck(reference,E),centered=bottleneck(reference,shifted),T=Math.abs(delta),H=hausdorff(reference,shifted);
    const residual=finite(T-Math.abs(centered-native),'Saturation residual');
    const lower=Math.max(0,finite(native-T-allowance,'Lower bound'),finite(H-allowance,'Witness lower bound')),upper=finite(native+T+allowance,'Upper bound');
    if(lower>upper)throw new Error('Native witness bounds are inconsistent at this allowance.');
    const path=Array.from({length:steps},(_,i)=>{
      const lambda=i/(steps-1),bounds=endpointBounds(native,centered,delta,lambda,allowance);
      return {lambda,distance:bottleneck(reference,shiftDiagram(E,lambda*delta,allowance)),lower:bounds[0],upper:bounds[1]};
    });
    return {id:a.id,delta,native,centered,change:centered-native,absolute_shift:T,saturation_residual:residual,near_saturated:Math.abs(residual)<=twiceAllowance,hausdorff:H,lower,upper,path};
  });
  const native=Object.fromEntries(alternatives.map(a=>[a.id,a.native]));
  const centered=Object.fromEntries(alternatives.map(a=>[a.id,a.centered]));
  const ranks=intervalRanking(Object.fromEntries(alternatives.map(a=>[a.id,a.lower])),Object.fromEntries(alternatives.map(a=>[a.id,a.upper])),tolerance);
  const rankings={native:topSet(native,tolerance),centered:topSet(centered,tolerance),possible_centered:ranks.possible,guaranteed_centered:ranks.guaranteed,guaranteed_unique_centered:ranks.guaranteed_unique,native_margin_leaders:alternatives.filter(a=>alternatives.every(b=>a.id===b.id||finite(a.native-b.native,'Native margin')>finite(a.absolute_shift+b.absolute_shift+tolerance+twiceAllowance,'Required margin'))).map(a=>a.id)};
  for(const key of Object.keys(rankings))rankings[key]=ids.filter(id=>rankings[key].includes(id));
  const credit=top=>site.selected==null?null:top.includes(site.selected)?1/top.length:0;
  const warnings=['Finite-coordinate floating-point calculations; the numerical allowance is user-supplied, not a validated solver error bound.','Sampled paths are direct matching evaluations; numerical endpoint saturation is not an exact-real proof.','These outputs audit diagram alignment and rankings, not biological validity or clinical prediction.'];
  if(alternatives.some(a=>a.delta===0))warnings.push('A zero shift gives a constant path; endpoint saturation is then trivial.');
  for(const a of alternatives)if(a.absolute_shift>0&&a.absolute_shift<=twiceAllowance)warnings.push(`${a.id}: the nonzero shift is no larger than twice the allowance; numerical near-saturation is low-information at this error budget.`);
  if(alternatives.some(a=>a.saturation_residual < -2*allowance))warnings.push('An endpoint exceeds the translation bound beyond the allowance; inspect numerical inputs and precision.');
  return {schema_version:'anchor-audit/report-v1',id:site.id??'unnamed-site',backend:{name:'reference',libraries:{}},numeric_scope:'Finite-diagram threshold matching in IEEE-754 arithmetic; no validated real-arithmetic certificate.',tolerance,allowance,selected:site.selected??null,alternatives,rankings,credits:site.selected==null?null:{native:credit(rankings.native),centered:credit(rankings.centered)},warnings};
}
export const PRESETS=[
  {id:'tie-split',title:'A tie becomes a decision',description:'Three native distances tie. Different anchor shifts create a unique leader while the illustrative selected allele loses credit.',site:{id:'synthetic-tie-split',reference:[[0,4]],alternates:[{id:'A',diagram:[[1,5]],delta:.25},{id:'B',diagram:[[1,5]],delta:-.25},{id:'C',diagram:[[1,5]],delta:.1}],selected:'B'}},
  {id:'opposite',title:'Same shift, opposite response',description:'Native distance and mean shift match, but relative diagram location changes the direction of response.',site:{id:'synthetic-opposite-slopes',reference:[[0,4]],alternates:[{id:'Right',diagram:[[1,5]],delta:.25},{id:'Left',diagram:[[-1,3]],delta:.25}]}},
  {id:'turning',title:'A path that turns',description:'Equal endpoint distances can conceal a decrease followed by an increase. Direct midpoint evaluation detects the turn.',site:{id:'synthetic-turning',reference:[[0,4]],alternates:[{id:'Turning',diagram:[[-1,3]],delta:2},{id:'Fixed',diagram:[[.5,4.5]],delta:0}]}},
  {id:'cap',title:'Matching to the diagonal',description:'The distance rises and then levels off when matching to the diagonal becomes cheaper.',site:{id:'synthetic-diagonal-cap',reference:[[0,2]],alternates:[{id:'Capped',diagram:[[0,2]],delta:2},{id:'Fixed',diagram:[[.25,2.25]],delta:0}]}},
  {id:'multiplicity',title:'Why a lower bound can abstain',description:'Repeated intervals matter to complete matching. A nearest-neighbor lower bound can miss multiplicity.',site:{id:'synthetic-multiplicity',reference:[[0,4],[0,4]],alternates:[{id:'One copy',diagram:[[0,4]],delta:.25},{id:'Two copies',diagram:[[0,4],[0,4]],delta:.25}]}}
];
