/* Slimmed by BUILD-113 route-level code splitting; page modules live in src/pages/* and shared UI in src/ui.tsx. */
import { Suspense, useEffect, useRef, useState } from 'react';
import { BrowserRouter, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from 'react-router';
import {
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  ChevronRight,
  CircleHelp,
  Clock3,
  FolderOpen,
  GraduationCap,
  Heart,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  MessageSquare,
  Network,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  Users,
  X,
} from 'lucide-react';
import { useSearchShortcut } from './a11y/shortcuts';
import { formatDocumentTitle, resolveRouteTitle } from './routeMeta';
import { ApiError, loadAssignments, loadChapters, loadCourses, loadNotifications, loadProfile, loadRecommendations, loadResources, openSession } from './api/client';
import { AppDataContext, usePlatformData } from './appData';
import { overallProgress, previewData } from './data/preview';
import { OfflineBanner } from './offline/OfflineBanner';
import { InstallPromptButton, UpdatePromptBanner } from './offline/pwaPrompts';
import { useAppStore } from './state/app';
import type { PlatformData, Role } from './types';
import { lazyRetry } from './lazyRetry';
import { useUnreadNotificationPolling } from './useUnreadPolling';

const AdminPage = lazyRetry(() => import('./AdminPage'));
const DashboardPage = lazyRetry(() => import('./pages/dashboard').then((m) => ({ default: m.DashboardPage })));
const CoursesPage = lazyRetry(() => import('./pages/courses').then((m) => ({ default: m.CoursesPage })));
const CourseScope = lazyRetry(() => import('./pages/courses').then((m) => ({ default: m.CourseScope })));
const CoursePage = lazyRetry(() => import('./pages/courses').then((m) => ({ default: m.CoursePage })));
const TasksPage = lazyRetry(() => import('./pages/tasks').then((m) => ({ default: m.TasksPage })));
const ExamsPage = lazyRetry(() => import('./pages/exams').then((m) => ({ default: m.ExamsPage })));
const ExamPage = lazyRetry(() => import('./pages/exams').then((m) => ({ default: m.ExamPage })));
const AssignmentPage = lazyRetry(() => import('./pages/assignments').then((m) => ({ default: m.AssignmentPage })));
const DiscussionsPage = lazyRetry(() => import('./pages/community').then((m) => ({ default: m.DiscussionsPage })));
const DiscussionDetailPage = lazyRetry(() => import('./pages/community').then((m) => ({ default: m.DiscussionDetailPage })));
const ActivitiesPage = lazyRetry(() => import('./pages/community').then((m) => ({ default: m.ActivitiesPage })));
const ActivityDetailPage = lazyRetry(() => import('./pages/community').then((m) => ({ default: m.ActivityDetailPage })));
const MessagesPage = lazyRetry(() => import('./pages/community').then((m) => ({ default: m.MessagesPage })));
const SearchPage = lazyRetry(() => import('./pages/search').then((m) => ({ default: m.SearchPage })));
const HelpPage = lazyRetry(() => import('./pages/misc').then((m) => ({ default: m.HelpPage })));
const SettingsPage = lazyRetry(() => import('./pages/misc').then((m) => ({ default: m.SettingsPage })));
const FavoritesPage = lazyRetry(() => import('./pages/misc').then((m) => ({ default: m.FavoritesPage })));
const ResourcesPage = lazyRetry(() => import('./pages/misc').then((m) => ({ default: m.ResourcesPage })));
const ProfilePage = lazyRetry(() => import('./pages/misc').then((m) => ({ default: m.ProfilePage })));
const GradesPage = lazyRetry(() => import('./pages/misc').then((m) => ({ default: m.GradesPage })));
const ResourceReaderPage = lazyRetry(() => import('./pages/reader').then((m) => ({ default: m.ResourceReaderPage })));
const AssistantPage = lazyRetry(() => import('./pages/assistant').then((m) => ({ default: m.AssistantPage })));
const TeacherPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherPage })));
const TeacherActivityManagerPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherActivityManagerPage })));
const TeacherResourceManagerPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherResourceManagerPage })));
const TeacherQuestionBankPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherQuestionBankPage })));
const TeacherAssignmentManagerPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherAssignmentManagerPage })));
const TeacherExamManagerPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherExamManagerPage })));
const TeacherGradebookPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherGradebookPage })));
const TeacherAssignmentPage = lazyRetry(() => import('./pages/teacher').then((m) => ({ default: m.TeacherAssignmentPage })));
const KnowledgeGraphPage = lazyRetry(() => import('./pages/knowledge').then((m) => ({ default: m.KnowledgeGraphPage })));

