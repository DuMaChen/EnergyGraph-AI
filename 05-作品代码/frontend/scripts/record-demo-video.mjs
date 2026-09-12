import { chromium } from 'playwright';
import { execFileSync } from 'node:child_process';
import { mkdirSync, readdirSync } from 'node:fs';
import path from 'node:path';

const BASE = process.env.DEMO_BASE_URL || 'http://139.196.45.2';
const ROOT = path.resolve(import.meta.dirname, '..', '..');
const OUT_DIR = path.join(ROOT, '03-作品Demo');
const TMP_DIR = '/tmp/energygraph-demo-video';
mkdirSync(TMP_DIR, { recursive: true });
mkdirSync(OUT_DIR, { recursive: true });

const browser = await chromium.launch({
  executablePath: '/usr/bin/google-chrome',
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
});
const context = await browser.newContext({
  recordVideo: { dir: TMP_DIR, size: { width: 1280, height: 720 } },
});
const page = await context.newPage();
const pageErrors = [];
page.on('pageerror', (error) => pageErrors.push(error.message));

const clickVisible = async (locator) => {
  await locator.waitFor({ state: 'visible' });
  await locator.scrollIntoViewIfNeeded();
  await locator.click({ force: true });
};

console.log('[1/4] demo landing page');
await page.goto(`${BASE}/demo?preview=1`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
const courseBtn = page.locator('[data-view="course"]');
if (await courseBtn.count()) {
  await clickVisible(courseBtn);
  await page.locator('#view-course').waitFor({ state: 'visible' });
  await page.waitForTimeout(1200);
}
const assistantBtn = page.locator('[data-view="assistant"]');
if (await assistantBtn.count()) {
  await clickVisible(assistantBtn);
}
const input = page.locator('#assistantQuestion');
await input.waitFor({ state: 'visible', timeout: 15000 });
await input.fill('储能变流器在并网控制中承担什么作用？');
await page.waitForTimeout(800);
await clickVisible(page.locator('#assistantSubmit'));
await page.locator('#answerText').waitFor({ state: 'visible', timeout: 15000 });
await page.waitForTimeout(2500);

console.log('[2/4] SPA shell /learn/');
await page.goto(`${BASE}/learn/`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(2500);
const url = page.url();
if (url.includes('login')) {
  await page.locator('body').waitFor({ state: 'visible' });
} else {
  await page.getByRole('heading', { name: /林同学|学习空间/ }).waitFor({ state: 'visible', timeout: 20000 });
}
await page.waitForTimeout(1500);

console.log('[3/4] Moodle login entry');
await page.goto(`${BASE}/login/index.php`, { waitUntil: 'domcontentloaded' });
await page.locator('body').waitFor({ state: 'visible' });
await page.waitForTimeout(1500);

console.log('[4/4] mobile viewport /demo');
await page.setViewportSize({ width: 390, height: 844 });
await page.goto(`${BASE}/demo?preview=1`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(2500);

if (pageErrors.length) {
  console.error('PAGE_ERRORS', pageErrors);
  process.exitCode = 1;
}

await context.close();
await browser.close();

const webmFiles = readdirSync(TMP_DIR).filter((name) => name.endsWith('.webm'));
if (!webmFiles.length) {
  console.error('NO_VIDEO_RECORDED');
  process.exit(1);
}
const webm = path.join(TMP_DIR, webmFiles[0]);
const mp4 = path.join(OUT_DIR, 'demo-video.mp4');
execFileSync('ffmpeg', [
  '-y', '-i', webm,
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
  '-an', mp4,
], { stdio: 'inherit' });
console.log(`DEMO_VIDEO_OK ${mp4}`);
