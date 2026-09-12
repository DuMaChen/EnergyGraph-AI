export type Role = 'student' | 'teacher' | 'admin';
export type AgentMode = 'qa' | 'learning_diagnosis' | 'scenario' | 'teacher_assistant' | 'question_draft' | 'grading';

export interface AgentContext {
  resourceId?: string;
  resourcePage?: number;
  nodeIds?: string[];
  sessionId?: string;
  turnNo?: number;
  idempotencyKey?: string;
}

export interface ScenarioSession {
  sessionId: string;
  state: 'active' | 'completed';
  title: string;
  goal: string;
  assumptions: string;
  turnCount: number;
}

export interface Session {
  role: Role;
  courseId: number;
  csrfToken: string;
  features: Record<string, boolean>;
}

export interface CourseSummary {
  id: number;
  name: string;
  teacher: string;
  className: string;
  status: 'active' | 'archived';
  progress: number;
  chapterCount: number;
  resourceCount: number;
  lastAccessedAt: string | null;
}

export type CourseSort = 'last_accessed' | 'name' | 'progress' | 'id';

export interface CourseList {
  items: CourseSummary[];
  page: number;
  pageSize: number;
  total: number;
}

export type GlobalSearchKind = 'course' | 'chapter' | 'resource' | 'assignment' | 'exam' | 'discussion' | 'knowledge';
export type GlobalSearchFilterKind = 'all' | GlobalSearchKind;

export interface GlobalSearchItem {
  id: string;
  kind: GlobalSearchKind;
  title: string;
  summary: string;
  chapterId: number | null;
}

export interface GlobalSearchResult {
  courseId: number;
  query: string;
  kind: GlobalSearchFilterKind;
  items: GlobalSearchItem[];
  counts: Record<GlobalSearchKind, number>;
  page: number;
  pageSize: number;
  total: number;
}

export interface GlobalSearchFilters {
  kind?: GlobalSearchFilterKind;
  page?: number;
  pageSize?: number;
}

export interface Chapter {
  id: number;
  name: string;
  progress: number;
  status: string;
  lessons: number;
  duration: string;
}

export interface Resource {
  id: string;
  title: string;
  sourceFile: string;
  chapterId: number;
  pageStart: number;
  pageCount: number;
  type: 'PDF' | '资料' | '测验';
  version: string;
  available: boolean;
  mountStatus: 'ready' | 'pending_mount' | 'unavailable';
  locator?: string | null;
}

export type TeacherResourceStatus = 'draft' | 'published' | 'archived';

export interface TeacherResourceRevision {
  id: string;
  resourceId: string;
  revision: number;
  filename: string;
  sha256: string;
  sizeBytes: number;
  uploadedBy: string;
  status: 'active' | 'superseded';
  createdAt: string;
}

export interface TeacherResource extends Resource {
  title: string;
  sourceReference: string;
  status: TeacherResourceStatus;
  revision: number;
  revisions: TeacherResourceRevision[];
}

export interface ResourceProgress {
  resourceId: string;
  page: number;
  percent: number;
  completed: boolean;
  version: number;
  updatedAt: string | null;
  hasSavedProgress: boolean;
}

export interface LearningPosition {
  courseId: number;
  resource: Resource;
  progress: ResourceProgress;
}

export interface ResourceNote {
  id: string;
  resourceId: string;
  page: number;
  text: string;
  version: number;
  updatedAt: string | null;
}

export interface ResourceAnnotations {
  resourceId: string;
  favorite: boolean;
  notes: ResourceNote[];
}

export interface FavoriteResource extends Resource {
  favoriteAt: string | null;
  noteCount: number;
}

export interface Assignment {
  id: string;
  title: string;
  type: string;
  status: '待完成' | '进行中' | '已完成' | '已过期';
  dueAt: string;
  questionCount: number;
  score: number | null;
  progress: number;
  allowAttempts?: number;
}

export type StudentTaskKind = 'assignment' | 'exam' | 'discussion' | 'notification';
export type StudentTaskStatus = 'pending' | 'in_progress' | 'completed' | 'expired';

export interface StudentTask {
  id: string;
  sourceId: string;
  kind: StudentTaskKind;
  title: string;
  summary: string;
  status: StudentTaskStatus;
  dueAt: string | null;
  updatedAt: string;
  progress: number;
}

