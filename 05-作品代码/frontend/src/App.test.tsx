import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';
import { previewData } from './data/preview';
import { previewStudentTasks } from './ui-helpers';
import { useAppStore } from './state/app';

type QuickResponseView = 'open' | 'won' | 'lost';

function apiOk(data: unknown, status = 200): Response {
  return { ok: true, status, json: async () => ({ status: 'ok', data }) } as Response;
}

function apiFailure(status: number, code: string, message: string): Response {
  return { ok: false, status, json: async () => ({ status: 'error', data: null, error: { code, message } }) } as Response;
}

function quickResponseActivity(id: string, view: QuickResponseView) {
  const won = view === 'won';
  const closed = view !== 'open';
  return {
    id,
    kind: 'quick_response',
    title: '第 3 章课堂抢答',
    body: '请在教师发出口令后抢答。',
    options: [],
    status: closed ? 'closed' : 'published',
    max_attempts: 1,
    has_responded: won,
    attempts_used: won ? 1 : 0,
    can_respond: !closed,
    can_reopen: !closed,
    next_attempt: closed ? null : 1,
    my_response: won ? { id: `${id}-response`, activity_id: id, attempt: 1, answers: ['claim'], submitted_at: '2026-07-29T08:00:00Z' } : null,
  };
}

function quickResponseResults(id: string, view: QuickResponseView, participants: Array<{ user_ref: string; submitted_at: string }> = []) {
  const closed = view !== 'open';
  return {
    activity_id: id,
    kind: 'quick_response',
    total_responses: closed ? 1 : 0,
    has_responded: view === 'won',
    results_available: closed,
    options: [],
    participants,
  };
}

function emptyApiData(): Response {
  return apiOk({ items: [], nodes: [], unread_count: 0 });
}

