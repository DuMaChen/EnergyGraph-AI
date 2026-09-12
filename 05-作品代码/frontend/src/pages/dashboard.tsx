/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { AlertTriangle, ArrowUpRight, BarChart3, Bell, BookOpen, Bot, CheckCircle2, ChevronRight, Clock3, FileText, GraduationCap, RefreshCw } from 'lucide-react';
import { ApiError, loadLearningPosition } from '../api/client';
import { ChapterRow, Metric, Notice, PageHead, SectionTitle, TaskRow } from '../ui';
import { LearningPosition } from '../types';
import { overallProgress } from '../data/preview';
import { useAppStore } from '../state/app';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { usePlatformData } from '../appData';

export function DashboardPage() {
  const data = usePlatformData();
  const navigate = useNavigate();
  const preview = useAppStore((state) => state.preview);
  const role = useAppStore((state) => state.role());
  const sessionCourseId = useAppStore((state) => state.session?.courseId || 0);
  const hasStudentSession = !preview && role === 'student' && sessionCourseId > 0;
  const [learningPosition, setLearningPosition] = useState<LearningPosition | null>(null);
  const [learningPositionState, setLearningPositionState] = useState<'idle' | 'loading' | 'ready' | 'error'>(hasStudentSession ? 'loading' : 'idle');
  const [learningPositionError, setLearningPositionError] = useState('');
  const [learningPositionReload, setLearningPositionReload] = useState(0);
  const progress = overallProgress(data.chapters);
  const pending = data.assignments.filter((item) => item.status !== '已完成');
  const scoredAssignments = data.assignments.filter((item) => item.score !== null && Number.isFinite(item.score));
  const averageScore = scoredAssignments.length
    ? Math.round(scoredAssignments.reduce((sum, item) => sum + Number(item.score), 0) / scoredAssignments.length)
    : null;
  const studyHours = data.studyHours === null ? '待同步' : `${data.studyHours} 小时`;
  const currentCoursePath = !preview && role === 'student' && sessionCourseId > 0
    ? `/courses/${encodeURIComponent(String(sessionCourseId))}`
    : '/course';
  const recentTitle = learningPosition?.resource.title || '';
  const compactRecentTitle = recentTitle.length > 24 ? `${recentTitle.slice(0, 24)}…` : recentTitle;

  useEffect(() => {
    let active = true;
    if (!hasStudentSession) {
      setLearningPosition(null);
      setLearningPositionError('');
      setLearningPositionState('idle');
      return () => { active = false; };
    }
    setLearningPosition(null);
    setLearningPositionError('');
    setLearningPositionState('loading');
    void loadLearningPosition()
      .then((position) => {
        if (!active) return;
        if (position && (!sessionCourseId || position.courseId !== sessionCourseId)) {
          setLearningPositionError('最近学习位置与当前课程不一致，请重试。');
          setLearningPositionState('error');
          return;
        }
        setLearningPosition(position);
        setLearningPositionState('ready');
      })
      .catch((caught: unknown) => {
        if (!active) return;
        setLearningPosition(null);
        setLearningPositionError(caught instanceof ApiError ? caught.message : '最近学习位置暂时无法读取，请检查网络后重试。');
        setLearningPositionState('error');
      });
    return () => { active = false; };
  }, [hasStudentSession, learningPositionReload, sessionCourseId]);

  function retryLearningPosition() {
    setLearningPositionReload((value) => value + 1);
  }

  function openLearningPosition() {
    if (!hasStudentSession) {
      navigate('/course');
      return;
    }
    if (learningPositionState === 'error') {
      retryLearningPosition();
      return;
    }
    if (learningPositionState !== 'ready') return;
    if (!learningPosition) {
      navigate(currentCoursePath);
      return;
    }
    navigate(`/courses/${encodeURIComponent(String(learningPosition.courseId))}/resources/${encodeURIComponent(learningPosition.resource.id)}?page=${learningPosition.progress.page}`);
  }

  const resumeButtonLabel = preview
    ? '继续学习'
    : role !== 'student'
      ? '进入课程空间'
      : learningPositionState === 'loading'
        ? '正在定位最近学习'
        : learningPositionState === 'error'
          ? '重试最近学习'
          : learningPosition
            ? `${learningPosition.resource.available ? '继续' : '查看状态'}：${compactRecentTitle}`
            : '进入当前课程';
  return <>
    <PageHead eyebrow="学习工作台" title="早上好，林同学" description="从上次学习的位置继续，完成今天最重要的课程任务。" action={<button className="button primary dashboard-resume-action" onClick={openLearningPosition} disabled={learningPositionState === 'loading'} aria-busy={learningPositionState === 'loading'} aria-describedby={hasStudentSession ? 'learning-position-status' : undefined} title={recentTitle ? `继续学习：${recentTitle}` : undefined}>{learningPositionState === 'loading' ? <RefreshCw size={16} className="spin" /> : <BookOpen size={16} />}<span>{resumeButtonLabel}</span></button>} />
    <section className="course-banner"><div className="course-banner-copy"><p className="eyebrow">当前课程</p><h2>电力系统储能技术</h2><p>面向电力系统储能组成、规划、接入运行和性能评估的专业课程。</p><div className="course-facts"><span><GraduationCap size={15} />{data.chapters.length} 个章节</span><span><FileText size={15} />{data.resources.length} 份资料</span><span><Clock3 size={15} />已学习 {studyHours}</span></div>{!preview && role === 'student' && <div id="learning-position-status" className={`learning-position-summary ${learningPositionState}`} role={learningPositionState === 'error' ? 'alert' : 'status'} aria-live="polite">{learningPositionState === 'loading' && <><RefreshCw size={17} className="spin" /><div><strong>正在读取最近学习位置</strong><span>请稍候，加载完成后即可继续。</span></div></>}{learningPositionState === 'ready' && learningPosition && <><FileText size={17} /><div><strong>{learningPosition.resource.title}</strong><span>第 {learningPosition.resource.chapterId} 章 · 第 {learningPosition.progress.page} 页 · 已学习 {Math.round(learningPosition.progress.percent)}%</span></div></>}{learningPositionState === 'ready' && !learningPosition && <><BookOpen size={17} /><div><strong>尚无已保存的学习位置</strong><span>进入当前课程空间选择资料开始学习。</span></div></>}{learningPositionState === 'error' && <><AlertTriangle size={17} /><div><strong>无法恢复最近学习位置</strong><span>{learningPositionError}</span></div><button className="text-button" onClick={retryLearningPosition}>重新定位<RefreshCw size={14} /></button></>}</div>}<button className="button warm" onClick={() => navigate(currentCoursePath)}>进入课程空间<ArrowUpRight size={16} /></button></div><div className="course-score"><span>总体进度</span><strong>{progress}%</strong><div className="progress-line light"><span style={{ width: `${progress}%` }} /></div><small>已完成 {data.chapters.filter((chapter) => chapter.status === '已完成').length} / {data.chapters.length} 个章节</small></div></section>
    <div className="metric-grid"><Metric icon={<CheckCircle2 />} value={String(data.assignments.filter((item) => item.status === '已完成').length)} label="已完成任务" tone="green" /><Metric icon={<Clock3 />} value={String(pending.length)} label="待处理任务" tone="orange" /><Metric icon={<BarChart3 />} value={averageScore === null ? '—' : String(averageScore)} label="已评分平均" tone="blue" suffix={averageScore === null ? undefined : '分'} /><Metric icon={<Bot />} value={String(data.recommendations.length)} label="学习建议" tone="gold" /></div>
    <div className="dashboard-grid"><section className="section-block"><SectionTitle title="继续学习" link="查看全部章节" onClick={() => navigate('/course')} /><div className="chapter-list compact">{data.chapters.slice(0, 4).map((chapter) => <ChapterRow key={chapter.id} chapter={chapter} onClick={() => navigate('/course')} />)}</div></section><section className="section-block"><SectionTitle title="最近待办" link="全部任务" onClick={() => navigate('/tasks')} /><div className="task-list">{pending.slice(0, 3).map((assignment) => <TaskRow key={assignment.id} assignment={assignment} onClick={() => navigate('/tasks')} />)}</div></section></div>
    <div className="dashboard-grid lower"><section className="section-block"><SectionTitle title="学习建议" link="查看学情" onClick={() => navigate('/profile')} /><div className="recommendation-list">{data.recommendations.slice(0, 3).map((item, index) => <div className="recommendation-row" key={item.id}><span className="recommendation-number">{String(index + 1).padStart(2, '0')}</span><div><strong>{item.title}</strong><small>{item.type} · {item.reason}</small></div><button className="icon-button" title={`查看${item.title}`} aria-label={`查看${item.title}`} onClick={() => navigate('/resources')}><ChevronRight size={17} /></button></div>)}{!data.recommendations.length && <div className="empty-state compact-empty">暂无学习建议。</div>}</div></section><section className="section-block notice-block"><SectionTitle title="课程动态" link="查看通知" onClick={() => navigate('/messages')} /><div className="notice-list">{data.notifications.slice(0, 3).map((item) => <Notice key={item.id} icon={<Bell />} title={item.title} meta={item.createdAt || item.audience} />)}{!data.notifications.length && <div className="empty-state compact-empty">暂无课程通知。</div>}</div></section></div>
  </>;
}
