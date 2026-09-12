/* EnergyGraph PWA service worker (offline-first reading support).
 *
 * Cache policy:
 * - API requests (/api/...) are NEVER cached: they carry session/identity
 *   data and must stay network-only.
 * - App shell navigations are network-first with a cached index.html
 *   fallback so the SPA still opens offline.
 * - Static assets (js/css/fonts/images) are cache-first with runtime
 *   population so a previously visited build works offline.
 * - PDF locator requests (/local/course_agent/..., *.pdf) are cache-first:
 *   pages opened online become readable offline.
 */

const VERSION = 'v1';
const APP_SHELL_CACHE = `energygraph-app-shell-${VERSION}`;
const STATIC_CACHE = `energygraph-static-${VERSION}`;
const PDF_CACHE = `energygraph-pdf-${VERSION}`;
const CACHE_PREFIXES = ['energygraph-app-shell-', 'energygraph-static-', 'energygraph-pdf-'];

const STATIC_EXTENSIONS = /\.(?:js|css|woff2?|png|svg|jpg|jpeg|gif|webp|ico)$/i;

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(APP_SHELL_CACHE);
    const base = self.registration.scope;
    await cache.add(base).catch(() => {});
    await cache.add(new URL('index.html', base).href).catch(() => {});
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((key) => CACHE_PREFIXES.some((prefix) => key.startsWith(prefix)) && !key.endsWith(VERSION))
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

function isApiRequest(url) {
  return url.pathname.includes('/api/');
}

function isPdfRequest(url) {
  return url.pathname.includes('/local/course_agent/') || /\.pdf$/i.test(url.pathname);
}

function isStaticAsset(url) {
  return STATIC_EXTENSIONS.test(url.pathname);
}

function sameOrigin(url) {
  return url.origin === self.location.origin;
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok && response.type === 'basic') {
    await cache.put(request, response.clone());
  }
  return response;
}

async function networkFirstNavigation(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(APP_SHELL_CACHE);
      await cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cache = await caches.open(APP_SHELL_CACHE);
    const base = self.registration.scope;
    return (await cache.match(request))
      || (await cache.match(new URL('index.html', base).href))
      || (await cache.match(base));
  }
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (!sameOrigin(url)) return;
  if (isApiRequest(url)) return;

  if (request.mode === 'navigate') {
    event.respondWith(networkFirstNavigation(request));
    return;
  }
  if (isPdfRequest(url)) {
    event.respondWith(cacheFirst(request, PDF_CACHE));
    return;
  }
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  }
});

self.addEventListener('message', (event) => {
  if (!event.data || event.data.type !== 'CACHE_PDF' || typeof event.data.url !== 'string') return;
  event.waitUntil((async () => {
    try {
      const url = new URL(event.data.url, self.location.origin);
      if (!sameOrigin(url) || isApiRequest(url)) return;
      const cache = await caches.open(PDF_CACHE);
      const response = await fetch(url);
      if (response.ok && response.type === 'basic') {
        await cache.put(url, response);
      }
    } catch { /* offline caching is best effort */ }
  })());
});
