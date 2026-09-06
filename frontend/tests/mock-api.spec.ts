import { expect, test } from '@playwright/test';

type Build080MockVersion = { id: string; version_name: string; status: string; manifest_sha256: string; workflow_id: string; source_count: number; hit_status: string; created_by: string };
type Build080MockFile = { id: string; version_id: string; filename: string; sha256: string; size_bytes: number; status: string; created_at: string };
type Build080MockHit = { id: string; version_id: string; case_id: string; question: string; expected_chapter: string; actual_sources: Array<{ file: string; page: number }>; status: string; request_id: string; actor_uid: string; created_at: string };

test('student session uses real API data and keeps empty states honest', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-student' });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
  await expect(page.locator('.preview-banner')).toHaveCount(0);
  await expect(page.getByText('电力系统储能技术').first()).toBeVisible();
});

test('global search keeps seven-kind counts, filters and canonical pagination', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-global-search-${Date.now()}` });
  const items = [
    ['course', '1', null], ['chapter', 'chapter-1', 7], ['resource', 'resource-1', 7],
    ['assignment', 'assignment-1', null], ['exam', 'exam-1', null], ['discussion', 'discussion-1', null], ['knowledge', 'knowledge-1', 7],
    ['discussion', 'discussion-2', null], ['chapter', 'chapter-2', 8], ['resource', 'resource-2', 8],
    ['assignment', 'assignment-2', null], ['exam', 'exam-2', null],
  ].map(([kind, id, chapterId], index) => ({
    kind,
    id,
    title: `Unified ${kind} ${index + 1}`,
    summary: `Mock ${kind}`,
    chapter_id: chapterId,
  }));
  const searchRequests: string[] = [];
  await page.route('**/api/search*', async (route) => {
    const url = new URL(route.request().url());
    searchRequests.push(url.search);
    const kind = url.searchParams.get('kind') || 'all';
    const currentPage = Number(url.searchParams.get('page') || '1');
    const pageSize = Number(url.searchParams.get('page_size') || '10');
    const visible = kind === 'all' ? items : items.filter((item) => item.kind === kind);
    const counts = Object.fromEntries(['course', 'chapter', 'resource', 'assignment', 'exam', 'discussion', 'knowledge'].map((itemKind) => [
      itemKind,
      items.filter((item) => item.kind === itemKind).length,
    ]));
    const start = (currentPage - 1) * pageSize;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: {
        course_id: 1,
        query: 'Unified',
        kind,
        items: visible.slice(start, start + pageSize),
        counts,
        page: currentPage,
        page_size: pageSize,
        total: visible.length,
      } }),
    });
  });

  await page.goto('search?q=Unified');
  await expect(page.getByRole('heading', { name: '搜索“Unified”' })).toBeVisible();
  await expect(page.getByRole('tab', { name: /全部/ })).toContainText('12');
  await expect(page.locator('.search-result-row')).toHaveCount(10);
  await expect(page.getByText('第 1 / 2 页')).toBeVisible();
  await page.getByRole('tab', { name: /资料/ }).click({ force: true });
  await expect(page.locator('.search-result-row')).toHaveCount(2);
  await expect(page).toHaveURL(/\/search\?q=Unified&kind=resource$/);
  await expect.poll(() => searchRequests.at(-1) || '').toContain('kind=resource');
  await page.getByRole('tab', { name: /全部/ }).click({ force: true });
  await expect(page.getByText('第 1 / 2 页')).toBeVisible();
  await page.getByRole('button', { name: '搜索下一页' }).click({ force: true });
  await expect(page).toHaveURL(/\/search\?q=Unified&page=2$/);
  await expect(page.getByText('Unified exam 12')).toBeVisible();
  await expect(page.getByText('Unified course 1')).toHaveCount(0);
});

test('teacher global search opens an assignment on its canonical detail route', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-global-search-assignment-${Date.now()}` });
  await page.route('**/api/search*', async (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'ok', data: {
      course_id: 1,
      query: 'Draft Assignment',
      kind: 'all',
      items: [{ kind: 'assignment', id: 'assignment-draft', title: 'Draft Assignment', summary: '教师草稿作业', chapter_id: null }],
      counts: { course: 0, chapter: 0, resource: 0, assignment: 1, exam: 0, discussion: 0, knowledge: 0 },
      page: 1,
      page_size: 10,
      total: 1,
    } }),
  }));

  await page.goto('search?q=Draft%20Assignment');
  await page.getByRole('button', { name: /Draft Assignment/ }).click({ force: true });
  await expect(page).toHaveURL(/\/teacher\/courses\/1\/assignments\/assignment-draft$/);
});

test('global search opens all seven kinds on canonical routes', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-global-search-routes-${Date.now()}` });
  const cases = [
    ['course', '1', null, '/courses/1'],
    ['chapter', 'chapter-1', 7, '/courses/1/chapters/7'],
    ['resource', 'resource-1', 7, '/courses/1/resources/resource-1'],
    ['assignment', 'assignment-1', null, '/courses/1/assignments/assignment-1'],
    ['exam', 'exam-1', null, '/courses/1/exams/exam-1'],
    ['discussion', 'discussion-1', null, '/courses/1/discussions/discussion-1'],
    ['knowledge', 'knowledge-1', 7, '/knowledge-graph?q=Unified%20knowledge'],
  ] as const;
  await page.route('**/api/search*', async (route) => {
    const url = new URL(route.request().url());
    const kind = url.searchParams.get('q') || 'course';
    const item = cases.find(([itemKind]) => itemKind === kind) || cases[0];
    const [itemKind, id, chapterId] = item;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: {
        course_id: 1,
        query: kind,
        kind: 'all',
        items: [{ kind: itemKind, id, title: 'Unified knowledge', summary: 'canonical fixture', chapter_id: chapterId }],
        counts: { course: itemKind === 'course' ? 1 : 0, chapter: itemKind === 'chapter' ? 1 : 0, resource: itemKind === 'resource' ? 1 : 0, assignment: itemKind === 'assignment' ? 1 : 0, exam: itemKind === 'exam' ? 1 : 0, discussion: itemKind === 'discussion' ? 1 : 0, knowledge: itemKind === 'knowledge' ? 1 : 0 },
        page: 1,
        page_size: 10,
        total: 1,
      } }),
    });
  });

  for (const [kind, , , expectedPath] of cases) {
    await page.goto(`search?q=${kind}`);
    await expect(page.locator('.search-result-row')).toHaveCount(1);
    await page.locator('.search-result-row').click({ force: true });
    await expect(page).toHaveURL(new RegExp(`${expectedPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
  }
});

test('admin global search preserves staff canonical routes for all seven kinds', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'admin', 'x-dev-user': `playwright-global-search-admin-${Date.now()}` });
  const cases = [
    ['course', '1', null, '/teacher/courses/1/overview'],
    ['chapter', 'chapter-1', 7, '/teacher/courses/1/overview'],
    ['resource', 'resource-1', 7, '/teacher/courses/1/resources'],
    ['assignment', 'assignment-1', null, '/teacher/courses/1/assignments/assignment-1'],
    ['exam', 'exam-1', null, '/teacher/courses/1/exams'],
    ['discussion', 'discussion-1', null, '/courses/1/discussions/discussion-1'],
    ['knowledge', 'knowledge-1', 7, '/knowledge-graph?q=Unified%20knowledge'],
  ] as const;
  await page.route('**/api/search*', async (route) => {
    const query = new URL(route.request().url()).searchParams.get('q') || 'course';
    const item = cases.find(([itemKind]) => itemKind === query) || cases[0];
    const [itemKind, id, chapterId] = item;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: {
        course_id: 1,
        query,
        kind: 'all',
        items: [{ kind: itemKind, id, title: 'Unified knowledge', summary: 'admin canonical fixture', chapter_id: chapterId }],
        counts: { course: itemKind === 'course' ? 1 : 0, chapter: itemKind === 'chapter' ? 1 : 0, resource: itemKind === 'resource' ? 1 : 0, assignment: itemKind === 'assignment' ? 1 : 0, exam: itemKind === 'exam' ? 1 : 0, discussion: itemKind === 'discussion' ? 1 : 0, knowledge: itemKind === 'knowledge' ? 1 : 0 },
        page: 1,
        page_size: 10,
        total: 1,
      } }),
    });
  });

  for (const [kind, , , expectedPath] of cases) {
    await page.goto(`search?q=${kind}`);
    await expect(page.locator('.search-result-row')).toHaveCount(1);
    await page.locator('.search-result-row').click({ force: true });
    await expect(page).toHaveURL(new RegExp(`${expectedPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
  }
});

test('dashboard restores the latest learning position after a real progress save and refresh', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-resume-${Date.now()}` });
  await page.goto('/');
  const saved = await page.evaluate(async () => {
    const resourcesResponse = await fetch('/api/textbook/resources?chapter_id=3');
    const resourcesPayload = await resourcesResponse.json();
    const resource = resourcesPayload.data.items[0];
    const savedPage = Math.min(12, resource.page_end);
    const progressResponse = await fetch(`/api/student/resources/${encodeURIComponent(resource.id)}/progress`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': `browser-resume-${Date.now()}` },
      body: JSON.stringify({ page: savedPage, percent: 60, completed: false, base_version: 0 }),
    });
    if (!progressResponse.ok) throw new Error(`progress save failed: ${progressResponse.status}`);
    return { id: resource.id, page: savedPage };
  });

  await page.reload();
  await expect(page.getByText(new RegExp(`第 3 章 .* 第 ${saved.page} 页 .* 已学习 60%`))).toBeVisible();
  await expect(page.locator('.dashboard-resume-action')).toContainText('继续');
  await page.locator('.dashboard-resume-action').click({ force: true });
  await expect(page).toHaveURL(new RegExp(`/courses/1/resources/${saved.id}\\?page=${saved.page}$`));
});

test('student can browse the API-backed course list and enter an authorized course', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-course-list' });
  const courseRequests: string[] = [];
  page.on('request', (request) => { if (request.url().includes('/api/courses')) courseRequests.push(request.url()); });
  await page.goto('courses');
  await expect(page.getByRole('heading', { name: '我的课程' })).toBeVisible();
  await expect(page.locator('.preview-banner')).toHaveCount(0);
  const card = page.locator('.course-summary-card[data-course-id="1"]');
  await expect(card).toBeVisible();
  await expect(card.getByText('电力系统储能技术')).toBeVisible();
  await expect(card.getByText('6 个章节')).toBeVisible();
  await card.getByRole('button', { name: '进入课程 电力系统储能技术' }).click({ force: true });
  await expect(page).toHaveURL(/\/courses\/1$/);
  await expect(page.getByRole('heading', { name: '电力系统储能技术' })).toBeVisible();
  await page.goto('courses');
  await page.getByLabel('课程排序').selectOption('progress');
  await expect.poll(() => courseRequests.some((url) => url.includes('sort=progress') && url.includes('page=1') && url.includes('page_size=6'))).toBe(true);
});

test('course list uses server pagination without mixing page results', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-course-pagination' });
  const items = Array.from({ length: 7 }, (_, index) => ({
    id: index + 1,
    name: `测试课程 ${index + 1}`,
    teacher: '课程教师',
    class_name: '测试班',
    status: 'active',
    progress: index * 10,
    chapter_count: 6,
    resource_count: 20,
    last_accessed_at: null,
  }));
  await page.route('**/api/courses*', async (route) => {
    const url = new URL(route.request().url());
    const currentPage = Number(url.searchParams.get('page') || '1');
    const pageSize = Number(url.searchParams.get('page_size') || '6');
    const start = (currentPage - 1) * pageSize;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: { items: items.slice(start, start + pageSize), page: currentPage, page_size: pageSize, total: items.length } }),
    });
  });
  await page.goto('courses');
  await expect(page.locator('.course-summary-card')).toHaveCount(6);
  await expect(page.getByText('第 1 / 2 页')).toBeVisible();
  const nextPageButton = page.getByRole('button', { name: '下一页' });
  await expect(nextPageButton).toBeEnabled();
  await nextPageButton.click({ force: true });
  await expect(page.locator('.course-summary-card')).toHaveCount(1);
  await expect(page.getByRole('heading', { name: '测试课程 7' })).toBeVisible();
  await expect(page.getByText('测试课程 1')).toHaveCount(0);
  await expect(page.getByText('第 2 / 2 页')).toBeVisible();
});

