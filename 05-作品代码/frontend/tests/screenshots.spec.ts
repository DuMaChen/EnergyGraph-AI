import fs from 'node:fs';
import path from 'node:path';

import { expect, test } from '@playwright/test';

const viewports = [
  { name: '390', width: 390, height: 844 },
  { name: '412', width: 412, height: 915 },
  { name: '768', width: 768, height: 1024 },
  { name: '1024', width: 1024, height: 900 },
  { name: '1280', width: 1280, height: 900 },
  { name: '1440', width: 1440, height: 900 },
] as const;

const screens = [
  { role: 'student', user: 'screenshot-student', route: '/', marker: '早上好，林同学', name: 'student-dashboard' },
  { role: 'teacher', user: 'screenshot-teacher', route: 'teacher/resources', marker: '课程资料管理', name: 'teacher-resources' },
  { role: 'admin', user: 'screenshot-admin', route: 'admin/knowledge-bases', marker: '平台运维与知识库', name: 'admin-knowledge-bases' },
] as const;

test('captures six local mock viewports for the key role workspaces', async ({ browser }) => {
  const outputDir = process.env.SCREENSHOT_OUTPUT_DIR
    ? path.resolve(process.env.SCREENSHOT_OUTPUT_DIR)
    : path.resolve(process.cwd(), '../acceptance/frontend/BUILD-070/screenshots');
  fs.mkdirSync(outputDir, { recursive: true });

  for (const screen of screens) {
    for (const viewport of viewports) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        extraHTTPHeaders: { 'x-dev-role': screen.role, 'x-dev-user': screen.user },
      });
      const page = await context.newPage();
      await page.goto(screen.route);
      await expect(page.getByRole('heading', { name: screen.marker })).toBeVisible();
      await expect(page.locator('body')).toHaveCSS('overflow-x', 'visible');
      await page.waitForTimeout(150);
      const cdp = await context.newCDPSession(page);
      const capture = await cdp.send('Page.captureScreenshot', { format: 'png', fromSurface: true });
      fs.writeFileSync(path.join(outputDir, `${screen.name}-${viewport.name}.png`), Buffer.from(capture.data, 'base64'));
      await context.close();
    }
  }
});
