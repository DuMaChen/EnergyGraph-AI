/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { Activity, ActivityKind, AssignmentDetail, AssignmentGrade, AssignmentQuestion, AssignmentSubmission, Gradebook, TeacherAssignment, TeacherExam, TeacherQuestion, TeacherResource } from '../types';
import { AlertTriangle, ArrowLeft, BarChart3, CheckCircle2, ChevronRight, Clock3, Download, FileText, FolderOpen, ListChecks, MessageSquare, RefreshCw, Send, Users, X } from 'lucide-react';
import { ApiError, createActivity, createTeacherAssignment, createTeacherExam, createTeacherQuestion, createTeacherResource, gradeAssignment, gradeSubmission, loadActivities, loadAssignment, loadTeacherAssignments, loadTeacherExams, loadTeacherGradebook, loadTeacherQuestions, loadTeacherResources, loadTeacherSubmissions, publishNotification, publishTeacherAssignment, publishTeacherExam, publishTeacherQuestion, reviewGrade, subjectiveAgentReview, transitionActivity, transitionTeacherAssignment, transitionTeacherExam, transitionTeacherQuestion, transitionTeacherResource, updateTeacherQuestion, uploadTeacherResource } from '../api/client';
import { Metric, PageHead, SectionTitle, TaskRow } from '../ui';
import { activityKindLabel, isOptionlessActivityKind, isSingleConfigurationActivityKind } from '../ui-helpers';
import { useAppStore } from '../state/app';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router';
import { usePlatformData } from '../appData';

export function TeacherPage() {
  const data = usePlatformData();
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [audience, setAudience] = useState('course_all');
  const [publishing, setPublishing] = useState(false);
  const [message, setMessage] = useState('');
  const [gradebook, setGradebook] = useState<Gradebook | null>(null);
  useEffect(() => { void loadTeacherGradebook().then(setGradebook).catch(() => setGradebook(null)); }, []);
  const teacherAverage = gradebook?.assignments.length ? Math.round(gradebook.assignments.reduce((total, item) => total + item.averageRatio, 0) / gradebook.assignments.length) : 0;
  const teacherPending = gradebook?.assignments.reduce((total, item) => total + Math.max(0, item.submittedCount - item.gradedCount), 0) || 0;

  async function publish() {
    if (!title.trim() || !body.trim() || publishing) return;
    setPublishing(true); setMessage('');
    try {
      await publishNotification(title, body, audience, csrfToken, `notification-create:${Date.now()}`);
      setTitle(''); setBody(''); setMessage('通知已发布，目标受众可以在消息中心查看。');
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '通知发布失败，请重试。'); }
    finally { setPublishing(false); }
  }

  return <><PageHead eyebrow="教学空间" title="教师工作台" description="管理课程内容、题目、作业发布和学生学习状态。" action={<div className="page-actions"><button className="button secondary" onClick={() => navigate('/teacher/resources')}><FolderOpen size={16} />管理资料</button><button className="button secondary" onClick={() => navigate('/teacher/exams')}><Clock3 size={16} />管理考试</button><button className="button secondary" onClick={() => navigate('/teacher/activities')}><ListChecks size={16} />管理活动</button><button className="button primary" onClick={() => navigate('/teacher/questions')}><FileText size={16} />创建题目</button></div>} /><div className="teacher-grid"><section className="teacher-summary"><div><span className="eyebrow">课程概览</span><h2>电力系统储能技术</h2><p>6 个章节 · {data.resources.length} 项已登记资源</p></div><div className="teacher-metrics"><span><strong>{gradebook?.students.length ?? '—'}</strong><small>已提交学生</small></span><span><strong>{gradebook ? `${teacherAverage}%` : '—'}</strong><small>平均正确率</small></span><span><strong>{gradebook ? teacherPending : '—'}</strong><small>待批改项</small></span></div></section><section className="section-block"><SectionTitle title="近期作业" link="进入作业管理" onClick={() => navigate('/teacher/assignments')} /><div className="task-list">{data.assignments.slice(0, 3).map((assignment) => <TaskRow key={assignment.id} assignment={assignment} onClick={() => navigate(`/teacher/assignments/${encodeURIComponent(assignment.id)}`)} />)}</div></section><section className="section-block"><SectionTitle title="教学工具" link="管理题库" onClick={() => navigate('/teacher/questions')} /><div className="tool-grid"><Tool icon={<ListChecks />} title="题库与作业" desc="创建题目、组卷和发布任务" onClick={() => navigate('/teacher/questions')} /><Tool icon={<Clock3 />} title="考试管理" desc="设置时间窗、组卷和发布考试" onClick={() => navigate('/teacher/exams')} /><Tool icon={<ListChecks />} title="课堂活动" desc="管理签到、抢答、随机选人和分组" onClick={() => navigate('/teacher/activities')} /><Tool icon={<BarChart3 />} title="学情分析" desc="查看完成率与知识点掌握" onClick={() => navigate('/teacher/gradebook')} /><Tool icon={<MessageSquare />} title="讨论与通知" desc="发布课程互动和公告" onClick={() => navigate('/messages')} /><Tool icon={<FolderOpen />} title="课程资料" desc="上传、替换和归档教材资料" onClick={() => navigate('/teacher/resources')} /></div></section><section className="section-block notification-composer"><SectionTitle title="发布课程通知" link="打开消息中心" onClick={() => navigate('/messages')} /><label>标题<input aria-label="通知标题" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={160} placeholder="例如：本周作业提交提醒" /></label><label>内容<textarea aria-label="通知内容" value={body} onChange={(event) => setBody(event.target.value)} maxLength={8000} placeholder="填写要发送给课程成员的内容" /></label><label>受众<select aria-label="通知受众" value={audience} onChange={(event) => setAudience(event.target.value)}><option value="course_all">全体课程成员</option><option value="course_students">学生</option><option value="course_teachers">教师</option></select></label>{message && <div className="reader-notice">{message}</div>}<button className="button primary" onClick={() => void publish()} disabled={publishing || !title.trim() || !body.trim()}>{publishing ? '发布中…' : '发布通知'}<Send size={16} /></button></section></div></>;
}

