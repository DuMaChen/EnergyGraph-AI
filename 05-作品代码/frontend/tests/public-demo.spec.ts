import { expect, test, type Locator } from '@playwright/test';

const BASE = 'http://139.196.45.2';

async function clickVisible(locator: Locator) {
  await expect(locator).toBeVisible();
  await locator.scrollIntoViewIfNeeded();
  await locator.click({ force: true });
}

test('public demo page loads and interactive controls work', async ({ page }) => {
  test.setTimeout(120_000);
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  await page.goto(`${BASE}/demo?preview=1`, { waitUntil: 'domcontentloaded' });

  const title = await page.title();
  expect(title.length).toBeGreaterThan(0);
  expect(await page.locator('body').innerText()).toContain('储能');

  const courseBtn = page.locator('[data-view="course"]');
  if (await courseBtn.count()) {
    await clickVisible(courseBtn);
    await expect(page.locator('#view-course')).toHaveClass(/active/);
  }

  const assistantBtn = page.locator('[data-view="assistant"]');
  if (await assistantBtn.count()) {
    await clickVisible(assistantBtn);
  }
  const input = page.locator('#assistantQuestion');
  await expect(input).toBeVisible({ timeout: 15_000 });
  await input.fill('储能变流器在并网控制中承担什么作用？');
  const submit = page.locator('#assistantSubmit');
  await clickVisible(submit);
  await expect(page.locator('#answerText')).toContainText('示例回答', { timeout: 15_000 });

  expect(pageErrors).toEqual([]);
});

test('public learn route serves the app shell', async ({ page }) => {
  test.setTimeout(90_000);
  await page.goto(`${BASE}/learn/`, { waitUntil: 'domcontentloaded' });
  const url = page.url();
  if (url.includes('login')) {
    // Unauthenticated: Moodle login redirect is correct behaviour.
    await expect(page.locator('body')).toContainText('登录', { timeout: 15_000 });
  } else {
    // SPA shell hydrates a few seconds after load.
    await expect(page.getByRole('heading', { name: /林同学|学习空间/ })).toBeVisible({ timeout: 20_000 });
    const metrics = await page.evaluate(() => ({
      documentWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      navCount: document.querySelectorAll('nav a').length,
    }));
    expect(metrics.documentWidth).toBeLessThanOrEqual(metrics.viewportWidth + 1);
    expect(metrics.navCount).toBeGreaterThanOrEqual(5);
  }
});

test('public demo mobile viewport renders without horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${BASE}/demo?preview=1`, { waitUntil: 'domcontentloaded' });
  const metrics = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: window.innerWidth,
  }));
  expect(metrics.documentWidth).toBeLessThanOrEqual(metrics.viewportWidth + 1);
});
