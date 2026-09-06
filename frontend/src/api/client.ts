import type { Activity, ActivityGroup, ActivityGroupsState, ActivityKind, ActivityResults, ActivityResponse, AdminBackupStatus, AdminCourse, AdminCourseDirectory, AdminDirectoryRole, AdminModerationDecision, AdminModerationItem, AdminModerationQueue, AdminStatus, AdminUser, AdminUserDirectory, AgentContext, ApiEnvelope, Assignment, AssignmentDetail, AssignmentDraft, AssignmentGrade, AssignmentQuestion, AssignmentSubmission, AuditLogEntry, Chapter, ClassroomDisplayMember, ClassroomRoster, CourseList, CourseSort, CourseSummary, DiscussionReply, DiscussionTopic, Exam, ExamAttempt, ExamDetail, ExamDraft, ExamSubmission, FavoriteResource, GlobalSearchFilterKind, GlobalSearchFilters, GlobalSearchItem, GlobalSearchKind, GlobalSearchResult, Gradebook, KnowledgeGraphNode, KnowledgeGraphPath, KnowledgeGraphSnapshot, KnowledgeBaseFile, KnowledgeBaseHitTest, KnowledgeBaseVersion, KnowledgeBaseVersionStatus, LearningPosition, NotificationItem, ProfilePoint, RandomSelectionRecord, RandomSelectionState, Recommendation, Resource, ResourceAnnotations, ResourceNote, ResourceProgress, ScenarioSession, Session, SessionPayload, StudentTask, StudentTaskCounts, StudentTaskFilters, StudentTaskKind, StudentTaskList, StudentTaskStatus, TeacherAssignment, TeacherExam, TeacherQuestion, TeacherResource, TeacherResourceRevision, TeacherResourceStatus, QuestionType } from '../types';

type RawChapter = { id: number; name: string; progress?: number; status?: string; lessons?: number; lesson_count?: number; duration?: string };
type RawCourseSummary = { id: number; name?: string; teacher?: string; teacher_name?: string; class_name?: string; className?: string; status?: string; progress?: number; chapter_count?: number; chapterCount?: number; resource_count?: number; resourceCount?: number; last_accessed_at?: string | null; lastAccessedAt?: string | null };
type RawGraphNeighbor = { id: string; name: string; chapter_id?: number; chapterId?: number; relation_type?: string; relationType?: string };
type RawGraphNode = { id: string; name: string; chapter_id?: number; chapterId?: number; category?: string; description?: string; neighbors?: RawGraphNeighbor[] };
type RawGraphEdge = { id?: string; source_id?: string; sourceId?: string; target_id?: string; targetId?: string; relation_type?: string; relationType?: string };
type RawAssignment = { id: string; title: string; type?: string; status?: string; dueAt?: string; due_at?: string; questionCount?: number; question_count?: number; question_ids?: string[]; score?: number | null; progress?: number; allow_attempts?: number; allowAttempts?: number };
type RawStudentTask = { id?: unknown; source_id?: unknown; sourceId?: unknown; kind?: unknown; title?: unknown; summary?: unknown; status?: unknown; due_at?: unknown; dueAt?: unknown; updated_at?: unknown; updatedAt?: unknown; progress?: unknown };
type RawStudentTaskCounts = { by_status?: unknown; byStatus?: unknown; by_kind?: unknown; byKind?: unknown };
type RawStudentTaskList = { items?: unknown; page?: unknown; page_size?: unknown; pageSize?: unknown; total?: unknown; counts?: unknown };
type RawGlobalSearchItem = { id?: unknown; kind?: unknown; title?: unknown; summary?: unknown; chapter_id?: unknown; chapterId?: unknown };
type RawGlobalSearchResult = { course_id?: unknown; courseId?: unknown; query?: unknown; kind?: unknown; items?: unknown; counts?: unknown; page?: unknown; page_size?: unknown; pageSize?: unknown; total?: unknown };
type RawExamAttempt = { attempt: number; started_at?: string; startedAt?: string; deadline_at?: string; deadlineAt?: string; status?: ExamAttempt['status']; submitted_at?: string | null; submittedAt?: string | null };
type RawExamSubmission = { id: string; exam_id?: string; examId?: string; attempt?: number; submitted_at?: string; submittedAt?: string; status?: string; score?: number; max_score?: number; maxScore?: number; needs_review?: boolean; needsReview?: boolean };
type RawExam = { id: string; title: string; status?: string; availability?: Exam['availability']; open_at?: string; openAt?: string; close_at?: string; closeAt?: string; duration_seconds?: number; durationSeconds?: number; allow_attempts?: number; allowAttempts?: number; question_ids?: string[]; question_count?: number; questionCount?: number; questions?: RawQuestion[]; my_attempts?: RawExamAttempt[]; myAttempts?: RawExamAttempt[]; my_submissions?: RawExamSubmission[]; mySubmissions?: RawExamSubmission[]; attempt?: RawExamAttempt; server_now?: string; serverNow?: string };
type RawQuestion = { id: string; prompt: string; question_type?: QuestionType; questionType?: QuestionType; options?: string[]; max_score?: number; maxScore?: number };
type RawTeacherQuestion = RawQuestion & { answer?: string | string[] | boolean | null; answer_json?: unknown; rubric?: string; chapter_id?: number | null; chapter_name?: string | null; node_id?: string | null; node_name?: string | null; status?: TeacherQuestion['status']; version?: number; created_by?: string; updated_at?: string };
type RawTeacherAssignment = RawAssignment & { question_ids?: string[]; status?: TeacherAssignment['status']; submitted_count?: number; graded_count?: number; version?: number };
type RawTeacherExam = RawExam & { status?: TeacherExam['status']; created_by?: string; updated_at?: string; version?: number };
type RawGradebook = { assignment_id?: string; assignmentId?: string; assignments?: Array<{ id: string; title: string; status: string; submitted_count?: number; submittedCount?: number; graded_count?: number; gradedCount?: number; completion_rate?: number; completionRate?: number; average_score?: number; averageScore?: number; average_ratio?: number; averageRatio?: number; question_count?: number; questionCount?: number }>; students?: Array<{ user_uid?: string; userUid?: string; submission_count?: number; submissionCount?: number; completed_assignments?: number; completedAssignments?: number; average_ratio?: number; averageRatio?: number; needs_review?: boolean; needsReview?: boolean; risk_level?: 'high' | 'normal'; riskLevel?: 'high' | 'normal' }>; knowledge_points?: Array<{ id: string; name: string; score?: number; max_score?: number; maxScore?: number; attempts?: number; ratio?: number; status?: 'weak' | 'learning' | 'mastered' }>; risk_students?: Array<{ user_uid?: string; userUid?: string; submission_count?: number; submissionCount?: number; completed_assignments?: number; completedAssignments?: number; average_ratio?: number; averageRatio?: number; needs_review?: boolean; needsReview?: boolean; risk_level?: 'high' | 'normal'; riskLevel?: 'high' | 'normal' }> };
type RawGrade = { id: string; question_id?: string; questionId?: string; score?: number; max_score?: number; maxScore?: number; feedback?: string | null; source?: string; reviewed_by?: string | null; review_reason?: string | null };
type RawSubmission = { id?: string; submission_id?: string; assignment_id?: string; assignmentId?: string; attempt?: number; status?: string; created_at?: string; createdAt?: string; answers?: Record<string, unknown>; score?: number | null; max_score?: number | null; maxScore?: number | null; needs_review?: boolean; needsReview?: boolean; grades?: RawGrade[] };
type RawDraft = { assignment_id?: string; assignmentId?: string; attempt?: number; answers?: Record<string, unknown>; version?: number; updated_at?: string | null; updatedAt?: string | null; has_saved_draft?: boolean; hasSavedDraft?: boolean };
type RawDiscussionReply = { id: string; topic_id?: string; topicId?: string; author_label?: string; authorLabel?: string; body: string; status?: string; created_at?: string; createdAt?: string };
type RawDiscussion = { id: string; title: string; body: string; status: DiscussionTopic['status']; pinned?: boolean; author_label?: string; authorLabel?: string; reply_count?: number; replyCount?: number; created_at?: string; createdAt?: string; updated_at?: string; updatedAt?: string; replies?: RawDiscussionReply[]; can_moderate?: boolean; canModerate?: boolean };
type RawNotification = { id: string; audience: string; title: string; body: string; created_by?: string; createdBy?: string; created_at?: string; createdAt?: string; is_read?: boolean; isRead?: boolean };
type RawActivityOption = { id: string; label: string; count?: number; ratio?: number };
type RawActivityResponse = { id: string; activity_id?: string; activityId?: string; attempt?: number; answers?: string[]; submitted_at?: string; submittedAt?: string };
type RawActivity = { id: string; kind: ActivityKind; title: string; body: string; options?: RawActivityOption[]; status: Activity['status']; max_attempts?: number; maxAttempts?: number; has_responded?: boolean; hasResponded?: boolean; attempts_used?: number; attemptsUsed?: number; can_respond?: boolean; canRespond?: boolean; can_reopen?: boolean; canReopen?: boolean; next_attempt?: number | null; nextAttempt?: number | null; my_response?: RawActivityResponse | null; myResponse?: RawActivityResponse | null };
type RawActivityResults = { activity_id?: string; activityId?: string; kind: ActivityKind; total_responses?: number; totalResponses?: number; has_responded?: boolean; hasResponded?: boolean; results_available?: boolean; resultsAvailable?: boolean; options?: RawActivityOption[]; participants?: Array<{ user_ref?: string; userRef?: string; submitted_at?: string; submittedAt?: string }> };
type RawClassroomDisplayMember = { display_name?: string; displayName?: string; name?: string; is_me?: boolean; isMe?: boolean };
type RawClassroomRosterMember = RawClassroomDisplayMember & { user_ref?: string; userRef?: string; id?: string };
type RawClassroomRoster = { configured?: boolean; roster_configured?: boolean; rosterConfigured?: boolean; items?: RawClassroomRosterMember[]; students?: RawClassroomRosterMember[]; total?: number; student_count?: number; studentCount?: number; message?: string | null };
type RawRandomSelectionRecord = RawClassroomDisplayMember & { user_ref?: string; userRef?: string; cycle?: number; sequence?: number; round?: number; selected_at?: string; selectedAt?: string; member?: RawClassroomDisplayMember; participant?: RawClassroomDisplayMember; selected?: RawClassroomDisplayMember };
type RawRandomSelectionState = { activity_id?: string; activityId?: string; kind?: 'random_selection'; round?: number; current_round?: number; currentRound?: number; latest?: RawRandomSelectionRecord | null; latest_selection?: RawRandomSelectionRecord | null; latestSelection?: RawRandomSelectionRecord | null; selection?: RawRandomSelectionRecord | null; history?: RawRandomSelectionRecord[]; selections?: RawRandomSelectionRecord[]; remaining_count?: number | null; remainingCount?: number | null; remaining?: number | null; can_select?: boolean; canSelect?: boolean };
type RawActivityGroupMember = RawClassroomDisplayMember & { user_ref?: string; userRef?: string };
type RawActivityGroup = { id?: string; name?: string; group_name?: string; groupName?: string; label?: string; members?: RawActivityGroupMember[]; items?: RawActivityGroupMember[] };
type RawActivityGroupsState = { activity_id?: string; activityId?: string; kind?: 'group_task'; revision?: number | null; generated_at?: string | null; generatedAt?: string | null; groups?: RawActivityGroup[]; my_group?: RawActivityGroup | null; myGroup?: RawActivityGroup | null; group?: RawActivityGroup | null; can_generate?: boolean; canGenerate?: boolean };
type RawResource = { id: string; title?: string; sourceFile?: string; source_file?: string; normalized_file?: string; chapterId?: number; chapter_id?: number; pageStart?: number; page_start?: number; pageCount?: number; page_end?: number; type?: Resource['type']; version?: string; status?: string; available?: boolean; mount_status?: Resource['mountStatus']; locator?: string | null; favorite_at?: string | null; favoriteAt?: string | null; note_count?: number; noteCount?: number };
type RawTeacherResourceRevision = { id: string; resource_id?: string; resourceId?: string; revision: number; filename: string; sha256: string; size_bytes?: number; sizeBytes?: number; uploaded_by?: string; uploadedBy?: string; status?: TeacherResourceRevision['status']; created_at?: string; createdAt?: string };
type RawTeacherResource = RawResource & { title?: string; source_reference?: string; sourceReference?: string; status?: TeacherResourceStatus; revision?: number; deduplicated?: boolean; revisions?: RawTeacherResourceRevision[] };
type RawProfilePoint = { id: string; name: string; status: ProfilePoint['status']; ratio?: number | null };
type RawRecommendation = { id?: string; node_id?: string; title: string; type?: string; reason?: string; resourceId?: string; resource_id?: string };
type RawAdminStatus = { adapter?: string; workflow_configured?: boolean; workflowConfigured?: boolean; mock_workflow?: boolean; mockWorkflow?: boolean; published_kb?: { id: string; version_name?: string; versionName?: string; status: string; hit_status?: string; hitStatus?: string } | null; backup?: { managed_by?: string; managedBy?: string; status: string } };
type RawAdminUser = { id: string; display_name?: string; displayName?: string; role: AdminDirectoryRole; course_id?: number; courseId?: number; status?: AdminUser['status']; last_accessed_at?: string | null; lastAccessedAt?: string | null };
type RawAdminCourse = RawCourseSummary & { enrollment_count?: number | null; enrollmentCount?: number | null; active_users?: number | null; activeUsers?: number | null };
type RawAdminDirectory<T> = { items?: T[]; page?: number; page_size?: number; total?: number; source?: string; configured?: boolean; message?: string };
type RawKbVersion = { id: string; version_name?: string; versionName?: string; status: KnowledgeBaseVersionStatus; manifest_sha256?: string; manifestSha256?: string; workflow_id?: string; workflowId?: string; source_count?: number; sourceCount?: number; hit_status?: string; hitStatus?: string; created_by?: string; createdBy?: string; updated_at?: string; updatedAt?: string };
type RawKbFile = { id: string; version_id?: string; versionId?: string; filename: string; sha256: string; size_bytes?: number; sizeBytes?: number; status?: string; error_message?: string; errorMessage?: string; created_at?: string; createdAt?: string };
type RawKbHitTest = { id: string; version_id?: string; versionId?: string; case_id?: string; caseId?: string; question: string; expected_chapter?: string; expectedChapter?: string; actual_sources?: Array<Record<string, unknown>>; actualSources?: Array<Record<string, unknown>>; status: string; request_id?: string; requestId?: string; actor_uid?: string; actorUid?: string; created_at?: string; createdAt?: string };
type RawAuditLog = { id: string; actor_uid?: string; actorUid?: string; action: string; object_type?: string; objectType?: string; object_id?: string; objectId?: string; result: string; reason?: string; request_id?: string; requestId?: string; created_at?: string; createdAt?: string };
type RawModerationItem = { id: string; content_type?: 'topic' | 'reply'; contentType?: 'topic' | 'reply'; topic_id?: string; topicId?: string; reply_id?: string | null; replyId?: string | null; title: string; body: string; status: 'pending_review'; author_ref?: string; authorRef?: string; created_at?: string; createdAt?: string; updated_at?: string; updatedAt?: string };
type RawModerationDecision = { id: string; content_type?: 'topic' | 'reply'; contentType?: 'topic' | 'reply'; topic_id?: string; topicId?: string; reply_id?: string | null; replyId?: string | null; decision: 'approve' | 'reject'; status: string };
type RawBackupStatus = { managed_by?: string; managedBy?: string; verification: string; restore_rehearsal?: string; restoreRehearsal?: string; secrets_excluded?: boolean; secretsExcluded?: boolean; status: string };

