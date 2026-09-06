import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  fullyParallel: false,
  reporter: [['line'], ['html', { open: 'never', outputFolder: '/tmp/pw-public/report' }]],
  use: {
    baseURL: 'http://139.196.45.2',
    browserName: 'chromium',
    launchOptions: {
      executablePath: '/usr/bin/google-chrome',
      args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
    },
    screenshot: 'only-on-failure',
  },
});
