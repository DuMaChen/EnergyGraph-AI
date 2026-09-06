/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ArrowUpRight, BarChart3, BookOpen, Bot, CheckCircle2, ChevronRight, Clock3, FileText, FolderOpen, GraduationCap, Heart, ListChecks, Network, RefreshCw, Search } from 'lucide-react';
import { ApiError, loadFavoriteResources, saveResourceFavorite } from '../api/client';
import { FavoriteResource, Resource } from '../types';
import { Metric, PageHead, SectionTitle } from '../ui';
import { overallProgress } from '../data/preview';
import { useAppStore } from '../state/app';
import { memo, useCallback, useDeferredValue, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router';
import { usePlatformData } from '../appData';

export function HelpPage() {
  const navigate = useNavigate();
  return <><PageHead eyebrow="支持中心" title="帮助中心" description="从课程入口、资料阅读、任务提交到 Agent 使用，快速找到下一步操作。" /><div className="help-layout"><section className="section-block help-list"><div className="section-title"><h2>常见入口</h2><span className="status-tag">课程平台</span></div><button className="help-row" onClick={() => navigate('/course')}><BookOpen size={18} /><span><strong>如何开始学习</strong><small>从课程空间选择章节，再打开对应资料或任务。</small></span><ChevronRight size={17} /></button><button className="help-row" onClick={() => navigate('/resources')}><FolderOpen size={18} /><span><strong>如何查找资料</strong><small>在资料库搜索文件名，进入资源页查看挂载状态和学习进度。</small></span><ChevronRight size={17} /></button><button className="help-row" onClick={() => navigate('/tasks')}><ListChecks size={18} /><span><strong>如何提交任务</strong><small>草稿会自动保存，最终提交由服务端校验截止时间和尝试次数。</small></span><ChevronRight size={17} /></button><button className="help-row" onClick={() => navigate('/assistant')}><Bot size={18} /><span><strong>如何使用课程 Agent</strong><small>问题会绑定课程上下文；来源显示为待核验时不要把回答当作教材事实。</small></span><ChevronRight size={17} /></button></section><aside className="section-block help-contact"><span className="side-kicker">遇到问题</span><h2>先检查课程会话</h2><p>如果页面显示预览、文件待挂载或服务异常，请先刷新并确认登录状态。学习记录不会把预览数据写入成绩。</p><button className="button secondary" onClick={() => window.location.reload()}><RefreshCw size={16} />重新加载课程</button></aside></div></>;
}

export function SettingsPage() {
  const [notifications, setNotifications] = useState(() => window.localStorage.getItem('learning-settings:notifications') !== 'false');
  const [autoSave, setAutoSave] = useState(() => window.localStorage.getItem('learning-settings:auto-save') !== 'false');
  const [highContrast, setHighContrast] = useState(() => window.localStorage.getItem('learning-settings:high-contrast') === 'true');
  const [message, setMessage] = useState('');

  useEffect(() => {
    window.localStorage.setItem('learning-settings:notifications', String(notifications));
    window.localStorage.setItem('learning-settings:auto-save', String(autoSave));
    window.localStorage.setItem('learning-settings:high-contrast', String(highContrast));
    document.documentElement.dataset.contrast = highContrast ? 'high' : 'normal';
  }, [autoSave, highContrast, notifications]);

  function saveMessage() {
    setMessage('设置已保存到本机。');
    window.setTimeout(() => setMessage(''), 1800);
  }

  return <><PageHead eyebrow="账户与支持" title="学习设置" description="管理当前浏览器的通知、自动保存和显示偏好。账号权限仍由课程服务端控制。" />{message && <div className="reader-notice" role="status">{message}</div>}<div className="settings-layout"><section className="section-block settings-panel"><div className="section-title"><h2>学习偏好</h2><span className="status-tag">仅本机保存</span></div><label className="setting-row"><span><strong>课程通知提醒</strong><small>显示教师发布的通知和任务提醒。</small></span><input type="checkbox" checked={notifications} onChange={(event) => { setNotifications(event.target.checked); saveMessage(); }} /></label><label className="setting-row"><span><strong>阅读进度自动保存</strong><small>在资源阅读器中节流保存页码和完成状态。</small></span><input type="checkbox" checked={autoSave} onChange={(event) => { setAutoSave(event.target.checked); saveMessage(); }} /></label><label className="setting-row"><span><strong>增强文字对比度</strong><small>提高辅助阅读时的文字和状态颜色对比。</small></span><input type="checkbox" checked={highContrast} onChange={(event) => { setHighContrast(event.target.checked); saveMessage(); }} /></label></section><section className="section-block settings-note"><span className="side-kicker">安全边界</span><h2>凭据不会保存在前端</h2><p>讯飞 API Key、API Secret、Moodle 会话和服务端密钥不由本页面管理，也不会写入本机设置。</p><span className="status-tag active">当前设置已脱敏</span></section></div></>;
}

export function FavoritesPage() {
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [items, setItems] = useState<FavoriteResource[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>(preview ? 'ready' : 'loading');
  const [message, setMessage] = useState('');
  const [busyId, setBusyId] = useState('');

  const reload = useCallback(async () => {
    if (preview) {
      setItems([]);
      setState('ready');
      return;
    }
    setState('loading');
    try {
      setItems(await loadFavoriteResources());
      setMessage('');
      setState('ready');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '收藏服务暂时不可用。');
      setState('error');
    }
  }, [preview]);

  useEffect(() => { void reload(); }, [reload]);

  async function removeFavorite(resource: FavoriteResource) {
    if (busyId) return;
    setBusyId(resource.id);
    setMessage('');
    try {
      await saveResourceFavorite(resource.id, false, csrfToken, `favorite-list-remove:${resource.id}:${Date.now()}`);
      setItems((current) => current.filter((item) => item.id !== resource.id));
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '取消收藏失败，请稍后重试。');
    } finally {
      setBusyId('');
    }
  }

  return <><PageHead eyebrow="资料库" title="资料收藏" description="集中查看收藏的课程资料和页码笔记。" action={<button className="button secondary" onClick={() => void reload()}><RefreshCw size={16} />刷新收藏</button>} />{message && <div className="reader-notice conflict" role="alert">{message}</div>}{preview && <div className="empty-state"><Heart size={24} /><strong>预览模式没有真实收藏</strong><span>登录课程平台并在资料阅读器中收藏内容后，这里会显示你的资料。</span></div>}{!preview && state === 'loading' && <div className="empty-state">正在读取收藏…</div>}{!preview && state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message || '收藏服务暂时不可用。'}</strong><button className="button secondary" onClick={() => void reload()}><RefreshCw size={16} />重新加载</button></div>}{!preview && state === 'ready' && !items.length && <div className="empty-state"><Heart size={24} /><strong>还没有收藏资料</strong><span>在资料阅读器中收藏重点内容，稍后可以从这里快速继续学习。</span></div>}{!preview && state === 'ready' && items.length > 0 && <div className="resource-grid">{items.map((resource) => <article className="resource-card" key={resource.id}><div className="resource-card-top"><span className="resource-icon"><Heart size={19} /></span><span className="status-tag">{resource.noteCount ? `${resource.noteCount} 条笔记` : '已收藏'}</span></div><h2>{resource.title}</h2><p>第 {resource.chapterId} 章 · {resource.pageCount} 页 · {resource.version}</p><div className="row-actions"><button className="button quiet" onClick={() => navigate(`/resources/${encodeURIComponent(resource.id)}`)}>{resource.available ? '打开资料' : '查看状态'}<ArrowUpRight size={15} /></button><button className="text-button danger" onClick={() => void removeFavorite(resource)} disabled={busyId === resource.id}>取消收藏</button></div></article>)}</div>}</>;
}