function normalizeAdminStatus(item: RawAdminStatus): AdminStatus {
  return {
    adapter: item.adapter || 'unknown',
    workflowConfigured: Boolean(item.workflowConfigured ?? item.workflow_configured),
    mockWorkflow: Boolean(item.mockWorkflow ?? item.mock_workflow),
    publishedKb: item.published_kb ? {
      id: item.published_kb.id,
      versionName: item.published_kb.versionName || item.published_kb.version_name || '',
      status: item.published_kb.status,
      hitStatus: item.published_kb.hitStatus || item.published_kb.hit_status || '',
    } : null,
    backup: {
      managedBy: item.backup?.managedBy || item.backup?.managed_by || 'unknown',
      status: item.backup?.status || 'unknown',
    },
  };
}

function normalizeAdminUser(item: RawAdminUser): AdminUser {
  return {
    id: item.id,
    displayName: item.displayName || item.display_name || '未命名用户',
    role: item.role,
    courseId: Number(item.courseId ?? item.course_id ?? 0),
    status: item.status || 'unknown',
    lastAccessedAt: item.lastAccessedAt ?? item.last_accessed_at ?? null,
  };
}

function normalizeAdminCourse(item: RawAdminCourse): AdminCourse {
  return {
    ...normalizeCourseSummary(item),
    enrollmentCount: item.enrollmentCount ?? item.enrollment_count ?? null,
    activeUsers: item.activeUsers ?? item.active_users ?? null,
  };
}

function normalizeCourseSummary(item: RawCourseSummary): CourseSummary {
  return {
    id: Number(item.id),
    name: item.name || '未命名课程',
    teacher: item.teacher || item.teacher_name || '课程教师',
    className: item.className || item.class_name || '未命名班级',
    status: item.status === 'archived' ? 'archived' : 'active',
    progress: Math.max(0, Math.min(100, Number(item.progress || 0))),
    chapterCount: Number(item.chapterCount ?? item.chapter_count ?? 0),
    resourceCount: Number(item.resourceCount ?? item.resource_count ?? 0),
    lastAccessedAt: item.lastAccessedAt ?? item.last_accessed_at ?? null,
  };
}

function normalizeKbVersion(item: RawKbVersion): KnowledgeBaseVersion {
  return {
    id: item.id,
    versionName: item.versionName || item.version_name || '',
    status: item.status,
    manifestSha256: item.manifestSha256 || item.manifest_sha256 || '',
    workflowId: item.workflowId || item.workflow_id || '',
    sourceCount: Number(item.sourceCount ?? item.source_count ?? 0),
    hitStatus: item.hitStatus || item.hit_status || 'not_tested',
    createdBy: item.createdBy || item.created_by || '',
    updatedAt: item.updatedAt || item.updated_at || '',
  };
}

function normalizeKbFile(item: RawKbFile): KnowledgeBaseFile {
  return {
    id: item.id,
    versionId: item.versionId || item.version_id || '',
    filename: item.filename,
    sha256: item.sha256,
    sizeBytes: Number(item.sizeBytes ?? item.size_bytes ?? 0),
    status: item.status || 'accepted',
    errorMessage: item.errorMessage || item.error_message || '',
    createdAt: item.createdAt || item.created_at || '',
  };
}

function normalizeKbHitTest(item: RawKbHitTest): KnowledgeBaseHitTest {
  return {
    id: item.id,
    versionId: item.versionId || item.version_id || '',
    caseId: item.caseId || item.case_id || '',
    question: item.question,
    expectedChapter: item.expectedChapter || item.expected_chapter || '',
    actualSources: item.actualSources || item.actual_sources || [],
    status: item.status,
    requestId: item.requestId || item.request_id || '',
    actorUid: item.actorUid || item.actor_uid || '',
    createdAt: item.createdAt || item.created_at || '',
  };
}

function normalizeAuditLog(item: RawAuditLog): AuditLogEntry {
  return {
    id: item.id,
    actorUid: item.actorUid || item.actor_uid || '',
    action: item.action,
    objectType: item.objectType || item.object_type || '',
    objectId: item.objectId || item.object_id || '',
    result: item.result,
    reason: item.reason || '',
    requestId: item.requestId || item.request_id || '',
    createdAt: item.createdAt || item.created_at || '',
  };
}

function normalizeModerationItem(item: RawModerationItem): AdminModerationItem {
  return {
    id: item.id,
    contentType: item.contentType || item.content_type || 'topic',
    topicId: item.topicId || item.topic_id || '',
    replyId: item.replyId ?? item.reply_id ?? null,
    title: item.title || '',
    body: item.body || '',
    status: 'pending_review',
    authorRef: item.authorRef || item.author_ref || '',
    createdAt: item.createdAt || item.created_at || '',
    updatedAt: item.updatedAt || item.updated_at || '',
  };
}

function normalizeModerationDecision(item: RawModerationDecision): AdminModerationDecision {
  return {
    id: item.id,
    contentType: item.contentType || item.content_type || 'topic',
    topicId: item.topicId || item.topic_id || '',
    replyId: item.replyId ?? item.reply_id ?? null,
    decision: item.decision,
    status: item.status,
  };
}

function normalizeBackupStatus(item: RawBackupStatus): AdminBackupStatus {
  return {
    managedBy: item.managedBy || item.managed_by || 'unknown',
    verification: item.verification,
    restoreRehearsal: item.restoreRehearsal || item.restore_rehearsal || 'unknown',
    secretsExcluded: Boolean(item.secretsExcluded ?? item.secrets_excluded),
    status: item.status,
  };
}

function normalizeGraphNode(item: RawGraphNode): KnowledgeGraphNode {
  return {
    id: item.id,
    name: item.name,
    chapterId: Number(item.chapterId ?? item.chapter_id ?? 0),
    category: item.category || '知识点',
    description: item.description || '',
    neighbors: (item.neighbors || []).map((neighbor) => ({
      id: neighbor.id,
      name: neighbor.name,
      chapterId: Number(neighbor.chapterId ?? neighbor.chapter_id ?? 0),
      relationType: neighbor.relationType || neighbor.relation_type || 'related',
    })),
  };
}

export class ApiError extends Error {
  readonly code: string;
  readonly requestId?: string;

  constructor(message: string, code = 'api_error', requestId?: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.requestId = requestId;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, { credentials: 'same-origin', ...options });
  const payload = (await response.json().catch(() => null)) as ApiEnvelope<T> | null;
  if (response.status === 401 || payload?.error?.code === 'session_expired' || payload?.error?.code === 'not_authenticated') {
    if (typeof window !== 'undefined') window.dispatchEvent(new Event('course:session-expired'));
  }
  if (!response.ok || !payload || payload.status !== 'ok' || payload.data === null) {
    throw new ApiError(payload?.error?.message || `服务返回 HTTP ${response.status}`, payload?.error?.code, payload?.request_id);
  }
  return payload.data;
}

export async function openSession(): Promise<Session> {
  const payload = await request<SessionPayload>('/api/course/session/open', { method: 'POST' });
  return {
    role: payload.role || 'student',
    courseId: payload.course_id || 1,
    csrfToken: payload.csrf_token || '',
    features: payload.features || {},
  };
}

export async function loadCourses(filters: { sort?: CourseSort; page?: number; pageSize?: number } = {}): Promise<CourseList> {
  const params = new URLSearchParams({
    sort: filters.sort || 'last_accessed',
    page: String(filters.page || 1),
    page_size: String(filters.pageSize || 20),
  });
  const payload = await request<{ items?: RawCourseSummary[]; page?: number; page_size?: number; total?: number }>(`/api/courses?${params.toString()}`);
  return {
    items: (payload.items || []).map(normalizeCourseSummary),
    page: Number(payload.page || 1),
    pageSize: Number(payload.page_size || 20),
    total: Number(payload.total || 0),
  };
}

const globalSearchKinds: GlobalSearchKind[] = ['course', 'chapter', 'resource', 'assignment', 'exam', 'discussion', 'knowledge'];
const globalSearchFilterKinds: GlobalSearchFilterKind[] = ['all', ...globalSearchKinds];
const globalSearchIdPattern = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/;

function invalidGlobalSearchPayload(field: string): never {
  throw new ApiError(`全局搜索响应格式错误：${field}`, 'invalid_global_search_payload');
}

function globalSearchInteger(value: unknown, field: string, minimum = 0): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < minimum) invalidGlobalSearchPayload(field);
  return value;
}

function globalSearchText(value: unknown, field: string, maximum: number, allowEmpty = false): string {
  if (typeof value !== 'string' || value.length > maximum || hasAsciiControlCharacter(value) || (!allowEmpty && !value.trim())) invalidGlobalSearchPayload(field);
  return value;
}

function globalSearchAlias(record: Record<string, unknown>, camelName: string, snakeName: string, field: string): unknown {
  const hasCamel = Object.prototype.hasOwnProperty.call(record, camelName);
  const hasSnake = Object.prototype.hasOwnProperty.call(record, snakeName);
  if (hasCamel && hasSnake && !Object.is(record[camelName], record[snakeName])) invalidGlobalSearchPayload(field);
  return hasCamel ? record[camelName] : record[snakeName];
}

