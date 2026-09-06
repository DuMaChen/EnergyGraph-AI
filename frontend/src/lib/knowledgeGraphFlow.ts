import { MarkerType, Position, type Edge, type Node } from '@xyflow/react';
import type { KnowledgeGraphEdge, KnowledgeGraphNode, ProfilePoint } from '../types';

export type KnowledgeGraphPointData = {
  code: string;
  label: string;
  subtitle: string;
  pathIndex: number;
  selected: boolean;
  status: ProfilePoint['status'];
  onSelect: (id: string) => void;
};

export type KnowledgeGraphFlowNode = Node<KnowledgeGraphPointData, 'knowledgePoint'>;

const KNOWLEDGE_GRAPH_NODE_WIDTH = 218;
const KNOWLEDGE_GRAPH_NODE_HEIGHT = 160;
const KNOWLEDGE_GRAPH_HANDLE_X = (KNOWLEDGE_GRAPH_NODE_WIDTH - 1) / 2;

export function buildKnowledgeGraphFlowNodes(
  nodes: KnowledgeGraphNode[],
  profile: ProfilePoint[],
  selectedId: string,
  pathNodes: string[],
  onSelect: (id: string) => void,
): KnowledgeGraphFlowNode[] {
  const mastery = new Map(profile.map((item) => [item.id, item.status]));
  const chapters = [...new Set(nodes.map((node) => node.chapterId))].sort((left, right) => left - right);
  const chapterIndexes = new Map(chapters.map((chapter, index) => [chapter, index]));
  const chapterOffsets = new Map<number, number>();
  return [...nodes].sort((left, right) => left.chapterId - right.chapterId || left.id.localeCompare(right.id)).map((node) => {
    const offset = chapterOffsets.get(node.chapterId) || 0;
    chapterOffsets.set(node.chapterId, offset + 1);
    const pathIndex = pathNodes.indexOf(node.id);
    return {
      id: node.id,
      type: 'knowledgePoint' as const,
      // Give React Flow a stable first measurement so edges can be positioned
      // before the ResizeObserver callback runs for the custom node.
      width: KNOWLEDGE_GRAPH_NODE_WIDTH,
      height: KNOWLEDGE_GRAPH_NODE_HEIGHT,
      measured: { width: KNOWLEDGE_GRAPH_NODE_WIDTH, height: KNOWLEDGE_GRAPH_NODE_HEIGHT },
      handles: [
        { id: 'target', type: 'target', position: Position.Top, x: KNOWLEDGE_GRAPH_HANDLE_X, y: 0, width: 1, height: 1 },
        { id: 'source', type: 'source', position: Position.Bottom, x: KNOWLEDGE_GRAPH_HANDLE_X, y: KNOWLEDGE_GRAPH_NODE_HEIGHT - 1, width: 1, height: 1 },
      ],
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      dragHandle: '.graph-node-drag-handle',
      position: { x: (chapterIndexes.get(node.chapterId) || 0) * 270, y: offset * 158 },
      data: {
        code: node.id,
        label: node.name,
        subtitle: `第 ${node.chapterId} 章 · ${node.category}`,
        pathIndex,
        selected: node.id === selectedId,
        status: mastery.get(node.id) || 'unassessed',
        onSelect,
      },
    } satisfies KnowledgeGraphFlowNode;
  });
}

export function buildKnowledgeGraphFlowEdges(nodes: KnowledgeGraphNode[], edges: KnowledgeGraphEdge[], pathNodes: string[]): Edge[] {
  const visibleIds = new Set(nodes.map((node) => node.id));
  return edges.filter((edge) => visibleIds.has(edge.sourceId) && visibleIds.has(edge.targetId)).map((edge) => {
    const sourceIndex = pathNodes.indexOf(edge.sourceId);
    const isPathEdge = edge.relationType === 'prerequisite' && sourceIndex >= 0 && pathNodes[sourceIndex + 1] === edge.targetId;
    return {
      id: edge.id,
      source: edge.sourceId,
      target: edge.targetId,
      type: 'smoothstep',
      animated: isPathEdge,
      className: isPathEdge ? 'graph-flow-edge path-edge' : 'graph-flow-edge',
      markerEnd: { type: MarkerType.ArrowClosed },
      data: { relationType: edge.relationType },
    } satisfies Edge;
  });
}