const roleNames: Record<Role, string> = { student: '学生', teacher: '教师', admin: '管理员' };
const emptyPlatformData: PlatformData = { courses: [], chapters: [], resources: [], assignments: [], profile: [], recommendations: [], notifications: [], unreadNotificationCount: 0, studyHours: null };
function moodleLoginHref(): string {
  const wantsUrl = `${window.location.origin}${import.meta.env.BASE_URL}`;
  return `/login/index.php?wantsurl=${encodeURIComponent(wantsUrl)}`;
}
const moodleSignupHref = '/login/signup.php';
function App() {
  const [booting, setBooting] = useState(true);
  const data = useAppStore((state) => state.data);
  const setData = useAppStore((state) => state.setData);
  const setSession = useAppStore((state) => state.setSession);
  const markSessionExpired = useAppStore((state) => state.markSessionExpired);
  const setPreview = useAppStore((state) => state.setPreview);
  const sessionExpired = useAppStore((state) => state.sessionExpired);

  useEffect(() => {
    let active = true;
    async function bootstrap() {
      try {
        const session = await openSession();
        const loadOptional = async <T,>(load: () => Promise<T>, fallback: T): Promise<T> => {
          try {
            return await load();
          } catch (error) {
            if (error instanceof ApiError && (error.code === 'session_expired' || error.code === 'not_authenticated')) throw error;
            return fallback;
          }
        };
        const [coursesResult, chapters, assignments, resources, profile, recommendations, notificationResult] = await Promise.all([
          loadOptional(() => loadCourses(), { items: [], page: 1, pageSize: 20, total: 0 }),
          loadOptional(loadChapters, []),
          loadOptional(loadAssignments, []),
          loadOptional(loadResources, []),
          loadOptional(loadProfile, []),
          loadOptional(loadRecommendations, []),
          loadOptional(() => loadNotifications(false, 1, 100), { items: [], unreadCount: 0, page: 1, pageSize: 100, total: 0, focusFound: false, focusedId: null }),
        ]);
        if (!active) return;
        setSession(session);
        setPreview(false);
        setData({
          // Once the server session is established, an empty response is a
          // real empty state. Never replace it with preview records.
          courses: coursesResult.items,
          chapters,
          assignments,
          resources,
          profile,
          recommendations,
          notifications: notificationResult.items,
          unreadNotificationCount: notificationResult.unreadCount,
          studyHours: null,
        });
      } catch (error) {
        if (!active) return;
        if (error instanceof ApiError && (error.code === 'session_expired' || error.code === 'not_authenticated')) {
          markSessionExpired();
          setPreview(false);
          setData(emptyPlatformData);
        } else {
          setPreview(true);
          setData(previewData);
        }
      } finally {
        if (active) setBooting(false);
      }
    }
    void bootstrap();
    return () => { active = false; };
  }, [markSessionExpired, setData, setPreview, setSession]);

  if (booting) return <LoadingScreen />;
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <AppDataContext.Provider value={sessionExpired ? emptyPlatformData : data ?? emptyPlatformData}>
        <AppShell />
      </AppDataContext.Provider>
    </BrowserRouter>
  );
}
function LoadingScreen() {
  return <main className="loading-screen"><div className="loading-mark"><GraduationCap size={24} /></div><p>正在建立课程空间…</p></main>;
}
function RouteLoading() {
  return <div className="route-loading" role="status" aria-live="polite"><RefreshCw size={18} />正在打开工作区…</div>;
}
function AppShell() {
  const role = useAppStore((state) => state.role());
  const preview = useAppStore((state) => state.preview);
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen);
  const session = useAppStore((state) => state.session);
  const sessionExpired = useAppStore((state) => state.sessionExpired);
  const markSessionExpired = useAppStore((state) => state.markSessionExpired);
  const clearSession = useAppStore((state) => state.clearSession);
  const pwaUpdateReady = useAppStore((state) => state.pwaUpdateReady);
  const data = usePlatformData();
  const location = useLocation();
  const navigate = useNavigate();
  const [globalQuery, setGlobalQuery] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const globalSearchRef = useRef<HTMLInputElement>(null);
  const userMenuTriggerRef = useRef<HTMLButtonElement>(null);
  const mainContentRef = useRef<HTMLElement>(null);
  const lastFocusedPathRef = useRef<string | null>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const sidebarRef = useRef<HTMLElement>(null);
  const sidebarCloseRef = useRef<HTMLButtonElement>(null);
  const progress = overallProgress(data.chapters);
  const unreadAnnouncement = useUnreadNotificationPolling();
  useSearchShortcut(globalSearchRef, () => {
    setGlobalQuery('');
    if (location.pathname === '/search') navigate('/search', { replace: true });
  });
  const closeUserMenu = () => {
    setUserMenuOpen(false);
    userMenuTriggerRef.current?.focus();
  };
  useEffect(() => {
    const handleSessionExpired = () => {
      markSessionExpired();
      setUserMenuOpen(false);
      navigate('/', { replace: true });
    };
    window.addEventListener('course:session-expired', handleSessionExpired);
    return () => window.removeEventListener('course:session-expired', handleSessionExpired);
  }, [markSessionExpired, navigate]);
  useEffect(() => {
    if (location.pathname === '/search') {
      setGlobalQuery(new URLSearchParams(location.search).get('q') || '');
    } else {
      setGlobalQuery('');
    }
  }, [location.pathname, location.search]);
  useEffect(() => {
    document.title = formatDocumentTitle(resolveRouteTitle(location.pathname));
  }, [location.pathname]);
  useEffect(() => {
    const previousPath = lastFocusedPathRef.current;
    lastFocusedPathRef.current = location.pathname;
    if (previousPath !== null && previousPath !== location.pathname) {
      mainContentRef.current?.focus({ preventScroll: true });
    }
  }, [location.pathname]);
  useEffect(() => {
    if (sidebarOpen) {
      sidebarCloseRef.current?.focus({ preventScroll: true });
      return;
    }
    const active = document.activeElement;
    if (active === document.body || (sidebarRef.current && sidebarRef.current.contains(active))) {
      menuButtonRef.current?.focus({ preventScroll: true });
    }
  }, [sidebarOpen]);
  useEffect(() => {
    if (!sidebarOpen) return;
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [sidebarOpen, setSidebarOpen]);
  function handleSidebarKeyDown(event: React.KeyboardEvent<HTMLElement>) {
    if (event.key !== 'Tab' || !sidebarRef.current) return;
    const focusable = Array.from(sidebarRef.current.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'));
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
  function submitGlobalSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = globalQuery.trim();
    navigate(query ? `/search?q=${encodeURIComponent(query)}` : '/search');
  }
  function signOut() {
    clearSession();
    setUserMenuOpen(false);
    if (preview) {
      navigate('/');
      return;
    }
    const sesskey = session?.csrfToken ? `?sesskey=${encodeURIComponent(session.csrfToken)}` : '';
    window.location.assign(`/login/logout.php${sesskey}`);
  }
  const navItems = [
    { to: '/', label: '学习工作台', icon: LayoutDashboard },
    { to: '/courses', label: '我的课程', icon: BookOpen },
    { to: '/course', label: '课程空间', icon: BookOpen },
    { to: '/tasks', label: '待办任务', icon: ListChecks },
    { to: '/exams', label: '考试', icon: Clock3 },
    { to: '/resources', label: '资料库', icon: FolderOpen },
    ...(role === 'student' ? [{ to: '/favorites', label: '资料收藏', icon: Heart }] : []),
    { to: '/knowledge-graph', label: '学习图谱', icon: Network },
    { to: '/discussions', label: '课程讨论', icon: MessageSquare },
    { to: '/activities', label: '课堂活动', icon: ListChecks },
    { to: '/assistant', label: '课程 Agent', icon: Bot },
  ];
  if (role !== 'student') navItems.push({ to: '/teacher', label: '教师工作台', icon: Users }, { to: '/teacher/activities', label: '活动管理', icon: ListChecks });
  if (role === 'admin') navItems.push({ to: '/admin', label: '管理员工作台', icon: ShieldCheck });

  return (
    <div className="app-shell">
      <span className="sr-only notification-live-region" role="status" aria-live="polite">{unreadAnnouncement}</span>
      <a className="skip-link" href="#main-content">跳到主内容</a>
      <aside ref={sidebarRef} onKeyDown={handleSidebarKeyDown} className={`sidebar ${sidebarOpen ? 'is-open' : ''}`}>
        <div className="brand"><span className="brand-mark"><GraduationCap size={19} /></span><span><strong>储能学习空间</strong><small>课程平台</small></span><button ref={sidebarCloseRef} className="icon-button sidebar-close" onClick={() => setSidebarOpen(false)} aria-label="关闭导航"><X size={18} /></button></div>
        <div className="profile-mini"><span className="avatar">{role === 'student' ? '林' : '师'}</span><span><strong>{role === 'student' ? '林同学' : roleNames[role]}</strong><small>{roleNames[role]} · 本学期</small></span></div>
        <nav className="main-nav" aria-label="主导航">
          <span className="nav-heading">我的学习</span>
          {navItems.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={() => setSidebarOpen(false)}><Icon size={18} /><span>{label}</span></NavLink>)}
          <span className="nav-heading nav-heading-spaced">账户与支持</span>
          <NavLink to="/profile" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={() => setSidebarOpen(false)}><BarChart3 size={18} /><span>学习记录</span></NavLink>
          <button className="nav-link nav-button" onClick={() => navigate('/help')}><CircleHelp size={18} /><span>帮助中心</span></button>
        </nav>
        <div className="course-mini"><div className="course-mini-title">电力系统储能技术</div><div className="course-mini-meta">6 章 · 20 份资料</div><div className="progress-line"><span style={{ width: `${progress}%` }} /></div><div className="course-mini-footer"><span>课程进度</span><strong>{progress}%</strong></div></div>
      </aside>
      {sidebarOpen && <button className="sidebar-overlay" onClick={() => setSidebarOpen(false)} aria-label="关闭导航遮罩" />}
      <div className="app-main">
        <header className="topbar">
          <button ref={menuButtonRef} className="icon-button menu-button" onClick={() => setSidebarOpen(true)} aria-label="打开导航"><Menu size={20} /></button>
          <form className="global-search" onSubmit={submitGlobalSearch}><Search size={17} /><input ref={globalSearchRef} aria-label="搜索课程资料" value={globalQuery} onChange={(event) => setGlobalQuery(event.target.value)} placeholder="搜索课程、资料或知识点" /></form>
          <div className="topbar-actions"><InstallPromptButton /><button className="icon-button" title="消息通知" aria-label={data.unreadNotificationCount ? `消息通知，${data.unreadNotificationCount} 条未读` : '消息通知'} onClick={() => navigate('/messages')}><Bell size={18} />{data.unreadNotificationCount > 0 && <i />}</button><button className="icon-button" title="设置" aria-label="设置" onClick={() => navigate('/settings')}><Settings2 size={18} /></button><div className="user-menu" onKeyDown={(event) => { if (event.key === 'Escape' && userMenuOpen) { event.preventDefault(); closeUserMenu(); } }}><button ref={userMenuTriggerRef} className="top-user top-user-menu" aria-label="打开用户菜单" aria-expanded={userMenuOpen} onClick={() => setUserMenuOpen((current) => !current)}><span className="avatar avatar-small">{role === 'student' ? '林' : role === 'admin' ? '管' : '师'}</span><span><strong>{role === 'student' ? '林同学' : roleNames[role]}</strong><small>{roleNames[role]}</small></span><ChevronRight size={14} className={userMenuOpen ? 'user-menu-chevron open' : 'user-menu-chevron'} /></button>{userMenuOpen && <div className="user-menu-panel" role="menu"><button role="menuitem" onClick={() => { closeUserMenu(); navigate('/profile'); }}><BarChart3 size={15} />我的学习记录</button><button role="menuitem" onClick={() => { closeUserMenu(); navigate('/settings'); }}><Settings2 size={15} />学习设置</button><button role="menuitem" onClick={signOut}><LogOut size={15} />退出课程</button></div>}</div></div>
        </header>
        <main className="content" id="main-content" tabIndex={-1} ref={mainContentRef}>
          {preview && <div className="preview-banner"><div className="preview-banner-copy"><CircleHelp size={16} /><span>当前为预览模式，展示示例课程数据；登录课程平台并完成接口配置后才会写入真实学习记录。</span></div><div className="preview-actions"><a className="button secondary" href={moodleLoginHref()}>登录课程平台<ArrowUpRight size={14} /></a><a className="button quiet" href={moodleSignupHref}>创建账号<ArrowUpRight size={14} /></a></div></div>}
          {sessionExpired && <div className="session-expired-banner" role="alert"><AlertTriangle size={16} /><span>课程会话已过期，已清理当前页面数据。请重新登录后继续学习。</span><button className="text-button" onClick={() => window.location.assign(moodleLoginHref())}>重新登录<ArrowUpRight size={14} /></button><a className="text-button" href={moodleSignupHref}>创建账号<ArrowUpRight size={14} /></a></div>}
          <UpdatePromptBanner visible={pwaUpdateReady} />
          <OfflineBanner />
          <Suspense fallback={<RouteLoading />}>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/course" element={<CoursePage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/courses/:courseId" element={<CourseScope />}>
              <Route index element={<CoursePage />} />
              <Route path="chapters" element={<CoursePage />} />
              <Route path="chapters/:chapterId" element={<CoursePage />} />
              <Route path="assignments" element={<TasksPage />} />
              <Route path="assignments/:assignmentId" element={<AssignmentPage />} />
              <Route path="exams" element={<ExamsPage />} />
              <Route path="exams/:examId" element={<ExamPage />} />
              <Route path="resources" element={<ResourcesPage />} />
              <Route path="resources/:resourceId" element={<ResourceReaderPage />} />
              <Route path="materials" element={<ResourcesPage />} />
              <Route path="discussions" element={<DiscussionsPage />} />
              <Route path="discussions/:topicId" element={<DiscussionDetailPage />} />
              <Route path="progress" element={<ProfilePage />} />
              <Route path="grades" element={<GradesPage />} />
              <Route path="agent" element={<AssistantPage />} />
            </Route>
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/tasks/:assignmentId" element={<AssignmentPage />} />
            <Route path="/exams" element={<ExamsPage />} />
            <Route path="/exams/:examId" element={<ExamPage />} />
            <Route path="/resources" element={<ResourcesPage />} />
            <Route path="/resources/:resourceId" element={<ResourceReaderPage />} />
            <Route path="/favorites" element={role !== 'student' ? <Navigate to="/" replace /> : <FavoritesPage />} />
            <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
            <Route path="/discussions" element={<DiscussionsPage />} />
            <Route path="/discussions/:topicId" element={<DiscussionDetailPage />} />
            <Route path="/activities" element={<ActivitiesPage />} />
            <Route path="/activities/:activityId" element={<ActivityDetailPage />} />
            <Route path="/messages" element={<MessagesPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/help" element={<HelpPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/assistant" element={<AssistantPage />} />
            <Route path="/teacher" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherPage />} />
            <Route path="/teacher/courses" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherPage />} />
            <Route path="/teacher/courses/:courseId" element={<CourseScope staffOnly />}>
              <Route index element={<TeacherPage />} />
              <Route path="overview" element={<TeacherPage />} />
              <Route path="editor" element={<TeacherPage />} />
              <Route path="question-bank" element={<TeacherQuestionBankPage />} />
              <Route path="assignments" element={<TeacherAssignmentManagerPage />} />
              <Route path="exams" element={<TeacherExamManagerPage />} />
              <Route path="activities" element={<TeacherActivityManagerPage />} />
              <Route path="resources" element={<TeacherResourceManagerPage />} />
              <Route path="gradebook" element={<TeacherGradebookPage />} />
              <Route path="grading" element={<TeacherGradebookPage />} />
              <Route path="analytics" element={<TeacherGradebookPage />} />
              <Route path="agent" element={<AssistantPage />} />
              <Route path="assignments/:assignmentId" element={<TeacherAssignmentPage />} />
            </Route>
            <Route path="/teacher/questions" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherQuestionBankPage />} />
            <Route path="/teacher/assignments" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherAssignmentManagerPage />} />
            <Route path="/teacher/exams" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherExamManagerPage />} />
            <Route path="/teacher/activities" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherActivityManagerPage />} />
            <Route path="/teacher/resources" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherResourceManagerPage />} />
            <Route path="/teacher/gradebook" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherGradebookPage />} />
            <Route path="/teacher/assignments/:assignmentId" element={role === 'student' ? <Navigate to="/" replace /> : <TeacherAssignmentPage />} />
            <Route path="/admin" element={role !== 'admin' ? <Navigate to="/" replace /> : <AdminPage />} />
            <Route path="/admin/:section" element={role !== 'admin' ? <Navigate to="/" replace /> : <AdminPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="*" element={<Navigate to={location.pathname.startsWith('/course') ? '/course' : '/'} replace />} />
          </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  );
}
export default App;
