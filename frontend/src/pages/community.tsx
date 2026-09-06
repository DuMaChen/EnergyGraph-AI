/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { Activity, ActivityGroupsState, ActivityKind, ActivityResults, ClassroomRoster, DiscussionTopic, NotificationItem, RandomSelectionState } from '../types';
import { AlertTriangle, ArrowLeft, Bell, CheckCircle2, ChevronLeft, ChevronRight, CircleHelp, RefreshCw, Search, Send, Shuffle, Users, UsersRound, Zap } from 'lucide-react';
import { ApiError, createDiscussion, createDiscussionReply, generateActivityGroups, loadActivities, loadActivity, loadActivityGroups, loadActivityResults, loadClassroomRoster, loadDiscussion, loadDiscussions, loadNotifications, loadRandomSelection, markAllNotificationsRead, markNotificationRead, moderateDiscussion, reportDiscussion, selectRandomStudent, submitActivityResponse } from '../api/client';
import { PageHead } from '../ui';
import { activityKindLabel, syncGlobalNotificationState } from '../ui-helpers';
import { useAppStore } from '../state/app';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router';
import { usePlatformData } from '../appData';

export function DiscussionsPage() {
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [items, setItems] = useState<DiscussionTopic[]>([]);
  const [query, setQuery] = useState('');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [creating, setCreating] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const loadSequence = useRef(0);
  const pageSize = 8;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const load = useCallback(async () => {
    const sequence = ++loadSequence.current;
    if (preview) { setItems([]); setTotal(0); setState('ready'); return; }
    setState('loading');
    try {
      const loaded = await loadDiscussions(query, page, pageSize);
      if (sequence !== loadSequence.current) return;
      setItems(loaded.items); setTotal(loaded.total); setState('ready'); setMessage('');
    }
    catch (caught) {
      if (sequence !== loadSequence.current) return;
      setState('error'); setMessage(caught instanceof ApiError ? caught.message : '讨论服务暂时不可用。');
    }
  }, [preview, query, page]);

  useEffect(() => { setPage(1); }, [query]);
  useEffect(() => { void load(); }, [load]);

  async function create() {
    if (!title.trim() || !body.trim() || creating || preview) return;
    setCreating(true); setMessage('');
    try {
      const topic = await createDiscussion(title, body, csrfToken, `discussion-create:${Date.now()}`);
      navigate(`/discussions/${encodeURIComponent(topic.id)}`);
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '主题发布失败。'); }
    finally { setCreating(false); }
  }

  return <><PageHead eyebrow="课程互动" title="课程讨论" description="围绕课程资料提问、回复和整理结论；内容以纯文本保存并受课程权限控制。" action={<button className="button secondary" onClick={() => void load()}><RefreshCw size={16} />刷新</button>} />{preview && <div className="preview-banner"><CircleHelp size={16} /><span>当前为预览模式，讨论发布不会写入课程平台。</span></div>}<div className="discussion-layout"><section className="discussion-list-panel"><div className="discussion-toolbar"><div className="resource-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} aria-label="搜索讨论" placeholder="搜索主题或内容" /></div><span className="status-tag">{total} 个主题</span></div>{state === 'loading' && <div className="empty-state">正在读取讨论…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void load()}>重新加载</button></div>}{state === 'ready' && !items.length && <div className="empty-state">当前没有可见讨论主题。</div>}{state === 'ready' && items.map((item) => <button className="discussion-row" key={item.id} onClick={() => navigate(`/discussions/${encodeURIComponent(item.id)}`)}><div className="discussion-row-heading"><strong>{item.title}</strong><span className={`status-tag ${item.status === 'solved' ? 'active' : ''}`}>{item.pinned ? '置顶 · ' : ''}{item.status === 'solved' ? '已解决' : item.status === 'closed' ? '已关闭' : '开放'}</span></div><p>{item.body}</p><small>{item.authorLabel} · {item.replyCount} 条回复 · {item.updatedAt || item.createdAt}</small></button>)}{state === 'ready' && totalPages > 1 && <nav className="course-pagination" aria-label="讨论列表分页"><span>第 {page} / {totalPages} 页，共 {total} 条</span><button className="icon-button" type="button" aria-label="讨论上一页" title="上一页" disabled={page <= 1} onClick={() => setPage(page - 1)}><ChevronLeft size={17} /></button><button className="icon-button" type="button" aria-label="讨论下一页" title="下一页" disabled={page >= totalPages} onClick={() => setPage(page + 1)}><ChevronRight size={17} /></button></nav>}</section><aside className="discussion-compose"><span className="side-kicker">发起讨论</span><h2>把问题留在课程里</h2><label>主题<input value={title} onChange={(event) => setTitle(event.target.value)} maxLength={160} placeholder="例如：并网控制中的功率约束如何理解？" /></label><label>内容<textarea value={body} onChange={(event) => setBody(event.target.value)} maxLength={8000} placeholder="描述你的问题或想和同学核对的结论" /></label>{message && <div className="reader-notice conflict">{message}</div>}<button className="button primary" onClick={() => void create()} disabled={preview || creating || !title.trim() || !body.trim()}>{creating ? '发布中…' : '发布主题'}<Send size={16} /></button></aside></div></>;
}