describe('learning platform component', () => {
  beforeEach(() => {
    useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('preview test')));
  });

  it('component shows a preview-mode learning workspace', async () => {
    render(<App />);
    expect(await screen.findByText('当前为预览模式，展示示例课程数据；登录课程平台并完成接口配置后才会写入真实学习记录。')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: '登录课程平台' })).toHaveAttribute('href', expect.stringContaining('/login/index.php?wantsurl='));
    expect(screen.getByRole('link', { name: '创建账号' })).toHaveAttribute('href', '/login/signup.php');
    expect(screen.getAllByText('电力系统储能技术').length).toBeGreaterThan(0);
    expect(vi.mocked(fetch).mock.calls.some((call) => String(call[0]).includes('/api/student/learning-position'))).toBe(false);
    fireEvent.click(await screen.findByRole('button', { name: '继续学习' }));
    await waitFor(() => expect(window.location.pathname).toBe('/course'));
  });

  it('component does not request a student learning position for a teacher session', async () => {
    window.history.pushState({}, '', '/');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('link', { name: '教师工作台' })).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.some((call) => String(call[0]).includes('/api/student/learning-position'))).toBe(false);
    expect(screen.queryByText('正在读取最近学习位置')).not.toBeInTheDocument();
  });

  it('component disables duplicate resume actions while loading and opens the saved page', async () => {
    window.history.pushState({}, '', '/');
    let resolvePosition: ((response: Response) => void) | null = null;
    let positionRequests = 0;
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/learning-position')) {
        positionRequests += 1;
        return new Promise<Response>((resolve) => { resolvePosition = resolve; });
      }
      return emptyApiData();
    });

    render(<App />);
    const loadingButton = await screen.findByRole('button', { name: '正在定位最近学习' });
    expect(loadingButton).toBeDisabled();
    expect(loadingButton).toHaveAttribute('aria-busy', 'true');
    fireEvent.click(loadingButton);
    expect(positionRequests).toBe(1);

    await act(async () => {
      resolvePosition?.(apiOk({ position: {
        course_id: 1,
        resource: { id: 'res-34', title: '储能变流器拓扑及并网控制', source_file: '3.4.pdf', chapter_id: 3, page_start: 1, page_end: 38, status: 'published', available: true, mount_status: 'ready' },
        progress: { resource_id: 'res-34', page: 12, percent: 31.5, completed: false, version: 4, updated_at: '2026-07-29T08:30:00Z', has_saved_progress: true },
      } }));
      await Promise.resolve();
    });

    expect(await screen.findByText('第 3 章 · 第 12 页 · 已学习 32%')).toBeInTheDocument();
    const resumeButton = screen.getByRole('button', { name: '继续：储能变流器拓扑及并网控制' });
    fireEvent.click(resumeButton);
    await waitFor(() => {
      expect(window.location.pathname).toBe('/courses/1/resources/res-34');
      expect(window.location.search).toBe('?page=12');
    });
  });

  it('component treats a null learning position as an honest current-course fallback', async () => {
    window.history.pushState({}, '', '/');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 7, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/learning-position')) return apiOk({ position: null });
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByText('尚无已保存的学习位置')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '进入当前课程' }));
    await waitFor(() => expect(window.location.pathname).toBe('/courses/7'));
  });

  it('component labels an unmounted saved resource as a status view instead of readable content', async () => {
    window.history.pushState({}, '', '/');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/learning-position')) return apiOk({ position: {
        course_id: 1,
        resource: { id: 'res-pending', title: null, source_file: 'pending.pdf', chapter_id: 3, page_start: 1, page_end: 20, status: 'published', version: 'v1', available: false, mount_status: 'pending_mount' },
        progress: { resource_id: 'res-pending', page: 8, percent: 40, completed: false, version: 2, updated_at: '2026-07-29T08:30:00Z', has_saved_progress: true },
      } });
      return emptyApiData();
    });

    render(<App />);
    const statusButton = await screen.findByRole('button', { name: '查看状态：pending' });
    expect(screen.queryByRole('button', { name: '继续：pending' })).not.toBeInTheDocument();
    fireEvent.click(statusButton);
    await waitFor(() => {
      expect(window.location.pathname).toBe('/courses/1/resources/res-pending');
      expect(window.location.search).toBe('?page=8');
    });
  });

  it('component reports a resume failure and retries without pretending it found a position', async () => {
    window.history.pushState({}, '', '/');
    let attempts = 0;
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/learning-position')) {
        attempts += 1;
        return attempts === 1 ? apiFailure(503, 'learning_position_unavailable', '学习位置服务暂时不可用') : apiOk({ position: null });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByText('无法恢复最近学习位置')).toBeInTheDocument();
    expect(screen.getByText('学习位置服务暂时不可用')).toBeInTheDocument();
    expect(window.location.pathname).toBe('/');
    fireEvent.click(screen.getByRole('button', { name: '重新定位' }));
    expect(await screen.findByText('尚无已保存的学习位置')).toBeInTheDocument();
    expect(attempts).toBe(2);
  });

  it('component restores the latest learning position from the API after remounting', async () => {
    window.history.pushState({}, '', '/');
    let positionRequests = 0;
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/learning-position')) {
        positionRequests += 1;
        const page = positionRequests === 1 ? 4 : 9;
        const title = positionRequests === 1 ? '第一次加载的资料' : '刷新后恢复的资料';
        return apiOk({ position: {
          course_id: 1,
          resource: { id: 'res-refresh', title, source_file: 'refresh.pdf', chapter_id: 2, page_start: 1, page_end: 20, status: 'published', available: true, mount_status: 'ready' },
          progress: { resource_id: 'res-refresh', page, percent: page * 5, completed: false, version: positionRequests, updated_at: '2026-07-29T08:30:00Z', has_saved_progress: true },
        } });
      }
      return emptyApiData();
    });

    const firstRender = render(<App />);
    expect(await screen.findByText('第一次加载的资料')).toBeInTheDocument();
    expect(screen.getByText('第 2 章 · 第 4 页 · 已学习 20%')).toBeInTheDocument();
    firstRender.unmount();
    useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });

    render(<App />);
    expect(await screen.findByText('刷新后恢复的资料')).toBeInTheDocument();
    expect(screen.getByText('第 2 章 · 第 9 页 · 已学习 45%')).toBeInTheDocument();
    expect(positionRequests).toBe(2);
  });

  it('component preview task center exposes assignments, exams, discussions and notifications', async () => {
    window.history.pushState({}, '', '/tasks');
    render(<App />);

    expect(await screen.findByRole('heading', { name: '待办任务' })).toBeInTheDocument();
    expect(screen.getByText('第 3 章章节练习')).toBeInTheDocument();
    expect(screen.getByText('第 3 章储能系统限时考试')).toBeInTheDocument();
    expect(screen.getByText('并网控制约束讨论')).toBeInTheDocument();
    expect(screen.getByText('第 3 章案例练习已更新')).toBeInTheDocument();
  });

  it('component task filters and refresh issue fresh unified task requests', async () => {
    window.history.pushState({}, '', '/tasks');
    const taskRequests: string[] = [];
    const allItems = [
      { id: 'assignment:a-1', source_id: 'a-1', kind: 'assignment', title: '服务端作业', summary: '完成章节作业', status: 'pending', due_at: '2026-08-01T08:00:00Z', updated_at: '2026-07-29T08:00:00Z', progress: 0 },
      { id: 'exam:e-1', source_id: 'e-1', kind: 'exam', title: '服务端考试', summary: '继续考试', status: 'in_progress', due_at: '2026-08-02T08:00:00Z', updated_at: '2026-07-29T08:10:00Z', progress: 50 },
      { id: 'discussion:d-1', source_id: 'd-1', kind: 'discussion', title: '服务端讨论', summary: '参与主题', status: 'pending', due_at: null, updated_at: '2026-07-29T08:20:00Z', progress: 0 },
      { id: 'notification:n-1', source_id: 'n-1', kind: 'notification', title: '服务端通知', summary: '查看公告', status: 'completed', due_at: null, updated_at: '2026-07-29T08:30:00Z', progress: 100 },
    ];
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/tasks?')) {
        taskRequests.push(url);
        const query = new URLSearchParams(url.split('?')[1]);
        const kind = query.get('kind');
        const status = query.get('status');
        const items = allItems.filter((item) => (!kind || item.kind === kind) && (!status || item.status === status));
        return apiOk({ items, page: 1, page_size: 10, total: items.length, counts: { by_status: { pending: 2, in_progress: 1, completed: 1, expired: 0 }, by_kind: { assignment: 1, exam: 1, discussion: 1, notification: 1 } } });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByText('服务端作业')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /考试/ }));
    expect(await screen.findByText('服务端考试')).toBeInTheDocument();
    expect(screen.queryByText('服务端作业')).not.toBeInTheDocument();
    await waitFor(() => expect(taskRequests.at(-1)).toContain('kind=exam'));

    fireEvent.click(screen.getByRole('tab', { name: /进行中/ }));
    await waitFor(() => expect(taskRequests.at(-1)).toContain('status=in_progress'));
    const beforeRefresh = taskRequests.length;
    fireEvent.click(screen.getByRole('button', { name: '刷新状态' }));
    await waitFor(() => expect(taskRequests.length).toBe(beforeRefresh + 1));
    expect(taskRequests.at(-1)).toContain('kind=exam&status=in_progress');
  });

  it('component task center exposes a retry without treating failure as empty data', async () => {
    window.history.pushState({}, '', '/tasks');
    let attempts = 0;
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/tasks?')) {
        attempts += 1;
        if (attempts === 1) return apiFailure(503, 'task_center_unavailable', '任务状态暂时不可用');
        return apiOk({ items: [], page: 1, page_size: 10, total: 0, counts: { by_status: { pending: 0, in_progress: 0, completed: 0, expired: 0 }, by_kind: { assignment: 0, exam: 0, discussion: 0, notification: 0 } } });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('alert')).toHaveTextContent('任务状态暂时不可用');
    expect(screen.queryByText('当前筛选下没有任务。')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '重试' }));
    expect(await screen.findByText('当前筛选下没有任务。')).toBeInTheDocument();
    expect(attempts).toBe(2);
  });

  it('component task center ignores a stale response after a faster filter wins', async () => {
    window.history.pushState({}, '', '/tasks');
    let resolveSlowAssignment: ((response: Response) => void) | null = null;
    const counts = { by_status: { pending: 1, in_progress: 1, completed: 0, expired: 0 }, by_kind: { assignment: 1, exam: 1, discussion: 0, notification: 0 } };
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/student/tasks?')) {
        const kind = new URLSearchParams(url.split('?')[1]).get('kind');
        if (kind === 'assignment') return new Promise<Response>((resolve) => { resolveSlowAssignment = resolve; });
        if (kind === 'exam') return apiOk({ items: [{ id: 'exam:fast', source_id: 'fast', kind: 'exam', title: '较新的考试结果', summary: '', status: 'in_progress', due_at: null, updated_at: '2026-07-29T08:00:00Z', progress: 50 }], page: 1, page_size: 10, total: 1, counts });
        return apiOk({ items: [], page: 1, page_size: 10, total: 0, counts });
      }
      return emptyApiData();
    });

    render(<App />);
    await screen.findByText('当前筛选下没有任务。');
    fireEvent.click(screen.getByRole('button', { name: /作业/ }));
    await waitFor(() => expect(resolveSlowAssignment).not.toBeNull());
    fireEvent.click(screen.getByRole('button', { name: /考试/ }));
    expect(await screen.findByText('较新的考试结果')).toBeInTheDocument();

    await act(async () => {
      resolveSlowAssignment?.(apiOk({ items: [{ id: 'assignment:slow', source_id: 'slow', kind: 'assignment', title: '过期的作业响应', summary: '', status: 'pending', due_at: null, updated_at: '2026-07-29T07:00:00Z', progress: 0 }], page: 1, page_size: 10, total: 1, counts }));
      await Promise.resolve();
    });
    expect(screen.getByText('较新的考试结果')).toBeInTheDocument();
    expect(screen.queryByText('过期的作业响应')).not.toBeInTheDocument();
  });

  it('component reader exposes an explicit pending-mount state instead of fake PDF content', async () => {
    window.history.pushState({}, '', '/resources/res-34');
    render(<App />);
    expect((await screen.findAllByText('文件待挂载')).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('课程已登记这份资料，但当前环境没有可读取的 PDF 文件。挂载与 manifest 校验完成后，阅读器才会开放。')).toBeInTheDocument();
    expect(screen.queryByTitle('储能变流器拓扑及并网控制')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '收藏资料' }));
    expect(screen.getByRole('button', { name: '取消收藏' })).toBeInTheDocument();
    fireEvent.change(screen.getByRole('textbox', { name: '第 1 页笔记' }), { target: { value: '待复习：并网控制' } });
    fireEvent.click(screen.getByRole('button', { name: '保存笔记' }));
    expect(await screen.findByText('笔记已保存。')).toBeInTheDocument();
  });

  it('component global search, help and settings routes are usable in preview mode', async () => {
    window.history.pushState({}, '', '/search?q=储能变流器');
    render(<App />);
    expect(await screen.findByRole('heading', { name: '搜索“储能变流器”' })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /储能变流器拓扑及并网控制/ })).toBeInTheDocument();

    window.history.pushState({}, '', '/help');
    render(<App />);
    expect(await screen.findByRole('heading', { name: '帮助中心' })).toBeInTheDocument();

    window.localStorage.clear();
    window.history.pushState({}, '', '/settings');
    render(<App />);
    expect(await screen.findByRole('heading', { name: '学习设置' })).toBeInTheDocument();
    const notifications = screen.getByRole('checkbox', { name: /课程通知提醒/ });
    fireEvent.click(notifications);
    expect(window.localStorage.getItem('learning-settings:notifications')).toBe('false');
  });

  it('component resource list filters by search, reports visible counts and clears the filter', async () => {
    window.history.pushState({}, '', '/resources');
    render(<App />);
    expect(await screen.findByRole('heading', { name: '课程资料' })).toBeInTheDocument();
    expect(document.querySelectorAll('.resource-card')).toHaveLength(5);
    expect(screen.getByText(/共 5 份资料，当前显示 5 份/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '清除筛选' })).toBeDisabled();

    const search = screen.getByRole('textbox', { name: '搜索资料' }) as HTMLInputElement;
    fireEvent.change(search, { target: { value: '规划' } });
    await waitFor(() => expect(document.querySelectorAll('.resource-card')).toHaveLength(1));
    expect(screen.getByText(/共 5 份资料，当前显示 1 份/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: '电化学储能系统的规划配置' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: '储能变流器拓扑及并网控制' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: '清除筛选' })).toBeEnabled();

    fireEvent.change(search, { target: { value: '不存在的关键字' } });
    await waitFor(() => expect(screen.getByText('没有匹配的课程资料。')).toBeInTheDocument());
    expect(screen.getByText(/共 5 份资料，当前显示 0 份/)).toBeInTheDocument();
    expect(document.querySelectorAll('.resource-card')).toHaveLength(0);

    fireEvent.click(screen.getByRole('button', { name: '清除筛选' }));
    await waitFor(() => expect(document.querySelectorAll('.resource-card')).toHaveLength(5));
    expect(screen.getByText(/共 5 份资料，当前显示 5 份/)).toBeInTheDocument();
    expect(search.value).toBe('');
  });

  it('component search results support arrow-key navigation with roving tab stops', async () => {
    window.history.pushState({}, '', '/search?q=储能');
    render(<App />);
    await screen.findByRole('heading', { name: '搜索“储能”' });
    await waitFor(() => expect(document.querySelectorAll('.search-result-row').length).toBeGreaterThanOrEqual(2));

    const row = (index: number) => document.querySelectorAll<HTMLButtonElement>('.search-result-row')[index];
    expect(row(0)!.tabIndex).toBe(0);

    await act(async () => { row(0)!.focus(); });
    fireEvent.keyDown(row(0)!, { key: 'ArrowDown' });
    expect(document.activeElement).toBe(row(1));
    await waitFor(() => {
      expect(row(0)!.tabIndex).toBe(-1);
      expect(row(1)!.tabIndex).toBe(0);
    });

    fireEvent.keyDown(row(1)!, { key: 'ArrowUp' });
    expect(document.activeElement).toBe(row(0));

    fireEvent.keyDown(row(0)!, { key: 'End' });
    const last = document.querySelectorAll<HTMLButtonElement>('.search-result-row').length - 1;
    expect(document.activeElement).toBe(row(last));

    fireEvent.keyDown(row(last)!, { key: 'Home' });
    expect(document.activeElement).toBe(row(0));

    fireEvent.keyDown(row(0)!, { key: 'ArrowUp' });
    expect(document.activeElement).toBe(row(0));

    await act(async () => { row(last)!.focus(); });
    expect(row(last)!.tabIndex).toBe(0);
    expect(row(0)!.tabIndex).toBe(-1);
  });

  it('component exposes ARIA table semantics on student and teacher data tables', async () => {
    window.history.pushState({}, '', '/tasks');
    render(<App />);
    const taskTable = await screen.findByRole('table', { name: '任务列表' });
    expect(within(taskTable).getAllByRole('columnheader').map((node) => node.textContent)).toEqual(['任务', '截止时间', '状态', '操作']);
    expect(within(taskTable).getAllByRole('row')).toHaveLength(1 + previewStudentTasks.length);

    window.history.pushState({}, '', '/exams');
    render(<App />);
    const examTable = await screen.findByRole('table', { name: '考试列表' });
    expect(within(examTable).getAllByRole('columnheader')).toHaveLength(4);

    window.history.pushState({}, '', '/courses/1/grades');
    render(<App />);
    const gradeTable = await screen.findByRole('table', { name: '任务成绩' });
    expect(within(gradeTable).getAllByRole('columnheader')).toHaveLength(4);
    expect(within(gradeTable).getAllByRole('cell').length).toBeGreaterThan(0);

    window.history.pushState({}, '', '/teacher/resources');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/teacher/resources')) return apiOk({ items: [{ id: 'tr-1', title: '教师资料 1', chapter_id: 3, source_file: '3.4.pdf', page_start: 1, page_end: 38, sha256: 'abc', version: 'v1', available: false, mount_status: 'pending_mount', source_reference: '教材', status: 'draft', revision: 1, revisions: [{ id: 'r1', resource_id: 'tr-1', revision: 1, filename: '3.4.pdf', sha256: 'abc', size_bytes: 100, uploaded_by: 'teacher', created_at: '2026-08-01T00:00:00Z' }] }], page: 1, page_size: 20, total: 1 });
      return emptyApiData();
    });
    render(<App />);
    const teacherTable = await screen.findByRole('table', { name: '资料版本' });
    expect(within(teacherTable).getAllByRole('columnheader')).toHaveLength(4);
    expect(within(teacherTable).getAllByRole('row')).toHaveLength(2);
    expect(within(teacherTable).getAllByRole('cell').length).toBeGreaterThan(0);
  });

  it('component exports the teacher gradebook as a CSV download', async () => {
    window.history.pushState({}, '', '/teacher/gradebook');
    const blobs = new Map<string, Blob>();
    let counter = 0;
    const created: Array<{ url: string; download: string }> = [];
    const MockURL = class extends URL {
      static createObjectURL(blob: Blob): string {
        const url = `blob:gradebook-mock-${++counter}`;
        blobs.set(url, blob);
        return url;
      }
      static revokeObjectURL(): void {}
    };
    vi.stubGlobal('URL', MockURL);
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
      created.push({ url: this.href, download: this.download });
    });
    try {
      vi.mocked(fetch).mockImplementation(async (input) => {
        const url = String(input);
        if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
        if (url.includes('/api/teacher/gradebook')) return apiOk({
          assignments: [{ id: 'gb-1', title: '第 3 章练习', status: 'published', submittedCount: 5, gradedCount: 3, completionRate: 60, averageScore: 72, averageRatio: 72, questionCount: 8 }],
          students: [{ userUid: 'stu-1', submissionCount: 2, completedAssignments: 1, averageRatio: 80, needsReview: false, riskLevel: 'normal' }],
          knowledge_points: [{ id: 'kp-1', name: '并网控制', score: 3, max_score: 4, attempts: 1, ratio: 75, status: 'learning' }],
          risk_students: [],
        });
        return emptyApiData();
      });

      render(<App />);
      await screen.findByRole('heading', { name: '成绩册与学情' });
      fireEvent.click(await screen.findByRole('button', { name: '导出 CSV' }));

      expect(created).toHaveLength(1);
      expect(created[0]!.download).toMatch(/^成绩册-\d{4}-\d{2}-\d{2}\.csv$/);
      const blob = blobs.get(created[0]!.url);
      expect(blob).toBeDefined();
      const text = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = () => reject(reader.error);
        reader.readAsText(blob!);
      });
      expect(text.replace(/^\uFEFF/, '').startsWith('作业成绩汇总')).toBe(true);
      expect(text).toContain('作业,题数,状态,已提交,已批改,完成率,平均成绩,平均正确率');
      expect(text).toContain('第 3 章练习,8,published,5,3,60%,72,72%');
      expect(text).toContain('学生汇总');
      expect(text).toContain('stu-1,2,1,80%,否');
      expect(text).toContain('知识点掌握');
      expect(text).toContain('并网控制,learning,75%');
    } finally {
      clickSpy.mockRestore();
      vi.unstubAllGlobals();
    }
  });

  it('component discussion list paginates and resets on query change', async () => {
    window.history.pushState({}, '', '/discussions');
    const topics = Array.from({ length: 12 }, (_, index) => ({ id: `topic-${index + 1}`, title: `分页讨论 ${index + 1}`, body: '讨论内容', status: 'open', pinned: false, author_label: '学生', reply_count: 0, created_at: '2026-08-01' }));
    const requestedPages: string[] = [];
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/discussions?')) {
        const params = new URL(url, 'http://localhost').searchParams;
        const page = Number(params.get('page') || 1);
        const pageSize = Number(params.get('page_size') || 8);
        const query = params.get('query') || '';
        requestedPages.push(params.toString());
        const visible = topics.filter((item) => !query || item.title.includes(query));
        const start = (page - 1) * pageSize;
        return apiOk({ items: visible.slice(start, start + pageSize), page, page_size: pageSize, total: visible.length });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByText('第 1 / 2 页，共 12 条')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /分页讨论/ })).toHaveLength(8);
    expect(screen.getByRole('button', { name: '讨论上一页' })).toBeDisabled();

    fireEvent.click(screen.getByRole('button', { name: '讨论下一页' }));
    await waitFor(() => expect(screen.getByText('第 2 / 2 页，共 12 条')).toBeInTheDocument());
    expect(screen.getAllByRole('button', { name: /分页讨论/ })).toHaveLength(4);
    expect(requestedPages.some((value) => value.includes('page=2'))).toBe(true);

    fireEvent.click(screen.getByRole('button', { name: '讨论上一页' }));
    await waitFor(() => expect(screen.getByText('第 1 / 2 页，共 12 条')).toBeInTheDocument());
    expect(screen.getAllByRole('button', { name: /分页讨论/ })).toHaveLength(8);

    fireEvent.change(screen.getByRole('textbox', { name: '搜索讨论' }), { target: { value: '分页讨论 12' } });
    await waitFor(() => expect(screen.getByText('1 个主题')).toBeInTheDocument());
    expect(screen.getAllByRole('button', { name: /分页讨论/ })).toHaveLength(1);
    expect(screen.queryByText(/第 1 \/ 1 页/)).not.toBeInTheDocument();
  });

  it('preview global search keeps course results in the current course scope', async () => {
    const otherCourse = {
      id: 2,
      name: '其他课程',
      teacher: '其他教师',
      className: '其他班级',
      status: 'active' as const,
      progress: 0,
      chapterCount: 0,
      resourceCount: 0,
      lastAccessedAt: null,
    };
    previewData.courses.push(otherCourse);
    window.history.pushState({}, '', '/search?q=其他课程');
    try {
      render(<App />);
      expect(await screen.findByRole('heading', { name: '搜索“其他课程”' })).toBeInTheDocument();
      expect(await screen.findByText('没有找到匹配内容，请尝试其他关键词或结果类型。')).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /其他课程/ })).not.toBeInTheDocument();
    } finally {
      previewData.courses.pop();
    }
  });

  it('component renders the server global search and uses a student canonical target', async () => {
    window.history.pushState({}, '', '/search?q=Unified');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/search')) return apiOk({
        course_id: 1,
        query: 'Unified',
        kind: 'all',
        items: [
          { kind: 'course', id: '1', title: 'Unified Course', summary: '课程教师 · 测试班', chapter_id: null },
          { kind: 'chapter', id: '7', title: 'Unified Chapter', summary: '课程章节', chapter_id: 7 },
          { kind: 'resource', id: 'res-unified', title: 'Unified Resource', summary: 'resource.pdf', chapter_id: 7 },
          { kind: 'assignment', id: 'assignment-unified', title: 'Unified Assignment', summary: '课程作业', chapter_id: null },
          { kind: 'exam', id: 'exam-unified', title: 'Unified Exam', summary: '课程考试', chapter_id: null },
          { kind: 'discussion', id: 'topic-unified', title: 'Unified Discussion', summary: '课程讨论', chapter_id: null },
          { kind: 'knowledge', id: 'kp-unified', title: 'Unified Knowledge', summary: '知识点', chapter_id: 7 },
        ],
        counts: { course: 1, chapter: 1, resource: 1, assignment: 1, exam: 1, discussion: 1, knowledge: 1 },
        page: 1,
        page_size: 10,
        total: 7,
      });
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('heading', { name: '搜索“Unified”' })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /Unified Assignment/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /全部/ })).toHaveTextContent('7');
    fireEvent.click(screen.getByRole('button', { name: /Unified Assignment/ }));
    await waitFor(() => expect(window.location.pathname).toBe('/courses/1/assignments/assignment-unified'));
  });

  it('component canonicalizes trimmed global-search parameters before loading results', async () => {
    window.history.pushState({}, '', '/search?q=%20Unified%20&kind=not-a-kind&page=not-a-page');
    render(<App />);

    await waitFor(() => {
      expect(window.location.pathname).toBe('/search');
      expect(window.location.search).toBe('?q=Unified');
    });
    expect(await screen.findByRole('heading', { name: '搜索“Unified”' })).toBeInTheDocument();
  });

  it('component redirects a global-search page beyond the server total to the last page', async () => {
    window.history.pushState({}, '', '/search?q=Unified&kind=resource&page=3');
    const searchRequests: string[] = [];
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/search')) {
        searchRequests.push(url);
        const requestUrl = new URL(url, window.location.origin);
        const page = Number(requestUrl.searchParams.get('page'));
        return apiOk({
          course_id: 1,
          query: 'Unified',
          kind: 'resource',
          items: page === 2 ? [{ kind: 'resource', id: 'resource-last-page', title: 'Last Resource', summary: '最后一页资料', chapter_id: 3 }] : [],
          counts: { course: 0, chapter: 0, resource: 11, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
          page,
          page_size: 10,
          total: 11,
        });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('button', { name: /Last Resource/ })).toBeInTheDocument();
    await waitFor(() => expect(window.location.search).toBe('?q=Unified&kind=resource&page=2'));
    expect(searchRequests.some((url) => new URL(url, window.location.origin).searchParams.get('page') === '3')).toBe(true);
    expect(searchRequests.some((url) => new URL(url, window.location.origin).searchParams.get('page') === '2')).toBe(true);
  });

  it('component ignores a slow global-search response after the URL query changes', async () => {
    window.history.pushState({}, '', '/search?q=first');
    let resolveFirst: ((response: Response) => void) | null = null;
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/search')) {
        const query = new URL(url, window.location.origin).searchParams.get('q');
        if (query === 'first') return new Promise<Response>((resolve) => { resolveFirst = resolve; });
        return apiOk({
          course_id: 1,
          query: 'second',
          kind: 'all',
          items: [{ kind: 'course', id: '1', title: 'Second Result', summary: '当前课程', chapter_id: null }],
          counts: { course: 1, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
          page: 1,
          page_size: 10,
          total: 1,
        });
      }
      return emptyApiData();
    });

    render(<App />);
    const input = await screen.findByRole('textbox', { name: '搜索课程内容' });
    fireEvent.change(input, { target: { value: 'second' } });
    fireEvent.click(screen.getByRole('button', { name: '搜索' }));
    expect(await screen.findByRole('button', { name: /Second Result/ })).toBeInTheDocument();
    await act(async () => {
      resolveFirst?.(apiOk({
        course_id: 1,
        query: 'first',
        kind: 'all',
        items: [{ kind: 'course', id: '1', title: 'Stale First Result', summary: '旧请求', chapter_id: null }],
        counts: { course: 1, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
        page: 1,
        page_size: 10,
        total: 1,
      }));
      await Promise.resolve();
    });
    expect(screen.queryByRole('button', { name: /Stale First Result/ })).not.toBeInTheDocument();
  });

  it('component sends staff lifecycle search results to staff canonical routes', async () => {
    window.history.pushState({}, '', '/search?q=Draft');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/search')) return apiOk({
        course_id: 1,
        query: 'Draft',
        kind: 'all',
        items: [{ kind: 'resource', id: 'res-draft', title: 'Draft Resource', summary: '教师草稿', chapter_id: 3 }],
        counts: { course: 0, chapter: 0, resource: 1, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
        page: 1,
        page_size: 10,
        total: 1,
      });
      return emptyApiData();
    });

    render(<App />);
    const result = await screen.findByRole('button', { name: /Draft Resource/ });
    fireEvent.click(result);
    await waitFor(() => expect(window.location.pathname).toBe('/teacher/courses/1/resources'));
  });

  it('component sends staff assignment search results to the canonical assignment detail route', async () => {
    window.history.pushState({}, '', '/search?q=Draft%20Assignment');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/search')) return apiOk({
        course_id: 1,
        query: 'Draft Assignment',
        kind: 'all',
        items: [{ kind: 'assignment', id: 'assignment-draft', title: 'Draft Assignment', summary: '教师草稿作业', chapter_id: null }],
        counts: { course: 0, chapter: 0, resource: 0, assignment: 1, exam: 0, discussion: 0, knowledge: 0 },
        page: 1,
        page_size: 10,
        total: 1,
      });
      return emptyApiData();
    });

    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: /Draft Assignment/ }));
    await waitFor(() => expect(window.location.pathname).toBe('/teacher/courses/1/assignments/assignment-draft'));
  });

  it('component rejects a search response from a different current course', async () => {
    window.history.pushState({}, '', '/search?q=Wrong%20Course');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.includes('/api/search')) return apiOk({
        course_id: 2,
        query: 'Wrong Course',
        kind: 'all',
        items: [{ kind: 'course', id: '2', title: 'Wrong Course', summary: '越界课程', chapter_id: null }],
        counts: { course: 1, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
        page: 1,
        page_size: 10,
        total: 1,
      });
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('alert')).toHaveTextContent('搜索结果不属于当前课程');
    expect(screen.queryByRole('button', { name: /Wrong Course/ })).not.toBeInTheDocument();
  });

  it('component message center filters unread notices and updates the global indicator', async () => {
    window.history.pushState({}, '', '/messages');
    render(<App />);

    expect(await screen.findByRole('heading', { name: '课程通知' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '消息通知，1 条未读' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('tab', { name: /未读/ }));
    const unreadNotice = await screen.findByRole('button', { name: '第 3 章案例练习已更新，标为已读' });
    fireEvent.click(unreadNotice);

    expect(await screen.findByText('当前没有未读通知。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '消息通知' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '全部已读' })).toBeDisabled();

    fireEvent.click(screen.getByRole('tab', { name: /全部/ }));
    expect(await screen.findByRole('button', { name: '第 3 章案例练习已更新，已读' })).toBeDisabled();
  });

  it('component message center consumes a task notification deep link without auto-reading it', async () => {
    window.history.pushState({}, '', '/messages?notice=notice-preview-1');
    render(<App />);

    expect(await screen.findByText('已定位到任务对应的课程通知。')).toBeInTheDocument();
    const focusedNotice = screen.getByRole('button', { name: '第 3 章案例练习已更新，标为已读' });
    expect(focusedNotice).toHaveAttribute('aria-current', 'true');
    expect(focusedNotice).toBeEnabled();
    expect(focusedNotice).toHaveClass('focused');
    expect(screen.getByRole('tab', { name: /全部/ })).toHaveAttribute('aria-selected', 'true');
  });

  it('component message center reports an inaccessible deep link without exposing its cause', async () => {
    window.history.pushState({}, '', '/messages?notice=notice-private-or-missing');
    render(<App />);

    expect(await screen.findByText('该通知不存在或当前账号不可查看。')).toBeInTheDocument();
    expect(document.querySelector('[aria-current="true"]')).toBeNull();
  });

  it('component message center can mark every preview notice read in one action', async () => {
    window.history.pushState({}, '', '/messages');
    render(<App />);

    fireEvent.click(await screen.findByRole('button', { name: '全部已读' }));
    expect(await screen.findByText('已将 1 条通知标为已读。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '全部已读' })).toBeDisabled();
    expect(screen.getByRole('button', { name: '消息通知' })).toBeInTheDocument();
  });

  it('component preserves unread state when the server rejects a read write', async () => {
    window.history.pushState({}, '', '/messages');
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      if (url.includes('/api/notifications/notice-1/read') && init?.method === 'PUT') {
        return { ok: false, status: 503, json: async () => ({ status: 'error', data: null, error: { code: 'notification_unavailable', message: '通知状态暂时无法保存' } }) } as Response;
      }
      if (url.includes('/api/notifications?')) {
        return {
          ok: true,
          status: 200,
          json: async () => ({ status: 'ok', data: { items: [{ id: 'notice-1', audience: 'course_students', title: '服务端通知', body: '测试失败恢复', created_at: '2026-07-28', is_read: false }], total: 1, page: 1, page_size: 8, unread_count: 1 } }),
        } as Response;
      }
      return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { items: [] } }) } as Response;
    });

    render(<App />);
    const notice = await screen.findByRole('button', { name: '服务端通知，标为已读' });
    fireEvent.click(notice);

    expect(await screen.findByText('通知状态暂时无法保存')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '服务端通知，标为已读' })).toBeEnabled();
    expect(screen.getByRole('button', { name: '消息通知，1 条未读' })).toBeInTheDocument();
  });

  it('component applies a knowledge graph URL query on first render', async () => {
    window.history.pushState({}, '', '/knowledge-graph?q=%E5%B9%B6%E7%BD%91%E6%8E%A7%E5%88%B6');
    render(<App />);
    expect(await screen.findByRole('heading', { name: '知识点与先修关系' })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: '搜索知识点' })).toHaveValue('并网控制');
    expect(await screen.findByText('1 个节点 · 0 条关系')).toBeInTheDocument();
  });

  it('component knowledge graph retry issues a fresh snapshot request', async () => {
    window.history.pushState({}, '', '/knowledge-graph');
    let graphAttempts = 0;
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      if (url.endsWith('/api/knowledge-graph/graph')) {
        graphAttempts += 1;
        if (graphAttempts === 1) {
          return { ok: false, status: 503, json: async () => ({ status: 'error', data: null, error: { code: 'graph_unavailable', message: '图谱暂时不可用' } }) } as Response;
        }
        return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { nodes: [{ id: 'kp-1', name: '基础知识点', chapter_id: 1, category: '概念' }], edges: [] } }) } as Response;
      }
      if (url.includes('/api/knowledge-graph/nodes/kp-1')) {
        return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { id: 'kp-1', name: '基础知识点', chapter_id: 1, category: '概念', neighbors: [] } }) } as Response;
      }
      return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { items: [], nodes: [], unread_count: 0 } }) } as Response;
    });

    render(<App />);
    expect(await screen.findByText('图谱暂时不可用')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '重新加载' }));
    expect(await screen.findByText('1 个节点 · 0 条关系')).toBeInTheDocument();
    expect(graphAttempts).toBe(2);
  });

  it('component exposes a timed exam preview and an explicit preview boundary', async () => {
    window.history.pushState({}, '', '/exams');
    render(<App />);
    expect(await screen.findByRole('heading', { name: '限时考试' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '进入考试' }));
    expect(await screen.findByRole('heading', { name: '第 3 章储能系统限时考试' })).toBeInTheDocument();
    expect(screen.getByText('当前为预览模式，提交不会写入课程平台。')).toBeInTheDocument();
    expect(screen.getByText(/考试状态/)).toBeInTheDocument();
  });

  it('authenticated empty data does not render preview metrics or sample notices', async () => {
    window.history.pushState({}, '', '/');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      return { ok: true, json: async () => ({ status: 'ok', data: { items: [], unread_count: 0 } }) } as Response;
    });
    render(<App />);
    expect(await screen.findByRole('heading', { name: '早上好，林同学' })).toBeInTheDocument();
    expect(screen.queryByText('第 3 章案例练习已更新')).not.toBeInTheDocument();
    expect(screen.getByText('已评分平均')).toBeInTheDocument();
    expect(screen.getByText('已学习 待同步')).toBeInTheDocument();
  });

  it('component shows closed activity results without allowing another student response', async () => {
    window.history.pushState({}, '', '/activities/activity-closed');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      if (url.includes('/api/activities/activity-closed/results')) {
        return {
          ok: true,
          json: async () => ({
            status: 'ok',
            data: {
              activity_id: 'activity-closed',
              kind: 'poll',
              total_responses: 1,
              has_responded: false,
              results_available: true,
              options: [
                { id: 'option-1', label: '功率平衡', count: 1, ratio: 100 },
                { id: 'option-2', label: '通信协调', count: 0, ratio: 0 },
              ],
            },
          }),
        } as Response;
      }
      if (url.includes('/api/activities/activity-closed')) {
        return {
          ok: true,
          json: async () => ({
            status: 'ok',
            data: {
              id: 'activity-closed',
              kind: 'poll',
              title: '储能系统并网控制重点',
              body: '选择本节课最重要的控制目标。',
              options: [
                { id: 'option-1', label: '功率平衡' },
                { id: 'option-2', label: '通信协调' },
              ],
              status: 'closed',
              max_attempts: 1,
              has_responded: false,
              attempts_used: 0,
              can_respond: false,
              next_attempt: null,
              my_response: null,
            },
          }),
        } as Response;
      }
      return { ok: true, json: async () => ({ status: 'ok', data: { items: [], unread_count: 0 } }) } as Response;
    });

    render(<App />);

    expect(await screen.findByRole('button', { name: '活动已结束' })).toBeDisabled();
    expect(screen.getByText('1 人参与')).toBeInTheDocument();
  });

  it('student confirms a check-in without option controls and keeps the server result', async () => {
    window.history.pushState({}, '', '/activities/checkin-1');
    let responded = false;
    const submittedBodies: Array<Record<string, unknown>> = [];
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      if (url.includes('/api/activities/checkin-1/responses') && init?.method === 'POST') {
        submittedBodies.push(JSON.parse(String(init.body)) as Record<string, unknown>);
        responded = true;
        return { ok: true, status: 201, json: async () => ({ status: 'ok', data: { id: 'checkin-response-1', activity_id: 'checkin-1', attempt: 1, answers: ['present'], submitted_at: '2026-07-29T08:00:00Z' } }) } as Response;
      }
      if (url.includes('/api/activities/checkin-1/results')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { activity_id: 'checkin-1', kind: 'checkin', total_responses: responded ? 1 : 0, has_responded: responded, results_available: responded, options: [], participants: [] } }) } as Response;
      }
      if (url.includes('/api/activities/checkin-1')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { id: 'checkin-1', kind: 'checkin', title: '第 3 章课堂签到', body: '请在课堂内完成签到。', options: [], status: 'published', max_attempts: 1, has_responded: responded, attempts_used: responded ? 1 : 0, can_respond: !responded, next_attempt: responded ? null : 1, my_response: responded ? { id: 'checkin-response-1', activity_id: 'checkin-1', attempt: 1, answers: ['present'], submitted_at: '2026-07-29T08:00:00Z' } : null } }) } as Response;
      }
      return { ok: true, status: 200, json: async () => ({ status: 'ok', data: { items: [], unread_count: 0 } }) } as Response;
    });

    render(<App />);
    const submit = await screen.findByRole('button', { name: '确认签到' });
    expect(screen.queryByRole('radio')).not.toBeInTheDocument();
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument();
    fireEvent.click(submit);
    await waitFor(() => expect(submittedBodies).toEqual([{ answers: ['present'], attempt: 1 }]));
    expect(await screen.findByText('签到成功，服务端已记录本次签到。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '已签到' })).toBeDisabled();
    expect(screen.getByText('1 人已签到')).toBeInTheDocument();
  });

  it('teacher creates a quick response without sending the internal claim sentinel', async () => {
    window.history.pushState({}, '', '/teacher/activities');
    const createBodies: Array<Record<string, unknown>> = [];
    let created = false;
    const activity = quickResponseActivity('quick-created', 'open');
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/teacher/activities') && init?.method === 'POST') {
        createBodies.push(JSON.parse(String(init.body)) as Record<string, unknown>);
        created = true;
        return apiOk(activity, 201);
      }
      if (url.endsWith('/api/activities')) {
        return apiOk({ items: created ? [activity] : [] });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('heading', { name: '课堂活动管理' })).toBeInTheDocument();
    fireEvent.change(screen.getByRole('combobox', { name: '活动类型' }), { target: { value: 'quick_response' } });
    fireEvent.change(screen.getByRole('combobox', { name: '活动保存状态' }), { target: { value: 'published' } });
    fireEvent.change(screen.getByRole('textbox', { name: '活动标题' }), { target: { value: '课堂抢答测试' } });
    fireEvent.change(screen.getByRole('textbox', { name: '活动说明' }), { target: { value: '请在教师发出口令后抢答。' } });
    expect(screen.queryByRole('textbox', { name: '活动选项' })).not.toBeInTheDocument();
    expect(screen.getByRole('spinbutton', { name: '活动允许次数' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: '发布课堂活动' }));

    expect(await screen.findByText('课堂活动已发布，学生可以在开放活动中看到。')).toBeInTheDocument();
    expect(createBodies).toHaveLength(1);
    expect(createBodies[0]).toMatchObject({ kind: 'quick_response', options: [], status: 'published', max_attempts: 1 });
    expect(JSON.stringify(createBodies[0])).not.toContain('claim');
  });

  it('quick-response winner submits the fixed claim and stays won after refresh', async () => {
    window.history.pushState({}, '', '/activities/quick-win');
    let serverView: QuickResponseView = 'open';
    const submissions: RequestInit[] = [];
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/activities/quick-win/responses') && init?.method === 'POST') {
        submissions.push(init);
        serverView = 'won';
        return apiOk({ id: 'quick-win-response', activity_id: 'quick-win', attempt: 1, answers: ['claim'], submitted_at: '2026-07-29T08:00:00Z' }, 201);
      }
      if (url.endsWith('/api/activities/quick-win/results')) {
        return apiOk(quickResponseResults('quick-win', serverView));
      }
      if (url.endsWith('/api/activities/quick-win')) {
        return apiOk(quickResponseActivity('quick-win', serverView));
      }
      return emptyApiData();
    });

    const firstMount = render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '立即抢答' }));
    expect(await screen.findByText('抢答成功，你是本次首位响应者。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '已抢到' })).toBeDisabled();
    expect(screen.getByText('你是首位响应者')).toBeInTheDocument();
    expect(submissions).toHaveLength(1);
    expect(JSON.parse(String(submissions[0].body))).toEqual({ answers: ['claim'], attempt: 1 });
    const headers = new Headers(submissions[0].headers);
    expect(headers.get('X-Moodle-Sesskey')).toBe('csrf-fixture');
    expect(headers.get('Idempotency-Key')).toBe('activity-response:quick-win:1');

    firstMount.unmount();
    window.history.replaceState({}, '', '/activities/quick-win');
    render(<App />);
    expect(await screen.findByRole('button', { name: '已抢到' })).toBeDisabled();
    expect(screen.getByText('你是首位响应者')).toBeInTheDocument();
    expect(submissions).toHaveLength(1);
  });

  it('quick-response loser becomes terminal on 409 without exposing user_ref', async () => {
    window.history.pushState({}, '', '/activities/quick-lost');
    let claimRejected = false;
    let resolveDetailRefresh: ((response: Response) => void) | null = null;
    let resolveResultsRefresh: ((response: Response) => void) | null = null;
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/activities/quick-lost/responses') && init?.method === 'POST') {
        claimRejected = true;
        return apiFailure(409, 'quick_response_already_claimed', '已有同学抢答成功，本次抢答已结束。');
      }
      if (url.endsWith('/api/activities/quick-lost/results')) {
        if (claimRejected) return new Promise<Response>((resolve) => { resolveResultsRefresh = resolve; });
        return apiOk(quickResponseResults('quick-lost', 'open'));
      }
      if (url.endsWith('/api/activities/quick-lost')) {
        if (claimRejected) return new Promise<Response>((resolve) => { resolveDetailRefresh = resolve; });
        return apiOk(quickResponseActivity('quick-lost', 'open'));
      }
      return emptyApiData();
    });

    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '立即抢答' }));

    expect(await screen.findByText('抢答已结束')).toBeInTheDocument();
    expect(screen.getByText('已结束')).toBeInTheDocument();
    expect(resolveDetailRefresh).not.toBeNull();
    expect(resolveResultsRefresh).not.toBeNull();
    await act(async () => {
      resolveDetailRefresh?.(apiOk(quickResponseActivity('quick-lost', 'lost')));
      resolveResultsRefresh?.(apiOk(quickResponseResults('quick-lost', 'lost', [{ user_ref: 'u_private_winner', submitted_at: '2026-07-29T08:00:00Z' }])));
    });

    expect(await screen.findByText('已有同学抢答成功，本次抢答已结束。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '抢答已结束' })).toBeDisabled();
    expect(screen.getByText('胜出者身份仅教师可见')).toBeInTheDocument();
    expect(document.body.textContent).not.toContain('u_private_winner');
    expect(document.body.textContent).not.toContain('user_ref');
  });

  it('keeps a confirmed quick-response win when the follow-up GET fails', async () => {
    window.history.pushState({}, '', '/activities/quick-sync-fails');
    let submitted = false;
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/activities/quick-sync-fails/responses') && init?.method === 'POST') {
        submitted = true;
        return apiOk({ id: 'quick-sync-response', activity_id: 'quick-sync-fails', attempt: 1, answers: ['claim'], submitted_at: '2026-07-29T08:00:00Z' }, 201);
      }
      if (url.endsWith('/api/activities/quick-sync-fails/results')) {
        return submitted ? apiFailure(503, 'activity_unavailable', '结果同步暂时不可用') : apiOk(quickResponseResults('quick-sync-fails', 'open'));
      }
      if (url.endsWith('/api/activities/quick-sync-fails')) {
        return submitted ? apiFailure(503, 'activity_unavailable', '活动同步暂时不可用') : apiOk(quickResponseActivity('quick-sync-fails', 'open'));
      }
      return emptyApiData();
    });

    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '立即抢答' }));

    expect(await screen.findByText('抢答成功，服务端已确认；当前状态同步暂时不可用。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '已抢到' })).toBeDisabled();
    expect(screen.getByText('你是首位响应者')).toBeInTheDocument();
  });

  it('moves an ambiguous quick-response network result into the uncertain state', async () => {
    window.history.pushState({}, '', '/activities/quick-uncertain');
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/activities/quick-uncertain/responses') && init?.method === 'POST') {
        throw new TypeError('network outcome unknown');
      }
      if (url.endsWith('/api/activities/quick-uncertain/results')) {
        return apiOk(quickResponseResults('quick-uncertain', 'open'));
      }
      if (url.endsWith('/api/activities/quick-uncertain')) {
        return apiOk(quickResponseActivity('quick-uncertain', 'open'));
      }
      return emptyApiData();
    });

    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '立即抢答' }));

    expect(await screen.findByText('抢答请求结果待确认，请先确认服务端状态。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '确认抢答结果' })).toBeEnabled();
    expect(screen.getByRole('button', { name: '结果待确认' })).toBeDisabled();
  });

  it.each([
    { target: 'won' as const, expectedMessage: '服务端已确认你是本次首位响应者。', expectedButton: '已抢到' },
    { target: 'lost' as const, expectedMessage: '已有同学抢答成功，本次抢答已结束。', expectedButton: '抢答已结束' },
    { target: 'open' as const, expectedMessage: '当前尚未产生抢答结果。', expectedButton: '立即抢答' },
  ])('confirmation recovers an uncertain quick response to $target', async ({ target, expectedMessage, expectedButton }) => {
    const activityId = `quick-confirm-${target}`;
    window.history.pushState({}, '', `/activities/${activityId}`);
    let detailReads = 0;
    let postAttempts = 0;
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith(`/api/activities/${activityId}/responses`) && init?.method === 'POST') {
        postAttempts += 1;
        throw new TypeError('network outcome unknown');
      }
      if (url.endsWith(`/api/activities/${activityId}/results`)) {
        const view = detailReads >= 3 ? target : 'open';
        return apiOk(quickResponseResults(activityId, view, view === 'lost' ? [{ user_ref: 'u_hidden_winner', submitted_at: '2026-07-29T08:00:00Z' }] : []));
      }
      if (url.endsWith(`/api/activities/${activityId}`)) {
        detailReads += 1;
        return apiOk(quickResponseActivity(activityId, detailReads >= 3 ? target : 'open'));
      }
      return emptyApiData();
    });

    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '立即抢答' }));
    fireEvent.click(await screen.findByRole('button', { name: '确认抢答结果' }));

    expect(await screen.findByText(expectedMessage)).toBeInTheDocument();
    const resultButton = screen.getByRole('button', { name: expectedButton });
    if (target === 'open') expect(resultButton).toBeEnabled();
    else expect(resultButton).toBeDisabled();
    expect(screen.queryByRole('button', { name: '确认抢答结果' })).not.toBeInTheDocument();
    expect(postAttempts).toBe(1);
    expect(document.body.textContent).not.toContain('u_hidden_winner');
  });

  it('sends only one quick-response POST when the claim button is clicked twice', async () => {
    window.history.pushState({}, '', '/activities/quick-double-click');
    let serverView: QuickResponseView = 'open';
    let postAttempts = 0;
    let resolvePost: ((response: Response) => void) | null = null;
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/activities/quick-double-click/responses') && init?.method === 'POST') {
        postAttempts += 1;
        return new Promise<Response>((resolve) => { resolvePost = resolve; });
      }
      if (url.endsWith('/api/activities/quick-double-click/results')) {
        return apiOk(quickResponseResults('quick-double-click', serverView));
      }
      if (url.endsWith('/api/activities/quick-double-click')) {
        return apiOk(quickResponseActivity('quick-double-click', serverView));
      }
      return emptyApiData();
    });

    render(<App />);
    const claimButton = await screen.findByRole('button', { name: '立即抢答' });
    fireEvent.click(claimButton);
    fireEvent.click(claimButton);
    expect(postAttempts).toBe(1);
    expect(resolvePost).not.toBeNull();

    await act(async () => {
      serverView = 'won';
      resolvePost?.(apiOk({ id: 'quick-double-response', activity_id: 'quick-double-click', attempt: 1, answers: ['claim'], submitted_at: '2026-07-29T08:00:00Z' }, 201));
    });
    expect(await screen.findByText('抢答成功，你是本次首位响应者。')).toBeInTheDocument();
    expect(postAttempts).toBe(1);
  });

  it('does not offer reopen for a teacher quick response that already has a winner', async () => {
    window.history.pushState({}, '', '/teacher/activities');
    const wonActivity = { ...quickResponseActivity('quick-teacher-won', 'won'), title: '课堂首位响应' };
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      }
      if (url.endsWith('/api/activities')) {
        return apiOk({ items: [wonActivity] });
      }
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByText('课堂首位响应')).toBeInTheDocument();
    expect(screen.getByText('首位响应已确认')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '重新开放' })).not.toBeInTheDocument();
  });

  it('teacher randomly selects one roster member with one protected POST', async () => {
    window.history.pushState({}, '', '/activities/random-ui');
    let selected = false;
    const writes: RequestInit[] = [];
    const activity = {
      id: 'random-ui', kind: 'random_selection', title: '课堂随机选人', body: '从当前班级抽取一名学生。', options: [], status: 'published',
      max_attempts: 1, has_responded: false, attempts_used: 0, can_respond: false, can_reopen: false, next_attempt: null, my_response: null,
    };
    const randomState = () => selected
      ? { activity_id: 'random-ui', round: 1, latest: { round: 1, cycle: 1, sequence: 1, user_ref: 'u_private_student_1', display_name: '学生一', selected_at: '2026-07-29T09:00:00Z' }, history: [{ round: 1, cycle: 1, sequence: 1, user_ref: 'u_private_student_1', display_name: '学生一', selected_at: '2026-07-29T09:00:00Z' }], remaining_count: null, can_select: true }
      : { activity_id: 'random-ui', round: 0, latest: null, history: [], remaining_count: null, can_select: true };
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.endsWith('/api/teacher/classroom-roster')) return apiOk({ configured: true, items: [{ user_ref: 'u_private_student_1', display_name: '学生一' }, { user_ref: 'u_private_student_2', display_name: '学生二' }] });
      if (url.endsWith('/api/teacher/activities/random-ui/random-select') && init?.method === 'POST') {
        writes.push(init); selected = true; return apiOk(randomState(), 201);
      }
      if (url.endsWith('/api/activities/random-ui/random-selection')) return apiOk(randomState());
      if (url.endsWith('/api/activities/random-ui')) return apiOk(activity);
      return emptyApiData();
    });

    render(<App />);
    const selectButton = await screen.findByRole('button', { name: '抽取一名学生' });
    expect(screen.getByText('2 名学生可参与')).toBeInTheDocument();
    fireEvent.click(selectButton);
    fireEvent.click(selectButton);

    expect(await screen.findByText('第 1 轮抽取已确认：学生一')).toBeInTheDocument();
    expect(screen.getAllByText('学生一').length).toBeGreaterThan(0);
    expect(writes).toHaveLength(1);
    expect(JSON.parse(String(writes[0].body))).toEqual({});
    const headers = new Headers(writes[0].headers);
    expect(headers.get('X-Moodle-Sesskey')).toBe('csrf-fixture');
    expect(headers.get('Idempotency-Key')).toMatch(/^activity-random-select:random-ui:/);
    expect(document.body.textContent).not.toContain('u_private_student_1');
  });

  it('student sees only their assigned group and teammate display names', async () => {
    window.history.pushState({}, '', '/activities/group-student-ui');
    const activity = {
      id: 'group-student-ui', kind: 'group_task', title: '课堂分组任务', body: '查看本次课堂分工。', options: [], status: 'published',
      max_attempts: 1, has_responded: false, attempts_used: 0, can_respond: false, can_reopen: false, next_attempt: null, my_response: null,
    };
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'student', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.endsWith('/api/activities/group-student-ui/groups')) return apiOk({
        activity_id: 'group-student-ui', revision: 2, my_group: { id: 'alpha', name: '甲组', members: [{ display_name: '学生一', is_me: true }, { display_name: '学生二', is_me: false }] }, can_generate: false,
      });
      if (url.endsWith('/api/activities/group-student-ui')) return apiOk(activity);
      return emptyApiData();
    });

    render(<App />);
    expect(await screen.findByRole('heading', { name: '课堂分组任务' })).toBeInTheDocument();
    expect(screen.getByText('甲组')).toBeInTheDocument();
    expect(screen.getByText('学生一')).toBeInTheDocument();
    expect(screen.getByText('学生二')).toBeInTheDocument();
    expect(screen.getByText('本人')).toBeInTheDocument();
    expect(screen.queryByText('乙组')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /生成分组|重新分组/ })).not.toBeInTheDocument();
    expect(document.body.textContent).not.toContain('user_ref');
    expect(document.body.textContent).not.toContain('u_private');
  });

  it('teacher generates a balanced group revision with protected headers', async () => {
    window.history.pushState({}, '', '/activities/group-teacher-ui');
    let generated = false;
    const writes: RequestInit[] = [];
    const activity = {
      id: 'group-teacher-ui', kind: 'group_task', title: '课堂分组任务', body: '生成本次课堂小组。', options: [{ id: 'alpha', label: '甲组' }, { id: 'beta', label: '乙组' }], status: 'published',
      max_attempts: 1, has_responded: false, attempts_used: 0, can_respond: false, can_reopen: false, next_attempt: null, my_response: null,
    };
    const groupsState = () => generated
      ? { activity_id: 'group-teacher-ui', revision: 1, groups: [{ id: 'alpha', name: '甲组', members: [{ user_ref: 'u_1', display_name: '学生一' }, { user_ref: 'u_3', display_name: '学生三' }] }, { id: 'beta', name: '乙组', members: [{ user_ref: 'u_2', display_name: '学生二' }] }], can_generate: true }
      : { activity_id: 'group-teacher-ui', revision: null, groups: [], can_generate: true };
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) return apiOk({ role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} });
      if (url.endsWith('/api/teacher/classroom-roster')) return apiOk({ configured: true, items: [{ user_ref: 'u_1', display_name: '学生一' }, { user_ref: 'u_2', display_name: '学生二' }, { user_ref: 'u_3', display_name: '学生三' }] });
      if (url.endsWith('/api/teacher/activities/group-teacher-ui/groups/generate') && init?.method === 'POST') {
        writes.push(init); generated = true; return apiOk(groupsState(), 201);
      }
      if (url.endsWith('/api/activities/group-teacher-ui/groups')) return apiOk(groupsState());
      if (url.endsWith('/api/activities/group-teacher-ui')) return apiOk(activity);
      return emptyApiData();
    });

    render(<App />);
    const generateButton = await screen.findByRole('button', { name: '生成分组' });
    expect(screen.getByText('3 名学生可参与')).toBeInTheDocument();
    fireEvent.click(generateButton);
    fireEvent.click(generateButton);

    expect(await screen.findByText('第 1 版分组已确认。')).toBeInTheDocument();
    expect(screen.getByText('Revision 1')).toBeInTheDocument();
    expect(screen.getAllByText('甲组').length).toBeGreaterThan(0);
    expect(screen.getAllByText('乙组').length).toBeGreaterThan(0);
    expect(writes).toHaveLength(1);
    const headers = new Headers(writes[0].headers);
    expect(headers.get('X-Moodle-Sesskey')).toBe('csrf-fixture');
    expect(headers.get('Idempotency-Key')).toMatch(/^activity-groups-generate:group-teacher-ui:/);
  });

  it('teacher activity transition keys stay unique across component remounts', async () => {
    window.history.pushState({}, '', '/teacher/activities');
    const transitionKeys: string[] = [];
    const activity = {
      id: 'activity-remount',
      kind: 'poll',
      title: '跨页面活动状态测试',
      body: '验证重新进入页面后的幂等键。',
      options: [{ id: 'option-1', label: '功率平衡' }, { id: 'option-2', label: '通信协调' }],
      status: 'published',
      max_attempts: 1,
      has_responded: false,
      attempts_used: 0,
      can_respond: false,
      next_attempt: null,
      my_response: null,
    };
    vi.mocked(fetch).mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      if (url.includes('/api/teacher/activities/activity-remount/close')) {
        transitionKeys.push(String(new Headers(init?.headers).get('Idempotency-Key')));
        return { ok: true, json: async () => ({ status: 'ok', data: { ...activity, status: 'closed' } }) } as Response;
      }
      if (url.endsWith('/api/activities')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { items: [activity] } }) } as Response;
      }
      return { ok: true, json: async () => ({ status: 'ok', data: { items: [] } }) } as Response;
    });

    const firstMount = render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '关闭' }));
    await waitFor(() => expect(transitionKeys).toHaveLength(1));
    firstMount.unmount();

    window.history.pushState({}, '', '/teacher/activities');
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '关闭' }));
    await waitFor(() => expect(transitionKeys).toHaveLength(2));
    expect(transitionKeys[0]).not.toBe(transitionKeys[1]);
  });

  it('component exposes teacher exam management from a real teacher session', async () => {
    window.history.pushState({}, '', '/teacher/exams');
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes('/api/course/session/open')) {
        return { ok: true, json: async () => ({ status: 'ok', data: { role: 'teacher', course_id: 1, csrf_token: 'csrf-fixture', features: {} } }) } as Response;
      }
      return { ok: true, json: async () => ({ status: 'ok', data: { items: [] } }) } as Response;
    });
    render(<App />);
    expect(await screen.findByRole('heading', { name: '考试管理' })).toBeInTheDocument();
    expect(await screen.findByText('当前没有考试。')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '保存考试草稿' })).toBeDisabled();
    expect(screen.queryByText('当前为预览模式')).not.toBeInTheDocument();
  });
});

