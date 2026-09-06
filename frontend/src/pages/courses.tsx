/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ArrowUpRight, BookOpen, Bot, CheckCircle2, ChevronLeft, ChevronRight, FileText, LayoutDashboard, RefreshCw } from 'lucide-react';
import { ApiError, loadCourses } from '../api/client';
import { CourseSort, CourseSummary, Resource } from '../types';
import { Navigate, Outlet, useNavigate, useParams, useSearchParams } from 'react-router';
import { PageHead, SectionTitle } from '../ui';
import { useAppStore } from '../state/app';
import { useEffect, useState } from 'react';
import { usePlatformData } from '../appData';

export function CoursesPage() {
  const preview = useAppStore((state) => state.preview);
  const data = usePlatformData();
  const navigate = useNavigate();
  const [courses, setCourses] = useState<CourseSummary[]>(data.courses);
  const [loading, setLoading] = useState(!preview);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [sort, setSort] = useState<CourseSort>('last_accessed');
  const [page, setPage] = useState(1);
  const pageSize = 6;
  const [total, setTotal] = useState(data.courses.length);
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  useEffect(() => {
    let active = true;
    if (preview) {
      const start = (page - 1) * pageSize;
      const sorted = [...data.courses].sort((left, right) => {
        if (sort === 'name') return left.name.localeCompare(right.name) || left.id - right.id;
        if (sort === 'progress') return right.progress - left.progress || left.id - right.id;
        if (sort === 'id') return left.id - right.id;
        return Number(right.lastAccessedAt !== null) - Number(left.lastAccessedAt !== null) || String(right.lastAccessedAt || '').localeCompare(String(left.lastAccessedAt || '')) || left.id - right.id;
      });
      setCourses(sorted.slice(start, start + pageSize));
      setTotal(sorted.length);
      setLoading(false);
      setError(null);
      return () => { active = false; };
    }
    setLoading(true);
    setError(null);
    void loadCourses({ sort, page, pageSize })
      .then((result) => {
        if (!active) return;
        setCourses(result.items);
        setTotal(result.total);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setCourses([]);
        setError(reason instanceof ApiError ? reason.message : '课程列表暂时无法加载，请重试。');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [data.courses, page, preview, reloadToken, sort]);

  return <>
    <PageHead eyebrow="课程中心" title="我的课程" description="查看已授权的课程空间，选择课程后继续学习。" action={<button className="button secondary" onClick={() => navigate('/')}><LayoutDashboard size={16} />返回工作台</button>} />
    <div className="course-list-toolbar" aria-label="课程列表工具">
      <div><span className="eyebrow">课程空间</span><strong>{total} 门课程</strong></div>
      <label><span>排序</span><select aria-label="课程排序" value={sort} onChange={(event) => { setSort(event.target.value as CourseSort); setPage(1); }}><option value="last_accessed">最近访问</option><option value="progress">学习进度</option><option value="name">课程名称</option><option value="id">课程编号</option></select></label>
    </div>
    {loading && <div className="route-loading" role="status"><RefreshCw size={18} />正在加载课程列表…</div>}
    {error && <div className="error-state" role="alert"><AlertTriangle size={18} /><div><strong>课程列表加载失败</strong><span>{error}</span></div><button className="button secondary" onClick={() => setReloadToken((value) => value + 1)}><RefreshCw size={15} />重试</button></div>}
    {!loading && !error && !courses.length && <div className="empty-state courses-empty"><BookOpen size={24} /><strong>暂无可用课程</strong><span>当前账号没有已授权的课程空间。</span></div>}
    {!loading && !error && courses.length > 0 && <section className="course-list-grid" aria-label="我的课程列表">{courses.map((course) => <article className="course-summary-card" key={course.id} data-course-id={course.id}>
      <div className="course-summary-card-head"><span className="course-summary-icon"><BookOpen size={20} /></span><span className={`status-tag ${course.status === 'active' ? 'active' : ''}`}>{course.status === 'active' ? '进行中' : '已归档'}</span></div>
      <h2>{course.name}</h2>
      <p className="course-summary-teacher">{course.teacher} · {course.className}</p>
      <div className="course-summary-meta"><span>{course.chapterCount} 个章节</span><span>{course.resourceCount} 份资料</span></div>
      <div className="course-summary-progress"><div><span>学习进度</span><strong>{course.progress}%</strong></div><div className="progress-line"><span style={{ width: `${course.progress}%` }} /></div></div>
      <button className="button primary course-summary-action" onClick={() => navigate(`/courses/${encodeURIComponent(String(course.id))}`)} aria-label={`进入课程 ${course.name}`}><BookOpen size={16} />进入课程</button>
    </article>)}</section>}
    {!loading && !error && totalPages > 1 && <nav className="course-pagination" aria-label="课程列表分页"><span>第 {page} / {totalPages} 页</span><button className="icon-button" type="button" aria-label="上一页" title="上一页" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}><ChevronLeft size={17} /></button><button className="icon-button" type="button" aria-label="下一页" title="下一页" disabled={page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))}><ChevronRight size={17} /></button></nav>}
  </>;
}

