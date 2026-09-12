import { act, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useUnreadNotificationPolling } from './useUnreadPolling';
import { useAppStore } from './state/app';

function Harness({ intervalMs = 60_000 }: { intervalMs?: number }) {
  const announcement = useUnreadNotificationPolling(intervalMs);
  return <span role="status">{announcement}</span>;
}

function notificationsPayload(unreadCount: number) {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      status: 'ok',
      data: {
        items: [],
        unread_count: unreadCount,
        page: 1,
        page_size: 1,
        total: unreadCount,
        focus_found: false,
        focused_id: null,
      },
    }),
  } as Response;
}

function emptyData() {
  return {
    courses: [],
    chapters: [],
    resources: [],
    assignments: [],
    profile: [],
    recommendations: [],
    notifications: [],
    unreadNotificationCount: 0,
    studyHours: null,
  };
}

describe('useUnreadNotificationPolling', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    useAppStore.setState({ session: null, sessionExpired: false, data: emptyData(), preview: false, sidebarOpen: false });
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it('polls on interval, syncs store unread count and announces new notifications', async () => {
    let calls = 0;
    vi.stubGlobal('fetch', vi.fn(async () => {
      calls += 1;
      return notificationsPayload(calls === 1 ? 0 : 3);
    }));
    render(<Harness intervalMs={60_000} />);
    await act(async () => {
      vi.advanceTimersByTimeAsync(60_000);
    });
    expect(calls).toBe(1);
    expect(useAppStore.getState().data?.unreadNotificationCount).toBe(0);
    expect(screen.getByRole('status')).toHaveTextContent('');
    await act(async () => {
      vi.advanceTimersByTimeAsync(60_000);
    });
    expect(calls).toBe(2);
    expect(useAppStore.getState().data?.unreadNotificationCount).toBe(3);
    expect(screen.getByRole('status')).toHaveTextContent('您有 3 条新通知，当前共 3 条未读。');
  });

  it('does not announce when count decreases', async () => {
    useAppStore.setState({ data: { ...emptyData(), unreadNotificationCount: 5 } });
    vi.stubGlobal('fetch', vi.fn(async () => notificationsPayload(2)));
    render(<Harness />);
    await act(async () => {
      vi.advanceTimersByTimeAsync(60_000);
    });
    expect(useAppStore.getState().data?.unreadNotificationCount).toBe(2);
    expect(screen.getByRole('status')).toHaveTextContent('');
  });

  it('skips polling in preview mode', async () => {
    useAppStore.setState({ preview: true });
    const fetchMock = vi.fn(async () => notificationsPayload(1));
    vi.stubGlobal('fetch', fetchMock);
    render(<Harness />);
    await act(async () => {
      vi.advanceTimersByTimeAsync(180_000);
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('skips polling when session expired', async () => {
    useAppStore.setState({ sessionExpired: true });
    const fetchMock = vi.fn(async () => notificationsPayload(1));
    vi.stubGlobal('fetch', fetchMock);
    render(<Harness />);
    await act(async () => {
      vi.advanceTimersByTimeAsync(180_000);
    });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('clears the interval on unmount', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => notificationsPayload(0)));
    const view = render(<Harness />);
    view.unmount();
    expect(vi.getTimerCount()).toBe(0);
  });
});
