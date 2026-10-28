import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
const learning=JSON.parse(await fs.readFile(new URL('../../docs/learning.json',import.meta.url),'utf8'));
test.beforeEach(async({page})=>{
  await page.goto('/');
  await expect(page.locator('#lessons details')).toHaveCount(10);
  await expect(page.locator('#score-table tbody tr')).toHaveCount(3);
});

test('controls recompute rankings and expose a nonmonotone path',async({page})=>{
  await expect(page.locator('#native-count')).toHaveText('3 alleles');
  await page.locator('[data-lambda="0"]').click();
  await expect(page.locator('#current-count')).toHaveText('3 alleles');
  await expect(page.locator('#current-credit')).toHaveText('0.333');
  await page.locator('[data-lambda="1"]').click();
  await expect(page.locator('#current-members')).toHaveText('A');
  await expect(page.locator('#current-credit')).toHaveText('0.000');
  await page.locator('#tolerance').selectOption('0.25');
  await expect(page.locator('#current-members')).toHaveText('A · C');
  await page.locator('#preset').selectOption('turning');
  await page.locator('[data-lambda="0.5"]').click();
  await expect(page.locator('#current-members')).toHaveText('Fixed');
  const state=await page.evaluate(()=>window.anchorAuditLab.snapshot());
  expect(state.current.find(a=>a.id==='Turning').value).toBe(0);
  await page.locator('#preset').selectOption('multiplicity');
  await expect(page.locator('#diagram-chart')).toContainText('×2');
});

test('local import, hostile labels, export and reimport preserve calculations',async({page})=>{
  const external=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4173'))external.push(r.url());});
  const input={id:'local-example',reference:[[0,4]],alternates:[{id:'<img src=x onerror=alert(1)>',diagram:[[1,5]],delta:.25}],selected:null};
  const dialogs=[];page.on('dialog',async d=>{dialogs.push(d.message());await d.dismiss();});
  await page.locator('#diagram-input').fill(JSON.stringify(input));
  await page.locator('#run-input').click();
  await expect(page.locator('#score-table tbody tr')).toHaveCount(1);
  await expect(page.locator('#score-table tbody')).toContainText(input.alternates[0].id);
  expect(await page.locator('#score-table img').count()).toBe(0);
  const downloadPromise=page.waitForEvent('download');
  await page.locator('#export-audit').click();
  const report=JSON.parse(await fs.readFile(await (await downloadPromise).path(),'utf8'));
  expect(report.input).toEqual(input);expect(report.alternatives[0].centered).toBe(1.25);
  await page.locator('#diagram-file').setInputFiles({name:'export.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(report))});
  expect((await page.evaluate(()=>window.anchorAuditLab.snapshot())).report.alternatives[0].centered).toBe(1.25);
  expect(dialogs).toEqual([]);expect(external).toEqual([]);
});

test('invalid input preserves the last accepted audit',async({page})=>{
  const original=await page.evaluate(()=>window.anchorAuditLab.snapshot().site.id);
  for(const content of ['{broken',JSON.stringify({id:'invalid',reference:[[2,1]],alternates:[{id:'A',diagram:[],delta:0}]}),JSON.stringify({id:'huge',reference:[],alternates:[{id:'A',diagram:[[0,4]],delta:1e20}]})]){
    await page.locator('#diagram-input').fill(content);await page.locator('#run-input').click();
    await expect(page.locator('#input-status')).not.toBeEmpty();
    expect(await page.evaluate(()=>window.anchorAuditLab.snapshot().site.id)).toBe(original);
  }
});

test('learning practice gives feedback and supports retries',async({page})=>{
  await expect(page.locator('#quiz-items fieldset')).toHaveCount(12);
  await page.getByRole('button',{name:'Check answers',exact:true}).click();
  await expect(page.locator('#quiz-result')).toContainText('0 / 12');
  for(const [i,q]of learning.quiz.entries())await page.locator(`input[name="question-${i}"][value="${q.answer_index}"]`).check();
  await page.getByRole('button',{name:'Check answers',exact:true}).click();
  await expect(page.locator('#quiz-result')).toContainText('12 / 12');
  await expect(page.locator('#practice-progress')).toContainText('12 / 12');
  await page.locator('#reset-quiz').click();
  await expect(page.locator('#quiz-items input:checked')).toHaveCount(0);
});

test('responsive layout and automated accessibility scan',async({page},testInfo)=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.screenshot({path:`validation/lab-${testInfo.project.name}.png`,fullPage:false});
  const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  expect(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
  expect(errors).toEqual([]);
});


test('the endpoint envelope includes an off-grid zero-distance cusp',async({page})=>{
  const input={id:'off-grid-cusp',reference:[[0,4]],alternates:[{id:'Cusp',diagram:[[-.37,3.63]],delta:1}]};
  await page.locator('#diagram-input').fill(JSON.stringify(input));
  await page.locator('#run-input').click();
  await page.locator('#lambda').fill('0.37');
  const state=await page.evaluate(()=>window.anchorAuditLab.snapshot());
  expect(state.current[0].value).toBe(0);
  expect(state.envelope.some(p=>Math.abs(p.lambda-.37)<1e-10&&p.lower<=1e-12)).toBe(true);
  // Check the rendered lower boundary, not only the calculated diagnostic points.
  const polygon=await page.locator('#distance-chart polygon').getAttribute('points');
  const lower=polygon.trim().split(/\s+/).map(p=>p.split(',').map(Number)).slice(0,state.envelope.length);
  const x=57+.37*442;
  const right=lower.findIndex(([px])=>px>=x);
  expect(right).toBeGreaterThan(0);
  const [leftX,leftY]=lower[right-1], [rightX,rightY]=lower[right];
  const boundaryY=leftY+(rightY-leftY)*(x-leftX)/(rightX-leftX);
  // Zero distance is y=265; coarse 0.05 interpolation incorrectly put this boundary above zero.
  expect(boundaryY).toBeCloseTo(265,8);
});
