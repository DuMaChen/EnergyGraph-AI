/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ArrowLeft, CheckCircle2, CircleHelp, RefreshCw, Send } from 'lucide-react';
import { ApiError, loadAssignment, loadAssignmentDraft, saveAssignmentDraft, submitAssignment } from '../api/client';
import { AssignmentDetail } from '../types';
import { PageHead, QuestionBlock } from '../ui';
import { useAppStore } from '../state/app';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';
import { usePlatformData } from '../appData';

function readCachedAssignmentDraft(assignmentId: string, attempt: number): { answers: Record<string, unknown>; version: number } | null {
  try {
    const raw = window.localStorage.getItem(`assignment-draft:${assignmentId}:${attempt}`);
    if (!raw) return null;
    const value = JSON.parse(raw) as { answers?: Record<string, unknown>; version?: number };
    if (!value.answers || typeof value.answers !== 'object') return null;
    return { answers: value.answers, version: Number(value.version || 0) };
  } catch { return null; }
}

export function AssignmentPage() {
  const { assignmentId = '' } = useParams();
  const navigate = useNavigate();
  const data = usePlatformData();
  const preview = useAppStore((state) => state.preview);
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const [detail, setDetail] = useState<AssignmentDetail | null>(null);
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const answersRef = useRef<Record<string, unknown>>({});
  const pendingAnswersRef = useRef<Record<string, unknown> | null>(null);
  const draftVersionRef = useRef(0);
  const draftRequestSequenceRef = useRef(0);
  const saveTimer = useRef<number | null>(null);
  const savePromise = useRef<Promise<void> | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'error' | 'preview'>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const [draftState, setDraftState] = useState<'idle' | 'saving' | 'saved' | 'offline' | 'conflict' | 'error'>('idle');
  const [submitState, setSubmitState] = useState<'idle' | 'submitting' | 'submitted'>('idle');
  const [submissionId, setSubmissionId] = useState('');

  useEffect(() => {
    let active = true;
    setState('loading');
    setErrorMessage('');
    async function load() {
      if (preview) {
        const summary = data.assignments.find((item) => item.id === assignmentId);
        if (!summary) { if (active) { setState('error'); setErrorMessage('作业不存在或已从课程中移除。'); } return; }
        if (active) {
          setDetail({ ...summary, allowAttempts: summary.allowAttempts || 1, questions: [], mySubmissions: [] });
          setState('preview');
        }
        return;
      }
      try {
        const [loaded, serverDraft] = await Promise.all([loadAssignment(assignmentId), loadAssignmentDraft(assignmentId)]);
        if (!active) return;
        const cached = readCachedAssignmentDraft(assignmentId, serverDraft.attempt);
        const selected = cached && cached.version >= serverDraft.version ? cached : serverDraft;
        setDetail(loaded);
        setAnswers(selected.answers || {});
        answersRef.current = selected.answers || {};
        draftVersionRef.current = selected.version;
        setState('ready');
        setDraftState(cached && cached.version > serverDraft.version ? 'offline' : 'idle');
      } catch (caught) {
        if (!active) return;
        setState('error');
        setErrorMessage(caught instanceof ApiError ? caught.message : '作业服务暂时不可用，请稍后重试。');
      }
    }
    void load();
    return () => {
      active = false;
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
    };
  }, [assignmentId, data.assignments, preview]);

  function cacheDraft(nextAnswers: Record<string, unknown>, version: number) {
    try { window.localStorage.setItem(`assignment-draft:${assignmentId}:1`, JSON.stringify({ answers: nextAnswers, version })); } catch { /* local storage is optional */ }
  }

  function flushDraft(): Promise<void> {
    if (preview || !detail) return Promise.resolve();
    if (savePromise.current) return savePromise.current;
    const nextAnswers = pendingAnswersRef.current || answersRef.current;
    pendingAnswersRef.current = null;
    const baseVersion = draftVersionRef.current;
    const idempotencyKey = `assignment-draft:${assignmentId}:1:${baseVersion}:${++draftRequestSequenceRef.current}`;
    setDraftState('saving');
    const promise = saveAssignmentDraft(assignmentId, 1, nextAnswers, baseVersion, csrfToken, idempotencyKey)
      .then((saved) => {
        draftVersionRef.current = saved.version;
        cacheDraft(nextAnswers, saved.version);
        setDraftState('saved');
      })
      .catch((caught) => {
        if (caught instanceof ApiError && caught.code === 'assignment_draft_conflict') setDraftState('conflict');
        else if (caught instanceof TypeError || (caught instanceof ApiError && caught.code === 'network_error')) setDraftState('offline');
        else setDraftState('error');
        throw caught;
      })
      .finally(() => { savePromise.current = null; });
    savePromise.current = promise;
    return promise;
  }

  function scheduleDraft(nextAnswers: Record<string, unknown>) {
    if (preview || !detail) return;
    answersRef.current = nextAnswers;
    pendingAnswersRef.current = nextAnswers;
    cacheDraft(nextAnswers, draftVersionRef.current);
    if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
    saveTimer.current = window.setTimeout(() => { void flushDraft(); }, 700);
    setDraftState('saving');
  }

  function updateAnswer(questionId: string, value: unknown) {
    const next = { ...answersRef.current, [questionId]: value };
    answersRef.current = next;
    setAnswers(next);
    scheduleDraft(next);
  }

  async function submit() {
    if (!detail || preview || submitState === 'submitting') return;
    setSubmitState('submitting');
    setErrorMessage('');
    try {
      if (saveTimer.current !== null) window.clearTimeout(saveTimer.current);
      pendingAnswersRef.current = answersRef.current;
      await flushDraft();
      const result = await submitAssignment(assignmentId, 1, answersRef.current, csrfToken, `assignment-submit:${assignmentId}:1`);
      setSubmissionId(result.id);
      setSubmitState('submitted');
    } catch (caught) {
      setSubmitState('idle');
      setErrorMessage(caught instanceof ApiError ? caught.message : '提交未完成，请重试。');
    }
  }

  if (state === 'loading') return <><PageHead eyebrow="作业" title="正在打开作业" description="正在读取题目、草稿和服务端状态。" /><div className="empty-state">正在读取作业内容…</div></>;
  if (state === 'error' || !detail) return <><PageHead eyebrow="作业" title="无法打开作业" description="作业状态没有被伪造为可提交。" action={<button className="button secondary" onClick={() => navigate('/tasks')}><ArrowLeft size={16} />返回任务中心</button>} /><div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{errorMessage}</strong><button className="button secondary" onClick={() => window.location.reload()}><RefreshCw size={16} />重新加载</button></div></>;
  const latestSubmission = detail.mySubmissions[detail.mySubmissions.length - 1];
  const draftLabel = draftState === 'saving' ? '保存中' : draftState === 'saved' ? '草稿已保存' : draftState === 'offline' ? '本机草稿' : draftState === 'conflict' ? '版本冲突' : draftState === 'error' ? '保存失败' : '未修改';
  return <><PageHead eyebrow="作业答题" title={detail.title} description={`${detail.questionCount} 道题 · 截止 ${detail.dueAt}`} action={<button className="button secondary" onClick={() => navigate('/tasks')}><ArrowLeft size={16} />返回任务中心</button>} /><div className="assessment-layout"><aside className="assessment-summary"><span className="side-kicker">作答状态</span><strong>{submitState === 'submitted' ? '已提交' : detail.status}</strong><p>第 1 次尝试 · 最多 {detail.allowAttempts} 次</p><div className="assessment-progress"><span>已填写 {Object.keys(answers).length} / {detail.questions.length} 题</span><div className="progress-line"><span style={{ width: `${detail.questions.length ? Math.round((Object.keys(answers).length / detail.questions.length) * 100) : 0}%` }} /></div></div>{latestSubmission && <div className="result-summary"><span>最近提交</span><strong>{latestSubmission.score === null ? '等待批改' : `${latestSubmission.score} / ${latestSubmission.maxScore}`}</strong><small>{latestSubmission.needsReview ? '等待教师复核' : latestSubmission.status}</small></div>}</aside><section className="assessment-main">{state === 'preview' && <div className="preview-banner"><CircleHelp size={16} /><span>当前为预览模式，题目提交不会写入课程平台。</span></div>}{detail.questions.length ? detail.questions.map((question, index) => <QuestionBlock key={question.id} index={index + 1} question={question} value={answers[question.id]} disabled={submitState === 'submitted'} onChange={(value) => updateAnswer(question.id, value)} />) : <div className="empty-state">当前环境只返回作业摘要，真实课程会话建立后才会显示题目。</div>}{errorMessage && <div className="reader-notice conflict">{errorMessage}</div>}{submitState === 'submitted' && <div className="submission-success"><CheckCircle2 size={20} /><div><strong>提交成功</strong><span>提交编号：{submissionId}</span></div></div>}{detail.questions.length > 0 && state !== 'preview' && submitState !== 'submitted' && <div className="assessment-footer"><span className={`draft-status ${draftState}`}>{draftLabel}</span><button className="button primary" onClick={() => void submit()} disabled={submitState === 'submitting'}>{submitState === 'submitting' ? '提交中…' : '最终提交'}<Send size={16} /></button></div>}</section></div></>;
}