function normalizeGlobalSearchItem(value: unknown, index: number, courseId: number): GlobalSearchItem {
  if (!isRecord(value)) invalidGlobalSearchPayload(`items[${index}]`);
  const item = value as RawGlobalSearchItem;
  if (typeof item.kind !== 'string' || !globalSearchKinds.includes(item.kind as GlobalSearchKind)) invalidGlobalSearchPayload(`items[${index}].kind`);
  const kind = item.kind as GlobalSearchKind;
  const id = globalSearchText(item.id, `items[${index}].id`, 200);
  if (!globalSearchIdPattern.test(id)) invalidGlobalSearchPayload(`items[${index}].id`);
  if (kind === 'course' && id !== String(courseId)) invalidGlobalSearchPayload(`items[${index}].id`);
  const chapterValue = globalSearchAlias(item, 'chapterId', 'chapter_id', `items[${index}].chapter_id`);
  const needsChapter = kind === 'chapter' || kind === 'resource' || kind === 'knowledge';
  if (needsChapter && (!Number.isSafeInteger(chapterValue) || Number(chapterValue) < 1)) invalidGlobalSearchPayload(`items[${index}].chapter_id`);
  if (!needsChapter && chapterValue !== null) invalidGlobalSearchPayload(`items[${index}].chapter_id`);
  return {
    id,
    kind,
    title: globalSearchText(item.title, `items[${index}].title`, 180),
    summary: globalSearchText(item.summary, `items[${index}].summary`, 240, true),
    chapterId: needsChapter ? Number(chapterValue) : null,
  };
}

export async function loadGlobalSearch(query: string, filters: GlobalSearchFilters = {}): Promise<GlobalSearchResult> {
  const normalizedQuery = query.trim();
  const kind = filters.kind || 'all';
  const page = filters.page ?? 1;
  const pageSize = filters.pageSize ?? 20;
  if (!normalizedQuery || normalizedQuery.length > 100 || hasAsciiControlCharacter(normalizedQuery)) throw new ApiError('搜索关键词无效', 'invalid_global_search_filter');
  if (!globalSearchFilterKinds.includes(kind) || !Number.isSafeInteger(page) || page < 1 || !Number.isSafeInteger(pageSize) || pageSize < 1 || pageSize > 50) {
    throw new ApiError('搜索筛选或分页参数无效', 'invalid_global_search_filter');
  }
  const params = new URLSearchParams({ q: normalizedQuery, kind, page: String(page), page_size: String(pageSize) });
  const payload = await request<RawGlobalSearchResult>(`/api/search?${params.toString()}`);
  if (!isRecord(payload) || !Array.isArray(payload.items) || !isRecord(payload.counts)) invalidGlobalSearchPayload('response');
  const rawCounts = payload.counts;
  const courseId = globalSearchInteger(globalSearchAlias(payload, 'courseId', 'course_id', 'course_id'), 'course_id', 1);
  if (payload.query !== normalizedQuery || payload.kind !== kind) invalidGlobalSearchPayload('query_or_kind');
  const responsePage = globalSearchInteger(payload.page, 'page', 1);
  const responsePageSize = globalSearchInteger(globalSearchAlias(payload, 'pageSize', 'page_size', 'page_size'), 'page_size', 1);
  if (responsePage !== page || responsePageSize !== pageSize || responsePageSize > 50) invalidGlobalSearchPayload('pagination');
  const counts = Object.fromEntries(globalSearchKinds.map((searchKind) => [
    searchKind,
    globalSearchInteger(rawCounts[searchKind], `counts.${searchKind}`),
  ])) as Record<GlobalSearchKind, number>;
  const total = globalSearchInteger(payload.total, 'total');
  const expectedTotal = kind === 'all' ? globalSearchKinds.reduce((sum, searchKind) => sum + counts[searchKind], 0) : counts[kind];
  if (total !== expectedTotal) invalidGlobalSearchPayload('total');
  const items = payload.items.map((item, index) => normalizeGlobalSearchItem(item, index, courseId));
  const expectedItems = Math.min(pageSize, Math.max(0, total - (page - 1) * pageSize));
  if (items.length !== expectedItems || (kind !== 'all' && items.some((item) => item.kind !== kind))) invalidGlobalSearchPayload('items');
  if (new Set(items.map((item) => `${item.kind}:${item.id}`)).size !== items.length) invalidGlobalSearchPayload('items.duplicate');
  return { courseId, query: normalizedQuery, kind, items, counts, page, pageSize, total };
}

export async function loadAdminStatus(): Promise<AdminStatus> {
  return normalizeAdminStatus(await request<RawAdminStatus>('/api/admin/status'));
}

export async function loadAdminBackupStatus(): Promise<AdminBackupStatus> {
  return normalizeBackupStatus(await request<RawBackupStatus>('/api/admin/backup/status'));
}

export async function loadAdminAuditLog(filters: { action?: string; objectType?: string; page?: number; pageSize?: number } = {}): Promise<{ items: AuditLogEntry[]; page: number; pageSize: number; total: number }> {
  const params = new URLSearchParams();
  if (filters.action) params.set('action', filters.action);
  if (filters.objectType) params.set('object_type', filters.objectType);
  if (filters.page) params.set('page', String(filters.page));
  if (filters.pageSize) params.set('page_size', String(filters.pageSize));
  const query = params.toString();
  const payload = await request<{ items?: RawAuditLog[]; page?: number; page_size?: number; total?: number }>(`/api/admin/audit-log${query ? `?${query}` : ''}`);
  return {
    items: (payload.items || []).map(normalizeAuditLog),
    page: Number(payload.page || 1),
    pageSize: Number(payload.page_size || 20),
    total: Number(payload.total || 0),
  };
}

export async function loadAdminModeration(filters: { query?: string; contentType?: 'topic' | 'reply'; page?: number; pageSize?: number } = {}): Promise<AdminModerationQueue> {
  const params = new URLSearchParams({ page: String(filters.page || 1), page_size: String(filters.pageSize || 20) });
  if (filters.query) params.set('query', filters.query);
  if (filters.contentType) params.set('content_type', filters.contentType);
  const payload = await request<{ items?: RawModerationItem[]; page?: number; page_size?: number; total?: number }>(`/api/admin/moderation?${params.toString()}`);
  return {
    items: (payload.items || []).map(normalizeModerationItem),
    page: Number(payload.page || 1),
    pageSize: Number(payload.page_size || 20),
    total: Number(payload.total || 0),
  };
}

export async function decideAdminModeration(contentType: 'topic' | 'reply', contentId: string, decision: 'approve' | 'reject', reason: string, csrfToken: string, idempotencyKey: string): Promise<AdminModerationDecision> {
  const payload = await request<RawModerationDecision>(`/api/admin/moderation/${encodeURIComponent(contentType)}/${encodeURIComponent(contentId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `admin-moderation-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ decision, reason }),
  });
  return normalizeModerationDecision(payload);
}

export async function loadAdminUsers(filters: { query?: string; role?: AdminDirectoryRole; page?: number; pageSize?: number } = {}): Promise<AdminUserDirectory> {
  const params = new URLSearchParams({ page: String(filters.page || 1), page_size: String(filters.pageSize || 20) });
  if (filters.query) params.set('query', filters.query);
  if (filters.role) params.set('role', filters.role);
  const payload = await request<RawAdminDirectory<RawAdminUser>>(`/api/admin/users?${params.toString()}`);
  return {
    items: (payload.items || []).map(normalizeAdminUser),
    page: Number(payload.page || 1),
    pageSize: Number(payload.page_size || 20),
    total: Number(payload.total || 0),
    source: payload.source || 'unknown',
    configured: Boolean(payload.configured),
    message: payload.message,
  };
}

export async function loadAdminCourses(filters: { query?: string; page?: number; pageSize?: number } = {}): Promise<AdminCourseDirectory> {
  const params = new URLSearchParams({ page: String(filters.page || 1), page_size: String(filters.pageSize || 20) });
  if (filters.query) params.set('query', filters.query);
  const payload = await request<RawAdminDirectory<RawAdminCourse>>(`/api/admin/courses?${params.toString()}`);
  return {
    items: (payload.items || []).map(normalizeAdminCourse),
    page: Number(payload.page || 1),
    pageSize: Number(payload.page_size || 20),
    total: Number(payload.total || 0),
    source: payload.source || 'unknown',
    configured: Boolean(payload.configured),
    message: payload.message,
  };
}

export async function loadKnowledgeBaseVersions(): Promise<KnowledgeBaseVersion[]> {
  const payload = await request<{ items?: RawKbVersion[] }>('/api/knowledge-base/versions');
  return (payload.items || []).map(normalizeKbVersion);
}

export async function createKnowledgeBaseVersion(versionName: string, workflowId: string, csrfToken: string, idempotencyKey: string): Promise<KnowledgeBaseVersion> {
  const payload = await request<RawKbVersion>('/api/knowledge-base/versions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `kb-create-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ version_name: versionName, workflow_id: workflowId }),
  });
  return normalizeKbVersion(payload);
}

export async function loadKnowledgeBaseFiles(versionId: string): Promise<KnowledgeBaseFile[]> {
  const payload = await request<{ items?: RawKbFile[] }>(`/api/knowledge-base/versions/${encodeURIComponent(versionId)}/files`);
  return (payload.items || []).map(normalizeKbFile);
}

