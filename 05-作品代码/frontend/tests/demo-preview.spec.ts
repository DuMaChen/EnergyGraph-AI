import { expect, test, type Locator } from '@playwright/test';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const demoUrl = `${pathToFileURL(resolve(process.cwd(), '../agent-ui/index.html')).href}?preview=1`;

async function clickVisible(locator: Locator) {
  await expect(locator).toBeVisible();
  await locator.scrollIntoViewIfNeeded();
  await locator.click({ force: true });
}

test('preview desktop controls remain interactive', async ({ page }) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.goto(demoUrl);

  await expect(page.locator('a.auth-link-primary')).toHaveAttribute('href', '/login/index.php?wantsurl=%2Flearn%2F');
  await expect(page.locator('a.auth-link', { hasText: '注册账号' })).toHaveAttribute('href', '/login/signup.php');

  await clickVisible(page.locator('[data-view="course"]'));
  await expect(page.locator('#view-course')).toHaveClass(/active/);
  await clickVisible(page.locator('[data-course-tab="chapters"]'));
  await expect(page.locator('#courseTabChapters')).toBeVisible();

  await clickVisible(page.locator('[data-view="assistant"]'));
  await page.locator('#assistantQuestion').fill('储能变流器在并网控制中承担什么作用？');
  await clickVisible(page.locator('#assistantSubmit'));
  await expect(page.locator('#answerText')).toContainText('预览模式的示例回答');

  await clickVisible(page.locator('[data-scenario-key="grid-dispatch"]'));
  await expect(page.locator('#scenarioStatus')).toContainText('模拟数据');
  await clickVisible(page.locator('[data-view="home"]'));
  await clickVisible(page.locator('.row-action').first());
  await expect(page.locator('#detailDrawer')).toHaveClass(/open/);
  await page.waitForTimeout(250);
  await clickVisible(page.locator('#drawerClose'));
  await expect(page.locator('#detailDrawer')).not.toHaveClass(/open/);

  expect(pageErrors).toEqual([]);
});

test('preview mobile menu opens and closes', async ({ page }) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(demoUrl);

  await clickVisible(page.locator('#menuToggle'));
  await expect(page.locator('#sidebar')).toHaveClass(/open/);
  await expect(page.locator('#sidebarOverlay')).toHaveClass(/open/);
  await clickVisible(page.locator('#sidebarOverlay'));
  await expect(page.locator('#sidebar')).not.toHaveClass(/open/);
  await expect(page.locator('#sidebarOverlay')).not.toHaveClass(/open/);

  expect(pageErrors).toEqual([]);
});
