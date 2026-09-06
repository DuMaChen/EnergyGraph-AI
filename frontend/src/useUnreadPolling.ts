import { useEffect, useRef, useState } from 'react';
import { loadNotifications } from './api/client';
import { useAppStore } from './state/app';
import { syncGlobalNotificationState } from './ui-helpers';

export const UNREAD_POLL_INTERVAL_MS = 60_000;

export function useUnreadNotificationPolling(intervalMs = UNREAD_POLL_INTERVAL_MS): string {
  const preview = useAppStore((state) => state.preview);
  const sessionExpired = useAppStore((state) => state.sessionExpired);
  const [announcement, setAnnouncement] = useState('');
  const lastCountRef = useRef<number | null>(null);

  useEffect(() => {
    if (preview || sessionExpired) return;
    let active = true;
    let timer: number | undefined;

    const poll = async () => {
      try {
        const result = await loadNotifications(false, 1, 1);
        if (!active) return;
        const previous = lastCountRef.current ?? useAppStore.getState().data?.unreadNotificationCount ?? 0;
        lastCountRef.current = result.unreadCount;
        syncGlobalNotificationState(result.unreadCount);
        if (result.unreadCount > previous) {
          const delta = result.unreadCount - previous;
          setAnnouncement(`您有 ${delta} 条新通知，当前共 ${result.unreadCount} 条未读。`);
        }
      } catch {
        // 静默失败：保留上次状态，下一轮重试
      }
    };

    const schedule = () => {
      window.clearInterval(timer);
      timer = window.setInterval(() => {
        if (document.visibilityState === 'visible') void poll();
      }, intervalMs);
    };
    schedule();
    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        void poll();
        schedule();
      }
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      active = false;
      window.clearInterval(timer);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [intervalMs, preview, sessionExpired]);

  return announcement;
}