test('course list renders an explicit empty state from an empty API response', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-course-empty' });
  await page.route('**/api/courses*', async (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'ok', data: { items: [], page: 1, page_size: 20, total: 0 } }),
  }));
  await page.goto('courses');
  await expect(page.getByRole('heading', { name: '我的课程' })).toBeVisible();
  await expect(page.getByText('暂无可用课程')).toBeVisible();
  await expect(page.locator('.course-summary-card')).toHaveCount(0);
});

test('course list renders a retryable error state when the API fails', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-course-error' });
  await page.route('**/api/courses*', async (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'error', data: null, error: { code: 'course_service_unavailable', message: '课程服务暂不可用' } }),
  }));
  await page.goto('courses');
  await expect(page.getByRole('alert')).toContainText('课程列表加载失败');
  await expect(page.getByRole('button', { name: /重试/ })).toBeVisible();
});

test('session expiry clears protected data and offers a login path', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-build020-expiry-${Date.now()}` });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
  await page.route('**/api/student/tasks*', async (route) => route.fulfill({
    status: 401,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'error', data: null, error: { code: 'session_expired', message: '课程会话已过期' } }),
  }));
  await page.goto('tasks');
  await expect(page.locator('.session-expired-banner')).toContainText('课程会话已过期');
  await expect(page.getByText('当前为预览模式')).toHaveCount(0);
  await expect(page.getByText('请重新登录后继续学习。')).toBeVisible();
  await expect(page.getByRole('button', { name: /重新登录/ })).toBeVisible();
});

test('startup session expiry never falls back to preview data', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-build020-startup-expiry-${Date.now()}` });
  await page.route('**/api/student/assignments*', async (route) => route.fulfill({
    status: 401,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'error', data: null, error: { code: 'session_expired', message: '课程会话已过期' } }),
  }));
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('课程会话已过期');
  await expect(page.getByText('当前为预览模式')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
});

test('teacher session exposes the teacher workspace through the server role', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': 'playwright-teacher' });
  await page.goto('/');
  await expect(page.getByRole('link', { name: '教师工作台' })).toBeVisible();
  await expect(page.locator('.preview-banner')).toHaveCount(0);
});

test('student canonical course routes resolve to the planned learning pages', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-route-student-${Date.now()}` });
  const routes = [
    ['courses/1', '电力系统储能技术'],
    ['courses/1/chapters/3', '电力储能系统的组成及工作原理'],
    ['courses/1/assignments', '待办任务'],
    ['courses/1/exams', '限时考试'],
    ['courses/1/resources', '课程资料'],
    ['courses/1/materials', '课程资料'],
    ['courses/1/discussions', '课程讨论'],
    ['courses/1/progress', '我的学习状态'],
    ['courses/1/grades', '成绩与反馈'],
    ['courses/1/agent', '在课程语境中学习'],
  ] as const;
  for (const [route, heading] of routes) {
    await page.goto(route);
    await expect(page.getByRole('heading', { name: heading })).toBeVisible();
    await expect(page.locator('.preview-banner')).toHaveCount(0);
  }
});

test('unified task center filters four task kinds and performs a real refresh', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-task-center-${Date.now()}` });
  const requests: string[] = [];
  const items = [
    { id: 'assignment:browser-a', source_id: 'browser-a', kind: 'assignment', title: '浏览器作业任务', summary: '完成章节练习', status: 'pending', due_at: '2026-08-01T08:00:00Z', updated_at: '2026-07-29T08:00:00Z', progress: 0 },
    { id: 'exam:browser-e', source_id: 'browser-e', kind: 'exam', title: '浏览器考试任务', summary: '继续限时考试', status: 'in_progress', due_at: '2026-08-02T08:00:00Z', updated_at: '2026-07-29T08:10:00Z', progress: 50 },
    { id: 'discussion:browser-d', source_id: 'browser-d', kind: 'discussion', title: '浏览器讨论任务', summary: '发表课程观点', status: 'pending', due_at: null, updated_at: '2026-07-29T08:20:00Z', progress: 0 },
    { id: 'notification:browser-n', source_id: 'browser-n', kind: 'notification', title: '浏览器通知任务', summary: '查看课程公告', status: 'completed', due_at: null, updated_at: '2026-07-29T08:30:00Z', progress: 100 },
  ];
  await page.route('**/api/student/tasks*', async (route) => {
    const url = route.request().url();
    requests.push(url);
    const query = new URL(url).searchParams;
    const kind = query.get('kind');
    const status = query.get('status');
    const visible = items.filter((item) => (!kind || item.kind === kind) && (!status || item.status === status));
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: { items: visible, page: 1, page_size: 10, total: visible.length, counts: { by_status: { pending: 2, in_progress: 1, completed: 1, expired: 0 }, by_kind: { assignment: 1, exam: 1, discussion: 1, notification: 1 } } } }),
    });
  });

  await page.goto('tasks');
  await expect(page.getByText('浏览器作业任务')).toBeVisible();
  await expect(page.getByText('浏览器考试任务')).toBeVisible();
  await expect(page.getByText('浏览器讨论任务')).toBeVisible();
  await expect(page.getByText('浏览器通知任务')).toBeVisible();
  await page.locator('.task-kind-filters button').filter({ hasText: '考试' }).click({ force: true });
  await expect(page.getByText('浏览器考试任务')).toBeVisible();
  await expect(page.getByText('浏览器作业任务')).toHaveCount(0);
  await page.getByRole('tab', { name: /进行中/ }).click({ force: true });
  await expect.poll(() => requests.at(-1) || '').toContain('kind=exam&status=in_progress');
  const beforeRefresh = requests.length;
  await page.getByRole('button', { name: '刷新状态' }).click({ force: true });
  await expect.poll(() => requests.length).toBe(beforeRefresh + 1);
});

test('task-center notification deep link locates the requested visible notice', async ({ page }) => {
  const suffix = Date.now();
  const title = `任务定位通知 ${suffix}`;
  const targetId = `notice-task-${suffix}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-task-notice-teacher-${suffix}` });
  await page.goto('teacher');
  await page.route('**/api/teacher/notifications*', async (route) => {
    if (route.request().method() !== 'POST') {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: { id: targetId, audience: 'course_students', title, body: '从任务中心定位这条通知。', created_by: 'teacher-fixture', is_read: false } }),
    });
  });
  const target = await page.evaluate(async ({ notificationTitle, testSuffix }) => {
    const response = await fetch('/api/teacher/notifications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': `task-notice-target-${testSuffix}` },
      body: JSON.stringify({ title: notificationTitle, body: '从任务中心定位这条通知。', audience: 'course_students' }),
    });
    const payload = await response.json();
    return { status: response.status, id: String(payload.data?.id || '') };
  }, { notificationTitle: title, testSuffix: suffix });
  expect(target.status).toBe(201);
  expect(target.id).toBe(targetId);

  await page.route('**/api/student/tasks*', async (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'ok', data: { items: [{ id: `notification:${target.id}`, source_id: target.id, kind: 'notification', title, summary: '从任务中心定位这条通知。', status: 'pending', due_at: null, updated_at: '2026-07-29T08:00:00Z', progress: 0 }], page: 1, page_size: 10, total: 1, counts: { by_status: { pending: 1, in_progress: 0, completed: 0, expired: 0 }, by_kind: { assignment: 0, exam: 0, discussion: 0, notification: 1 } } } }),
  }));
  await page.route('**/api/notifications*', async (route) => {
    if (route.request().method() !== 'GET') {
      await route.continue();
      return;
    }
    const requestUrl = new URL(route.request().url());
    const focusFound = requestUrl.searchParams.get('focus_id') === target.id;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: {
        items: [{ id: target.id, audience: 'course_students', title, body: '从任务中心定位这条通知。', created_by: 'teacher-fixture', created_at: '2026-07-30T00:00:00Z', is_read: false }],
        unread_count: 1,
        page: 1,
        page_size: Number(requestUrl.searchParams.get('page_size') || 8),
        total: 1,
        focus_found: focusFound,
        focused_id: focusFound ? target.id : null,
      } }),
    });
  });
  let readWrites = 0;
  page.on('request', (request) => {
    if (request.method() === 'PUT' && request.url().includes(`/api/notifications/${target.id}/read`)) readWrites += 1;
  });
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-task-notice-student-${suffix}` });
  await page.goto('tasks');
  const taskRow = page.locator('.task-center-row').filter({ hasText: title });
  await taskRow.getByRole('button', { name: /查看/ }).click({ force: true });

  await expect(page).toHaveURL(new RegExp(`/messages\\?notice=${target.id}$`));
  await expect(page.getByText('已定位到任务对应的课程通知。')).toBeVisible();
  const focusedNotice = page.getByRole('button', { name: `${title}，标为已读` });
  await expect(focusedNotice).toHaveAttribute('aria-current', 'true');
  await expect(focusedNotice).toBeEnabled();
  expect(readWrites).toBe(0);
});

test('canonical teacher course routes preserve the teacher role boundary', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-route-teacher-${Date.now()}` });
  const routes = [
    ['teacher/courses/1/overview', '教师工作台'],
    ['teacher/courses/1/question-bank', '题库管理'],
    ['teacher/courses/1/assignments', '作业发布'],
    ['teacher/courses/1/exams', '考试管理'],
    ['teacher/courses/1/resources', '课程资料管理'],
    ['teacher/courses/1/activities', '课堂活动管理'],
    ['teacher/courses/1/gradebook', '成绩册与学情'],
    ['teacher/courses/1/grading', '成绩册与学情'],
    ['teacher/courses/1/analytics', '成绩册与学情'],
    ['teacher/courses/1/agent', '在课程语境中学习'],
  ] as const;
  for (const [route, heading] of routes) {
    await page.goto(route);
    await expect(page.getByRole('heading', { name: heading })).toBeVisible();
    await expect(page.locator('.preview-banner')).toHaveCount(0);
  }
});

test('student cannot enter a canonical teacher course route', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-route-forbidden-${Date.now()}` });
  await page.goto('teacher/courses/1/overview');
  await expect(page).toHaveURL(/\/learn\/$/);
  await expect(page.getByRole('heading', { name: '早上好，林同学' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '教师工作台' })).toHaveCount(0);
});

test('student cannot use an unauthorized course id to render the current course data', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-course-forbidden-${Date.now()}` });
  await page.goto('courses/999');
  await expect(page).toHaveURL(/\/courses$/);
  await expect(page.getByRole('heading', { name: '我的课程' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '电力系统储能技术' })).toBeVisible();
});

test('all canonical student course subroutes reject an unauthorized course id', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-course-scope-${Date.now()}` });
  for (const route of ['assignments', 'exams', 'resources', 'discussions', 'progress', 'grades', 'agent']) {
    await page.goto(`courses/999/${route}`);
    await expect(page).toHaveURL(/\/courses$/);
    await expect(page.getByRole('heading', { name: '我的课程' })).toBeVisible();
  }
});

test('teacher canonical course subroutes reject an unauthorized course id', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-teacher-course-scope-${Date.now()}` });
  await page.goto('teacher/courses/999/gradebook');
  await expect(page).toHaveURL(/\/courses$/);
  await expect(page.getByRole('heading', { name: '我的课程' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '成绩册与学情' })).toHaveCount(0);
});

test('resource reader opens the mounted PDF and renders the course reader', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-reader' });
  await page.goto('resources');
  const card = page.locator('.resource-card').filter({ hasText: '储能变流器拓扑及并网控制' });
  await expect(card.getByRole('button', { name: '打开资料' })).toBeVisible();
  await card.getByRole('button', { name: '打开资料' }).click({ force: true });
  await expect(page.getByRole('heading', { name: '储能变流器拓扑及并网控制' })).toBeVisible();
  await expect(page.getByText('课程阅读器').first()).toBeVisible();
  await expect(page.locator('iframe.pdf-frame')).toBeVisible();
});