export interface StudentTaskCounts {
  byStatus: Record<StudentTaskStatus, number>;
  byKind: Record<StudentTaskKind, number>;
}

export interface StudentTaskList {
  items: StudentTask[];
  page: number;
  pageSize: number;
  total: number;
  counts: StudentTaskCounts;
}

export interface StudentTaskFilters {
  kind?: StudentTaskKind;
  status?: StudentTaskStatus;
  page?: number;
  pageSize?: number;
}

export interface TeacherQuestion {
  id: string;
  questionType: QuestionType;
  prompt: string;
  options: string[];
  answer: string | string[] | boolean | null;
  rubric: string;
  maxScore: number;
  chapterId?: number | null;
  chapterName?: string | null;
  nodeId?: string | null;
  nodeName?: string | null;
  status: 'draft' | 'published' | 'withdrawn' | 'archived';
  version: number;
  createdBy: string;
  updatedAt: string;
}

export interface TeacherAssignment {
  id: string;
  title: string;
  type: string;
  dueAt: string;
  progress: number;
  score: number | null;
  questionCount: number;
  allowAttempts?: number;
  status: 'draft' | 'published' | 'withdrawn' | 'archived';
  questionIds: string[];
  submittedCount?: number;
  gradedCount?: number;
}

export type TeacherExamStatus = 'draft' | 'published' | 'withdrawn' | 'archived';

export interface TeacherExam {
  id: string;
  title: string;
  status: TeacherExamStatus;
  availability: ExamAvailability;
  openAt: string;
  closeAt: string;
  durationSeconds: number;
  allowAttempts: number;
  questionCount: number;
  questionIds: string[];
  createdBy: string;
  updatedAt: string;
}

export interface GradebookAssignment {
  id: string;
  title: string;
  status: string;
  submittedCount: number;
  gradedCount: number;
  completionRate: number;
  averageScore: number;
  averageRatio: number;
  questionCount: number;
}

export interface GradebookStudent {
  userUid: string;
  submissionCount: number;
  completedAssignments: number;
  averageRatio: number;
  needsReview: boolean;
  riskLevel: 'high' | 'normal';
}

export interface GradebookKnowledgePoint {
  id: string;
  name: string;
  score: number;
  maxScore: number;
  attempts: number;
  ratio: number;
  status: 'weak' | 'learning' | 'mastered';
}

export interface Gradebook {
  assignmentId?: string;
  assignments: GradebookAssignment[];
  students: GradebookStudent[];
  knowledgePoints: GradebookKnowledgePoint[];
  riskStudents: GradebookStudent[];
}

export interface AdminStatus {
  adapter: string;
  workflowConfigured: boolean;
  mockWorkflow: boolean;
  publishedKb: { id: string; versionName: string; status: string; hitStatus: string } | null;
  backup: { managedBy: string; status: string };
}

export type AdminDirectoryRole = 'student' | 'teacher' | 'admin';

export interface AdminUser {
  id: string;
  displayName: string;
  role: AdminDirectoryRole;
  courseId: number;
  status: 'active' | 'suspended' | 'unknown';
  lastAccessedAt: string | null;
}

export interface AdminCourse extends CourseSummary {
  enrollmentCount: number | null;
  activeUsers: number | null;
}

export interface AdminUserDirectory {
  items: AdminUser[];
  page: number;
  pageSize: number;
  total: number;
  source: string;
  configured: boolean;
  message?: string;
}

export interface AdminCourseDirectory {
  items: AdminCourse[];
  page: number;
  pageSize: number;
  total: number;
  source: string;
  configured: boolean;
  message?: string;
}

export type ModerationContentType = 'topic' | 'reply';
export type ModerationDecision = 'approve' | 'reject';

export interface AdminModerationItem {
  id: string;
  contentType: ModerationContentType;
  topicId: string;
  replyId: string | null;
  title: string;
  body: string;
  status: 'pending_review';
  authorRef: string;
  createdAt: string;
  updatedAt: string;
}

export interface AdminModerationQueue {
  items: AdminModerationItem[];
  page: number;
  pageSize: number;
  total: number;
}