export function TeacherActivityManagerPage() {
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [activities, setActivities] = useState<Activity[]>([]);
  const [kind, setKind] = useState<ActivityKind>('poll');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [options, setOptions] = useState('');
  const [status, setStatus] = useState<'draft' | 'published'>('draft');
  const [maxAttempts, setMaxAttempts] = useState('1');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [transitioning, setTransitioning] = useState('');
  const [message, setMessage] = useState('');
  const transitionSequenceRef = useRef(0);
  const transitionInstanceRef = useRef('');

  const reload = useCallback(async () => {
    setLoading(true);
    try { setActivities(await loadActivities()); setMessage(''); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '课堂活动管理暂时不可用。'); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void reload(); }, [reload]);

  async function create() {
    const labels = options.split('\n').map((item) => item.trim()).filter(Boolean);
    const optionless = isOptionlessActivityKind(kind);
    if (!title.trim() || !body.trim() || (!optionless && labels.length < 2) || saving) return;
    if (!optionless && labels.length > 20) { setMessage(kind === 'group_task' ? '分组名称需为 2 到 20 个。' : '选项最多 20 个。'); return; }
    if (!optionless && new Set(labels.map((item) => item.toLocaleLowerCase())).size !== labels.length) { setMessage(kind === 'group_task' ? '分组名称不能重复。' : '选项不能重复。'); return; }
    const attempts = isSingleConfigurationActivityKind(kind) ? 1 : Number(maxAttempts);
    if (!Number.isInteger(attempts) || attempts < 1 || attempts > 3) { setMessage('允许次数需为 1 到 3 次。'); return; }
    setSaving(true); setMessage('');
    try {
      await createActivity({ kind, title: title.trim(), body: body.trim(), options: optionless ? [] : labels.map((label, index) => ({ id: kind === 'group_task' ? `group-${index + 1}` : `option-${index + 1}`, label })), status, maxAttempts: attempts }, csrfToken, `activity-create:${Date.now()}`);
      setTitle(''); setBody(''); setOptions(''); setStatus('draft'); setMaxAttempts('1'); await reload(); setMessage(status === 'published' ? '课堂活动已发布，学生可以在开放活动中看到。' : '课堂活动草稿已保存。');
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '课堂活动创建失败，请重试。'); }
    finally { setSaving(false); }
  }

  async function transition(activity: Activity, action: 'publish' | 'close' | 'reopen') {
    if (transitioning) return;
    if (!transitionInstanceRef.current) {
      transitionInstanceRef.current = globalThis.crypto?.randomUUID?.() || `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
    }
    setTransitioning(`${activity.id}:${action}`); setMessage('');
    try {
      await transitionActivity(activity.id, action, csrfToken, `activity-${action}:${activity.id}:${transitionInstanceRef.current}:${++transitionSequenceRef.current}`);
      await reload();
      setMessage(action === 'publish' ? '课堂活动已发布。' : action === 'close' ? '课堂活动已关闭，学生不能继续提交。' : '课堂活动已重新开放。');
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '课堂活动状态更新失败。'); }
    finally { setTransitioning(''); }
  }

  const statusLabel = (value: Activity['status']) => value === 'published' ? '已发布' : value === 'draft' ? '草稿' : '已关闭';
  const configuredItemCount = options.split('\n').filter((item) => item.trim()).length;
  const hasValidOptions = isOptionlessActivityKind(kind) || (configuredItemCount >= 2 && configuredItemCount <= 20);
  return <><PageHead eyebrow="教师工作台" title="课堂活动管理" description="创建签到、抢答、投票、问卷、随机选人和分组任务，并管理活动状态。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回教师工作台</button>} /><div className="teacher-workspace"><section className="section-block teacher-form-panel activity-management-form"><SectionTitle title="创建课堂活动" link="刷新活动" onClick={() => void reload()} /><div className="form-grid"><label>活动类型<select aria-label="活动类型" value={kind} onChange={(event) => { const next = event.target.value as ActivityKind; setKind(next); if (isOptionlessActivityKind(next)) setOptions(''); if (isSingleConfigurationActivityKind(next)) setMaxAttempts('1'); }}><option value="poll">投票（单选）</option><option value="survey">问卷（可多选）</option><option value="checkin">课堂签到</option><option value="quick_response">课堂抢答</option><option value="random_selection">随机选人</option><option value="group_task">分组任务</option></select></label><label>保存状态<select aria-label="活动保存状态" value={status} onChange={(event) => setStatus(event.target.value as 'draft' | 'published')}><option value="draft">保存草稿</option><option value="published">直接发布</option></select></label><label>允许次数<input aria-label="活动允许次数" type="number" min="1" max="3" value={maxAttempts} disabled={isSingleConfigurationActivityKind(kind)} onChange={(event) => setMaxAttempts(event.target.value)} /></label><label className="form-span">标题<input aria-label="活动标题" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={160} placeholder="例如：储能系统并网控制重点" /></label><label className="form-span">说明<textarea aria-label="活动说明" value={body} onChange={(event) => setBody(event.target.value)} maxLength={8000} placeholder="说明本次活动要检查的知识点" /></label>{!isOptionlessActivityKind(kind) && <label className="form-span">{kind === 'group_task' ? '组名（每行一个，2 到 20 个）' : '选项（每行一个，至少两项）'}<textarea aria-label={kind === 'group_task' ? '分组名称' : '活动选项'} value={options} onChange={(event) => setOptions(event.target.value)} maxLength={4000} placeholder={kind === 'group_task' ? '第一组\n第二组\n第三组' : '功率平衡\n电流控制\n通信协调'} /></label>}</div>{message && <div className="reader-notice conflict" role="status">{message}</div>}<button className="button primary" onClick={() => void create()} disabled={saving || transitioning !== '' || !title.trim() || !body.trim() || !hasValidOptions}>{saving ? '保存中…' : status === 'published' ? '发布课堂活动' : '保存活动草稿'}<ListChecks size={16} /></button></section><section className="section-block"><div className="section-title"><h2>活动列表</h2><button className="icon-button" title="刷新活动列表" aria-label="刷新活动列表" onClick={() => void reload()}><RefreshCw size={16} /></button></div>{loading && <div className="empty-state">正在读取活动…</div>}{!loading && !activities.length && <div className="empty-state">当前没有课堂活动。</div>}{!loading && activities.length > 0 && <div className="teacher-table activity-management-table" role="table" aria-label="活动列表"><div className="teacher-table-head" role="row"><span role="columnheader">活动</span><span role="columnheader">类型</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{activities.map((activity) => <div className="teacher-table-row" key={activity.id} role="row"><div role="cell"><strong>{activity.title}</strong><small>{activity.kind === 'checkin' ? '单次签到记录' : activity.kind === 'quick_response' ? activity.status === 'closed' && !activity.canReopen ? '首位响应已确认' : '等待首位学生响应' : activity.kind === 'random_selection' ? '教师随机抽取 · 单次配置' : activity.kind === 'group_task' ? `${activity.options.length} 个预设组 · 单次配置` : `${activity.options.length} 个选项 · ${activity.maxAttempts} 次机会`}</small></div><span role="cell">{activityKindLabel(activity.kind)}</span><span className={`status-tag ${activity.status === 'published' ? 'active' : ''}`} role="cell">{statusLabel(activity.status)}</span><div className="row-actions" role="cell"><button className="text-button" onClick={() => navigate(`/activities/${encodeURIComponent(activity.id)}`)}>{activity.status === 'draft' ? '预览' : '查看活动'}</button>{activity.status === 'draft' && <button className="text-button" onClick={() => void transition(activity, 'publish')} disabled={transitioning !== ''}>发布</button>}{activity.status === 'published' && <button className="text-button danger" onClick={() => void transition(activity, 'close')} disabled={transitioning !== ''}>关闭</button>}{activity.status === 'closed' && activity.canReopen && <button className="text-button" onClick={() => void transition(activity, 'reopen')} disabled={transitioning !== ''}>重新开放</button>}</div></div>)}</div>}</section></div></>;
}

export function TeacherResourceManagerPage() {
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const chapters = usePlatformData().chapters;
  const [resources, setResources] = useState<TeacherResource[]>([]);
  const [filter, setFilter] = useState('');
  const [title, setTitle] = useState('');
  const [chapterId, setChapterId] = useState('3');
  const [sourceReference, setSourceReference] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const resourceUploadSequenceRef = useRef(0);

  const reload = useCallback(async () => {
    setState('loading');
    try { setResources(await loadTeacherResources(filter)); setState('ready'); setMessage(''); }
    catch (caught) { setState('error'); setMessage(caught instanceof ApiError ? caught.message : '资源列表暂时不可用。'); }
  }, [filter]);
  useEffect(() => { void reload(); }, [reload]);

  async function create() {
    if (!title.trim() || !chapterId || busy) return;
    setBusy('create'); setMessage('');
    try {
      const resource = await createTeacherResource({ title: title.trim(), chapter_id: Number(chapterId), source_reference: sourceReference.trim() }, csrfToken, `teacher-resource-create:${Date.now()}`);
      if (selectedFile) await uploadTeacherResource(resource.id, selectedFile, selectedFile.name, csrfToken, `teacher-resource-upload:${resource.id}:${Date.now()}`);
      setTitle(''); setSourceReference(''); setSelectedFile(null); await reload(); setMessage(selectedFile ? '资源已上传并保存为草稿。' : '资源元数据已创建，请继续上传文件。');
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '资源创建失败，请检查文件和引用。'); }
    finally { setBusy(''); }
  }

  async function upload(resource: TeacherResource, file: File | null) {
    if (!file || busy) return;
    setBusy(`upload:${resource.id}`); setMessage('');
    const idempotencyKey = `teacher-resource-upload:${resource.id}:${++resourceUploadSequenceRef.current}`;
    try { await uploadTeacherResource(resource.id, file, file.name, csrfToken, idempotencyKey); await reload(); setMessage('新修订已上传，资源回到草稿状态。'); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '资源上传失败。'); }
    finally { setBusy(''); }
  }

  async function transition(resource: TeacherResource, action: 'publish' | 'archive') {
    if (busy) return;
    setBusy(`${action}:${resource.id}`); setMessage('');
    try { await transitionTeacherResource(resource.id, action, csrfToken, `teacher-resource-${action}:${resource.id}:${resource.revision}`); await reload(); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '资源状态更新失败。'); }
    finally { setBusy(''); }
  }

  const statusLabel = (status: TeacherResource['status']) => status === 'draft' ? '草稿' : status === 'published' ? '已发布' : '已归档';
  return <><PageHead eyebrow="教师工作台" title="课程资料管理" description="上传、替换、发布和归档课程资料；每次替换都会保留可追溯的修订记录。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回工作台</button>} /><div className="teacher-workspace"><section className="section-block teacher-form-panel"><SectionTitle title="新增课程资料" link="刷新列表" onClick={() => void reload()} /><div className="form-grid"><label className="form-span">资料标题<input aria-label="资料标题" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={180} placeholder="例如：第 3 章并网控制补充讲义" /></label><label>所属章节<select aria-label="所属章节" value={chapterId} onChange={(event) => setChapterId(event.target.value)}>{chapters.map((chapter) => <option key={chapter.id} value={chapter.id}>{chapter.name}</option>)}</select></label><label>来源引用<input aria-label="来源引用" value={sourceReference} onChange={(event) => setSourceReference(event.target.value)} maxLength={240} placeholder="可选：教材、教师补充或课程链接" /></label><label className="form-span">文件<input aria-label="课程资料文件" type="file" accept=".pdf,.md,application/pdf,text/markdown" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} /></label></div>{message && <div className="reader-notice conflict">{message}</div>}<button className="button primary" onClick={() => void create()} disabled={busy !== '' || !title.trim()}>{busy === 'create' ? '创建中…' : '创建资料草稿'}<FileText size={16} /></button></section><section className="section-block"><div className="section-title"><h2>资料版本</h2><div className="inline-controls"><label className="sr-only" htmlFor="resource-status">筛选资源状态</label><select id="resource-status" aria-label="筛选资源状态" value={filter} onChange={(event) => setFilter(event.target.value)}><option value="">全部状态</option><option value="draft">草稿</option><option value="published">已发布</option><option value="archived">已归档</option></select></div></div>{state === 'loading' && <div className="empty-state">正在读取资源列表…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void reload()}>重新加载</button></div>}{state === 'ready' && !resources.length && <div className="empty-state">当前没有符合条件的资源。</div>}{state === 'ready' && resources.length > 0 && <div className="teacher-table resource-management-table" role="table" aria-label="资料版本"><div className="teacher-table-head" role="row"><span role="columnheader">资料</span><span role="columnheader">修订</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{resources.map((resource) => <div className="teacher-table-row" key={resource.id} role="row"><div role="cell"><strong>{resource.title}</strong><small>第 {resource.chapterId} 章 · {resource.sourceReference || '未填写来源'} · {resource.revisions.length} 个文件修订</small></div><span role="cell">v{resource.revision}</span><span className={`status-tag ${resource.status === 'published' ? 'active' : ''}`} role="cell">{statusLabel(resource.status)}</span><div className="row-actions" role="cell"><label className="text-button">替换<input className="sr-only" type="file" accept=".pdf,.md,application/pdf,text/markdown" onChange={(event) => { void upload(resource, event.target.files?.[0] || null); event.currentTarget.value = ''; }} /></label>{resource.status === 'draft' && resource.revision > 0 && <button className="text-button" onClick={() => void transition(resource, 'publish')} disabled={busy !== ''}>发布</button>}{resource.status !== 'archived' && <button className="text-button danger" onClick={() => void transition(resource, 'archive')} disabled={busy !== ''}>归档</button>}</div></div>)}</div>}</section></div></>;
}

export function TeacherQuestionBankPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const chapters = usePlatformData().chapters;
  const [questions, setQuestions] = useState<TeacherQuestion[]>([]);
  const [filter, setFilter] = useState('');
  const [questionType, setQuestionType] = useState<'single_choice' | 'multiple_choice' | 'true_false' | 'short_answer' | 'essay'>('single_choice');
  const [prompt, setPrompt] = useState('');
  const [options, setOptions] = useState('功率平衡\n电流约束\n通信可靠性');
  const [answer, setAnswer] = useState('功率平衡');
  const [rubric, setRubric] = useState('');
  const [maxScore, setMaxScore] = useState('10');
  const [chapterId, setChapterId] = useState('');
  const [message, setMessage] = useState('');
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingVersion, setEditingVersion] = useState(1);
  useEffect(() => {
    const draft = searchParams.get('draft');
    if (draft && !prompt) {
      setPrompt(draft.slice(0, 2000));
      setMessage('Agent 草稿已带入，提交前请检查题干、答案和评分标准。');
    }
  }, [prompt, searchParams]);
  const reload = useCallback(async () => {
    setState('loading');
    try { setQuestions(await loadTeacherQuestions(filter)); setState('ready'); setMessage(''); }
    catch (caught) { setState('error'); setMessage(caught instanceof ApiError ? caught.message : '题库暂时不可用。'); }
  }, [filter]);
  useEffect(() => { void reload(); }, [reload]);

  async function create() {
    if (!prompt.trim() || saving) return;
    setSaving(true); setMessage('');
    const optionList = options.split('\n').map((item) => item.trim()).filter(Boolean);
    const parsedAnswer = questionType === 'true_false' ? answer === 'true' : questionType === 'multiple_choice' ? answer.split(',').map((item) => item.trim()).filter(Boolean) : answer.trim();
    const payload = { question_type: questionType, prompt: prompt.trim(), options: questionType === 'short_answer' || questionType === 'essay' ? [] : optionList, answer: parsedAnswer, rubric: rubric.trim(), max_score: Number(maxScore), chapter_id: chapterId ? Number(chapterId) : null };
    try {
      if (editingId) {
        await updateTeacherQuestion(editingId, { ...payload, base_version: editingVersion }, csrfToken, `teacher-question-update:${editingId}:${editingVersion}`);
        setMessage('题目已更新为草稿。');
      } else {
        await createTeacherQuestion(payload, csrfToken, `teacher-question-create:${Date.now()}`);
      }
      setEditingId(null); setEditingVersion(1); setPrompt(''); setAnswer(questionType === 'true_false' ? 'true' : ''); setRubric(''); await reload();
      setMessage(editingId ? '题目已更新为草稿。' : '题目已保存为草稿，可在列表中发布。');
    } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '题目创建失败，请检查格式。'); }
    finally { setSaving(false); }
  }

  async function publish(question: TeacherQuestion) {
    try { await publishTeacherQuestion(question.id, csrfToken, `teacher-question-publish:${question.id}`); await reload(); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '题目发布失败。'); }
  }

  async function transition(question: TeacherQuestion, action: 'withdraw' | 'archive') {
    try { await transitionTeacherQuestion(question.id, action, csrfToken, `teacher-question-${action}:${question.id}`); await reload(); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '题目状态更新失败。'); }
  }

  function edit(question: TeacherQuestion) {
    setEditingId(question.id); setEditingVersion(question.version); setQuestionType(question.questionType); setPrompt(question.prompt); setOptions(question.options.join('\n')); setAnswer(Array.isArray(question.answer) ? question.answer.join(',') : question.answer === null ? '' : String(question.answer)); setRubric(question.rubric); setMaxScore(String(question.maxScore)); setChapterId(question.chapterId ? String(question.chapterId) : ''); setMessage(`正在编辑题目 v${question.version}，保存时会检查版本冲突。`); window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function cancelEdit() { setEditingId(null); setEditingVersion(1); setPrompt(''); setAnswer(''); setRubric(''); setMessage('已取消编辑。'); }

  const objective = questionType !== 'short_answer' && questionType !== 'essay';
  return <><PageHead eyebrow="教师工作台" title="题库管理" description="创建、审核和发布课程题目；已发布题目才能被作业引用。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回工作台</button>} /><div className="teacher-workspace"><section className="section-block teacher-form-panel"><SectionTitle title={editingId ? '编辑题目草稿' : '创建题目'} link="刷新题库" onClick={() => void reload()} /><div className="form-grid"><label>题型<select aria-label="题型" value={questionType} onChange={(event) => setQuestionType(event.target.value as typeof questionType)} disabled={Boolean(editingId)}><option value="single_choice">单选题</option><option value="multiple_choice">多选题</option><option value="true_false">判断题</option><option value="short_answer">简答题</option><option value="essay">论述题</option></select></label><label>分值<input aria-label="题目分值" type="number" min="1" max="100" value={maxScore} onChange={(event) => setMaxScore(event.target.value)} /></label><label>章节<select aria-label="题目章节" value={chapterId} onChange={(event) => setChapterId(event.target.value)}><option value="">未指定章节</option>{chapters.map((chapter) => <option key={chapter.id} value={chapter.id}>{chapter.name}</option>)}</select></label><label className="form-span">题干<textarea aria-label="题干" value={prompt} onChange={(event) => setPrompt(event.target.value)} maxLength={2000} placeholder="输入教师确认后的题目内容" /></label>{objective && <label>选项（每行一项）<textarea aria-label="题目选项" value={options} onChange={(event) => setOptions(event.target.value)} /></label>}{objective ? <label>正确答案{questionType === 'true_false' ? <select aria-label="正确答案" value={answer} onChange={(event) => setAnswer(event.target.value)}><option value="true">正确</option><option value="false">错误</option></select> : <input aria-label="正确答案" value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder={questionType === 'multiple_choice' ? '多个答案用英文逗号分隔' : '填写一个选项'} />}</label> : <label>评分标准<textarea aria-label="评分标准" value={rubric} onChange={(event) => setRubric(event.target.value)} placeholder="说明答案应包含的要点，供教师复核和 Agent 初评参考" /></label>}</div>{message && <div className="reader-notice conflict">{message}</div>}<button className="button primary" onClick={() => void create()} disabled={saving || !prompt.trim()}>{saving ? '保存中…' : editingId ? '保存编辑' : '保存为草稿'}<FileText size={16} /></button>{editingId && <button className="button quiet" onClick={cancelEdit}>取消编辑<X size={15} /></button>}</section><section className="section-block"><div className="section-title"><h2>题库</h2><div className="inline-controls"><label className="sr-only" htmlFor="question-status">筛选状态</label><select id="question-status" aria-label="筛选题目状态" value={filter} onChange={(event) => setFilter(event.target.value)}><option value="">全部状态</option><option value="draft">草稿</option><option value="published">已发布</option><option value="withdrawn">已撤回</option><option value="archived">已归档</option></select></div></div>{state === 'loading' && <div className="empty-state">正在读取题库…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void reload()}>重新加载</button></div>}{state === 'ready' && !questions.length && <div className="empty-state">当前筛选没有题目。</div>}{state === 'ready' && questions.length > 0 && <div className="teacher-table" role="table" aria-label="题库"><div className="teacher-table-head" role="row"><span role="columnheader">题目</span><span role="columnheader">类型</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{questions.map((question) => <div className="teacher-table-row" key={question.id} role="row"><div role="cell"><strong>{question.prompt}</strong><small>{question.chapterName || '未指定章节'} · {question.maxScore} 分 · v{question.version}</small></div><span role="cell">{question.questionType === 'single_choice' ? '单选' : question.questionType === 'multiple_choice' ? '多选' : question.questionType === 'true_false' ? '判断' : question.questionType === 'short_answer' ? '简答' : '论述'}</span><span className={`status-tag ${question.status === 'published' ? 'active' : ''}`} role="cell">{question.status === 'draft' ? '草稿' : question.status === 'published' ? '已发布' : question.status === 'withdrawn' ? '已撤回' : '已归档'}</span><div className="row-actions" role="cell">{question.status === 'draft' && <><button className="text-button" onClick={() => edit(question)}>编辑</button><button className="text-button" onClick={() => void publish(question)}>发布</button></>}{question.status === 'published' && <button className="text-button" onClick={() => void transition(question, 'withdraw')}>撤回</button>}{question.status !== 'archived' && <button className="text-button danger" onClick={() => void transition(question, 'archive')}>归档</button>}</div></div>)}</div>}</section></div></>;
}

export function TeacherAssignmentManagerPage() {
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [questions, setQuestions] = useState<TeacherQuestion[]>([]);
  const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [dueAt, setDueAt] = useState('');
  const [attempts, setAttempts] = useState('1');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const reload = useCallback(async () => {
    setLoading(true);
    try { const [availableQuestions, availableAssignments] = await Promise.all([loadTeacherQuestions('published'), loadTeacherAssignments()]); setQuestions(availableQuestions); setAssignments(availableAssignments); setMessage(''); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '作业管理暂时不可用。'); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void reload(); }, [reload]);
  function toggle(questionId: string) { setSelected((current) => current.includes(questionId) ? current.filter((item) => item !== questionId) : [...current, questionId]); }
  async function create() {
    if (!title.trim() || !selected.length || saving) return;
    setSaving(true); setMessage('');
    try { await createTeacherAssignment({ title: title.trim(), question_ids: selected, due_at: dueAt ? new Date(dueAt).toISOString() : null, allow_attempts: Number(attempts) }, csrfToken, `teacher-assignment-create:${Date.now()}`); setTitle(''); setSelected([]); setDueAt(''); await reload(); setMessage('作业已保存为草稿。'); }
    catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '作业创建失败。'); }
    finally { setSaving(false); }
  }
  async function publish(assignment: TeacherAssignment) { try { await publishTeacherAssignment(assignment.id, csrfToken, `teacher-assignment-publish:${assignment.id}`); await reload(); } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '作业发布失败。'); } }
  async function transition(assignment: TeacherAssignment, action: 'withdraw' | 'archive') { try { await transitionTeacherAssignment(assignment.id, action, csrfToken, `teacher-assignment-${action}:${assignment.id}`); await reload(); } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '作业状态更新失败。'); } }
  return <><PageHead eyebrow="教师工作台" title="作业发布" description="从已发布题目组卷，保存草稿后再发布到学生任务中心。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回工作台</button>} /><div className="teacher-workspace"><section className="section-block"><SectionTitle title="可用题目" link="打开题库" onClick={() => navigate('/teacher/questions')} />{loading && <div className="empty-state">正在读取题目…</div>}{!loading && !questions.length && <div className="empty-state">暂无已发布题目，请先完成题库审核。</div>}{!loading && <div className="selection-list">{questions.map((question) => <label className="selection-row" key={question.id}><input type="checkbox" checked={selected.includes(question.id)} onChange={() => toggle(question.id)} /><span><strong>{question.prompt}</strong><small>{question.chapterName || '未指定章节'} · {question.maxScore} 分</small></span></label>)}</div>}</section><section className="section-block teacher-form-panel"><SectionTitle title="创建作业草稿" link="刷新" onClick={() => void reload()} /><div className="form-grid"><label className="form-span">标题<input aria-label="作业标题" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={160} placeholder="例如：第 3 章并网控制练习" /></label><label>截止时间<input aria-label="作业截止时间" type="datetime-local" value={dueAt} onChange={(event) => setDueAt(event.target.value)} /></label><label>允许次数<input aria-label="允许提交次数" type="number" min="1" max="10" value={attempts} onChange={(event) => setAttempts(event.target.value)} /></label></div><p className="form-help">已选择 {selected.length} 道题目。发布后学生只能看到题目内容，答案和评分标准仍保留在教师端。</p>{message && <div className="reader-notice conflict">{message}</div>}<button className="button primary" onClick={() => void create()} disabled={saving || !title.trim() || !selected.length}>{saving ? '保存中…' : '保存作业草稿'}<FileText size={16} /></button></section><section className="section-block"><SectionTitle title="作业列表" link="打开成绩册" onClick={() => navigate('/teacher/gradebook')} />{!loading && !assignments.length && <div className="empty-state">当前没有作业。</div>}{assignments.length > 0 && <div className="teacher-table" role="table" aria-label="作业列表"><div className="teacher-table-head" role="row"><span role="columnheader">作业</span><span role="columnheader">题目数</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{assignments.map((assignment) => <div className="teacher-table-row" key={assignment.id} role="row"><div role="cell"><strong>{assignment.title}</strong><small>{assignment.dueAt} · {assignment.allowAttempts} 次机会</small></div><span role="cell">{assignment.questionCount}</span><span className={`status-tag ${assignment.status === 'published' ? 'active' : ''}`} role="cell">{assignment.status === 'draft' ? '草稿' : assignment.status === 'published' ? '已发布' : assignment.status === 'withdrawn' ? '已撤回' : '已归档'}</span><div className="row-actions" role="cell">{assignment.status === 'draft' && <button className="text-button" onClick={() => void publish(assignment)}>发布</button>}{assignment.status === 'published' && <><button className="text-button" onClick={() => navigate(`/teacher/assignments/${encodeURIComponent(assignment.id)}`)}>批改</button><button className="text-button" onClick={() => void transition(assignment, 'withdraw')}>撤回</button></>}{assignment.status !== 'archived' && <button className="text-button danger" onClick={() => void transition(assignment, 'archive')}>归档</button>}</div></div>)}</div>}</section></div></>;
}

export function TeacherExamManagerPage() {
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [questions, setQuestions] = useState<TeacherQuestion[]>([]);
  const [exams, setExams] = useState<TeacherExam[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [openAt, setOpenAt] = useState('');
  const [closeAt, setCloseAt] = useState('');
  const [durationMinutes, setDurationMinutes] = useState('30');
  const [attempts, setAttempts] = useState('1');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const createSequenceRef = useRef(0);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const [availableQuestions, availableExams] = await Promise.all([loadTeacherQuestions('published'), loadTeacherExams()]);
      setQuestions(availableQuestions);
      setExams(availableExams);
      setMessage('');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '考试管理暂时不可用。');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void reload(); }, [reload]);

  function toggle(questionId: string) {
    setSelected((current) => current.includes(questionId) ? current.filter((item) => item !== questionId) : [...current, questionId]);
  }

  function formatTime(value: string) {
    if (!value) return '未设置';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? '时间无效' : date.toLocaleString('zh-CN', { hour12: false });
  }

  function statusLabel(status: TeacherExam['status']) {
    return status === 'draft' ? '草稿' : status === 'published' ? '已发布' : status === 'withdrawn' ? '已撤回' : '已归档';
  }

  async function create() {
    if (!title.trim() || !selected.length || !openAt || !closeAt || busy) return;
    const openDate = new Date(openAt);
    const closeDate = new Date(closeAt);
    const duration = Number(durationMinutes);
    const allowedAttempts = Number(attempts);
    if (Number.isNaN(openDate.getTime()) || Number.isNaN(closeDate.getTime()) || closeDate <= openDate) {
      setMessage('开放时间必须早于结束时间。');
      return;
    }
    if (!Number.isInteger(duration) || duration < 1 || duration > 1440 || !Number.isInteger(allowedAttempts) || allowedAttempts < 1 || allowedAttempts > 10) {
      setMessage('考试时长需为 1 到 1440 分钟，允许次数需为 1 到 10 次。');
      return;
    }
    setBusy('create');
    setMessage('');
    try {
      await createTeacherExam({ title: title.trim(), question_ids: selected, open_at: openDate.toISOString(), close_at: closeDate.toISOString(), duration_seconds: duration * 60, allow_attempts: allowedAttempts }, csrfToken, `teacher-exam-create:${++createSequenceRef.current}`);
      setTitle('');
      setOpenAt('');
      setCloseAt('');
      setSelected([]);
      await reload();
      setMessage('考试已保存为草稿，请核对配置后发布。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '考试创建失败，请检查题目和时间配置。');
    } finally {
      setBusy('');
    }
  }

  async function publish(exam: TeacherExam) {
    if (busy) return;
    setBusy(exam.id);
    setMessage('');
    try {
      await publishTeacherExam(exam.id, csrfToken, `teacher-exam-publish:${exam.id}`);
      await reload();
      setMessage('考试已发布，学生将在开放时间内看到。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '考试发布失败。');
    } finally {
      setBusy('');
    }
  }

  async function transition(exam: TeacherExam, action: 'withdraw' | 'archive') {
    if (busy) return;
    setBusy(exam.id);
    setMessage('');
    try {
      await transitionTeacherExam(exam.id, action, csrfToken, `teacher-exam-${action}:${exam.id}`);
      await reload();
      setMessage(action === 'withdraw' ? '考试已撤回。' : '考试已归档。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '考试状态更新失败。');
    } finally {
      setBusy('');
    }
  }

  return <><PageHead eyebrow="教师工作台" title="考试管理" description="从已发布题目组卷，配置服务端时间窗和尝试次数，保存草稿后再发布。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回教师工作台</button>} /><div className="teacher-workspace"><section className="section-block"><SectionTitle title="可用题目" link="打开题库" onClick={() => navigate('/teacher/questions')} />{loading && <div className="empty-state">正在读取题目…</div>}{!loading && !questions.length && <div className="empty-state">暂无已发布题目，请先完成题库审核。</div>}{!loading && questions.length > 0 && <div className="selection-list">{questions.map((question) => <label className="selection-row" key={question.id}><input type="checkbox" checked={selected.includes(question.id)} onChange={() => toggle(question.id)} /><span><strong>{question.prompt}</strong><small>{question.chapterName || '未指定章节'} · {question.maxScore} 分</small></span></label>)}</div>}</section><section className="section-block teacher-form-panel"><SectionTitle title="创建考试草稿" link="刷新" onClick={() => void reload()} /><div className="form-grid"><label className="form-span">考试标题<input aria-label="考试标题" value={title} onChange={(event) => setTitle(event.target.value)} maxLength={180} placeholder="例如：第 3 章储能系统阶段考试" /></label><label>开放时间<input aria-label="考试开放时间" type="datetime-local" value={openAt} onChange={(event) => setOpenAt(event.target.value)} /></label><label>结束时间<input aria-label="考试结束时间" type="datetime-local" value={closeAt} onChange={(event) => setCloseAt(event.target.value)} /></label><label>考试时长（分钟）<input aria-label="考试时长" type="number" min="1" max="1440" value={durationMinutes} onChange={(event) => setDurationMinutes(event.target.value)} /></label><label>允许次数<input aria-label="考试允许次数" type="number" min="1" max="10" value={attempts} onChange={(event) => setAttempts(event.target.value)} /></label></div><p className="form-help">已选择 {selected.length} 道题目。服务端负责裁决开放时间、截止时间和尝试次数。</p>{message && <div className="reader-notice conflict" role="alert">{message}</div>}<button className="button primary" onClick={() => void create()} disabled={Boolean(busy) || !title.trim() || !selected.length || !openAt || !closeAt}>{busy === 'create' ? '保存中…' : '保存考试草稿'}<FileText size={16} /></button></section><section className="section-block"><div className="section-title"><h2>考试列表</h2><button className="icon-button" title="刷新考试列表" aria-label="刷新考试列表" onClick={() => void reload()}><RefreshCw size={16} /></button></div>{loading && <div className="empty-state">正在读取考试…</div>}{!loading && !exams.length && <div className="empty-state">当前没有考试。</div>}{!loading && exams.length > 0 && <div className="teacher-table" role="table" aria-label="考试列表"><div className="teacher-table-head" role="row"><span role="columnheader">考试</span><span role="columnheader">时间</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{exams.map((exam) => <div className="teacher-table-row" key={exam.id} role="row"><div role="cell"><strong>{exam.title}</strong><small>{exam.questionCount} 道题 · {Math.round(exam.durationSeconds / 60)} 分钟 · {exam.allowAttempts} 次机会</small></div><span role="cell"><small>开放 {formatTime(exam.openAt)}</small><small>结束 {formatTime(exam.closeAt)}</small></span><span className={`status-tag ${exam.status === 'published' ? 'active' : ''}`} role="cell">{statusLabel(exam.status)}</span><div className="row-actions" role="cell">{exam.status === 'draft' && <button className="text-button" onClick={() => void publish(exam)} disabled={Boolean(busy)}>发布</button>}{exam.status === 'published' && <button className="text-button" onClick={() => void transition(exam, 'withdraw')} disabled={Boolean(busy)}>撤回</button>}{exam.status !== 'archived' && <button className="text-button danger" onClick={() => void transition(exam, 'archive')} disabled={Boolean(busy)}>归档</button>}{exam.status === 'withdrawn' && <button className="text-button" onClick={() => void publish(exam)} disabled={Boolean(busy)}>重新发布</button>}</div></div>)}</div>}</section></div></>;
}

export function TeacherGradebookPage() {
  function exportGradebookCsv(gradebook: Gradebook): { filename: string; content: string } {
    const escape = (value: string | number): string => {
      const text = String(value);
      return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
    };
    const rows: Array<Array<string | number>> = [];
    rows.push(['作业成绩汇总']);
    rows.push(['作业', '题数', '状态', '已提交', '已批改', '完成率', '平均成绩', '平均正确率']);
    gradebook.assignments.forEach((item) => {
      rows.push([item.title, item.questionCount, item.status, item.submittedCount, item.gradedCount, `${item.completionRate}%`, item.averageScore, `${item.averageRatio}%`]);
    });
    rows.push([]);
    rows.push(['学生汇总']);
    rows.push(['学生', '提交次数', '已完成作业', '平均正确率', '需要关注']);
    gradebook.students.forEach((student) => {
      rows.push([student.userUid, student.submissionCount, student.completedAssignments, `${student.averageRatio}%`, student.riskLevel === 'high' ? '是' : '否']);
    });
    rows.push([]);
    rows.push(['知识点掌握']);
    rows.push(['知识点', '状态', '掌握度']);
    gradebook.knowledgePoints.forEach((point) => {
      rows.push([point.name, point.status, `${point.ratio}%`]);
    });
    const content = `\uFEFF${rows.map((row) => row.map(escape).join(',')).join('\r\n')}`;
    const date = new Date().toISOString().slice(0, 10);
    return { filename: `成绩册-${date}.csv`, content };
  }

  function downloadGradebookCsv(gradebook: Gradebook) {
    const { filename, content } = exportGradebookCsv(gradebook);
    const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const navigate = useNavigate();
  const [gradebook, setGradebook] = useState<Gradebook | null>(null);
  const [assignmentId, setAssignmentId] = useState('');
  const [message, setMessage] = useState('');
  const load = useCallback(async () => { try { setGradebook(await loadTeacherGradebook(assignmentId)); setMessage(''); } catch (caught) { setMessage(caught instanceof ApiError ? caught.message : '成绩册暂时不可用。'); } }, [assignmentId]);
  useEffect(() => { void load(); }, [load]);
  const average = gradebook?.assignments.length ? Math.round(gradebook.assignments.reduce((total, item) => total + item.averageRatio, 0) / gradebook.assignments.length) : 0;
  return <><PageHead eyebrow="教师工作台" title="成绩册与学情" description="查看作业提交、成绩汇总、知识点掌握和需要关注的学生。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回工作台</button>} />{message && <div className="reader-notice conflict">{message}</div>}{gradebook && <><div className="metric-grid teacher-grade-metrics"><Metric icon={<ListChecks />} value={String(gradebook.assignments.length)} label="作业" tone="blue" /><Metric icon={<Users />} value={String(gradebook.students.length)} label="提交学生" tone="green" /><Metric icon={<BarChart3 />} value={`${average}`} label="平均正确率" tone="gold" suffix="%" /><Metric icon={<AlertTriangle />} value={String(gradebook.riskStudents.length)} label="需要关注" tone="orange" /></div><section className="section-block"><div className="section-title"><h2>作业成绩汇总</h2><div className="inline-controls"><label className="sr-only" htmlFor="gradebook-assignment">筛选作业</label><select id="gradebook-assignment" aria-label="筛选成绩册作业" value={assignmentId} onChange={(event) => setAssignmentId(event.target.value)}><option value="">全部作业</option>{gradebook.assignments.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select><button className="icon-button" title="刷新成绩册" aria-label="刷新成绩册" onClick={() => void load()}><RefreshCw size={16} /></button><button className="button quiet" onClick={() => downloadGradebookCsv(gradebook)}>导出 CSV<Download size={15} /></button></div></div><div className="teacher-table" role="table" aria-label="作业成绩汇总"><div className="teacher-table-head" role="row"><span role="columnheader">作业</span><span role="columnheader">提交/批改</span><span role="columnheader">完成率</span><span role="columnheader">平均成绩</span></div>{gradebook.assignments.map((item) => <div className="teacher-table-row" key={item.id} role="row"><div role="cell"><strong>{item.title}</strong><small>{item.questionCount} 道题 · {item.status}</small></div><span role="cell">{item.submittedCount} / {item.gradedCount}</span><span role="cell">{item.completionRate}%</span><span role="cell">{item.averageScore} · {item.averageRatio}%</span></div>)}</div></section><div className="dashboard-grid"><section className="section-block"><SectionTitle title="风险学生" link="刷新" onClick={() => void load()} />{!gradebook.riskStudents.length ? <div className="empty-state">当前没有需要重点关注的提交。</div> : <div className="risk-list">{gradebook.riskStudents.map((student) => <div className="risk-row" key={student.userUid}><span className="status-tag">重点关注</span><div><strong>{student.userUid}</strong><small>{student.submissionCount} 次提交 · 平均 {student.averageRatio}%{student.needsReview ? ' · 待复核' : ''}</small></div></div>)}</div>}</section><section className="section-block"><SectionTitle title="知识点掌握" link="打开学习图谱" onClick={() => navigate('/profile')} />{!gradebook.knowledgePoints.length ? <div className="empty-state">完成批改后会显示知识点统计。</div> : <div className="mastery-list">{gradebook.knowledgePoints.slice(0, 8).map((point) => <div className="mastery-row" key={point.id}><div><strong>{point.name}</strong><small>{point.status === 'mastered' ? '已掌握' : point.status === 'weak' ? '薄弱' : '学习中'}</small></div><div className="progress-line"><span style={{ width: `${point.ratio}%` }} /></div><strong>{point.ratio}%</strong></div>)}</div>}</section></div></>}</>;
}

export function TeacherAssignmentPage() {
  const { assignmentId = '' } = useParams();
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [assignment, setAssignment] = useState<AssignmentDetail | null>(null);
  const [submissions, setSubmissions] = useState<AssignmentSubmission[]>([]);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const [busy, setBusy] = useState('');

  const reload = useCallback(async () => {
    setState('loading');
    try {
      const [loaded, rows] = await Promise.all([loadAssignment(assignmentId), loadTeacherSubmissions(assignmentId)]);
      setAssignment(loaded); setSubmissions(rows); setState('ready'); setErrorMessage('');
    } catch (caught) {
      setState('error'); setErrorMessage(caught instanceof ApiError ? caught.message : '批改数据暂时不可用。');
    }
  }, [assignmentId]);

  useEffect(() => { void reload(); }, [reload]);

  async function runBatchGrade() {
    setBusy('batch');
    try { await gradeAssignment(assignmentId, csrfToken, `assignment-grade:${assignmentId}`); await reload(); }
    catch (caught) { setErrorMessage(caught instanceof ApiError ? caught.message : '批量批改未完成。'); }
    finally { setBusy(''); }
  }

  async function runGrade(submissionId: string) {
    setBusy(submissionId);
    try { await gradeSubmission(assignmentId, submissionId, csrfToken, `submission-grade:${submissionId}`); await reload(); }
    catch (caught) { setErrorMessage(caught instanceof ApiError ? caught.message : '批改未完成。'); }
    finally { setBusy(''); }
  }

  async function runAgentReview(submissionId: string, questionId: string) {
    setBusy(`${submissionId}:${questionId}`);
    try { await subjectiveAgentReview(assignmentId, submissionId, questionId, csrfToken, `subjective-review:${submissionId}:${questionId}`); await reload(); }
    catch (caught) { setErrorMessage(caught instanceof ApiError ? caught.message : 'Agent 初评未完成，请转人工复核。'); }
    finally { setBusy(''); }
  }

  async function confirmReview(grade: AssignmentGrade) {
    const reason = window.prompt('填写教师复核说明', '教师已复核该成绩项')?.trim();
    if (!reason) return;
    setBusy(`review:${grade.id}`);
    try { await reviewGrade(grade.id, grade.score, reason, csrfToken, `grade-review:${grade.id}:${grade.score}`); await reload(); }
    catch (caught) { setErrorMessage(caught instanceof ApiError ? caught.message : '成绩复核未完成。'); }
    finally { setBusy(''); }
  }

  if (state === 'loading') return <><PageHead eyebrow="批改中心" title="正在读取提交" description="正在读取作业、提交和评分状态。" /><div className="empty-state">正在读取批改数据…</div></>;
  if (state === 'error' || !assignment) return <><PageHead eyebrow="批改中心" title="无法打开批改中心" description="服务端没有返回可核验的提交数据。" action={<button className="button secondary" onClick={() => navigate('/teacher')}><ArrowLeft size={16} />返回教师工作台</button>} /><div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{errorMessage}</strong><button className="button secondary" onClick={() => void reload()}><RefreshCw size={16} />重新加载</button></div></>;
  return <><PageHead eyebrow="批改中心" title={assignment.title} description={`${submissions.length} 份提交 · 题目答案、客观评分和主观复核分开显示。`} action={<div className="page-actions"><button className="button secondary" onClick={() => void reload()}><RefreshCw size={16} />刷新</button><button className="button primary" onClick={() => void runBatchGrade()} disabled={busy !== ''}>{busy === 'batch' ? '批改中…' : '批量自动评分'}<CheckCircle2 size={16} /></button></div>} />{errorMessage && <div className="reader-notice conflict">{errorMessage}</div>}<div className="grading-list">{submissions.length === 0 && <div className="empty-state">当前作业还没有学生提交。</div>}{submissions.map((submission) => <SubmissionReview key={submission.id} submission={submission} questions={assignment.questions} busy={busy} onGrade={() => void runGrade(submission.id)} onAgentReview={(questionId) => void runAgentReview(submission.id, questionId)} onConfirmReview={(grade) => void confirmReview(grade)} />)}</div></>;
}

function SubmissionReview({ submission, questions, busy, onGrade, onAgentReview, onConfirmReview }: { submission: AssignmentSubmission; questions: AssignmentQuestion[]; busy: string; onGrade: () => void; onAgentReview: (questionId: string) => void; onConfirmReview: (grade: AssignmentGrade) => void }) {
  return <article className="submission-card"><div className="submission-header"><div><span className="side-kicker">提交 {submission.attempt} · {submission.id}</span><h2>{submission.score === null ? '等待评分' : `${submission.score} / ${submission.maxScore}`}</h2><small>{submission.createdAt || '时间由服务端记录'} · {submission.needsReview ? '等待教师复核' : submission.status}</small></div><button className="button secondary" onClick={onGrade} disabled={busy !== ''}>{busy === submission.id ? '评分中…' : '重新评分'}<CheckCircle2 size={15} /></button></div><div className="submission-questions">{questions.map((question) => { const answer = submission.answers?.[question.id]; const grade = submission.grades.find((item) => item.questionId === question.id); const reviewBusy = `${submission.id}:${question.id}` === busy; return <div className="submission-question" key={question.id}><div><strong>{question.prompt}</strong><p>{Array.isArray(answer) ? answer.join('、') : String(answer ?? '未作答')}</p></div><div className="grade-cell">{grade ? <><strong>{grade.score} / {grade.maxScore}</strong><small>{grade.source === 'agent_initial' ? 'Agent 初评，待教师复核' : grade.source === 'teacher_review' ? '教师已复核' : '客观题自动评分'}</small><div className="grade-actions">{(question.questionType === 'short_answer' || question.questionType === 'essay') && grade.source !== 'teacher_review' && <button className="text-button" onClick={() => onConfirmReview(grade)} disabled={busy !== ''}>确认复核</button>}{(question.questionType === 'short_answer' || question.questionType === 'essay') && grade.source !== 'teacher_review' && <button className="text-button" onClick={() => onAgentReview(question.id)} disabled={busy !== ''}>{reviewBusy ? '初评中…' : '请求 Agent 初评'}</button>}</div></> : <small>尚未评分</small>}</div></div>; })}</div></article>;
}

function Tool({ icon, title, desc, onClick }: { icon: React.ReactNode; title: string; desc: string; onClick: () => void }) { return <button className="tool-item" onClick={onClick}><span>{icon}</span><strong>{title}</strong><small>{desc}</small><ChevronRight size={15} /></button>; }
