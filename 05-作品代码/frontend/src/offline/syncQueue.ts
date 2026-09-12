import type { ResourceProgress } from '../types';
import {
  ApiError,
  deleteResourceNote as deleteNote,
  saveResourceFavorite as saveFavorite,
  saveResourceNote as saveNote,
  saveResourceProgress as saveProgress,
} from '../api/client';
import { newSyncId, type OfflineStore, type SyncOp } from './offlineStore';

export interface SyncApi {
  saveProgress(resourceId: string, progress: Pick<ResourceProgress, 'page' | 'percent' | 'completed'>, baseVersion: number, csrfToken: string, idempotencyKey: string): Promise<ResourceProgress>;
  saveFavorite(resourceId: string, favorite: boolean, csrfToken: string, idempotencyKey: string): Promise<{ resourceId: string; favorite: boolean }>;
  saveNote(resourceId: string, page: number, text: string, baseVersion: number, csrfToken: string, idempotencyKey: string): Promise<{ id: string; resourceId: string; page: number; text: string; version: number; updatedAt: string | null }>;
  deleteNote(resourceId: string, page: number, baseVersion: number, csrfToken: string, idempotencyKey: string): Promise<{ resourceId: string; page: number; deleted: boolean; version: number }>;
}

export const defaultSyncApi: SyncApi = {
  saveProgress,
  saveFavorite,
  saveNote,
  deleteNote,
};

function isNetworkFailure(error: unknown): boolean {
  return error instanceof TypeError || (error instanceof ApiError && error.code === 'network_error');
}

function opKey(op: SyncOp): string {
  if (op.kind === 'note-save' || op.kind === 'note-delete') return `${op.kind}:${op.resourceId}:${op.page}`;
  return `${op.kind}:${op.resourceId}`;
}

export async function enqueueProgress(store: OfflineStore, progress: ResourceProgress): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => op.kind === 'progress' && op.resourceId === progress.resourceId).map((op) => op.id));
  await store.enqueue({ id: newSyncId(), kind: 'progress', resourceId: progress.resourceId, createdAt: new Date().toISOString(), progress });
}

export async function enqueueFavorite(store: OfflineStore, resourceId: string, favorite: boolean): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => op.kind === 'favorite' && op.resourceId === resourceId).map((op) => op.id));
  await store.enqueue({ id: newSyncId(), kind: 'favorite', resourceId, createdAt: new Date().toISOString(), favorite });
}

export async function enqueueNoteSave(store: OfflineStore, resourceId: string, page: number, text: string, baseVersion: number): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => (op.kind === 'note-save' || op.kind === 'note-delete') && op.resourceId === resourceId && op.page === page).map((op) => op.id));
  await store.enqueue({ id: newSyncId(), kind: 'note-save', resourceId, createdAt: new Date().toISOString(), page, text, baseVersion });
}

export async function enqueueNoteDelete(store: OfflineStore, resourceId: string, page: number, baseVersion: number): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => (op.kind === 'note-save' || op.kind === 'note-delete') && op.resourceId === resourceId && op.page === page).map((op) => op.id));
  await store.enqueue({ id: newSyncId(), kind: 'note-delete', resourceId, createdAt: new Date().toISOString(), page, baseVersion });
}

export async function clearQueuedProgress(store: OfflineStore, resourceId: string): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => op.kind === 'progress' && op.resourceId === resourceId).map((op) => op.id));
}

export async function clearQueuedFavorite(store: OfflineStore, resourceId: string): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => op.kind === 'favorite' && op.resourceId === resourceId).map((op) => op.id));
}

export async function clearQueuedNote(store: OfflineStore, resourceId: string, page: number): Promise<void> {
  const ops = await store.listOps();
  await store.removeOps(ops.filter((op) => (op.kind === 'note-save' || op.kind === 'note-delete') && op.resourceId === resourceId && op.page === page).map((op) => op.id));
}

export async function pendingSyncCount(store: OfflineStore): Promise<number> {
  return (await store.listOps()).length;
}

export interface FlushResult {
  synced: number;
  dropped: number;
  stopped: boolean;
  remaining: number;
}

export async function flushSyncQueue(store: OfflineStore, api: SyncApi, csrfToken: string): Promise<FlushResult> {
  const ops = await store.listOps();
  if (!ops.length) return { synced: 0, dropped: 0, stopped: false, remaining: 0 };

  const latestByKey = new Map<string, SyncOp>();
  for (const op of [...ops].sort((a, b) => a.createdAt.localeCompare(b.createdAt))) {
    latestByKey.set(opKey(op), op);
  }
  const coalesced = [...latestByKey.values()].sort((a, b) => a.createdAt.localeCompare(b.createdAt));

  let synced = 0;
  let dropped = 0;
  let stopped = false;
  for (const op of coalesced) {
    const key = opKey(op);
    const idempotencyKey = `offline-sync:${op.id}`;
    try {
      if (op.kind === 'progress') {
        await api.saveProgress(op.resourceId, { page: op.progress.page, percent: op.progress.percent, completed: op.progress.completed }, op.progress.version, csrfToken, idempotencyKey);
      } else if (op.kind === 'favorite') {
        await api.saveFavorite(op.resourceId, op.favorite, csrfToken, idempotencyKey);
      } else if (op.kind === 'note-save') {
        await api.saveNote(op.resourceId, op.page, op.text, op.baseVersion, csrfToken, idempotencyKey);
      } else {
        await api.deleteNote(op.resourceId, op.page, op.baseVersion, csrfToken, idempotencyKey);
      }
      await store.removeOps(ops.filter((queued) => opKey(queued) === key).map((queued) => queued.id));
      synced += 1;
    } catch (error) {
      if (isNetworkFailure(error)) {
        stopped = true;
        break;
      }
      await store.removeOps(ops.filter((queued) => opKey(queued) === key).map((queued) => queued.id));
      dropped += 1;
    }
  }

  return { synced, dropped, stopped, remaining: (await store.listOps()).length };
}