export async function uploadKnowledgeBaseFile(versionId: string, file: Blob, filename: string, csrfToken: string, idempotencyKey: string): Promise<KnowledgeBaseFile> {
  const payload = await request<RawKbFile>(`/api/knowledge-base/versions/${encodeURIComponent(versionId)}/files?filename=${encodeURIComponent(filename)}`, {
    method: 'PUT',
    headers: { 'Content-Type': file.type || 'application/octet-stream', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `kb-upload-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: file,
  });
  return normalizeKbFile(payload);
}

export async function loadKnowledgeBaseHitTests(versionId: string): Promise<KnowledgeBaseHitTest[]> {
  const payload = await request<{ items?: RawKbHitTest[] }>(`/api/knowledge-base/versions/${encodeURIComponent(versionId)}/hit-tests`);
  return (payload.items || []).map(normalizeKbHitTest);
}

export async function runKnowledgeBaseHitTest(versionId: string, caseId: string, csrfToken: string, idempotencyKey: string): Promise<KnowledgeBaseHitTest> {
  const payload = await request<RawKbHitTest>(`/api/knowledge-base/versions/${encodeURIComponent(versionId)}/hit-tests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `kb-hit-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ case_id: caseId }),
  });
  return normalizeKbHitTest(payload);
}

export async function updateKnowledgeBaseStatus(versionId: string, status: KnowledgeBaseVersionStatus, csrfToken: string, idempotencyKey: string): Promise<KnowledgeBaseVersion> {
  const payload = await request<RawKbVersion>(`/api/knowledge-base/versions/${encodeURIComponent(versionId)}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `kb-status-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ status }),
  });
  return normalizeKbVersion(payload);
}

export async function rollbackKnowledgeBase(versionId: string, reason: string, csrfToken: string, idempotencyKey: string): Promise<KnowledgeBaseVersion> {
  const payload = await request<RawKbVersion>(`/api/knowledge-base/versions/${encodeURIComponent(versionId)}/rollback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `kb-rollback-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ reason }),
  });
  return normalizeKbVersion(payload);
}

export async function loadChapters(): Promise<Chapter[]> {
  const payload = await request<{ items?: RawChapter[] }>('/api/knowledge-graph/chapters');
  return (payload.items || []).map((item) => ({
    id: Number(item.id),
    name: item.name,
    progress: Number(item.progress || 0),
    status: item.status || (Number(item.progress || 0) > 0 ? '学习中' : '未开始'),
    lessons: Number(item.lessons || item.lesson_count || 0),
    duration: item.duration || '待估算',
  }));
}

export async function loadKnowledgeGraphNodes(query = ''): Promise<KnowledgeGraphNode[]> {
  const params = new URLSearchParams({ limit: '100' });
  if (query.trim()) params.set('q', query.trim());
  const payload = await request<{ items?: RawGraphNode[] }>(`/api/knowledge-graph/search?${params.toString()}`);
  return (payload.items || []).map(normalizeGraphNode);
}

export async function loadKnowledgeGraph(): Promise<KnowledgeGraphSnapshot> {
  const payload = await request<{ nodes?: RawGraphNode[]; edges?: RawGraphEdge[] }>('/api/knowledge-graph/graph');
  const nodes = (payload.nodes || []).map(normalizeGraphNode);
  const nodeIds = new Set(nodes.map((node) => node.id));
  const edges = (payload.edges || []).flatMap((item, index) => {
    const sourceId = item.sourceId || item.source_id || '';
    const targetId = item.targetId || item.target_id || '';
    if (!sourceId || !targetId || !nodeIds.has(sourceId) || !nodeIds.has(targetId)) return [];
    return [{
      id: item.id || `${sourceId}:${targetId}:${index}`,
      sourceId,
      targetId,
      relationType: item.relationType || item.relation_type || 'related',
    }];
  });
  return { nodes, edges };
}

export async function loadKnowledgeGraphNode(nodeId: string): Promise<KnowledgeGraphNode> {
  return normalizeGraphNode(await request<RawGraphNode>(`/api/knowledge-graph/nodes/${encodeURIComponent(nodeId)}`));
}

export async function loadKnowledgeGraphPath(startId: string, endId: string, maxDepth = 8): Promise<KnowledgeGraphPath> {
  const params = new URLSearchParams({ from: startId, to: endId, max_depth: String(maxDepth) });
  const payload = await request<{ path?: string[]; depth?: number }>(`/api/knowledge-graph/paths?${params.toString()}`);
  return { path: Array.isArray(payload.path) ? payload.path.map(String) : [], depth: Number(payload.depth || 0) };
}

export async function loadAssignments(): Promise<Assignment[]> {
  const payload = await request<{ items?: RawAssignment[] }>('/api/student/assignments');
  return (payload.items || []).map((item) => ({
    id: item.id,
    title: item.title,
    type: item.type || '课程作业',
    status: item.status === '进行中' || item.status === '已完成' || item.status === '已过期' ? item.status : '待完成',
    dueAt: item.dueAt || item.due_at || '未设置',
    questionCount: item.questionCount || item.question_ids?.length || 0,
    score: item.score ?? null,
    progress: Number(item.progress || 0),
    allowAttempts: Number(item.allowAttempts || item.allow_attempts || 1),
  }));
}

const studentTaskKinds: StudentTaskKind[] = ['assignment', 'exam', 'discussion', 'notification'];
const studentTaskStatuses: StudentTaskStatus[] = ['pending', 'in_progress', 'completed', 'expired'];

function invalidTaskPayload(field: string): never {
  throw new ApiError(`任务中心响应格式错误：${field}`, 'invalid_task_payload');
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function requiredTaskString(value: unknown, field: string, allowEmpty = false): string {
  if (typeof value !== 'string' || (!allowEmpty && !value.trim())) invalidTaskPayload(field);
  return value;
}

function taskNumber(value: unknown, field: string): number {
  const normalized = typeof value === 'number' ? value : typeof value === 'string' && value.trim() ? Number(value) : Number.NaN;
  if (!Number.isFinite(normalized)) invalidTaskPayload(field);
  return normalized;
}

function taskInteger(value: unknown, field: string, minimum = 0): number {
  const normalized = taskNumber(value, field);
  if (!Number.isInteger(normalized) || normalized < minimum) invalidTaskPayload(field);
  return normalized;
}

function normalizeTaskCountRecord<T extends string>(value: unknown, keys: readonly T[], field: string): Record<T, number> {
  if (!isRecord(value)) invalidTaskPayload(field);
  return Object.fromEntries(keys.map((key) => {
    if (value[key] === undefined) invalidTaskPayload(`${field}.${key}`);
    return [key, taskInteger(value[key], `${field}.${key}`)];
  })) as Record<T, number>;
}

function normalizeStudentTask(item: unknown, index: number): StudentTask {
  if (!isRecord(item)) invalidTaskPayload(`items[${index}]`);
  const raw = item as RawStudentTask;
  const kind = raw.kind;
  const status = raw.status;
  if (typeof kind !== 'string' || !studentTaskKinds.includes(kind as StudentTaskKind)) invalidTaskPayload(`items[${index}].kind`);
  if (typeof status !== 'string' || !studentTaskStatuses.includes(status as StudentTaskStatus)) invalidTaskPayload(`items[${index}].status`);
  const dueAt = raw.dueAt ?? raw.due_at;
  if (dueAt !== null && typeof dueAt !== 'string') invalidTaskPayload(`items[${index}].due_at`);
  return {
    id: requiredTaskString(raw.id, `items[${index}].id`),
    sourceId: requiredTaskString(raw.sourceId ?? raw.source_id, `items[${index}].source_id`),
    kind: kind as StudentTaskKind,
    title: requiredTaskString(raw.title, `items[${index}].title`),
    summary: requiredTaskString(raw.summary, `items[${index}].summary`, true),
    status: status as StudentTaskStatus,
    dueAt,
    updatedAt: requiredTaskString(raw.updatedAt ?? raw.updated_at, `items[${index}].updated_at`),
    progress: (() => {
      const progress = taskNumber(raw.progress, `items[${index}].progress`);
      if (progress < 0 || progress > 100) invalidTaskPayload(`items[${index}].progress`);
      return progress;
    })(),
  };
}

export async function loadTasks(filters: StudentTaskFilters = {}): Promise<StudentTaskList> {
  if (filters.kind && !studentTaskKinds.includes(filters.kind)) throw new ApiError('任务类型筛选无效', 'invalid_task_filter');
  if (filters.status && !studentTaskStatuses.includes(filters.status)) throw new ApiError('任务状态筛选无效', 'invalid_task_filter');
  const page = Math.max(1, Math.trunc(filters.page || 1));
  const pageSize = Math.max(1, Math.min(100, Math.trunc(filters.pageSize || 20)));
  const params = new URLSearchParams({
    kind: filters.kind || '',
    status: filters.status || '',
    page: String(page),
    page_size: String(pageSize),
  });
  const payload = await request<RawStudentTaskList>(`/api/student/tasks?${params.toString()}`);
  if (!Array.isArray(payload.items)) invalidTaskPayload('items');
  if (!isRecord(payload.counts)) invalidTaskPayload('counts');
  const rawCounts = payload.counts as RawStudentTaskCounts;
  const counts: StudentTaskCounts = {
    byStatus: normalizeTaskCountRecord(rawCounts.byStatus ?? rawCounts.by_status, studentTaskStatuses, 'counts.by_status'),
    byKind: normalizeTaskCountRecord(rawCounts.byKind ?? rawCounts.by_kind, studentTaskKinds, 'counts.by_kind'),
  };
  return {
    items: payload.items.map(normalizeStudentTask),
    page: taskInteger(payload.page, 'page', 1),
    pageSize: taskInteger(payload.pageSize ?? payload.page_size, 'page_size', 1),
    total: taskInteger(payload.total, 'total'),
    counts,
  };
}

function normalizeExamAttempt(item: RawExamAttempt): ExamAttempt {
  return {
    attempt: Number(item.attempt || 1),
    startedAt: item.startedAt || item.started_at || '',
    deadlineAt: item.deadlineAt || item.deadline_at || '',
    status: item.status || 'in_progress',
    submittedAt: item.submittedAt ?? item.submitted_at ?? null,
  };
}

function normalizeExamSubmission(item: RawExamSubmission, examId: string): ExamSubmission {
  return {
    id: item.id,
    examId: item.examId || item.exam_id || examId,
    attempt: Number(item.attempt || 1),
    submittedAt: item.submittedAt || item.submitted_at || '',
    status: item.status || 'submitted',
    score: Number(item.score || 0),
    maxScore: Number(item.maxScore ?? item.max_score ?? 0),
    needsReview: Boolean(item.needsReview ?? item.needs_review),
  };
}

function normalizeExam(item: RawExam): Exam {
  const availability = item.availability || 'not_open';
  const status = item.status === '进行中' || item.status === '已完成' || item.status === '已结束' ? item.status : availability === 'open' ? '进行中' : availability === 'closed' ? '已结束' : '未开始';
  return {
    id: item.id,
    title: item.title,
    type: '考试',
    status,
    availability,
    openAt: item.openAt || item.open_at || '',
    closeAt: item.closeAt || item.close_at || '',
    durationSeconds: Number(item.durationSeconds ?? item.duration_seconds ?? 0),
    allowAttempts: Number(item.allowAttempts ?? item.allow_attempts ?? 1),
    questionCount: Number(item.questionCount ?? item.question_count ?? item.question_ids?.length ?? item.questions?.length ?? 0),
  };
}

export async function loadExams(): Promise<Exam[]> {
  const payload = await request<{ items?: RawExam[] }>('/api/student/exams');
  return (payload.items || []).map(normalizeExam);
}

export async function loadExam(examId: string): Promise<ExamDetail> {
  const payload = await request<RawExam>(`/api/student/exams/${encodeURIComponent(examId)}`);
  const base = normalizeExam(payload);
  return {
    ...base,
    questions: (payload.questions || []).map((item): AssignmentQuestion => ({ id: item.id, prompt: item.prompt, questionType: item.questionType || item.question_type || 'short_answer', options: item.options || [], maxScore: Number(item.maxScore || item.max_score || 0) })),
    myAttempts: (payload.myAttempts || payload.my_attempts || []).map(normalizeExamAttempt),
    mySubmissions: (payload.mySubmissions || payload.my_submissions || []).map((item) => normalizeExamSubmission(item, examId)),
  };
}

export async function startExam(examId: string, csrfToken: string, idempotencyKey: string): Promise<ExamDetail> {
  const payload = await request<RawExam>(`/api/student/exams/${encodeURIComponent(examId)}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `exam-start-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  const detail = await normalizeExamDetail(payload, examId);
  detail.attempt = payload.attempt ? normalizeExamAttempt(payload.attempt) : undefined;
  detail.serverNow = payload.serverNow || payload.server_now;
  return detail;
}

async function normalizeExamDetail(payload: RawExam, examId: string): Promise<ExamDetail> {
  return {
    ...normalizeExam(payload),
    questions: (payload.questions || []).map((item): AssignmentQuestion => ({ id: item.id, prompt: item.prompt, questionType: item.questionType || item.question_type || 'short_answer', options: item.options || [], maxScore: Number(item.maxScore || item.max_score || 0) })),
    myAttempts: (payload.myAttempts || payload.my_attempts || []).map(normalizeExamAttempt),
    mySubmissions: (payload.mySubmissions || payload.my_submissions || []).map((item) => normalizeExamSubmission(item, examId)),
  };
}

export async function loadExamDraft(examId: string, attempt: number): Promise<ExamDraft> {
  const payload = await request<{ exam_id?: string; examId?: string; attempt?: number; answers?: Record<string, unknown>; version?: number; updated_at?: string | null; updatedAt?: string | null; has_saved_draft?: boolean; hasSavedDraft?: boolean }>(`/api/student/exams/${encodeURIComponent(examId)}/draft?attempt=${attempt}`);
  return { examId: payload.examId || payload.exam_id || examId, attempt: Number(payload.attempt || attempt), answers: payload.answers || {}, version: Number(payload.version || 0), updatedAt: payload.updatedAt ?? payload.updated_at ?? null, hasSavedDraft: Boolean(payload.hasSavedDraft ?? payload.has_saved_draft) };
}

export async function saveExamDraft(examId: string, attempt: number, answers: Record<string, unknown>, baseVersion: number, csrfToken: string, idempotencyKey: string): Promise<ExamDraft> {
  const payload = await request<{ exam_id?: string; examId?: string; attempt?: number; answers?: Record<string, unknown>; version?: number; updated_at?: string | null; updatedAt?: string | null; has_saved_draft?: boolean; hasSavedDraft?: boolean }>(`/api/student/exams/${encodeURIComponent(examId)}/draft`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `exam-draft-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ attempt, answers, base_version: baseVersion }),
  });
  return { examId: payload.examId || payload.exam_id || examId, attempt: Number(payload.attempt || attempt), answers: payload.answers || {}, version: Number(payload.version || 0), updatedAt: payload.updatedAt ?? payload.updated_at ?? null, hasSavedDraft: Boolean(payload.hasSavedDraft ?? payload.has_saved_draft) };
}

export async function submitExam(examId: string, attempt: number, answers: Record<string, unknown>, csrfToken: string, idempotencyKey: string): Promise<ExamSubmission> {
  const payload = await request<RawExamSubmission>(`/api/student/exams/${encodeURIComponent(examId)}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `exam-submit-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ attempt, answers }),
  });
  return normalizeExamSubmission(payload, examId);
}

function normalizeTeacherQuestion(item: RawTeacherQuestion): TeacherQuestion {
  return {
    id: item.id,
    questionType: item.questionType || item.question_type || 'short_answer',
    prompt: item.prompt,
    options: item.options || [],
    answer: item.answer ?? null,
    rubric: item.rubric || '',
    maxScore: Number(item.maxScore || item.max_score || 0),
    chapterId: item.chapter_id ?? null,
    chapterName: item.chapter_name ?? null,
    nodeId: item.node_id ?? null,
    nodeName: item.node_name ?? null,
    status: item.status || 'draft',
    version: Number(item.version || 1),
    createdBy: item.created_by || '',
    updatedAt: item.updated_at || '',
  };
}