export function DiscussionDetailPage() {
  const { topicId = '' } = useParams();
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const role = useAppStore((state) => state.role());
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [topic, setTopic] = useState<DiscussionTopic | null>(null);
  const [reply, setReply] = useState('');
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [reportReason, setReportReason] = useState('');
  const [reporting, setReporting] = useState('');
  const reportSequence = useRef(0);

  const load = useCallback(async () => {
    if (preview) { setState('error'); setMessage('预览模式没有讨论详情。'); return; }
    setState('loading');
    try { setTopic(await loadDiscussion(topicId)); setState('ready'); setMessage(''); }
    catch (caught) { setState('error'); setMessage(caught instanceof ApiError ? caught.message : '讨论主题暂时不可用。'); }
  }, [preview, topicId]);
  useEffect(() => { void load(); }, [load]);

  async function sendReply() {
    if (!reply.trim() || !topic) return;
    try { await createDiscussionReply(topic.id, reply, csrfToken, `discussion-reply:${topic.id}:${Date.now()}`); setReply(''); await load(); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '回复发布失败。'); }
  }

  async function moderate(update: { status?: string; pinned?: boolean }) {
    if (!topic) return;
    try { setTopic(await moderateDiscussion(topic.id, { ...update, reason: '教师在讨论管理页操作' }, csrfToken, `discussion-moderate:${topic.id}:${update.status || update.pinned}`)); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '讨论管理操作失败。'); }
  }

  async function report(replyId: string | null = null) {
    if (!topic || !reportReason.trim() || reporting) return;
    setReporting(replyId || 'topic');
    try {
      reportSequence.current += 1;
      await reportDiscussion(topic.id, replyId, reportReason.trim(), csrfToken, `discussion-report:${topic.id}:${replyId || 'topic'}:${reportSequence.current}`);
      setReportReason('');
      if (replyId) {
        await load();
        setMessage('已提交举报，管理员会核对该回复。');
      } else {
        navigate('/discussions');
      }
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '举报提交失败。'); }
    finally { setReporting(''); }
  }

  if (state === 'loading') return <><PageHead eyebrow="课程讨论" title="正在打开主题" description="正在读取主题和回复。" /><div className="empty-state">正在读取讨论…</div></>;
  if (state === 'error' || !topic) return <><PageHead eyebrow="课程讨论" title="无法打开主题" description="服务端没有返回可见讨论内容。" action={<button className="button secondary" onClick={() => navigate('/discussions')}><ArrowLeft size={16} />返回讨论</button>} /><div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void load()}>重新加载</button></div></>;
  return <><PageHead eyebrow="课程讨论" title={topic.title} description={`${topic.authorLabel} · ${topic.replyCount} 条回复`} action={<button className="button secondary" onClick={() => navigate('/discussions')}><ArrowLeft size={16} />返回讨论</button>} /><div className="discussion-detail-layout"><main className="discussion-thread"><article className="topic-post"><div className="discussion-row-heading"><span className={`status-tag ${topic.status === 'solved' ? 'active' : ''}`}>{topic.pinned ? '置顶 · ' : ''}{topic.status === 'solved' ? '已解决' : topic.status === 'closed' ? '已关闭' : '开放'}</span><small>{topic.authorLabel} · {topic.createdAt}</small></div><p>{topic.body}</p></article><div className="reply-list">{(topic.replies || []).map((item) => <article className="reply-item" key={item.id}><div className="reply-meta"><strong>{item.authorLabel}</strong><small>{item.createdAt}</small><button className="text-button" onClick={() => void report(item.id)} disabled={!reportReason.trim() || reporting !== ''}>举报</button></div><p>{item.body}</p></article>)}{!(topic.replies || []).length && <div className="empty-state">还没有回复，成为第一个回应的人。</div>}</div>{topic.status !== 'closed' && <div className="reply-compose"><textarea value={reply} onChange={(event) => setReply(event.target.value)} aria-label="回复内容" placeholder="写下你的回复" maxLength={8000} /><button className="button primary" onClick={() => void sendReply()} disabled={!reply.trim()}>回复主题<Send size={16} /></button></div>}{message && <div className="reader-notice conflict">{message}</div>}</main><aside className="discussion-side"><span className="side-kicker">主题状态</span><strong>{topic.status === 'closed' ? '已关闭' : topic.status === 'solved' ? '已解决' : '开放讨论'}</strong>{(topic.canModerate || role !== 'student') && <div className="moderation-actions"><button className="button quiet" onClick={() => void moderate({ pinned: !topic.pinned })}>{topic.pinned ? '取消置顶' : '置顶主题'}</button><button className="button quiet" onClick={() => void moderate({ status: topic.status === 'solved' ? 'open' : 'solved' })}>{topic.status === 'solved' ? '重新打开' : '标记解决'}</button><button className="button quiet" onClick={() => void moderate({ status: topic.status === 'closed' ? 'open' : 'closed' })}>{topic.status === 'closed' ? '重新打开' : '关闭主题'}</button></div>}<div className="moderation-report"><label htmlFor="discussion-report-reason">举报原因<textarea id="discussion-report-reason" aria-label="举报原因" value={reportReason} onChange={(event) => setReportReason(event.target.value)} maxLength={500} placeholder="说明需要管理员核对的内容" /></label><button className="button quiet" onClick={() => void report()} disabled={!reportReason.trim() || reporting !== ''}>举报主题</button><small>举报后内容会进入管理员审核队列。</small></div></aside></div></>;
}

export function ActivitiesPage() {
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const role = useAppStore((state) => state.session?.role || 'student');
  const [items, setItems] = useState<Activity[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const load = useCallback(async () => {
    if (preview) { setItems([]); setState('ready'); return; }
    setState('loading');
    try { setItems(await loadActivities()); setState('ready'); setMessage(''); }
    catch (caught) { setState('error'); setMessage(caught instanceof ApiError ? caught.message : '课堂活动暂时不可用。'); }
  }, [preview]);
  useEffect(() => { void load(); }, [load]);
  return <>
    <PageHead eyebrow="课程互动" title="课堂活动" description="参与签到、抢答、投票、问卷、随机选人和分组任务，并查看可见结果。" action={<button className="button secondary" onClick={() => void load()}><RefreshCw size={16} />刷新</button>} />
    {preview && <div className="preview-banner"><CircleHelp size={16} /><span>当前为预览模式，课堂活动需要建立课程会话后才会读取。</span></div>}
    {state === 'loading' && <div className="empty-state">正在读取课堂活动…</div>}
    {state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void load()}>重新加载</button></div>}
    {state === 'ready' && !items.length && <div className="empty-state">当前没有开放的课堂活动。</div>}
    {state === 'ready' && <div className="activity-list">{items.map((item) => {
      const isCheckin = item.kind === 'checkin';
      const isQuickResponse = item.kind === 'quick_response';
      const isRandomSelection = item.kind === 'random_selection';
      const isGroupTask = item.kind === 'group_task';
      const studentState = item.status === 'closed'
        ? isQuickResponse && item.hasResponded ? '抢答成功' : '已结束'
        : isRandomSelection ? '等待抽取'
          : isGroupTask ? '查看分组'
            : item.canRespond
          ? isCheckin ? '待签到' : isQuickResponse ? '可抢答' : item.attemptsUsed > 0 ? '可再次提交' : '待参与'
          : isCheckin ? '已签到' : isQuickResponse ? '已结束' : '已提交';
      const detail = isCheckin
        ? item.status === 'draft' ? '尚未发布' : item.status === 'closed' ? '签到已关闭，可查看统计' : role !== 'student' ? '可查看签到人数' : item.canRespond ? '等待确认' : '服务端已记录'
        : isQuickResponse
          ? item.status === 'draft' ? '尚未发布' : item.status === 'closed' ? item.hasResponded && role === 'student' ? '你是本次首位响应者' : '抢答已结束，可查看结果' : role !== 'student' ? '等待首位学生响应' : '抢答已开放'
          : isRandomSelection
            ? item.status === 'draft' ? '尚未发布' : item.status === 'closed' ? '随机选人已关闭' : role !== 'student' ? '打开详情开始抽取' : '等待教师抽取'
            : isGroupTask
              ? item.status === 'draft' ? `${item.options.length} 个预设组 · 尚未发布` : item.status === 'closed' ? '分组任务已关闭' : role !== 'student' ? `${item.options.length} 个预设组 · 可生成分组` : '打开详情查看我的组'
              : `${item.options.length} 个选项 · ${item.status === 'draft' ? '尚未发布' : item.status === 'closed' ? '活动已关闭，可查看结果' : role !== 'student' ? '可查看活动和汇总' : item.canRespond ? `剩余 ${item.maxAttempts - item.attemptsUsed} 次机会` : '可查看结果'}`;
      return <button className="activity-card" key={item.id} onClick={() => navigate(`/activities/${encodeURIComponent(item.id)}`)}><div className="activity-card-head"><span className={`status-tag ${item.status === 'published' ? 'active' : ''}`}>{activityKindLabel(item.kind)}</span><span className={!item.canRespond && item.status === 'published' && role === 'student' ? 'activity-state done' : 'activity-state'}>{role !== 'student' ? item.status === 'draft' ? '草稿' : item.status === 'closed' ? '已关闭' : '已发布' : studentState}</span></div><strong>{item.title}</strong><p>{item.body}</p><small>{detail}</small><ChevronRight size={17} /></button>;
    })}</div>}
  </>;
}