export interface AdminModerationDecision {
  id: string;
  contentType: ModerationContentType;
  topicId: string;
  replyId: string | null;
  decision: ModerationDecision;
  status: string;
}

export type KnowledgeBaseVersionStatus = 'draft' | 'processing' | 'tested' | 'published' | 'failed' | 'archived';

export interface KnowledgeBaseVersion {
  id: string;
  versionName: string;
  status: KnowledgeBaseVersionStatus;
  manifestSha256: string;
  workflowId: string;
  sourceCount: number;
  hitStatus: string;
  createdBy: string;
  updatedAt: string;
}

export interface KnowledgeBaseFile {
  id: string;
  versionId: string;
  filename: string;
  sha256: string;
  sizeBytes: number;
  status: string;
  errorMessage: string;
  createdAt: string;
}

export interface KnowledgeBaseHitTest {
  id: string;
  versionId: string;
  caseId: string;
  question: string;
  expectedChapter: string;
  actualSources: Array<Record<string, unknown>>;
  status: string;
  requestId: string;
  actorUid: string;
  createdAt: string;
}

export interface AuditLogEntry {
  id: string;
  actorUid: string;
  action: string;
  objectType: string;
  objectId: string;
  result: string;
  reason: string;
  requestId: string;
  createdAt: string;
}

export interface AdminBackupStatus {
  managedBy: string;
  verification: string;
  restoreRehearsal: string;
  secretsExcluded: boolean;
  status: string;
}

export type QuestionType = 'single_choice' | 'multiple_choice' | 'true_false' | 'short_answer' | 'essay';

export interface AssignmentQuestion {
  id: string;
  prompt: string;
  questionType: QuestionType;
  options: string[];
  maxScore: number;
}

export interface AssignmentGrade {
  id: string;
  questionId: string;
  score: number;
  maxScore: number;
  feedback: string;
  source: string;
  reviewedBy?: string | null;
  reviewReason?: string | null;
}

export interface AssignmentSubmission {
  id: string;
  assignmentId: string;
  attempt: number;
  status: string;
  createdAt: string;
  answers?: Record<string, unknown>;
  grades: AssignmentGrade[];
  score: number | null;
  maxScore: number | null;
  needsReview?: boolean;
}

export interface AssignmentDraft {
  assignmentId: string;
  attempt: number;
  answers: Record<string, unknown>;
  version: number;
  updatedAt: string | null;
  hasSavedDraft: boolean;
}

export interface AssignmentDetail extends Assignment {
  allowAttempts: number;
  questions: AssignmentQuestion[];
  mySubmissions: AssignmentSubmission[];
  myDraft?: AssignmentDraft;
}

export type ExamAvailability = 'not_open' | 'open' | 'closed';

export interface Exam {
  id: string;
  title: string;
  type: '考试';
  status: '未开始' | '进行中' | '已完成' | '已结束';
  availability: ExamAvailability;
  openAt: string;
  closeAt: string;
  durationSeconds: number;
  allowAttempts: number;
  questionCount: number;
}

export interface ExamAttempt {
  attempt: number;
  startedAt: string;
  deadlineAt: string;
  status: 'in_progress' | 'submitted' | 'expired';
  submittedAt?: string | null;
}

export interface ExamSubmission {
  id: string;
  examId: string;
  attempt: number;
  submittedAt: string;
  status: string;
  score: number;
  maxScore: number;
  needsReview: boolean;
}

export interface ExamDraft {
  examId: string;
  attempt: number;
  answers: Record<string, unknown>;
  version: number;
  updatedAt: string | null;
  hasSavedDraft: boolean;
}

export interface ExamDetail extends Exam {
  questions: AssignmentQuestion[];
  myAttempts: ExamAttempt[];
  mySubmissions: ExamSubmission[];
  attempt?: ExamAttempt;
  serverNow?: string;
}

export interface ProfilePoint {
  id: string;
  name: string;
  status: 'mastered' | 'learning' | 'weak' | 'unassessed';
  ratio: number | null;
}

export interface KnowledgeGraphNeighbor {
  id: string;
  name: string;
  chapterId: number;
  relationType: string;
}

