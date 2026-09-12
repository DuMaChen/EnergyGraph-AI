/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AgentContext, AgentMode, ScenarioSession } from '../types';
import { Bot, ChevronRight, FileText, RefreshCw, Send, X } from 'lucide-react';
import { PageHead } from '../ui';
import { endScenario, startScenario, streamAgent } from '../api/client';
import { useAppStore } from '../state/app';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';
import { usePlatformData } from '../appData';

export function AssistantPage() {
  const preview = useAppStore((state) => state.preview);
  const role = useAppStore((state) => state.session?.role || 'student');
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const data = usePlatformData();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<AgentMode>('qa');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [state, setState] = useState<'idle' | 'loading' | 'done' | 'error' | 'cancelled'>('idle');
  const [sources, setSources] = useState<Array<{ id: string; file: string; chapter: string; page: number; resourceId: string; version: string; verified: boolean }>>([]);
  const [lastQuestion, setLastQuestion] = useState('');
  const [scenario, setScenario] = useState<ScenarioSession | null>(null);
  const [scenarioMessage, setScenarioMessage] = useState('');
  const controller = useRef<AbortController | null>(null);
  const resourceId = searchParams.get('resource_id') || '';
  const resourcePage = Number(searchParams.get('page') || searchParams.get('resource_page') || 0);
  const nodeIds = searchParams.getAll('node_id').filter(Boolean);
  const chapterId = Number(searchParams.get('chapter_id') || 0);
  const contextResource = data.resources.find((item) => item.id === resourceId);
  const contextChapter = data.chapters.find((item) => item.id === chapterId) || (contextResource ? data.chapters.find((item) => item.id === contextResource.chapterId) : null);
  const context: AgentContext = {
    ...(resourceId ? { resourceId } : {}),
    ...(resourcePage > 0 ? { resourcePage } : {}),
    ...(nodeIds.length ? { nodeIds } : {}),
    ...(scenario?.sessionId && mode === 'scenario' ? { sessionId: scenario.sessionId, turnNo: scenario.turnCount + 1, idempotencyKey: `agent-scenario-${scenario.sessionId}-${scenario.turnCount + 1}` } : {}),
  };
  useEffect(() => () => { controller.current?.abort(); }, []);

  async function submit(overrideQuestion?: string) {
    const trimmed = (overrideQuestion ?? question).trim();
    if (!trimmed || state === 'loading') return;
    setLastQuestion(trimmed);
    setQuestion(trimmed);
    setState('loading'); setAnswer(''); setSources([]); setScenarioMessage('');
    const requestController = new AbortController();
    controller.current = requestController;
    if (preview) {
      await new Promise((resolve) => window.setTimeout(resolve, 350));
      if (requestController.signal.aborted) { setState('cancelled'); return; }
      setAnswer(`这是预览模式的示例回答。关于“${trimmed}”，建议先阅读第 3 章相关教材，再结合章节练习验证理解。真实课程回答将由服务端 Agent 返回，并经过来源校验。`);
      setSources([{ id: 'preview-source', file: contextResource?.sourceFile || '3.4 储能变流器拓扑及并网控制.pdf', chapter: contextChapter?.name || '第3章 电力储能系统的组成及工作原理', page: resourcePage || 1, resourceId: contextResource?.id || 'res-34', version: 'preview', verified: false }]);
      setState('done'); controller.current = null; return;
    }
    try {
      let requestContext = context;
      if (mode === 'scenario' && !scenario) {
        const started = await startScenario('grid-dispatch', csrfToken, `agent-scenario-start:${Date.now()}`);
        setScenario(started);
        requestContext = { ...context, sessionId: started.sessionId, turnNo: 1, idempotencyKey: `agent-scenario-${started.sessionId}-1` };
      }
      await streamAgent(trimmed, mode, (event) => {
        if (event.event === 'token') setAnswer((current) => current + String(event.data.text || ''));
        if (event.event === 'source') {
          const item = event.data;
          const sourceId = String(item.source_id || item.file || `source-${Date.now()}`);
          setSources((current) => current.some((source) => source.id === sourceId) ? current : [...current, { id: sourceId, file: String(item.file || ''), chapter: String(item.chapter || ''), page: Number(item.page || 0), resourceId: String(item.resource_id || ''), version: String(item.version || ''), verified: item.status !== 'unverified' && sourceId !== 'unverified' }]);
        }
      }, csrfToken, requestController.signal, requestContext);
      if (mode === 'scenario' && requestContext.sessionId) setScenario((current) => current ? { ...current, turnCount: current.turnCount + 1 } : current);
      setState('done');
    } catch (error) {
      if (requestController.signal.aborted) { setState('cancelled'); setScenarioMessage('本次生成已取消，可以修改问题后重试。'); }
      else { setAnswer(error instanceof Error ? error.message : '本次请求未完成。'); setState('error'); }
    } finally {
      if (controller.current === requestController) controller.current = null;
    }
  }
  async function endCurrentScenario() {
    if (!scenario || preview) return;
    try {
      const result = await endScenario(scenario.sessionId, csrfToken, `agent-scenario-end:${scenario.sessionId}`);
      setScenario((current) => current ? { ...current, state: 'completed', turnCount: result.turnCount } : current);
      setScenarioMessage(result.summary.status || '情景演练已结束。');
    } catch (error) { setScenarioMessage(error instanceof Error ? error.message : '情景结束失败，请重试。'); }
  }

  const cancel = () => { controller.current?.abort(); };
  const modes: { id: AgentMode; label: string }[] = [{ id: 'qa', label: '课程问答' }, { id: 'learning_diagnosis', label: '学习诊断' }, { id: 'scenario', label: '情景演练' }, ...(role === 'student' ? [] : [{ id: 'teacher_assistant' as AgentMode, label: '教师助手' }, { id: 'question_draft' as AgentMode, label: '出题草稿' }, { id: 'grading' as AgentMode, label: '批改建议' }])];
  const composePlaceholder = mode === 'scenario' ? '描述你在当前调度情景中的判断…' : mode === 'question_draft' ? '描述要生成的题型、章节和考查要点…' : mode === 'grading' ? '粘贴学生答案并说明需要复核的评分要点…' : '例如：储能变流器在并网控制中承担什么作用？';
  const stateLabel = state === 'loading' ? '生成中' : state === 'done' ? '已完成' : state === 'error' ? '服务异常' : state === 'cancelled' ? '已取消' : '等待提问';
  const contextTitle = contextResource ? `${contextResource.title} · 第 ${resourcePage || contextResource.pageStart} 页` : contextChapter?.name || '当前课程';
  return <><PageHead eyebrow="课程 Agent" title="在课程语境中学习" description="回答会绑定当前课程资料；没有可核验来源时，不会把生成内容显示为课程事实。" /><div className="agent-layout"><section className="agent-panel"><div className="agent-panel-heading"><div><span className="ai-label"><Bot size={16} />AI 学习助手</span><h2>把不确定的问题说出来</h2></div><span className={`agent-state ${state}`}>{stateLabel}</span></div><div className="mode-tabs" role="tablist">{modes.map((item) => <button key={item.id} role="tab" aria-selected={mode === item.id} className={mode === item.id ? 'active' : ''} onClick={() => setMode(item.id)}>{item.label}</button>)}</div>{mode === 'scenario' && scenario && <div className="agent-scenario-banner"><strong>{scenario.title}</strong><span>{scenario.goal}</span><small>{scenario.assumptions} · 已完成 {scenario.turnCount} 轮</small><button className="text-button" onClick={() => void endCurrentScenario()} disabled={scenario.state === 'completed' || state === 'loading'}>结束演练</button></div>}<div className="agent-compose"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={composePlaceholder} aria-label="输入课程问题" /><div className="compose-footer"><span>AI 生成内容请结合课程来源核验</span><div className="agent-actions">{state === 'loading' ? <button className="button quiet" onClick={cancel}><X size={16} />取消生成</button> : <>{state === 'error' && lastQuestion && <button className="button quiet" onClick={() => void submit(lastQuestion)}><RefreshCw size={16} />重试</button>}<button className="button primary" onClick={() => void submit()} disabled={!question.trim()}><Send size={16} />发送问题</button></>}</div></div></div>{scenarioMessage && <div className="reader-notice conflict">{scenarioMessage}</div>}<div className="agent-answer"><div className="answer-heading"><span>回答</span>{state === 'loading' && <RefreshCw size={15} className="spin" />}</div><p>{answer || (state === 'idle' ? '提交问题后，回答和来源会显示在这里。' : state === 'cancelled' ? '生成已取消。' : '本次没有返回可显示内容。')}</p></div>{role !== 'student' && state === 'done' && answer && mode === 'question_draft' && <div className="agent-draft-actions"><span>草稿不会自动发布，进入题库后仍需教师确认。</span><button className="button secondary" onClick={() => navigate(`/teacher/questions?draft=${encodeURIComponent(answer)}`)}>带到题库编辑<FileText size={15} /></button></div>}{role !== 'student' && state === 'done' && answer && mode === 'grading' && <div className="agent-draft-actions"><span>批改建议不会直接写入成绩。</span><button className="button secondary" onClick={() => navigate('/teacher/gradebook')}>进入批改中心<ChevronRight size={15} /></button></div>}{sources.length > 0 && <div className="source-area"><h3>课程来源</h3>{sources.map((item) => { const canOpen = item.verified && item.resourceId && item.page > 0; return canOpen ? <button className="source-line" key={item.id} onClick={() => navigate(`/resources/${encodeURIComponent(item.resourceId)}?page=${item.page}`)}><FileText size={15} /><span>{item.file} · {item.chapter} · 第 {item.page} 页</span><small>打开教材</small></button> : <div className="source-line unverified" key={item.id}><FileText size={15} /><span>{item.file || '来源待核验'}</span><small>待核验</small></div>; })}</div>}</section><aside className="agent-side"><div className="agent-side-block"><span className="side-kicker">当前上下文</span><h3>{contextTitle}</h3><p>{resourceId ? '本次问题会带入服务端校验过的资源和页码。' : '回答将优先围绕当前课程和已发布资料生成。'}</p>{resourceId && <button className="text-button" onClick={() => navigate(`/resources/${encodeURIComponent(resourceId)}?page=${resourcePage || contextResource?.pageStart || 1}`)}>查看教材<ChevronRight size={14} /></button>}</div><div className="agent-side-block warm-block"><span className="side-kicker">学习提示</span><h3>先理解，再验证</h3><p>对模型回答中的页码、定义和结论，请通过来源卡片回到教材核对。</p></div></aside></div></>;
}
