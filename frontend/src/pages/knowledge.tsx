/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, Bot, ChevronRight, CircleHelp, ListChecks, Network, Search } from 'lucide-react';
import { ApiError, loadKnowledgeGraph, loadKnowledgeGraphNode, loadKnowledgeGraphPath } from '../api/client';
import { KnowledgeGraphEdge, KnowledgeGraphNode } from '../types';
import { PageHead } from '../ui';
import { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { useAppStore } from '../state/app';
import { useNavigate, useSearchParams } from 'react-router';
import { usePlatformData } from '../appData';
import { lazyRetry } from '../lazyRetry';
const KnowledgeGraphCanvas = lazyRetry(() => import('../KnowledgeGraphCanvas'));

export function KnowledgeGraphPage() {
  const data = usePlatformData();
  const preview = useAppStore((state) => state.preview);
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q')?.trim() || '';
  const [nodes, setNodes] = useState<KnowledgeGraphNode[]>([]);
  const [edges, setEdges] = useState<KnowledgeGraphEdge[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [detail, setDetail] = useState<KnowledgeGraphNode | null>(null);
  const [queryInput, setQueryInput] = useState(initialQuery);
  const [query, setQuery] = useState(initialQuery);
  const [chapterFilter, setChapterFilter] = useState('');
  const [view, setView] = useState<'graph' | 'list'>('graph');
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [pathStart, setPathStart] = useState('');
  const [pathEnd, setPathEnd] = useState('');
  const [pathNodes, setPathNodes] = useState<string[]>([]);
  const [pathState, setPathState] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [pathMessage, setPathMessage] = useState('');
  const [reloadToken, setReloadToken] = useState(0);
  const pathRequestRef = useRef(0);
  const selectNode = useCallback((id: string) => setSelectedId(id), []);

  useEffect(() => {
    let active = true;
    setState('loading');
    pathRequestRef.current += 1;
    setPathState('idle');
    setPathNodes([]);
    setPathMessage('');
    async function load() {
      try {
        const loaded = preview
          ? { nodes: data.profile.map((item) => ({ id: item.id, name: item.name, chapterId: Number(item.id.split('-')[1] || 0), category: '知识点', description: '', neighbors: [] })), edges: [] }
          : await loadKnowledgeGraph();
        if (!active) return;
        setNodes(loaded.nodes);
        setEdges(loaded.edges);
        setSelectedId((current) => loaded.nodes.some((item) => item.id === current) ? current : loaded.nodes[0]?.id || '');
        setPathStart((current) => loaded.nodes.some((item) => item.id === current) ? current : loaded.nodes[0]?.id || '');
        setPathEnd((current) => loaded.nodes.some((item) => item.id === current) ? current : loaded.nodes[loaded.nodes.length - 1]?.id || '');
        setState('ready');
        setMessage('');
      } catch (caught) {
        if (!active) return;
        setState('error');
        setMessage(caught instanceof ApiError ? caught.message : '知识图谱服务暂时不可用。');
      }
    }
    void load();
    return () => { active = false; };
  }, [data.profile, preview, reloadToken]);

  useEffect(() => {
    if (!selectedId) { setDetail(null); return; }
    const fallback = nodes.find((item) => item.id === selectedId) || null;
    if (preview) { setDetail(fallback); return; }
    let active = true;
    setDetail(null);
    void loadKnowledgeGraphNode(selectedId).then((loaded) => { if (active) setDetail(loaded); }).catch((caught: unknown) => { if (active) setMessage(caught instanceof ApiError ? caught.message : '知识点详情暂时不可用。'); });
    return () => { active = false; };
  }, [nodes, preview, selectedId]);

  const normalizedQuery = query.toLocaleLowerCase();
  const visibleNodes = nodes.filter((node) => (!chapterFilter || String(node.chapterId) === chapterFilter) && (!normalizedQuery || `${node.name} ${node.id} ${node.category}`.toLocaleLowerCase().includes(normalizedQuery)));
  const visibleNodeIds = new Set(visibleNodes.map((node) => node.id));
  const visibleEdgeCount = edges.filter((edge) => visibleNodeIds.has(edge.sourceId) && visibleNodeIds.has(edge.targetId)).length;
  const profile = detail ? data.profile.find((item) => item.id === detail.id) : undefined;
  const statusLabel = profile?.status === 'mastered' ? '已掌握' : profile?.status === 'weak' ? '需要加强' : profile?.status === 'learning' ? '学习中' : '未评估';
  function submitSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuery = queryInput.trim();
    setQuery(nextQuery);
    setSearchParams(nextQuery ? { q: nextQuery } : {}, { replace: true });
  }

  async function showPath() {
    if (!pathStart || !pathEnd || pathStart === pathEnd || preview) return;
    const requestId = pathRequestRef.current + 1;
    pathRequestRef.current = requestId;
    setPathState('loading');
    setPathNodes([]);
    setPathMessage('正在计算先修路径…');
    try {
      const result = await loadKnowledgeGraphPath(pathStart, pathEnd);
      if (pathRequestRef.current !== requestId) return;
      if (!result.path.length) throw new ApiError('未找到有限先修路径', 'path_not_found');
      setPathNodes(result.path);
      setPathState('ready');
      setPathMessage(`已找到 ${result.path.length} 个知识点，路径深度 ${result.depth}。`);
    } catch (caught) {
      if (pathRequestRef.current !== requestId) return;
      setPathState('error');
      setPathMessage(caught instanceof ApiError ? caught.message : '先修路径暂时不可用。');
    }
  }

  function clearPathSelection(next: string, target: 'start' | 'end') {
    pathRequestRef.current += 1;
    setPathState('idle');
    setPathNodes([]);
    setPathMessage('');
    if (target === 'start') setPathStart(next);
    else setPathEnd(next);
  }

  return <>
    <PageHead eyebrow="学习图谱" title="知识点与先修关系" description="从课程知识点出发查看掌握状态、邻接关系和对应教材。" action={<button className="button secondary" onClick={() => navigate('/assistant')}><Bot size={16} />问课程 Agent</button>} />
    <form className="graph-toolbar" onSubmit={submitSearch}>
      <label><span>搜索知识点</span><input aria-label="搜索知识点" value={queryInput} onChange={(event) => setQueryInput(event.target.value)} placeholder="输入知识点名称" /></label>
      <label><span>章节</span><select aria-label="筛选章节" value={chapterFilter} onChange={(event) => setChapterFilter(event.target.value)}><option value="">全部章节</option>{data.chapters.map((chapter) => <option key={chapter.id} value={chapter.id}>第 {chapter.id} 章</option>)}</select></label>
      <button className="button primary" type="submit"><Search size={16} />搜索</button>
    </form>
    {preview && <div className="preview-banner"><CircleHelp size={16} /><span>当前为预览模式，显示已知学习点摘要；登录课程平台后可查看服务端邻接关系。</span></div>}
    {state === 'loading' && <div className="empty-state">正在读取知识图谱…</div>}
    {state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => setReloadToken((current) => current + 1)}>重新加载</button></div>}
    {state === 'ready' && <>
      <section className="graph-path-panel" aria-label="学习路径">
        <div className="graph-path-heading"><div><span className="side-kicker">学习路径</span><strong>规划先修顺序</strong></div><small>{preview ? '登录课程平台后开放' : '选择起点和目标'}</small></div>
        <div className="graph-path-controls">
          <label><span>起点知识点</span><select aria-label="起点知识点" value={pathStart} onChange={(event) => clearPathSelection(event.target.value, 'start')}>{nodes.map((node) => <option value={node.id} key={node.id}>{node.name}</option>)}</select></label>
          <label><span>目标知识点</span><select aria-label="目标知识点" value={pathEnd} onChange={(event) => clearPathSelection(event.target.value, 'end')}>{nodes.map((node) => <option value={node.id} key={node.id}>{node.name}</option>)}</select></label>
          <button className="button secondary" type="button" onClick={() => void showPath()} disabled={preview || pathState === 'loading' || !pathStart || !pathEnd || pathStart === pathEnd}>{pathState === 'loading' ? '计算中…' : '显示学习路径'}<Network size={16} /></button>
        </div>
        {pathMessage && <div className={`graph-path-message ${pathState === 'error' ? 'error' : ''}`} role={pathState === 'error' ? 'alert' : undefined}>{pathMessage}</div>}
        {pathNodes.length > 0 && <ol className="graph-path-list">{pathNodes.map((nodeId, index) => { const node = nodes.find((item) => item.id === nodeId); return <li key={nodeId}><button type="button" onClick={() => setSelectedId(nodeId)}><span>{index + 1}</span><strong>{node?.name || nodeId}</strong></button>{index < pathNodes.length - 1 && <ChevronRight size={14} />}</li>; })}</ol>}
      </section>
      <div className="graph-layout">
        <section className="graph-board section-block">
          <div className="graph-board-heading">
            <div><h2>课程知识点</h2><small>{visibleNodes.length} 个节点 · {visibleEdgeCount} 条关系{pathNodes.length ? ` · 高亮路径 ${pathNodes.length} 个` : ''}</small></div>
            <div className="segmented-control" role="group" aria-label="图谱视图">
              <button type="button" aria-pressed={view === 'graph'} className={view === 'graph' ? 'active' : ''} onClick={() => setView('graph')}><Network size={15} />关系图</button>
              <button type="button" aria-pressed={view === 'list'} className={view === 'list' ? 'active' : ''} onClick={() => setView('list')}><ListChecks size={15} />列表</button>
            </div>
          </div>
          {!visibleNodes.length ? <div className="empty-state">当前筛选没有知识点。</div> : view === 'graph' ? <>
            <div className="graph-legend" aria-label="图谱图例"><span><i className="mastered" />已掌握</span><span><i className="learning" />学习中</span><span><i className="weak" />需要加强</span><span><b />先修方向</span></div>
            <Suspense fallback={<div className="graph-flow graph-flow-loading">正在加载关系图…</div>}>
              <KnowledgeGraphCanvas nodes={visibleNodes} edges={edges} profile={data.profile} selectedId={selectedId} pathNodes={pathNodes} onSelect={selectNode} />
            </Suspense>
          </> : <div className="graph-node-grid">{visibleNodes.map((node) => { const pathIndex = pathNodes.indexOf(node.id); return <button className={`graph-node ${node.id === selectedId ? 'selected' : ''} ${pathIndex >= 0 ? 'path-node' : ''} ${pathIndex === 0 ? 'path-start' : ''}`} key={node.id} onClick={() => setSelectedId(node.id)}><span className="graph-node-code">{node.id}</span><strong>{node.name}</strong><small>第 {node.chapterId} 章 · {node.category}</small>{pathIndex >= 0 && <em>路径第 {pathIndex + 1} 步</em>}</button>; })}</div>}
        </section>
        <aside className="graph-detail section-block">
          {detail ? <><div className="graph-detail-head"><span className="graph-node-code">{detail.id}</span><span className={`status-tag ${profile?.status === 'mastered' ? 'active' : ''}`}>{statusLabel}</span></div><h2>{detail.name}</h2><p>{detail.description || '该知识点的正式描述将在课程图谱资料中展示。'}</p>{profile?.ratio !== null && profile?.ratio !== undefined && <div className="graph-mastery"><span>掌握度</span><strong>{Math.round(profile.ratio * 100)}%</strong><div className="progress-line"><span style={{ width: `${profile.ratio * 100}%` }} /></div></div>}<div className="section-title"><h3>相邻知识点</h3><span>{detail.neighbors.length}</span></div>{detail.neighbors.length ? <div className="graph-neighbors">{detail.neighbors.map((neighbor) => <button className="text-button" key={`${neighbor.id}-${neighbor.relationType}`} onClick={() => setSelectedId(neighbor.id)}>{neighbor.name}<small>{neighbor.relationType === 'prerequisite' ? '先修关系' : '相关关系'}</small><ChevronRight size={14} /></button>)}</div> : <div className="empty-state compact-empty">暂无已加载的邻接关系。</div>}<button className="button quiet" onClick={() => navigate(`/assistant?node_id=${encodeURIComponent(detail.id)}`)}><Bot size={15} />围绕此知识点提问</button></> : <div className="empty-state">选择一个知识点查看详情。</div>}
        </aside>
      </div>
    </>}
  </>;
}
