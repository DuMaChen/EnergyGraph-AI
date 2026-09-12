/* GENERATED shared UI helpers extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { useAppStore } from './state/app';
import { ActivityKind, ExamDetail, StudentTask, StudentTaskCounts, StudentTaskKind, StudentTaskStatus } from './types';

export const previewExams: ExamDetail[] = [{
  id: 'exam-preview-1', title: '第 3 章储能系统限时考试', type: '考试', status: '进行中', availability: 'open',
  openAt: '2026-07-20T08:00:00+08:00', closeAt: '2026-08-20T23:59:00+08:00', durationSeconds: 1800, allowAttempts: 1, questionCount: 2,
  questions: [
    { id: 'exam-q-1', prompt: '储能系统参与电网运行时首先需要满足哪项约束？', questionType: 'single_choice', options: ['功率平衡', '取消保护'], maxScore: 10 },
    { id: 'exam-q-2', prompt: '简述储能变流器并网控制的两个关键目标。', questionType: 'short_answer', options: [], maxScore: 10 },
  ], myAttempts: [], mySubmissions: [],
}];

export const previewStudentTasks: StudentTask[] = [
  { id: 'task-preview-assignment', sourceId: 'assignment-a001', kind: 'assignment', title: '第 3 章章节练习', summary: '完成储能系统组成与工作原理练习。', status: 'pending', dueAt: '2026-08-04T23:59:00+08:00', updatedAt: '2026-07-29T09:00:00+08:00', progress: 0 },
  { id: 'task-preview-exam', sourceId: 'exam-preview-1', kind: 'exam', title: '第 3 章储能系统限时考试', summary: '考试时长 30 分钟，进入后可查看考试规则。', status: 'in_progress', dueAt: '2026-08-20T23:59:00+08:00', updatedAt: '2026-07-29T08:40:00+08:00', progress: 35 },
  { id: 'task-preview-discussion', sourceId: 'discussion-preview-1', kind: 'discussion', title: '并网控制约束讨论', summary: '围绕功率平衡与保护约束补充你的观点。', status: 'pending', dueAt: null, updatedAt: '2026-07-28T18:20:00+08:00', progress: 0 },
  { id: 'task-preview-notification', sourceId: 'notice-preview-1', kind: 'notification', title: '第 3 章案例练习已更新', summary: '请在本周内完成并网控制案例练习。', status: 'completed', dueAt: null, updatedAt: '2026-07-27T10:00:00+08:00', progress: 100 },
];

export const studentTaskKinds: Array<{ value: '' | StudentTaskKind; label: string }> = [
  { value: '', label: '全部类型' },
  { value: 'assignment', label: '作业' },
  { value: 'exam', label: '考试' },
  { value: 'discussion', label: '讨论' },
  { value: 'notification', label: '通知' },
];

export const studentTaskStatuses: Array<{ value: '' | StudentTaskStatus; label: string }> = [
  { value: '', label: '全部' },
  { value: 'pending', label: '待完成' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed', label: '已完成' },
  { value: 'expired', label: '已过期' },
];

function countStudentTasks(items: StudentTask[]): StudentTaskCounts {
  return {
    byStatus: {
      pending: items.filter((item) => item.status === 'pending').length,
      in_progress: items.filter((item) => item.status === 'in_progress').length,
      completed: items.filter((item) => item.status === 'completed').length,
      expired: items.filter((item) => item.status === 'expired').length,
    },
    byKind: {
      assignment: items.filter((item) => item.kind === 'assignment').length,
      exam: items.filter((item) => item.kind === 'exam').length,
      discussion: items.filter((item) => item.kind === 'discussion').length,
      notification: items.filter((item) => item.kind === 'notification').length,
    },
  };
}

export const previewStudentTaskCounts = countStudentTasks(previewStudentTasks);

export function activityKindLabel(kind: ActivityKind, detailed = false) {
  if (kind === 'checkin') return detailed ? '课堂签到' : '签到';
  if (kind === 'quick_response') return detailed ? '课堂抢答' : '抢答';
  if (kind === 'random_selection') return detailed ? '课堂随机选人' : '随机选人';
  if (kind === 'group_task') return detailed ? '课堂分组任务' : '分组任务';
  if (kind === 'poll') return detailed ? '单选投票' : '投票';
  return detailed ? '多选问卷' : '问卷';
}

export function isOptionlessActivityKind(kind: ActivityKind) {
  return kind === 'checkin' || kind === 'quick_response' || kind === 'random_selection';
}

export function isSingleConfigurationActivityKind(kind: ActivityKind) {
  return isOptionlessActivityKind(kind) || kind === 'group_task';
}

export function syncGlobalNotificationState(nextUnreadCount: number, notificationId?: string, markAll = false) {
  const appState = useAppStore.getState();
  if (!appState.data) return;
  const shouldUpdateItems = markAll || Boolean(notificationId);
  if (!shouldUpdateItems && appState.data.unreadNotificationCount === nextUnreadCount) return;
  appState.setData({
    ...appState.data,
    unreadNotificationCount: nextUnreadCount,
    notifications: shouldUpdateItems
      ? appState.data.notifications.map((item) => markAll || item.id === notificationId ? { ...item, isRead: true } : item)
      : appState.data.notifications,
  });
}
