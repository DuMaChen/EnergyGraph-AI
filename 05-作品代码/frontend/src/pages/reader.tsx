/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ArrowLeft, Bot, CheckCircle2, ChevronRight, Download, FileText, Minus, Plus, RefreshCw, Star, Trash2 } from 'lucide-react';
import { ApiError, deleteResourceNote, loadResource, loadResourceAnnotations, loadResourceProgress, saveResourceFavorite, saveResourceNote, saveResourceProgress } from '../api/client';
import { PageHead } from '../ui';
import { Resource, ResourceAnnotations, ResourceProgress } from '../types';
import { cacheUrlForOffline, isPwaSupported, isUrlCached } from '../offline/pwa';
import { clearQueuedFavorite, clearQueuedNote, clearQueuedProgress, enqueueFavorite, enqueueNoteDelete, enqueueNoteSave, enqueueProgress } from '../offline/syncQueue';
import { getOfflineStore } from '../offline/offlineStore';
import { useAppStore } from '../state/app';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router';
import { usePlatformData } from '../appData';

function readCachedResourceProgress(resourceId: string): ResourceProgress | null {
  try {
    const raw = window.localStorage.getItem(`resource-progress:${resourceId}`);
    return raw ? JSON.parse(raw) as ResourceProgress : null;
  } catch { return null; }
}

