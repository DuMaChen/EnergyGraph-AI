/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ArrowLeft, CheckCircle2, ChevronRight, CircleHelp, Clock3, RefreshCw, Send } from 'lucide-react';
import { ApiError, loadExam, loadExamDraft, loadExams, saveExamDraft, startExam, submitExam } from '../api/client';
import { Exam, ExamAttempt, ExamDetail, ExamDraft } from '../types';
import { PageHead, QuestionBlock } from '../ui';
import { previewExams } from '../ui-helpers';
import { useAppStore } from '../state/app';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';

export function ExamsPage() {
  const preview = useAppStore((state) => state.preview);
  const navigate = useNavigate();
  const [exams, setExams] = useState<Exam[]>(previewExams);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>(preview ? 'ready' : 'loading');
  const [errorMessage, setErrorMessage] = useState('');
  useEffect(() => {
    if (preview) { setExams(previewExams); setState('ready'); return; }
    let active = true;
    void loadExams().then((items) => { if (active) { setExams(items); setState('ready'); } }).catch((caught) => { if (active) { setErrorMessage(caught instanceof ApiError ? caught.message : '考试服务暂时不可用。'); setState('error'); } });
    return () => { active = false; };
  }, [preview]);
  return <><PageHead eyebrow="考试中心" title="限时考试" description="开放时间、答题时限和最终成绩由课程服务端决定。" action={<button className="button secondary" onClick={() => navigate('/tasks')}><ArrowLeft size={16} />返回任务中心</button>} />{state === 'loading' && <div className="empty-state">正在读取考试安排…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{errorMessage}</strong><button className="button secondary" onClick={() => window.location.reload()}><RefreshCw size={16} />重新加载</button></div>}{state === 'ready' && <div className="task-table" role="table" aria-label="考试列表"><div className="task-table-head" role="row"><span role="columnheader">考试</span><span role="columnheader">开放时间</span><span role="columnheader">状态</span><span role="columnheader">操作</span></div>{exams.map((exam) => <div className="task-table-row" key={exam.id} role="row"><div role="cell"><span className="table-kind">{exam.type}</span><strong>{exam.title}</strong><small>{exam.questionCount} 道题 · 时长 {Math.round(exam.durationSeconds / 60)} 分钟</small></div><span role="cell">{exam.openAt ? new Date(exam.openAt).toLocaleString('zh-CN', { hour12: false }) : '未设置'}</span><span className={`status-tag ${exam.status === '进行中' ? 'active' : ''}`} role="cell">{exam.status}</span><span className="task-table-actions" role="cell"><button className="button quiet" onClick={() => navigate(`/exams/${encodeURIComponent(exam.id)}`)}>{exam.status === '已完成' ? '查看结果' : '进入考试'}<ChevronRight size={15} /></button></span></div>)}{!exams.length && <div className="task-table-row empty-row" role="row"><div className="empty-state" role="cell">当前没有已发布的考试。</div></div>}</div>}</>;
}

