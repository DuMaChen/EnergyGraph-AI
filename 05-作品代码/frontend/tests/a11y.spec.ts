import { expect, test } from '@playwright/test';

test('visible controls have accessible names and mobile layout stays usable', async ({ page }) => {
  await page.goto('/');
  const unnamed = await page.locator('button, input, select, textarea, a').evaluateAll((elements) => elements
    .filter((element) => {
      const style = window.getComputedStyle(element);
      if (style.display === 'none' || style.visibility === 'hidden') return false;
      const html = element as HTMLInputElement;
      const label = html.getAttribute('aria-label') || html.getAttribute('title') || html.getAttribute('placeholder') || element.textContent?.trim();
      return !label;
    })
    .map((element) => element.outerHTML.slice(0, 160)));
  expect(unnamed).toEqual([]);

  await page.locator('body').focus();
  let focusable = false;
  for (let index = 0; index < 12 && !focusable; index += 1) {
    await page.keyboard.press('Tab');
    focusable = await page.evaluate(() => {
      const element = document.activeElement;
      return Boolean(element && element !== document.body && (element as HTMLElement).getBoundingClientRect().height > 0);
    });
  }
  expect(focusable).toBe(true);

  const contrastFailures = await page.locator('main *').evaluateAll((elements) => {
    const parse = (value: string): [number, number, number, number] | null => {
      const match = value.match(/rgba?\(([^)]+)\)/);
      if (!match) return null;
      const values = match[1].split(',').map((item) => Number.parseFloat(item.trim()));
      return values.length >= 3 && values.every((item) => !Number.isNaN(item)) ? [values[0], values[1], values[2], values.length > 3 ? values[3] : 1] : null;
    };
    const composite = (foreground: [number, number, number, number], background: [number, number, number, number]): [number, number, number, number] => {
      const alpha = foreground[3] + background[3] * (1 - foreground[3]);
      if (alpha === 0) return [0, 0, 0, 0];
      return [
        (foreground[0] * foreground[3] + background[0] * background[3] * (1 - foreground[3])) / alpha,
        (foreground[1] * foreground[3] + background[1] * background[3] * (1 - foreground[3])) / alpha,
        (foreground[2] * foreground[3] + background[2] * background[3] * (1 - foreground[3])) / alpha,
        alpha,
      ];
    };
    const luminance = (color: [number, number, number, number]) => color.slice(0, 3).reduce((sum, value, index) => {
      const normalized = value / 255;
      const channel = normalized <= 0.03928 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
      return sum + channel * [0.2126, 0.7152, 0.0722][index];
    }, 0);
    const ratio = (foreground: [number, number, number, number], background: [number, number, number, number]) => {
      const first = luminance(foreground);
      const second = luminance(background);
      return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
    };
    return elements.filter((element) => {
      const style = window.getComputedStyle(element);
      if (!(element.textContent || '').trim() || Array.from(element.children).some((child) => (child.textContent || '').trim())) return false;
      if (style.display === 'none' || style.visibility === 'hidden' || Number.parseFloat(style.opacity) === 0) return false;
      if (element.getBoundingClientRect().width === 0 || element.getBoundingClientRect().height === 0) return false;
      const foreground = parse(style.color);
      if (!foreground) return false;
      const layers: [number, number, number, number][] = [];
      let parent: Element | null = element;
      while (parent) {
        const candidate = parse(window.getComputedStyle(parent).backgroundColor);
        if (candidate && candidate[3] > 0) layers.unshift(candidate);
        parent = parent.parentElement;
      }
      const background = layers.reduce((current, layer) => composite(layer, current), [255, 255, 255, 1] as [number, number, number, number]);
      const visibleForeground = composite(foreground, background);
      const fontSize = Number.parseFloat(style.fontSize);
      const fontWeight = Number.parseInt(style.fontWeight, 10) || 400;
      const isLargeText = fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700);
      const minimum = isLargeText ? 3 : 4.5;
      return ratio(visibleForeground, background) < minimum;
    }).map((element) => element.textContent?.trim().slice(0, 80) || 'unknown');
  });
  expect(contrastFailures).toEqual([]);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: window.innerWidth }));
  expect(dimensions.width).toBeLessThanOrEqual(dimensions.viewport + 1);
});

test('empty and error states remain visible instead of looking successful', async ({ page }) => {
  await page.route('**/api/course/session/open', async (route) => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ status: 'error', data: null, error: { code: 'service_unavailable', message: '课程服务暂不可用' } }) }));
  await page.goto('/');
  await expect(page.getByText('当前为预览模式，展示示例课程数据；登录课程平台并完成接口配置后才会写入真实学习记录。')).toBeVisible();
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
});

test('knowledge graph search and node controls remain keyboard-addressable', async ({ page }) => {
  await page.goto('knowledge-graph');
  await expect(page.getByRole('heading', { name: '知识点与先修关系' })).toBeVisible();
  await expect(page.getByLabel('搜索知识点')).toBeVisible();
  await expect(page.getByLabel('筛选章节')).toBeVisible();
  const visibleButtons = await page.locator('main button:visible').evaluateAll((elements) => elements
    .filter((element) => !(element.getAttribute('aria-label') || element.getAttribute('title') || element.textContent?.trim()))
    .map((element) => element.outerHTML.slice(0, 160)));
  expect(visibleButtons).toEqual([]);
});

test('skip link, search shortcut and reduced-motion rules are wired', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');

  const skip = page.getByRole('link', { name: '跳到主内容' });
  await expect(skip).toHaveCount(1);
  await expect(skip).toHaveCSS('top', '-100px');

  await page.keyboard.press('Tab');
  await expect(skip).toBeFocused();
  await expect(skip).toHaveCSS('top', '12px');

  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();

  const search = page.getByLabel('搜索课程资料');
  await page.keyboard.press('/');
  await expect(search).toBeFocused();
  await search.fill('储能');
  await page.keyboard.press('Escape');
  await expect(search).not.toBeFocused();
  await expect(search).toHaveValue('');

  const reducedMotionActive = await page.evaluate(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  expect(reducedMotionActive).toBe(true);
  const hasReducedMotionRule = await page.evaluate(() => {
    for (const sheet of Array.from(document.styleSheets)) {
      try {
        for (const rule of Array.from(sheet.cssRules)) {
          if (rule instanceof CSSMediaRule && rule.conditionText.includes('prefers-reduced-motion')) return true;
        }
      } catch { /* cross-origin stylesheet is skipped */ }
    }
    return false;
  });
  expect(hasReducedMotionRule).toBe(true);
});

test('navigating updates the document title and moves focus to main content', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/学习工作台 · 储能学习空间/);

  await page.getByRole('link', { name: '我的课程' }).click();
  await expect(page).toHaveTitle(/我的课程 · 储能学习空间/);
  await expect(page.locator('#main-content')).toBeFocused();

  await page.getByRole('link', { name: '待办任务' }).click();
  await expect(page).toHaveTitle(/待办任务 · 储能学习空间/);
  await expect(page.locator('#main-content')).toBeFocused();
});

test('mobile sidebar drawer moves and restores focus', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');

  const trigger = page.getByRole('button', { name: '打开导航' });
  await expect(trigger).toBeVisible();
  await trigger.click();
  await expect(page.getByRole('button', { name: '关闭导航', exact: true })).toBeFocused();

  await page.keyboard.press('Escape');
  await expect(page.locator('.sidebar')).not.toHaveClass(/is-open/);
  await expect(trigger).toBeFocused();
});
