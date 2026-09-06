export const SITE_TITLE = '储能学习空间';
export const DEFAULT_ROUTE_TITLE = '课程平台';

const ROUTE_TITLES: ReadonlyArray<{ pattern: RegExp; title: string }> = [
  { pattern: /^\/teacher\/courses\/[^/]+\/question-bank(\/|$)/, title: '题库管理' },
  { pattern: /^\/teacher\/courses\/[^/]+\/assignments\/[^/]+(\/|$)/, title: '作业详情' },
  { pattern: /^\/teacher\/courses\/[^/]+\/assignments(\/|$)/, title: '作业管理' },
  { pattern: /^\/teacher\/courses\/[^/]+\/exams(\/|$)/, title: '考试管理' },
  { pattern: /^\/teacher\/courses\/[^/]+\/activities(\/|$)/, title: '活动管理' },
  { pattern: /^\/teacher\/courses\/[^/]+\/resources(\/|$)/, title: '资源管理' },
  { pattern: /^\/teacher\/courses\/[^/]+\/(gradebook|grading|analytics)(\/|$)/, title: '成绩册' },
  { pattern: /^\/teacher\/courses\/[^/]+\/agent(\/|$)/, title: '课程 Agent' },
  { pattern: /^\/teacher\/courses\/[^/]+(\/|$)/, title: '教师课程空间' },
  { pattern: /^\/teacher\/courses(\/|$)/, title: '教师课程管理' },
  { pattern: /^\/teacher\/questions(\/|$)/, title: '题库管理' },
  { pattern: /^\/teacher\/assignments\/[^/]+(\/|$)/, title: '作业详情' },
  { pattern: /^\/teacher\/assignments(\/|$)/, title: '作业管理' },
  { pattern: /^\/teacher\/exams(\/|$)/, title: '考试管理' },
  { pattern: /^\/teacher\/activities(\/|$)/, title: '活动管理' },
  { pattern: /^\/teacher\/resources(\/|$)/, title: '资源管理' },
  { pattern: /^\/teacher\/gradebook(\/|$)/, title: '成绩册' },
  { pattern: /^\/teacher(\/|$)/, title: '教师工作台' },
  { pattern: /^\/admin(\/|$)/, title: '管理员工作台' },
  { pattern: /^\/courses\/[^/]+\/resources\/[^/]+(\/|$)/, title: '章节阅读' },
  { pattern: /^\/courses\/[^/]+\/assignments\/[^/]+(\/|$)/, title: '作业详情' },
  { pattern: /^\/courses\/[^/]+\/discussions\/[^/]+(\/|$)/, title: '讨论详情' },
  { pattern: /^\/courses\/[^/]+\/exams\/[^/]+(\/|$)/, title: '考试详情' },
  { pattern: /^\/courses\/[^/]+\/agent(\/|$)/, title: '课程 Agent' },
  { pattern: /^\/courses\/[^/]+\/progress(\/|$)/, title: '学习记录' },
  { pattern: /^\/courses\/[^/]+\/grades(\/|$)/, title: '成绩册' },
  { pattern: /^\/courses\/[^/]+(\/|$)/, title: '课程空间' },
  { pattern: /^\/tasks\/[^/]+(\/|$)/, title: '作业详情' },
  { pattern: /^\/exams\/[^/]+(\/|$)/, title: '考试详情' },
  { pattern: /^\/resources\/[^/]+(\/|$)/, title: '章节阅读' },
  { pattern: /^\/discussions\/[^/]+(\/|$)/, title: '讨论详情' },
  { pattern: /^\/activities\/[^/]+(\/|$)/, title: '活动详情' },
  { pattern: /^\/$/, title: '学习工作台' },
  { pattern: /^\/course(\/|$)/, title: '课程空间' },
  { pattern: /^\/courses(\/|$)/, title: '我的课程' },
  { pattern: /^\/tasks(\/|$)/, title: '待办任务' },
  { pattern: /^\/exams(\/|$)/, title: '考试中心' },
  { pattern: /^\/resources(\/|$)/, title: '资料库' },
  { pattern: /^\/favorites(\/|$)/, title: '资料收藏' },
  { pattern: /^\/knowledge-graph(\/|$)/, title: '学习图谱' },
  { pattern: /^\/discussions(\/|$)/, title: '课程讨论' },
  { pattern: /^\/activities(\/|$)/, title: '课堂活动' },
  { pattern: /^\/messages(\/|$)/, title: '消息通知' },
  { pattern: /^\/search(\/|$)/, title: '全局搜索' },
  { pattern: /^\/help(\/|$)/, title: '帮助中心' },
  { pattern: /^\/settings(\/|$)/, title: '学习设置' },
  { pattern: /^\/assistant(\/|$)/, title: '课程 Agent' },
  { pattern: /^\/profile(\/|$)/, title: '学习记录' },
];

export function resolveRouteTitle(pathname: string): string {
  for (const entry of ROUTE_TITLES) {
    if (entry.pattern.test(pathname)) return entry.title;
  }
  return DEFAULT_ROUTE_TITLE;
}

export function formatDocumentTitle(title: string): string {
  return `${title} · ${SITE_TITLE}`;
}