export function ActivityDetailPage() {
  const { activityId = '' } = useParams();
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const role = useAppStore((state) => state.session?.role || 'student');
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [activity, setActivity] = useState<Activity | null>(null);
  const [results, setResults] = useState<ActivityResults | null>(null);
  const [answers, setAnswers] = useState<string[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [messageTone, setMessageTone] = useState<'info' | 'success' | 'error'>('info');
  const [quickVerdict, setQuickVerdict] = useState<'idle' | 'won' | 'lost' | 'uncertain'>('idle');
  const [roster, setRoster] = useState<ClassroomRoster | null>(null);
  const [rosterState, setRosterState] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [rosterMessage, setRosterMessage] = useState('');
  const [eventState, setEventState] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [eventMessage, setEventMessage] = useState('');
  const [eventMessageTone, setEventMessageTone] = useState<'info' | 'success' | 'error'>('info');
  const [randomSelection, setRandomSelection] = useState<RandomSelectionState | null>(null);
  const [groupsState, setGroupsState] = useState<ActivityGroupsState | null>(null);
  const [randomBusy, setRandomBusy] = useState(false);
  const [groupBusy, setGroupBusy] = useState(false);
  const submitLockRef = useRef(false);
  const randomLockRef = useRef(false);
  const groupLockRef = useRef(false);
  const randomIdempotencyRef = useRef('');
  const groupIdempotencyRef = useRef('');
  const randomPendingRoundRef = useRef<number | null>(null);
  const groupPendingRevisionRef = useRef<number | null>(null);
  const activityKindRef = useRef<ActivityKind | null>(null);
  const loadedActivityIdRef = useRef('');

  const refreshRoster = useCallback(async (): Promise<ClassroomRoster | null> => {
    if (role === 'student') return null;
    setRosterState('loading'); setRosterMessage('');
    try {
      const loaded = await loadClassroomRoster();
      setRoster(loaded); setRosterState('ready');
      return loaded;
    } catch (caught) {
      setRosterState('error');
      setRosterMessage(caught instanceof ApiError ? caught.message : '班级花名册暂时不可用。');
      return null;
    }
  }, [role]);

  const refreshRandomSelection = useCallback(async (): Promise<RandomSelectionState | null> => {
    setEventState('loading'); setEventMessage(''); setEventMessageTone('info');
    try {
      const loaded = await loadRandomSelection(activityId);
      if (randomIdempotencyRef.current && randomPendingRoundRef.current !== null && loaded.round > randomPendingRoundRef.current) {
        randomIdempotencyRef.current = '';
        randomPendingRoundRef.current = null;
      }
      setRandomSelection(loaded); setEventState('ready');
      return loaded;
    } catch (caught) {
      setEventState('error'); setEventMessageTone('error');
      setEventMessage(caught instanceof ApiError ? caught.message : '随机选人结果暂时不可用。');
      return null;
    }
  }, [activityId]);

  const refreshGroups = useCallback(async (): Promise<ActivityGroupsState | null> => {
    setEventState('loading'); setEventMessage(''); setEventMessageTone('info');
    try {
      const loaded = await loadActivityGroups(activityId);
      if (groupIdempotencyRef.current && groupPendingRevisionRef.current !== null && (loaded.revision || 0) > groupPendingRevisionRef.current) {
        groupIdempotencyRef.current = '';
        groupPendingRevisionRef.current = null;
      }
      setGroupsState(loaded); setEventState('ready');
      return loaded;
    } catch (caught) {
      setEventState('error'); setEventMessageTone('error');
      setEventMessage(caught instanceof ApiError ? caught.message : '分组结果暂时不可用。');
      return null;
    }
  }, [activityId]);

  const load = useCallback(async (showLoading = true): Promise<Activity | null> => {
    if (preview) {
      if (showLoading) { setState('error'); setMessageTone('error'); setMessage('预览模式没有课堂活动详情。'); }
      return null;
    }
    if (showLoading) setState('loading');
    try {
      if (loadedActivityIdRef.current !== activityId) {
        loadedActivityIdRef.current = activityId;
        activityKindRef.current = null;
        setRandomSelection(null); setGroupsState(null); setRoster(null);
        setEventState('idle'); setRosterState('idle');
        randomIdempotencyRef.current = ''; groupIdempotencyRef.current = '';
        randomPendingRoundRef.current = null; groupPendingRevisionRef.current = null;
      }
      const knownKind = activityKindRef.current;
      if (knownKind === 'random_selection') {
        const [loaded] = await Promise.all([loadActivity(activityId), refreshRandomSelection(), role === 'student' ? Promise.resolve(null) : refreshRoster()]);
        setActivity(loaded); setResults(null); setAnswers([]); setState('ready');
        if (showLoading) { setMessage(''); setMessageTone('info'); }
        return loaded;
      }
      if (knownKind === 'group_task') {
        const [loaded] = await Promise.all([loadActivity(activityId), refreshGroups(), role === 'student' ? Promise.resolve(null) : refreshRoster()]);
        setActivity(loaded); setResults(null); setAnswers([]); setState('ready');
        if (showLoading) { setMessage(''); setMessageTone('info'); }
        return loaded;
      }
      if (knownKind) {
        const [loaded, loadedResults] = await Promise.all([loadActivity(activityId), loadActivityResults(activityId)]);
        setActivity(loaded); setResults(loadedResults); setAnswers(loaded.myResponse?.answers || []); setState('ready');
        if (loaded.kind === 'quick_response') setQuickVerdict(loaded.status === 'closed' ? loaded.hasResponded ? 'won' : 'lost' : 'idle');
        if (showLoading) { setMessage(''); setMessageTone('info'); }
        return loaded;
      }
      const loaded = await loadActivity(activityId);
      activityKindRef.current = loaded.kind;
      setActivity(loaded); setAnswers(loaded.myResponse?.answers || []);
      if (loaded.kind === 'random_selection') {
        setResults(null);
        await Promise.all([refreshRandomSelection(), role === 'student' ? Promise.resolve(null) : refreshRoster()]);
      } else if (loaded.kind === 'group_task') {
        setResults(null);
        await Promise.all([refreshGroups(), role === 'student' ? Promise.resolve(null) : refreshRoster()]);
      } else {
        setResults(await loadActivityResults(activityId));
      }
      setState('ready');
      if (loaded.kind === 'quick_response') setQuickVerdict(loaded.status === 'closed' ? loaded.hasResponded ? 'won' : 'lost' : 'idle');
      if (showLoading) { setMessage(''); setMessageTone('info'); }
      return loaded;
    } catch (caught) {
      if (showLoading) { setState('error'); setMessageTone('error'); setMessage(caught instanceof ApiError ? caught.message : '课堂活动暂时不可用。'); }
      return null;
    }
  }, [activityId, preview, refreshGroups, refreshRandomSelection, refreshRoster, role]);
  useEffect(() => { void load(); }, [load]);

  function toggleAnswer(optionId: string) {
    if (!activity?.canRespond) return;
    if (activity.kind === 'checkin' || activity.kind === 'quick_response') return;
    if (activity?.kind === 'poll') { setAnswers([optionId]); return; }
    setAnswers((current) => current.includes(optionId) ? current.filter((item) => item !== optionId) : [...current, optionId]);
  }

  async function submit() {
    const submissionAnswers = activity?.kind === 'checkin' ? ['present'] : activity?.kind === 'quick_response' ? ['claim'] : answers;
    if (!activity || !submissionAnswers.length || submitLockRef.current || submitting || !activity.canRespond || activity.nextAttempt === null) return;
    submitLockRef.current = true;
    setSubmitting(true); setMessage(''); setMessageTone('info');
    try {
      const response = await submitActivityResponse(activity.id, submissionAnswers, csrfToken, `activity-response:${activity.id}:${activity.nextAttempt}`, activity.nextAttempt);
      if (activity.kind === 'quick_response') {
        setQuickVerdict('won');
        setActivity((current) => current ? { ...current, status: 'closed', hasResponded: true, attemptsUsed: 1, canRespond: false, canReopen: false, nextAttempt: null, myResponse: response } : current);
        setResults((current) => current ? { ...current, totalResponses: 1, hasResponded: true, resultsAvailable: true, options: [], participants: [] } : current);
      }
      const synced = await load(false);
      setMessageTone('success');
      setMessage(activity.kind === 'checkin' ? '签到成功，服务端已记录本次签到。' : activity.kind === 'quick_response' ? synced ? '抢答成功，你是本次首位响应者。' : '抢答成功，服务端已确认；当前状态同步暂时不可用。' : '提交成功，最新答案已保存并计入汇总。');
    } catch (caught) {
      if (activity.kind === 'quick_response' && caught instanceof ApiError && caught.code === 'quick_response_already_claimed') {
        setQuickVerdict('lost');
        setActivity((current) => current ? { ...current, status: 'closed', canRespond: false, canReopen: false, nextAttempt: null } : current);
        setResults((current) => current ? { ...current, totalResponses: Math.max(1, current.totalResponses), hasResponded: false, resultsAvailable: true, options: [], participants: [] } : current);
        await load(false);
        setMessageTone('info');
        setMessage(caught.message);
      } else if (activity.kind === 'quick_response') {
        const confirmed = await load(false);
        if (confirmed?.status === 'closed') {
          const won = confirmed.hasResponded;
          setQuickVerdict(won ? 'won' : 'lost');
          setMessageTone(won ? 'success' : 'info');
          setMessage(won ? '服务端已确认你是本次首位响应者。' : '已有同学抢答成功，本次抢答已结束。');
        } else {
          setQuickVerdict('uncertain');
          setMessageTone('info');
          setMessage('抢答请求结果待确认，请先确认服务端状态。');
        }
      } else {
        setMessageTone('error');
        setMessage(caught instanceof ApiError ? caught.message : '活动提交失败，请重试。');
      }
    }
    finally { submitLockRef.current = false; setSubmitting(false); }
  }

  async function confirmQuickResponse() {
    if (submitLockRef.current || submitting) return;
    submitLockRef.current = true;
    setSubmitting(true); setMessage(''); setMessageTone('info');
    const confirmed = await load(false);
    if (!confirmed) {
      setMessageTone('error'); setMessage('暂时无法确认抢答结果，请稍后重试。');
    } else if (confirmed.status === 'closed') {
      const won = confirmed.hasResponded;
      setQuickVerdict(won ? 'won' : 'lost');
      setMessageTone(won ? 'success' : 'info');
      setMessage(won ? '服务端已确认你是本次首位响应者。' : '已有同学抢答成功，本次抢答已结束。');
    } else {
      setQuickVerdict('idle'); setMessageTone('info'); setMessage('当前尚未产生抢答结果。');
    }
    submitLockRef.current = false; setSubmitting(false);
  }

  async function runRandomSelection() {
    if (!activity || activity.kind !== 'random_selection' || role === 'student' || activity.status !== 'published' || randomLockRef.current || randomBusy || rosterState !== 'ready' || !roster?.configured || roster.items.length < 1 || eventState !== 'ready' || !randomSelection?.canSelect) return;
    randomLockRef.current = true;
    setRandomBusy(true); setEventMessage(''); setEventMessageTone('info');
    if (!randomIdempotencyRef.current) {
      const operationId = globalThis.crypto?.randomUUID?.() || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
      randomIdempotencyRef.current = `activity-random-select:${activity.id}:${operationId}`;
      randomPendingRoundRef.current = randomSelection.round;
    }
    try {
      const selected = await selectRandomStudent(activity.id, csrfToken, randomIdempotencyRef.current);
      setRandomSelection(selected); setEventState('ready'); setEventMessageTone('success');
      setEventMessage(selected.latest ? `第 ${selected.round} 轮抽取已确认：${selected.latest.displayName}` : '随机抽取已完成。');
      randomIdempotencyRef.current = '';
      randomPendingRoundRef.current = null;
    } catch (caught) {
      setEventMessageTone('error');
      setEventMessage(caught instanceof ApiError ? caught.message : '随机抽取失败，可刷新结果后重试。');
    } finally {
      randomLockRef.current = false; setRandomBusy(false);
    }
  }

  async function generateGroups() {
    const requiredGroups = activity?.kind === 'group_task' ? activity.options.length : 0;
    if (!activity || activity.kind !== 'group_task' || role === 'student' || activity.status !== 'published' || groupLockRef.current || groupBusy || rosterState !== 'ready' || !roster?.configured || roster.items.length < requiredGroups || requiredGroups < 2 || eventState !== 'ready' || !groupsState?.canGenerate) return;
    groupLockRef.current = true;
    setGroupBusy(true); setEventMessage(''); setEventMessageTone('info');
    if (!groupIdempotencyRef.current) {
      const operationId = globalThis.crypto?.randomUUID?.() || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
      groupIdempotencyRef.current = `activity-groups-generate:${activity.id}:${operationId}`;
      groupPendingRevisionRef.current = groupsState.revision || 0;
    }
    try {
      const generated = await generateActivityGroups(activity.id, csrfToken, groupIdempotencyRef.current);
      setGroupsState(generated); setEventState('ready'); setEventMessageTone('success');
      setEventMessage(`第 ${generated.revision} 版分组已确认。`);
      groupIdempotencyRef.current = '';
      groupPendingRevisionRef.current = null;
    } catch (caught) {
      setEventMessageTone('error');
      setEventMessage(caught instanceof ApiError ? caught.message : '分组生成失败，可刷新结果后重试。');
    } finally {
      groupLockRef.current = false; setGroupBusy(false);
    }
  }

  if (state === 'loading') return <><PageHead eyebrow="课堂活动" title="正在打开活动" description="正在读取活动选项和结果。" /><div className="empty-state">正在读取课堂活动…</div></>;
  if (state === 'error' || !activity) return <><PageHead eyebrow="课堂活动" title="无法打开活动" description="服务端没有返回可见的课堂活动。" action={<button className="button secondary" onClick={() => navigate('/activities')}><ArrowLeft size={16} />返回活动</button>} /><div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void load()}>重新加载</button></div></>;
  const isCheckin = activity.kind === 'checkin';
  const isQuickResponse = activity.kind === 'quick_response';
  const isRandomSelection = activity.kind === 'random_selection';
  const isGroupTask = activity.kind === 'group_task';
  const eventStatusLabel = activity.status === 'draft' ? '草稿' : activity.status === 'closed' ? '已关闭' : '已发布';
  const limitedRandomHistory = (randomSelection?.history || []).slice(-10).reverse();
  const studentGroup = groupsState?.myGroup || groupsState?.groups.find((group) => group.members.some((member) => member.isMe)) || null;

  function rosterReadiness(requiredCount: number) {
    if (rosterState === 'idle' || rosterState === 'loading') return <div className="roster-readiness pending"><RefreshCw size={20} /><div><strong>正在读取班级花名册</strong><small>目录状态确认中</small></div></div>;
    if (rosterState === 'error') return <div className="roster-readiness blocked"><AlertTriangle size={20} /><div><strong>花名册加载失败</strong><small>{rosterMessage || '暂时无法确认班级成员。'}</small></div><button className="button secondary" onClick={() => void refreshRoster()}>重新读取</button></div>;
    if (!roster?.configured) return <div className="roster-readiness blocked"><AlertTriangle size={20} /><div><strong>班级目录未配置</strong><small>当前课程没有可用的学生花名册。</small></div><button className="button secondary" onClick={() => void refreshRoster()}>重新读取</button></div>;
    if (!roster.items.length) return <div className="roster-readiness blocked"><Users size={20} /><div><strong>班级花名册为空</strong><small>当前没有可参与课堂活动的学生。</small></div><button className="button secondary" onClick={() => void refreshRoster()}>刷新花名册</button></div>;
    if (roster.items.length < requiredCount) return <div className="roster-readiness blocked"><AlertTriangle size={20} /><div><strong>班级人数不足</strong><small>当前 {roster.items.length} 名学生，少于 {requiredCount} 个预设组。</small></div><button className="button secondary" onClick={() => void refreshRoster()}>刷新花名册</button></div>;
    return <div className="roster-readiness ready"><CheckCircle2 size={20} /><div><strong>花名册已就绪</strong><small>{Math.max(roster.total, roster.items.length)} 名学生可参与</small></div><button className="icon-button" title="刷新班级花名册" aria-label="刷新班级花名册" onClick={() => void refreshRoster()}><RefreshCw size={16} /></button></div>;
  }

  if (isRandomSelection) {
    const canSelect = role !== 'student' && activity.status === 'published' && rosterState === 'ready' && Boolean(roster?.configured && roster.items.length) && eventState === 'ready' && Boolean(randomSelection?.canSelect);
    const actionLabel = randomBusy ? '抽取中…' : activity.status === 'closed' ? '活动已关闭' : activity.status === 'draft' ? '发布后可抽取' : randomSelection?.round ? '继续抽取' : '抽取一名学生';
    return <>
      <PageHead eyebrow="课堂随机选人" title={activity.title} description={activity.body} action={<button className="button secondary" onClick={() => navigate('/activities')}><ArrowLeft size={16} />返回活动</button>} />
      <div className={`activity-layout classroom-event-layout ${role === 'student' ? 'student-event-layout' : ''}`}>
        {role === 'student' ? <section className="activity-form classroom-student-result"><div className="activity-form-head"><span className="status-tag">随机选人</span><span className="activity-state">{eventStatusLabel}</span></div>
          {eventState === 'loading' && <div className="empty-state">正在读取最新抽取结果…</div>}
          {eventState === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{eventMessage}</strong><button className="button secondary" onClick={() => void refreshRandomSelection()}>重新加载</button></div>}
          {eventState === 'ready' && randomSelection?.latest && <div className={`random-selection-stage ${randomSelection.latest.isMe ? 'is-me' : ''}`}><Shuffle size={32} /><small>最新抽取</small><strong>{randomSelection.latest.displayName}</strong><span>{randomSelection.latest.isMe ? '本次抽中的是你' : '本次未抽中你'}</span></div>}
          {eventState === 'ready' && !randomSelection?.latest && <div className="empty-state">教师尚未开始抽取。</div>}
        </section> : <><section className="activity-form classroom-event-controls" aria-busy={randomBusy}><div className="activity-form-head"><span className="status-tag">随机选人</span><span className="activity-state">{eventStatusLabel}</span></div>
          {rosterReadiness(1)}
          {eventMessage && eventState !== 'error' && <div className={`reader-notice ${eventMessageTone === 'error' ? 'conflict' : ''}`} role="status" aria-live="polite" aria-atomic="true">{eventMessage}</div>}
          {eventMessageTone === 'error' && eventState === 'ready' && <button className="button secondary" onClick={() => void load()} disabled={randomBusy}>刷新抽取结果<RefreshCw size={16} /></button>}
          <button className="button primary" onClick={() => void runRandomSelection()} disabled={!canSelect || randomBusy}>{actionLabel}<Shuffle size={16} /></button>
        </section><section className="activity-results classroom-event-results" aria-busy={eventState === 'loading'}><div className="section-title"><h2>抽取结果</h2><span className="status-tag">{randomSelection?.round ? `第 ${randomSelection.round} 轮` : '尚未抽取'}</span></div>
          {eventState === 'loading' && <div className="empty-state">正在读取抽取结果…</div>}
          {eventState === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{eventMessage}</strong><button className="button secondary" onClick={() => void refreshRandomSelection()}>重新加载</button></div>}
          {eventState === 'ready' && randomSelection?.latest && <><div className="random-selection-stage teacher-view"><Shuffle size={30} /><small>本轮抽取</small><strong>{randomSelection.latest.displayName}</strong><span>第 {randomSelection.latest.round || randomSelection.round} 轮已确认{randomSelection.remainingCount !== null ? ` · 剩余 ${randomSelection.remainingCount} 人` : ''}</span></div>{limitedRandomHistory.length > 0 && <div className="random-history"><div className="classroom-result-heading"><h3>最近抽取</h3><small>最近 {limitedRandomHistory.length} 轮</small></div><ol>{limitedRandomHistory.map((record, index) => <li key={`${record.round}:${record.selectedAt}:${index}`}><span className="round-index">{record.round}</span><strong>{record.displayName}</strong>{record.selectedAt && <time dateTime={record.selectedAt}>{record.selectedAt}</time>}</li>)}</ol></div>}</>}
          {eventState === 'ready' && !randomSelection?.latest && <div className="empty-state">尚未产生抽取结果。</div>}
        </section></>}
      </div>
    </>;
  }

  if (isGroupTask) {
    const requiredGroups = activity.options.length;
    const canGenerate = role !== 'student' && activity.status === 'published' && requiredGroups >= 2 && rosterState === 'ready' && Boolean(roster?.configured && roster.items.length >= requiredGroups) && eventState === 'ready' && Boolean(groupsState?.canGenerate);
    const actionLabel = groupBusy ? '分组中…' : activity.status === 'closed' ? '活动已关闭' : activity.status === 'draft' ? '发布后可分组' : groupsState?.revision ? '重新分组' : '生成分组';
    return <>
      <PageHead eyebrow="课堂分组任务" title={activity.title} description={activity.body} action={<button className="button secondary" onClick={() => navigate('/activities')}><ArrowLeft size={16} />返回活动</button>} />
      <div className={`activity-layout classroom-event-layout ${role === 'student' ? 'student-event-layout' : ''}`}>
        {role === 'student' ? <section className="activity-form classroom-student-result"><div className="activity-form-head"><span className="status-tag">我的分组</span><span className="activity-state">{eventStatusLabel}</span></div>
          {eventState === 'loading' && <div className="empty-state">正在读取我的分组…</div>}
          {eventState === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{eventMessage}</strong><button className="button secondary" onClick={() => void refreshGroups()}>重新加载</button></div>}
          {eventState === 'ready' && studentGroup && <article className="activity-group student-group"><div className="activity-group-head"><UsersRound size={20} /><strong>{studentGroup.name}</strong><span>{studentGroup.members.length} 人</span></div><ul>{studentGroup.members.map((member, index) => <li key={`${member.displayName}:${index}`}><span>{member.displayName}</span>{member.isMe && <small>本人</small>}</li>)}</ul></article>}
          {eventState === 'ready' && !studentGroup && <div className="empty-state">教师尚未生成你的分组。</div>}
        </section> : <><section className="activity-form classroom-event-controls" aria-busy={groupBusy}><div className="activity-form-head"><span className="status-tag">分组任务</span><span className="activity-state">{eventStatusLabel}</span></div>
          <div className="configured-groups"><small>预设组名</small><div>{activity.options.map((option) => <span key={option.id}>{option.label}</span>)}</div></div>
          {rosterReadiness(requiredGroups)}
          {eventMessage && eventState !== 'error' && <div className={`reader-notice ${eventMessageTone === 'error' ? 'conflict' : ''}`} role="status" aria-live="polite" aria-atomic="true">{eventMessage}</div>}
          {eventMessageTone === 'error' && eventState === 'ready' && <button className="button secondary" onClick={() => void load()} disabled={groupBusy}>刷新分组结果<RefreshCw size={16} /></button>}
          <button className="button primary" onClick={() => void generateGroups()} disabled={!canGenerate || groupBusy}>{actionLabel}<UsersRound size={16} /></button>
        </section><section className="activity-results classroom-event-results" aria-busy={eventState === 'loading'}><div className="section-title"><h2>全部分组</h2><span className="status-tag">{groupsState?.revision ? `Revision ${groupsState.revision}` : '尚未分组'}</span></div>
          {eventState === 'loading' && <div className="empty-state">正在读取分组结果…</div>}
          {eventState === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{eventMessage}</strong><button className="button secondary" onClick={() => void refreshGroups()}>重新加载</button></div>}
          {eventState === 'ready' && Boolean(groupsState?.groups.length) && <div className="activity-groups-grid">{groupsState?.groups.map((group, groupIndex) => <article className="activity-group" key={`${group.name}:${groupIndex}`}><div className="activity-group-head"><UsersRound size={19} /><strong>{group.name}</strong><span>{group.members.length} 人</span></div><ul>{group.members.map((member, memberIndex) => <li key={`${member.displayName}:${memberIndex}`}><span>{member.displayName}</span>{member.isMe && <small>本人</small>}</li>)}</ul></article>)}</div>}
          {eventState === 'ready' && !groupsState?.groups.length && <div className="empty-state">尚未生成分组结果。</div>}
        </section></>}
      </div>
    </>;
  }
  const isSingleAction = isCheckin || isQuickResponse;
  const stateLabel = role !== 'student'
    ? activity.status === 'draft' ? '草稿' : activity.status === 'closed' ? '已关闭' : '已发布'
    : isQuickResponse
      ? quickVerdict === 'uncertain' ? '待确认' : activity.status === 'closed' ? activity.hasResponded ? '抢答成功' : '已结束' : activity.canRespond ? '可抢答' : '已结束'
      : activity.status === 'closed' ? '已结束' : activity.canRespond ? isCheckin ? '待签到' : activity.attemptsUsed > 0 ? '可再次提交' : '未提交' : isCheckin ? '已签到' : '已提交';
  const submitLabel = role !== 'student'
    ? '仅学生可提交'
    : isQuickResponse
      ? quickVerdict === 'uncertain' ? '结果待确认' : activity.status === 'closed' ? activity.hasResponded ? '已抢到' : '抢答已结束' : activity.canRespond ? '立即抢答' : '抢答已结束'
      : activity.status === 'closed' ? isCheckin ? '签到已结束' : '活动已结束' : activity.canRespond ? isCheckin ? '确认签到' : activity.attemptsUsed > 0 ? `再次提交（${activity.nextAttempt}/${activity.maxAttempts}）` : '提交活动' : isCheckin ? '已签到' : '已提交';
  const canSubmit = activity.canRespond && (isSingleAction || answers.length > 0) && (!isQuickResponse || quickVerdict === 'idle');
  return <>
    <PageHead eyebrow={isCheckin ? '课堂签到' : isQuickResponse ? '课堂抢答' : activity.kind === 'poll' ? '课堂投票' : '课程问卷'} title={activity.title} description={activity.body} action={<button className="button secondary" onClick={() => navigate('/activities')}><ArrowLeft size={16} />返回活动</button>} />
    <div className="activity-layout"><section className="activity-form" aria-busy={submitting}><div className="activity-form-head"><span className={`status-tag ${activity.status === 'published' ? 'active' : ''}`}>{activityKindLabel(activity.kind, true)}</span><span className={`activity-state ${!activity.canRespond && activity.status === 'published' ? 'done' : ''}`}>{stateLabel}</span></div>
      {isCheckin ? <div className={`checkin-panel ${activity.hasResponded ? 'done' : ''}`}><CheckCircle2 size={28} /><strong>{activity.hasResponded ? '签到已记录' : '等待签到'}</strong><small>{activity.myResponse?.submittedAt || (activity.status === 'published' ? '当前签到已开放' : '当前签到未开放')}</small></div> : isQuickResponse ? <div className={`quick-response-panel ${activity.hasResponded ? 'won' : activity.status === 'closed' ? 'closed' : ''}`}><Zap size={30} /><strong>{activity.hasResponded ? '抢答成功' : activity.status === 'closed' ? '抢答已结束' : '等待抢答'}</strong><small>{activity.myResponse?.submittedAt || (activity.status === 'closed' ? '结果已由服务端确认' : '当前抢答已开放')}</small></div> : <fieldset disabled={!activity.canRespond || submitting}><legend>{activity.kind === 'poll' ? '请选择一项' : '请选择一项或多项'}</legend><div className="activity-options">{activity.options.map((option) => <label key={option.id}><input type={activity.kind === 'poll' ? 'radio' : 'checkbox'} name="activity-answer" checked={answers.includes(option.id)} onChange={() => toggleAnswer(option.id)} />{option.label}</label>)}</div></fieldset>}
      {!isSingleAction && activity.maxAttempts > 1 && <small className="activity-attempts">已使用 {activity.attemptsUsed}/{activity.maxAttempts} 次机会</small>}
      {message && <div className={`reader-notice ${messageTone === 'error' ? 'conflict' : ''}`} role="status" aria-live="polite" aria-atomic="true">{message}</div>}
      {isQuickResponse && quickVerdict === 'uncertain' && <button className="button secondary" onClick={() => void confirmQuickResponse()} disabled={submitting}>确认抢答结果<RefreshCw size={16} /></button>}
      <button className="button primary" onClick={() => void submit()} disabled={!canSubmit || submitting}>{submitting ? isCheckin ? '签到中…' : isQuickResponse ? '抢答中…' : '提交中…' : submitLabel}{isCheckin ? <CheckCircle2 size={16} /> : isQuickResponse ? <Zap size={16} /> : <Send size={16} />}</button>
    </section><section className="activity-results"><div className="section-title"><h2>{isCheckin ? '签到统计' : isQuickResponse ? '抢答结果' : '结果汇总'}</h2><span className="status-tag">{results?.resultsAvailable ? isQuickResponse ? results.totalResponses ? '结果已产生' : '暂无响应' : `${results.totalResponses} 人${isCheckin ? '已签到' : '参与'}` : isCheckin ? '签到后可见' : isQuickResponse ? '结束后可见' : '提交后可见'}</span></div>
      {!results?.resultsAvailable && <div className="empty-state">{isCheckin ? '完成签到后可查看当前统计；签到关闭后统计将向课程成员开放。' : isQuickResponse ? '抢答结束后可查看结果状态。' : '完成提交后即可查看匿名汇总；活动关闭后结果将向课程成员开放。'}</div>}
      {results?.resultsAvailable && isCheckin && <div className="checkin-summary"><strong>{results.totalResponses}</strong><span>已签到</span></div>}
      {results?.resultsAvailable && isQuickResponse && <div className={`quick-response-summary ${results.totalResponses ? 'resolved' : ''}`}><Zap size={26} /><div><strong>{results.totalResponses ? role === 'student' && results.hasResponded ? '你是首位响应者' : '首位响应已确认' : '暂无学生响应'}</strong><span>{role === 'student' ? results.hasResponded ? '服务端已记录你的抢答结果' : '胜出者身份仅教师可见' : results.totalResponses ? '胜出记录已进入课程审计' : '活动尚未产生胜出记录'}</span></div></div>}
      {results?.resultsAvailable && !isSingleAction && results.options.map((option) => <div className="activity-result-row" key={option.id}><div><strong>{option.label}</strong><small>{option.count} 人 · {option.ratio}%</small></div><div className="progress-line"><span style={{ width: `${option.ratio}%` }} /></div></div>)}
      {isSingleAction && role !== 'student' && Boolean(results?.participants.length) && <ol className="checkin-participants" aria-label={isCheckin ? '签到记录' : '抢答胜出记录'}>{results?.participants.map((participant) => <li key={`${participant.userRef}:${participant.submittedAt}`}><span>成员 {participant.userRef.replace(/^u_/, '').slice(-8)}</span><time dateTime={participant.submittedAt}>{participant.submittedAt}</time></li>)}</ol>}
    </section></div>
  </>;
}