function normalizeTeacherAssignment(item: RawTeacherAssignment): TeacherAssignment {
  return {
    id: item.id,
    title: item.title,
    type: item.type || '课程作业',
    dueAt: item.dueAt || item.due_at || '未设置',
    progress: Number(item.progress || 0),
    score: item.score ?? null,
    questionCount: Number(item.questionCount || item.question_count || item.question_ids?.length || 0),
    allowAttempts: Number(item.allowAttempts || item.allow_attempts || 1),
    status: item.status || 'draft',
    questionIds: item.question_ids || [],
    submittedCount: Number(item.submitted_count || 0),
    gradedCount: Number(item.graded_count || 0),
  };
}

function normalizeTeacherExam(item: RawTeacherExam): TeacherExam {
  return {
    id: item.id,
    title: item.title,
    status: item.status || 'draft',
    availability: item.availability || 'not_open',
    openAt: item.openAt || item.open_at || '',
    closeAt: item.closeAt || item.close_at || '',
    durationSeconds: Number(item.durationSeconds || item.duration_seconds || 0),
    allowAttempts: Number(item.allowAttempts || item.allow_attempts || 1),
    questionCount: Number(item.questionCount || item.question_count || item.question_ids?.length || 0),
    questionIds: item.question_ids || [],
    createdBy: item.created_by || '',
    updatedAt: item.updated_at || '',
  };
}

export async function loadTeacherQuestions(status = ''): Promise<TeacherQuestion[]> {
  const suffix = status ? `?status=${encodeURIComponent(status)}` : '';
  const payload = await request<{ items?: RawTeacherQuestion[] }>(`/api/teacher/questions${suffix}`);
  return (payload.items || []).map(normalizeTeacherQuestion);
}

export async function loadTeacherAssignments(): Promise<TeacherAssignment[]> {
  const payload = await request<{ items?: RawTeacherAssignment[] }>('/api/teacher/assignments');
  return (payload.items || []).map(normalizeTeacherAssignment);
}

export async function loadTeacherExams(): Promise<TeacherExam[]> {
  const payload = await request<{ items?: RawTeacherExam[] }>('/api/teacher/exams');
  return (payload.items || []).map(normalizeTeacherExam);
}

export async function loadTeacherResources(status = ''): Promise<TeacherResource[]> {
  const suffix = status ? `?status=${encodeURIComponent(status)}` : '';
  const payload = await request<{ items?: RawTeacherResource[] }>(`/api/teacher/resources${suffix}`);
  return (payload.items || []).map(normalizeTeacherResource);
}

export async function createTeacherResource(payload: { title: string; chapter_id: number; node_id?: string | null; source_reference?: string }, csrfToken: string, idempotencyKey: string): Promise<TeacherResource> {
  const response = await request<RawTeacherResource>('/api/teacher/resources', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-resource-create-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify(payload),
  });
  return normalizeTeacherResource(response);
}

export async function uploadTeacherResource(resourceId: string, file: Blob, filename: string, csrfToken: string, idempotencyKey: string): Promise<TeacherResource> {
  const response = await request<RawTeacherResource>(`/api/teacher/resources/${encodeURIComponent(resourceId)}/file?filename=${encodeURIComponent(filename)}`, {
    method: 'PUT',
    headers: { 'Content-Type': file.type || 'application/octet-stream', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-resource-file-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: file,
  });
  return normalizeTeacherResource(response);
}

export async function transitionTeacherResource(resourceId: string, action: 'publish' | 'archive', csrfToken: string, idempotencyKey: string): Promise<TeacherResource> {
  const response = await request<RawTeacherResource>(`/api/teacher/resources/${encodeURIComponent(resourceId)}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-resource-${action}-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherResource(response);
}

export async function createTeacherQuestion(payload: { question_type: QuestionType; prompt: string; options?: string[]; answer?: string | string[] | boolean | null; rubric?: string; max_score: number; chapter_id?: number | null; node_id?: string | null }, csrfToken: string, idempotencyKey: string): Promise<TeacherQuestion> {
  const response = await request<RawTeacherQuestion>('/api/teacher/questions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-question-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify(payload),
  });
  return normalizeTeacherQuestion(response);
}

export async function updateTeacherQuestion(questionId: string, payload: { question_type: QuestionType; prompt: string; options?: string[]; answer?: string | string[] | boolean | null; rubric?: string; max_score: number; chapter_id?: number | null; node_id?: string | null; base_version: number }, csrfToken: string, idempotencyKey: string): Promise<TeacherQuestion> {
  const response = await request<RawTeacherQuestion>(`/api/teacher/questions/${encodeURIComponent(questionId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-question-update-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify(payload),
  });
  return normalizeTeacherQuestion(response);
}

export async function publishTeacherQuestion(questionId: string, csrfToken: string, idempotencyKey: string): Promise<TeacherQuestion> {
  const response = await request<RawTeacherQuestion>(`/api/teacher/questions/${encodeURIComponent(questionId)}/publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-question-publish-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherQuestion(response);
}

export async function transitionTeacherQuestion(questionId: string, action: 'withdraw' | 'archive', csrfToken: string, idempotencyKey: string): Promise<TeacherQuestion> {
  const response = await request<RawTeacherQuestion>(`/api/teacher/questions/${encodeURIComponent(questionId)}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-question-${action}-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherQuestion(response);
}

export async function createTeacherAssignment(payload: { title: string; question_ids: string[]; due_at?: string | null; allow_attempts?: number }, csrfToken: string, idempotencyKey: string): Promise<TeacherAssignment> {
  const response = await request<RawTeacherAssignment>('/api/teacher/assignments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-assignment-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify(payload),
  });
  return normalizeTeacherAssignment(response);
}

export async function publishTeacherAssignment(assignmentId: string, csrfToken: string, idempotencyKey: string): Promise<TeacherAssignment> {
  const response = await request<RawTeacherAssignment>(`/api/teacher/assignments/${encodeURIComponent(assignmentId)}/publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-assignment-publish-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherAssignment(response);
}

export async function transitionTeacherAssignment(assignmentId: string, action: 'withdraw' | 'archive', csrfToken: string, idempotencyKey: string): Promise<TeacherAssignment> {
  const response = await request<RawTeacherAssignment>(`/api/teacher/assignments/${encodeURIComponent(assignmentId)}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-assignment-${action}-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherAssignment(response);
}

export async function createTeacherExam(payload: { title: string; question_ids: string[]; open_at: string; close_at: string; duration_seconds: number; allow_attempts: number }, csrfToken: string, idempotencyKey: string): Promise<TeacherExam> {
  const response = await request<RawTeacherExam>('/api/teacher/exams', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-exam-create-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify(payload),
  });
  return normalizeTeacherExam(response);
}

export async function publishTeacherExam(examId: string, csrfToken: string, idempotencyKey: string): Promise<TeacherExam> {
  const response = await request<RawTeacherExam>(`/api/teacher/exams/${encodeURIComponent(examId)}/publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-exam-publish-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherExam(response);
}

export async function transitionTeacherExam(examId: string, action: 'withdraw' | 'archive', csrfToken: string, idempotencyKey: string): Promise<TeacherExam> {
  const response = await request<RawTeacherExam>(`/api/teacher/exams/${encodeURIComponent(examId)}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `teacher-exam-${action}-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeTeacherExam(response);
}

function normalizeGradebookStudent(item: NonNullable<RawGradebook['students']>[number]): Gradebook['students'][number] {
  return {
    userUid: item.userUid || item.user_uid || '',
    submissionCount: Number(item.submissionCount || item.submission_count || 0),
    completedAssignments: Number(item.completedAssignments || item.completed_assignments || 0),
    averageRatio: Number(item.averageRatio ?? item.average_ratio ?? 0),
    needsReview: Boolean(item.needsReview ?? item.needs_review),
    riskLevel: item.riskLevel || item.risk_level || 'normal',
  };
}

export async function loadTeacherGradebook(assignmentId = ''): Promise<Gradebook> {
  const payload = await request<RawGradebook>(`/api/teacher/gradebook${assignmentId ? `?assignment_id=${encodeURIComponent(assignmentId)}` : ''}`);
  const assignments = (payload.assignments || []).map((item) => ({
    id: item.id,
    title: item.title,
    status: item.status,
    submittedCount: Number(item.submittedCount || item.submitted_count || 0),
    gradedCount: Number(item.gradedCount || item.graded_count || 0),
    completionRate: Number(item.completionRate ?? item.completion_rate ?? 0),
    averageScore: Number(item.averageScore ?? item.average_score ?? 0),
    averageRatio: Number(item.averageRatio ?? item.average_ratio ?? 0),
    questionCount: Number(item.questionCount || item.question_count || 0),
  }));
  const knowledgePoints = (payload.knowledge_points || []).map((item) => ({ id: item.id, name: item.name, score: Number(item.score || 0), maxScore: Number(item.maxScore || item.max_score || 0), attempts: Number(item.attempts || 0), ratio: Number(item.ratio || 0), status: item.status || 'weak' }));
  const students = (payload.students || []).map(normalizeGradebookStudent);
  return { assignmentId: payload.assignmentId || payload.assignment_id, assignments, students, knowledgePoints, riskStudents: (payload.risk_students || []).map(normalizeGradebookStudent) };
}

function normalizeGrade(item: RawGrade): AssignmentGrade {
  return {
    id: item.id,
    questionId: item.questionId || item.question_id || '',
    score: Number(item.score || 0),
    maxScore: Number(item.maxScore || item.max_score || 0),
    feedback: item.feedback || '',
    source: item.source || 'unknown',
    reviewedBy: item.reviewed_by,
    reviewReason: item.review_reason,
  };
}

function normalizeSubmission(item: RawSubmission, assignmentId: string): AssignmentSubmission {
  return {
    id: item.id || item.submission_id || '',
    assignmentId: item.assignmentId || item.assignment_id || assignmentId,
    attempt: Number(item.attempt || 1),
    status: item.status || 'submitted',
    createdAt: item.createdAt || item.created_at || '',
    answers: item.answers,
    grades: (item.grades || []).map(normalizeGrade),
    score: item.score ?? null,
    maxScore: item.maxScore ?? item.max_score ?? null,
    needsReview: Boolean(item.needsReview ?? item.needs_review),
  };
}

function normalizeDraft(item: RawDraft, assignmentId: string, attempt = 1): AssignmentDraft {
  return {
    assignmentId: item.assignmentId || item.assignment_id || assignmentId,
    attempt: Number(item.attempt || attempt),
    answers: item.answers || {},
    version: Number(item.version || 0),
    updatedAt: item.updatedAt ?? item.updated_at ?? null,
    hasSavedDraft: Boolean(item.hasSavedDraft ?? item.has_saved_draft),
  };
}

export async function loadAssignment(assignmentId: string): Promise<AssignmentDetail> {
  const payload = await request<RawAssignment & { questions?: RawQuestion[]; my_submissions?: RawSubmission[]; mySubmissions?: RawSubmission[]; my_draft?: RawDraft; myDraft?: RawDraft }>(`/api/student/assignments/${encodeURIComponent(assignmentId)}`);
  const base = normalizeAssignment(payload);
  return {
    ...base,
    allowAttempts: Number(payload.allowAttempts || payload.allow_attempts || 1),
    questions: (payload.questions || []).map((item) => ({
      id: item.id,
      prompt: item.prompt,
      questionType: item.questionType || item.question_type || 'short_answer',
      options: item.options || [],
      maxScore: Number(item.maxScore || item.max_score || 0),
    })),
    mySubmissions: (payload.mySubmissions || payload.my_submissions || []).map((item) => normalizeSubmission(item, assignmentId)),
    myDraft: payload.myDraft || payload.my_draft ? normalizeDraft(payload.myDraft || payload.my_draft || {}, assignmentId) : undefined,
  };
}

function normalizeAssignment(item: RawAssignment): Assignment {
  return {
    id: item.id,
    title: item.title,
    type: item.type || '课程作业',
    status: item.status === '进行中' || item.status === '已完成' || item.status === '已过期' ? item.status : '待完成',
    dueAt: item.dueAt || item.due_at || '未设置',
    questionCount: item.questionCount || item.question_count || item.question_ids?.length || 0,
    score: item.score ?? null,
    progress: Number(item.progress || 0),
    allowAttempts: Number(item.allowAttempts || item.allow_attempts || 1),
  };
}

export async function loadAssignmentDraft(assignmentId: string, attempt = 1): Promise<AssignmentDraft> {
  const payload = await request<RawDraft>(`/api/student/assignments/${encodeURIComponent(assignmentId)}/draft?attempt=${attempt}`);
  return normalizeDraft(payload, assignmentId, attempt);
}

export async function saveAssignmentDraft(
  assignmentId: string,
  attempt: number,
  answers: Record<string, unknown>,
  baseVersion: number,
  csrfToken: string,
  idempotencyKey: string,
): Promise<AssignmentDraft> {
  const payload = await request<RawDraft>(`/api/student/assignments/${encodeURIComponent(assignmentId)}/draft`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `assignment-draft-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({ attempt, answers, base_version: baseVersion }),
  });
  return normalizeDraft(payload, assignmentId, attempt);
}

export async function submitAssignment(assignmentId: string, attempt: number, answers: Record<string, unknown>, csrfToken: string, idempotencyKey: string): Promise<{ id: string; assignmentId: string; attempt: number; status: string }> {
  const payload = await request<{ id: string; assignment_id?: string; assignmentId?: string; attempt: number; status: string }>(`/api/student/assignments/${encodeURIComponent(assignmentId)}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `assignment-submit-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({ attempt, answers }),
  });
  return { id: payload.id, assignmentId: payload.assignmentId || payload.assignment_id || assignmentId, attempt: Number(payload.attempt), status: payload.status };
}