test('student favorites page keeps preview empty and supports server list removal', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-favorites-${Date.now()}` });
  await page.goto('favorites');
  await expect(page.getByRole('heading', { name: '资料收藏' })).toBeVisible();
  await expect(page.getByText('还没有收藏资料')).toBeVisible();
  await page.route('**/api/student/resources/favorites', async (route) => {
    if (route.request().method() !== 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { resource_id: 'res-b06094df045f317595ff', favorite: false } }) });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: { items: [{ id: 'res-b06094df045f317595ff', title: '收藏的并网控制', source_file: '3.4.pdf', chapter_id: 3, page_end: 38, available: false, mount_status: 'pending_mount', version: 'v1', note_count: 1, favorite_at: '2026-07-26T08:00:00Z' }], page: 1, page_size: 20, total: 1 } }),
    });
  });
  await page.reload();
  await expect(page.getByRole('heading', { name: '收藏的并网控制' })).toBeVisible();
  await expect(page.getByText('1 条笔记')).toBeVisible();
  await page.getByRole('button', { name: '取消收藏' }).click({ force: true });
  await expect(page.getByText('还没有收藏资料')).toBeVisible();
});

test('student can save a draft and submit an assignment through the server contract', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-assessment' });
  await page.route('**/api/student/assignments/ui-assignment-1', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
      id: 'ui-assignment-1', title: '第 3 章章节练习', status: 'published', due_at: '2026-07-28', question_ids: ['ui-q-1'], allow_attempts: 1,
      questions: [{ id: 'ui-q-1', prompt: '储能系统可以承担什么作用？', question_type: 'single_choice', options: ['平衡供需', '取消电网'], max_score: 10 }], my_submissions: [], my_draft: { assignment_id: 'ui-assignment-1', attempt: 1, answers: {}, version: 0, has_saved_draft: false },
    } }) });
  });
  await page.route('**/api/student/assignments/ui-assignment-1/draft**', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { assignment_id: 'ui-assignment-1', attempt: 1, answers: {}, version: 0, has_saved_draft: false } }) });
      return;
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { assignment_id: 'ui-assignment-1', attempt: 1, answers: { 'ui-q-1': '平衡供需' }, version: 1, has_saved_draft: true } }) });
  });
  await page.route('**/api/student/assignments/ui-assignment-1/submit', async (route) => {
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { id: 'ui-submission-1', assignment_id: 'ui-assignment-1', attempt: 1, status: 'submitted' } }) });
  });
  await page.goto('tasks/ui-assignment-1');
  await expect(page.getByRole('heading', { name: '第 3 章章节练习' })).toBeVisible();
  await page.getByLabel('平衡供需').check({ force: true });
  await page.getByRole('button', { name: '最终提交' }).click({ force: true });
  await expect(page.getByText('提交成功')).toBeVisible();
  await expect(page.getByText('提交编号：ui-submission-1')).toBeVisible();
});

test('teacher can open a submission and refresh the server-side grade result', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': 'playwright-grader' });
  await page.route('**/api/student/assignments/teacher-assignment-1', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
      id: 'teacher-assignment-1', title: '教师批改验收作业', status: 'published', due_at: '2026-07-28', question_ids: ['teacher-q-1'], allow_attempts: 1,
      questions: [{ id: 'teacher-q-1', prompt: '选择正确的储能作用', question_type: 'single_choice', options: ['平衡供需', '取消电网'], max_score: 10 }],
    } }) });
  });
  let graded = false;
  await page.route('**/api/teacher/assignments/teacher-assignment-1/submissions', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [{ id: 'teacher-sub-1', assignment_id: 'teacher-assignment-1', attempt: 1, status: 'submitted', created_at: '2026-07-25T08:00:00Z', answers: { 'teacher-q-1': '平衡供需' }, score: graded ? 10 : null, max_score: 10, grades: graded ? [{ id: 'teacher-grade-1', question_id: 'teacher-q-1', score: 10, max_score: 10, feedback: '客观题按固定答案评分', source: 'deterministic' }] : [] }] } }) });
  });
  await page.route('**/api/teacher/submissions/teacher-sub-1/grade', async (route) => {
    graded = true;
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { submission_id: 'teacher-sub-1', assignment_id: 'teacher-assignment-1', score: 10, max_score: 10, grades: [{ id: 'teacher-grade-1', question_id: 'teacher-q-1', score: 10, max_score: 10, feedback: '客观题按固定答案评分', source: 'deterministic' }] } }) });
  });
  await page.goto('teacher/assignments/teacher-assignment-1');
  await expect(page.getByRole('heading', { name: '教师批改验收作业' })).toBeVisible();
  await expect(page.getByText('等待评分')).toBeVisible();
  await page.getByRole('button', { name: '重新评分' }).click({ force: true });
  await expect(page.getByRole('heading', { name: '10 / 10' })).toBeVisible();
  await expect(page.getByText('客观题自动评分')).toBeVisible();
});

test('student can create and reply to a discussion, and teacher can moderate it', async ({ page }) => {
  const topicTitle = `Playwright 讨论 ${Date.now()}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-social-${Date.now()}` });
  await page.goto('discussions');
  await expect(page.getByRole('heading', { name: '课程讨论' })).toBeVisible();
  await page.getByLabel('主题').fill(topicTitle);
  await page.getByLabel('内容').fill('讨论储能变流器的并网控制目标。');
  await page.getByRole('button', { name: '发布主题' }).click({ force: true });
  await expect(page.getByRole('heading', { name: topicTitle })).toBeVisible();
  await page.getByLabel('回复内容').fill('可以从功率平衡和电流约束两个角度分析。');
  await page.getByRole('button', { name: '回复主题' }).click({ force: true });
  await expect(page.getByText('可以从功率平衡和电流约束两个角度分析。')).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-social-teacher-${Date.now()}` });
  await page.reload();
  await expect(page.getByRole('button', { name: '置顶主题' })).toBeVisible();
  await page.getByRole('button', { name: '置顶主题' }).click({ force: true });
  await expect(page.getByText('置顶 · 开放')).toBeVisible();
  await page.getByRole('button', { name: '标记解决' }).click({ force: true });
  await expect(page.getByText('置顶 · 已解决')).toBeVisible();
});

test('teacher can publish notifications and student can paginate, persist and bulk-read them', async ({ page }) => {
  const suffix = Date.now();
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-notice-teacher-${suffix}` });
  await page.goto('teacher');
  await page.getByLabel('通知标题').fill(`Playwright 通知 ${suffix}`);
  await page.getByLabel('通知内容').fill('请完成本周课程练习。');
  await page.getByLabel('通知受众').selectOption('course_students');
  await page.getByRole('button', { name: '发布通知' }).click({ force: true });
  await expect(page.getByText('通知已发布，目标受众可以在消息中心查看。')).toBeVisible();
  const extraStatuses = await page.evaluate(async (testSuffix) => Promise.all(Array.from({ length: 8 }, async (_, index) => {
    const response = await fetch('/api/teacher/notifications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': `playwright-notice-page-${testSuffix}-${index}` },
      body: JSON.stringify({ title: `分页通知 ${testSuffix}-${index + 1}`, body: '用于验证消息中心服务端分页。', audience: 'course_students' }),
    });
    return response.status;
  })), suffix);
  expect(extraStatuses).toEqual(Array(8).fill(201));
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-notice-student-${suffix}` });
  await page.goto('messages');
  await expect(page.getByRole('navigation', { name: '通知列表分页' })).toContainText('第 1 / 2 页，共 9 条');
  await expect(page.getByRole('button', { name: '消息通知，9 条未读' })).toBeVisible();
  const message = page.locator('.message-row').first();
  const firstTitle = await message.locator('strong').textContent();
  expect(firstTitle).toBeTruthy();
  await expect(message).toBeVisible();
  await expect(message.locator('[aria-label="未读"]')).toHaveCount(1);
  await message.click({ force: true });
  await expect(message.locator('[aria-label="未读"]')).toHaveCount(0);
  await page.reload();
  const persisted = page.getByRole('button', { name: `${firstTitle}，已读` });
  await expect(persisted.locator('[aria-label="未读"]')).toHaveCount(0);
  await page.getByRole('button', { name: '通知下一页' }).click({ force: true });
  await expect(page.getByRole('navigation', { name: '通知列表分页' })).toContainText('第 2 / 2 页，共 9 条');
  await page.getByRole('button', { name: '全部已读' }).click();
  await expect(page.getByText(/已将 \d+ 条通知标为已读/)).toBeVisible();
  await page.getByRole('tab', { name: /未读/ }).click();
  await expect(page.getByText('当前没有未读通知。')).toBeVisible();
  await page.reload();
  await page.getByRole('tab', { name: /未读/ }).click();
  await expect(page.getByText('当前没有未读通知。')).toBeVisible();
  await expect(page.getByRole('button', { name: '消息通知' })).toBeVisible();
});

