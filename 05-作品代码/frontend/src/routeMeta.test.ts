import { describe, expect, it } from 'vitest';
import { DEFAULT_ROUTE_TITLE, formatDocumentTitle, resolveRouteTitle } from './routeMeta';

describe('route metadata', () => {
  it('resolves top-level routes to their page titles', () => {
    expect(resolveRouteTitle('/')).toBe('学习工作台');
    expect(resolveRouteTitle('/course')).toBe('课程空间');
    expect(resolveRouteTitle('/courses')).toBe('我的课程');
    expect(resolveRouteTitle('/tasks')).toBe('待办任务');
    expect(resolveRouteTitle('/exams')).toBe('考试中心');
    expect(resolveRouteTitle('/resources')).toBe('资料库');
    expect(resolveRouteTitle('/favorites')).toBe('资料收藏');
    expect(resolveRouteTitle('/knowledge-graph')).toBe('学习图谱');
    expect(resolveRouteTitle('/discussions')).toBe('课程讨论');
    expect(resolveRouteTitle('/activities')).toBe('课堂活动');
    expect(resolveRouteTitle('/messages')).toBe('消息通知');
    expect(resolveRouteTitle('/search')).toBe('全局搜索');
    expect(resolveRouteTitle('/help')).toBe('帮助中心');
    expect(resolveRouteTitle('/settings')).toBe('学习设置');
    expect(resolveRouteTitle('/assistant')).toBe('课程 Agent');
    expect(resolveRouteTitle('/profile')).toBe('学习记录');
  });

  it('resolves detail and nested course routes with specific titles', () => {
    expect(resolveRouteTitle('/tasks/assign-1')).toBe('作业详情');
    expect(resolveRouteTitle('/exams/exam-9')).toBe('考试详情');
    expect(resolveRouteTitle('/resources/res-34')).toBe('章节阅读');
    expect(resolveRouteTitle('/discussions/topic-2')).toBe('讨论详情');
    expect(resolveRouteTitle('/activities/act-7')).toBe('活动详情');
    expect(resolveRouteTitle('/courses/1')).toBe('课程空间');
    expect(resolveRouteTitle('/courses/1/resources/res-34')).toBe('章节阅读');
    expect(resolveRouteTitle('/courses/1/assignments/assign-1')).toBe('作业详情');
    expect(resolveRouteTitle('/courses/1/exams/exam-9')).toBe('考试详情');
    expect(resolveRouteTitle('/courses/1/discussions/topic-2')).toBe('讨论详情');
    expect(resolveRouteTitle('/courses/1/progress')).toBe('学习记录');
    expect(resolveRouteTitle('/courses/1/grades')).toBe('成绩册');
    expect(resolveRouteTitle('/courses/1/agent')).toBe('课程 Agent');
    expect(resolveRouteTitle('/courses/1/materials')).toBe('课程空间');
  });

  it('resolves teacher and admin routes with staff-specific titles', () => {
    expect(resolveRouteTitle('/teacher')).toBe('教师工作台');
    expect(resolveRouteTitle('/teacher/courses')).toBe('教师课程管理');
    expect(resolveRouteTitle('/teacher/courses/1')).toBe('教师课程空间');
    expect(resolveRouteTitle('/teacher/courses/1/question-bank')).toBe('题库管理');
    expect(resolveRouteTitle('/teacher/courses/1/assignments')).toBe('作业管理');
    expect(resolveRouteTitle('/teacher/courses/1/assignments/assign-1')).toBe('作业详情');
    expect(resolveRouteTitle('/teacher/courses/1/exams')).toBe('考试管理');
    expect(resolveRouteTitle('/teacher/courses/1/activities')).toBe('活动管理');
    expect(resolveRouteTitle('/teacher/courses/1/resources')).toBe('资源管理');
    expect(resolveRouteTitle('/teacher/courses/1/gradebook')).toBe('成绩册');
    expect(resolveRouteTitle('/teacher/courses/1/grading')).toBe('成绩册');
    expect(resolveRouteTitle('/teacher/courses/1/analytics')).toBe('成绩册');
    expect(resolveRouteTitle('/teacher/questions')).toBe('题库管理');
    expect(resolveRouteTitle('/teacher/assignments')).toBe('作业管理');
    expect(resolveRouteTitle('/teacher/assignments/assign-1')).toBe('作业详情');
    expect(resolveRouteTitle('/teacher/exams')).toBe('考试管理');
    expect(resolveRouteTitle('/teacher/activities')).toBe('活动管理');
    expect(resolveRouteTitle('/teacher/resources')).toBe('资源管理');
    expect(resolveRouteTitle('/teacher/gradebook')).toBe('成绩册');
    expect(resolveRouteTitle('/admin')).toBe('管理员工作台');
    expect(resolveRouteTitle('/admin/kb-versions')).toBe('管理员工作台');
  });

  it('falls back to the default title for unknown paths and is pathname-based', () => {
    expect(resolveRouteTitle('/unknown-path')).toBe(DEFAULT_ROUTE_TITLE);
    expect(resolveRouteTitle('/search')).toBe('全局搜索');
    expect(resolveRouteTitle('/resources/res-1')).toBe('章节阅读');
    expect(resolveRouteTitle('/')).not.toBe(DEFAULT_ROUTE_TITLE);
  });

  it('formats the document title with the site name', () => {
    expect(formatDocumentTitle('学习工作台')).toBe('学习工作台 · 储能学习空间');
    expect(formatDocumentTitle(DEFAULT_ROUTE_TITLE)).toBe('课程平台 · 储能学习空间');
  });
});