export async function loadTeacherSubmissions(assignmentId: string): Promise<AssignmentSubmission[]> {
  const payload = await request<{ items?: RawSubmission[] }>(`/api/teacher/assignments/${encodeURIComponent(assignmentId)}/submissions`);
  return (payload.items || []).map((item) => normalizeSubmission(item, assignmentId));
}

export async function gradeSubmission(assignmentId: string, submissionId: string, csrfToken: string, idempotencyKey: string): Promise<AssignmentSubmission> {
  const payload = await request<RawSubmission>(`/api/teacher/submissions/${encodeURIComponent(submissionId)}/grade`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `submission-grade-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({}),
  });
  return normalizeSubmission(payload, assignmentId);
}

export async function gradeAssignment(assignmentId: string, csrfToken: string, idempotencyKey: string): Promise<{ taskId: string; status: string }> {
  const payload = await request<{ id?: string; task_id?: string; taskId?: string; status?: string }>(`/api/teacher/assignments/${encodeURIComponent(assignmentId)}/grade`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `assignment-grade-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({}),
  });
  return { taskId: payload.taskId || payload.task_id || payload.id || '', status: payload.status || 'processing' };
}

export async function subjectiveAgentReview(assignmentId: string, submissionId: string, questionId: string, csrfToken: string, idempotencyKey: string): Promise<AssignmentGrade> {
  const payload = await request<{ grade: RawGrade }>(`/api/teacher/submissions/${encodeURIComponent(submissionId)}/subjective/${encodeURIComponent(questionId)}/agent-review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `subjective-review-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({ assignment_id: assignmentId }),
  });
  return normalizeGrade(payload.grade);
}

export async function reviewGrade(gradeId: string, score: number, reason: string, csrfToken: string, idempotencyKey: string): Promise<AssignmentGrade> {
  const payload = await request<RawGrade>(`/api/teacher/grade-items/${encodeURIComponent(gradeId)}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `grade-review-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({ score, reason }),
  });
  return normalizeGrade(payload);
}

export async function loadResources(chapterId?: number): Promise<Resource[]> {
  const search = chapterId ? `?chapter_id=${encodeURIComponent(chapterId)}` : '';
  const payload = await request<{ items?: RawResource[] }>(`/api/textbook/resources${search}`);
  return (payload.items || []).map(normalizeResource);
}

export async function loadFavoriteResources(): Promise<FavoriteResource[]> {
  const payload = await request<{ items?: RawResource[] }>('/api/student/resources/favorites');
  return (payload.items || []).map((item) => ({
    ...normalizeResource(item),
    favoriteAt: item.favoriteAt ?? item.favorite_at ?? null,
    noteCount: Number(item.noteCount ?? item.note_count ?? 0),
  }));
}

function normalizeResource(item: RawResource): Resource {
  return {
    id: item.id,
    title: item.title || (item.source_file || item.sourceFile || '').replace(/\.pdf$/i, ''),
    sourceFile: item.sourceFile || item.source_file || '',
    chapterId: Number(item.chapterId || item.chapter_id),
    pageStart: Number(item.pageStart || item.page_start || 1),
    pageCount: Number(item.pageCount || item.page_end || 0),
    type: item.type || 'PDF',
    version: item.version || '课程资料',
    available: item.available !== false,
    mountStatus: item.mount_status || (item.available === false ? 'pending_mount' : 'ready'),
    locator: item.locator,
  };
}

function normalizeTeacherResourceRevision(item: RawTeacherResourceRevision): TeacherResourceRevision {
  return {
    id: item.id,
    resourceId: item.resourceId || item.resource_id || '',
    revision: Number(item.revision || 0),
    filename: item.filename,
    sha256: item.sha256,
    sizeBytes: Number(item.sizeBytes ?? item.size_bytes ?? 0),
    uploadedBy: item.uploadedBy || item.uploaded_by || '',
    status: item.status || 'active',
    createdAt: item.createdAt || item.created_at || '',
  };
}

function normalizeTeacherResource(item: RawTeacherResource): TeacherResource {
  return {
    ...normalizeResource(item),
    title: item.title || (item.source_file || item.sourceFile || '').replace(/\.(pdf|md)$/i, ''),
    sourceReference: item.sourceReference || item.source_reference || '',
    status: item.status || 'draft',
    revision: Number(item.revision || 0),
    revisions: (item.revisions || []).map(normalizeTeacherResourceRevision),
  };
}

export async function loadResource(resourceId: string): Promise<{ resource: Resource; page: number; locator: string | null }> {
  const payload = await request<{ resource: RawResource; page: number; locator?: string | null }>(`/api/textbook/resources/${encodeURIComponent(resourceId)}`);
  return {
    resource: normalizeResource({ ...payload.resource, locator: payload.locator }),
    page: Number(payload.page || 1),
    locator: payload.locator || null,
  };
}

type RawProgress = { resource_id?: string; resourceId?: string; page?: number; percent?: number; completed?: boolean; version?: number; updated_at?: string | null; updatedAt?: string | null; has_saved_progress?: boolean; hasSavedProgress?: boolean };
type RawResourceNote = { id?: string; resource_id?: string; resourceId?: string; page: number; text?: string; note?: string; version?: number; updated_at?: string | null; updatedAt?: string | null };
type RawResourceAnnotations = { resource_id?: string; resourceId?: string; favorite?: boolean; notes?: RawResourceNote[] };

function normalizeProgress(item: RawProgress): ResourceProgress {
  return {
    resourceId: item.resourceId || item.resource_id || '',
    page: Number(item.page || 1),
    percent: Number(item.percent || 0),
    completed: Boolean(item.completed),
    version: Number(item.version || 0),
    updatedAt: item.updatedAt ?? item.updated_at ?? null,
    hasSavedProgress: Boolean(item.hasSavedProgress ?? item.has_saved_progress),
  };
}

const learningPositionResourceId = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$/;

function hasAsciiControlCharacter(value: string): boolean {
  for (const character of value) {
    const code = character.charCodeAt(0);
    if (code < 32 || code === 127) return true;
  }
  return false;
}

function invalidLearningPosition(field: string): never {
  throw new ApiError(`最近学习位置响应格式错误：${field}`, 'invalid_learning_position_payload');
}

function learningPositionField(item: Record<string, unknown>, camelCase: string, snakeCase: string): unknown {
  return item[camelCase] ?? item[snakeCase];
}

function normalizeLearningPosition(value: unknown): LearningPosition {
  if (!isRecord(value)) invalidLearningPosition('position');
  if (!isRecord(value.resource)) invalidLearningPosition('position.resource');
  if (!isRecord(value.progress)) invalidLearningPosition('position.progress');

  const courseId = value.course_id;
  const rawResource = value.resource;
  const rawProgress = value.progress;
  const resourceId = rawResource.id;
  const sourceFile = learningPositionField(rawResource, 'sourceFile', 'source_file');
  const chapterId = learningPositionField(rawResource, 'chapterId', 'chapter_id');
  const pageStartValue = learningPositionField(rawResource, 'pageStart', 'page_start');
  const pageCount = learningPositionField(rawResource, 'pageCount', 'page_end');
  const titleValue = rawResource.title;
  const typeValue = rawResource.type;
  const versionValue = rawResource.version;
  const availableValue = rawResource.available;
  const mountStatusValue = rawResource.mount_status;
  const locatorValue = rawResource.locator;
  const resourceStatus = rawResource.status;
  const progressResourceId = learningPositionField(rawProgress, 'resourceId', 'resource_id');
  const progressPage = rawProgress.page;
  const progressPercent = rawProgress.percent;
  const progressCompleted = rawProgress.completed;
  const progressVersion = rawProgress.version;
  const updatedAtValue = learningPositionField(rawProgress, 'updatedAt', 'updated_at');
  const hasSavedProgressValue = learningPositionField(rawProgress, 'hasSavedProgress', 'has_saved_progress');

  if (!Number.isSafeInteger(courseId) || Number(courseId) <= 0) invalidLearningPosition('position.course_id');
  if (typeof resourceId !== 'string' || !learningPositionResourceId.test(resourceId)) invalidLearningPosition('position.resource.id');
  if (typeof sourceFile !== 'string' || !sourceFile.trim() || sourceFile.length > 500) invalidLearningPosition('position.resource.source_file');
  if (titleValue !== undefined && titleValue !== null && (typeof titleValue !== 'string' || !titleValue.trim() || titleValue.length > 200)) invalidLearningPosition('position.resource.title');
  if (!Number.isSafeInteger(chapterId) || Number(chapterId) <= 0) invalidLearningPosition('position.resource.chapter_id');
  const pageStart = pageStartValue === undefined ? 1 : pageStartValue;
  if (!Number.isSafeInteger(pageStart) || Number(pageStart) < 1) invalidLearningPosition('position.resource.page_start');
  if (!Number.isSafeInteger(pageCount) || Number(pageCount) < Number(pageStart) || Number(pageCount) > 1_000_000) invalidLearningPosition('position.resource.page_end');
  if (typeValue !== undefined && typeValue !== 'PDF' && typeValue !== '资料' && typeValue !== '测验') invalidLearningPosition('position.resource.type');
  if (versionValue !== undefined && (typeof versionValue !== 'string' || versionValue.length > 120)) invalidLearningPosition('position.resource.version');
  if (resourceStatus !== 'published') invalidLearningPosition('position.resource.status');
  if (typeof availableValue !== 'boolean') invalidLearningPosition('position.resource.available');
  if (mountStatusValue !== 'ready' && mountStatusValue !== 'pending_mount' && mountStatusValue !== 'unavailable') invalidLearningPosition('position.resource.mount_status');
  if ((availableValue && mountStatusValue !== 'ready') || (!availableValue && mountStatusValue === 'ready')) invalidLearningPosition('position.resource.mount_status');
  if (locatorValue !== undefined && locatorValue !== null && (typeof locatorValue !== 'string' || locatorValue.length > 2048 || hasAsciiControlCharacter(locatorValue) || /^javascript:/i.test(locatorValue.trim()))) invalidLearningPosition('position.resource.locator');
  if (progressResourceId !== resourceId) invalidLearningPosition('position.progress.resource_id');
  if (!Number.isSafeInteger(progressPage) || Number(progressPage) < Number(pageStart) || Number(progressPage) > Number(pageCount)) invalidLearningPosition('position.progress.page');
  if (typeof progressPercent !== 'number' || !Number.isFinite(progressPercent) || progressPercent < 0 || progressPercent > 100) invalidLearningPosition('position.progress.percent');
  if (typeof progressCompleted !== 'boolean') invalidLearningPosition('position.progress.completed');
  if (!Number.isSafeInteger(progressVersion) || Number(progressVersion) < 1) invalidLearningPosition('position.progress.version');
  if (typeof updatedAtValue !== 'string' || !updatedAtValue || updatedAtValue.length > 100 || !Number.isFinite(Date.parse(updatedAtValue))) invalidLearningPosition('position.progress.updated_at');
  if (hasSavedProgressValue !== true) invalidLearningPosition('position.progress.has_saved_progress');

  const title = (typeof titleValue === 'string' ? titleValue : sourceFile.replace(/\.pdf$/i, '')).trim();
  return {
    courseId: Number(courseId),
    resource: {
      id: resourceId,
      title,
      sourceFile: sourceFile.trim(),
      chapterId: Number(chapterId),
      pageStart: Number(pageStart),
      pageCount: Number(pageCount),
      type: (typeValue || 'PDF') as Resource['type'],
      version: typeof versionValue === 'string' && versionValue ? versionValue : '课程资料',
      available: availableValue,
      mountStatus: mountStatusValue,
      locator: typeof locatorValue === 'string' ? locatorValue : null,
    },
    progress: {
      resourceId,
      page: Number(progressPage),
      percent: progressPercent,
      completed: progressCompleted,
      version: Number(progressVersion),
      updatedAt: updatedAtValue,
      hasSavedProgress: true,
    },
  };
}