describe('keyboard accessibility', () => {
  beforeEach(() => {
    useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('preview test')));
    window.history.pushState({}, '', '/');
  });

  it('provides a skip link that targets main content', async () => {
    await act(async () => { render(<App />); });
    const link = await screen.findByRole('link', { name: '跳到主内容' });
    expect(link).toHaveAttribute('href', '#main-content');
    expect(screen.getByRole('main')).toHaveAttribute('id', 'main-content');
    expect(screen.getByRole('main')).toHaveAttribute('tabindex', '-1');
  });

  it('closes the user menu with Escape and returns focus to its trigger', async () => {
    await act(async () => { render(<App />); });
    const trigger = await screen.findByRole('button', { name: '打开用户菜单' });
    fireEvent.click(trigger);
    expect(screen.getByRole('menu')).toBeInTheDocument();
    fireEvent.keyDown(trigger, { key: 'Escape' });
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it('focuses the global search with "/" and clears it with Escape', async () => {
    await act(async () => { render(<App />); });
    const search = (await screen.findByLabelText('搜索课程资料')) as HTMLInputElement;
    fireEvent.keyDown(window, { key: '/' });
    expect(search).toHaveFocus();
    fireEvent.change(search, { target: { value: '储能' } });
    expect(search.value).toBe('储能');
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(search).not.toHaveFocus();
    expect(search.value).toBe('');
  });
});

