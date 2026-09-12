import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  const apiTarget = env.VITE_API_PROXY_TARGET || 'http://localhost:8081';
  return {
    base: env.VITE_BASE_PATH || '/',
    plugins: [react()],
    server: {
      port: 4173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          configure: (proxy) => {
            // The production Caddy route is same-origin. During local
            // browser tests, rewrite only the upstream Origin so the
            // Adapter's CSRF guard still exercises its real rule.
            proxy.on('proxyReq', (request) => request.setHeader('Origin', apiTarget));
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
