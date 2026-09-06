import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useAppStore } from '../state/app';
import { OfflineBanner } from './OfflineBanner';
import { createMemoryOfflineStore, type OfflineStore } from './offlineStore';
import { enqueueProgress, type SyncApi } from './syncQueue';
import type { ResourceProgress } from '../types';

const progress: ResourceProgress = {
  resourceId: 'res-1',
  page: 12,
  percent: 40,
  completed: false,
  version: 3,
  updatedAt: '2026-08-06T10:00:00+08:00',
  hasSavedProgress: true,
};

function makeApi(): SyncApi {
  return {
    saveProgress: vi.fn(async () => ({ ...progress, version: progress.version + 1 })),
    saveFavorite: vi.fn(async () => ({ resourceId: 'res-1', favorite: true })),
    saveNote: vi.fn(async () => ({ id: 'n1', resourceId: 'res-1', page: 12, text: 'note', version: 1, updatedAt: null })),
    deleteNote: vi.fn(async () => ({ resourceId: 'res-1', page: 12, deleted: true, version: 2 })),
  };
}

function setOnline(value: boolean): void {
  Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => value });
  act(() => {
    window.dispatchEvent(new Event(value ? 'online' : 'offline'));
  });
}

async function flushAsyncWork(): Promise<void> {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
  });
}

describe('OfflineBanner', () => {
  let store: OfflineStore;
  let api: SyncApi;

  beforeEach(() => {
    store = createMemoryOfflineStore();
    api = makeApi();
    useAppStore.setState({
      session: { role: 'student', courseId: 1, csrfToken: 'csrf-test', features: {} },
      sessionExpired: false,
      data: null,
      preview: false,
      sidebarOpen: false,
    });
    setOnline(true);
  });

  afterEach(async () => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    await act(async () => {
      useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });
    });
  });

  it('renders nothing in preview mode even while offline', async () => {
    setOnline(false);
    useAppStore.setState({ preview: true });
    await act(async () => {
      render(<OfflineBanner store={store} api={api} />);
    });
    await flushAsyncWork();
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
  });

  it('shows the offline banner with pending count when offline', async () => {
    setOnline(false);
    await enqueueProgress(store, progress);
    await act(async () => {
      render(<OfflineBanner store={store} api={api} />);
    });
    await flushAsyncWork();
    const banner = await screen.findByRole('status');
    expect(banner).toHaveTextContent('当前离线');
    expect(banner).toHaveTextContent('进度、收藏和笔记会先保存在本机');
  });

  it('auto flushes pending changes when the connection is restored', async () => {
    setOnline(false);
    await enqueueProgress(store, progress);
    await act(async () => {
      render(<OfflineBanner store={store} api={api} />);
    });
    await flushAsyncWork();
    await screen.findByRole('status');

    setOnline(true);
    await flushAsyncWork();
    await waitFor(() => expect(api.saveProgress).toHaveBeenCalledTimes(1));
    expect(api.saveProgress).toHaveBeenCalledWith('res-1', { page: 12, percent: 40, completed: false }, 3, 'csrf-test', expect.stringMatching(/^offline-sync:offline-/));
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
  });

  it('shows a manual sync button and flushes on click', async () => {
    await enqueueProgress(store, progress);
    api.saveProgress = vi.fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce({ ...progress, version: progress.version + 1 });
    await act(async () => {
      render(<OfflineBanner store={store} api={api} />);
    });
    await flushAsyncWork();
    const banner = await screen.findByRole('status');
    expect(banner).toHaveTextContent('1 项离线修改待同步');

    fireEvent.click(screen.getByRole('button', { name: '立即同步' }));
    await flushAsyncWork();
    await waitFor(() => expect(api.saveProgress).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
  });
});