test('teacher can create activity drafts and publish a student-visible activity', async ({ page }) => {
  const suffix = Date.now();
  const draftTitle = `Playwright 活动草稿 ${suffix}`;
  const publishedTitle = `Playwright 活动发布 ${suffix}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-activity-teacher-${suffix}` });
  await page.goto('teacher/activities');
  await expect(page.getByRole('heading', { name: '课堂活动管理' })).toBeVisible();
  await page.getByLabel('活动标题').fill(draftTitle);
  await page.getByLabel('活动说明').fill('检查学生对并网控制关键目标的理解。');
  await page.getByLabel('活动选项').fill('功率平衡\n电流控制\n通信协调');
  await page.getByRole('button', { name: '保存活动草稿' }).click({ force: true });
  await expect(page.getByText('课堂活动草稿已保存。')).toBeVisible();
  await expect(page.getByText(draftTitle, { exact: true })).toBeVisible();

  await page.getByLabel('活动标题').fill(publishedTitle);
  await page.getByLabel('活动说明').fill('请选择最重要的控制目标。');
  await page.getByLabel('活动选项').fill('功率平衡\n电流控制\n通信协调');
  await page.getByLabel('活动保存状态').selectOption('published');
  await page.getByRole('button', { name: '发布课堂活动' }).click({ force: true });
  await expect(page.getByText('课堂活动已发布，学生可以在开放活动中看到。')).toBeVisible();
  await expect(page.getByText(publishedTitle, { exact: true })).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-activity-student-${suffix}` });
  await page.goto('activities');
  await expect(page.getByRole('button', { name: new RegExp(publishedTitle) })).toBeVisible();
  await expect(page.getByText(draftTitle, { exact: true })).toHaveCount(0);
});

test('teacher can publish a check-in and inspect a persisted student attendance record', async ({ page }) => {
  const suffix = Date.now();
  const title = `Playwright 课堂签到 ${suffix}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-checkin-teacher-${suffix}` });
  await page.goto('teacher/activities');
  await page.getByLabel('活动类型').selectOption('checkin');
  await expect(page.getByLabel('活动选项')).toHaveCount(0);
  await expect(page.getByLabel('活动允许次数')).toBeDisabled();
  await page.getByLabel('活动标题').fill(title);
  await page.getByLabel('活动说明').fill('请在本节课内完成签到。');
  await page.getByLabel('活动保存状态').selectOption('published');
  await page.getByRole('button', { name: '发布课堂活动' }).click({ force: true });
  await expect(page.getByText('课堂活动已发布，学生可以在开放活动中看到。')).toBeVisible();
  const row = page.locator('.teacher-table-row').filter({ hasText: title });
  await expect(row).toContainText('签到');

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-checkin-student-${suffix}` });
  await page.goto('activities');
  await page.getByRole('button', { name: new RegExp(title) }).click({ force: true });
  const checkinUrl = page.url();
  await expect(page.getByRole('button', { name: '确认签到' })).toBeVisible();
  await page.getByRole('button', { name: '确认签到' }).click({ force: true });
  await expect(page.getByText('签到成功，服务端已记录本次签到。')).toBeVisible();
  await expect(page.getByRole('button', { name: '已签到' })).toBeDisabled();
  await page.reload();
  await expect(page.getByRole('button', { name: '已签到' })).toBeDisabled();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-checkin-teacher-${suffix}` });
  await page.goto(checkinUrl);
  await expect(page.getByText('1 人已签到')).toBeVisible();
  await expect(page.getByRole('list', { name: '签到记录' }).getByRole('listitem')).toHaveCount(1);
});

test('quick response keeps the winner terminal, rejects the loser privately and cannot reopen', async ({ page, context }) => {
  const activityId = 'ui-quick-response-1';
  const title = 'Playwright 课堂抢答';
  const submittedAt = '2026-07-29T08:30:00Z';
  const winnerUser = 'playwright-quick-winner';
  const loserUser = 'playwright-quick-loser';
  const winnerPrivateRef = 'u_private_quick_response_winner';
  const studentActivityBodies: string[] = [];
  let claimedBy: string | null = null;

  const activityFor = (user: string, role: string) => {
    const hasWinner = claimedBy !== null;
    const hasResponded = claimedBy === user;
    return {
      id: activityId,
      kind: 'quick_response',
      title,
      body: '请在教师发出口令后抢答。',
      options: [],
      status: hasWinner ? 'closed' : 'published',
      max_attempts: 1,
      has_responded: hasResponded,
      attempts_used: hasResponded ? 1 : 0,
      can_respond: role === 'student' && !hasWinner,
      can_reopen: false,
      next_attempt: role === 'student' && !hasWinner ? 1 : null,
      my_response: hasResponded ? {
        id: 'quick-response-winning-response',
        activity_id: activityId,
        attempt: 1,
        answers: ['claim'],
        submitted_at: submittedAt,
      } : null,
    };
  };

  await context.route('**/api/activities**', async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    const headers = request.headers();
    const role = headers['x-dev-role'] || 'student';
    const user = headers['x-dev-user'] || '';
    const fulfill = async (status: number, payload: unknown) => {
      const body = JSON.stringify(payload);
      if (role === 'student') studentActivityBodies.push(body);
      await route.fulfill({ status, contentType: 'application/json', body });
    };

    if (path === '/api/activities' && request.method() === 'GET') {
      await fulfill(200, { status: 'ok', data: { items: [activityFor(user, role)] } });
      return;
    }
    if (path === `/api/activities/${activityId}` && request.method() === 'GET') {
      await fulfill(200, { status: 'ok', data: activityFor(user, role) });
      return;
    }
    if (path === `/api/activities/${activityId}/results` && request.method() === 'GET') {
      const hasWinner = claimedBy !== null;
      const hasResponded = claimedBy === user;
      await fulfill(200, { status: 'ok', data: {
        activity_id: activityId,
        kind: 'quick_response',
        total_responses: hasWinner ? 1 : 0,
        has_responded: hasResponded,
        results_available: hasWinner,
        options: [],
        participants: role === 'student' || !hasWinner ? [] : [{ user_ref: winnerPrivateRef, submitted_at: submittedAt }],
      } });
      return;
    }
    if (path === `/api/activities/${activityId}/responses` && request.method() === 'POST') {
      const body = request.postDataJSON() as { answers?: string[]; attempt?: number } | null;
      expect(body).toEqual({ answers: ['claim'], attempt: 1 });
      expect(headers['idempotency-key']).toBe(`activity-response:${activityId}:1`);
      expect(headers['x-moodle-sesskey']).toBeTruthy();
      if (claimedBy === null) {
        claimedBy = user;
        await fulfill(201, { status: 'ok', data: {
          id: 'quick-response-winning-response',
          activity_id: activityId,
          attempt: 1,
          answers: ['claim'],
          submitted_at: submittedAt,
        } });
        return;
      }
      await fulfill(409, { status: 'error', data: null, error: {
        code: 'quick_response_already_claimed',
        message: '已有同学抢答成功，本次抢答已结束',
      } });
      return;
    }
    await route.continue();
  });

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': winnerUser });
  const loserPage = await context.newPage();
  await loserPage.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': loserUser });
  await Promise.all([page.goto(`activities/${activityId}`), loserPage.goto(`activities/${activityId}`)]);
  await expect(page.getByRole('button', { name: '立即抢答' })).toBeEnabled();
  await expect(loserPage.getByRole('button', { name: '立即抢答' })).toBeEnabled();

  const winnerResponsePromise = page.waitForResponse((response) => response.url().endsWith(`/api/activities/${activityId}/responses`) && response.request().method() === 'POST');
  await page.getByRole('button', { name: '立即抢答' }).click({ force: true });
  expect((await winnerResponsePromise).status()).toBe(201);
  await expect(page.getByRole('button', { name: '已抢到' })).toBeDisabled();
  await expect(page.getByText('你是首位响应者')).toBeVisible();
  await page.reload();
  await expect(page.getByRole('button', { name: '已抢到' })).toBeDisabled();
  await expect(page.getByText('你是首位响应者')).toBeVisible();

  const loserResponsePromise = loserPage.waitForResponse((response) => response.url().endsWith(`/api/activities/${activityId}/responses`) && response.request().method() === 'POST');
  await loserPage.getByRole('button', { name: '立即抢答' }).click({ force: true });
  const loserResponse = await loserResponsePromise;
  expect(loserResponse.status()).toBe(409);
  expect(await loserResponse.text()).not.toContain('user_ref');
  await expect(loserPage.getByText('已有同学抢答成功，本次抢答已结束')).toBeVisible();
  await expect(loserPage.getByRole('button', { name: '抢答已结束' })).toBeDisabled();
  await expect(loserPage.locator('body')).not.toContainText(winnerPrivateRef);
  expect(studentActivityBodies.every((body) => !body.includes('user_ref') && !body.includes(winnerPrivateRef))).toBe(true);

  const teacherPage = await context.newPage();
  await teacherPage.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': 'playwright-quick-teacher' });
  await teacherPage.goto('teacher/activities');
  const teacherRow = teacherPage.locator('.teacher-table-row').filter({ hasText: title });
  await expect(teacherRow).toContainText('首位响应已确认');
  await expect(teacherRow.getByRole('button', { name: '重新开放', exact: true })).toHaveCount(0);

  await loserPage.close();
  await teacherPage.close();
});

test('random selection and group tasks preserve roster privacy across teacher and student views', async ({ page, context }) => {
  const randomActivityId = 'ui-random-selection-1';
  const groupActivityId = 'ui-group-task-1';
  const selectedUser = 'playwright-random-student';
  let randomSelected = false;
  let groupsGenerated = false;
  let randomWrites = 0;
  let groupWrites = 0;

  const randomActivity = {
    id: randomActivityId,
    kind: 'random_selection',
    title: 'Playwright 随机选人',
    body: '从当前课程花名册中抽取一名学生。',
    options: [],
    status: 'published',
    max_attempts: 1,
    has_responded: false,
    attempts_used: 0,
    can_respond: false,
    can_reopen: false,
    next_attempt: null,
    my_response: null,
  };
  const groupActivity = (role: string) => ({
    id: groupActivityId,
    kind: 'group_task',
    title: 'Playwright 分组任务',
    body: '按预设组名生成均衡分组。',
    options: role === 'student' ? [] : [{ id: 'alpha', label: '甲组' }, { id: 'beta', label: '乙组' }],
    status: 'published',
    max_attempts: 1,
    has_responded: false,
    attempts_used: 0,
    can_respond: false,
    can_reopen: false,
    next_attempt: null,
    my_response: null,
  });

  await context.route('**/api/**', async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    const headers = request.headers();
    const role = headers['x-dev-role'] || 'student';
    const user = headers['x-dev-user'] || '';
    const fulfill = (status: number, data: unknown) => route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data }),
    });

    if (path === `/api/activities/${randomActivityId}` && request.method() === 'GET') {
      await fulfill(200, randomActivity);
      return;
    }
    if (path === `/api/activities/${randomActivityId}/random-selection` && request.method() === 'GET') {
      const privateRecord = randomSelected ? {
        round: 1,
        cycle: 1,
        sequence: 1,
        user_ref: 'u_private_random_student',
        display_name: '学生一',
        selected_at: '2026-07-29T09:00:00Z',
      } : null;
      const studentRecord = privateRecord ? {
        round: 1,
        display_name: privateRecord.display_name,
        selected_at: privateRecord.selected_at,
        is_me: user === selectedUser,
      } : null;
      await fulfill(200, role === 'student'
        ? { activity_id: randomActivityId, kind: 'random_selection', round: randomSelected ? 1 : 0, latest: studentRecord, selection: studentRecord, can_select: false }
        : { activity_id: randomActivityId, kind: 'random_selection', round: randomSelected ? 1 : 0, latest: privateRecord, selection: privateRecord, history: privateRecord ? [privateRecord] : [], can_select: true });
      return;
    }
    if (path === `/api/teacher/activities/${randomActivityId}/random-select` && request.method() === 'POST') {
      expect(request.postDataJSON()).toEqual({});
      expect(headers['idempotency-key']).toMatch(/^activity-random-select:/);
      expect(headers['x-moodle-sesskey']).toBeTruthy();
      randomWrites += 1;
      randomSelected = true;
      await fulfill(201, {
        activity_id: randomActivityId,
        kind: 'random_selection',
        round: 1,
        latest: { round: 1, cycle: 1, sequence: 1, user_ref: 'u_private_random_student', display_name: '学生一', selected_at: '2026-07-29T09:00:00Z' },
        history: [{ round: 1, cycle: 1, sequence: 1, user_ref: 'u_private_random_student', display_name: '学生一', selected_at: '2026-07-29T09:00:00Z' }],
        can_select: true,
      });
      return;
    }
    if (path === '/api/teacher/classroom-roster' && request.method() === 'GET') {
      await fulfill(200, { configured: true, items: [{ user_ref: 'u_1', display_name: '学生一' }, { user_ref: 'u_2', display_name: '学生二' }, { user_ref: 'u_3', display_name: '学生三' }] });
      return;
    }
    if (path === `/api/activities/${groupActivityId}` && request.method() === 'GET') {
      await fulfill(200, groupActivity(role));
      return;
    }
    if (path === `/api/activities/${groupActivityId}/groups` && request.method() === 'GET') {
      if (!groupsGenerated) {
        await fulfill(200, role === 'student'
          ? { activity_id: groupActivityId, kind: 'group_task', revision: null, my_group: null, can_generate: false }
          : { activity_id: groupActivityId, kind: 'group_task', revision: null, groups: [], can_generate: true });
        return;
      }
      await fulfill(200, role === 'student'
        ? { activity_id: groupActivityId, kind: 'group_task', revision: 1, my_group: { id: 'alpha', name: '甲组', members: [{ display_name: '学生一', is_me: true }, { display_name: '学生三', is_me: false }] }, can_generate: false }
        : { activity_id: groupActivityId, kind: 'group_task', revision: 1, groups: [{ id: 'alpha', name: '甲组', members: [{ user_ref: 'u_1', display_name: '学生一' }, { user_ref: 'u_3', display_name: '学生三' }] }, { id: 'beta', name: '乙组', members: [{ user_ref: 'u_2', display_name: '学生二' }] }], can_generate: true });
      return;
    }
    if (path === `/api/teacher/activities/${groupActivityId}/groups/generate` && request.method() === 'POST') {
      expect(request.postDataJSON()).toEqual({});
      expect(headers['idempotency-key']).toMatch(/^activity-groups-generate:/);
      expect(headers['x-moodle-sesskey']).toBeTruthy();
      groupWrites += 1;
      groupsGenerated = true;
      await fulfill(201, { activity_id: groupActivityId, kind: 'group_task', revision: 1, groups: [{ id: 'alpha', name: '甲组', members: [{ user_ref: 'u_1', display_name: '学生一' }, { user_ref: 'u_3', display_name: '学生三' }] }, { id: 'beta', name: '乙组', members: [{ user_ref: 'u_2', display_name: '学生二' }] }], can_generate: true });
      return;
    }
    await route.continue();
  });

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': 'playwright-classroom-teacher' });
  await page.goto(`activities/${randomActivityId}`);
  await page.getByRole('button', { name: '抽取一名学生' }).click({ force: true });
  await expect(page.getByText('第 1 轮抽取已确认：学生一')).toBeVisible();
  expect(randomWrites).toBe(1);
  await expect(page.locator('body')).not.toContainText('u_private_random_student');

  const studentPage = await context.newPage();
  await studentPage.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': selectedUser });
  await studentPage.goto(`activities/${randomActivityId}`);
  await expect(studentPage.getByText('本次抽中的是你')).toBeVisible();
  await expect(studentPage.locator('body')).not.toContainText('u_private_random_student');

  await page.goto(`activities/${groupActivityId}`);
  await page.getByRole('button', { name: '生成分组' }).click({ force: true });
  await expect(page.getByText('第 1 版分组已确认。')).toBeVisible();
  await expect(page.getByText('Revision 1')).toBeVisible();
  expect(groupWrites).toBe(1);

  await studentPage.goto(`activities/${groupActivityId}`);
  await expect(studentPage.getByText('甲组')).toBeVisible();
  await expect(studentPage.getByText('本人')).toBeVisible();
  await expect(studentPage.getByText('乙组')).toHaveCount(0);
  await expect(studentPage.locator('body')).not.toContainText('u_1');
  await expect(studentPage.getByRole('button', { name: /生成分组|重新分组/ })).toHaveCount(0);
  await studentPage.close();
});

test('teacher can publish close and reopen an activity while student attempts stay bounded', async ({ page }) => {
  const suffix = Date.now();
  const title = `Playwright 生命周期活动 ${suffix}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-activity-lifecycle-teacher-${suffix}` });
  await page.goto('teacher/activities');
  await page.getByLabel('活动标题').fill(title);
  await page.getByLabel('活动说明').fill('验证课堂活动发布、关闭、重开和两次提交。');
  await page.getByLabel('活动选项').fill('第一次选择\n第二次选择');
  await page.getByLabel('活动允许次数').fill('2');
  await page.getByRole('button', { name: '保存活动草稿' }).click({ force: true });
  let row = page.locator('.teacher-table-row').filter({ hasText: title });
  await expect(row).toContainText('草稿');
  await row.getByRole('button', { name: '发布', exact: true }).click({ force: true });
  await expect(page.getByText('课堂活动已发布。')).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-activity-lifecycle-student-${suffix}` });
  await page.goto('activities');
  await page.getByRole('button', { name: new RegExp(title) }).click({ force: true });
  const activityUrl = page.url();
  await expect(page.getByText('提交后可见')).toBeVisible();
  await page.getByLabel('第一次选择').check({ force: true });
  await page.getByRole('button', { name: '提交活动' }).click({ force: true });
  await expect(page.getByRole('button', { name: '再次提交（2/2）' })).toBeVisible();
  await page.getByLabel('第二次选择').check({ force: true });
  await page.getByRole('button', { name: '再次提交（2/2）' }).click({ force: true });
  await expect(page.getByRole('button', { name: '已提交' })).toBeDisabled();
  await expect(page.getByText('1 人参与')).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-activity-lifecycle-teacher-${suffix}` });
  await page.goto('teacher/activities');
  row = page.locator('.teacher-table-row').filter({ hasText: title });
  await row.getByRole('button', { name: '关闭', exact: true }).click({ force: true });
  await expect(page.getByText('课堂活动已关闭，学生不能继续提交。')).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-activity-lifecycle-student-${suffix}` });
  await page.goto(activityUrl);
  await expect(page.getByRole('button', { name: '活动已结束' })).toBeDisabled();
  await expect(page.getByText('1 人参与')).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-activity-lifecycle-teacher-${suffix}` });
  await page.goto('teacher/activities');
  row = page.locator('.teacher-table-row').filter({ hasText: title });
  await row.getByRole('button', { name: '重新开放', exact: true }).click({ force: true });
  await expect(page.getByText('课堂活动已重新开放。')).toBeVisible();

  await page.goto('courses');
  await page.goto('teacher/activities');
  row = page.locator('.teacher-table-row').filter({ hasText: title });
  await row.getByRole('button', { name: '关闭', exact: true }).click({ force: true });
  await expect(page.getByText('课堂活动已关闭，学生不能继续提交。')).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-activity-lifecycle-student-${suffix}` });
  await page.goto(activityUrl);
  await expect(page.getByRole('button', { name: '活动已结束' })).toBeDisabled();
});

