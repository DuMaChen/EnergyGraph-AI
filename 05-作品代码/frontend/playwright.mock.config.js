import { defineConfig } from '@playwright/test';
var runId = "".concat(process.pid, "-").concat(Date.now());
var frontendPort = 4300;
var apiPort = 4301;
export default defineConfig({
    testDir: './tests',
    testMatch: '**/mock-api.spec.ts',
    timeout: 30000,
    fullyParallel: true,
    reporter: 'line',
    use: {
        baseURL: "http://127.0.0.1:".concat(frontendPort, "/learn/"),
        browserName: 'chromium',
        launchOptions: {
            executablePath: '/usr/bin/google-chrome',
            args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'],
        },
    },
    webServer: [
        {
            command: "cd .. && env PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter MOCK_AUTH_MODE=true MOCK_WORKFLOW_MODE=true AGENT_UID_SALT=frontend-playwright-only COURSE_MANIFEST=$PWD/course-data/normalized/manifest.json GRAPH_BASELINE=$PWD/course-data/normalized/graph-baseline.json COURSE_DB=/tmp/energygraph-playwright-mock-".concat(runId, ".db RESOURCE_STORAGE_DIR=/tmp/energygraph-playwright-resource-files-").concat(runId, " python3 -m uvicorn app.main:app --host 127.0.0.1 --port ").concat(apiPort),
            url: "http://127.0.0.1:".concat(apiPort, "/health"),
            reuseExistingServer: false,
            timeout: 30000,
        },
        {
            command: "VITE_BASE_PATH=/learn/ VITE_API_PROXY_TARGET=http://127.0.0.1:".concat(apiPort, " npm run dev -- --host 127.0.0.1 --port ").concat(frontendPort),
            url: "http://127.0.0.1:".concat(frontendPort, "/learn/"),
            reuseExistingServer: false,
            timeout: 30000,
        },
    ],
});
