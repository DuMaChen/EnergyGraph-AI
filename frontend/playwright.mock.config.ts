import { defineConfig } from '@playwright/test';

const runId = `${process.pid}-${Date.now()}`;
const frontendPort = 4300;
const apiPort = 4301;

export default defineConfig({
  testDir: './tests',
  testMatch: '**/mock-api.spec.ts',
  timeout: 30_000,
  fullyParallel: true,
  reporter: 'line',
  use: {
    baseURL: `http://127.0.0.1:${frontendPort}/learn/`,
    browserName: 'chromium',
    launchOptions: {
      executablePath: '/usr/bin/google-chrome',
      args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
    },
  },
  webServer: [
    {
      command: `cd .. && env PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter MOCK_AUTH_MODE=true MOCK_WORKFLOW_MODE=true AGENT_UID_SALT=frontend-playwright-only COURSE_MANIFEST=$PWD/course-data/normalized/manifest.json GRAPH_BASELINE=$PWD/course-data/normalized/graph-baseline.json COURSE_DB=/tmp/energygraph-playwright-mock-${runId}.db RESOURCE_STORAGE_DIR=/tmp/energygraph-playwright-resource-files-${runId} python3 -m uvicorn app.main:app --host 127.0.0.1 --port ${apiPort}`,
      url: `http://127.0.0.1:${apiPort}/health`,
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: `VITE_BASE_PATH=/learn/ VITE_API_PROXY_TARGET=http://127.0.0.1:${apiPort} npm run dev -- --host 127.0.0.1 --port ${frontendPort}`,
      url: `http://127.0.0.1:${frontendPort}/learn/`,
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