test('student can submit a poll and see the aggregate result after refresh', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-activity-${Date.now()}` });
  await page.goto('activities');
  await expect(page.getByRole('heading', { name: '课堂活动' })).toBeVisible();
  await page.getByRole('button', { name: /储能系统并网控制重点/ }).click({ force: true });
  await expect(page.getByRole('heading', { name: '储能系统并网控制重点' })).toBeVisible();
  await page.getByLabel('功率平衡').check({ force: true });
  await page.getByRole('button', { name: '提交活动' }).click({ force: true });
  await expect(page.getByText('提交成功，最新答案已保存并计入汇总。')).toBeVisible();
  await expect(page.getByRole('button', { name: '已提交' })).toBeVisible();
  await expect(page.getByText(/人参与/)).toBeVisible();
  await page.reload();
  await expect(page.getByRole('button', { name: '已提交' })).toBeVisible();
  await expect(page.getByRole('button', { name: '已提交' })).toBeDisabled();
});

test('student can start, autosave and submit a timed exam through the server contract', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-exam-${Date.now()}` });
  const now = new Date().toISOString();
  const closeAt = new Date(Date.now() + 600_000).toISOString();
  let draftVersion = 0;
  let submitted = false;
  let savedAnswers: Record<string, unknown> = {};
  const exam = {
    id: 'ui-exam-1', title: 'BUILD-050 限时考试', status: 'open', availability: 'open',
    open_at: now, close_at: closeAt, duration_seconds: 600, allow_attempts: 1,
    question_count: 1, question_ids: ['ui-exam-q-1'], my_attempts: [], my_submissions: [],
  };
  const detail = {
    ...exam,
    questions: [{ id: 'ui-exam-q-1', prompt: '储能系统参与电网运行时首先需要满足哪项约束？', question_type: 'single_choice', options: ['功率平衡', '取消保护'], max_score: 10 }],
  };
  await page.route('**/api/student/exams', async (route) => route.fulfill({
    status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [exam] } }),
  }));
  await page.route('**/api/student/exams/ui-exam-1', async (route) => route.fulfill({
    status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { ...detail, my_attempts: [], my_submissions: [] } }),
  }));
  await page.route('**/api/student/exams/ui-exam-1/start', async (route) => route.fulfill({
    status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
      ...detail,
      attempt: { attempt: 1, started_at: now, deadline_at: closeAt, status: 'in_progress', submitted_at: null },
      server_now: now,
    } }),
  }));
  await page.route('**/api/student/exams/ui-exam-1/draft**', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { exam_id: 'ui-exam-1', attempt: 1, answers: savedAnswers, version: draftVersion, has_saved_draft: draftVersion > 0 } }) });
      return;
    }
    const body = route.request().postDataJSON() as { answers?: Record<string, unknown> };
    savedAnswers = body.answers || {};
    draftVersion += 1;
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { exam_id: 'ui-exam-1', attempt: 1, answers: savedAnswers, version: draftVersion, has_saved_draft: true } }) });
  });
  await page.route('**/api/student/exams/ui-exam-1/submit', async (route) => {
    submitted = true;
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
      id: 'ui-exam-submission-1', exam_id: 'ui-exam-1', attempt: 1, submitted_at: now, status: 'submitted', score: 10, max_score: 10, needs_review: false,
    } }) });
  });

  await page.goto('exams');
  await expect(page.getByRole('heading', { name: '限时考试' })).toBeVisible();
  const examRow = page.locator('.task-table-row').filter({ hasText: 'BUILD-050 限时考试' });
  await expect(examRow).toBeVisible();
  await examRow.getByRole('button', { name: '进入考试' }).click({ force: true });
  await expect(page.getByRole('heading', { name: 'BUILD-050 限时考试' })).toBeVisible();
  await page.getByLabel('功率平衡').check({ force: true });
  await expect(page.getByText('答案已保存')).toBeVisible({ timeout: 5_000 });
  await page.getByRole('button', { name: '提交考试' }).click({ force: true });
  await expect(page.getByText('提交成功')).toBeVisible();
  await expect(page.getByText('成绩：10 / 10')).toBeVisible();
  expect(submitted).toBe(true);
  expect(savedAnswers['ui-exam-q-1']).toBe('功率平衡');
});

test('teacher can create a question, publish an assignment and open the gradebook', async ({ page }) => {
  const suffix = Date.now();
  const prompt = `BUILD-070 题目 ${suffix}`;
  const assignment = `BUILD-070 作业 ${suffix}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-build070-${suffix}` });
  await page.goto('teacher/questions');
  await expect(page.getByRole('heading', { name: '题库管理' })).toBeVisible();
  await page.getByLabel('题干').fill(prompt);
  await page.getByLabel('正确答案').fill('功率平衡');
  await page.getByRole('button', { name: '保存为草稿' }).click({ force: true });
  await expect(page.getByText('题目已保存为草稿，可在列表中发布。')).toBeVisible();
  const questionRow = page.locator('.teacher-table-row').filter({ hasText: prompt });
  await expect(questionRow).toBeVisible();
  await questionRow.getByRole('button', { name: '发布' }).click({ force: true });
  await expect(questionRow.getByText('已发布')).toBeVisible();

  await page.goto('teacher/assignments');
  await expect(page.getByRole('heading', { name: '作业发布' })).toBeVisible();
  await page.locator('.selection-row').filter({ hasText: prompt }).locator('input').check({ force: true });
  await page.getByLabel('作业标题').fill(assignment);
  await page.getByRole('button', { name: '保存作业草稿' }).click({ force: true });
  await expect(page.getByText('作业已保存为草稿。')).toBeVisible();
  const assignmentRow = page.locator('.teacher-table-row').filter({ hasText: assignment });
  await expect(assignmentRow).toBeVisible();
  await assignmentRow.getByRole('button', { name: '发布' }).click({ force: true });
  await expect(assignmentRow.getByText('已发布')).toBeVisible();

  await page.goto('teacher/gradebook');
  await expect(page.getByRole('heading', { name: '成绩册与学情' })).toBeVisible();
  await expect(page.locator('.teacher-table-row').filter({ hasText: assignment })).toBeVisible();
});

