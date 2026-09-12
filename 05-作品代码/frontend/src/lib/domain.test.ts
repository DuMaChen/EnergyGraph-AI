import { describe, expect, it } from 'vitest';
import { chapterStatusLabel, pendingAssignments } from './domain';

describe('domain progress helpers', () => {
  it('domain filters pending assignments', () => {
    const result = pendingAssignments([
      { id: 'a', title: 'a', type: '作业', status: '待完成', dueAt: '', questionCount: 1, score: null, progress: 0 },
      { id: 'b', title: 'b', type: '作业', status: '已完成', dueAt: '', questionCount: 1, score: 90, progress: 100 },
    ]);
    expect(result.map((item) => item.id)).toEqual(['a']);
  });

  it('domain maps chapter progress to a stable label', () => {
    expect(chapterStatusLabel({ progress: 0, status: '未开始' })).toBe('未开始');
    expect(chapterStatusLabel({ progress: 20, status: '未开始' })).toBe('学习中');
    expect(chapterStatusLabel({ progress: 100, status: '学习中' })).toBe('已完成');
  });
});
