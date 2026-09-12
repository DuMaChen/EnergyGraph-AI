/* GENERATED shared UI components extracted from src/App.tsx (BUILD-113 route-level code splitting). */
import { BookOpen, CheckCircle2, ChevronRight, ListChecks } from 'lucide-react';
import { Assignment, AssignmentQuestion, Chapter } from './types';

export function PageHead({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-head"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{description}</p></div>{action}</div>;
}

export function Metric({ icon, value, label, tone, suffix }: { icon: React.ReactNode; value: string; label: string; tone: string; suffix?: string }) { return <div className="metric"><span className={`metric-icon ${tone}`}>{icon}</span><div><strong>{value}<small>{suffix}</small></strong><span>{label}</span></div></div>; }

export function SectionTitle({ title, link, onClick }: { title: string; link: string; onClick: () => void }) { return <div className="section-title"><h2>{title}</h2><button className="text-button" onClick={onClick}>{link}<ChevronRight size={14} /></button></div>; }

export function ChapterRow({ chapter, onClick }: { chapter: Chapter; onClick: () => void }) { return <button className="chapter-row" onClick={onClick}><span className={`chapter-status ${chapter.status === '已完成' ? 'done' : ''}`}>{chapter.status === '已完成' ? <CheckCircle2 size={17} /> : <BookOpen size={16} />}</span><span className="row-main"><strong>{chapter.name}</strong><small>{chapter.lessons} 个学习单元 · {chapter.duration}</small></span><span className="row-progress"><span className="progress-line"><span style={{ width: `${chapter.progress}%` }} /></span><small>{chapter.progress}%</small></span><ChevronRight size={16} className="row-chevron" /></button>; }

export function TaskRow({ assignment, onClick }: { assignment: Assignment; onClick: () => void }) { return <button className="task-row" onClick={onClick}><span className={`task-icon ${assignment.status === '进行中' ? 'active' : ''}`}><ListChecks size={16} /></span><span className="row-main"><strong>{assignment.title}</strong><small>{assignment.type} · 截止 {assignment.dueAt}</small></span><span className={`status-tag ${assignment.status === '进行中' ? 'active' : ''}`}>{assignment.status}</span><ChevronRight size={16} className="row-chevron" /></button>; }

export function Notice({ icon, title, meta }: { icon: React.ReactNode; title: string; meta: string }) { return <div className="notice-row"><span>{icon}</span><div><strong>{title}</strong><small>{meta}</small></div></div>; }

export function QuestionBlock({ index, question, value, disabled, onChange }: { index: number; question: AssignmentQuestion; value: unknown; disabled: boolean; onChange: (value: unknown) => void }) {
  const selected = Array.isArray(value) ? value.map(String) : [];
  return <article className="question-block"><div className="question-heading"><span className="question-number">{index}</span><div><h2>{question.prompt}</h2><small>{question.maxScore} 分 · {question.questionType === 'essay' ? '主观题，提交后由教师复核' : question.questionType === 'short_answer' ? '简答题，提交后由教师复核' : '客观题，服务端自动评分'}</small></div></div>{question.questionType === 'short_answer' || question.questionType === 'essay' ? <textarea aria-label={`第 ${index} 题答案`} value={typeof value === 'string' ? value : ''} disabled={disabled} onChange={(event) => onChange(event.target.value)} placeholder="填写你的答案" /> : <div className="question-options">{question.options.map((option) => question.questionType === 'multiple_choice' ? <label key={option}><input type="checkbox" checked={selected.includes(option)} disabled={disabled} onChange={(event) => onChange(event.target.checked ? [...selected, option] : selected.filter((item) => item !== option))} />{option}</label> : <label key={option}><input type="radio" name={`question-${question.id}`} value={option} checked={value === option} disabled={disabled} onChange={() => onChange(option)} />{option}</label>)}</div>}</article>;
}
