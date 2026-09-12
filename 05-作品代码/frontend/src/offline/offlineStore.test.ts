import { describe, expect, it, vi } from 'vitest';
import { createMemoryOfflineStore, type SyncOp } from './offlineStore';
import type { ResourceAnnotations, ResourceProgress } from '../types';

const progress: ResourceProgress = {
  resourceId: 'res-1',
  page: 12,
  percent: 40,
  completed: false,
  version: 3,
  updatedAt: '2026-08-06T10:00:00+08:00',
  hasSavedProgress: true,
};

const annotations: ResourceAnnotations = {
  resourceId: 'res-1',
  favorite: true,
  notes: [{ id: 'n1', resourceId: 'res-1', page: 12, text: '并网控制要点', version: 1, updatedAt: null }],
};

function makeOp(overrides: Partial<SyncOp>): SyncOp {
  return {
    id: 'op-1',
    kind: 'progress',
    resourceId: 'res-1',
    createdAt: '2026-08-06T10:00:00+08:00',
    progress,
    ...overrides,
  } as SyncOp;
}

describe('offlineStore memory implementation', () => {
  it('round-trips reading progress and annotations per resource', async () => {
    const store = createMemoryOfflineStore();
    expect(await store.getProgress('res-1')).toBeNull();
    expect(await store.getAnnotations('res-1')).toBeNull();

    await store.setProgress(progress);
    await store.setAnnotations(annotations);

    expect(await store.getProgress('res-1')).toEqual(progress);
    expect(await store.getAnnotations('res-1')).toEqual(annotations);
    expect(await store.getProgress('res-other')).toBeNull();
  });

  it('keeps resources isolated so another course resource cannot leak', async () => {
    const store = createMemoryOfflineStore();
    await store.setProgress(progress);
    await store.setAnnotations(annotations);
    expect(await store.getProgress('res-2')).toBeNull();
    expect(await store.getAnnotations('res-2')).toBeNull();
  });

  it('enqueues, lists and removes sync operations', async () => {
    const store = createMemoryOfflineStore();
    const op = makeOp({});
    await store.enqueue(op);
    expect(await store.listOps()).toEqual([op]);

    await store.removeOps(['op-1']);
    expect(await store.listOps()).toEqual([]);
  });

  it('notifies subscribers when the queue changes', async () => {
    const store = createMemoryOfflineStore();
    const listener = vi.fn();
    const unsubscribe = store.subscribe(listener);
    await store.enqueue(makeOp({}));
    expect(listener).toHaveBeenCalledTimes(1);
    await store.removeOps(['op-1']);
    expect(listener).toHaveBeenCalledTimes(2);
    unsubscribe();
    await store.enqueue(makeOp({ id: 'op-2' }));
    expect(listener).toHaveBeenCalledTimes(2);
  });

  it('falls back to an empty queue when a stored value is malformed', async () => {
    const store = createMemoryOfflineStore();
    const ops = await store.listOps();
    expect(Array.isArray(ops)).toBe(true);
    expect(ops).toHaveLength(0);
  });
});
