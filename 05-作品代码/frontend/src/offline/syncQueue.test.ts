import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from '../api/client';
import type { ResourceProgress } from '../types';
import { createMemoryOfflineStore } from './offlineStore';
import { defaultSyncApi, enqueueFavorite, enqueueNoteDelete, enqueueNoteSave, enqueueProgress, flushSyncQueue, pendingSyncCount, type SyncApi } from './syncQueue';

const progress: ResourceProgress = {
  resourceId: 'res-1',
  page: 12,
  percent: 40,
  completed: false,
  version: 3,
  updatedAt: '2026-08-06T10:00:00+08:00',
  hasSavedProgress: true,
};

function makeApi(overrides: Partial<SyncApi> = {}): SyncApi {
  return {
    saveProgress: vi.fn(async () => ({ ...progress, version: progress.version + 1 })),
    saveFavorite: vi.fn(async () => ({ resourceId: 'res-1', favorite: true })),
    saveNote: vi.fn(async () => ({ id: 'n1', resourceId: 'res-1', page: 12, text: 'note', version: 1, updatedAt: null })),
    deleteNote: vi.fn(async () => ({ resourceId: 'res-1', page: 12, deleted: true, version: 2 })),
    ...overrides,
  };
}

function apiOk(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ status: 'ok', data }) } as Response;
}