export function MessagesPage() {
  const platformData = usePlatformData();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedFocusId = (searchParams.get('notice') || '').trim();
  const previewNotifications = preview ? platformData.notifications : null;
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [focusedId, setFocusedId] = useState('');
  const [focusMessage, setFocusMessage] = useState('');
  const loadSequence = useRef(0);
  const focusedRow = useRef<HTMLButtonElement | null>(null);
  const pageSize = 8;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const effectiveUnreadOnly = requestedFocusId ? false : unreadOnly;

  function clearRequestedFocus() {
    if (!requestedFocusId) return;
    const next = new URLSearchParams(searchParams);
    next.delete('notice');
    setSearchParams(next, { replace: true });
    setFocusedId('');
    setFocusMessage('');
  }

  const load = useCallback(async () => {
    const sequence = ++loadSequence.current;
    if (preview) {
      const previewItems = previewNotifications ?? [];
      const visible = effectiveUnreadOnly ? previewItems.filter((item) => !item.isRead) : previewItems;
      const focusIndex = requestedFocusId ? visible.findIndex((item) => item.id === requestedFocusId) : -1;
      const resolvedPage = focusIndex >= 0 ? Math.floor(focusIndex / pageSize) + 1 : page;
      const start = (resolvedPage - 1) * pageSize;
      if (sequence !== loadSequence.current) return;
      setItems(visible.slice(start, start + pageSize));
      setUnreadCount(previewItems.filter((item) => !item.isRead).length);
      setTotal(visible.length);
      if (resolvedPage !== page) setPage(resolvedPage);
      setFocusedId(focusIndex >= 0 ? requestedFocusId : '');
      setFocusMessage(requestedFocusId ? focusIndex >= 0 ? '已定位到任务对应的课程通知。' : '该通知不存在或当前账号不可查看。' : '');
      setState('ready');
      return;
    }
    setState((current) => current === 'ready' ? 'ready' : 'loading');
    try {
      const result = await loadNotifications(effectiveUnreadOnly, page, pageSize, requestedFocusId);
      if (sequence !== loadSequence.current) return;
      setItems(result.items);
      setUnreadCount(result.unreadCount);
      setTotal(result.total);
      if (result.page !== page) setPage(result.page);
      setFocusedId(requestedFocusId && result.focusFound ? result.focusedId || '' : '');
      setFocusMessage(requestedFocusId ? result.focusFound ? '已定位到任务对应的课程通知。' : '该通知不存在或当前账号不可查看。' : '');
      syncGlobalNotificationState(result.unreadCount);
      setState('ready');
      setMessage('');
    }
    catch (caught) {
      if (sequence !== loadSequence.current) return;
      setState('error');
      setMessage(caught instanceof ApiError ? caught.message : '通知服务暂时不可用。');
    }
  }, [effectiveUnreadOnly, page, preview, previewNotifications, requestedFocusId]);
  useEffect(() => {
    void load();
    return () => { loadSequence.current += 1; };
  }, [load]);
  useEffect(() => {
    if (requestedFocusId && unreadOnly) setUnreadOnly(false);
  }, [requestedFocusId, unreadOnly]);
  useEffect(() => {
    if (state === 'ready' && focusedId) focusedRow.current?.scrollIntoView?.({ block: 'center' });
  }, [focusedId, state]);
  useEffect(() => {
    if (state === 'ready') {
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    }
  }, [page, state]);

  async function markRead(item: NotificationItem) {
    if (item.isRead || busy) return;
    setBusy(item.id);
    setMessage('');
    try {
      const fallbackUnreadCount = Math.max(0, unreadCount - 1);
      const result = preview
        ? { unreadCount: fallbackUnreadCount }
        : await markNotificationRead(item.id, csrfToken, `notification-read:${item.id}`);
      const nextUnreadCount = result.unreadCount ?? fallbackUnreadCount;
      syncGlobalNotificationState(nextUnreadCount, item.id);
      setUnreadCount(nextUnreadCount);
      if (effectiveUnreadOnly) {
        const nextTotal = Math.max(0, total - 1);
        setTotal(nextTotal);
        setItems((current) => current.filter((entry) => entry.id !== item.id));
        if (page > 1 && (page - 1) * pageSize >= nextTotal) setPage((value) => Math.max(1, value - 1));
      } else {
        setItems((current) => current.map((entry) => entry.id === item.id ? { ...entry, isRead: true } : entry));
      }
    }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '通知已读状态保存失败。'); }
    finally { setBusy(''); }
  }

  async function markAllRead() {
    if (!unreadCount || busy) return;
    setBusy('all');
    setMessage('');
    try {
      const key = `notification-read-all:${unreadCount}:${items[0]?.id || 'empty'}`;
      const result = preview ? { markedCount: unreadCount, unreadCount: 0 } : await markAllNotificationsRead(csrfToken, key);
      syncGlobalNotificationState(result.unreadCount, undefined, true);
      setUnreadCount(result.unreadCount);
      if (effectiveUnreadOnly) { setItems([]); setTotal(0); setPage(1); }
      else setItems((current) => current.map((item) => ({ ...item, isRead: true })));
      setMessage(result.markedCount ? `已将 ${result.markedCount} 条通知标为已读。` : '所有通知均已是已读状态。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '全部已读状态保存失败。');
    } finally {
      setBusy('');
    }
  }

  return <><PageHead eyebrow="消息中心" title="课程通知" description="课程公告、学习提醒和教师消息都在这里，已读状态由服务端保存。" action={<button className="button secondary" onClick={() => void load()} disabled={Boolean(busy)}><RefreshCw size={16} />刷新</button>} />{preview && <div className="preview-banner"><CircleHelp size={16} /><span>当前为预览模式，通知数据不会写入课程平台。</span></div>}<div className="message-toolbar"><div className="filter-tabs" role="tablist" aria-label="通知筛选"><button role="tab" aria-selected={!effectiveUnreadOnly} className={!effectiveUnreadOnly ? 'active' : ''} onClick={() => { clearRequestedFocus(); setUnreadOnly(false); setPage(1); }}>全部<small>{effectiveUnreadOnly ? '' : total}</small></button><button role="tab" aria-selected={effectiveUnreadOnly} className={effectiveUnreadOnly ? 'active' : ''} onClick={() => { clearRequestedFocus(); setUnreadOnly(true); setPage(1); }}>未读<small>{unreadCount}</small></button></div><button className="button quiet" onClick={() => void markAllRead()} disabled={!unreadCount || Boolean(busy)}><CheckCircle2 size={16} />{busy === 'all' ? '保存中…' : '全部已读'}</button></div>{state === 'loading' && <div className="empty-state" role="status">正在读取通知…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void load()}>重新加载</button></div>}{state === 'ready' && focusMessage && <div className={`reader-notice ${focusedId ? 'focus-success' : 'conflict'}`} role="status" aria-live="polite">{focusMessage}</div>}{state === 'ready' && message && <div className="reader-notice" role="status" aria-live="polite">{message}</div>}{state === 'ready' && !items.length && <div className="empty-state">{effectiveUnreadOnly ? '当前没有未读通知。' : '当前没有通知。'}</div>}{state === 'ready' && items.length > 0 && <div className="message-list" aria-busy={Boolean(busy)}>{items.map((item) => <button ref={item.id === focusedId ? focusedRow : undefined} className={`message-row ${item.isRead ? 'read' : ''} ${item.id === focusedId ? 'focused' : ''}`} key={item.id} data-notification-id={item.id} aria-current={item.id === focusedId ? 'true' : undefined} aria-label={`${item.title}，${item.isRead ? '已读' : '标为已读'}`} disabled={Boolean(busy) || item.isRead} onClick={() => void markRead(item)}><span className="message-icon"><Bell size={17} /></span><span className="row-main"><strong>{item.title}</strong><small>{item.body}</small><em>{item.createdAt || '课程服务端通知'}</em></span>{!item.isRead && <i aria-label="未读" />}</button>)}</div>}{state === 'ready' && totalPages > 1 && <nav className="course-pagination" aria-label="通知列表分页"><span>第 {page} / {totalPages} 页，共 {total} 条</span><button className="icon-button" aria-label="通知上一页" title="上一页" disabled={page <= 1 || Boolean(busy)} onClick={() => { clearRequestedFocus(); setPage((value) => Math.max(1, value - 1)); }}><ChevronLeft size={17} /></button><button className="icon-button" aria-label="通知下一页" title="下一页" disabled={page >= totalPages || Boolean(busy)} onClick={() => { clearRequestedFocus(); setPage((value) => Math.min(totalPages, value + 1)); }}><ChevronRight size={17} /></button></nav>}</>;
}