export function ResourceReaderPage() {
  const { resourceId = '' } = useParams();
  const navigate = useNavigate();
  const [readerSearchParams] = useSearchParams();
  const data = usePlatformData();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [resource, setResource] = useState<Resource | null>(null);
  const [progress, setProgress] = useState<ResourceProgress | null>(null);
  const [annotations, setAnnotations] = useState<ResourceAnnotations>({ resourceId, favorite: false, notes: [] });
  const [noteDraft, setNoteDraft] = useState('');
  const [annotationState, setAnnotationState] = useState<'idle' | 'saving' | 'saved' | 'error' | 'conflict'>('idle');
  const [annotationMessage, setAnnotationMessage] = useState('');
  const [page, setPage] = useState(1);
  const [readerState, setReaderState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'offline' | 'conflict' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const saveTimer = useRef<number | null>(null);
  const [offlineCached, setOfflineCached] = useState(false);
  const requestedPage = Number(readerSearchParams.get('page') || 0);

  useEffect(() => {
    let active = true;
    setReaderState('loading');
    setResource(null);
    setProgress(null);
    setAnnotations({ resourceId, favorite: false, notes: [] });
    setNoteDraft('');
    setAnnotationState('idle');
    setAnnotationMessage('');
    setErrorMessage('');
    async function load() {
      if (preview) {
        const item = data.resources.find((candidate) => candidate.id === resourceId);
        if (!item) {
          if (active) { setErrorMessage('资料不存在或已从课程中移除。'); setReaderState('error'); }
          return;
        }
        const initial: ResourceProgress = { resourceId: item.id, page: item.pageStart, percent: 0, completed: false, version: 0, updatedAt: null, hasSavedProgress: false };
        const startPage = requestedPage >= item.pageStart && requestedPage <= item.pageCount ? requestedPage : initial.page;
        if (active) { setResource(item); setProgress(initial); setPage(startPage); setAnnotations({ resourceId: item.id, favorite: false, notes: [] }); setReaderState('ready'); }
        return;
      }
      try {
        const [opened, saved] = await Promise.all([loadResource(resourceId), loadResourceProgress(resourceId)]);
        if (!active) return;
        const merged = { ...saved.resource, ...opened.resource, locator: opened.locator };
        let loadedAnnotations: ResourceAnnotations = { resourceId, favorite: false, notes: [] };
        try { loadedAnnotations = await loadResourceAnnotations(resourceId); }
        catch { loadedAnnotations = (await getOfflineStore().getAnnotations(resourceId)) ?? { resourceId, favorite: false, notes: [] }; }
        const cached = readCachedResourceProgress(resourceId) ?? (await getOfflineStore().getProgress(resourceId));
        const initialProgress = cached && cached.version >= saved.progress.version ? cached : saved.progress;
        void getOfflineStore().setAnnotations(loadedAnnotations);
        void getOfflineStore().setProgress(initialProgress);
        setResource(merged);
        setProgress(initialProgress);
        setAnnotations(loadedAnnotations);
        const startPage = requestedPage >= merged.pageStart && requestedPage <= merged.pageCount ? requestedPage : initialProgress.page;
        setPage(startPage);
        setNoteDraft(loadedAnnotations.notes.find((note) => note.page === startPage)?.text || '');
        setReaderState('ready');
        setSaveState('idle');
      } catch (caught) {
        if (!active) return;
        const cachedResource = data.resources.find((candidate) => candidate.id === resourceId);
        const cachedProgress = readCachedResourceProgress(resourceId) ?? (await getOfflineStore().getProgress(resourceId));
        if (cachedResource && cachedProgress) {
          setResource(cachedResource);
          setProgress(cachedProgress);
          setAnnotations((await getOfflineStore().getAnnotations(resourceId)) ?? { resourceId, favorite: false, notes: [] });
          setNoteDraft('');
          setPage(cachedProgress.page);
          setSaveState('offline');
          setReaderState('ready');
          return;
        }
        setErrorMessage(caught instanceof ApiError ? caught.message : '资源服务暂时不可用，请检查网络后重试。');
        setReaderState('error');
      }
    }
    void load();
    return () => {
      active = false;
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
    };
  }, [data.resources, preview, requestedPage, resourceId]);

  useEffect(() => {
    setNoteDraft(annotations.notes.find((note) => note.page === page)?.text || '');
  }, [annotations.notes, page]);

  useEffect(() => {
    if (preview || !resource?.locator) { setOfflineCached(false); return; }
    const locator = resource.locator.replace(/([?&]page=)\d+/, `$1${page}`);
    void isUrlCached(locator).then(setOfflineCached);
  }, [page, preview, resource]);

  function cacheProgress(next: ResourceProgress) {
    try { window.localStorage.setItem(`resource-progress:${resourceId}`, JSON.stringify(next)); } catch { /* storage may be unavailable */ }
    void getOfflineStore().setProgress(next);
  }

  function scheduleSave(next: ResourceProgress) {
    if (preview || !resource?.available) return;
    cacheProgress(next);
    if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
    setSaveState('saving');
    saveTimer.current = window.setTimeout(() => {
      void saveResourceProgress(resourceId, next, next.version, csrfToken, `resource-progress:${resourceId}:${next.version}:${next.page}:${next.percent}`)
        .then((saved) => { setProgress(saved); setPage(saved.page); cacheProgress(saved); setSaveState('saved'); void clearQueuedProgress(getOfflineStore(), resourceId); })
        .catch((caught) => {
          if (caught instanceof ApiError && caught.code === 'resource_progress_conflict') setSaveState('conflict');
          else {
            void enqueueProgress(getOfflineStore(), next);
            if (caught instanceof TypeError || (caught instanceof ApiError && caught.code === 'network_error')) setSaveState('offline');
            else setSaveState('error');
          }
        });
    }, 500);
  }

  function changePage(nextPage: number) {
    if (!resource?.available || !progress || !resource.pageCount) return;
    const next = Math.max(resource.pageStart, Math.min(resource.pageCount, Math.round(nextPage)));
    const nextProgress: ResourceProgress = { ...progress, page: next, percent: Math.round((next / resource.pageCount) * 100), completed: next >= resource.pageCount };
    setPage(next);
    setProgress(nextProgress);
    scheduleSave(nextProgress);
  }

  function markComplete() {
    if (resource?.available && progress && resource.pageCount) changePage(resource.pageCount);
  }

  function updateLocalNote(text: string, version: number) {
    setAnnotations((current) => {
      const notes = current.notes.filter((note) => note.page !== page);
      return { ...current, notes: [...notes, { id: `${resourceId}:${page}`, resourceId, page, text, version, updatedAt: new Date().toISOString() }] };
    });
  }

  async function toggleFavorite() {
    const next = !annotations.favorite;
    setAnnotations((current) => ({ ...current, favorite: next }));
    if (preview) return;
    setAnnotationState('saving');
    try {
      const saved = await saveResourceFavorite(resourceId, next, csrfToken, `resource-favorite:${resourceId}:${next}`);
      setAnnotations((current) => ({ ...current, favorite: saved.favorite }));
      setAnnotationState('saved');
      void clearQueuedFavorite(getOfflineStore(), resourceId);
    } catch {
      void enqueueFavorite(getOfflineStore(), resourceId, next);
      setAnnotations((current) => ({ ...current, favorite: !next }));
      setAnnotationState('error');
      setAnnotationMessage('收藏同步失败，已加入离线待同步队列。');
    }
  }

  async function saveCurrentNote() {
    const text = noteDraft.trim();
    if (!text) { setAnnotationMessage('请输入笔记内容后再保存。'); return; }
    const current = annotations.notes.find((note) => note.page === page);
    setAnnotationState('saving');
    try {
      if (preview) {
        updateLocalNote(text, (current?.version || 0) + 1);
      } else {
        const saved = await saveResourceNote(resourceId, page, text, current?.version || 0, csrfToken, `resource-note:${resourceId}:${page}:${current?.version || 0}:${text}`);
        updateLocalNote(saved.text, saved.version);
      }
      setAnnotationState('saved');
      setAnnotationMessage('笔记已保存。');
      void clearQueuedNote(getOfflineStore(), resourceId, page);
    } catch (caught) {
      if (!(caught instanceof ApiError && caught.code === 'resource_note_conflict')) {
        void enqueueNoteSave(getOfflineStore(), resourceId, page, text, current?.version || 0);
      }
      setAnnotationState(caught instanceof ApiError && caught.code === 'resource_note_conflict' ? 'conflict' : 'error');
      setAnnotationMessage(caught instanceof ApiError && caught.code === 'resource_note_conflict' ? '这页笔记已在其他页面更新，请刷新后再编辑。' : '笔记保存失败，已加入离线待同步队列。');
    }
  }

  async function removeCurrentNote() {
    const current = annotations.notes.find((note) => note.page === page);
    if (!current) { setNoteDraft(''); return; }
    setAnnotationState('saving');
    try {
      if (preview) {
        setAnnotations((value) => ({ ...value, notes: value.notes.filter((note) => note.page !== page) }));
      } else {
        await deleteResourceNote(resourceId, page, current.version, csrfToken, `resource-note-delete:${resourceId}:${page}:${current.version}`);
        setAnnotations((value) => ({ ...value, notes: value.notes.filter((note) => note.page !== page) }));
      }
      setNoteDraft('');
      setAnnotationState('saved');
      setAnnotationMessage('笔记已删除。');
      void clearQueuedNote(getOfflineStore(), resourceId, page);
    } catch (caught) {
      if (!(caught instanceof ApiError && caught.code === 'resource_note_conflict')) {
        void enqueueNoteDelete(getOfflineStore(), resourceId, page, current.version);
      }
      setAnnotationState(caught instanceof ApiError && caught.code === 'resource_note_conflict' ? 'conflict' : 'error');
      setAnnotationMessage(caught instanceof ApiError && caught.code === 'resource_note_conflict' ? '这页笔记已在其他页面更新，请刷新后再操作。' : '笔记删除失败，已加入离线待同步队列。');
    }
  }

  const chapterResources = data.resources.filter((item) => item.chapterId === resource?.chapterId);
  const saveLabel = saveState === 'saving' ? '保存中' : saveState === 'saved' ? '已保存' : saveState === 'offline' ? '离线草稿' : saveState === 'conflict' ? '版本冲突' : saveState === 'error' ? '保存失败' : '';
  const pageLocator = resource?.locator ? resource.locator.replace(/([?&]page=)\d+/, `$1${page}`) : null;
  const currentNote = annotations.notes.find((note) => note.page === page);
  return <><PageHead eyebrow="章节阅读" title={resource?.title || '资源阅读器'} description={resource ? `${resource.sourceFile} · 第 ${resource.chapterId} 章` : '正在读取课程资源。'} action={<button className="button secondary" onClick={() => navigate(-1)}><ArrowLeft size={16} />返回资料库</button>} /><div className="reader-layout"><aside className="reader-catalog"><span className="catalog-label">本章资料</span>{chapterResources.map((item) => <button key={item.id} className={`reader-catalog-item ${item.id === resourceId ? 'active' : ''}`} onClick={() => navigate(`/resources/${encodeURIComponent(item.id)}`)}><span><strong>{item.title}</strong><small>{item.pageCount} 页 · {item.available ? '可阅读' : '待挂载'}</small></span><ChevronRight size={15} /></button>)}</aside><section className="reader-surface">{readerState === 'loading' && <div className="empty-state">正在读取资源状态…</div>}{readerState === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{errorMessage}</strong><button className="button secondary" onClick={() => window.location.reload()}>重新加载</button></div>}{readerState === 'ready' && resource && progress && <><div className="reader-toolbar"><div><strong>{resource.available ? '课程阅读器' : '文件待挂载'}</strong><small>{resource.available ? `第 ${page} / ${resource.pageCount} 页` : '当前仅有资源元数据，教材文件尚未挂载'}</small></div><div className="reader-toolbar-actions"><button className={`icon-button ${annotations.favorite ? 'is-favorite' : ''}`} title={annotations.favorite ? '取消收藏' : '收藏资料'} aria-label={annotations.favorite ? '取消收藏' : '收藏资料'} onClick={() => void toggleFavorite()}><Star size={16} fill={annotations.favorite ? 'currentColor' : 'none'} /></button>{resource?.available && pageLocator && isPwaSupported() && <button className={`icon-button ${offlineCached ? 'is-favorite' : ''}`} title={offlineCached ? '已缓存，可离线阅读' : '缓存此资料用于离线阅读'} aria-label={offlineCached ? '已缓存，可离线阅读' : '缓存此资料用于离线阅读'} aria-pressed={offlineCached} onClick={() => { void cacheUrlForOffline(pageLocator).then(() => void isUrlCached(pageLocator).then(setOfflineCached)); }}><Download size={16} /></button>}{resource && <button className="button quiet" onClick={() => navigate(`/assistant?resource_id=${encodeURIComponent(resource.id)}&page=${page}&chapter_id=${resource.chapterId}`)}><Bot size={15} />问 Agent</button>}<div className="reader-controls"><button className="icon-button" title="上一页" aria-label="上一页" disabled={!resource.available || page <= resource.pageStart} onClick={() => changePage(page - 1)}><Minus size={16} /></button><input aria-label="当前页码" type="number" min={resource.pageStart} max={resource.pageCount || undefined} value={page} disabled={!resource.available} onChange={(event) => { const next = Number(event.target.value); changePage(next); setNoteDraft(annotations.notes.find((note) => note.page === next)?.text || ''); }} /><button className="icon-button" title="下一页" aria-label="下一页" disabled={!resource.available || page >= resource.pageCount} onClick={() => { const next = Math.min(resource.pageCount, page + 1); changePage(next); setNoteDraft(annotations.notes.find((note) => note.page === next)?.text || ''); }}><Plus size={16} /></button></div></div></div>{resource.available && pageLocator ? <iframe className="pdf-frame" title={resource.title} src={pageLocator} loading="lazy" referrerPolicy="no-referrer" /> : <div className="resource-pending"><FileText size={34} /><h2>文件待挂载</h2><p>课程已登记这份资料，但当前环境没有可读取的 PDF 文件。挂载与 manifest 校验完成后，阅读器才会开放。</p><code>{resource.sourceFile}</code></div>}<section className="reader-notes" aria-label="页码笔记"><div className="reader-notes-heading"><div><strong>第 {page} 页笔记</strong><small>{annotations.notes.length ? `已保存 ${annotations.notes.length} 条笔记` : '记录对本页的理解和疑问'}</small></div><span className={`reader-save-state ${annotationState}`}>{annotationMessage || (currentNote ? '已保存' : '')}</span></div><textarea value={noteDraft} maxLength={2000} onChange={(event) => setNoteDraft(event.target.value)} placeholder="写下这一页的重点、疑问或待复习内容" aria-label={`第 ${page} 页笔记`} /><div className="reader-notes-actions"><button className="button quiet" onClick={() => void removeCurrentNote()} disabled={!currentNote || annotationState === 'saving'}><Trash2 size={15} />删除笔记</button><button className="button primary" onClick={() => void saveCurrentNote()} disabled={!noteDraft.trim() || annotationState === 'saving'}>保存笔记<CheckCircle2 size={15} /></button></div></section><div className="reader-footer"><span>学习进度 {Math.round(progress.percent)}%</span><div className="progress-line"><span style={{ width: `${progress.percent}%` }} /></div><span className={`reader-save-state ${saveState}`}>{saveLabel || (progress.completed ? '已完成' : '未完成')}</span><button className="button quiet" disabled={!resource.available || progress.completed} onClick={markComplete}>标记完成<CheckCircle2 size={15} /></button></div>{(saveState === 'offline' || saveState === 'error') && <div className="reader-notice">网络或服务不可用，当前进度已保存在本机草稿中。<button className="text-button" onClick={() => scheduleSave(progress)}>重试同步<RefreshCw size={14} /></button></div>}{saveState === 'conflict' && <div className="reader-notice conflict">此资源已在其他页面更新进度，请刷新后再继续，避免覆盖较新的记录。</div>}</>}</section></div></>;
}
