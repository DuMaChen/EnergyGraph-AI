import { describe, expect, it, vi } from 'vitest';
import { buildKnowledgeGraphFlowEdges, buildKnowledgeGraphFlowNodes } from './lib/knowledgeGraphFlow';
import type { KnowledgeGraphEdge, KnowledgeGraphNode, ProfilePoint } from './types';

const nodes: KnowledgeGraphNode[] = [
  { id: 'kp-1', name: '基础', chapterId: 1, category: '概念', description: '', neighbors: [] },
  { id: 'kp-2', name: '进阶', chapterId: 1, category: '应用', description: '', neighbors: [] },
  { id: 'kp-3', name: '综合', chapterId: 2, category: '综合', description: '', neighbors: [] },
];
const edges: KnowledgeGraphEdge[] = [
  { id: 'edge-1', sourceId: 'kp-1', targetId: 'kp-2', relationType: 'prerequisite' },
  { id: 'edge-related-same-endpoints', sourceId: 'kp-1', targetId: 'kp-2', relationType: 'related' },
  { id: 'edge-2', sourceId: 'kp-2', targetId: 'kp-3', relationType: 'prerequisite' },
  { id: 'edge-cross-course', sourceId: 'kp-1', targetId: 'other-course', relationType: 'related' },
];
const profile: ProfilePoint[] = [
  { id: 'kp-1', name: '基础', status: 'mastered', ratio: 1 },
  { id: 'kp-2', name: '进阶', status: 'weak', ratio: 0.4 },
];

describe('knowledge graph flow projection', () => {
  it('builds stable chapter columns with selection, mastery and path state', () => {
    const onSelect = vi.fn();
    const result = buildKnowledgeGraphFlowNodes(nodes, profile, 'kp-2', ['kp-1', 'kp-2', 'kp-3'], onSelect);
    expect(result.map((node) => [node.id, node.position.x, node.position.y])).toEqual([
      ['kp-1', 0, 0],
      ['kp-2', 0, 158],
      ['kp-3', 270, 0],
    ]);
    expect(result[0]?.data).toMatchObject({ pathIndex: 0, selected: false, status: 'mastered' });
    expect(result[0]?.dragHandle).toBe('.graph-node-drag-handle');
    expect(result[0]).toMatchObject({ width: 218, height: 160, sourcePosition: 'bottom', targetPosition: 'top' });
    expect(result[0]?.handles).toMatchObject([
      { id: 'target', type: 'target', position: 'top' },
      { id: 'source', type: 'source', position: 'bottom' },
    ]);
    expect(result[1]?.data).toMatchObject({ pathIndex: 1, selected: true, status: 'weak' });
    expect(result[2]?.data).toMatchObject({ pathIndex: 2, selected: false, status: 'unassessed' });
  });

  it('keeps only visible edges and highlights consecutive path edges', () => {
    const result = buildKnowledgeGraphFlowEdges(nodes, edges, ['kp-1', 'kp-2', 'kp-3']);
    expect(result).toHaveLength(3);
    expect(result.map((edge) => [edge.id, edge.animated, edge.className])).toEqual([
      ['edge-1', true, 'graph-flow-edge path-edge'],
      ['edge-related-same-endpoints', false, 'graph-flow-edge'],
      ['edge-2', true, 'graph-flow-edge path-edge'],
    ]);
  });
});