export function CourseScope({ staffOnly = false }: { staffOnly?: boolean }) {
  const { courseId: requestedCourseParam } = useParams();
  const session = useAppStore((state) => state.session);
  const role = useAppStore((state) => state.role());
  const data = usePlatformData();
  const requestedCourse = Number(requestedCourseParam || 0);
  const authorized = requestedCourse > 0 && (session ? requestedCourse === session.courseId : data.courses.some((course) => course.id === requestedCourse));
  if (staffOnly && role === 'student') return <Navigate to="/" replace />;
  if (!authorized) return <Navigate to="/courses" replace />;
  return <Outlet />;
}

export function CoursePage() {
  const data = usePlatformData();
  const navigate = useNavigate();
  const session = useAppStore((state) => state.session);
  const { courseId: requestedCourseParam, chapterId: requestedChapterParam } = useParams();
  const [searchParams] = useSearchParams();
  const requestedCourse = Number(requestedCourseParam || 0);
  const sessionCourseId = session?.courseId || 0;
  const requestedChapter = Number(searchParams.get('chapter_id') || requestedChapterParam || 0);
  const [chapterId, setChapterId] = useState(requestedChapter || 3);
  useEffect(() => {
    if (requestedChapter && data.chapters.some((item) => item.id === requestedChapter)) setChapterId(requestedChapter);
  }, [data.chapters, requestedChapter]);
  if (requestedCourse && ((sessionCourseId && requestedCourse !== sessionCourseId) || (!sessionCourseId && !data.courses.some((item) => item.id === requestedCourse)))) {
    return <Navigate to="/courses" replace />;
  }
  const chapter = data.chapters.find((item) => item.id === chapterId) || data.chapters[0];
  const resources = data.resources.filter((item) => item.chapterId === chapter?.id);
  return <><PageHead eyebrow="课程空间" title="电力系统储能技术" description="按章节学习课程内容，查看任务、资料和知识点进度。" action={<button className="button secondary" onClick={() => navigate('/assistant')}><Bot size={16} />课程 Agent</button>} /><div className="course-toolbar"><div className="tabs" role="tablist"><button className="tab active">章节学习</button><button className="tab" onClick={() => navigate('/tasks')}>作业与测验</button><button className="tab" onClick={() => navigate('/discussions')}>讨论</button><button className="tab" onClick={() => navigate('/profile')}>成绩</button></div><span className="course-toolbar-note"><CheckCircle2 size={15} />进度会在真实课程会话中保存</span></div><div className="course-layout"><aside className="chapter-sidebar"><div className="catalog-label">课程目录</div>{data.chapters.map((item) => <button key={item.id} className={`catalog-item ${item.id === chapter?.id ? 'active' : ''}`} onClick={() => setChapterId(item.id)}><span><strong>{item.name}</strong><small>{item.lessons} 个单元 · {item.progress}%</small></span><ChevronRight size={15} /></button>)}</aside><section className="course-detail"><div className="detail-heading"><div><p className="eyebrow">第 {chapter?.id} 章</p><h2>{chapter?.name.replace(/^第 \d+ 章 /, '')}</h2><p>{chapter?.lessons} 个学习单元 · 预计 {chapter?.duration}</p></div><span className={`status-tag ${chapter?.status === '学习中' ? 'active' : ''}`}>{chapter?.status}</span></div><div className="chapter-progress-card"><div><span>章节完成度</span><strong>{chapter?.progress}%</strong></div><div className="progress-line"><span style={{ width: `${chapter?.progress}%` }} /></div><small>完成阅读或任务点后，章节进度会自动更新。</small></div><SectionTitle title="章节资料" link="查看全部资料" onClick={() => navigate('/resources')} /><div className="resource-list">{(resources.length ? resources : data.resources.slice(0, 3)).map((resource) => <ResourceRow resource={resource} key={resource.id} />)}</div></section></div></>;
}

function ResourceRow({ resource }: { resource: Resource }) {
  const navigate = useNavigate();
  return <div className="resource-row"><span className="resource-icon"><FileText size={18} /></span><div className="row-main"><strong>{resource.title}</strong><small>{resource.type} · {resource.pageCount} 页 · {resource.version}</small></div><button className="button quiet" onClick={() => navigate(`/resources/${encodeURIComponent(resource.id)}`)}>{resource.available ? '打开资料' : '查看状态'}<ArrowUpRight size={15} /></button></div>;
}