test('teacher can create, publish, withdraw and archive a timed exam', async ({ page }) => {
  const suffix = Date.now();
  const prompt = `BUILD-050 考试题目 ${suffix}`;
  const title = `BUILD-050 教师考试 ${suffix}`;
  const inputDate = (offsetMs: number) => {
    const date = new Date(Date.now() + offsetMs);
    const pad = (value: number) => String(value).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  };
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-build050-exam-${suffix}` });
  await page.goto('teacher/questions');
  await expect(page.getByRole('heading', { name: '题库管理' })).toBeVisible();
  await page.getByLabel('题干').fill(prompt);
  await page.getByLabel('正确答案').fill('功率平衡');
  await page.getByRole('button', { name: '保存为草稿' }).click({ force: true });
  await expect(page.getByText('题目已保存为草稿，可在列表中发布。')).toBeVisible();
  const questionRow = page.locator('.teacher-table-row').filter({ hasText: prompt });
  await questionRow.getByRole('button', { name: '发布' }).click({ force: true });
  await expect(questionRow.getByText('已发布')).toBeVisible();

  await page.goto('teacher/exams');
  await expect(page.getByRole('heading', { name: '考试管理' })).toBeVisible();
  await page.locator('.selection-row').filter({ hasText: prompt }).locator('input').check({ force: true });
  await page.getByLabel('考试标题').fill(title);
  await page.getByLabel('考试开放时间').fill(inputDate(60 * 60 * 1000));
  await page.getByLabel('考试结束时间').fill(inputDate(3 * 60 * 60 * 1000));
  await page.getByLabel('考试时长').fill('45');
  await page.getByLabel('考试允许次数').fill('2');
  await page.getByRole('button', { name: '保存考试草稿' }).click({ force: true });
  await expect(page.getByRole('alert')).toContainText('考试已保存为草稿');
  const examRow = page.locator('.teacher-table-row').filter({ hasText: title });
  await expect(examRow).toBeVisible();
  await examRow.getByRole('button', { name: '发布' }).click({ force: true });
  await expect(examRow.getByText('已发布')).toBeVisible();
  await page.reload();
  const refreshedRow = page.locator('.teacher-table-row').filter({ hasText: title });
  await expect(refreshedRow.getByText('已发布')).toBeVisible();
  await refreshedRow.getByRole('button', { name: '撤回' }).click({ force: true });
  await expect(refreshedRow.getByText('已撤回')).toBeVisible();
  await refreshedRow.getByRole('button', { name: '归档' }).click({ force: true });
  await expect(refreshedRow.getByText('已归档')).toBeVisible();
});

test('teacher can upload, replace, publish and archive a resource revision', async ({ page }) => {
  const suffix = Date.now();
  const title = `STAFF-010 资源 ${suffix}`;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-staff010-${suffix}` });
  await page.goto('teacher/resources');
  await expect(page.getByRole('heading', { name: '课程资料管理' })).toBeVisible();
  await page.getByLabel('资料标题').fill(title);
  await page.getByLabel('来源引用').fill('STAFF-010 浏览器夹具');
  await page.getByLabel('课程资料文件').setInputFiles({ name: 'staff010.md', mimeType: 'text/markdown', buffer: Buffer.from('# STAFF-010 fixture') });
  await page.getByRole('button', { name: '创建资料草稿' }).click({ force: true });
  await expect(page.getByText('资源已上传并保存为草稿。')).toBeVisible();
  let row = page.locator('.teacher-table-row').filter({ hasText: title });
  await expect(row).toContainText('v1');
  await row.getByRole('button', { name: '发布' }).click({ force: true });
  await expect(row.getByText('已发布')).toBeVisible();
  await row.locator('input[type="file"]').setInputFiles({ name: 'staff010-v2.md', mimeType: 'text/markdown', buffer: Buffer.from('# STAFF-010 replacement') });
  await expect(page.getByText('新修订已上传，资源回到草稿状态。')).toBeVisible();
  row = page.locator('.teacher-table-row').filter({ hasText: title });
  await expect(row).toContainText('v2');
  await row.getByRole('button', { name: '发布' }).click({ force: true });
  await expect(row.getByText('已发布')).toBeVisible();
  await row.getByRole('button', { name: '归档' }).click({ force: true });
  await expect(row.getByText('已归档')).toBeVisible();
});

test('admin can create, test and publish a knowledge-base version', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'admin', 'x-dev-user': 'playwright-build080-admin' });
  let version: Build080MockVersion | null = null;
  const files: Build080MockFile[] = [];
  const hits: Build080MockHit[] = [];
  await page.route('**/api/admin/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { adapter: 'healthy', workflow_configured: false, mock_workflow: true, published_kb: null, backup: { managed_by: 'host-cron', status: 'verify_on_server' } } }) }));
  await page.route('**/api/admin/backup/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { managed_by: 'host-cron', verification: 'verify_on_server', restore_rehearsal: 'run_on_server', secrets_excluded: true, status: 'operator_action_required' } }) }));
  await page.route('**/api/admin/audit-log**', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [], page: 1, page_size: 50, total: 0 } }) }));
  await page.route('**/api/knowledge-base/versions', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: version ? [version] : [] } }) });
      return;
    }
    version = { id: 'kb-build080-1', version_name: 'BUILD-080 v1', status: 'draft', manifest_sha256: 'server-manifest-hash', workflow_id: 'workflow-fixture-v1', source_count: 0, hit_status: 'not_tested', created_by: 'u_admin' };
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: version }) });
  });
  await page.route('**/api/knowledge-base/versions/*/files**', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: files } }) });
      return;
    }
    files.push({ id: 'kb-file-1', version_id: version.id, filename: 'notes.md', sha256: 'file-hash', size_bytes: 12, status: 'accepted', created_at: '2026-07-25' });
    version.status = 'processing';
    version.source_count = 1;
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: files[files.length - 1] }) });
  });
  await page.route('**/api/knowledge-base/versions/*/hit-tests', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: hits, required: ['qa-001', 'qa-002', 'qa-003'] } }) });
      return;
    }
    const body = route.request().postDataJSON() as { case_id: string };
    hits.push({ id: 'hit-' + body.case_id, version_id: version.id, case_id: body.case_id, question: body.case_id, expected_chapter: '第3章', actual_sources: [{ file: 'fixture.pdf', page: 1 }], status: 'passed', request_id: 'request-' + body.case_id, actor_uid: 'u_admin', created_at: '2026-07-25' });
    version.hit_status = 'passed';
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: hits[hits.length - 1] }) });
  });
  await page.route('**/api/knowledge-base/versions/*/status', async (route) => {
    const body = route.request().postDataJSON() as { status: string };
    version.status = body.status;
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: version }) });
  });
  await page.goto('admin/knowledge-bases');
  await expect(page.getByRole('heading', { name: '平台运维与知识库' })).toBeVisible();
  await page.getByLabel('知识库版本名称').fill('BUILD-080 v1');
  await page.getByLabel('Workflow 标识').fill('workflow-fixture-v1');
  await page.getByRole('button', { name: '创建草稿' }).click({ force: true });
  await expect(page.getByText('BUILD-080 v1').first()).toBeVisible();
  await page.locator('#admin-kb-file').setInputFiles({ name: 'notes.md', mimeType: 'text/markdown', buffer: Buffer.from('# fixture') });
  await expect(page.getByText('文件已接收，版本进入处理中。')).toBeVisible();
  for (const caseId of ['qa-001', 'qa-002', 'qa-003']) {
    const hitRow = page.locator('.admin-hit-row').filter({ hasText: caseId });
    await hitRow.getByRole('button', { name: '执行测试' }).click({ force: true });
    await expect(hitRow.getByText('passed')).toBeVisible();
  }
  await expect(page.getByText('3 / 3 已通过')).toBeVisible();
  await page.getByRole('button', { name: '通过测试门槛' }).click({ force: true });
  await expect(page.getByRole('button', { name: '发布版本' })).toBeVisible();
  await page.getByRole('button', { name: '发布版本' }).click({ force: true });
  await expect(page.locator('.admin-detail-panel').getByText('已发布')).toBeVisible();
});

test('admin user directory supports scope, search, role filtering and pagination', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'admin', 'x-dev-user': 'playwright-build080-directory' });
  const userRequests: string[] = [];
  await page.route('**/api/admin/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { adapter: 'healthy', workflow_configured: false, mock_workflow: true, published_kb: null, backup: { managed_by: 'host-cron', status: 'verify_on_server' } } }) }));
  await page.route('**/api/admin/backup/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { managed_by: 'host-cron', verification: 'verify_on_server', restore_rehearsal: 'run_on_server', secrets_excluded: true, status: 'operator_action_required' } }) }));
  await page.route('**/api/admin/audit-log**', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [], page: 1, page_size: 50, total: 0 } }) }));
  await page.route('**/api/knowledge-base/versions*', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [] } }) }));
  await page.route('**/api/admin/users*', async (route) => {
    const url = new URL(route.request().url());
    userRequests.push(url.href);
    const query = url.searchParams.get('query') || '';
    const role = url.searchParams.get('role') || '';
    const currentPage = Number(url.searchParams.get('page') || '1');
    let data: { items: Array<Record<string, unknown>>; page: number; page_size: number; total: number; source: string; configured: boolean; message?: string };
    if (query === '未配置') {
      data = { items: [], page: 1, page_size: 20, total: 0, source: 'not_configured', configured: false, message: 'Moodle 管理目录尚未配置' };
    } else if (query === '教师' || role === 'teacher') {
      data = { items: [{ id: 'teacher-c1', display_name: '课程一教师', role: 'teacher', course_id: 1, status: 'active', last_accessed_at: null }], page: 1, page_size: 20, total: 1, source: 'mock_fixture', configured: true };
    } else if (role === 'student') {
      data = { items: [{ id: 'student-c1', display_name: '课程一学生', role: 'student', course_id: 1, status: 'active', last_accessed_at: null }], page: 1, page_size: 20, total: 1, source: 'mock_fixture', configured: true };
    } else if (currentPage === 2) {
      data = { items: [{ id: 'student-c1-21', display_name: '课程一学生 21', role: 'student', course_id: 1, status: 'active', last_accessed_at: null }], page: 2, page_size: 20, total: 21, source: 'mock_fixture', configured: true };
    } else {
      data = { items: [{ id: 'student-c1', display_name: '课程一学生', role: 'student', course_id: 1, status: 'active', last_accessed_at: null }, { id: 'teacher-c1', display_name: '课程一教师', role: 'teacher', course_id: 1, status: 'active', last_accessed_at: null }], page: 1, page_size: 20, total: 21, source: 'mock_fixture', configured: true };
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data }) });
  });

  await page.goto('admin/users');
  await expect(page.getByRole('heading', { name: '用户与角色' })).toBeVisible();
  await expect(page.getByText('来源：隔离夹具')).toBeVisible();
  await expect(page.getByText('课程一学生')).toBeVisible();
  await expect(page.getByText('第 1 / 2 页 · 共 21 条')).toBeVisible();
  await page.getByRole('button', { name: '下一页' }).click({ force: true });
  await expect(page.getByText('课程一学生 21')).toBeVisible();
  await expect(page.getByText('课程一学生', { exact: true })).toHaveCount(0);

  await page.getByLabel('搜索用户').fill('教师');
  await expect(page.getByText('课程一教师')).toBeVisible();
  await page.getByLabel('搜索用户').fill('');
  await page.getByLabel('筛选用户角色').selectOption('student');
  await expect(page.getByText('课程一学生')).toBeVisible();
  await expect.poll(() => userRequests.some((request) => request.includes('role=student'))).toBe(true);

  await page.getByLabel('搜索用户').fill('未配置');
  await expect(page.getByText('Moodle 管理目录尚未配置，未显示伪造用户。')).toBeVisible();
  await expect(page.locator('.directory-table-row')).toHaveCount(0);
});

test('admin course directory renders the current course and its class summary', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'admin', 'x-dev-user': 'playwright-build080-course-directory' });
  await page.route('**/api/admin/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { adapter: 'healthy', workflow_configured: false, mock_workflow: true, published_kb: null, backup: { managed_by: 'host-cron', status: 'verify_on_server' } } }) }));
  await page.route('**/api/admin/backup/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { managed_by: 'host-cron', verification: 'verify_on_server', restore_rehearsal: 'run_on_server', secrets_excluded: true, status: 'operator_action_required' } }) }));
  await page.route('**/api/admin/audit-log**', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [], page: 1, page_size: 50, total: 0 } }) }));
  await page.route('**/api/knowledge-base/versions*', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [] } }) }));
  await page.route('**/api/admin/courses*', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [{ id: 1, name: '电力系统储能技术', teacher: '课程教师', class_name: '储能技术课程班', status: 'active', progress: 42, chapter_count: 6, resource_count: 20, enrollment_count: 36, active_users: 31 }], page: 1, page_size: 20, total: 1, source: 'mock_fixture', configured: true } }) }));

  await page.goto('admin/courses');
  await expect(page.getByRole('heading', { name: '课程与班级' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '电力系统储能技术', level: 3 })).toBeVisible();
  await expect(page.getByText('课程教师 · 储能技术课程班')).toBeVisible();
  await expect(page.getByText('36')).toBeVisible();
  await page.getByLabel('搜索课程', { exact: true }).fill('储能');
  await expect(page.getByRole('heading', { name: '电力系统储能技术', level: 3 })).toBeVisible();
});

