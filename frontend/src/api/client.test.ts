import { beforeEach, describe, expect, it, vi } from 'vitest';
import { type AgentEvent, createActivity, createDiscussion, createDiscussionReply, createKnowledgeBaseVersion, createTeacherAssignment, createTeacherExam, createTeacherQuestion, createTeacherResource, decideAdminModeration, deleteResourceNote, generateActivityGroups, loadActivities, loadActivity, loadActivityGroups, loadActivityResults, loadAdminAuditLog, loadAdminBackupStatus, loadAdminCourses, loadAdminModeration, loadAdminStatus, loadAdminUsers, loadAssignment, loadAssignmentDraft, loadAssignments, loadClassroomRoster, loadCourses, loadDiscussions, loadExam, loadExamDraft, loadExams, loadFavoriteResources, loadGlobalSearch, loadKnowledgeGraph, loadKnowledgeGraphNode, loadKnowledgeGraphNodes, loadKnowledgeGraphPath, loadLearningPosition, loadNotifications, loadProfile, loadRandomSelection, loadResourceAnnotations, loadResourceProgress, loadResources, loadTasks, loadTeacherAssignments, loadTeacherExams, loadTeacherGradebook, loadTeacherQuestions, loadTeacherResources, markAllNotificationsRead, markNotificationRead, moderateDiscussion, parseAgentSseBlock, publishTeacherAssignment, publishTeacherExam, publishTeacherQuestion, reportDiscussion, saveAssignmentDraft, saveExamDraft, saveResourceFavorite, saveResourceNote, saveResourceProgress, selectRandomStudent, startExam, streamAgent, submitActivityResponse, submitAssignment, submitExam, transitionActivity, transitionTeacherExam, transitionTeacherResource, updateTeacherQuestion, uploadKnowledgeBaseFile, uploadTeacherResource } from './client';

function apiResponse(data: unknown, status = 200): Response {
  return { ok: true, status, json: async () => ({ status: 'ok', data }) } as Response;
}

