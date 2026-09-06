/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, BookOpen, ChevronLeft, ChevronRight, Clock3, FileText, GraduationCap, ListChecks, MessageSquare, Network, Search } from 'lucide-react';
import { ApiError, loadGlobalSearch } from '../api/client';
import { GlobalSearchFilterKind, GlobalSearchItem, GlobalSearchKind, GlobalSearchResult, PlatformData, Role } from '../types';
import { PageHead } from '../ui';
import { previewExams, previewStudentTasks } from '../ui-helpers';
import { useAppStore } from '../state/app';
import { useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router';
import { usePlatformData } from '../appData';

const globalSearchKinds: GlobalSearchKind[] = ['course', 'chapter', 'resource', 'assignment', 'exam', 'discussion', 'knowledge'];

const globalSearchFilterKinds: GlobalSearchFilterKind[] = ['all', ...globalSearchKinds];

const globalSearchLabels: Record<GlobalSearchFilterKind, string> = {
  all: '全部', course: '课程', chapter: '章节', resource: '资料', assignment: '作业', exam: '考试', discussion: '讨论', knowledge: '知识点',
};

function emptyGlobalSearch(courseId: number, query: string, kind: GlobalSearchFilterKind, page: number, pageSize: number): GlobalSearchResult {
  return { courseId, query, kind, items: [], counts: { course: 0, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 }, page, pageSize, total: 0 };
}

function previewGlobalSearch(data: PlatformData, query: string, kind: GlobalSearchFilterKind, page: number, pageSize: number, courseId: number): GlobalSearchResult {
  const candidates: GlobalSearchItem[] = [];
  data.courses.filter((item) => item.id === courseId).forEach((item) => candidates.push({ id: String(item.id), kind: 'course', title: item.name, summary: `${item.teacher} · ${item.className}`, chapterId: null }));
  data.chapters.forEach((item) => candidates.push({ id: String(item.id), kind: 'chapter', title: item.name, summary: `${item.lessons} 个学习单元 · 当前进度 ${item.progress}%`, chapterId: item.id }));
  data.resources.forEach((item) => candidates.push({ id: item.id, kind: 'resource', title: item.title, summary: `${item.sourceFile} · 第 ${item.chapterId} 章`, chapterId: item.chapterId }));
  data.assignments.forEach((item) => candidates.push({ id: item.id, kind: 'assignment', title: item.title, summary: `${item.type} · 截止 ${item.dueAt}`, chapterId: null }));
  previewExams.forEach((item) => candidates.push({ id: item.id, kind: 'exam', title: item.title, summary: `课程考试 · 截止 ${item.closeAt}`, chapterId: null }));
  previewStudentTasks.filter((item) => item.kind === 'discussion').forEach((item) => candidates.push({ id: item.sourceId, kind: 'discussion', title: item.title, summary: '课程讨论', chapterId: null }));
  data.profile.forEach((item) => candidates.push({ id: item.id, kind: 'knowledge', title: item.name, summary: item.ratio === null ? '尚未评估' : `当前掌握度 ${Math.round(item.ratio * 100)}%`, chapterId: Number(item.id.split('-')[1] || 0) || 1 }));
  const needle = query.toLocaleLowerCase();
  const rank = (item: GlobalSearchItem) => {
    const title = item.title.toLocaleLowerCase();
    if (title === needle) return 0;
    if (title.startsWith(needle)) return 1;
    if (title.includes(needle)) return 2;
    return 3;
  };
  const matching = candidates
    .filter((item) => `${item.title} ${item.summary}`.toLocaleLowerCase().includes(needle))
    .sort((left, right) => rank(left) - rank(right)
      || globalSearchKinds.indexOf(left.kind) - globalSearchKinds.indexOf(right.kind)
      || (left.chapterId || 0) - (right.chapterId || 0)
      || left.title.localeCompare(right.title, 'zh-CN')
      || left.id.localeCompare(right.id));
  const counts = emptyGlobalSearch(courseId, query, kind, page, pageSize).counts;
  matching.forEach((item) => { counts[item.kind] += 1; });
  const filtered = kind === 'all' ? matching : matching.filter((item) => item.kind === kind);
  const start = (page - 1) * pageSize;
  return { courseId, query, kind, items: filtered.slice(start, start + pageSize), counts, page, pageSize, total: filtered.length };
}

function globalSearchIcon(kind: GlobalSearchKind) {
  if (kind === 'course') return <GraduationCap size={17} />;
  if (kind === 'chapter') return <BookOpen size={17} />;
  if (kind === 'resource') return <FileText size={17} />;
  if (kind === 'assignment') return <ListChecks size={17} />;
  if (kind === 'exam') return <Clock3 size={17} />;
  if (kind === 'discussion') return <MessageSquare size={17} />;
  return <Network size={17} />;
}

function globalSearchTarget(item: GlobalSearchItem, courseId: number, role: Role): string {
  const course = encodeURIComponent(String(courseId));
  const id = encodeURIComponent(item.id);
  if (item.kind === 'course') return role === 'student' ? `/courses/${course}` : `/teacher/courses/${course}/overview`;
  if (item.kind === 'chapter') return role === 'student' ? `/courses/${course}/chapters/${encodeURIComponent(String(item.chapterId))}` : `/teacher/courses/${course}/overview`;
  if (item.kind === 'resource') return role === 'student' ? `/courses/${course}/resources/${id}` : `/teacher/courses/${course}/resources`;
  if (item.kind === 'assignment') return role === 'student' ? `/courses/${course}/assignments/${id}` : `/teacher/courses/${course}/assignments/${id}`;
  if (item.kind === 'exam') return role === 'student' ? `/courses/${course}/exams/${id}` : `/teacher/courses/${course}/exams`;
  if (item.kind === 'discussion') return `/courses/${course}/discussions/${id}`;
  return `/knowledge-graph?q=${encodeURIComponent(item.title)}`;
}

function globalSearchQueryString(query: string, kind: GlobalSearchFilterKind, page: number): string {
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (kind !== 'all') params.set('kind', kind);
  if (page > 1) params.set('page', String(page));
  const serialized = params.toString();
  return serialized ? `?${serialized}` : '';
}

function globalSearchPath(query: string, kind: GlobalSearchFilterKind, page: number): string {
  return `/search${globalSearchQueryString(query, kind, page)}`;
}

export function SearchPage() {
  const data = usePlatformData();
  const preview = useAppStore((state) => state.preview);
  const session = useAppStore((state) => state.session);
  const role = useAppStore((state) => state.role());
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const query = (searchParams.get('q') || '').trim();
  const requestedKind = searchParams.get('kind') || 'all';
  const kind = globalSearchFilterKinds.includes(requestedKind as GlobalSearchFilterKind) ? requestedKind as GlobalSearchFilterKind : 'all';
  const requestedPage = Number(searchParams.get('page') || 1);
  const page = Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1;
  const pageSize = 10;
  const courseId = session?.courseId || data.courses[0]?.id || 1;
  const canonicalSearch = globalSearchQueryString(query, kind, page);
  const isCanonicalRoute = location.search === canonicalSearch;
  const [input, setInput] = useState(query);
  const [result, setResult] = useState<GlobalSearchResult>(() => emptyGlobalSearch(courseId, query, kind, page, pageSize));
  const [state, setState] = useState<'idle' | 'loading' | 'ready' | 'error'>(query ? 'loading' : 'idle');
  const [message, setMessage] = useState('');
  const [reloadToken, setReloadToken] = useState(0);
  const requestSequence = useRef(0);
  const [activeIndex, setActiveIndex] = useState(0);
  const rowRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const totalPages = Math.max(1, Math.ceil(result.total / pageSize));
  const resultItems = result.items;

  useEffect(() => {
    setActiveIndex(0);
  }, [resultItems]);

  function handleResultKeyDown(event: ReactKeyboardEvent<HTMLDivElement>) {
    const count = resultItems.length;
    if (!count) return;
    const moveTo = (target: number) => {
      event.preventDefault();
      setActiveIndex(target);
      rowRefs.current[target]?.focus();
    };
    if (event.key === 'ArrowDown') moveTo(activeIndex < 0 ? 0 : Math.min(count - 1, activeIndex + 1));
    else if (event.key === 'ArrowUp') moveTo(activeIndex < 0 ? 0 : Math.max(0, activeIndex - 1));
    else if (event.key === 'Home') moveTo(0);
    else if (event.key === 'End') moveTo(count - 1);
  }

  useEffect(() => setInput(query), [query]);
  useEffect(() => {
    if (!isCanonicalRoute) navigate(`/search${canonicalSearch}`, { replace: true });
  }, [canonicalSearch, isCanonicalRoute, navigate]);
  useEffect(() => {
    const sequence = ++requestSequence.current;
    if (!isCanonicalRoute) return;
    if (!query) {
      setResult(emptyGlobalSearch(courseId, query, kind, page, pageSize));
      setState('idle');
      setMessage('');
      return;
    }
    setState('loading');
    setMessage('');
    setResult(emptyGlobalSearch(courseId, query, kind, page, pageSize));
    if (preview) {
      const loaded = previewGlobalSearch(data, query, kind, page, pageSize, courseId);
      const loadedTotalPages = Math.max(1, Math.ceil(loaded.total / pageSize));
      if (page > loadedTotalPages) {
        navigate(globalSearchPath(query, kind, loadedTotalPages), { replace: true });
        return;
      }
      setResult(loaded);
      setState('ready');
      return;
    }
    void loadGlobalSearch(query, { kind, page, pageSize }).then((loaded) => {
      if (sequence !== requestSequence.current) return;
      if (!session || loaded.courseId !== session.courseId) throw new ApiError('搜索结果不属于当前课程', 'search_course_mismatch');
      const loadedTotalPages = Math.max(1, Math.ceil(loaded.total / pageSize));
      if (page > loadedTotalPages) {
        navigate(globalSearchPath(query, kind, loadedTotalPages), { replace: true });
        return;
      }
      setResult(loaded);
      setState('ready');
    }).catch((caught) => {
      if (sequence !== requestSequence.current) return;
      setResult(emptyGlobalSearch(courseId, query, kind, page, pageSize));
      setMessage(caught instanceof ApiError ? caught.message : '课程搜索暂时不可用，请稍后重试。');
      setState('error');
    });
  }, [courseId, data, isCanonicalRoute, kind, navigate, page, preview, query, reloadToken, session]);

  function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = input.trim();
    navigate(globalSearchPath(value, 'all', 1));
  }

  function selectKind(nextKind: GlobalSearchFilterKind) {
    navigate(globalSearchPath(query, nextKind, 1));
  }

  function selectPage(nextPage: number) {
    navigate(globalSearchPath(query, kind, nextPage));
  }

  return <><PageHead eyebrow="全局搜索" title={query ? `搜索“${query.slice(0, 100)}”` : '搜索课程内容'} description="查找当前课程的章节、资料、作业、考试、讨论和知识点。" /><form className="search-page-form" role="search" onSubmit={submit}><label htmlFor="global-search-page">搜索课程内容</label><div><Search size={17} /><input id="global-search-page" value={input} maxLength={100} onChange={(event) => setInput(event.target.value)} placeholder="输入课程、资料或知识点" /><button className="button primary" type="submit"><Search size={16} />搜索</button></div></form>{!query ? <section className="section-block search-empty"><Search size={28} /><h2>从课程内容开始查找</h2><p>可以搜索“储能变流器”“第 3 章”或“章节练习”。</p></section> : <section className="section-block search-results" aria-live="polite" aria-busy={state === 'loading'}><div className="section-title"><h2>搜索结果</h2><span className="status-tag">{state === 'loading' ? '搜索中…' : `${result.total} 条`}</span></div><div className="filter-tabs search-filter-tabs" role="tablist" aria-label="搜索结果类型">{globalSearchFilterKinds.map((filterKind) => <button type="button" role="tab" aria-selected={kind === filterKind} className={kind === filterKind ? 'active' : ''} key={filterKind} disabled={state === 'loading'} onClick={() => selectKind(filterKind)}>{globalSearchLabels[filterKind]}<small>{filterKind === 'all' ? globalSearchKinds.reduce((sum, itemKind) => sum + result.counts[itemKind], 0) : result.counts[filterKind]}</small></button>)}</div>{state === 'loading' && <div className="empty-state" role="status">正在搜索当前课程…</div>}{state === 'error' && <div className="empty-state reader-error" role="alert"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => setReloadToken((value) => value + 1)}>重新搜索</button></div>}{state === 'ready' && !resultItems.length && <div className="empty-state">没有找到匹配内容，请尝试其他关键词或结果类型。</div>}{state === 'ready' && resultItems.length > 0 && <div className="search-result-list" onKeyDown={handleResultKeyDown}>{resultItems.map((item, index) => <button className="search-result-row" key={`${item.kind}:${item.id}`} ref={(node) => { rowRefs.current[index] = node; }} tabIndex={activeIndex === index ? 0 : -1} onFocus={() => setActiveIndex(index)} onClick={() => navigate(globalSearchTarget(item, result.courseId, role))}><span className="search-result-icon">{globalSearchIcon(item.kind)}</span><span><strong>{item.title}</strong><small><em>{globalSearchLabels[item.kind]}</em>{item.summary}</small></span><ChevronRight size={17} /></button>)}</div>}{state === 'ready' && totalPages > 1 && <nav className="course-pagination" aria-label="搜索结果分页"><span>第 {page} / {totalPages} 页，共 {result.total} 条</span><button className="icon-button" type="button" aria-label="搜索上一页" title="上一页" disabled={page <= 1} onClick={() => selectPage(page - 1)}><ChevronLeft size={17} /></button><button className="icon-button" type="button" aria-label="搜索下一页" title="下一页" disabled={page >= totalPages} onClick={() => selectPage(page + 1)}><ChevronRight size={17} /></button></nav>}</section>}</>;
}