describe('offline sync queue', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('enqueueProgress replaces an earlier queued progress for the same resource', async () => {
    const store = createMemoryOfflineStore();
    await enqueueProgress(store, { ...progress, page: 3 });
    await enqueueProgress(store, { ...progress, page: 7 });
    const ops = await store.listOps();
    expect(ops).toHaveLength(1);
    expect(ops[0].kind).toBe('progress');
    if (ops[0].kind === 'progress') expect(ops[0].progress.page).toBe(7);
  });

  it('enqueueNoteDelete replaces a queued note-save for the same page', async () => {
    const store = createMemoryOfflineStore();
    await enqueueNoteSave(store, 'res-1', 12, 'note text', 1);
    await enqueueNoteDelete(store, 'res-1', 12, 2);
    const ops = await store.listOps();
    expect(ops).toHaveLength(1);
    expect(ops[0].kind).toBe('note-delete');
  });

  it('enqueueFavorite keeps separate resources isolated', async () => {
    const store = createMemoryOfflineStore();
    await enqueueFavorite(store, 'res-1', true);
    await enqueueFavorite(store, 'res-2', false);
    expect(await pendingSyncCount(store)).toBe(2);
  });

  it('flush sends ops in chronological order with per-op idempotency keys', async () => {
    const store = createMemoryOfflineStore();
    const api = makeApi();
    await store.enqueue({ id: 'op-first', kind: 'favorite', resourceId: 'res-1', createdAt: '2026-08-06T09:00:00+08:00', favorite: true });
    await store.enqueue({ id: 'op-second', kind: 'progress', resourceId: 'res-1', createdAt: '2026-08-06T10:00:00+08:00', progress });
    await store.enqueue({ id: 'op-third', kind: 'note-save', resourceId: 'res-1', createdAt: '2026-08-06T11:00:00+08:00', page: 12, text: 'note', baseVersion: 1 });

    const result = await flushSyncQueue(store, api, 'csrf-test');

    expect(result).toEqual({ synced: 3, dropped: 0, stopped: false, remaining: 0 });
    expect(api.saveFavorite).toHaveBeenCalledWith('res-1', true, 'csrf-test', 'offline-sync:op-first');
    expect(api.saveProgress).toHaveBeenCalledWith('res-1', { page: 12, percent: 40, completed: false }, 3, 'csrf-test', 'offline-sync:op-second');
    expect(api.saveNote).toHaveBeenCalledWith('res-1', 12, 'note', 1, 'csrf-test', 'offline-sync:op-third');
  });

  it('flush coalesces duplicate keys keeping only the latest op', async () => {
    const store = createMemoryOfflineStore();
    const api = makeApi();
    await store.enqueue({ id: 'op-old', kind: 'progress', resourceId: 'res-1', createdAt: '2026-08-06T09:00:00+08:00', progress: { ...progress, page: 2, version: 2 } });
    await store.enqueue({ id: 'op-new', kind: 'progress', resourceId: 'res-1', createdAt: '2026-08-06T10:00:00+08:00', progress: { ...progress, page: 9, version: 4 } });
    await store.enqueue({ id: 'op-note-save', kind: 'note-save', resourceId: 'res-1', createdAt: '2026-08-06T10:30:00+08:00', page: 12, text: 'old', baseVersion: 1 });
    await store.enqueue({ id: 'op-note-delete', kind: 'note-delete', resourceId: 'res-1', createdAt: '2026-08-06T11:00:00+08:00', page: 12, baseVersion: 1 });

    const result = await flushSyncQueue(store, api, 'csrf-test');

    expect(result).toEqual({ synced: 3, dropped: 0, stopped: false, remaining: 0 });
    expect(api.saveProgress).toHaveBeenCalledTimes(1);
    const saveProgressMock = vi.mocked(api.saveProgress);
    expect(saveProgressMock.mock.calls[0][1]).toEqual({ page: 9, percent: 40, completed: false });
    expect(api.saveNote).toHaveBeenCalledTimes(1);
    expect(api.saveNote).toHaveBeenCalledWith('res-1', 12, 'old', 1, 'csrf-test', 'offline-sync:op-note-save');
    expect(api.deleteNote).toHaveBeenCalledTimes(1);
    expect(api.deleteNote).toHaveBeenCalledWith('res-1', 12, 1, 'csrf-test', 'offline-sync:op-note-delete');
  });

  it('stops on network failure and keeps remaining ops queued', async () => {
    const store = createMemoryOfflineStore();
    const api = makeApi({
      saveProgress: vi.fn(async () => { throw new TypeError('Failed to fetch'); }),
    });
    await store.enqueue({ id: 'op-a', kind: 'progress', resourceId: 'res-1', createdAt: '2026-08-06T09:00:00+08:00', progress });
    await store.enqueue({ id: 'op-b', kind: 'favorite', resourceId: 'res-1', createdAt: '2026-08-06T10:00:00+08:00', favorite: true });

    const result = await flushSyncQueue(store, api, 'csrf-test');

    expect(result).toEqual({ synced: 0, dropped: 0, stopped: true, remaining: 2 });
    expect(api.saveFavorite).not.toHaveBeenCalled();
  });

  it('drops conflicting ops and keeps flushing the rest', async () => {
    const store = createMemoryOfflineStore();
    const api = makeApi({
      saveProgress: vi.fn(async () => { throw new ApiError('版本冲突', 'version_conflict'); }),
    });
    await store.enqueue({ id: 'op-a', kind: 'progress', resourceId: 'res-1', createdAt: '2026-08-06T09:00:00+08:00', progress });
    await store.enqueue({ id: 'op-b', kind: 'favorite', resourceId: 'res-1', createdAt: '2026-08-06T10:00:00+08:00', favorite: true });

    const result = await flushSyncQueue(store, api, 'csrf-test');

    expect(result).toEqual({ synced: 1, dropped: 1, stopped: false, remaining: 0 });
    expect(api.saveFavorite).toHaveBeenCalledTimes(1);
  });

  it('returns immediately for an empty queue', async () => {
    const store = createMemoryOfflineStore();
    const api = makeApi();
    expect(await flushSyncQueue(store, api, 'csrf-test')).toEqual({ synced: 0, dropped: 0, stopped: false, remaining: 0 });
    expect(api.saveProgress).not.toHaveBeenCalled();
  });

  describe('defaultSyncApi', () => {
    it('saveProgress sends PUT with idempotency key, session key and base version', async () => {
      const fetchMock = vi.fn(async (_url: string, _init: RequestInit) => apiOk({ resource_id: 'res-1', page: 5, percent: 20, completed: false, version: 4, updated_at: '2026-08-06T12:00:00+08:00', has_saved_progress: true }));
      vi.stubGlobal('fetch', fetchMock);
      const result = await defaultSyncApi.saveProgress('res-1', { page: 5, percent: 20, completed: false }, 3, 'csrf-test', 'offline-sync:op-1');
      expect(result).toMatchObject({ resourceId: 'res-1', page: 5, percent: 20, version: 4, hasSavedProgress: true });
      const [url, init] = fetchMock.mock.calls[0];
      expect(url).toBe('/api/student/resources/res-1/progress');
      expect(init.method).toBe('PUT');
      expect((init.headers as Record<string, string>)['Idempotency-Key']).toBe('offline-sync:op-1');
      expect((init.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-test');
      expect(JSON.parse(init.body as string)).toEqual({ page: 5, percent: 20, completed: false, base_version: 3 });
    });

    it('saveFavorite sends PUT with the favorite flag', async () => {
      const fetchMock = vi.fn(async (_url: string, _init: RequestInit) => apiOk({ resource_id: 'res-1', favorite: true }));
      vi.stubGlobal('fetch', fetchMock);
      const result = await defaultSyncApi.saveFavorite('res-1', true, 'csrf-test', 'offline-sync:op-2');
      expect(result).toEqual({ resourceId: 'res-1', favorite: true });
      const [url, init] = fetchMock.mock.calls[0];
      expect(url).toBe('/api/student/resources/res-1/favorite');
      expect(init.method).toBe('PUT');
      expect((init.headers as Record<string, string>)['Idempotency-Key']).toBe('offline-sync:op-2');
      expect(JSON.parse(init.body as string)).toEqual({ favorite: true });
    });

    it('saveNote sends PUT to the page endpoint with text and base version', async () => {
      const fetchMock = vi.fn(async (_url: string, _init: RequestInit) => apiOk({ id: 'n1', resource_id: 'res-1', page: 12, text: '离线笔记', version: 1, updated_at: null }));
      vi.stubGlobal('fetch', fetchMock);
      const result = await defaultSyncApi.saveNote('res-1', 12, '离线笔记', 1, 'csrf-test', 'offline-sync:op-3');
      expect(result).toMatchObject({ id: 'n1', resourceId: 'res-1', page: 12, text: '离线笔记', version: 1 });
      const [url, init] = fetchMock.mock.calls[0];
      expect(url).toBe('/api/student/resources/res-1/notes/12');
      expect(init.method).toBe('PUT');
      expect(JSON.parse(init.body as string)).toEqual({ text: '离线笔记', base_version: 1 });
    });

    it('deleteNote sends DELETE with base version', async () => {
      const fetchMock = vi.fn(async (_url: string, _init: RequestInit) => apiOk({ resource_id: 'res-1', page: 12, deleted: true, version: 2 }));
      vi.stubGlobal('fetch', fetchMock);
      const result = await defaultSyncApi.deleteNote('res-1', 12, 2, 'csrf-test', 'offline-sync:op-4');
      expect(result).toMatchObject({ resourceId: 'res-1', page: 12, deleted: true, version: 2 });
      const [url, init] = fetchMock.mock.calls[0];
      expect(url).toBe('/api/student/resources/res-1/notes/12');
      expect(init.method).toBe('DELETE');
      expect(JSON.parse(init.body as string)).toEqual({ base_version: 2 });
    });
  });
});
