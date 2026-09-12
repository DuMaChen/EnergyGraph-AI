import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, '.', '');
    var apiTarget = env.VITE_API_PROXY_TARGET || 'http://localhost:8081';
    return {
        base: env.VITE_BASE_PATH || '/',
        plugins: [react()],
        server: {
            port: 4173,
            proxy: {
                '/api': {
                    target: apiTarget,
                    changeOrigin: true,
                    configure: function (proxy) {
                        // The production Caddy route is same-origin. During local
                        // browser tests, rewrite only the upstream Origin so the
                        // Adapter's CSRF guard still exercises its real rule.
                        proxy.on('proxyReq', function (request) { return request.setHeader('Origin', apiTarget); });
                    },
                },
            },
        },
        build: {
            target: 'es2022',
            sourcemap: false,
            rollupOptions: {
                output: {
                    manualChunks: {
                        'react-vendor': ['react', 'react-dom', 'react-router'],
                        'ui-vendor': ['lucide-react', 'zustand', 'zod'],
                    },
                },
            },
        },
    };
});