describe('route titles and navigation focus', () => {
  beforeEach(() => {
    useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('preview test')));
    window.history.pushState({}, '', '/');
  });

  it('updates the document title when navigating between routes', async () => {
    await act(async () => { render(<App />); });
    await waitFor(() => expect(document.title).toBe('学习工作台 · 储能学习空间'));
    fireEvent.click(await screen.findByRole('link', { name: '我的课程' }));
    await waitFor(() => expect(document.title).toBe('我的课程 · 储能学习空间'));
    fireEvent.click(await screen.findByRole('link', { name: '待办任务' }));
    await waitFor(() => expect(document.title).toBe('待办任务 · 储能学习空间'));
  });

  it('redirects unknown routes to the landing page and titles it', async () => {
    window.history.pushState({}, '', '/not-a-route');
    await act(async () => { render(<App />); });
    await waitFor(() => expect(window.location.pathname).toBe('/'));
    await waitFor(() => expect(document.title).toBe('学习工作台 · 储能学习空间'));
  });

  it('moves focus to main content after a route change', async () => {
    await act(async () => { render(<App />); });
    const main = screen.getByRole('main');
    fireEvent.click(await screen.findByRole('link', { name: '我的课程' }));
    await waitFor(() => expect(document.activeElement).toBe(main));
  });

  it('does not move focus for a same-path navigation', async () => {
    await act(async () => { render(<App />); });
    const search = (await screen.findByLabelText('搜索课程资料')) as HTMLInputElement;
    fireEvent.keyDown(window, { key: '/' });
    expect(search).toHaveFocus();
    fireEvent.change(search, { target: { value: '储能' } });
    fireEvent.submit(search.closest('form') as HTMLFormElement);
    await waitFor(() => expect(window.location.pathname).toBe('/search'));
    const main = screen.getByRole('main');
    await waitFor(() => expect(document.activeElement).toBe(main));
    fireEvent.keyDown(window, { key: '/' });
    expect(search).toHaveFocus();
    fireEvent.submit(search.closest('form') as HTMLFormElement);
    expect(document.activeElement).toBe(search);
  });
});