test('admin moderation queue filters content and records an approval decision', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'admin', 'x-dev-user': 'playwright-build080-moderation' });
  let approved = false;
  await page.route('**/api/admin/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { adapter: 'healthy', workflow_configured: false, mock_workflow: true, published_kb: null, backup: { managed_by: 'host-cron', status: 'verify_on_server' } } }) }));
  await page.route('**/api/admin/backup/status', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { managed_by: 'host-cron', verification: 'verify_on_server', restore_rehearsal: 'run_on_server', secrets_excluded: true, status: 'operator_action_required' } }) }));
  await page.route('**/api/admin/audit-log**', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [], page: 1, page_size: 50, total: 0 } }) }));
  await page.route('**/api/knowledge-base/versions*', async (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items: [] } }) }));
  await page.route('**/api/admin/moderation*', async (route) => {
    if (route.request().method() === 'PATCH') {
      approved = true;
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { id: 'topic-pending', content_type: 'topic', topic_id: 'topic-pending', reply_id: null, decision: 'approve', status: 'open' } }) });
      return;
    }
    const url = new URL(route.request().url());
    const contentType = url.searchParams.get('content_type') || '';
    const topic = { id: 'topic-pending', content_type: 'topic', topic_id: 'topic-pending', reply_id: null, title: '待审核主题', body: '请核对该主题。', status: 'pending_review', author_ref: 'u_topic', created_at: '2026-07-26', updated_at: '2026-07-26' };
    const reply = { id: 'reply-pending', content_type: 'reply', topic_id: 'topic-pending', reply_id: 'reply-pending', title: '待审核主题', body: '请核对该回复。', status: 'pending_review', author_ref: 'u_reply', created_at: '2026-07-26', updated_at: '2026-07-26' };
    const items = approved ? [reply] : contentType === 'reply' ? [reply] : [topic, reply];
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { items, page: 1, page_size: 20, total: items.length } }) });
  });
  await page.route('**/api/admin/moderation/**', async (route) => {
    if (route.request().method() !== 'PATCH') {
      await route.fallback();
      return;
    }
    approved = true;
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: { id: 'topic-pending', content_type: 'topic', topic_id: 'topic-pending', reply_id: null, decision: 'approve', status: 'open' } }) });
  });

  await page.goto('admin/moderation');
  await expect(page.getByRole('heading', { name: '内容审核' })).toBeVisible();
  await expect(page.getByText('待审核主题')).toHaveCount(2);
  await page.getByLabel('筛选审核类型').selectOption('reply');
  await expect(page.getByText('请核对该回复。')).toBeVisible();
  await expect(page.getByText('请核对该主题。')).toHaveCount(0);
  await page.getByLabel('筛选审核类型').selectOption('');
  await page.getByLabel('审核决定原因').fill('管理员核对通过');
  await page.getByRole('button', { name: '批准内容 topic-pending' }).click({ force: true });
  await expect(page.getByText('内容已审核通过。')).toBeVisible();
  await expect(page.getByText('请核对该回复。')).toBeVisible();
});

test('student carries a resource context into Agent and can open a verified source', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-build090-context-${Date.now()}` });
  await page.goto('assistant');
  const resourcePayload = await page.evaluate(async () => {
    const response = await fetch('/api/textbook/resources');
    return await response.json() as { data?: { items?: Array<{ id: string; source_file?: string; sourceFile?: string }> } };
  });
  const resource = resourcePayload.data?.items?.find((item) => (item.source_file || item.sourceFile) === '3.4 储能变流器拓扑及并网控制.pdf');
  expect(resource).toBeTruthy();
  const resourceId = resource?.id || '';
  await page.route('**/api/course-agent/chat', async (route) => {
    const body = [
      'event: token\ndata: {"text":"上下文回答："}\n\n',
      'event: token\ndata: {"text":"请核对教材。"}\n\n',
      `event: source\ndata: {"source_id":"source-build090","file":"3.4 储能变流器拓扑及并网控制.pdf","chapter":"第3章 电力储能系统的组成及工作原理","page":2,"resource_id":"${resourceId}","version":"local-manifest","status":"verified"}\n\n`,
      'event: done\ndata: {"request_id":"build090-context","reason":"stop"}\n\n',
    ].join('');
    await route.fulfill({ status: 200, contentType: 'text/event-stream', body });
  });
  await page.goto(`assistant?resource_id=${encodeURIComponent(resourceId)}&page=2&chapter_id=3`);
  await expect(page.getByText(/第 2 页/)).toBeVisible();
  await page.getByLabel('输入课程问题').fill('这个页面的并网控制重点是什么？');
  await page.getByRole('button', { name: '发送问题' }).click({ force: true });
  await expect(page.getByText('上下文回答：请核对教材。')).toBeVisible();
  const source = page.getByRole('button', { name: /3.4 储能变流器拓扑及并网控制/ });
  await expect(source).toBeVisible();
  await source.click({ force: true });
  await expect(page).toHaveURL(new RegExp(`resources/${resourceId}\\?page=2`));
});

test('student can start, continue and end a scenario through the Agent panel', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-build090-scenario-${Date.now()}` });
  await page.goto('assistant');
  await page.getByRole('tab', { name: '情景演练' }).click({ force: true });
  await page.getByLabel('输入课程问题').fill('我先按峰谷电价安排储能充放电。');
  await page.getByRole('button', { name: '发送问题' }).click({ force: true });
  await expect(page.getByText('储能电站并网调度')).toBeVisible();
  await expect(page.getByRole('button', { name: '结束演练' })).toBeVisible();
  await expect(page.getByText(/已收到问题/)).toBeVisible();
  await page.getByRole('button', { name: '结束演练' }).click({ force: true });
  await expect(page.getByText(/AI 生成内容，请结合课程来源复核/)).toBeVisible();
});

test('Agent error state can retry once and then render the recovered answer', async ({ page }) => {
  let calls = 0;
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-build090-retry-${Date.now()}` });
  await page.route('**/api/course-agent/chat', async (route) => {
    calls += 1;
    if (calls === 1) {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: 'event: error\ndata: {"code":"upstream_disconnected","message":"上游连接中断，请重试"}\n\n',
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: 'event: token\ndata: {"text":"重试后回答已恢复。"}\n\n' + 'event: done\ndata: {"request_id":"build090-retry","reason":"stop"}\n\n',
    });
  });
  await page.goto('assistant');
  await page.getByLabel('输入课程问题').fill('请重试这个问题');
  await page.getByRole('button', { name: '发送问题' }).click({ force: true });
  await expect(page.getByText('上游连接中断，请重试')).toBeVisible();
  await page.getByRole('button', { name: '重试' }).click({ force: true });
  await expect(page.getByText('重试后回答已恢复。')).toBeVisible();
  expect(calls).toBe(2);
});

test('Agent generation can be cancelled without rendering a late answer', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-build090-cancel-${Date.now()}` });
  await page.route('**/api/course-agent/chat', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: 'event: token\ndata: {"text":"不应在取消后显示。"}\n\n' + 'event: done\ndata: {"request_id":"build090-cancel","reason":"stop"}\n\n',
    });
  });
  await page.goto('assistant');
  await page.getByLabel('输入课程问题').fill('请取消这个问题');
  await page.getByRole('button', { name: '发送问题' }).click({ force: true });
  await page.getByRole('button', { name: '取消生成' }).click({ force: true });
  await expect(page.getByText('生成已取消。')).toBeVisible();
  await page.waitForTimeout(1200);
  await expect(page.getByText('不应在取消后显示。')).toHaveCount(0);
});

test('teacher can generate a question draft and review it in the question bank', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-build090-draft-${Date.now()}` });
  await page.route('**/api/course-agent/chat', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: 'event: token\ndata: {"text":"说明储能变流器并网控制中功率平衡的关键作用。"}\n\n' + 'event: done\ndata: {"request_id":"build090-draft","reason":"stop"}\n\n',
    });
  });
  await page.goto('assistant');
  await page.getByRole('tab', { name: '出题草稿' }).click({ force: true });
  await page.getByLabel('输入课程问题').fill('生成一道第 3 章单选题');
  await page.getByRole('button', { name: '发送问题' }).click({ force: true });
  await expect(page.getByText('说明储能变流器并网控制中功率平衡的关键作用。')).toBeVisible();
  await page.getByRole('button', { name: '带到题库编辑' }).click({ force: true });
  await expect(page).toHaveURL(/teacher\/questions\?draft=/);
  await expect(page.getByLabel('题干')).toHaveValue('说明储能变流器并网控制中功率平衡的关键作用。');
});

test('student can browse the knowledge graph and open a node detail', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-graph-${Date.now()}` });
  await page.goto('knowledge-graph');
  await expect(page.getByRole('heading', { name: '知识点与先修关系' })).toBeVisible();
  await expect(page.getByTestId('knowledge-graph-canvas')).toBeVisible();
  await expect(page.locator('.react-flow__edge')).toHaveCount(17, { timeout: 30_000 });
  const flowNode = page.locator('.react-flow__node').first();
  const dragHandle = flowNode.locator('.graph-node-drag-handle');
  await dragHandle.scrollIntoViewIfNeeded();
  const beforeDrag = await flowNode.boundingBox();
  const handleBox = await dragHandle.boundingBox();
  expect(beforeDrag).not.toBeNull();
  expect(handleBox).not.toBeNull();
  await page.mouse.move(handleBox!.x + handleBox!.width / 2, handleBox!.y + handleBox!.height / 2);
  await page.mouse.down();
  await page.mouse.move(handleBox!.x + handleBox!.width / 2 + 60, handleBox!.y + handleBox!.height / 2 + 40, { steps: 8 });
  await page.mouse.up();
  const afterDrag = await flowNode.boundingBox();
  expect(afterDrag).not.toBeNull();
  expect(Math.abs(afterDrag!.x - beforeDrag!.x) + Math.abs(afterDrag!.y - beforeDrag!.y)).toBeGreaterThan(20);
  const viewport = page.locator('.react-flow__viewport');
  const beforeZoom = await viewport.getAttribute('style');
  await page.locator('.react-flow__controls-zoomin').click();
  await expect.poll(() => viewport.getAttribute('style')).not.toBe(beforeZoom);
  await page.locator('.react-flow__controls-fitview').click();
  const node = page.getByRole('button', { name: /3\.4 储能变流器拓扑及并网控制/ });
  await expect(node).toBeVisible();
  await node.focus();
  await node.press('Enter');
  await expect(page.getByRole('heading', { name: '3.4 储能变流器拓扑及并网控制' })).toBeVisible();
  await expect(page.getByRole('heading', { name: '相邻知识点' })).toBeVisible();
  await page.getByRole('button', { name: '列表' }).click();
  await expect(page.locator('.graph-node-grid .graph-node')).toHaveCount(20);
  await page.getByRole('button', { name: '关系图' }).click();
  await expect(page.getByTestId('knowledge-graph-canvas')).toBeVisible();
});

test('knowledge graph URL filter and retry issue fresh snapshot requests', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-graph-filter-${Date.now()}` });
  let graphAttempts = 0;
  await page.route('**/api/knowledge-graph/graph', async (route) => {
    graphAttempts += 1;
    if (graphAttempts <= 2) {
      await route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ status: 'error', data: null, error: { code: 'graph_unavailable', message: '图谱暂时不可用' } }) });
      return;
    }
    await route.continue();
  });
  await page.goto('knowledge-graph?q=3.4');
  await expect(page.getByLabel('搜索知识点')).toHaveValue('3.4');
  await expect(page.getByText('图谱暂时不可用')).toBeVisible();
  await page.getByRole('button', { name: '重新加载' }).click({ force: true });
  await expect(page.getByTestId('knowledge-graph-canvas')).toBeVisible();
  await expect(page.locator('.react-flow__node')).toHaveCount(1);
  await expect(page.getByText('1 个节点 · 0 条关系')).toBeVisible();
  expect(graphAttempts).toBe(3);
});

test('student can calculate and inspect a prerequisite learning path', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-graph-path-${Date.now()}` });
  await page.goto('knowledge-graph');
  await expect(page.getByRole('heading', { name: '知识点与先修关系' })).toBeVisible();
  await page.getByLabel('起点知识点').selectOption('kp-3-1');
  await page.getByLabel('目标知识点').selectOption('kp-3-4');
  await page.getByRole('button', { name: '显示学习路径' }).click({ force: true });
  await expect(page.getByText('已找到 3 个知识点，路径深度 2。')).toBeVisible();
  await expect(page.locator('.graph-path-list li')).toHaveCount(3);
  await expect(page.locator('.graph-node.path-node')).toHaveCount(3);
  await expect(page.locator('.graph-flow-edge.path-edge')).toHaveCount(2, { timeout: 30_000 });
  await page.locator('.graph-path-list button').nth(1).click({ force: true });
  await expect(page.getByRole('heading', { name: '3.2 新型电力储能系统的组成' })).toBeVisible();
});

