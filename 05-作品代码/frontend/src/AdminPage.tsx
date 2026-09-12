import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router';
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  Database,
  FileText,
  HardDrive,
  History,
  ShieldAlert,
  RefreshCw,
  RotateCcw,
  Server,
  ShieldCheck,
  Upload,
  UserRoundCog,
  Users,
  XCircle,
} from 'lucide-react';
import {
  ApiError,
  createKnowledgeBaseVersion,
  decideAdminModeration,
  loadAdminAuditLog,
  loadAdminBackupStatus,
  loadAdminCourses,
  loadAdminModeration,
  loadAdminStatus,
  loadAdminUsers,
  loadKnowledgeBaseFiles,
  loadKnowledgeBaseHitTests,
  loadKnowledgeBaseVersions,
  rollbackKnowledgeBase,
  runKnowledgeBaseHitTest,
  updateKnowledgeBaseStatus,
  uploadKnowledgeBaseFile,
} from './api/client';
import { useAppStore } from './state/app';
import type {
  AdminBackupStatus,
  AdminCourseDirectory,
  AdminDirectoryRole,
  AdminModerationItem,
  AdminModerationQueue,
  AdminStatus,
  AuditLogEntry,
  AdminUserDirectory,
  KnowledgeBaseFile,
  KnowledgeBaseHitTest,
  KnowledgeBaseVersion,
  ModerationContentType,
} from './types';

const navItems = [
  { id: 'users', label: '用户与角色', icon: UserRoundCog },
  { id: 'courses', label: '课程与班级', icon: BookOpen },
  { id: 'moderation', label: '内容审核', icon: ShieldAlert },
  { id: 'agent-status', label: '服务状态', icon: Server },
  { id: 'knowledge-bases', label: '知识库版本', icon: Database },
  { id: 'audit-log', label: '审计记录', icon: History },
  { id: 'backup', label: '备份与恢复', icon: HardDrive },
];

const goldenCases = ['qa-001', 'qa-002', 'qa-003'];

