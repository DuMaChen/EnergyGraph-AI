import { getOfflineStore } from './offlineStore';

export const APP_SHELL_CACHE = 'energygraph-app-shell-v1';
export const STATIC_CACHE = 'energygraph-static-v1';
export const PDF_CACHE = 'energygraph-pdf-v1';

export function isPwaSupported(): boolean {
  if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) return false;
  if (typeof window === 'undefined' || !('caches' in window)) return false;
  return true;
}

export function shouldRegisterServiceWorker(): boolean {
  if (!import.meta.env.PROD) return false;
  if (!isPwaSupported()) return false;
  const params = new URLSearchParams(window.location.search);
  if (params.has('preview') || params.has('mock')) return false;
  return true;
}

export function watchServiceWorkerUpdates(registration: ServiceWorkerRegistration, onUpdateReady?: () => void): void {
  registration.addEventListener('updatefound', () => {
    const newWorker = registration.installing;
    if (!newWorker) return;
    newWorker.addEventListener('statechange', () => {
      if (newWorker.state === 'installed' && Boolean(navigator.serviceWorker?.controller)) {
        onUpdateReady?.();
      }
    });
  });
  void registration.update().catch(() => { /* update check is best effort */ });
}

export function registerServiceWorker(onUpdateReady?: () => void): void {
  if (!shouldRegisterServiceWorker()) return;
  window.addEventListener('load', () => {
    void navigator.serviceWorker
      .register(`${import.meta.env.BASE_URL}sw.js`, { scope: import.meta.env.BASE_URL })
      .then((registration) => { watchServiceWorkerUpdates(registration, onUpdateReady); })
      .catch(() => { /* offline-first is best effort */ });
  });
}

export async function cacheUrlForOffline(url: string): Promise<boolean> {
  if (!isPwaSupported() || !navigator.serviceWorker.controller) return false;
  navigator.serviceWorker.controller.postMessage({ type: 'CACHE_PDF', url });
  return true;
}

export async function isUrlCached(url: string): Promise<boolean> {
  try {
    if (typeof caches === 'undefined') return false;
    const cache = await caches.open(PDF_CACHE);
    const match = await cache.match(url);
    return Boolean(match);
  } catch { return false; }
}

export async function offlineStoreReady(): Promise<boolean> {
  try {
    await getOfflineStore().listOps();
    return true;
  } catch { return false; }
}