const ResourceCard = memo(function ResourceCard({ resource, onOpen }: { resource: Resource; onOpen: (id: string) => void }) {
  return <article className="resource-card"><div className="resource-card-top"><span className="resource-icon"><FileText size={19} /></span><span className={`status-tag ${resource.available ? '' : 'pending'}`}>{resource.available ? resource.type : '文件待挂载'}</span></div><h2>{resource.title}</h2><p>第 {resource.chapterId} 章 · {resource.pageCount} 页 · {resource.version}</p><button className="button quiet" onClick={() => onOpen(resource.id)}>{resource.available ? '打开资料' : '查看状态'}<ArrowUpRight size={15} /></button></article>;
});

export function ResourcesPage() {
  const data = usePlatformData();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);
  const filteredResources = useMemo(() => {
    const keyword = deferredQuery.trim().toLowerCase();
    return data.resources.filter((item) => !keyword || `${item.title}${item.sourceFile}`.toLowerCase().includes(keyword));
  }, [data.resources, deferredQuery]);
  const openResource = useCallback((id: string) => {
    navigate(`/resources/${encodeURIComponent(id)}`);
  }, [navigate]);
  return <><PageHead eyebrow="资料库" title="课程资料" description="按教材、章节和来源查找学习材料。" action={<button className="button secondary" onClick={() => setQuery('')} disabled={!query}><RefreshCw size={16} />清除筛选</button>} /><div className="resource-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索资料名称或文件名" aria-label="搜索资料" /></div><p className="resource-summary">共 {data.resources.length} 份资料，当前显示 {filteredResources.length} 份。</p><div className="resource-grid">{filteredResources.map((resource) => <ResourceCard key={resource.id} resource={resource} onOpen={openResource} />)}</div>{!filteredResources.length && <div className="empty-state">没有匹配的课程资料。</div>}</>;
}

