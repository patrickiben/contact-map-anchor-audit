import test from 'node:test';
import assert from 'node:assert/strict';
import {auditSite,bottleneck,hausdorff,shiftDiagram,endpointBounds,PRESETS} from '../docs/core.mjs';

test('all teaching presets satisfy their endpoint bounds at directly evaluated samples',()=>{
  for(const preset of PRESETS){
    const report=auditSite(preset.site,{steps:101});
    for(const a of report.alternatives)for(const p of a.path){
      assert.ok(p.distance>=p.lower-1e-14&&p.distance<=p.upper+1e-14);
    }
  }
});
test('turning paths require internal evaluations',()=>{
  const a=auditSite(PRESETS.find(p=>p.id==='turning').site).alternatives[0];
  assert.equal(a.native,1);assert.equal(a.centered,1);assert.equal(a.path[10].distance,0);
  assert.deepEqual(endpointBounds(1,1,2,.5),[0,2]);
});
test('multiplicity separates complete matching from the lower bound',()=>{
  const D=[[0,4],[0,4]],E=[[0,4]];
  assert.equal(bottleneck(D,E),2);assert.equal(hausdorff(D,E),0);
});
test('large translations cannot silently erase lifetime information',()=>{
  assert.throws(()=>shiftDiagram([[0,4]],1e20),/rounding/);
  assert.deepEqual(shiftDiagram([[0,4]],.25),[[.25,4.25]]);
});
test('tiny shifts and zero shifts have explicit interpretation limits',()=>{
  const report=auditSite({id:'tiny',reference:[],alternates:[{id:'A',diagram:[],delta:1e-14}]});
  assert.ok(report.warnings.some(w=>w.includes('low-information')));
  assert.deepEqual(report.backend,{name:'reference',libraries:{}});
});
