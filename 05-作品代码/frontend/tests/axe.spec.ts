import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';

const AXE_RULES_UNAVAILABLE_IN_CHROME_147 = ['color-contrast', 'color-contrast-enhanced'];

const runAxeWithoutChrome147ContrastHang = (page: Page) => new AxeBuilder({ page })
  .disableRules(AXE_RULES_UNAVAILABLE_IN_CHROME_147)
  .analyze();

const screens = [
  { role: 'student', user: 'axe-student', route: '/', marker: '早上好，林同学' },
  { role: 'teacher', user: 'axe-teacher', route: 'teacher/resources', marker: '课程资料管理' },
  { role: 'admin', user: 'axe-admin', route: 'admin/knowledge-bases', marker: '平台运维与知识库' },
] as const;

test('axe engine probe: default rules except Chrome 147 contrast hang', async ({ page }) => {
  await page.setContent('<!doctype html><html lang="zh-CN"><head><title>Probe</title></head><body><main><h1>Probe</h1><button type="button">Continue</button></main></body></html>');
  const result = await runAxeWithoutChrome147ContrastHang(page);
  expect(result.violations, JSON.stringify(result.violations, null, 2)).toEqual([]);
});

for (const screen of screens) {
  test(`axe scan: ${screen.role} ${screen.route}`, async ({ page }) => {
    await page.setExtraHTTPHeaders({ 'x-dev-role': screen.role, 'x-dev-user': screen.user });
    await page.goto(screen.route);
    await expect(page.getByRole('heading', { name: screen.marker })).toBeVisible();
    const result = await new AxeBuilder({ page })
      .include('main')
      .disableRules(AXE_RULES_UNAVAILABLE_IN_CHROME_147)
      .analyze();
    expect(result.violations, JSON.stringify(result.violations, null, 2)).toEqual([]);
  });
}
