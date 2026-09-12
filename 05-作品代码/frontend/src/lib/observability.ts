export type ClientErrorContext = 'render' | 'network' | 'stream' | 'unknown';

export interface ClientErrorRecord {
  id: string;
  context: ClientErrorContext;
  category: 'api' | 'network' | 'render' | 'unknown';
  route: string;
  timestamp: string;
}

const STORAGE_KEY = 'energygraph:client-errors';
const MAX_RECORDS = 20;

function errorCategory(error: unknown, context: ClientErrorContext): ClientErrorRecord['category'] {
  if (context === 'render') return 'render';
  if (error instanceof TypeError) return 'network';
  if (error instanceof Error && error.name === 'ApiError') return 'api';
  return context === 'network' || context === 'stream' ? 'network' : 'unknown';
}

function newErrorId(): string {
  const randomId = globalThis.crypto?.randomUUID?.();
  return randomId || `ui-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

/** Keep diagnostics useful without persisting exception messages or request data. */
export function reportClientError(error: unknown, context: ClientErrorContext): ClientErrorRecord {
  const record: ClientErrorRecord = {
    id: newErrorId(),
    context,
    category: errorCategory(error, context),
    route: typeof window === 'undefined' ? '/' : window.location.pathname,
    timestamp: new Date().toISOString(),
  };

  if (typeof window !== 'undefined') {
    try {
      const existing = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]') as unknown;
      const records = Array.isArray(existing) ? existing.filter((item): item is ClientErrorRecord => Boolean(item && typeof item === 'object')) : [];
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...records, record].slice(-MAX_RECORDS)));
    } catch {
      // Diagnostics must never break the recovery UI when storage is blocked.
    }
    window.dispatchEvent(new CustomEvent('platform:error', { detail: record }));
  }
  return record;
}

export function readClientErrorRecords(): ClientErrorRecord[] {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]') as unknown;
    return Array.isArray(parsed) ? parsed as ClientErrorRecord[] : [];
  } catch {
    return [];
  }
}