describe('client DTO normalization', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  it('emits a session-expired event for unauthenticated API responses', async () => {
    const onExpired = vi.fn();
    window.addEventListener('course:session-expired', onExpired);
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ status: 'error', data: null, error: { code: 'session_expired', message: '会话已过期' } }),
    } as Response);

    await expect(loadAssignments()).rejects.toMatchObject({ code: 'session_expired' });
    expect(onExpired).toHaveBeenCalledTimes(1);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
    window.removeEventListener('course:session-expired', onExpired);
  });

  it('client maps published assignment rows to learner display states', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', data: { items: [{ id: 'a-1', title: '章节练习', status: 'published', due_at: '2026-07-28', question_ids: ['q-1', 'q-2'] }] } }),
    } as Response);
    await expect(loadAssignments()).resolves.toEqual([{
      id: 'a-1',
      title: '章节练习',
      type: '课程作业',
      status: '待完成',
      dueAt: '2026-07-28',
      questionCount: 2,
      score: null,
      progress: 0,
      allowAttempts: 1,
    }]);
  });

  it('normalizes the unified task feed and sends every server-owned filter', async () => {
    vi.mocked(fetch).mockResolvedValue(apiResponse({
      items: [{ id: 'exam:exam-1', source_id: 'exam-1', kind: 'exam', title: '限时考试', summary: '进入考试', status: 'in_progress', due_at: '2026-08-01T08:00:00Z', updated_at: '2026-07-29T08:00:00Z', progress: 50 }],
      page: 2,
      page_size: 5,
      total: 6,
      counts: {
        by_status: { pending: 4, in_progress: 1, completed: 2, expired: 1 },
        by_kind: { assignment: 3, exam: 2, discussion: 2, notification: 1 },
      },
    }));

    await expect(loadTasks({ kind: 'exam', status: 'in_progress', page: 2, pageSize: 5 })).resolves.toEqual({
      items: [{ id: 'exam:exam-1', sourceId: 'exam-1', kind: 'exam', title: '限时考试', summary: '进入考试', status: 'in_progress', dueAt: '2026-08-01T08:00:00Z', updatedAt: '2026-07-29T08:00:00Z', progress: 50 }],
      page: 2,
      pageSize: 5,
      total: 6,
      counts: {
        byStatus: { pending: 4, in_progress: 1, completed: 2, expired: 1 },
        byKind: { assignment: 3, exam: 2, discussion: 2, notification: 1 },
      },
    });
    expect(String(vi.mocked(fetch).mock.calls[0]?.[0])).toBe('/api/student/tasks?kind=exam&status=in_progress&page=2&page_size=5');
  });

  it('rejects malformed unified task rows instead of coercing server state', async () => {
    vi.mocked(fetch).mockResolvedValue(apiResponse({
      items: [{ id: 'assignment:a-1', source_id: 'a-1', kind: 'assignment', title: '异常任务', summary: '', status: 'pending', due_at: null, updated_at: '2026-07-29T08:00:00Z', progress: 101 }],
      page: 1,
      page_size: 20,
      total: 1,
      counts: { by_status: {}, by_kind: {} },
    }));

    await expect(loadTasks()).rejects.toMatchObject({ code: 'invalid_task_payload' });
  });

  it('normalizes the paginated course list and sends a bounded sort query', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', data: { items: [{ id: 1, name: '储能技术', teacher_name: '课程教师', class_name: '测试班', status: 'active', progress: 42, chapter_count: 6, resource_count: 20, last_accessed_at: null }], page: 1, page_size: 10, total: 1 } }),
    } as Response);
    await expect(loadCourses({ sort: 'progress', page: 1, pageSize: 10 })).resolves.toEqual({
      items: [{ id: 1, name: '储能技术', teacher: '课程教师', className: '测试班', status: 'active', progress: 42, chapterCount: 6, resourceCount: 20, lastAccessedAt: null }],
      page: 1,
      pageSize: 10,
      total: 1,
    });
    expect(String(vi.mocked(fetch).mock.calls[0]?.[0])).toBe('/api/courses?sort=progress&page=1&page_size=10');
  });

  it('client maps node-based profile and snake-case resources', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { nodes: [{ id: 'kp-3-4', name: '并网控制', status: 'weak', ratio: 0.38 }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'res-1', source_file: '3.4.pdf', chapter_id: 3, page_start: 1, page_end: 38, version: 'v1' }] } }) } as Response);
    await expect(loadProfile()).resolves.toEqual([{ id: 'kp-3-4', name: '并网控制', status: 'weak', ratio: 0.38 }]);
    await expect(loadResources(3)).resolves.toEqual([{ id: 'res-1', title: '3.4', sourceFile: '3.4.pdf', chapterId: 3, pageStart: 1, pageCount: 38, type: 'PDF', version: 'v1', available: true, mountStatus: 'ready' }]);
  });

  it('normalizes resource progress and sends optimistic version headers', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { resource: { id: 'res-1', source_file: '3.4.pdf', chapter_id: 3, page_end: 38, available: false, mount_status: 'pending_mount' }, progress: { resource_id: 'res-1', page: 1, percent: 0, completed: false, version: 0, has_saved_progress: false } } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { resource_id: 'res-1', page: 2, percent: 3, completed: false, version: 1, has_saved_progress: true } }) } as Response);
    await expect(loadResourceProgress('res-1')).resolves.toMatchObject({ progress: { resourceId: 'res-1', version: 0 }, resource: { available: false, mountStatus: 'pending_mount' } });
    await expect(saveResourceProgress('res-1', { page: 2, percent: 3, completed: false }, 0, 'csrf-fixture', 'progress-key')).resolves.toMatchObject({ resourceId: 'res-1', version: 1 });
    const options = vi.mocked(fetch).mock.calls[1]?.[1] as RequestInit;
    expect((options.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect((options.headers as Record<string, string>)['Idempotency-Key']).toBe('progress-key');
    expect(JSON.parse(String(options.body))).toMatchObject({ page: 2, base_version: 0 });
  });

  it('normalizes null and saved learning positions without coercing fields', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(apiResponse({ position: null }))
      .mockResolvedValueOnce(apiResponse({
        position: {
          course_id: 7,
          resource: { id: 'res-3.4', title: null, source_file: '3.4.pdf', chapter_id: 3, page_start: 1, page_end: 38, type: 'PDF', version: 'v2', status: 'published', available: true, mount_status: 'ready' },
          progress: { resource_id: 'res-3.4', page: 12, percent: 31.5, completed: false, version: 4, updated_at: '2026-07-29T08:30:00Z', has_saved_progress: true },
        },
      }));

    await expect(loadLearningPosition()).resolves.toBeNull();
    await expect(loadLearningPosition()).resolves.toEqual({
      courseId: 7,
      resource: { id: 'res-3.4', title: '3.4', sourceFile: '3.4.pdf', chapterId: 3, pageStart: 1, pageCount: 38, type: 'PDF', version: 'v2', available: true, mountStatus: 'ready', locator: null },
      progress: { resourceId: 'res-3.4', page: 12, percent: 31.5, completed: false, version: 4, updatedAt: '2026-07-29T08:30:00Z', hasSavedProgress: true },
    });
    expect(vi.mocked(fetch).mock.calls.map((call) => call[0])).toEqual(['/api/student/learning-position', '/api/student/learning-position']);
  });

  it('rejects malicious or malformed learning positions instead of creating a navigation target', async () => {
    const validPosition = {
      course_id: 1,
      resource: { id: 'res-1', title: '并网控制', source_file: '3.4.pdf', chapter_id: 3, page_start: 1, page_end: 38, status: 'published', available: true, mount_status: 'ready' },
      progress: { resource_id: 'res-1', page: 3, percent: 8, completed: false, version: 1, updated_at: '2026-07-29T08:30:00Z', has_saved_progress: true },
    };
    vi.mocked(fetch)
      .mockResolvedValueOnce(apiResponse({ position: { ...validPosition, resource: { ...validPosition.resource, id: '../../admin' }, progress: { ...validPosition.progress, resource_id: '../../admin' } } }))
      .mockResolvedValueOnce(apiResponse({ position: { ...validPosition, progress: { ...validPosition.progress, page: 99 } } }))
      .mockResolvedValueOnce(apiResponse({ position: { ...validPosition, progress: { ...validPosition.progress, percent: '8' } } }))
      .mockResolvedValueOnce(apiResponse({ position: { ...validPosition, progress: { ...validPosition.progress, has_saved_progress: false } } }))
      .mockResolvedValueOnce(apiResponse({ position: { ...validPosition, resource: { ...validPosition.resource, status: 'archived' } } }))
      .mockResolvedValueOnce(apiResponse({ items: [] }));

    for (let index = 0; index < 6; index += 1) {
      await expect(loadLearningPosition()).rejects.toMatchObject({ code: 'invalid_learning_position_payload' });
    }
  });

  it('normalizes resource annotations and protects annotation writes', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { resource_id: 'res-1', favorite: true, notes: [{ id: 'res-1:2', resource_id: 'res-1', page: 2, text: '重点', version: 1, updated_at: '2026-07-26' }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { resource_id: 'res-1', favorite: false } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'res-1:2', resource_id: 'res-1', page: 2, text: '新重点', version: 2 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { resource_id: 'res-1', page: 2, deleted: true, version: 3 } }) } as Response);
    await expect(loadResourceAnnotations('res-1')).resolves.toMatchObject({ resourceId: 'res-1', favorite: true, notes: [{ page: 2, text: '重点', version: 1 }] });
    await expect(saveResourceFavorite('res-1', false, 'csrf-fixture', 'favorite-key')).resolves.toEqual({ resourceId: 'res-1', favorite: false });
    await expect(saveResourceNote('res-1', 2, '新重点', 1, 'csrf-fixture', 'note-key')).resolves.toMatchObject({ resourceId: 'res-1', page: 2, text: '新重点', version: 2 });
    await expect(deleteResourceNote('res-1', 2, 2, 'csrf-fixture', 'delete-key')).resolves.toMatchObject({ resourceId: 'res-1', page: 2, deleted: true, version: 3 });
    const calls = vi.mocked(fetch).mock.calls;
    expect((calls[1]?.[1]?.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect((calls[2]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toBe('note-key');
    expect(JSON.parse(String(calls[2]?.[1]?.body))).toMatchObject({ text: '新重点', base_version: 1 });
    expect(calls[3]?.[1]?.method).toBe('DELETE');
    expect(JSON.parse(String(calls[3]?.[1]?.body))).toMatchObject({ base_version: 2 });
  });

  it('normalizes the user-scoped favorite resource list', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', data: { items: [{ id: 'res-1', title: '并网控制', source_file: '3.4.pdf', chapter_id: 3, page_end: 38, available: false, mount_status: 'pending_mount', favorite_at: '2026-07-26T08:00:00Z', note_count: 2 }] } }),
    } as Response);
    await expect(loadFavoriteResources()).resolves.toEqual([{
      id: 'res-1',
      title: '并网控制',
      sourceFile: '3.4.pdf',
      chapterId: 3,
      pageStart: 1,
      pageCount: 38,
      type: 'PDF',
      version: '课程资料',
      available: false,
      mountStatus: 'pending_mount',
      favoriteAt: '2026-07-26T08:00:00Z',
      noteCount: 2,
    }]);
  });

  it('normalizes timed exams and sends server-window write headers', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'exam-1', title: '限时考试', status: 'published', availability: 'open', open_at: '2026-07-26T00:00:00Z', close_at: '2026-07-26T01:00:00Z', duration_seconds: 1800, allow_attempts: 1, question_count: 1 }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'exam-1', title: '限时考试', status: 'published', availability: 'open', open_at: '2026-07-26T00:00:00Z', close_at: '2026-07-26T01:00:00Z', duration_seconds: 1800, allow_attempts: 1, questions: [{ id: 'q-1', prompt: '题目', question_type: 'single_choice', options: ['A', 'B'], max_score: 10 }], my_attempts: [], my_submissions: [] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'exam-1', title: '限时考试', status: 'published', availability: 'open', open_at: '2026-07-26T00:00:00Z', close_at: '2026-07-26T01:00:00Z', duration_seconds: 1800, allow_attempts: 1, questions: [{ id: 'q-1', prompt: '题目', question_type: 'single_choice', options: ['A', 'B'], max_score: 10 }], my_attempts: [{ attempt: 1, started_at: '2026-07-26T00:10:00Z', deadline_at: '2026-07-26T00:40:00Z', status: 'in_progress' }], my_submissions: [], attempt: { attempt: 1, started_at: '2026-07-26T00:10:00Z', deadline_at: '2026-07-26T00:40:00Z', status: 'in_progress' }, server_now: '2026-07-26T00:10:00Z' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { exam_id: 'exam-1', attempt: 1, answers: {}, version: 0, has_saved_draft: false } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { exam_id: 'exam-1', attempt: 1, answers: { 'q-1': 'A' }, version: 1, has_saved_draft: true } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'exam-sub-1', exam_id: 'exam-1', attempt: 1, submitted_at: '2026-07-26T00:20:00Z', score: 10, max_score: 10, needs_review: false } }) } as Response);
    await expect(loadExams()).resolves.toMatchObject([{ id: 'exam-1', title: '限时考试', status: '进行中', durationSeconds: 1800 }]);
    await expect(loadExam('exam-1')).resolves.toMatchObject({ questions: [{ id: 'q-1', questionType: 'single_choice' }] });
    await expect(startExam('exam-1', 'csrf-fixture', 'exam-start-key')).resolves.toMatchObject({ attempt: { attempt: 1, deadlineAt: '2026-07-26T00:40:00Z' }, serverNow: '2026-07-26T00:10:00Z' });
    await expect(loadExamDraft('exam-1', 1)).resolves.toMatchObject({ examId: 'exam-1', version: 0 });
    await expect(saveExamDraft('exam-1', 1, { 'q-1': 'A' }, 0, 'csrf-fixture', 'exam-draft-key')).resolves.toMatchObject({ version: 1 });
    await expect(submitExam('exam-1', 1, { 'q-1': 'A' }, 'csrf-fixture', 'exam-submit-key')).resolves.toMatchObject({ examId: 'exam-1', score: 10 });
    const calls = vi.mocked(fetch).mock.calls;
    expect((calls[2]?.[1]?.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect((calls[4]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toBe('exam-draft-key');
    expect((calls[5]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toBe('exam-submit-key');
  });

  it('normalizes teacher exams and sends protected management headers', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'exam-1', title: '教师考试', status: 'draft', availability: 'not_open', open_at: '2026-07-28T00:00:00Z', close_at: '2026-07-29T00:00:00Z', duration_seconds: 1800, allow_attempts: 2, question_ids: ['q-1'], question_count: 1, created_by: 'u_teacher', updated_at: '2026-07-26T00:00:00Z' }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'exam-2', title: '新考试', status: 'draft', open_at: '2026-07-28T00:00:00Z', close_at: '2026-07-29T00:00:00Z', duration_seconds: 1800, allow_attempts: 1, question_ids: ['q-1'], question_count: 1 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'exam-2', title: '新考试', status: 'published', open_at: '2026-07-28T00:00:00Z', close_at: '2026-07-29T00:00:00Z', duration_seconds: 1800, allow_attempts: 1, question_ids: ['q-1'], question_count: 1 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'exam-2', title: '新考试', status: 'withdrawn', open_at: '2026-07-28T00:00:00Z', close_at: '2026-07-29T00:00:00Z', duration_seconds: 1800, allow_attempts: 1, question_ids: ['q-1'], question_count: 1 } }) } as Response);
    await expect(loadTeacherExams()).resolves.toMatchObject([{ id: 'exam-1', status: 'draft', questionCount: 1, durationSeconds: 1800, allowAttempts: 2 }]);
    await expect(createTeacherExam({ title: '新考试', question_ids: ['q-1'], open_at: '2026-07-28T00:00:00.000Z', close_at: '2026-07-29T00:00:00.000Z', duration_seconds: 1800, allow_attempts: 1 }, 'csrf-fixture', 'exam-create-key')).resolves.toMatchObject({ id: 'exam-2' });
    await expect(publishTeacherExam('exam-2', 'csrf-fixture', 'exam-publish-key')).resolves.toMatchObject({ status: 'published' });
    await expect(transitionTeacherExam('exam-2', 'withdraw', 'csrf-fixture', 'exam-withdraw-key')).resolves.toMatchObject({ status: 'withdrawn' });
    const calls = vi.mocked(fetch).mock.calls;
    expect((calls[1]?.[1]?.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect((calls[1]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toBe('exam-create-key');
    expect((calls[2]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toBe('exam-publish-key');
    expect((calls[3]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toBe('exam-withdraw-key');
  });

  it('client sends the Moodle sesskey on Agent POST requests', async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('event: done\ndata: {"request_id":"test"}\n\n'));
        controller.close();
      },
    });
    vi.mocked(fetch).mockResolvedValue({ ok: true, body: stream } as Response);
    await streamAgent('测试问题', 'qa', () => undefined, 'csrf-fixture');
    const options = vi.mocked(fetch).mock.calls[0]?.[1] as RequestInit;
    expect((options.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
  });

  it('sends trusted-context references without treating them as trusted content', async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('event: done\ndata: {"request_id":"test"}\n\n'));
        controller.close();
      },
    });
    vi.mocked(fetch).mockResolvedValue({ ok: true, body: stream } as Response);
    await streamAgent('测试问题', 'qa', () => undefined, 'csrf-fixture', undefined, { resourceId: 'res-1', resourcePage: 3, nodeIds: ['kp-1'] });
    const options = vi.mocked(fetch).mock.calls[0]?.[1] as RequestInit;
    expect(JSON.parse(String(options.body))).toMatchObject({ resource_id: 'res-1', resource_page: 3, node_ids: ['kp-1'] });
  });

  it('maps malformed SSE blocks to a typed error', () => {
    expect(parseAgentSseBlock('event: token\ndata: {"text":"ok"}')).toMatchObject({ event: 'token' });
    expect(() => parseAgentSseBlock('event: token\ndata: {bad}')).toThrowError('Agent 流式响应格式错误');
  });

  it('rejects an SSE stream that ends before a done event', async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('event: token\ndata: {"text":"partial"}\n\n'));
        controller.close();
      },
    });
    const events: AgentEvent[] = [];
    vi.mocked(fetch).mockResolvedValue({ ok: true, body: stream } as Response);

    await expect(streamAgent('测试问题', 'qa', (event) => events.push(event))).rejects.toMatchObject({ code: 'stream_incomplete' });
    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({ event: 'token', data: { text: 'partial' } });
  });

  it('surfaces an upstream error event and stops without synthesizing done', async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('event: error\ndata: {"code":"upstream_disconnected","message":"上游中断"}\n\n'));
        controller.close();
      },
    });
    const events: AgentEvent[] = [];
    vi.mocked(fetch).mockResolvedValue({ ok: true, body: stream } as Response);

    await expect(streamAgent('测试问题', 'qa', (event) => events.push(event))).rejects.toMatchObject({ code: 'upstream_disconnected' });
    expect(events).toHaveLength(1);
    expect(events[0].event).toBe('error');
  });

  it('dispatches only the first done event when an upstream repeats it', async () => {
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('event: done\ndata: {"request_id":"one"}\n\nevent: done\ndata: {"request_id":"two"}\n\n'));
        controller.close();
      },
    });
    const events: AgentEvent[] = [];
    vi.mocked(fetch).mockResolvedValue({ ok: true, body: stream } as Response);

    await expect(streamAgent('测试问题', 'qa', (event) => events.push(event))).resolves.toBeUndefined();
    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({ event: 'done', data: { request_id: 'one' } });
  });

  it('passes cancellation through without retrying the Agent request', async () => {
    const controller = new AbortController();
    const abortError = new DOMException('The operation was aborted', 'AbortError');
    vi.mocked(fetch).mockRejectedValue(abortError);

    await expect(streamAgent('测试问题', 'qa', () => undefined, '', controller.signal)).rejects.toBe(abortError);
    const options = vi.mocked(fetch).mock.calls[0]?.[1] as RequestInit;
    expect(options.signal).toBe(controller.signal);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
  });

  it('preserves the server error code for a non-streaming Agent failure', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({ request_id: 'request-rate-limit', error: { code: 'rate_limited', message: '请求过于频繁' } }),
    } as Response);

    await expect(streamAgent('测试问题', 'qa', () => undefined)).rejects.toMatchObject({ code: 'rate_limited', requestId: 'request-rate-limit' });
  });

  it('does not dispatch a late SSE frame after cancellation', async () => {
    let resolveRead: ((result: ReadableStreamReadResult<Uint8Array>) => void) | undefined;
    const reader = {
      read: vi.fn(() => new Promise<ReadableStreamReadResult<Uint8Array>>((resolve) => { resolveRead = resolve; })),
      cancel: vi.fn().mockResolvedValue(undefined),
      releaseLock: vi.fn(),
    };
    const controller = new AbortController();
    const events: AgentEvent[] = [];
    vi.mocked(fetch).mockResolvedValue({ ok: true, body: { getReader: () => reader } } as unknown as Response);

    const pending = streamAgent('测试问题', 'qa', (event) => events.push(event), '', controller.signal);
    await new Promise((resolve) => setTimeout(resolve, 0));
    controller.abort();
    resolveRead?.({ done: false, value: new TextEncoder().encode('event: token\\ndata: {"text":"迟到回答"}\\n\\n') });

    await expect(pending).rejects.toMatchObject({ name: 'AbortError' });
    expect(events).toHaveLength(0);
    expect(reader.cancel).toHaveBeenCalledTimes(1);
    expect(reader.releaseLock).toHaveBeenCalledTimes(1);
  });

  it('normalizes assignment detail and preserves server draft versions', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: {
        id: 'a-1', title: '章节作业', status: 'published', due_at: '2026-07-28', question_ids: ['q-1'], allow_attempts: 1,
        questions: [{ id: 'q-1', prompt: '选择正确项', question_type: 'single_choice', options: ['A', 'B'], max_score: 10 }],
        my_submissions: [], my_draft: { assignment_id: 'a-1', attempt: 1, answers: { 'q-1': 'A' }, version: 2, has_saved_draft: true },
      } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { assignment_id: 'a-1', attempt: 1, answers: { 'q-1': 'A' }, version: 2, has_saved_draft: true } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { assignment_id: 'a-1', attempt: 1, answers: { 'q-1': 'B' }, version: 3, has_saved_draft: true } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'sub-1', assignment_id: 'a-1', attempt: 1, status: 'submitted' } }) } as Response);
    await expect(loadAssignment('a-1')).resolves.toMatchObject({ allowAttempts: 1, questions: [{ id: 'q-1', questionType: 'single_choice' }], myDraft: { version: 2, answers: { 'q-1': 'A' } } });
    await expect(loadAssignmentDraft('a-1')).resolves.toMatchObject({ version: 2 });
    await expect(saveAssignmentDraft('a-1', 1, { 'q-1': 'B' }, 2, 'csrf-fixture', 'draft-key')).resolves.toMatchObject({ version: 3 });
    await expect(submitAssignment('a-1', 1, { 'q-1': 'B' }, 'csrf-fixture', 'submit-key')).resolves.toMatchObject({ id: 'sub-1', attempt: 1 });
    const draftOptions = vi.mocked(fetch).mock.calls[2]?.[1] as RequestInit;
    expect((draftOptions.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect((draftOptions.headers as Record<string, string>)['Idempotency-Key']).toBe('draft-key');
  });

  it('normalizes discussions and notifications from snake-case API DTOs', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'topic-1', title: '并网控制', body: '讨论功率平衡', status: 'open', pinned: 1, author_label: '课程成员', reply_count: 2, created_at: '2026-07-25' }], page: 1, page_size: 8, total: 3 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'notice-1', audience: 'course_students', title: '学习提醒', body: '请完成作业', created_by: 'teacher-1', created_at: '2026-07-25', is_read: 0 }], unread_count: 1, page: 2, page_size: 5, total: 6, focus_found: true, focused_id: 'notice-1' } }) } as Response);
    await expect(loadDiscussions('并网')).resolves.toEqual({ items: [{ id: 'topic-1', title: '并网控制', body: '讨论功率平衡', status: 'open', pinned: true, authorLabel: '课程成员', replyCount: 2, createdAt: '2026-07-25', updatedAt: '', replies: undefined, canModerate: false }], total: 3 });
    await expect(loadNotifications(true, 2, 5, 'notice-1')).resolves.toEqual({ items: [{ id: 'notice-1', audience: 'course_students', title: '学习提醒', body: '请完成作业', createdBy: 'teacher-1', createdAt: '2026-07-25', isRead: false }], unreadCount: 1, page: 2, pageSize: 5, total: 6, focusFound: true, focusedId: 'notice-1' });
    expect(vi.mocked(fetch).mock.calls[0]?.[0]).toBe('/api/discussions?query=%E5%B9%B6%E7%BD%91&page=1&page_size=8');
    expect(vi.mocked(fetch).mock.calls[1]?.[0]).toBe('/api/notifications?page=2&page_size=5&unread_only=true&focus_id=notice-1');
  });

  it('fails notification focus metadata closed when the target is absent or the flag is not boolean true', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [], focus_found: true, focused_id: 'notice-hidden', page: 1, page_size: 8, total: 0 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'notice-1', title: '通知', body: '内容', is_read: false }], focus_found: 'false', focused_id: 'notice-1', page: 1, page_size: 8, total: 1 } }) } as Response);

    await expect(loadNotifications(false, 1, 8, 'notice-hidden')).resolves.toMatchObject({ focusFound: false, focusedId: null });
    await expect(loadNotifications(false, 1, 8, 'notice-1')).resolves.toMatchObject({ focusFound: false, focusedId: null });
  });

  it('adds CSRF and idempotency headers to social write requests', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'topic-1', title: '主题', body: '正文', status: 'open' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'reply-1', topic_id: 'topic-1', body: '回复', status: 'visible' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'topic-1', title: '主题', body: '正文', status: 'solved', pinned: true } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { notification_id: 'notice-1', is_read: true, unread_count: 2 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { marked_count: 3, unread_count: 0 } }) } as Response);
    await createDiscussion('主题', '正文', 'csrf-fixture', 'topic-key');
    await createDiscussionReply('topic-1', '回复', 'csrf-fixture', 'reply-key');
    await moderateDiscussion('topic-1', { pinned: true, status: 'solved', reason: '已核验' }, 'csrf-fixture', 'moderate-key');
    await expect(markNotificationRead('notice-1', 'csrf-fixture', 'read-key')).resolves.toEqual({ unreadCount: 2 });
    await expect(markAllNotificationsRead('csrf-fixture', 'read-all-key')).resolves.toEqual({ markedCount: 3, unreadCount: 0 });
    const calls = vi.mocked(fetch).mock.calls;
    for (const index of [0, 1, 2, 3, 4]) {
      const headers = calls[index]?.[1]?.headers as Record<string, string>;
      expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
      expect(headers['Idempotency-Key']).toMatch(/key$/);
    }
    expect(calls[4]?.[0]).toBe('/api/notifications/read-all');
  });

  it('sends a course-scoped discussion report with CSRF and idempotency headers', async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: true, status: 202, json: async () => ({ status: 'ok', data: { id: 'reply-1', topic_id: 'topic-1', content_type: 'reply', status: 'pending_review' } }) } as Response);
    await expect(reportDiscussion('topic-1', 'reply-1', '请管理员核对', 'csrf-fixture', 'report-key')).resolves.toEqual({ id: 'reply-1', topicId: 'topic-1', contentType: 'reply', status: 'pending_review' });
    const options = vi.mocked(fetch).mock.calls[0]?.[1] as RequestInit;
    const headers = options.headers as Record<string, string>;
    expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(headers['Idempotency-Key']).toBe('report-key');
    expect(JSON.parse(String(options.body))).toEqual({ reply_id: 'reply-1', reason: '请管理员核对' });
  });

  it('normalizes activity details and aggregate result DTOs', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'activity-1', kind: 'poll', title: '控制重点', body: '选择一项', options: [{ id: 'a', label: '功率平衡' }], status: 'published', max_attempts: 1, has_responded: true, attempts_used: 1, can_respond: false, next_attempt: null, my_response: { id: 'response-1', activity_id: 'activity-1', attempt: 1, answers: ['a'], submitted_at: '2026-07-25' } }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'activity-1', kind: 'poll', title: '控制重点', body: '选择一项', options: [{ id: 'a', label: '功率平衡' }], status: 'published', max_attempts: 1, has_responded: true, attempts_used: 1, can_respond: false, next_attempt: null, my_response: { id: 'response-1', activity_id: 'activity-1', attempt: 1, answers: ['a'] } } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { activity_id: 'activity-1', kind: 'poll', total_responses: 2, has_responded: true, results_available: true, options: [{ id: 'a', label: '功率平衡', count: 2, ratio: 100 }] } }) } as Response);
    await expect(loadActivities()).resolves.toMatchObject([{ id: 'activity-1', kind: 'poll', hasResponded: true, attemptsUsed: 1, canRespond: false, nextAttempt: null, myResponse: { activityId: 'activity-1', answers: ['a'] } }]);
    await expect(loadActivity('activity-1')).resolves.toMatchObject({ id: 'activity-1', title: '控制重点' });
    await expect(loadActivityResults('activity-1')).resolves.toEqual({ activityId: 'activity-1', kind: 'poll', totalResponses: 2, hasResponded: true, resultsAvailable: true, options: [{ id: 'a', label: '功率平衡', count: 2, ratio: 100 }], participants: [] });
  });

  it('normalizes teacher check-in participants and sends a sentinel-free create payload', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'checkin-1', kind: 'checkin', title: '课堂签到', body: '请完成签到', options: [], status: 'published', max_attempts: 1 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { activity_id: 'checkin-1', kind: 'checkin', total_responses: 1, has_responded: false, results_available: true, options: [], participants: [{ user_ref: 'u_12345678', submitted_at: '2026-07-29T08:00:00Z' }] } }) } as Response);

    await expect(createActivity({ kind: 'checkin', title: '课堂签到', body: '请完成签到', options: [], status: 'published', maxAttempts: 1 }, 'csrf-fixture', 'activity-checkin-create')).resolves.toMatchObject({ kind: 'checkin', options: [], maxAttempts: 1 });
    const createRequest = vi.mocked(fetch).mock.calls[0]?.[1] as RequestInit;
    expect(JSON.parse(String(createRequest.body))).toMatchObject({ kind: 'checkin', options: [], max_attempts: 1 });
    await expect(loadActivityResults('checkin-1')).resolves.toEqual({
      activityId: 'checkin-1', kind: 'checkin', totalResponses: 1, hasResponded: false, resultsAvailable: true, options: [],
      participants: [{ userRef: 'u_12345678', submittedAt: '2026-07-29T08:00:00Z' }],
    });
  });

  it('creates a quick response without exposing its internal claim sentinel', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ status: 'ok', data: { id: 'quick-1', kind: 'quick_response', title: '课堂抢答', body: '请抢答', options: [], status: 'published', max_attempts: 1, can_reopen: true } }),
    } as Response);

    await expect(createActivity({ kind: 'quick_response', title: '课堂抢答', body: '请抢答', options: [], status: 'published', maxAttempts: 1 }, 'csrf-fixture', 'activity-quick-create')).resolves.toMatchObject({
      id: 'quick-1',
      kind: 'quick_response',
      options: [],
      maxAttempts: 1,
      canReopen: true,
    });

    const request = vi.mocked(fetch).mock.calls[0];
    const options = request?.[1] as RequestInit;
    const body = JSON.parse(String(options.body)) as Record<string, unknown>;
    expect(request?.[0]).toBe('/api/teacher/activities');
    expect(options.method).toBe('POST');
    expect(body).toMatchObject({ kind: 'quick_response', options: [], max_attempts: 1 });
    expect(JSON.stringify(body)).not.toContain('claim');
  });

  it('submits the fixed quick-response claim with protected write headers', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ status: 'ok', data: { id: 'quick-response-1', activity_id: 'quick-1', attempt: 1, answers: ['claim'], submitted_at: '2026-07-29T08:00:00Z' } }),
    } as Response);

    await expect(submitActivityResponse('quick-1', ['claim'], 'csrf-fixture', 'quick-claim-key', 1)).resolves.toMatchObject({
      activityId: 'quick-1',
      attempt: 1,
      answers: ['claim'],
    });

    const request = vi.mocked(fetch).mock.calls[0];
    const options = request?.[1] as RequestInit;
    const headers = options.headers as Record<string, string>;
    expect(request?.[0]).toBe('/api/activities/quick-1/responses');
    expect(options.method).toBe('POST');
    expect(JSON.parse(String(options.body))).toEqual({ answers: ['claim'], attempt: 1 });
    expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(headers['Idempotency-Key']).toBe('quick-claim-key');
    expect(headers['X-Request-ID']).toMatch(/^activity-response-/);
  });

  it('normalizes classroom roster, random selection and group-task contracts', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(apiResponse({ configured: true, items: [{ user_ref: 'u_1', display_name: '学生一' }, { user_ref: 'u_2', display_name: '学生二' }] }))
      .mockResolvedValueOnce(apiResponse({ activity_id: 'random-1', round: 2, latest: { round: 2, display_name: '学生二', selected_at: '2026-07-29T09:00:00Z', is_me: true }, remaining_count: null, can_select: false }))
      .mockResolvedValueOnce(apiResponse({ activity_id: 'random-1', round: 3, latest: { round: 3, display_name: '学生一', selected_at: '2026-07-29T09:01:00Z', user_ref: 'u_1' }, history: [{ round: 2, display_name: '学生二', selected_at: '2026-07-29T09:00:00Z', user_ref: 'u_2' }, { round: 3, display_name: '学生一', selected_at: '2026-07-29T09:01:00Z', user_ref: 'u_1' }], can_select: true }))
      .mockResolvedValueOnce(apiResponse({ activity_id: 'groups-1', revision: 2, my_group: { id: 'alpha', name: '甲组', members: [{ display_name: '学生一', is_me: true }, { display_name: '学生二', is_me: false }] }, can_generate: false }))
      .mockResolvedValueOnce(apiResponse({ activity_id: 'groups-1', revision: 3, groups: [{ id: 'alpha', name: '甲组', members: [{ user_ref: 'u_1', display_name: '学生一' }] }, { id: 'beta', name: '乙组', members: [{ user_ref: 'u_2', display_name: '学生二' }] }], can_generate: true }));

    await expect(loadClassroomRoster()).resolves.toEqual({
      configured: true,
      items: [{ userRef: 'u_1', displayName: '学生一' }, { userRef: 'u_2', displayName: '学生二' }],
      total: 2,
      message: null,
    });
    await expect(loadRandomSelection('random-1')).resolves.toMatchObject({
      activityId: 'random-1', round: 2, latest: { round: 2, displayName: '学生二', isMe: true }, history: [], canSelect: false,
    });
    await expect(selectRandomStudent('random-1', 'csrf-fixture', 'random-key')).resolves.toMatchObject({
      activityId: 'random-1', round: 3, latest: { displayName: '学生一' }, history: [{ displayName: '学生二' }, { displayName: '学生一' }], canSelect: true,
    });
    await expect(loadActivityGroups('groups-1')).resolves.toMatchObject({
      activityId: 'groups-1', revision: 2, myGroup: { name: '甲组', members: [{ displayName: '学生一', isMe: true }, { displayName: '学生二', isMe: false }] }, canGenerate: false,
    });
    await expect(generateActivityGroups('groups-1', 'csrf-fixture', 'groups-key')).resolves.toMatchObject({
      activityId: 'groups-1', revision: 3, groups: [{ name: '甲组', members: [{ displayName: '学生一' }] }, { name: '乙组', members: [{ displayName: '学生二' }] }], canGenerate: true,
    });

    expect(vi.mocked(fetch).mock.calls.map((call) => call[0])).toEqual([
      '/api/teacher/classroom-roster',
      '/api/activities/random-1/random-selection',
      '/api/teacher/activities/random-1/random-select',
      '/api/activities/groups-1/groups',
      '/api/teacher/activities/groups-1/groups/generate',
    ]);
    for (const index of [2, 4]) {
      const request = vi.mocked(fetch).mock.calls[index]?.[1] as RequestInit;
      const headers = request.headers as Record<string, string>;
      expect(request.method).toBe('POST');
      expect(JSON.parse(String(request.body))).toEqual({});
      expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
      expect(headers['Idempotency-Key']).toBe(index === 2 ? 'random-key' : 'groups-key');
    }
  });

  it('sends activity response and teacher creation headers', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'response-1', activity_id: 'activity-1', attempt: 1, answers: ['a'] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'activity-2', kind: 'survey', title: '反馈', body: '请选择', options: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }], status: 'published' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'activity-2', kind: 'survey', title: '反馈', body: '请选择', options: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }], status: 'closed' } }) } as Response);
    await submitActivityResponse('activity-1', ['a'], 'csrf-fixture', 'activity-response-key');
    await createActivity({ kind: 'survey', title: '反馈', body: '请选择', options: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }], status: 'published' }, 'csrf-fixture', 'activity-create-key');
    await transitionActivity('activity-2', 'close', 'csrf-fixture', 'activity-close-key');
    for (const call of vi.mocked(fetch).mock.calls) {
      const headers = call[1]?.headers as Record<string, string>;
      expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
      expect(headers['Idempotency-Key']).toMatch(/^activity-/);
    }
  });

  it('normalizes teacher question, assignment and gradebook data', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'q-1', question_type: 'single_choice', prompt: '题干', options: ['A', 'B'], answer: 'A', rubric: '', max_score: 10, status: 'draft', version: 1, chapter_id: 3, chapter_name: '第3章', created_by: 'teacher', updated_at: '2026-07-25' }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'a-1', title: '作业', status: 'draft', question_ids: ['q-1'], due_at: null, allow_attempts: 1 }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { assignments: [{ id: 'a-1', title: '作业', status: 'published', submitted_count: 2, graded_count: 1, average_ratio: 65, average_score: 13, completion_rate: 100, question_count: 2 }], students: [{ user_uid: 'u-1', submission_count: 1, completed_assignments: 1, average_ratio: 55, needs_review: true, risk_level: 'high' }], knowledge_points: [{ id: 'kp-1', name: '并网控制', score: 5, max_score: 10, attempts: 1, ratio: 50, status: 'weak' }], risk_students: [{ user_uid: 'u-1', submission_count: 1, completed_assignments: 1, average_ratio: 55, needs_review: true, risk_level: 'high' }] } }) } as Response);
    await expect(loadTeacherQuestions()).resolves.toMatchObject([{ id: 'q-1', questionType: 'single_choice', answer: 'A', chapterName: '第3章' }]);
    await expect(loadTeacherAssignments()).resolves.toMatchObject([{ id: 'a-1', questionIds: ['q-1'], status: 'draft' }]);
    await expect(loadTeacherGradebook()).resolves.toMatchObject({ assignments: [{ averageRatio: 65 }], students: [{ userUid: 'u-1', riskLevel: 'high' }], knowledgePoints: [{ status: 'weak' }] });
  });

  it('sends CSRF and idempotency headers for teacher publishing writes', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'q-1', question_type: 'single_choice', prompt: '题干', status: 'published', version: 2 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'a-1', title: '作业', status: 'published', question_ids: ['q-1'] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'q-2', question_type: 'single_choice', prompt: '新题', status: 'draft' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'a-2', title: '新作业', status: 'draft', question_ids: ['q-2'] } }) } as Response);
    await publishTeacherQuestion('q-1', 'csrf-fixture', 'question-publish-key');
    await publishTeacherAssignment('a-1', 'csrf-fixture', 'assignment-publish-key');
    await createTeacherQuestion({ question_type: 'single_choice', prompt: '新题', options: ['A', 'B'], answer: 'A', max_score: 10 }, 'csrf-fixture', 'question-create-key');
    await createTeacherAssignment({ title: '新作业', question_ids: ['q-2'] }, 'csrf-fixture', 'assignment-create-key');
    for (const call of vi.mocked(fetch).mock.calls) {
      const headers = call[1]?.headers as Record<string, string>;
      expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
      expect(headers['Idempotency-Key']).toMatch(/key$/);
    }
  });

  it('sends an optimistic version when saving a draft question edit', async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: true, json: async () => ({ status: 'ok', data: { id: 'q-1', question_type: 'single_choice', prompt: '更新题干', options: ['A', 'B'], answer: 'A', max_score: 10, status: 'draft', version: 2 } }) } as Response);
    await updateTeacherQuestion('q-1', { question_type: 'single_choice', prompt: '更新题干', options: ['A', 'B'], answer: 'A', max_score: 10, base_version: 1 }, 'csrf-fixture', 'question-update-key');
    const options = vi.mocked(fetch).mock.calls[0]?.[1] as RequestInit;
    expect((options.headers as Record<string, string>)['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(JSON.parse(String(options.body))).toMatchObject({ base_version: 1, prompt: '更新题干' });
  });

  it('normalizes teacher resource revisions and sends raw file writes with headers', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'res-1', title: '补充讲义', source_file: 'notes.md', chapter_id: 3, status: 'draft', revision: 1, revisions: [{ id: 'rev-1', resource_id: 'res-1', revision: 1, filename: 'notes.md', sha256: 'hash', size_bytes: 4, uploaded_by: 'teacher', status: 'active', created_at: '2026-07-25' }] }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'res-1', title: '补充讲义', source_file: 'notes.md', chapter_id: 3, status: 'draft', revision: 1, revisions: [] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'res-1', title: '补充讲义', source_file: 'notes.md', chapter_id: 3, status: 'published', revision: 1, revisions: [] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'res-1', title: '补充讲义', source_file: 'notes.md', chapter_id: 3, status: 'draft', revision: 1, revisions: [] } }) } as Response);
    await expect(loadTeacherResources()).resolves.toMatchObject([{ id: 'res-1', status: 'draft', revision: 1, revisions: [{ resourceId: 'res-1', sizeBytes: 4 }] }]);
    await createTeacherResource({ title: '补充讲义', chapter_id: 3 }, 'csrf-fixture', 'resource-create-key');
    await uploadTeacherResource('res-1', new Blob(['test'], { type: 'text/markdown' }), 'notes.md', 'csrf-fixture', 'resource-upload-key');
    await transitionTeacherResource('res-1', 'publish', 'csrf-fixture', 'resource-publish-key');
    const uploadOptions = vi.mocked(fetch).mock.calls[2]?.[1] as RequestInit;
    const headers = uploadOptions.headers as Record<string, string>;
    expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(headers['Idempotency-Key']).toBe('resource-upload-key');
    expect(uploadOptions.body).toBeInstanceOf(Blob);
    expect(vi.mocked(fetch).mock.calls[3]?.[0]).toBe('/api/teacher/resources/res-1/publish');
  });

  it('normalizes redacted admin status, audit and backup DTOs', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { adapter: 'healthy', workflow_configured: false, mock_workflow: true, published_kb: null, backup: { managed_by: 'host-cron', status: 'verify_on_server' } } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { managed_by: 'host-cron', verification: 'verify_on_server', restore_rehearsal: 'run_on_server', secrets_excluded: true, status: 'operator_action_required' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'audit-1', actor_uid: 'u_admin', action: 'status:published', object_type: 'knowledge_base', object_id: 'kb-1', result: 'success', reason: 'release', request_id: 'req-1', created_at: '2026-07-25' }], page: 1, page_size: 20, total: 1 } }) } as Response);
    await expect(loadAdminStatus()).resolves.toMatchObject({ adapter: 'healthy', workflowConfigured: false, mockWorkflow: true, backup: { managedBy: 'host-cron' } });
    await expect(loadAdminBackupStatus()).resolves.toMatchObject({ secretsExcluded: true, restoreRehearsal: 'run_on_server' });
    await expect(loadAdminAuditLog()).resolves.toMatchObject({ total: 1, items: [{ objectType: 'knowledge_base', requestId: 'req-1' }] });
  });

  it('normalizes admin directory DTOs and sends bounded filters', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'u-1', display_name: '课程教师', role: 'teacher', course_id: 4, status: 'suspended', last_accessed_at: null }], page: 2, page_size: 5, total: 6, source: 'moodle_bridge', configured: true } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 4, name: '储能技术', teacher_name: '课程教师', class_name: '四班', status: 'active', progress: 101, chapter_count: 8, resource_count: 12, enrollment_count: 30, active_users: 28 }], page: 3, page_size: 10, total: 1, source: 'moodle_bridge', configured: true } }) } as Response);
    await expect(loadAdminUsers({ query: '教师', role: 'teacher', page: 2, pageSize: 5 })).resolves.toEqual({
      items: [{ id: 'u-1', displayName: '课程教师', role: 'teacher', courseId: 4, status: 'suspended', lastAccessedAt: null }],
      page: 2,
      pageSize: 5,
      total: 6,
      source: 'moodle_bridge',
      configured: true,
      message: undefined,
    });
    await expect(loadAdminCourses({ query: '储能', page: 3, pageSize: 10 })).resolves.toMatchObject({
      items: [{ id: 4, name: '储能技术', teacher: '课程教师', className: '四班', progress: 100, enrollmentCount: 30, activeUsers: 28 }],
      page: 3,
      pageSize: 10,
      total: 1,
      source: 'moodle_bridge',
      configured: true,
    });
    expect(vi.mocked(fetch).mock.calls[0]?.[0]).toBe('/api/admin/users?page=2&page_size=5&query=%E6%95%99%E5%B8%88&role=teacher');
    expect(vi.mocked(fetch).mock.calls[1]?.[0]).toBe('/api/admin/courses?page=3&page_size=10&query=%E5%82%A8%E8%83%BD');
  });

  it('normalizes the admin moderation queue and sends auditable decisions', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'reply-1', content_type: 'reply', topic_id: 'topic-1', reply_id: 'reply-1', title: '待审核主题', body: '待核对内容', status: 'pending_review', author_ref: 'u_pseudo', created_at: '2026-07-26', updated_at: '2026-07-26' }], page: 1, page_size: 20, total: 1 } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'reply-1', content_type: 'reply', topic_id: 'topic-1', reply_id: 'reply-1', decision: 'approve', status: 'visible' } }) } as Response);
    await expect(loadAdminModeration({ query: '待审核', contentType: 'reply', page: 2, pageSize: 10 })).resolves.toEqual({
      items: [{ id: 'reply-1', contentType: 'reply', topicId: 'topic-1', replyId: 'reply-1', title: '待审核主题', body: '待核对内容', status: 'pending_review', authorRef: 'u_pseudo', createdAt: '2026-07-26', updatedAt: '2026-07-26' }],
      page: 1,
      pageSize: 20,
      total: 1,
    });
    await expect(decideAdminModeration('reply', 'reply-1', 'approve', '核对通过', 'csrf-fixture', 'moderation-key')).resolves.toMatchObject({ id: 'reply-1', contentType: 'reply', decision: 'approve', status: 'visible' });
    const calls = vi.mocked(fetch).mock.calls;
    expect(calls[0]?.[0]).toBe('/api/admin/moderation?page=2&page_size=10&query=%E5%BE%85%E5%AE%A1%E6%A0%B8&content_type=reply');
    const headers = calls[1]?.[1]?.headers as Record<string, string>;
    expect(headers['Idempotency-Key']).toBe('moderation-key');
    expect(headers['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(JSON.parse(String(calls[1]?.[1]?.body))).toEqual({ decision: 'approve', reason: '核对通过' });
  });

  it('sends admin knowledge-base write headers and raw file bodies', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'kb-1', version_name: 'v1', status: 'draft', manifest_sha256: 'hash', workflow_id: 'flow', source_count: 0, hit_status: 'not_tested' } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'file-1', version_id: 'kb-1', filename: 'notes.md', sha256: 'file-hash', size_bytes: 4, status: 'accepted' } }) } as Response);
    await createKnowledgeBaseVersion('v1', 'flow', 'csrf-fixture', 'kb-create-key');
    await uploadKnowledgeBaseFile('kb-1', new Blob(['test'], { type: 'text/markdown' }), 'notes.md', 'csrf-fixture', 'kb-upload-key');
    const calls = vi.mocked(fetch).mock.calls;
    const createHeaders = calls[0]?.[1]?.headers as Record<string, string>;
    const uploadOptions = calls[1]?.[1] as RequestInit;
    const uploadHeaders = uploadOptions.headers as Record<string, string>;
    expect(createHeaders['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(createHeaders['Idempotency-Key']).toBe('kb-create-key');
    expect(uploadHeaders['X-Moodle-Sesskey']).toBe('csrf-fixture');
    expect(uploadHeaders['Idempotency-Key']).toBe('kb-upload-key');
    expect(uploadOptions.body).toBeInstanceOf(Blob);
  });

  it('normalizes knowledge graph nodes and follows a selected node to its neighbors', async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { items: [{ id: 'kp-3-4', name: '并网控制', chapter_id: 3, category: '概念性' }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { id: 'kp-3-4', name: '并网控制', chapter_id: 3, category: '概念性', description: '控制目标', neighbors: [{ id: 'kp-3-2', name: '系统组成', chapter_id: 3, relation_type: 'prerequisite' }] } }) } as Response)
      .mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: { path: ['kp-3-1', 'kp-3-2', 'kp-3-4'], depth: 2 } }) } as Response);
    await expect(loadKnowledgeGraphNodes()).resolves.toEqual([{ id: 'kp-3-4', name: '并网控制', chapterId: 3, category: '概念性', description: '', neighbors: [] }]);
    await expect(loadKnowledgeGraphNode('kp-3-4')).resolves.toMatchObject({ chapterId: 3, description: '控制目标', neighbors: [{ id: 'kp-3-2', relationType: 'prerequisite' }] });
    await expect(loadKnowledgeGraphPath('kp-3-1', 'kp-3-4')).resolves.toEqual({ path: ['kp-3-1', 'kp-3-2', 'kp-3-4'], depth: 2 });
    expect(vi.mocked(fetch).mock.calls[0]?.[0]).toBe('/api/knowledge-graph/search?limit=100');
    expect(vi.mocked(fetch).mock.calls[1]?.[0]).toBe('/api/knowledge-graph/nodes/kp-3-4');
    expect(vi.mocked(fetch).mock.calls[2]?.[0]).toBe('/api/knowledge-graph/paths?from=kp-3-1&to=kp-3-4&max_depth=8');
  });

  it('normalizes a course-scoped graph snapshot and rejects dangling edges', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({ ok: true, json: async () => ({ status: 'ok', data: {
      nodes: [
        { id: 'kp-1', name: '基础', chapter_id: 1, category: '概念' },
        { id: 'kp-2', name: '进阶', chapter_id: 2, category: '应用' },
      ],
      edges: [
        { source_id: 'kp-1', target_id: 'kp-2', relation_type: 'prerequisite' },
        { source_id: 'kp-1', target_id: 'other-course', relation_type: 'related' },
        { source_id: 'other-course', target_id: 'kp-2', relation_type: 'related' },
      ],
    } }) } as Response);
    await expect(loadKnowledgeGraph()).resolves.toEqual({
      nodes: [
        { id: 'kp-1', name: '基础', chapterId: 1, category: '概念', description: '', neighbors: [] },
        { id: 'kp-2', name: '进阶', chapterId: 2, category: '应用', description: '', neighbors: [] },
      ],
      edges: [{ id: 'kp-1:kp-2:0', sourceId: 'kp-1', targetId: 'kp-2', relationType: 'prerequisite' }],
    });
    expect(vi.mocked(fetch).mock.calls[0]?.[0]).toBe('/api/knowledge-graph/graph');
  });

  it('normalizes the seven-kind global search response and preserves bounded filters', async () => {
    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 7,
      query: 'Unified',
      kind: 'all',
      items: [
        { kind: 'course', id: '7', title: 'Unified Course', summary: '课程教师 · 测试班', chapter_id: null },
        { kind: 'resource', id: 'res-unified', title: 'Unified Resource', summary: 'resource.pdf', chapter_id: 3 },
      ],
      counts: { course: 1, chapter: 1, resource: 1, assignment: 1, exam: 1, discussion: 1, knowledge: 1 },
      page: 1,
      page_size: 2,
      total: 7,
    }));

    await expect(loadGlobalSearch(' Unified ', { page: 1, pageSize: 2 })).resolves.toEqual({
      courseId: 7,
      query: 'Unified',
      kind: 'all',
      items: [
        { kind: 'course', id: '7', title: 'Unified Course', summary: '课程教师 · 测试班', chapterId: null },
        { kind: 'resource', id: 'res-unified', title: 'Unified Resource', summary: 'resource.pdf', chapterId: 3 },
      ],
      counts: { course: 1, chapter: 1, resource: 1, assignment: 1, exam: 1, discussion: 1, knowledge: 1 },
      page: 1,
      pageSize: 2,
      total: 7,
    });
    expect(vi.mocked(fetch).mock.calls[0]?.[0]).toBe('/api/search?q=Unified&kind=all&page=1&page_size=2');
  });

  it('rejects global search DTO coercion and inconsistent filtered totals', async () => {
    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 1,
      query: 'Unified',
      kind: 'resource',
      items: [{ kind: 'resource', id: 'res-1', title: 'Unified Resource', summary: '', chapter_id: '3' }],
      counts: { course: 0, chapter: 0, resource: 1, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
      page: 1,
      page_size: 20,
      total: 2,
    }));
    await expect(loadGlobalSearch('Unified', { kind: 'resource' })).rejects.toMatchObject({ code: 'invalid_global_search_payload' });

    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 1,
      query: 'Unified',
      kind: 'all',
      items: [],
      counts: { course: 1, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
      page: 1,
      page_size: 20,
      total: 0,
    }));
    await expect(loadGlobalSearch('Unified')).rejects.toMatchObject({ code: 'invalid_global_search_payload' });

    vi.mocked(fetch).mockResolvedValue({ ok: true, status: 200, json: async () => ({ status: 'ok' }) } as Response);
    await expect(loadGlobalSearch('Unified')).rejects.toMatchObject({ code: 'invalid_global_search_payload' });

    await expect(loadGlobalSearch('Unified\nChapter')).rejects.toMatchObject({ code: 'invalid_global_search_filter' });
  });

  it('rejects a course result whose item ID does not match the response course scope', async () => {
    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 1,
      query: 'Unified',
      kind: 'all',
      items: [{ kind: 'course', id: '2', title: '越界课程', summary: '不属于当前课程', chapter_id: null }],
      counts: { course: 1, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 },
      page: 1,
      page_size: 20,
      total: 1,
    }));
    await expect(loadGlobalSearch('Unified')).rejects.toMatchObject({ code: 'invalid_global_search_payload' });
  });

  it('rejects conflicting camelCase and snake_case global-search aliases', async () => {
    const emptyCounts = { course: 0, chapter: 0, resource: 0, assignment: 0, exam: 0, discussion: 0, knowledge: 0 };
    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 1,
      courseId: 2,
      query: 'Unified',
      kind: 'all',
      items: [],
      counts: emptyCounts,
      page: 1,
      page_size: 20,
      total: 0,
    }));
    await expect(loadGlobalSearch('Unified')).rejects.toMatchObject({ code: 'invalid_global_search_payload' });

    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 1,
      query: 'Unified',
      kind: 'all',
      items: [],
      counts: emptyCounts,
      page: 1,
      page_size: 20,
      pageSize: 10,
      total: 0,
    }));
    await expect(loadGlobalSearch('Unified')).rejects.toMatchObject({ code: 'invalid_global_search_payload' });

    vi.mocked(fetch).mockResolvedValue(apiResponse({
      course_id: 1,
      query: 'Unified',
      kind: 'resource',
      items: [{ kind: 'resource', id: 'res-1', title: 'Unified Resource', summary: '', chapter_id: 3, chapterId: 4 }],
      counts: { ...emptyCounts, resource: 1 },
      page: 1,
      page_size: 20,
      total: 1,
    }));
    await expect(loadGlobalSearch('Unified', { kind: 'resource' })).rejects.toMatchObject({ code: 'invalid_global_search_payload' });
  });
});