describe('mobile sidebar drawer focus management', () => {
  beforeEach(() => {
    useAppStore.setState({ session: null, sessionExpired: false, data: null, preview: false, sidebarOpen: false });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('preview test')));
    window.history.pushState({}, '', '/');
  });

  it('moves focus into the sidebar when it opens', async () => {
    await act(async () => { render(<App />); });
    const trigger = await screen.findByRole('button', { name: '打开导航' });
    fireEvent.click(trigger);
    expect(screen.getByRole('button', { name: '关闭导航' })).toHaveFocus();
  });

  it('closes the sidebar with Escape and returns focus to the trigger', async () => {
    await act(async () => { render(<App />); });
    const trigger = await screen.findByRole('button', { name: '打开导航' });
    fireEvent.click(trigger);
    expect(screen.getByRole('button', { name: '关闭导航' })).toHaveFocus();
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(screen.queryByRole('button', { name: '关闭导航遮罩' })).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it('returns focus to the trigger when the close button is used', async () => {
    await act(async () => { render(<App />); });
    const trigger = await screen.findByRole('button', { name: '打开导航' });
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('button', { name: '关闭导航' }));
    expect(trigger).toHaveFocus();
  });

  it('returns focus to the trigger when the overlay is used', async () => {
    await act(async () => { render(<App />); });
    const trigger = await screen.findByRole('button', { name: '打开导航' });
    fireEvent.click(trigger);
    fireEvent.click(screen.getByRole('button', { name: '关闭导航遮罩' }));
    expect(trigger).toHaveFocus();
  });

  it('wraps Tab focus within the sidebar', async () => {
    await act(async () => { render(<App />); });
    fireEvent.click(await screen.findByRole('button', { name: '打开导航' }));
    const sidebar = document.querySelector('aside.sidebar') as HTMLElement;
    const focusable = Array.from(sidebar.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'));
    expect(focusable.length).toBeGreaterThan(2);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    last.focus();
    fireEvent.keyDown(sidebar, { key: 'Tab' });
    expect(document.activeElement).toBe(first);
    first.focus();
    fireEvent.keyDown(sidebar, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(last);
  });
});