export default function AdminPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const csrfToken = useAppStore((state) => state.session?.csrfToken || '');
  const section = location.pathname.split('/')[2] || 'agent-status';
  const [status, setStatus] = useState<AdminStatus | null>(null);
  const [backup, setBackup] = useState<AdminBackupStatus | null>(null);
  const [versions, setVersions] = useState<KnowledgeBaseVersion[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [files, setFiles] = useState<KnowledgeBaseFile[]>([]);
  const [hitTests, setHitTests] = useState<KnowledgeBaseHitTest[]>([]);
  const [audit, setAudit] = useState<AuditLogEntry[]>([]);
  const [versionName, setVersionName] = useState('');
  const [workflowId, setWorkflowId] = useState('');
  const [rollbackReason, setRollbackReason] = useState('');
  const [auditAction, setAuditAction] = useState('');
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [directoryState, setDirectoryState] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [directoryMessage, setDirectoryMessage] = useState('');
  const [directoryQuery, setDirectoryQuery] = useState('');
  const [directoryRole, setDirectoryRole] = useState<AdminDirectoryRole | ''>('');
  const [directoryPage, setDirectoryPage] = useState(1);
  const [userDirectory, setUserDirectory] = useState<AdminUserDirectory | null>(null);
  const [courseDirectory, setCourseDirectory] = useState<AdminCourseDirectory | null>(null);
  const [moderationState, setModerationState] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [moderationMessage, setModerationMessage] = useState('');
  const [moderationQueue, setModerationQueue] = useState<AdminModerationQueue | null>(null);
  const [moderationQuery, setModerationQuery] = useState('');
  const [moderationType, setModerationType] = useState<ModerationContentType | ''>('');
  const [moderationPage, setModerationPage] = useState(1);
  const [moderationReason, setModerationReason] = useState('');

  const selected = versions.find((item) => item.id === selectedId) || versions[0] || null;
  const selectedVersionId = selected?.id || '';

  const reload = useCallback(async () => {
    setState('loading');
    try {
      const [nextStatus, nextBackup, nextVersions, nextAudit] = await Promise.all([
        loadAdminStatus(),
        loadAdminBackupStatus(),
        loadKnowledgeBaseVersions(),
        loadAdminAuditLog({ action: auditAction, pageSize: 50 }),
      ]);
      setStatus(nextStatus);
      setBackup(nextBackup);
      setVersions(nextVersions);
      setAudit(nextAudit.items);
      setSelectedId((current) => nextVersions.some((item) => item.id === current) ? current : nextVersions[0]?.id || '');
      setState('ready');
      setMessage('');
    } catch (caught) {
      setState('error');
      setMessage(caught instanceof ApiError ? caught.message : '管理员服务暂时不可用。');
    }
  }, [auditAction]);

  useEffect(() => { void reload(); }, [reload]);

  useEffect(() => {
    if (!selectedVersionId) {
      setFiles([]);
      setHitTests([]);
      return;
    }
    let active = true;
    Promise.all([loadKnowledgeBaseFiles(selectedVersionId), loadKnowledgeBaseHitTests(selectedVersionId)])
      .then(([nextFiles, nextHitTests]) => {
        if (active) {
          setFiles(nextFiles);
          setHitTests(nextHitTests);
        }
      })
      .catch((caught) => {
        if (active) setMessage(caught instanceof ApiError ? caught.message : '知识库详情读取失败。');
      });
    return () => { active = false; };
  }, [selectedVersionId]);

  useEffect(() => {
    if (section !== 'users' && section !== 'courses') return;
    let active = true;
    setDirectoryState('loading');
    setDirectoryMessage('');
    const request = section === 'users'
      ? loadAdminUsers({ query: directoryQuery, role: directoryRole || undefined, page: directoryPage, pageSize: 20 })
      : loadAdminCourses({ query: directoryQuery, page: directoryPage, pageSize: 20 });
    request.then((result) => {
      if (!active) return;
      if (section === 'users') setUserDirectory(result as AdminUserDirectory);
      else setCourseDirectory(result as AdminCourseDirectory);
      setDirectoryState('ready');
    }).catch((caught) => {
      if (!active) return;
      setDirectoryState('error');
      setDirectoryMessage(caught instanceof ApiError ? caught.message : '管理目录读取失败。');
    });
    return () => { active = false; };
  }, [section, directoryQuery, directoryRole, directoryPage]);

  useEffect(() => {
    if (section !== 'moderation') return;
    let active = true;
    setModerationState('loading');
    setModerationMessage('');
    loadAdminModeration({ query: moderationQuery, contentType: moderationType || undefined, page: moderationPage, pageSize: 20 })
      .then((result) => {
        if (!active) return;
        setModerationQueue(result);
        setModerationState('ready');
      })
      .catch((caught) => {
        if (!active) return;
        setModerationState('error');
        setModerationMessage(caught instanceof ApiError ? caught.message : '审核队列读取失败。');
      });
    return () => { active = false; };
  }, [section, moderationQuery, moderationType, moderationPage]);

  useEffect(() => { setDirectoryPage(1); }, [section, directoryQuery, directoryRole]);
  useEffect(() => { setModerationPage(1); }, [section, moderationQuery, moderationType]);

  async function createVersion() {
    if (!versionName.trim() || busy) return;
    setBusy('create');
    try {
      await createKnowledgeBaseVersion(versionName.trim(), workflowId.trim(), csrfToken, 'admin-kb-create-' + Date.now());
      setVersionName('');
      setWorkflowId('');
      await reload();
      setMessage('知识库版本已创建为草稿。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '知识库版本创建失败。');
    } finally {
      setBusy('');
    }
  }

  async function uploadFile(file: File) {
    if (!selected || busy) return;
    setBusy('upload');
    try {
      await uploadKnowledgeBaseFile(selected.id, file, file.name, csrfToken, 'admin-kb-upload-' + selected.id + '-' + Date.now());
      const [nextFiles, nextVersions] = await Promise.all([loadKnowledgeBaseFiles(selected.id), loadKnowledgeBaseVersions()]);
      setFiles(nextFiles);
      setVersions(nextVersions);
      setMessage('文件已接收，版本进入处理中。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '文件上传失败。');
    } finally {
      setBusy('');
    }
  }

  async function runHit(caseId: string) {
    if (!selected || busy) return;
    setBusy(caseId);
    try {
      await runKnowledgeBaseHitTest(selected.id, caseId, csrfToken, 'admin-kb-hit-' + selected.id + '-' + caseId);
      const [nextHits, nextVersions] = await Promise.all([loadKnowledgeBaseHitTests(selected.id), loadKnowledgeBaseVersions()]);
      setHitTests(nextHits);
      setVersions(nextVersions);
      setMessage(caseId + ' 命中测试已完成。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : caseId + ' 命中测试失败。');
    } finally {
      setBusy('');
    }
  }

  async function advanceVersion() {
    if (!selected || busy) return;
    const target = selected.status === 'draft' ? 'processing' : selected.status === 'processing' ? 'tested' : selected.status === 'tested' ? 'published' : '';
    if (!target) return;
    setBusy('status');
    try {
      const next = await updateKnowledgeBaseStatus(selected.id, target, csrfToken, 'admin-kb-status-' + selected.id + '-' + target);
      setVersions((items) => items.map((item) => item.id === next.id ? next : item));
      await reload();
      setMessage('版本已迁移到' + statusLabel(target) + '。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '知识库状态迁移失败。');
    } finally {
      setBusy('');
    }
  }

  async function rollback() {
    if (!selected || !rollbackReason.trim() || busy) return;
    setBusy('rollback');
    try {
      await rollbackKnowledgeBase(selected.id, rollbackReason.trim(), csrfToken, 'admin-kb-rollback-' + selected.id + '-' + Date.now());
      setRollbackReason('');
      await reload();
      setMessage('知识库已回滚，旧版本状态已保留。');
    } catch (caught) {
      setMessage(caught instanceof ApiError ? caught.message : '知识库回滚失败。');
    } finally {
      setBusy('');
    }
  }

  async function decideModeration(item: AdminModerationItem, decision: 'approve' | 'reject') {
    if (busy || !moderationReason.trim()) return;
    setBusy('moderation-' + item.id);
    try {
      await decideAdminModeration(item.contentType, item.id, decision, moderationReason.trim(), csrfToken, `admin-moderation-${item.id}-${decision}-${Date.now()}`);
      setModerationReason('');
      const next = await loadAdminModeration({ query: moderationQuery, contentType: moderationType || undefined, page: moderationPage, pageSize: 20 });
      setModerationQueue(next);
      setMessage(decision === 'approve' ? '内容已审核通过。' : '内容已拒绝并隐藏。');
    } catch (caught) {
      setModerationMessage(caught instanceof ApiError ? caught.message : '审核操作失败。');
    } finally {
      setBusy('');
    }
  }

  if (state === 'loading' && !status) {
    return <><AdminPageHead eyebrow="管理员工作台" title="正在读取运维状态" description="正在读取服务、知识库、审计和恢复状态。" /><div className="empty-state">正在读取管理员数据…</div></>;
  }
  if (state === 'error' && !status) {
    return <><AdminPageHead eyebrow="管理员工作台" title="管理员服务不可用" description="没有把未知状态显示为正常。" /><div className="empty-state reader-error"><AlertTriangle size={22} /><strong>{message}</strong><button className="button secondary" onClick={() => void reload()}><RefreshCw size={16} />重新加载</button></div></>;
  }

  return <><AdminPageHead eyebrow="管理员工作台" title="平台运维与知识库" description="查看脱敏服务状态、知识库发布门槛、审计记录和恢复检查。" action={<button className="button secondary" onClick={() => void reload()} disabled={busy !== ''}><RefreshCw size={16} />刷新状态</button>} />{message && <div className="reader-notice conflict">{message}</div>}<div className="admin-layout"><nav className="admin-nav" aria-label="管理员导航">{navItems.map(({ id, label, icon: Icon }) => <button key={id} className={section === id ? 'active' : ''} onClick={() => navigate('/admin/' + id)}><Icon size={17} /><span>{label}</span></button>)}</nav><div className="admin-content">
    {section === 'knowledge-bases' && <KnowledgeBaseView selected={selected} versions={versions} files={files} hitTests={hitTests} versionName={versionName} workflowId={workflowId} rollbackReason={rollbackReason} busy={busy} onSelect={setSelectedId} onVersionName={setVersionName} onWorkflowId={setWorkflowId} onRollbackReason={setRollbackReason} onCreate={() => void createVersion()} onUpload={(file) => void uploadFile(file)} onRunHit={(caseId) => void runHit(caseId)} onAdvance={() => void advanceVersion()} onRollback={() => void rollback()} />}
    {section === 'agent-status' && <section className="admin-status-grid"><section className="section-block"><div className="section-title"><h2>服务状态</h2><span className="status-tag active">脱敏视图</span></div><div className="admin-facts"><span><small>Adapter</small><strong>{status?.adapter}</strong></span><span><small>真实 Workflow</small><strong>{status?.workflowConfigured ? '已配置' : '未配置'}</strong></span><span><small>当前模式</small><strong>{status?.mockWorkflow ? 'Mock' : '真实配置'}</strong></span></div></section><section className="section-block"><div className="section-title"><h2>已发布知识库</h2><Database size={18} /></div>{status?.publishedKb ? <div className="admin-published"><strong>{status.publishedKb.versionName}</strong><span>{status.publishedKb.hitStatus} · {status.publishedKb.status}</span></div> : <div className="empty-state">当前没有已发布知识库。</div>}</section><section className="section-block"><div className="section-title"><h2>运维边界</h2><ShieldCheck size={18} /></div><ul className="admin-check-list"><li>浏览器不接触 API Key、API Secret 或 Cookie。</li><li>备份由服务器任务管理，浏览器只显示核验状态。</li><li>知识库发布必须经过 manifest 和黄金问题门槛。</li></ul></section></section>}
    {section === 'audit-log' && <section className="section-block"><div className="section-title"><h2>审计记录</h2><div className="inline-controls"><input aria-label="筛选审计动作" value={auditAction} onChange={(event) => setAuditAction(event.target.value)} placeholder="按动作筛选" /><button className="icon-button" title="重新查询审计记录" aria-label="重新查询审计记录" onClick={() => void reload()}><RefreshCw size={16} /></button></div></div>{!audit.length ? <div className="empty-state">当前没有匹配的审计记录。</div> : <div className="admin-audit-table"><div className="admin-audit-head"><span>时间</span><span>动作</span><span>对象</span><span>操作者 / request ID</span><span>结果</span></div>{audit.map((item) => <div className="admin-audit-row" key={item.id}><span>{item.createdAt}</span><span>{item.action}</span><span>{item.objectType} · {item.objectId}</span><span>{item.actorUid}<small>{item.requestId || '未记录'}</small></span><span className="status-tag active">{item.result}</span></div>)}</div>}</section>}
    {section === 'backup' && <section className="admin-status-grid"><section className="section-block"><div className="section-title"><h2>备份状态</h2><HardDrive size={18} /></div>{backup && <div className="admin-facts"><span><small>管理方式</small><strong>{backup.managedBy}</strong></span><span><small>校验入口</small><strong>{backup.verification}</strong></span><span><small>恢复演练</small><strong>{backup.restoreRehearsal}</strong></span><span><small>Secret 排除</small><strong>{backup.secretsExcluded ? '是' : '否'}</strong></span></div>}</section><section className="section-block"><div className="section-title"><h2>恢复检查</h2><RotateCcw size={18} /></div><p className="form-help">浏览器不会直接启动宿主机备份或恢复命令。请在服务器上执行 verify_backup.sh 和 restore_rehearsal.sh，再刷新本页核对状态。</p><span className="status-tag">{backup?.status || '未报告'}</span></section></section>}
    {section === 'users' && <AdminUsersView directory={userDirectory} state={directoryState} message={directoryMessage} query={directoryQuery} role={directoryRole} onQuery={(value) => { setDirectoryPage(1); setDirectoryQuery(value); }} onRole={(value) => { setDirectoryPage(1); setDirectoryRole(value); }} onPage={setDirectoryPage} />}
    {section === 'courses' && <AdminCoursesView directory={courseDirectory} state={directoryState} message={directoryMessage} query={directoryQuery} onQuery={(value) => { setDirectoryPage(1); setDirectoryQuery(value); }} onPage={setDirectoryPage} />}
    {section === 'moderation' && <AdminModerationView queue={moderationQueue} state={moderationState} message={moderationMessage} query={moderationQuery} contentType={moderationType} reason={moderationReason} onQuery={setModerationQuery} onContentType={setModerationType} onReason={setModerationReason} onPage={setModerationPage} onDecision={(item, decision) => void decideModeration(item, decision)} />}
  </div></div></>;
}

function DirectorySource({ configured, source, message }: { configured: boolean; source: string; message?: string }) {
  return <div className="directory-source"><span className={`status-tag ${configured ? 'active' : 'pending'}`}>{configured ? '已配置' : '未配置'}</span><span>来源：{source === 'mock_fixture' ? '隔离夹具' : source === 'moodle_bridge' ? 'Moodle bridge' : '服务器配置'}</span>{message && <small>{message}</small>}</div>;
}

function DirectoryPager({ page, total, pageSize, onPage }: { page: number; total: number; pageSize: number; onPage: (page: number) => void }) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  return <div className="directory-pager"><span>第 {page} / {pages} 页 · 共 {total} 条</span><div><button className="button quiet" disabled={page <= 1} onClick={() => onPage(page - 1)}>上一页</button><button className="button quiet" disabled={page >= pages} onClick={() => onPage(page + 1)}>下一页</button></div></div>;
}

function AdminUsersView({ directory, state, message, query, role, onQuery, onRole, onPage }: { directory: AdminUserDirectory | null; state: 'idle' | 'loading' | 'ready' | 'error'; message: string; query: string; role: AdminDirectoryRole | ''; onQuery: (value: string) => void; onRole: (value: AdminDirectoryRole | '') => void; onPage: (page: number) => void }) {
  return <section className="section-block directory-panel"><div className="section-title"><div><h2>用户与角色</h2><p className="form-help">只读显示当前授权课程的脱敏目录；不提供浏览器端禁用、改角色或删除操作。</p></div><Users size={18} /></div>{directory && <DirectorySource configured={directory.configured} source={directory.source} message={directory.message} />}<div className="directory-controls"><input aria-label="搜索用户" value={query} onChange={(event) => onQuery(event.target.value)} placeholder="按用户标识或显示名搜索" /><select aria-label="筛选用户角色" value={role} onChange={(event) => onRole(event.target.value as AdminDirectoryRole | '')}><option value="">全部角色</option><option value="student">学生</option><option value="teacher">教师</option><option value="admin">管理员</option></select></div>{state === 'loading' && <div className="empty-state">正在读取用户目录…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={20} />{message}</div>}{state === 'ready' && directory && !directory.items.length && <div className="empty-state">{directory.configured ? '当前筛选下没有用户。' : 'Moodle 管理目录尚未配置，未显示伪造用户。'}</div>}{state === 'ready' && directory && directory.items.length > 0 && <><div className="directory-table"><div className="directory-table-head"><span>用户</span><span>角色</span><span>状态</span><span>最近访问</span></div>{directory.items.map((item) => <div className="directory-table-row" key={item.id}><span><strong>{item.displayName}</strong><small>{item.id}</small></span><span>{item.role === 'student' ? '学生' : item.role === 'teacher' ? '教师' : '管理员'}</span><span className={`status-tag ${item.status === 'active' ? 'active' : 'pending'}`}>{item.status === 'active' ? '正常' : item.status === 'suspended' ? '已停用' : '未知'}</span><span>{item.lastAccessedAt || '未记录'}</span></div>)}</div><DirectoryPager page={directory.page} total={directory.total} pageSize={directory.pageSize} onPage={onPage} /></>}</section>;
}

function AdminCoursesView({ directory, state, message, query, onQuery, onPage }: { directory: AdminCourseDirectory | null; state: 'idle' | 'loading' | 'ready' | 'error'; message: string; query: string; onQuery: (value: string) => void; onPage: (page: number) => void }) {
  return <section className="section-block directory-panel"><div className="section-title"><div><h2>课程与班级</h2><p className="form-help">只读显示 Adapter 当前绑定的课程及 Moodle bridge 提供的班级统计。</p></div><BookOpen size={18} /></div>{directory && <DirectorySource configured={directory.configured} source={directory.source} message={directory.message} />}<div className="directory-controls"><input aria-label="搜索课程" value={query} onChange={(event) => onQuery(event.target.value)} placeholder="按课程、教师或班级搜索" /></div>{state === 'loading' && <div className="empty-state">正在读取课程目录…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={20} />{message}</div>}{state === 'ready' && directory && !directory.items.length && <div className="empty-state">当前没有可显示的课程。</div>}{state === 'ready' && directory && directory.items.length > 0 && <><div className="directory-course-grid">{directory.items.map((item) => <article className="directory-course-card" key={item.id}><div><span className="eyebrow">课程 #{item.id}</span><h3>{item.name}</h3><p>{item.teacher} · {item.className}</p></div><div className="directory-course-facts"><span><small>章节</small><strong>{item.chapterCount}</strong></span><span><small>资料</small><strong>{item.resourceCount}</strong></span><span><small>进度</small><strong>{item.progress}%</strong></span><span><small>人数</small><strong>{item.enrollmentCount ?? '未提供'}</strong></span></div><span className={`status-tag ${item.status === 'active' ? 'active' : ''}`}>{item.status === 'active' ? '进行中' : '已归档'}</span></article>)}</div><DirectoryPager page={directory.page} total={directory.total} pageSize={directory.pageSize} onPage={onPage} /></>}</section>;
}

function AdminModerationView({ queue, state, message, query, contentType, reason, onQuery, onContentType, onReason, onPage, onDecision }: { queue: AdminModerationQueue | null; state: 'idle' | 'loading' | 'ready' | 'error'; message: string; query: string; contentType: ModerationContentType | ''; reason: string; onQuery: (value: string) => void; onContentType: (value: ModerationContentType | '') => void; onReason: (value: string) => void; onPage: (page: number) => void; onDecision: (item: AdminModerationItem, decision: 'approve' | 'reject') => void }) {
  return <section className="section-block moderation-panel"><div className="section-title"><div><h2>内容审核</h2><p className="form-help">处理课程成员举报的讨论主题和回复；每次决策都写入课程范围审计。</p></div><ShieldAlert size={18} /></div><div className="moderation-controls"><input aria-label="搜索待审核内容" value={query} onChange={(event) => onQuery(event.target.value)} placeholder="按主题或内容搜索" /><select aria-label="筛选审核类型" value={contentType} onChange={(event) => onContentType(event.target.value as ModerationContentType | '')}><option value="">全部内容</option><option value="topic">讨论主题</option><option value="reply">讨论回复</option></select><input aria-label="审核决定原因" value={reason} onChange={(event) => onReason(event.target.value)} maxLength={500} placeholder="填写审核原因后再处理" /></div>{message && <div className="reader-notice conflict">{message}</div>}{state === 'loading' && <div className="empty-state">正在读取审核队列…</div>}{state === 'error' && <div className="empty-state reader-error"><AlertTriangle size={20} />{message}</div>}{state === 'ready' && queue && !queue.items.length && <div className="empty-state">当前没有待审核内容。</div>}{state === 'ready' && queue && queue.items.length > 0 && <><div className="moderation-list">{queue.items.map((item) => <article className="moderation-row" key={`${item.contentType}-${item.id}`}><div className="moderation-row-head"><div><span className="status-tag pending">{item.contentType === 'topic' ? '讨论主题' : '讨论回复'}</span><strong>{item.title}</strong><small>作者引用：{item.authorRef} · {item.createdAt}</small></div><span className="status-tag pending">待审核</span></div><p>{item.body}</p><small className="moderation-context">主题 ID：{item.topicId}{item.replyId ? ` · 回复 ID：${item.replyId}` : ''}</small><div className="moderation-actions"><button className="button secondary" aria-label={`批准内容 ${item.id}`} onClick={() => onDecision(item, 'approve')} disabled={!reason.trim()}><CheckCircle2 size={15} />批准</button><button className="button quiet" aria-label={`拒绝内容 ${item.id}`} onClick={() => onDecision(item, 'reject')} disabled={!reason.trim()}><XCircle size={15} />拒绝</button></div></article>)}</div><DirectoryPager page={queue.page} total={queue.total} pageSize={queue.pageSize} onPage={onPage} /></>}</section>;
}

function KnowledgeBaseView({ selected, versions, files, hitTests, versionName, workflowId, rollbackReason, busy, onSelect, onVersionName, onWorkflowId, onRollbackReason, onCreate, onUpload, onRunHit, onAdvance, onRollback }: { selected: KnowledgeBaseVersion | null; versions: KnowledgeBaseVersion[]; files: KnowledgeBaseFile[]; hitTests: KnowledgeBaseHitTest[]; versionName: string; workflowId: string; rollbackReason: string; busy: string; onSelect: (id: string) => void; onVersionName: (value: string) => void; onWorkflowId: (value: string) => void; onRollbackReason: (value: string) => void; onCreate: () => void; onUpload: (file: File) => void; onRunHit: (caseId: string) => void; onAdvance: () => void; onRollback: () => void }) {
  return <section className="admin-grid"><section className="section-block admin-create"><div className="section-title"><h2>创建知识库版本</h2><span className="status-tag">manifest 由服务端绑定</span></div><div className="form-grid"><label>版本名称<input aria-label="知识库版本名称" value={versionName} onChange={(event) => onVersionName(event.target.value)} maxLength={100} placeholder="例如：课程知识库 v2" /></label><label>Workflow 标识<input aria-label="Workflow 标识" value={workflowId} onChange={(event) => onWorkflowId(event.target.value)} maxLength={160} placeholder="发布后的 Workflow 标识" /></label></div><button className="button primary" onClick={onCreate} disabled={busy !== '' || !versionName.trim()}>创建草稿<Database size={16} /></button></section><section className="section-block admin-version-panel"><div className="section-title"><h2>版本列表</h2><span className="status-tag">{versions.length} 个版本</span></div>{!versions.length ? <div className="empty-state">尚未创建知识库版本。</div> : <div className="admin-version-list">{versions.map((item) => <button key={item.id} className={item.id === selected?.id ? 'admin-version-row active' : 'admin-version-row'} onClick={() => onSelect(item.id)}><span><strong>{item.versionName}</strong><small>{item.sourceCount} 个来源 · {item.updatedAt || '待记录'}</small></span><span className={'status-tag ' + (item.status === 'published' ? 'active' : '')}>{statusLabel(item.status)}</span></button>)}</div>}</section><section className="section-block admin-detail-panel"><div className="section-title"><h2>{selected ? selected.versionName : '选择一个版本'}</h2>{selected && <span className={'status-tag ' + (selected.status === 'published' ? 'active' : '')}>{statusLabel(selected.status)}</span>}</div>{selected ? <><div className="admin-facts"><span><small>manifest hash</small><strong>{selected.manifestSha256.slice(0, 12) || '待生成'}…</strong></span><span><small>Workflow</small><strong>{selected.workflowId || '未绑定'}</strong></span><span><small>命中状态</small><strong>{selected.hitStatus}</strong></span></div><div className="admin-actions">{selected.status === 'draft' && <button className="button secondary" onClick={onAdvance} disabled={busy !== ''}>开始处理<RefreshCw size={15} /></button>}{selected.status === 'processing' && <button className="button secondary" onClick={onAdvance} disabled={busy !== ''}>通过测试门槛<ShieldCheck size={15} /></button>}{selected.status === 'tested' && <button className="button primary" onClick={onAdvance} disabled={busy !== ''}>发布版本<CheckCircle2 size={15} /></button>}{(selected.status === 'tested' || selected.status === 'published' || selected.status === 'archived') && <><input aria-label="回滚原因" value={rollbackReason} onChange={(event) => onRollbackReason(event.target.value)} placeholder="填写回滚原因" maxLength={500} /><button className="button quiet" onClick={onRollback} disabled={busy !== '' || !rollbackReason.trim()}>回滚到此版本<RotateCcw size={15} /></button></>}</div><div className="admin-upload"><label className="button secondary" htmlFor="admin-kb-file"><Upload size={15} />上传 PDF/Markdown</label><input id="admin-kb-file" className="sr-only" type="file" accept=".pdf,.md,application/pdf,text/markdown" onChange={(event) => { const file = event.target.files?.[0]; if (file) onUpload(file); event.currentTarget.value = ''; }} disabled={busy !== '' || !['draft', 'processing'].includes(selected.status)} />{!['draft', 'processing'].includes(selected.status) && <small>只有草稿或处理中版本可以接收文件。</small>}</div><div className="admin-subsection"><div className="section-title"><h3>已接收文件</h3><span>{files.length} 个</span></div>{files.length ? <div className="admin-file-list">{files.map((file) => <div className="admin-file-row" key={file.id}><FileText size={16} /><span><strong>{file.filename}</strong><small>{file.sizeBytes} bytes · {file.sha256.slice(0, 12)}…</small></span><span className="status-tag active">{file.status}</span></div>)}</div> : <div className="empty-state">当前版本还没有文件。</div>}</div><div className="admin-subsection"><div className="section-title"><h3>黄金问题</h3><span>{hitTests.filter((item) => item.status === 'passed').length} / 3 已通过</span></div><div className="admin-hit-list">{goldenCases.map((caseId) => { const result = hitTests.find((item) => item.caseId === caseId); return <div className="admin-hit-row" key={caseId}><span><strong>{caseId}</strong><small>{result?.expectedChapter || '固定课程问题'}</small></span><span className={'status-tag ' + (result?.status === 'passed' ? 'active' : '')}>{result?.status || '未执行'}</span><button className="text-button" onClick={() => onRunHit(caseId)} disabled={busy !== '' || !['processing', 'tested', 'failed'].includes(selected.status)}>执行测试</button></div>; })}</div></div></> : <div className="empty-state">创建版本后可查看生命周期和证据。</div>}</section></section>;
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = { draft: '草稿', processing: '处理中', tested: '已测试', published: '已发布', failed: '测试失败', archived: '已归档' };
  return labels[status] || status;
}

function AdminPageHead({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-head"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{description}</p></div>{action}</div>;
}
