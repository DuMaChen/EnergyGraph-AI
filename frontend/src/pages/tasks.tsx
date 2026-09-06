/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { ApiError, loadTasks } from '../api/client';
import { PageHead } from '../ui';
import { previewStudentTaskCounts, previewStudentTasks, studentTaskKinds, studentTaskStatuses } from '../ui-helpers';
import { StudentTask, StudentTaskKind, StudentTaskList, StudentTaskStatus } from '../types';
import { useAppStore } from '../state/app';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router';

export function TasksPage() {
  const preview = useAppStore((state) => state.preview);
  const navigate = useNavigate();
  const [kind, setKind] = useState<'' | StudentTaskKind>('');
  const [statusFilter, setStatusFilter] = useState<'' | StudentTaskStatus>('');
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [result, setResult] = useState<StudentTaskList>({ items: preview ? previewStudentTasks : [], page: 1, pageSize, total: preview ? previewStudentTasks.length : 0, counts: previewStudentTaskCounts });
  const [state, setState] = useState<'loading' | 'ready' | 'error'>(preview ? 'ready' : 'loading');
  const [message, setMessage] = useState('');
  const loadSequence = useRef(0);
  const totalPages = Math.max(1, Math.ceil(result.total / pageSize));

  const load = useCallback(async () => {
    const sequence = ++loadSequence.current;
    setState('loading');
    setMessage('');
    if (preview) {
      const filtered = previewStudentTasks.filter((item) => (!kind || item.kind === kind) && (!statusFilter || item.status === statusFilter));
      const start = (page - 1) * pageSize;
      if (sequence !== loadSequence.current) return;
      setResult({ items: filtered.slice(start, start + pageSize), page, pageSize, total: filtered.length, counts: previewStudentTaskCounts });
      setState('ready');
      return;
    }
    try {
      const loaded = await loadTasks({ kind: kind || undefined, status: statusFilter || undefined, page, pageSize });
      if (sequence !== loadSequence.current) return;
      setResult(loaded);
      setState('ready');
    } catch (caught) {
      if (sequence !== loadSequence.current) return;
      setResult((current) => ({ ...current, items: [], total: 0 }));
      setMessage(caught instanceof ApiError ? caught.message : '任务中心暂时不可用。');
      setState('error');
    }
  }, [kind, page, preview, statusFilter]);

  useEffect(() => {
    void load();
    return () => { loadSequence.current += 1; };
  }, [load]);

  function taskPath(task: StudentTask) {
    if (task.kind === 'assignment') return `/tasks/${encodeURIComponent(task.sourceId)}`;
    if (task.kind === 'exam') return `/exams/${encodeURIComponent(task.sourceId)}`;
    if (task.kind === 'discussion') return `/discussions/${encodeURIComponent(task.sourceId)}`;
    return `/messages?notice=${encodeURIComponent(task.sourceId)}`;
  }

  function taskAction(task: StudentTask) {
    if (task.kind === 'notification' || task.status === 'completed' || task.status === 'expired') return '查看';
    if (task.kind === 'discussion') return '参与';
    return task.status === 'in_progress' ? '继续' : '开始';
  }

  function formatTaskTime(value: string | null) {
    if (!value) return '无截止时间';
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? '时间待同步' : parsed.toLocaleString('zh-CN', { hour12: false });
  }

  const allCount = Object.values(result.counts.byKind).reduce((sum, count) => sum + count, 0);
  return <>
    <PageHead eyebrow="任务中心" title="待办任务" description="作业、考试、讨论和通知由课程服务端统一计算状态与顺序。" action={<button className="button secondary" type="button" onClick={() => void load()} disabled={state === 'loading'}><RefreshCw size={16} className={state === 'loading' ? 'spin' : ''} />{state === 'loading' ? '刷新中…' : '刷新状态'}</button>} />
    <section className="task-center-controls" aria-label="任务筛选">
      <div className="task-kind-filters" role="group" aria-label="任务类型">
        {studentTaskKinds.map((item) => <button type="button" key={item.value || 'all'} className={kind === item.value ? 'active' : ''} aria-pressed={kind === item.value} onClick={() => { setKind(item.value); setPage(1); }}>{item.label}<small>{item.value ? result.counts.byKind[item.value] : allCount}</small></button>)}
      </div>
      <span className="task-center-summary">当前筛选 {result.total} 项</span>
    </section>
    <div className="filter-tabs" role="tablist" aria-label="任务状态">
      {studentTaskStatuses.map((item) => <button type="button" role="tab" aria-selected={statusFilter === item.value} key={item.value || 'all'} className={statusFilter === item.value ? 'active' : ''} onClick={() => { setStatusFilter(item.value); setPage(1); }}>{item.label}{item.value && <small>{result.counts.byStatus[item.value]}</small>}</button>)}
    </div>
    {state === 'loading' && <div className="route-loading" role="status"><RefreshCw size={18} className="spin" />正在读取任务状态…</div>}
    {state === 'error' && <div className="error-state" role="alert"><AlertTriangle size={18} /><div><strong>任务中心加载失败</strong><span>{message}</span></div><button className="button secondary" type="button" onClick={() => void load()}><RefreshCw size={15} />重试</button></div>}
    {state === 'ready' && <div className="task-table" aria-busy="false" role="table" aria-label="任务列表"><div className="task-table-head" role="row"><span role="columnheader">任务</span><span role="columnheader">截止时间</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{result.items.map((task) => <div className="task-table-row task-center-row" key={task.id} role="row"><div role="cell"><span className="table-kind">{studentTaskKinds.find((item) => item.value === task.kind)?.label}</span><strong>{task.title}</strong><small className="task-summary">{task.summary || `进度 ${task.progress}%`}</small></div><span className="task-time" role="cell">{formatTaskTime(task.dueAt)}</span><span className={`status-tag ${task.status === 'in_progress' || task.status === 'completed' ? 'active' : ''}`} role="cell">{studentTaskStatuses.find((item) => item.value === task.status)?.label}</span><span className="task-table-actions" role="cell"><button className="button quiet" type="button" onClick={() => navigate(taskPath(task))}>{taskAction(task)}<ChevronRight size={15} /></button></span></div>)}{!result.items.length && <div className="task-table-row empty-row" role="row"><div className="empty-state" role="cell">当前筛选下没有任务。</div></div>}</div>}
    {state === 'ready' && totalPages > 1 && <nav className="course-pagination" aria-label="任务列表分页"><span>第 {page} / {totalPages} 页，共 {result.total} 项</span><button className="icon-button" type="button" aria-label="任务上一页" title="上一页" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}><ChevronLeft size={17} /></button><button className="icon-button" type="button" aria-label="任务下一页" title="下一页" disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))}><ChevronRight size={17} /></button></nav>}
  </>;
}
