import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/a11y.spec.ts',
  timeout: 30_000,
  fullyParallel: true,
  reporter: 'line',
  use: {
    baseURL: 'http://127.0.0.1:4194/learn/',
    browserName: 'chromium',
    launchOptions: {
      executablePath: '/usr/bin/google-chrome',
      args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
    },
  },
  webServer: {
    command: 'VITE_BASE_PATH=/learn/ npm run dev -- --host 127.0.0.1 --port 4194',
    url: 'http://127.0.0.1:4194/learn/',
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
