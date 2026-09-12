import { useCallback, useEffect, useRef, useState } from 'react';
import { WifiOff, RefreshCw, CloudUpload } from 'lucide-react';
import { useAppStore } from '../state/app';
import { defaultSyncApi, flushSyncQueue, pendingSyncCount, type SyncApi } from './syncQueue';
import { getOfflineStore, type OfflineStore } from './offlineStore';
import { useOnlineStatus } from './useOnlineStatus';

interface OfflineBannerProps {
  store?: OfflineStore;
  api?: SyncApi;
}

export function OfflineBanner({ store = getOfflineStore(), api = defaultSyncApi }: OfflineBannerProps) {
  const online = useOnlineStatus();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const hasSession = useAppStore((state) => Boolean(state.session));
  const [pending, setPending] = useState(0);
  const [flushing, setFlushing] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);
  const flushStartedRef = useRef(false);
  const syncAttemptedRef = useRef(false);

  useEffect(() => {
    let active = true;
    const refresh = async () => {
      const count = await pendingSyncCount(store);
      if (active) setPending(count);
    };
    void refresh();
    const unsubscribe = store.subscribe(() => { void refresh(); });
    return () => { active = false; unsubscribe(); };
  }, [store]);

  const flush = useCallback(async () => {
    if (!online || flushing || preview || !hasSession || csrfToken === '') return;
    setFlushing(true);
    try {
      const result = await flushSyncQueue(store, api, csrfToken);
      if (result.stopped) setLastResult('网络仍不可用，修改已保留在本机。');
      else if (result.dropped > 0) setLastResult(`已同步 ${result.synced} 项，${result.dropped} 项因服务端更新被丢弃。`);
      else if (result.synced > 0) setLastResult(`已同步 ${result.synced} 项离线修改。`);
      else setLastResult('没有待同步的修改。');
    } catch {
      setLastResult('同步失败，修改仍保留在本机。');
    } finally {
      setFlushing(false);
    }
  }, [api, csrfToken, flushing, hasSession, online, preview, store]);

  useEffect(() => {
    if (!online) {
      syncAttemptedRef.current = false;
      return;
    }
    if (!syncAttemptedRef.current && hasSession && !preview && pending > 0 && !flushStartedRef.current) {
      syncAttemptedRef.current = true;
      flushStartedRef.current = true;
      void flush().finally(() => { flushStartedRef.current = false; });
    }
  }, [flush, hasSession, online, pending, preview]);

  if (preview || (online && pending === 0)) return null;

  const offline = !online;
  return (
    <div className={`offline-banner ${offline ? 'is-offline' : 'is-syncing'}`} role="status" aria-live="polite">
      <span className="offline-banner-icon">{offline ? <WifiOff size={16} /> : <CloudUpload size={16} />}</span>
      <span className="offline-banner-copy">
        {offline
          ? <><strong>当前离线</strong><small>进度、收藏和笔记会先保存在本机，恢复网络后自动同步。</small></>
          : <><strong>{pending} 项离线修改待同步</strong><small>{lastResult || '恢复网络后会自动同步到课程平台。'}</small></>}
      </span>
      {!offline && pending > 0 && (
        <button className="button quiet offline-banner-action" onClick={() => void flush()} disabled={flushing}>
          <RefreshCw size={14} className={flushing ? 'spin' : ''} />{flushing ? '同步中…' : '立即同步'}
        </button>
      )}
    </div>
  );
}
