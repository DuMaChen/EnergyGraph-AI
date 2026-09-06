import { expect, test } from '@playwright/test';

test('dashboard renders without horizontal overflow at target viewports', async ({ page }) => {
  for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    await page.goto('/');
    await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
    // The standard smoke may run with either an unavailable Adapter or an
    // already-running local Mock Adapter. The dedicated mock suite asserts
    // the authenticated/no-preview state explicitly.
    expect(await page.locator('.preview-banner').count()).toBeLessThanOrEqual(1);
    const metrics = await page.evaluate(() => ({
      documentWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
      navCount: document.querySelectorAll('nav a').length,
    }));
    expect(metrics.documentWidth).toBeLessThanOrEqual(metrics.viewportWidth + 1);
    expect(metrics.navCount).toBeGreaterThanOrEqual(5);
  }
});

test('global search, help and settings complete the shell workflow', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
  const userMenu = page.getByRole('button', { name: '打开用户菜单' });
  await expect(userMenu).toBeVisible();
  await userMenu.click({ force: true });
  await expect(page.getByRole('menuitem', { name: '学习设置' })).toBeVisible();

  await page.goto('search?q=储能变流器');
  await expect(page.getByRole('heading', { name: '搜索“储能变流器”' })).toBeVisible();
  await expect(page.locator('.search-result-row').filter({ hasText: '3.4 储能变流器拓扑及并网控制.pdf' })).toBeVisible();

  await page.goto('help');
  await expect(page.getByRole('heading', { name: '帮助中心' })).toBeVisible();
  await expect(page.getByRole('button', { name: /如何开始学习/ })).toBeVisible();

  await page.goto('settings');
  await expect(page.getByRole('heading', { name: '学习设置' })).toBeVisible();
  const notifications = page.getByRole('checkbox', { name: /课程通知提醒/ });
  await notifications.uncheck({ force: true });
  await expect(notifications).not.toBeChecked();
  await expect(page.getByText('设置已保存到本机。')).toBeVisible();

  await page.goto('/');
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
  await expect(userMenu).toBeVisible();
  await userMenu.click({ force: true });
  await page.getByRole('menuitem', { name: '退出课程' }).click({ force: true });
  if (page.url().includes('/login/logout.php')) {
    expect(page.url()).toMatch(/\/login\/logout\.php\?sesskey=.+/);
  } else {
    await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
  }
});
