import type { Assignment, Chapter } from '../types';

export function pendingAssignments(assignments: Assignment[]): Assignment[] {
  return assignments.filter((assignment) => assignment.status === '待完成' || assignment.status === '进行中');
}

export function chapterStatusLabel(chapter: Pick<Chapter, 'progress' | 'status'>): string {
  if (chapter.status === '已完成' || chapter.progress >= 100) return '已完成';
  if (chapter.progress > 0) return '学习中';
  return '未开始';
}