export async function loadLearningPosition(): Promise<LearningPosition | null> {
  const payload = await request<unknown>('/api/student/learning-position');
  if (!isRecord(payload) || !Object.prototype.hasOwnProperty.call(payload, 'position')) invalidLearningPosition('position');
  return payload.position === null ? null : normalizeLearningPosition(payload.position);
}

export async function loadResourceProgress(resourceId: string): Promise<{ resource: Resource; progress: ResourceProgress }> {
  const payload = await request<{ resource: RawResource; progress: RawProgress }>(`/api/student/resources/${encodeURIComponent(resourceId)}/progress`);
  return { resource: normalizeResource(payload.resource), progress: normalizeProgress(payload.progress) };
}

export async function saveResourceProgress(
  resourceId: string,
  progress: Pick<ResourceProgress, 'page' | 'percent' | 'completed'>,
  baseVersion: number,
  csrfToken: string,
  idempotencyKey: string,
): Promise<ResourceProgress> {
  const payload = await request<RawProgress>(`/api/student/resources/${encodeURIComponent(resourceId)}/progress`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      'X-Request-ID': `resource-progress-${Date.now()}`,
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
    },
    body: JSON.stringify({ ...progress, base_version: baseVersion }),
  });
  return normalizeProgress(payload);
}

function normalizeResourceNote(item: RawResourceNote, resourceId: string): ResourceNote {
  return {
    id: item.id || `${resourceId}:${item.page}`,
    resourceId: item.resourceId || item.resource_id || resourceId,
    page: Number(item.page),
    text: item.text || item.note || '',
    version: Number(item.version || 0),
    updatedAt: item.updatedAt ?? item.updated_at ?? null,
  };
}

function normalizeResourceAnnotations(item: RawResourceAnnotations, resourceId: string): ResourceAnnotations {
  return {
    resourceId: item.resourceId || item.resource_id || resourceId,
    favorite: Boolean(item.favorite),
    notes: (item.notes || []).map((note) => normalizeResourceNote(note, resourceId)),
  };
}

export async function loadResourceAnnotations(resourceId: string): Promise<ResourceAnnotations> {
  return normalizeResourceAnnotations(await request<RawResourceAnnotations>(`/api/student/resources/${encodeURIComponent(resourceId)}/annotations`), resourceId);
}

export async function saveResourceFavorite(resourceId: string, favorite: boolean, csrfToken: string, idempotencyKey: string): Promise<{ resourceId: string; favorite: boolean }> {
  const payload = await request<{ resource_id?: string; resourceId?: string; favorite?: boolean }>(`/api/student/resources/${encodeURIComponent(resourceId)}/favorite`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `resource-favorite-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ favorite }),
  });
  return { resourceId: payload.resourceId || payload.resource_id || resourceId, favorite: Boolean(payload.favorite) };
}

export async function saveResourceNote(resourceId: string, page: number, text: string, baseVersion: number, csrfToken: string, idempotencyKey: string): Promise<ResourceNote> {
  const payload = await request<RawResourceNote>(`/api/student/resources/${encodeURIComponent(resourceId)}/notes/${page}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `resource-note-save-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ text, base_version: baseVersion }),
  });
  return normalizeResourceNote(payload, resourceId);
}

export async function deleteResourceNote(resourceId: string, page: number, baseVersion: number, csrfToken: string, idempotencyKey: string): Promise<{ resourceId: string; page: number; deleted: boolean; version: number }> {
  const payload = await request<{ resource_id?: string; resourceId?: string; page: number; deleted?: boolean; version?: number }>(`/api/student/resources/${encodeURIComponent(resourceId)}/notes/${page}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `resource-note-delete-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ base_version: baseVersion }),
  });
  return { resourceId: payload.resourceId || payload.resource_id || resourceId, page: Number(payload.page), deleted: Boolean(payload.deleted), version: Number(payload.version || 0) };
}

export async function loadProfile(): Promise<ProfilePoint[]> {
  const payload = await request<{ items?: RawProfilePoint[]; nodes?: RawProfilePoint[] }>('/api/student/learning-profile');
  return (payload.items || payload.nodes || []).map((item) => ({
    id: item.id,
    name: item.name,
    status: item.status,
    ratio: item.ratio ?? null,
  }));
}

export async function loadRecommendations(): Promise<Recommendation[]> {
  const payload = await request<{ items?: RawRecommendation[] }>('/api/student/recommendations');
  return (payload.items || []).map((item) => ({
    id: item.id || item.node_id || item.resourceId || item.resource_id || 'recommendation',
    title: item.title,
    type: item.type || '学习建议',
    reason: item.reason || '根据当前学习状态推荐',
    resourceId: item.resourceId || item.resource_id || '',
  }));
}

function normalizeReply(item: RawDiscussionReply, topicId: string): DiscussionReply {
  return { id: item.id, topicId: item.topicId || item.topic_id || topicId, authorLabel: item.authorLabel || item.author_label || '课程成员', body: item.body, status: item.status || 'visible', createdAt: item.createdAt || item.created_at || '' };
}

function normalizeDiscussion(item: RawDiscussion): DiscussionTopic {
  return {
    id: item.id,
    title: item.title,
    body: item.body,
    status: item.status,
    pinned: Boolean(item.pinned),
    authorLabel: item.authorLabel || item.author_label || '课程成员',
    replyCount: Number(item.replyCount || item.reply_count || item.replies?.length || 0),
    createdAt: item.createdAt || item.created_at || '',
    updatedAt: item.updatedAt || item.updated_at || '',
    replies: item.replies?.map((reply) => normalizeReply(reply, item.id)),
    canModerate: Boolean(item.canModerate ?? item.can_moderate),
  };
}

function normalizeNotification(item: RawNotification): NotificationItem {
  return {
    id: item.id,
    audience: item.audience,
    title: item.title,
    body: item.body,
    createdBy: item.createdBy || item.created_by || '',
    createdAt: item.createdAt || item.created_at || '',
    isRead: Boolean(item.isRead ?? item.is_read),
  };
}

function normalizeActivityResponse(item: RawActivityResponse, activityId: string): ActivityResponse {
  return { id: item.id, activityId: item.activityId || item.activity_id || activityId, attempt: Number(item.attempt || 1), answers: item.answers || [], submittedAt: item.submittedAt || item.submitted_at || '' };
}

function normalizeActivity(item: RawActivity): Activity {
  return {
    id: item.id,
    kind: item.kind,
    title: item.title,
    body: item.body,
    options: (item.options || []).map((option) => ({ id: option.id, label: option.label })),
    status: item.status,
    maxAttempts: Number(item.maxAttempts || item.max_attempts || 1),
    hasResponded: Boolean(item.hasResponded ?? item.has_responded),
    attemptsUsed: Number(item.attemptsUsed ?? item.attempts_used ?? 0),
    canRespond: Boolean(item.canRespond ?? item.can_respond),
    canReopen: Boolean(item.canReopen ?? item.can_reopen),
    nextAttempt: item.nextAttempt ?? item.next_attempt ?? null,
    myResponse: item.myResponse || item.my_response ? normalizeActivityResponse((item.myResponse || item.my_response) as RawActivityResponse, item.id) : null,
  };
}

function normalizeActivityResults(item: RawActivityResults, activityId: string): ActivityResults {
  return {
    activityId: item.activityId || item.activity_id || activityId,
    kind: item.kind,
    totalResponses: Number(item.totalResponses ?? item.total_responses ?? 0),
    hasResponded: Boolean(item.hasResponded ?? item.has_responded),
    resultsAvailable: Boolean(item.resultsAvailable ?? item.results_available),
    options: (item.options || []).map((option) => ({ id: option.id, label: option.label, count: Number(option.count || 0), ratio: Number(option.ratio || 0) })),
    participants: (item.participants || []).map((participant) => ({ userRef: participant.userRef || participant.user_ref || '', submittedAt: participant.submittedAt || participant.submitted_at || '' })),
  };
}

function normalizeClassroomDisplayMember(item?: RawClassroomDisplayMember | null): ClassroomDisplayMember {
  return {
    displayName: item?.displayName || item?.display_name || item?.name || '课程成员',
    isMe: Boolean(item?.isMe ?? item?.is_me),
  };
}

function normalizeClassroomRoster(item: RawClassroomRoster | RawClassroomRosterMember[]): ClassroomRoster {
  const payload = Array.isArray(item) ? { configured: true, items: item } : item;
  const members = payload.items || payload.students || [];
  return {
    configured: Boolean(payload.configured ?? payload.rosterConfigured ?? payload.roster_configured ?? true),
    items: members.map((member) => ({
      userRef: member.userRef || member.user_ref || member.id || '',
      displayName: normalizeClassroomDisplayMember(member).displayName,
    })),
    total: Number(payload.total ?? payload.studentCount ?? payload.student_count ?? members.length),
    message: payload.message ?? null,
  };
}

function normalizeRandomSelectionRecord(item: RawRandomSelectionRecord, fallbackRound: number): RandomSelectionRecord {
  const selected = item.member || item.participant || item.selected || item;
  const display = normalizeClassroomDisplayMember(selected);
  const sequence = Math.max(0, Number(item.sequence ?? item.round ?? fallbackRound));
  return {
    displayName: display.displayName,
    isMe: Boolean(selected.isMe ?? selected.is_me ?? item.isMe ?? item.is_me),
    ...(item.userRef || item.user_ref ? { userRef: item.userRef || item.user_ref } : {}),
    cycle: item.cycle === undefined ? null : Math.max(0, Number(item.cycle)),
    sequence,
    round: Math.max(0, Number(item.round ?? sequence)),
    selectedAt: item.selectedAt || item.selected_at || '',
  };
}

function normalizeRandomSelection(item: RawRandomSelectionState, activityId: string): RandomSelectionState {
  const round = Math.max(0, Number(item.round ?? item.currentRound ?? item.current_round ?? 0));
  const rawSelection = item.selection ?? item.latest ?? item.latestSelection ?? item.latest_selection ?? null;
  const rawLatest = item.latest ?? item.latestSelection ?? item.latest_selection ?? rawSelection;
  const history = (item.history || item.selections || []).map((record, index) => normalizeRandomSelectionRecord(record, index + 1));
  return {
    activityId: item.activityId || item.activity_id || activityId,
    kind: 'random_selection',
    round,
    selection: rawSelection ? normalizeRandomSelectionRecord(rawSelection, round) : null,
    latest: rawLatest ? normalizeRandomSelectionRecord(rawLatest, round) : history[history.length - 1] || null,
    history,
    remainingCount: item.remainingCount ?? item.remaining_count ?? item.remaining ?? null,
    canSelect: Boolean(item.canSelect ?? item.can_select ?? true),
  };
}

function normalizeActivityGroup(item: RawActivityGroup, index: number): ActivityGroup {
  return {
    id: item.id || '',
    name: item.name || item.groupName || item.group_name || item.label || `第 ${index + 1} 组`,
    members: (item.members || item.items || []).map((member) => ({
      ...normalizeClassroomDisplayMember(member),
      ...(member.userRef || member.user_ref ? { userRef: member.userRef || member.user_ref } : {}),
    })),
  };
}

function normalizeActivityGroups(item: RawActivityGroupsState, activityId: string): ActivityGroupsState {
  const rawMyGroup = item.myGroup ?? item.my_group ?? item.group ?? null;
  const rawGroups = item.groups || [];
  const groups = rawGroups.map(normalizeActivityGroup);
  return {
    activityId: item.activityId || item.activity_id || activityId,
    kind: 'group_task',
    revision: item.revision === undefined || item.revision === null ? null : Math.max(0, Number(item.revision)),
    generatedAt: item.generatedAt ?? item.generated_at ?? null,
    groups,
    myGroup: rawMyGroup ? normalizeActivityGroup(rawMyGroup, Math.max(0, rawGroups.indexOf(rawMyGroup))) : groups.find((group) => group.members.some((member) => member.isMe)) || null,
    canGenerate: Boolean(item.canGenerate ?? item.can_generate ?? true),
  };
}

export async function loadDiscussions(query = '', page = 1, pageSize = 8): Promise<{ items: DiscussionTopic[]; total: number }> {
  const params = new URLSearchParams();
  if (query) params.set('query', query);
  params.set('page', String(page));
  params.set('page_size', String(pageSize));
  const payload = await request<{ items?: RawDiscussion[]; total?: number }>(`/api/discussions?${params}`);
  return { items: (payload.items || []).map(normalizeDiscussion), total: Number(payload.total || 0) };
}

export async function loadDiscussion(topicId: string): Promise<DiscussionTopic> {
  const payload = await request<RawDiscussion>(`/api/discussions/${encodeURIComponent(topicId)}`);
  return normalizeDiscussion(payload);
}

export async function createDiscussion(title: string, body: string, csrfToken: string, idempotencyKey: string): Promise<DiscussionTopic> {
  const payload = await request<RawDiscussion>('/api/discussions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `discussion-create-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ title, body }),
  });
  return normalizeDiscussion(payload);
}

