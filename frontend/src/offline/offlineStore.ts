import type { ResourceAnnotations, ResourceProgress } from '../types';

export type SyncOpKind = 'progress' | 'favorite' | 'note-save' | 'note-delete';

export type SyncOp =
  | { id: string; kind: 'progress'; resourceId: string; createdAt: string; progress: ResourceProgress }
  | { id: string; kind: 'favorite'; resourceId: string; createdAt: string; favorite: boolean }
  | { id: string; kind: 'note-save'; resourceId: string; createdAt: string; page: number; text: string; baseVersion: number }
  | { id: string; kind: 'note-delete'; resourceId: string; createdAt: string; page: number; baseVersion: number };

export interface OfflineStore {
  getProgress(resourceId: string): Promise<ResourceProgress | null>;
  setProgress(progress: ResourceProgress): Promise<void>;
  getAnnotations(resourceId: string): Promise<ResourceAnnotations | null>;
  setAnnotations(annotations: ResourceAnnotations): Promise<void>;
  enqueue(op: SyncOp): Promise<void>;
  listOps(): Promise<SyncOp[]>;
  removeOps(ids: string[]): Promise<void>;
  subscribe(listener: () => void): () => void;
}

const DB_NAME = 'energygraph-offline';
const DB_VERSION = 1;
const PROGRESS_STORE = 'progress';
const ANNOTATIONS_STORE = 'annotations';
const OPS_STORE = 'ops';

function requestToPromise<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error('indexeddb request failed'));
  });
}

function openDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(PROGRESS_STORE)) db.createObjectStore(PROGRESS_STORE, { keyPath: 'resourceId' });
      if (!db.objectStoreNames.contains(ANNOTATIONS_STORE)) db.createObjectStore(ANNOTATIONS_STORE, { keyPath: 'resourceId' });
      if (!db.objectStoreNames.contains(OPS_STORE)) db.createObjectStore(OPS_STORE, { keyPath: 'id' });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error('indexeddb open failed'));
  });
}

function createIndexedDbStore(): OfflineStore {
  let dbPromise: Promise<IDBDatabase> | null = null;
  function db(): Promise<IDBDatabase> {
    if (!dbPromise) dbPromise = openDatabase();
    return dbPromise;
  }
  const listeners = new Set<() => void>();
  const emit = () => { for (const listener of listeners) listener(); };

  async function withStore<T>(name: string, mode: IDBTransactionMode, action: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
    const database = await db();
    return requestToPromise(action(database.transaction(name, mode).objectStore(name)));
  }

  return {
    async getProgress(resourceId: string): Promise<ResourceProgress | null> {
      try {
        return (await withStore(PROGRESS_STORE, 'readonly', (store) => store.get(resourceId))) as ResourceProgress | null;
      } catch { return null; }
    },
    async setProgress(progress: ResourceProgress): Promise<void> {
      try { await withStore(PROGRESS_STORE, 'readwrite', (store) => store.put(progress)); } catch { /* storage is best effort */ }
    },
    async getAnnotations(resourceId: string): Promise<ResourceAnnotations | null> {
      try {
        return (await withStore(ANNOTATIONS_STORE, 'readonly', (store) => store.get(resourceId))) as ResourceAnnotations | null;
      } catch { return null; }
    },
    async setAnnotations(annotations: ResourceAnnotations): Promise<void> {
      try { await withStore(ANNOTATIONS_STORE, 'readwrite', (store) => store.put(annotations)); } catch { /* storage is best effort */ }
    },
    async enqueue(op: SyncOp): Promise<void> {
      try { await withStore(OPS_STORE, 'readwrite', (store) => store.put(op)); } catch { /* storage is best effort */ }
      emit();
    },
    async listOps(): Promise<SyncOp[]> {
      try {
        const all = (await withStore(OPS_STORE, 'readonly', (store) => store.getAll())) as unknown as SyncOp[];
        return Array.isArray(all) ? all : [];
      } catch { return []; }
    },
    async removeOps(ids: string[]): Promise<void> {
      try {
        const database = await db();
        const transaction = database.transaction(OPS_STORE, 'readwrite');
        const store = transaction.objectStore(OPS_STORE);
        for (const id of ids) store.delete(id);
        await new Promise<void>((resolve, reject) => {
          transaction.oncomplete = () => resolve();
          transaction.onerror = () => reject(transaction.error ?? new Error('indexeddb transaction failed'));
        });
      } catch { /* storage is best effort */ }
      if (ids.length) emit();
    },
    subscribe(listener: () => void): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

function createMemoryStore(): OfflineStore {
  const progress = new Map<string, ResourceProgress>();
  const annotations = new Map<string, ResourceAnnotations>();
  const ops = new Map<string, SyncOp>();
  const listeners = new Set<() => void>();
  const emit = () => { for (const listener of listeners) listener(); };

  return {
    async getProgress(resourceId: string): Promise<ResourceProgress | null> {
      return progress.get(resourceId) ?? null;
    },
    async setProgress(value: ResourceProgress): Promise<void> {
      progress.set(value.resourceId, value);
    },
    async getAnnotations(resourceId: string): Promise<ResourceAnnotations | null> {
      return annotations.get(resourceId) ?? null;
    },
    async setAnnotations(value: ResourceAnnotations): Promise<void> {
      annotations.set(value.resourceId, value);
    },
    async enqueue(op: SyncOp): Promise<void> {
      ops.set(op.id, op);
      emit();
    },
    async listOps(): Promise<SyncOp[]> {
      return [...ops.values()];
    },
    async removeOps(ids: string[]): Promise<void> {
      for (const id of ids) ops.delete(id);
      if (ids.length) emit();
    },
    subscribe(listener: () => void): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

export function createMemoryOfflineStore(): OfflineStore {
  return createMemoryStore();
}

let singleton: OfflineStore | null = null;

export function getOfflineStore(): OfflineStore {
  if (!singleton) {
    singleton = typeof indexedDB === 'undefined' ? createMemoryStore() : createIndexedDbStore();
  }
  return singleton;
}

export function newSyncId(): string {
  return `offline-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}