export function GradesPage() {
  const data = usePlatformData();
  const navigate = useNavigate();
  const { courseId = 'current' } = useParams();
  const scored = data.assignments.filter((item) => item.score !== null && Number.isFinite(item.score));
  const average = scored.length ? Math.round(scored.reduce((total, item) => total + Number(item.score), 0) / scored.length) : null;
  return <><PageHead eyebrow="课程成绩" title="成绩与反馈" description="查看当前课程任务的提交状态和服务端返回的成绩；未批改内容不会被显示为通过。" action={<button className="button secondary" onClick={() => navigate(`/courses/${encodeURIComponent(courseId)}/progress`)}><BarChart3 size={16} />学习记录</button>} /><div className="metric-grid"><Metric icon={<BarChart3 />} value={average === null ? '—' : String(average)} label="已评分平均" tone="blue" suffix={average === null ? undefined : '分'} /><Metric icon={<CheckCircle2 />} value={String(scored.length)} label="已评分任务" tone="green" /><Metric icon={<Clock3 />} value={String(data.assignments.filter((item) => item.score === null).length)} label="待反馈任务" tone="orange" /><Metric icon={<GraduationCap />} value={`${overallProgress(data.chapters)}%`} label="课程进度" tone="gold" /></div><section className="section-block grade-list"><div className="section-title"><h2>任务成绩</h2><span className="status-tag">{data.assignments.length} 项</span></div><div className="task-table" role="table" aria-label="任务成绩"><div className="task-table-head" role="row"><span role="columnheader">任务</span><span role="columnheader">类型</span><span role="columnheader">状态</span><span role="columnheader">成绩</span></div>{data.assignments.map((item) => <div className="task-table-row" key={item.id} role="row"><div role="cell"><strong>{item.title}</strong><small>截止 {item.dueAt} · {item.questionCount} 道题</small></div><span role="cell">{item.type}</span><span className={`status-tag ${item.status === '已完成' ? 'active' : ''}`} role="cell">{item.status}</span><span className="task-table-actions" role="cell"><button className="button quiet" onClick={() => navigate(`/courses/${encodeURIComponent(courseId)}/assignments/${encodeURIComponent(item.id)}`)}>{item.score === null ? '查看反馈' : `${item.score} 分`}<ChevronRight size={15} /></button></span></div>)}{!data.assignments.length && <div className="task-table-row empty-row" role="row"><div className="empty-state" role="cell">当前课程还没有成绩记录。</div></div>}</div></section></>;
}

export function ProfilePage() { const data = usePlatformData(); const navigate = useNavigate(); return <><PageHead eyebrow="学习记录" title="我的学习状态" description="查看课程进度、知识点掌握和下一步建议。" action={<button className="button secondary" onClick={() => navigate('/knowledge-graph')}><Network size={16} />打开学习图谱</button>} /><div className="profile-overview"><div><span className="eyebrow">当前课程</span><h2>电力系统储能技术</h2><p>学习记录来自当前课程会话；预览模式中的数据不会写入成绩。</p></div><strong>{overallProgress(data.chapters)}<small>%</small></strong></div><div className="profile-grid"><section className="section-block"><SectionTitle title="知识点掌握" link="打开知识图谱" onClick={() => navigate('/knowledge-graph')} /><div className="mastery-list">{data.profile.map((item) => <div className="mastery-row" key={item.id}><div><strong>{item.name}</strong><small>{item.status === 'mastered' ? '已掌握' : item.status === 'weak' ? '需要加强' : item.status === 'learning' ? '学习中' : '未评估'}</small></div><div className="progress-line"><span style={{ width: `${(item.ratio || 0) * 100}%` }} /></div><strong>{item.ratio === null ? '—' : `${Math.round(item.ratio * 100)}%`}</strong></div>)}</div></section><section className="section-block"><SectionTitle title="下一步建议" link="进入 Agent" onClick={() => navigate('/assistant')} /><div className="recommendation-list">{data.recommendations.map((item) => <div className="recommendation-row" key={item.id}><span className="recommendation-number">·</span><div><strong>{item.title}</strong><small>{item.reason}</small></div></div>)}</div></section></div></>; }