export async function createDiscussionReply(topicId: string, body: string, csrfToken: string, idempotencyKey: string): Promise<DiscussionReply> {
  const payload = await request<RawDiscussionReply>(`/api/discussions/${encodeURIComponent(topicId)}/replies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `discussion-reply-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ body }),
  });
  return normalizeReply(payload, topicId);
}

export async function reportDiscussion(topicId: string, replyId: string | null, reason: string, csrfToken: string, idempotencyKey: string): Promise<{ id: string; topicId: string; contentType: 'topic' | 'reply'; status: string }> {
  const payload = await request<{ id: string; topic_id?: string; topicId?: string; content_type?: 'topic' | 'reply'; contentType?: 'topic' | 'reply'; status: string }>(`/api/discussions/${encodeURIComponent(topicId)}/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `discussion-report-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ ...(replyId ? { reply_id: replyId } : {}), reason }),
  });
  return { id: payload.id, topicId: payload.topicId || payload.topic_id || topicId, contentType: payload.contentType || payload.content_type || 'topic', status: payload.status };
}

export async function moderateDiscussion(topicId: string, update: { status?: string; pinned?: boolean; reason: string }, csrfToken: string, idempotencyKey: string): Promise<DiscussionTopic> {
  const payload = await request<RawDiscussion>(`/api/discussions/${encodeURIComponent(topicId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `discussion-moderate-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify(update),
  });
  return normalizeDiscussion(payload);
}

export async function loadNotifications(unreadOnly = false, page = 1, pageSize = 20, focusId = ''): Promise<{ items: NotificationItem[]; unreadCount: number; page: number; pageSize: number; total: number; focusFound: boolean; focusedId: string | null }> {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (unreadOnly) params.set('unread_only', 'true');
  if (focusId) params.set('focus_id', focusId);
  const payload = await request<{ items?: RawNotification[]; unread_count?: number; unreadCount?: number; page?: number; page_size?: number; pageSize?: number; total?: number; focus_found?: boolean; focusFound?: boolean; focused_id?: string | null; focusedId?: string | null }>(`/api/notifications?${params.toString()}`);
  const items = (payload.items || []).map(normalizeNotification);
  const focusCandidate = payload.focusedId ?? payload.focused_id;
  const focusedId = typeof focusCandidate === 'string' && items.some((item) => item.id === focusCandidate) ? focusCandidate : null;
  const focusFound = (payload.focusFound ?? payload.focus_found) === true && focusedId !== null;
  return {
    items,
    unreadCount: Number(payload.unreadCount ?? payload.unread_count ?? 0),
    page: Number(payload.page ?? page),
    pageSize: Number(payload.pageSize ?? payload.page_size ?? pageSize),
    total: Number(payload.total ?? 0),
    focusFound,
    focusedId: focusFound ? focusedId : null,
  };
}

export async function markNotificationRead(notificationId: string, csrfToken: string, idempotencyKey: string): Promise<{ unreadCount: number | null }> {
  const payload = await request<{ unread_count?: number; unreadCount?: number }>(`/api/notifications/${encodeURIComponent(notificationId)}/read`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `notification-read-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  const unreadCount = payload.unreadCount ?? payload.unread_count;
  return { unreadCount: unreadCount === undefined ? null : Number(unreadCount) };
}

export async function markAllNotificationsRead(csrfToken: string, idempotencyKey: string): Promise<{ markedCount: number; unreadCount: number }> {
  const payload = await request<{ marked_count?: number; markedCount?: number; unread_count?: number; unreadCount?: number }>('/api/notifications/read-all', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `notification-read-all-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return {
    markedCount: Number(payload.markedCount ?? payload.marked_count ?? 0),
    unreadCount: Number(payload.unreadCount ?? payload.unread_count ?? 0),
  };
}

export async function publishNotification(title: string, body: string, audience: string, csrfToken: string, idempotencyKey: string): Promise<NotificationItem> {
  const payload = await request<RawNotification>('/api/teacher/notifications', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `notification-create-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ title, body, audience }),
  });
  return normalizeNotification(payload);
}

export async function loadActivities(): Promise<Activity[]> {
  const payload = await request<{ items?: RawActivity[] }>('/api/activities');
  return (payload.items || []).map(normalizeActivity);
}

export async function loadActivity(activityId: string): Promise<Activity> {
  const payload = await request<RawActivity>(`/api/activities/${encodeURIComponent(activityId)}`);
  return normalizeActivity(payload);
}

export async function submitActivityResponse(activityId: string, answers: string[], csrfToken: string, idempotencyKey: string, attempt = 1): Promise<ActivityResponse> {
  const payload = await request<RawActivityResponse>(`/api/activities/${encodeURIComponent(activityId)}/responses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `activity-response-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ answers, attempt }),
  });
  return normalizeActivityResponse(payload, activityId);
}

export async function loadActivityResults(activityId: string): Promise<ActivityResults> {
  const payload = await request<RawActivityResults>(`/api/activities/${encodeURIComponent(activityId)}/results`);
  return normalizeActivityResults(payload, activityId);
}

export async function loadClassroomRoster(): Promise<ClassroomRoster> {
  const payload = await request<RawClassroomRoster | RawClassroomRosterMember[]>('/api/teacher/classroom-roster');
  return normalizeClassroomRoster(payload);
}

export async function loadRandomSelection(activityId: string): Promise<RandomSelectionState> {
  const payload = await request<RawRandomSelectionState>(`/api/activities/${encodeURIComponent(activityId)}/random-selection`);
  return normalizeRandomSelection(payload, activityId);
}

export async function selectRandomStudent(activityId: string, csrfToken: string, idempotencyKey: string): Promise<RandomSelectionState> {
  const payload = await request<RawRandomSelectionState>(`/api/teacher/activities/${encodeURIComponent(activityId)}/random-select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `activity-random-select-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeRandomSelection(payload, activityId);
}

export async function loadActivityGroups(activityId: string): Promise<ActivityGroupsState> {
  const payload = await request<RawActivityGroupsState>(`/api/activities/${encodeURIComponent(activityId)}/groups`);
  return normalizeActivityGroups(payload, activityId);
}

export async function generateActivityGroups(activityId: string, csrfToken: string, idempotencyKey: string): Promise<ActivityGroupsState> {
  const payload = await request<RawActivityGroupsState>(`/api/teacher/activities/${encodeURIComponent(activityId)}/groups/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `activity-groups-generate-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeActivityGroups(payload, activityId);
}

export async function createActivity(payload: { kind: ActivityKind; title: string; body: string; options: { id: string; label: string }[]; status?: 'draft' | 'published'; maxAttempts?: number }, csrfToken: string, idempotencyKey: string): Promise<Activity> {
  const response = await request<RawActivity>('/api/teacher/activities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `activity-create-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ ...payload, max_attempts: payload.maxAttempts || 1 }),
  });
  return normalizeActivity(response);
}

export async function transitionActivity(activityId: string, action: 'publish' | 'close' | 'reopen', csrfToken: string, idempotencyKey: string): Promise<Activity> {
  const response = await request<RawActivity>(`/api/teacher/activities/${encodeURIComponent(activityId)}/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, 'X-Request-ID': `activity-${action}-${Date.now()}`, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({}),
  });
  return normalizeActivity(response);
}

export interface AgentEvent {
  event: 'token' | 'source' | 'done' | 'error';
  data: Record<string, unknown>;
}

export function parseAgentSseBlock(block: string): AgentEvent | null {
  const lines = block.split(/\r?\n/);
  const dataLine = lines.find((line) => line.startsWith('data:'));
  if (!dataLine) return null;
  let data: Record<string, unknown>;
  try {
    const parsed = JSON.parse(dataLine.slice(5).trim()) as unknown;
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('invalid payload');
    data = parsed as Record<string, unknown>;
  } catch {
    throw new ApiError('Agent 流式响应格式错误', 'stream_malformed');
  }
  const eventName = (lines.find((line) => line.startsWith('event:'))?.slice(6).trim() || 'error') as AgentEvent['event'];
  if (!['token', 'source', 'done', 'error'].includes(eventName)) {
    throw new ApiError('Agent 流式事件类型无效', 'stream_event_invalid');
  }
  return { event: eventName, data };
}

export async function streamAgent(
  question: string,
  mode: string,
  onEvent: (event: AgentEvent) => void,
  csrfToken = '',
  signal?: AbortSignal,
  context: AgentContext = {},
): Promise<void> {
  const response = await fetch('/api/course-agent/chat', {
    method: 'POST',
    credentials: 'same-origin',
    signal,
    headers: {
      'Content-Type': 'application/json',
      ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}),
      ...(context.idempotencyKey ? { 'Idempotency-Key': context.idempotencyKey } : {}),
    },
    body: JSON.stringify({
      question,
      mode,
      ...(context.resourceId ? { resource_id: context.resourceId } : {}),
      ...(context.resourcePage ? { resource_page: context.resourcePage } : {}),
      ...(context.nodeIds?.length ? { node_ids: context.nodeIds } : {}),
      ...(context.sessionId ? { session_id: context.sessionId } : {}),
      ...(context.turnNo ? { turn_no: context.turnNo } : {}),
    }),
  });
  if (!response.ok || !response.body) {
    const payload = await response.json().catch(() => null) as { error?: { code?: string; message?: string }; request_id?: string } | null;
    throw new ApiError(
      payload?.error?.message || (response.ok ? 'Agent 流式响应不可用' : `Agent 服务返回 HTTP ${response.status}`),
      payload?.error?.code || (response.ok ? 'stream_unavailable' : 'api_error'),
      payload?.request_id,
    );
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let doneSeen = false;
  const throwIfAborted = () => {
    if (signal?.aborted) throw new DOMException('The operation was aborted', 'AbortError');
  };
  const dispatch = (block: string) => {
    throwIfAborted();
    const event = parseAgentSseBlock(block);
    if (!event || doneSeen) return;
    if (event.event === 'done') doneSeen = true;
    onEvent(event);
    if (event.event === 'error') throw new ApiError(String(event.data.message || 'Agent 请求失败'), String(event.data.code || 'agent_error'));
  };
  try {
    while (true) {
      throwIfAborted();
      const packet = await reader.read();
      throwIfAborted();
      buffer += decoder.decode(packet.value || new Uint8Array(), { stream: !packet.done });
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() || '';
      for (const block of blocks) dispatch(block);
      if (packet.done && buffer.trim()) dispatch(buffer);
      if (packet.done) break;
    }
  } catch (error) {
    if (signal?.aborted) {
      try { await reader.cancel(); } catch { /* the fetch body may already be closed */ }
      throw new DOMException('The operation was aborted', 'AbortError');
    }
    throw error;
  } finally {
    reader.releaseLock();
  }
  if (!doneSeen) throw new ApiError('Agent 流式响应未正常结束', 'stream_incomplete');
}

export async function startScenario(scenarioKey: string, csrfToken: string, idempotencyKey: string): Promise<ScenarioSession> {
  const payload = await request<{ session_id: string; state?: string; title?: string; goal?: string; assumptions?: string; turn_count?: number }>('/api/scenarios/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ scenario_key: scenarioKey }),
  });
  return {
    sessionId: payload.session_id,
    state: payload.state === 'completed' ? 'completed' : 'active',
    title: payload.title || '课程情景演练',
    goal: payload.goal || '',
    assumptions: payload.assumptions || '',
    turnCount: Number(payload.turn_count || 0),
  };
}

export async function endScenario(sessionId: string, csrfToken: string, idempotencyKey: string): Promise<{ sessionId: string; turnCount: number; summary: { status: string; knowledgePoints: string[] } }> {
  const payload = await request<{ session_id: string; turn_count?: number; summary?: { status?: string; knowledge_points?: string[] } }>(`/api/scenarios/${encodeURIComponent(sessionId)}/end`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey, ...(csrfToken ? { 'X-Moodle-Sesskey': csrfToken } : {}) },
    body: JSON.stringify({ state: 'completed' }),
  });
  return { sessionId: payload.session_id, turnCount: Number(payload.turn_count || 0), summary: { status: payload.summary?.status || '', knowledgePoints: payload.summary?.knowledge_points || [] } };
}
