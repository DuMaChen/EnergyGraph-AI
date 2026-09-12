import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/smoke.spec.ts',
  timeout: 30_000,
  fullyParallel: true,
  reporter: 'line',
  use: {
    baseURL: 'http://127.0.0.1:4193/learn/',
    browserName: 'chromium',
    launchOptions: {
      executablePath: '/usr/bin/google-chrome',
      args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
    },
  },
  webServer: {
    command: 'VITE_BASE_PATH=/learn/ npm run dev -- --host 127.0.0.1 --port 4193',
    url: 'http://127.0.0.1:4193/learn/',
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