test('two student tabs surface a draft version conflict without overwriting the latest answer', async ({ page }) => {
  const context = page.context();
  const assignmentId = 'ui-assignment-multitab';
  const questionId = 'ui-q-multitab';
  const draftWrites: Array<{ base_version: number; answers: Record<string, unknown> }> = [];
  let serverAnswers: Record<string, unknown> = {};

  await context.route(`**/api/student/assignments/${assignmentId}/draft**`, async (route) => {
    const request = route.request();
    const body = request.postDataJSON() as { base_version?: number; answers?: Record<string, unknown> } | null;
    if (request.method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
        assignment_id: assignmentId, attempt: 1, answers: serverAnswers, version: draftWrites.length > 0 ? 1 : 0, has_saved_draft: draftWrites.length > 0,
      } }) });
      return;
    }
    if (request.method() === 'PUT') {
      const write = { base_version: Number(body?.base_version), answers: body?.answers || {} };
      draftWrites.push(write);
      if (draftWrites.length === 1) {
        serverAnswers = write.answers;
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
          assignment_id: assignmentId, attempt: 1, answers: serverAnswers, version: 1, has_saved_draft: true,
        } }) });
        return;
      }
      await route.fulfill({ status: 409, contentType: 'application/json', body: JSON.stringify({ status: 'error', request_id: 'multitab-conflict', error: {
        code: 'assignment_draft_conflict', message: '草稿版本冲突，请重新加载最新答案后再保存。', details: { current_version: 1 },
      } }) });
      return;
    }
    await route.continue();
  });

  await context.route(`**/api/student/assignments/${assignmentId}`, async (route) => {
    if (route.request().method() !== 'GET') {
      await route.continue();
      return;
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', data: {
      id: assignmentId, title: '多标签草稿冲突验收', status: 'published', due_at: '2026-07-28', question_ids: [questionId], allow_attempts: 1,
      questions: [{ id: questionId, prompt: '多标签答案不会互相覆盖吗？', question_type: 'single_choice', options: ['服务端版本保护', '直接覆盖'], max_score: 10 }], my_submissions: [],
    } }) });
  });

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-assessment-tab-a' });
  await page.goto(`tasks/${assignmentId}`);
  await expect(page.getByRole('heading', { name: '多标签草稿冲突验收' })).toBeVisible();
  const secondTab = await context.newPage();
  await secondTab.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': 'playwright-assessment-tab-b' });
  await secondTab.goto(`tasks/${assignmentId}`);
  await expect(secondTab.getByRole('heading', { name: '多标签草稿冲突验收' })).toBeVisible();

  await page.getByLabel('服务端版本保护').check({ force: true });
  await expect(page.getByText('草稿已保存')).toBeVisible();
  await secondTab.getByLabel('直接覆盖').check({ force: true });
  await expect(secondTab.getByText('版本冲突')).toBeVisible();

  expect(draftWrites).toHaveLength(2);
  expect(draftWrites.map((write) => write.base_version)).toEqual([0, 0]);
  expect(draftWrites[0]?.answers).toEqual({ [questionId]: '服务端版本保护' });
  expect(draftWrites[1]?.answers).toEqual({ [questionId]: '直接覆盖' });
  expect(serverAnswers).toEqual({ [questionId]: '服务端版本保护' });
  await secondTab.close();
});

test('unread notification badge refreshes via background polling and announces in live region', async ({ page }) => {
  const suffix = Date.now();
  let unreadCount = 0;
  await page.route('**/api/notifications*', async (route) => {
    const request = route.request();
    if (request.method() !== 'GET') {
      await route.continue();
      return;
    }
    const url = new URL(request.url());
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: {
        items: unreadCount > 0 ? [{
          id: `poll-notice-${suffix}`,
          audience: 'course_students',
          title: '实时播报验收通知',
          body: '轮询刷新未读数并播报。',
          created_by: 'teacher-fixture',
          created_at: '2026-08-06T12:00:00Z',
          is_read: false,
        }] : [],
        unread_count: unreadCount,
        page: 1,
        page_size: Number(url.searchParams.get('page_size') || 8),
        total: unreadCount,
        focus_found: false,
        focused_id: null,
      } }),
    });
  });
  await page.clock.install();
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-unread-poll-${suffix}` });
  await page.goto('/');
  await expect(page.getByRole('button', { name: '消息通知' })).toBeVisible();
  unreadCount = 3;
  await page.clock.fastForward(60_000);
  await expect(page.getByRole('button', { name: '消息通知，3 条未读' })).toBeVisible();
  await expect(page.locator('.notification-live-region')).toHaveText('您有 3 条新通知，当前共 3 条未读。');
});

test('resource list search filters cards, reports counts and clears the filter', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-resource-search-${Date.now()}` });
  await page.goto('resources');
  const inverterCard = page.locator('.resource-card').filter({ hasText: '储能变流器拓扑及并网控制' });
  const storageCard = page.locator('.resource-card').filter({ hasText: '电力储能系统的运行控制' });
  await expect(inverterCard).toBeVisible();
  await expect(storageCard).toBeVisible();
  await expect(page.locator('.resource-summary')).toContainText('份资料，当前显示');

  await page.getByRole('textbox', { name: '搜索资料' }).fill('变流器');
  await expect(inverterCard).toBeVisible();
  await expect(storageCard).toHaveCount(0);
  await expect(page.locator('.resource-summary')).toContainText('当前显示 1 份');

  await page.getByRole('button', { name: '清除筛选' }).click();
  await expect(storageCard).toBeVisible();
  await expect(page.locator('.resource-summary')).not.toContainText('当前显示 0 份');
});

test('search results support arrow-key navigation, Home/End and Enter activation', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-search-keys-${Date.now()}` });
  const items = [
    { id: 'chapter-1', kind: 'chapter', title: '键盘导航章节', summary: '课程章节', chapter_id: 1 },
    { id: 'res-1', kind: 'resource', title: '键盘导航资料', summary: '3.4 键盘导航资料.pdf · 第 3 章', chapter_id: 3 },
    { id: 'exam-1', kind: 'exam', title: '键盘导航考试', summary: '限时考试 · 截止 2026-08-02', chapter_id: null },
    { id: 'disc-1', kind: 'discussion', title: '键盘导航讨论', summary: '课程讨论', chapter_id: null },
  ];
  await page.route('**/api/search*', async (route) => {
    const url = new URL(route.request().url());
    const kind = url.searchParams.get('kind') || 'all';
    const visible = kind === 'all' ? items : items.filter((item) => item.kind === kind);
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: {
        course_id: 1,
        query: '键盘',
        kind,
        items: visible,
        counts: { course: 0, chapter: 1, resource: 1, assignment: 0, exam: 1, discussion: 1, knowledge: 0 },
        page: 1,
        page_size: 10,
        total: visible.length,
      } }),
    });
  });
  await page.goto('search?q=%E9%94%AE%E7%9B%98');
  await expect(page.getByRole('heading', { name: '搜索“键盘”' })).toBeVisible();
  const rows = page.locator('.search-result-row');
  await expect(rows).toHaveCount(4);
  await rows.first().focus();
  await expect(rows.nth(0)).toBeFocused();
  await page.keyboard.press('ArrowDown');
  await expect(rows.nth(1)).toBeFocused();
  await page.keyboard.press('ArrowDown');
  await expect(rows.nth(2)).toBeFocused();
  await page.keyboard.press('End');
  await expect(rows.nth(3)).toBeFocused();
  await page.keyboard.press('Home');
  await expect(rows.nth(0)).toBeFocused();
  await page.keyboard.press('ArrowUp');
  await expect(rows.nth(0)).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/\/courses\/1\/chapters\/1$/);
});

test('student and teacher data tables expose ARIA table semantics', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-table-student-${Date.now()}` });
  await page.goto('tasks');
  const taskTable = page.getByRole('table', { name: '任务列表' });
  await expect(taskTable).toBeVisible();
  await expect(taskTable.getByRole('columnheader')).toHaveCount(4);
  await expect(taskTable.getByRole('row').first()).toBeVisible();
  await expect(taskTable.getByRole('cell').first()).toBeVisible();

  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-table-teacher-${Date.now()}` });
  await page.goto('teacher/resources');
  const resourceTable = page.getByRole('table', { name: '资料版本' });
  await expect(resourceTable).toBeVisible();
  await expect(resourceTable.getByRole('columnheader')).toHaveCount(4);
  await expect(resourceTable.getByRole('row').nth(1)).toBeVisible();
  await expect(resourceTable.getByRole('cell').first()).toBeVisible();
});

test('teacher gradebook exports the summary CSV', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'teacher', 'x-dev-user': `playwright-gradebook-csv-${Date.now()}` });
  await page.goto('teacher/gradebook');
  await expect(page.getByRole('heading', { name: '成绩册与学情' })).toBeVisible();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: '导出 CSV' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^成绩册-\d{4}-\d{2}-\d{2}\.csv$/);
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream) chunks.push(chunk as Buffer);
  const text = Buffer.concat(chunks).toString('utf-8');
  expect(text.replace(/^\uFEFF/, '')).toContain('作业,题数,状态,已提交,已批改,完成率,平均成绩,平均正确率');
  expect(text).toContain('学生汇总');
  expect(text).toContain('知识点掌握');
});

test('discussion list paginates and resets on query change', async ({ page }) => {
  await page.setExtraHTTPHeaders({ 'x-dev-role': 'student', 'x-dev-user': `playwright-discussion-page-${Date.now()}` });
  const topics = Array.from({ length: 12 }, (_, index) => ({ id: `topic-${index + 1}`, title: `分页讨论 ${index + 1}`, body: '讨论内容', status: 'open', pinned: false, author_label: '学生', reply_count: 0, created_at: '2026-08-01' }));
  await page.route('**/api/discussions?*', async (route) => {
    const url = new URL(route.request().url());
    const pageNumber = Number(url.searchParams.get('page') || 1);
    const pageSize = Number(url.searchParams.get('page_size') || 8);
    const query = url.searchParams.get('query') || '';
    const visible = topics.filter((item) => !query || item.title.includes(query));
    const start = (pageNumber - 1) * pageSize;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', data: { items: visible.slice(start, start + pageSize), page: pageNumber, page_size: pageSize, total: visible.length } }),
    });
  });
  await page.goto('discussions');
  await expect(page.getByText('第 1 / 2 页，共 12 条')).toBeVisible();
  await expect(page.locator('.discussion-row')).toHaveCount(8);
  await expect(page.getByRole('button', { name: '讨论上一页' })).toBeDisabled();
  await page.getByRole('button', { name: '讨论下一页' }).click();
  await expect(page.getByText('第 2 / 2 页，共 12 条')).toBeVisible();
  await expect(page.locator('.discussion-row')).toHaveCount(4);
  await page.getByRole('textbox', { name: '搜索讨论' }).fill('分页讨论 12');
  await expect(page.getByText('1 个主题')).toBeVisible();
  await expect(page.locator('.discussion-row')).toHaveCount(1);
  await expect(page.getByText(/第 1 \/ 2 页/)).toHaveCount(0);
});
