import type { PlatformData } from '../types';

export const previewData: PlatformData = {
  courses: [{
    id: 1,
    name: '电力系统储能技术',
    teacher: '课程教师',
    className: '储能技术课程班',
    status: 'active',
    progress: 39,
    chapterCount: 6,
    resourceCount: 20,
    lastAccessedAt: null,
  }],
  chapters: [
    { id: 1, name: '第 1 章 概述', progress: 100, status: '已完成', lessons: 3, duration: '3.5 学时' },
    { id: 2, name: '第 2 章 电力系统与储能技术的应用', progress: 86, status: '学习中', lessons: 3, duration: '4 学时' },
    { id: 3, name: '第 3 章 电力储能系统的组成及工作原理', progress: 54, status: '学习中', lessons: 5, duration: '7 学时' },
    { id: 4, name: '第 4 章 电力储能系统的规划配置', progress: 0, status: '未开始', lessons: 3, duration: '5 学时' },
    { id: 5, name: '第 5 章 电力储能系统的接入与运行控制', progress: 0, status: '未开始', lessons: 4, duration: '5.5 学时' },
    { id: 6, name: '第 6 章 电力储能系统的性能检测与评估', progress: 0, status: '未开始', lessons: 2, duration: '4.5 学时' },
  ],
  resources: [
    { id: 'res-31', title: '抽水蓄能电站的组成及工作原理', sourceFile: '3.1 抽水蓄能电站的组成及工作原理.pdf', chapterId: 3, pageStart: 1, pageCount: 29, type: 'PDF', version: '课程教材 v1', available: false, mountStatus: 'pending_mount' },
    { id: 'res-34', title: '储能变流器拓扑及并网控制', sourceFile: '3.4 储能变流器拓扑及并网控制.pdf', chapterId: 3, pageStart: 1, pageCount: 38, type: 'PDF', version: '课程教材 v1', available: false, mountStatus: 'pending_mount' },
    { id: 'res-42', title: '电化学储能系统的规划配置', sourceFile: '4.2 电化学储能系统的规划配置.pdf', chapterId: 4, pageStart: 1, pageCount: 108, type: 'PDF', version: '课程教材 v1', available: false, mountStatus: 'pending_mount' },
    { id: 'res-51', title: '电力储能系统的运行控制', sourceFile: '5.2 电力储能系统的运行控制.pdf', chapterId: 5, pageStart: 1, pageCount: 18, type: '资料', version: '课程教材 v1', available: false, mountStatus: 'pending_mount' },
    { id: 'res-61', title: '电力储能系统的性能检测', sourceFile: '6.1 电力储能系统的性能检测.pdf', chapterId: 6, pageStart: 1, pageCount: 18, type: '资料', version: '课程教材 v1', available: false, mountStatus: 'pending_mount' },
  ],
  assignments: [
    { id: 'assignment-a001', title: '第 3 章章节练习', type: '章节练习', status: '待完成', dueAt: '2026-07-28', questionCount: 8, score: null, progress: 0 },
    { id: 'assignment-a002', title: '储能变流器并网控制讨论', type: '主题讨论', status: '进行中', dueAt: '2026-07-30', questionCount: 1, score: null, progress: 35 },
    { id: 'assignment-a003', title: '第 2 章基础测验', type: '在线测验', status: '已完成', dueAt: '2026-07-20', questionCount: 10, score: 86, progress: 100 },
    { id: 'assignment-a004', title: '储能系统案例分析', type: '综合作业', status: '待完成', dueAt: '2026-08-04', questionCount: 3, score: null, progress: 0 },
  ],
  profile: [
    { id: 'kp-1-1', name: '储能技术基本概念', status: 'mastered', ratio: 0.92 },
    { id: 'kp-2-1', name: '电力系统与储能应用', status: 'mastered', ratio: 0.84 },
    { id: 'kp-3-1', name: '抽水蓄能系统组成', status: 'learning', ratio: 0.62 },
    { id: 'kp-3-4', name: '储能变流器并网控制', status: 'weak', ratio: 0.38 },
    { id: 'kp-4-2', name: '电化学储能规划配置', status: 'unassessed', ratio: null },
  ],
  recommendations: [
    { id: 'rec-1', title: '储能变流器并网控制', type: '章节巩固', reason: '最近练习中有 2 个关键概念尚未稳定', resourceId: 'res-34' },
    { id: 'rec-2', title: '电化学储能系统的规划配置', type: '基础补齐', reason: '先修知识点尚未评估，建议先阅读教材', resourceId: 'res-42' },
    { id: 'rec-3', title: '储能系统的运行控制', type: '综合应用', reason: '基础概念已经掌握，可以进入工程情境练习', resourceId: 'res-51' },
  ],
  notifications: [
    { id: 'notice-preview-1', audience: 'course_all', title: '第 3 章案例练习已更新', body: '请在本周内完成并网控制案例练习。', createdBy: 'preview-teacher', createdAt: '教师公告 · 2 天前', isRead: false },
    { id: 'notice-preview-2', audience: 'course_students', title: '本周完成并网控制章节测验', body: '完成测验后可以查看当前章节反馈。', createdBy: 'preview-system', createdAt: '学习提醒 · 昨天', isRead: true },
    { id: 'notice-preview-3', audience: 'course_all', title: '课程资料 v1 已发布', body: '课程资料目录已更新，文件挂载后即可阅读。', createdBy: 'preview-admin', createdAt: '课程管理员 · 4 天前', isRead: true },
  ],
  unreadNotificationCount: 1,
  studyHours: 12.5,
};

export function overallProgress(chapters: PlatformData['chapters']): number {
  if (!chapters.length) return 0;
  return Math.round(chapters.reduce((sum, chapter) => sum + chapter.progress, 0) / chapters.length);
}
