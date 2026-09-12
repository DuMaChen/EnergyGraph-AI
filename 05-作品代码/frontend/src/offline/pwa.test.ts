import { afterEach, describe, expect, it, vi } from 'vitest';
import { cacheUrlForOffline, isPwaSupported, isUrlCached, offlineStoreReady, registerServiceWorker, shouldRegisterServiceWorker, watchServiceWorkerUpdates } from './pwa';

function createFakeRegistration() {
  const listeners: Record<string, Set<EventListener>> = {};
  const workerListeners: Record<string, Set<EventListener>> = {};
  const worker = {
    state: 'installing',
    addEventListener: (type: string, listener: EventListener) => {
      (workerListeners[type] ??= new Set()).add(listener);
    },
  };
  const registration = {
    installing: worker,
    update: vi.fn(async () => undefined),
    addEventListener: (type: string, listener: EventListener) => {
      (listeners[type] ??= new Set()).add(listener);
    },
  };
  const triggerUpdateFound = () => listeners['updatefound']?.forEach((listener) => listener(new Event('updatefound')));
  const triggerWorkerStateChange = (state: string) => {
    worker.state = state;
    workerListeners['statechange']?.forEach((listener) => listener(new Event('statechange')));
  };
  return { registration, triggerUpdateFound, triggerWorkerStateChange };
}

function stubServiceWorkerController(controller: unknown): void {
  Object.defineProperty(navigator, 'serviceWorker', { configurable: true, value: { controller } });
}

describe('pwa helpers', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    if (Object.prototype.hasOwnProperty.call(navigator, 'serviceWorker')) {
      Reflect.deleteProperty(navigator, 'serviceWorker');
    }
  });

  it('reports unsupported in environments without service worker and cache APIs', () => {
    expect(isPwaSupported()).toBe(false);
  });

  it('never registers the service worker outside a production build', () => {
    expect(shouldRegisterServiceWorker()).toBe(false);
  });

  it('registerServiceWorker is a no-op when unsupported or non-production', () => {
    const addEventListener = vi.spyOn(window, 'addEventListener');
    registerServiceWorker();
    expect(addEventListener).not.toHaveBeenCalledWith('load', expect.any(Function));
  });

  it('cacheUrlForOffline returns false without a service worker controller', async () => {
    expect(await cacheUrlForOffline('/local/course_agent/guide.pdf')).toBe(false);
  });

  it('isUrlCached returns false when the Cache API is unavailable', async () => {
    expect(await isUrlCached('/local/course_agent/guide.pdf')).toBe(false);
  });

  it('offlineStoreReady resolves true using the in-memory fallback', async () => {
    expect(await offlineStoreReady()).toBe(true);
  });

  it('watchServiceWorkerUpdates triggers an update check on the registration', () => {
    const { registration } = createFakeRegistration();
    watchServiceWorkerUpdates(registration as unknown as ServiceWorkerRegistration);
    expect(registration.update).toHaveBeenCalledTimes(1);
  });

  it('notifies an update when a new worker becomes installed while a controller exists', () => {
    stubServiceWorkerController({});
    const { registration, triggerUpdateFound, triggerWorkerStateChange } = createFakeRegistration();
    const onUpdateReady = vi.fn();
    watchServiceWorkerUpdates(registration as unknown as ServiceWorkerRegistration, onUpdateReady);
    triggerUpdateFound();
    triggerWorkerStateChange('installing');
    expect(onUpdateReady).not.toHaveBeenCalled();
    triggerWorkerStateChange('installed');
    expect(onUpdateReady).toHaveBeenCalledTimes(1);
  });

  it('does not notify an update on first install without a controller', () => {
    stubServiceWorkerController(null);
    const { registration, triggerUpdateFound, triggerWorkerStateChange } = createFakeRegistration();
    const onUpdateReady = vi.fn();
    watchServiceWorkerUpdates(registration as unknown as ServiceWorkerRegistration, onUpdateReady);
    triggerUpdateFound();
    triggerWorkerStateChange('installed');
    expect(onUpdateReady).not.toHaveBeenCalled();
  });
});
