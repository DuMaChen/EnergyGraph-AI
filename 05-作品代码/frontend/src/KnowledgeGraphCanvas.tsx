import { useEffect, useMemo } from 'react';
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Edge,
  type NodeProps,
} from '@xyflow/react';
import { GripVertical } from 'lucide-react';
import type { KnowledgeGraphEdge, KnowledgeGraphNode, ProfilePoint } from './types';
import { buildKnowledgeGraphFlowEdges, buildKnowledgeGraphFlowNodes, type KnowledgeGraphFlowNode } from './lib/knowledgeGraphFlow';

function KnowledgeGraphPoint({ id, data }: NodeProps<KnowledgeGraphFlowNode>) {
  const statusText = data.status === 'mastered' ? '已掌握' : data.status === 'weak' ? '需要加强' : data.status === 'learning' ? '学习中' : '未评估';
  return <div className="graph-node-shell">
    <Handle id="target" type="target" position={Position.Top} isConnectable={false} className="graph-handle" />
    <span className="graph-node-drag-handle" title="拖动知识点" aria-hidden="true"><GripVertical size={15} /></span>
    <button
      type="button"
      className={`graph-node nodrag ${data.selected ? 'selected' : ''} ${data.pathIndex >= 0 ? 'path-node' : ''} ${data.pathIndex === 0 ? 'path-start' : ''}`}
      aria-pressed={data.selected}
      onClick={() => data.onSelect(id)}
    >
      <span className="graph-node-code">{data.code}</span>
      <strong>{data.label}</strong>
      <small>{data.subtitle}</small>
      <span className={`graph-node-status ${data.status}`}>{statusText}</span>
      {data.pathIndex >= 0 && <em>路径第 {data.pathIndex + 1} 步</em>}
    </button>
    <Handle id="source" type="source" position={Position.Bottom} isConnectable={false} className="graph-handle" />
  </div>;
}

const knowledgeGraphNodeTypes = { knowledgePoint: KnowledgeGraphPoint };

export interface KnowledgeGraphCanvasProps {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
  profile: ProfilePoint[];
  selectedId: string;
  pathNodes: string[];
  onSelect: (id: string) => void;
}

export default function KnowledgeGraphCanvas({ nodes, edges, profile, selectedId, pathNodes, onSelect }: KnowledgeGraphCanvasProps) {
  const layoutNodes = useMemo(() => buildKnowledgeGraphFlowNodes(nodes, profile, selectedId, pathNodes, onSelect), [nodes, onSelect, pathNodes, profile, selectedId]);
  const layoutEdges = useMemo(() => buildKnowledgeGraphFlowEdges(nodes, edges, pathNodes), [edges, nodes, pathNodes]);
  const [flowNodes, setFlowNodes, onNodesChange] = useNodesState<KnowledgeGraphFlowNode>(layoutNodes);
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState<Edge>(layoutEdges);
  const flowInstanceKey = useMemo(() => `${layoutNodes.map((node) => node.id).join('|')}::${layoutEdges.map((edge) => `${edge.id}:${edge.className || ''}`).join('|')}`, [layoutEdges, layoutNodes]);


  useEffect(() => {
    setFlowNodes((current) => layoutNodes.map((node) => ({
      ...node,
      position: current.find((item) => item.id === node.id)?.position || node.position,
    })));
  }, [layoutNodes, setFlowNodes]);
  useEffect(() => { setFlowEdges(layoutEdges); }, [layoutEdges, setFlowEdges]);

  return <div className="graph-flow" data-testid="knowledge-graph-canvas">
    <ReactFlow
      key={flowInstanceKey}
      nodes={flowNodes}
      edges={flowEdges}
      nodeTypes={knowledgeGraphNodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodesConnectable={false}
      minZoom={0.35}
      maxZoom={1.8}
      fitView
      fitViewOptions={{ padding: 0.18 }}
    >
      <MiniMap pannable zoomable nodeColor={(node) => node.id === selectedId ? '#0b706b' : pathNodes.includes(node.id) ? '#2f9188' : '#a8bebc'} />
      <Controls showInteractive={false} />
      <Background gap={22} size={1} color="#d8e2e1" />
    </ReactFlow>
  </div>;
}