export function ExamPage() {
  const { examId = '' } = useParams();
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [detail, setDetail] = useState<ExamDetail | null>(null);
  const [attempt, setAttempt] = useState<ExamAttempt | null>(null);
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const answersRef = useRef<Record<string, unknown>>({});
  const draftVersionRef = useRef(0);
  const draftSequenceRef = useRef(0);
  const draftTimer = useRef<number | null>(null);
  const draftPromise = useRef<Promise<void> | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'error' | 'preview'>('loading');
  const [draftState, setDraftState] = useState<'idle' | 'saving' | 'saved' | 'conflict' | 'offline' | 'error'>('idle');
  const [submitState, setSubmitState] = useState<'idle' | 'submitting' | 'submitted'>('idle');
  const [remaining, setRemaining] = useState<number | null>(null);
  const [clockOffset, setClockOffset] = useState(0);
  const [message, setMessage] = useState('');
  const [submission, setSubmission] = useState<ExamDetail['mySubmissions'][number] | null>(null);

  useEffect(() => {
    let active = true;
    setState('loading');
    setMessage('');
    async function load() {
      if (preview) {
        const found = previewExams.find((item) => item.id === examId);
        if (!found) { if (active) { setState('error'); setMessage('考试不存在或已从课程中移除。'); } return; }
        if (active) { setDetail(found); setState('preview'); }
        return;
      }
      try {
        const loaded = await loadExam(examId);
        if (!active) return;
        setDetail(loaded);
        if (loaded.availability !== 'open') { setState('ready'); return; }
        const started = await startExam(examId, csrfToken, `exam-start:${examId}`);
        if (!active || !started.attempt) return;
        const draft = await loadExamDraft(examId, started.attempt.attempt);
        if (!active) return;
        setDetail(started);
        setAttempt(started.attempt);
        setAnswers(draft.answers || {});
        answersRef.current = draft.answers || {};
        draftVersionRef.current = draft.version;
        setClockOffset(started.serverNow ? new Date(started.serverNow).getTime() - Date.now() : 0);
        setState('ready');
      } catch (caught) {
        if (active) { setState('error'); setMessage(caught instanceof ApiError ? caught.message : '考试服务暂时不可用，请稍后重试。'); }
      }
    }
    void load();
    return () => { active = false; if (draftTimer.current !== null) window.clearTimeout(draftTimer.current); };
  }, [csrfToken, examId, preview]);

  useEffect(() => {
    if (!attempt) return;
    const tick = () => setRemaining(Math.max(0, Math.ceil((new Date(attempt.deadlineAt).getTime() - (Date.now() + clockOffset)) / 1000)));
    tick();
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [attempt, clockOffset]);

  function cacheAnswers(next: Record<string, unknown>) {
    try { window.localStorage.setItem(`exam-draft:${examId}:${attempt?.attempt || 1}`, JSON.stringify({ answers: next, version: draftVersionRef.current })); } catch { /* storage is optional */ }
  }

  function flushDraft(): Promise<void> {
    if (preview || !attempt) return Promise.resolve();
    if (draftPromise.current) return draftPromise.current;
    const next = answersRef.current;
    const baseVersion = draftVersionRef.current;
    setDraftState('saving');
    const promise = saveExamDraft(examId, attempt.attempt, next, baseVersion, csrfToken, `exam-draft:${examId}:${attempt.attempt}:${baseVersion}:${++draftSequenceRef.current}`)
      .then((saved: ExamDraft) => { draftVersionRef.current = saved.version; cacheAnswers(next); setDraftState('saved'); })
      .catch((caught) => { setDraftState(caught instanceof ApiError && caught.code === 'exam_draft_conflict' ? 'conflict' : caught instanceof TypeError ? 'offline' : 'error'); throw caught; })
      .finally(() => { draftPromise.current = null; });
    draftPromise.current = promise;
    return promise;
  }

  function updateAnswer(questionId: string, value: unknown) {
    const next = { ...answersRef.current, [questionId]: value };
    answersRef.current = next;
    setAnswers(next);
    cacheAnswers(next);
    if (!preview) {
      if (draftTimer.current !== null) window.clearTimeout(draftTimer.current);
      draftTimer.current = window.setTimeout(() => { void flushDraft(); }, 600);
      setDraftState('saving');
    }
  }

  async function submit() {
    if (!detail || !attempt || preview || submitState === 'submitting') return;
    if (remaining === 0) { setMessage('考试时间已结束，提交由服务端判定。'); return; }
    setSubmitState('submitting');
    setMessage('');
    try {
      if (draftTimer.current !== null) window.clearTimeout(draftTimer.current);
      await flushDraft();
      const result = await submitExam(examId, attempt.attempt, answersRef.current, csrfToken, `exam-submit:${examId}:${attempt.attempt}`);
      setSubmission(result);
      setSubmitState('submitted');
      setAttempt({ ...attempt, status: 'submitted', submittedAt: result.submittedAt });
    } catch (caught) {
      setSubmitState('idle');
      setMessage(caught instanceof ApiError ? caught.message : '考试提交未完成，请重试。');
    }
  }

  const formatRemaining = (seconds: number | null) => seconds === null ? '--:--' : `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  if (state === 'loading') return <><PageHead eyebrow="限时考试" title="正在打开考试" description="正在读取考试窗口、题目和服务端计时状态。" /><div className="empty-state">正在读取考试内容…</div></>;
  if (state === 'error' || !detail) return <><PageHead eyebrow="限时考试" title="无法打开考试" description="考试状态没有被伪造为可提交。" action={<button className="button secondary" onClick={() => navigate('/exams')}><ArrowLeft size={16} />返回考试中心</button>} /><div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => window.location.reload()}><RefreshCw size={16} />重新加载</button></div></>;
  const latest = submission || detail.mySubmissions[detail.mySubmissions.length - 1];
  const draftLabel = draftState === 'saving' ? '自动保存中' : draftState === 'saved' ? '答案已保存' : draftState === 'conflict' ? '版本冲突' : draftState === 'offline' ? '本机草稿' : draftState === 'error' ? '保存失败' : '未修改';
  const canAnswer = detail.questions.length > 0 && (state === 'preview' || Boolean(attempt && attempt.status === 'in_progress' && remaining !== 0));
  return <><PageHead eyebrow="限时考试" title={detail.title} description={`${detail.questionCount} 道题 · 时长 ${Math.round(detail.durationSeconds / 60)} 分钟`} action={<button className="button secondary" onClick={() => navigate('/exams')}><ArrowLeft size={16} />返回考试中心</button>} /><div className="assessment-layout"><aside className="assessment-summary"><span className="side-kicker">考试状态</span><strong>{state === 'preview' ? '预览模式' : attempt?.status === 'submitted' ? '已提交' : detail.status}</strong><p>开放：{new Date(detail.openAt).toLocaleString('zh-CN', { hour12: false })}</p><p>结束：{new Date(detail.closeAt).toLocaleString('zh-CN', { hour12: false })}</p>{attempt && <div className={`exam-countdown ${remaining !== null && remaining < 60 ? 'urgent' : ''}`}><Clock3 size={17} /><span>剩余时间</span><strong>{formatRemaining(remaining)}</strong></div>}<div className="assessment-progress"><span>已填写 {Object.keys(answers).length} / {detail.questions.length} 题</span><div className="progress-line"><span style={{ width: `${detail.questions.length ? Math.round((Object.keys(answers).length / detail.questions.length) * 100) : 0}%` }} /></div></div>{latest && <div className="result-summary"><span>最近成绩</span><strong>{latest.score} / {latest.maxScore}</strong><small>{latest.needsReview ? '等待教师复核' : '服务端已记录'}</small></div>}</aside><section className="assessment-main">{state === 'preview' && <div className="preview-banner"><CircleHelp size={16} /><span>当前为预览模式，提交不会写入课程平台。</span></div>}{!attempt && state !== 'preview' && <div className="empty-state">{detail.availability === 'not_open' ? '考试尚未开放，请在开放时间后进入。' : '考试已结束，不能开始新的尝试。'}</div>}{detail.questions.map((question, index) => <QuestionBlock key={question.id} index={index + 1} question={question} value={answers[question.id]} disabled={!canAnswer || submitState === 'submitted'} onChange={(value) => updateAnswer(question.id, value)} />)}{message && <div className="reader-notice conflict" role="alert">{message}</div>}{submitState === 'submitted' && latest && <div className="submission-success"><CheckCircle2 size={20} /><div><strong>提交成功</strong><span>成绩：{latest.score} / {latest.maxScore}</span></div></div>}{canAnswer && state !== 'preview' && submitState !== 'submitted' && <div className="assessment-footer"><span className={`draft-status ${draftState}`}>{draftLabel}</span><button className="button primary" onClick={() => void submit()} disabled={submitState === 'submitting'}>{submitState === 'submitting' ? '提交中…' : '提交考试'}<Send size={16} /></button></div>}</section></div></>;
}
