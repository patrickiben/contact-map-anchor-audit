import {test,expect} from '@playwright/test';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

test('single-file companion runs offline with no network requests',async({page})=>{
  const network=[],errors=[];
  page.on('request',request=>{if(/^https?:/.test(request.url()))network.push(request.url());});
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.resolve('standalone/AnchorAuditLab.html')).href);
  await expect(page.locator('#lessons details')).toHaveCount(10);
  await expect(page.locator('#quiz-items fieldset')).toHaveCount(12);
  await expect(page.locator('#study-content')).toContainText('84 sites');
  await page.locator('#preset').selectOption('turning');
  await page.locator('[data-lambda="0.5"]').click();
  await expect(page.locator('#current-members')).toHaveText('Fixed');
  expect((await page.evaluate(()=>window.anchorAuditLab.snapshot())).current[0].value).toBe(0);
  expect(network).toEqual([]);expect(errors).toEqual([]);
});
