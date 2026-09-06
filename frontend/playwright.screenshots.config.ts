import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/screenshots.spec.ts',
  timeout: 60_000,
  fullyParallel: false,
  reporter: 'line',
  use: {
    baseURL: 'http://127.0.0.1:4175/learn/',
    browserName: 'chromium',
    launchOptions: {
      executablePath: '/usr/bin/google-chrome',
      args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
    },
  },
  webServer: [
    {
      command: 'cd .. && env PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter MOCK_AUTH_MODE=true MOCK_WORKFLOW_MODE=true AGENT_UID_SALT=frontend-playwright-screenshots COURSE_MANIFEST=$PWD/course-data/normalized/manifest.json GRAPH_BASELINE=$PWD/course-data/normalized/graph-baseline.json COURSE_DB=/tmp/energygraph-playwright-screenshots.db RESOURCE_STORAGE_DIR=/tmp/energygraph-playwright-screenshot-files python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8082',
      url: 'http://127.0.0.1:8082/health',
      reuseExistingServer: true,
      timeout: 30_000,
    },
    {
      command: 'VITE_BASE_PATH=/learn/ VITE_API_PROXY_TARGET=http://127.0.0.1:8082 npm run dev -- --host 127.0.0.1 --port 4175',
      url: 'http://127.0.0.1:4175/learn/',
      reuseExistingServer: true,
      timeout: 30_000,
    },
  ],
});