export interface KnowledgeGraphNode {
  id: string;
  name: string;
  chapterId: number;
  category: string;
  description: string;
  neighbors: KnowledgeGraphNeighbor[];
}

export interface KnowledgeGraphEdge {
  id: string;
  sourceId: string;
  targetId: string;
  relationType: string;
}

export interface KnowledgeGraphSnapshot {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

export interface KnowledgeGraphPath {
  path: string[];
  depth: number;
}

export interface Recommendation {
  id: string;
  title: string;
  type: string;
  reason: string;
  resourceId: string;
}

export interface DiscussionReply {
  id: string;
  topicId: string;
  authorLabel: string;
  body: string;
  status: string;
  createdAt: string;
}

export interface DiscussionTopic {
  id: string;
  title: string;
  body: string;
  status: 'open' | 'solved' | 'closed' | 'pending_review';
  pinned: boolean;
  authorLabel: string;
  replyCount: number;
  createdAt: string;
  updatedAt: string;
  replies?: DiscussionReply[];
  canModerate?: boolean;
}

export interface NotificationItem {
  id: string;
  audience: string;
  title: string;
  body: string;
  createdBy: string;
  createdAt: string;
  isRead: boolean;
}

export type ActivityKind = 'poll' | 'survey' | 'checkin' | 'quick_response' | 'random_selection' | 'group_task';

export interface ActivityOption {
  id: string;
  label: string;
}

export interface ActivityResponse {
  id: string;
  activityId: string;
  attempt: number;
  answers: string[];
  submittedAt: string;
}

export interface Activity {
  id: string;
  kind: ActivityKind;
  title: string;
  body: string;
  options: ActivityOption[];
  status: 'draft' | 'published' | 'closed';
  maxAttempts: number;
  hasResponded: boolean;
  attemptsUsed: number;
  canRespond: boolean;
  canReopen: boolean;
  nextAttempt: number | null;
  myResponse?: ActivityResponse | null;
}

export interface ActivityResultOption extends ActivityOption {
  count: number;
  ratio: number;
}

export interface ActivityParticipant {
  userRef: string;
  submittedAt: string;
}

export interface ActivityResults {
  activityId: string;
  kind: ActivityKind;
  totalResponses: number;
  hasResponded: boolean;
  resultsAvailable: boolean;
  options: ActivityResultOption[];
  participants: ActivityParticipant[];
}

export interface ClassroomRosterMember {
  userRef: string;
  displayName: string;
}

export interface ClassroomRoster {
  configured: boolean;
  items: ClassroomRosterMember[];
  total: number;
  message: string | null;
}

export interface ClassroomDisplayMember {
  displayName: string;
  isMe: boolean;
}

export interface RandomSelectionRecord extends ClassroomDisplayMember {
  userRef?: string;
  cycle: number | null;
  sequence: number;
  round: number;
  selectedAt: string;
}

export interface RandomSelectionState {
  activityId: string;
  kind: 'random_selection';
  round: number;
  selection: RandomSelectionRecord | null;
  latest: RandomSelectionRecord | null;
  history: RandomSelectionRecord[];
  remainingCount: number | null;
  canSelect: boolean;
}

export type ActivityGroupMember = ClassroomDisplayMember & {
  userRef?: string;
};

export interface ActivityGroup {
  id: string;
  name: string;
  members: ActivityGroupMember[];
}

export interface ActivityGroupsState {
  activityId: string;
  kind: 'group_task';
  revision: number | null;
  generatedAt: string | null;
  groups: ActivityGroup[];
  myGroup: ActivityGroup | null;
  canGenerate: boolean;
}

export interface PlatformData {
  courses: CourseSummary[];
  chapters: Chapter[];
  resources: Resource[];
  assignments: Assignment[];
  profile: ProfilePoint[];
  recommendations: Recommendation[];
  notifications: NotificationItem[];
  unreadNotificationCount: number;
  studyHours: number | null;
}

export interface SessionPayload {
  role?: Role;
  course_id?: number;
  csrf_token?: string;
  features?: Record<string, boolean>;
  chapters?: Chapter[];
}

export interface ApiEnvelope<T> {
  status: 'ok' | 'error';
  data: T | null;
  error?: { code?: string; message?: string } | null;
  request_id?: string;
}
