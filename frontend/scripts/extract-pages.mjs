import ts from 'typescript';
import fs from 'fs';
import path from 'path';

const SRC = 'src/App.tsx';
const text = fs.readFileSync(SRC, 'utf8');
const sf = ts.createSourceFile(SRC, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

// ---------- collect imports ----------
const importBindings = new Map(); // name -> { module, typeOnly }
for (const s of sf.statements) {
  if (!ts.isImportDeclaration(s) || !s.moduleSpecifier || !ts.isStringLiteral(s.moduleSpecifier)) continue;
  const mod = s.moduleSpecifier.text;
  const clause = s.importClause;
  if (!clause) continue;
  if (clause.name) importBindings.set(clause.name.text, { module: mod, typeOnly: !!clause.isTypeOnly });
  const nb = clause.namedBindings;
  if (nb) {
    if (ts.isNamespaceImport(nb)) {
      importBindings.set(nb.name.text, { module: mod, typeOnly: !!clause.isTypeOnly, namespace: true });
    } else {
      nb.elements.forEach((el) => importBindings.set(el.name.text, { module: mod, typeOnly: !!el.isTypeOnly }));
    }
  }
}

// ---------- collect top-level statements + declared names ----------
const stmts = sf.statements;
function declaredNames(s) {
  const out = [];
  if (ts.isFunctionDeclaration(s) || ts.isClassDeclaration(s) || ts.isInterfaceDeclaration(s) || ts.isTypeAliasDeclaration(s) || ts.isEnumDeclaration(s) || ts.isModuleDeclaration(s)) {
    if (s.name) out.push(s.name.text);
  } else if (ts.isVariableStatement(s)) {
    for (const d of s.declarationList.declarations) {
      if (ts.isIdentifier(d.name)) out.push(d.name.text);
    }
  }
  return out;
}
const topLevel = new Map(); // name -> statement
for (const s of stmts) {
  for (const n of declaredNames(s)) {
    if (topLevel.has(n)) throw new Error(`duplicate top-level name: ${n}`);
    topLevel.set(n, s);
  }
}

function usedNames(node, out = new Set()) {
  ts.forEachChild(node, (child) => {
    if (ts.isIdentifier(child)) out.add(child.text);
    usedNames(child, out);
  });
  return out;
}

// ---------- move plan ----------
const pageFiles = {
  'src/pages/dashboard.tsx': ['DashboardPage'],
  'src/pages/courses.tsx': ['CoursesPage', 'CourseScope', 'CoursePage', 'ResourceRow'],
  'src/pages/tasks.tsx': ['TasksPage'],
  'src/pages/exams.tsx': ['ExamsPage', 'ExamPage'],
  'src/pages/assignments.tsx': ['readCachedAssignmentDraft', 'AssignmentPage'],
  'src/pages/community.tsx': ['DiscussionsPage', 'DiscussionDetailPage', 'ActivitiesPage', 'ActivityDetailPage', 'MessagesPage'],
  'src/pages/search.tsx': ['globalSearchKinds', 'globalSearchFilterKinds', 'globalSearchLabels', 'emptyGlobalSearch', 'previewGlobalSearch', 'globalSearchIcon', 'globalSearchTarget', 'globalSearchQueryString', 'globalSearchPath', 'SearchPage'],
  'src/pages/misc.tsx': ['HelpPage', 'SettingsPage', 'FavoritesPage', 'ResourcesPage', 'ProfilePage', 'GradesPage'],
  'src/pages/reader.tsx': ['readCachedResourceProgress', 'ResourceReaderPage'],
  'src/pages/assistant.tsx': ['AssistantPage'],
  'src/pages/teacher.tsx': ['TeacherPage', 'TeacherActivityManagerPage', 'TeacherResourceManagerPage', 'TeacherQuestionBankPage', 'TeacherAssignmentManagerPage', 'TeacherExamManagerPage', 'TeacherGradebookPage', 'TeacherAssignmentPage', 'SubmissionReview', 'Tool'],
  'src/pages/knowledge.tsx': ['KnowledgeGraphPage'],
};
const shared = ['PageHead', 'Metric', 'SectionTitle', 'ChapterRow', 'TaskRow', 'Notice', 'QuestionBlock', 'activityKindLabel', 'isOptionlessActivityKind', 'isSingleConfigurationActivityKind', 'syncGlobalNotificationState', 'previewExams', 'previewStudentTasks', 'studentTaskKinds', 'studentTaskStatuses', 'countStudentTasks', 'previewStudentTaskCounts'];

const plan = new Map(); // name -> file
for (const [file, names] of Object.entries(pageFiles)) for (const n of names) plan.set(n, file);
for (const n of shared) plan.set(n, 'src/ui.tsx');

function stmtsForFile(file) {
  const names = new Set([...plan.entries()].filter(([, f]) => f === file).map(([n]) => n));
  return stmts.filter((s) => declaredNames(s).some((n) => names.has(n)));
}

// fixpoint: any App top-level symbol used by a moved file also moves to ui.tsx
let changed = true;
let guard = 0;
while (changed) {
  changed = false;
  guard++;
  if (guard > 50) throw new Error('fixpoint did not converge');
  const files = new Set([...plan.values()]);
  for (const file of files) {
    const used = new Set();
    stmtsForFile(file).forEach((s) => usedNames(s, used));
    for (const n of used) {
      if (topLevel.has(n) && !plan.has(n) && n !== 'KnowledgeGraphCanvas') {
        plan.set(n, 'src/ui.tsx');
        changed = true;
      }
    }
  }
}

// ---------- helpers for emitting imports ----------
function relPath(fromDir, toFile) {
  let rel = path.relative(fromDir, toFile).replace(/\\/g, '/').replace(/\.tsx?$/, '');
  if (!rel.startsWith('.')) rel = `./${rel}`;
  return rel;
}

function emitImports(file, used) {
  const dir = path.dirname(file);
  const local = new Set([...plan.entries()].filter(([, f]) => f === file).map(([n]) => n));
  const groups = new Map(); // module -> { names:Set, typeOnly:boolean }
  for (const name of used) {
    if (local.has(name) || name === 'KnowledgeGraphCanvas') continue;
    const binding = importBindings.get(name);
    if (binding) {
      let g = groups.get(binding.module);
      if (!g) { g = { names: new Set(), typeOnly: binding.typeOnly }; groups.set(binding.module, g); }
      g.names.add(name);
      g.typeOnly = g.typeOnly && binding.typeOnly;
      continue;
    }
    const target = plan.get(name);
    if (target) {
      const mod = relPath(dir, target);
      let g = groups.get(mod);
      if (!g) { g = { names: new Set(), typeOnly: false }; groups.set(mod, g); }
      g.names.add(name);
      continue;
    }
    // otherwise a global / UMD type (window, React, ...) -> ignore
  }
  const lines = [];
  for (const [mod, g] of groups) {
    const body = [...g.names].sort().join(', ');
    lines.push(g.typeOnly ? `import type { ${body} } from '${mod}';` : `import { ${body} } from '${mod}';`);
  }
  return lines.sort();
}

// ---------- write page modules ----------
for (const [file, names] of Object.entries(pageFiles)) {
  const fileNames = new Set(names);
  const own = stmtsForFile(file);
  const used = new Set();
  own.forEach((s) => usedNames(s, used));
  const code = own.map((s) => s.getText(sf)).join('\n\n');
  let header = ['/* GENERATED page module extracted from src/App.tsx (BUILD-113 route-level code splitting). */', ...emitImports(file, used)];
  if (file === 'src/pages/knowledge.tsx') {
    header.push(`import { lazy } from 'react';`, `const KnowledgeGraphCanvas = lazy(() => import('../KnowledgeGraphCanvas'));`);
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, header.join('\n') + '\n\n' + code + '\n', 'utf8');
  console.log(`wrote ${file} (${fileNames.size} symbols)`);
}

// ---------- write ui.tsx ----------
{
  const file = 'src/ui.tsx';
  const own = stmtsForFile(file);
  const used = new Set();
  own.forEach((s) => usedNames(s, used));
  const code = own.map((s) => s.getText(sf)).join('\n\n');
  const header = ['/* GENERATED shared UI module extracted from src/App.tsx (BUILD-113 route-level code splitting). */', ...emitImports(file, used)];
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, header.join('\n') + '\n\n' + code + '\n', 'utf8');
  console.log(`wrote ${file} (${[...plan.entries()].filter(([, f]) => f === file).length} symbols)`);
}

// ---------- rewrite App.tsx ----------
{
  const moved = new Set(plan.keys());
  const keepStmts = stmts.filter((s) => {
    const names = declaredNames(s);
    if (names.length === 0) return true; // export default etc.
    if (names.includes('KnowledgeGraphCanvas')) return false; // handled inside knowledge.tsx
    return !names.some((n) => moved.has(n));
  });
  const keptUsed = new Set();
  keepStmts.forEach((s) => usedNames(s, keptUsed));
  keptUsed.add('lazy'); // AdminPage + page lazy consts

  // group kept imports by module
  const keptGroups = new Map();
  for (const name of keptUsed) {
    const b = importBindings.get(name);
    if (!b) continue;
    let g = keptGroups.get(b.module);
    if (!g) { g = { names: new Set(), typeOnly: b.typeOnly, namespace: !!b.namespace }; keptGroups.set(b.module, g); }
    g.names.add(name);
    g.typeOnly = g.typeOnly && b.typeOnly;
  }
  const uiNames = [...keptUsed].filter((n) => plan.get(n) === 'src/ui.tsx').sort();

  const importLines = [];
  const pushGroup = (mod, names, typeOnly = false, namespace = false) => {
    if (!names.length) return;
    if (namespace) importLines.push(`import * as ${names[0]} from '${mod}';`);
    else importLines.push(`${typeOnly ? 'import type' : 'import'} { ${names.sort().join(', ')} } from '${mod}';`);
  };
  // deterministic order: react, react-router, lucide-react, ./ui, then the rest sorted
  const ordered = ['react', 'react-router', 'lucide-react', './ui', ...[...keptGroups.keys()].filter((m) => !['react', 'react-router', 'lucide-react', './ui'].includes(m)).sort()];
  for (const mod of ordered) {
    if (mod === './ui') {
      if (uiNames.length) importLines.push(`import { ${uiNames.join(', ')} } from './ui';`);
      continue;
    }
    const g = keptGroups.get(mod);
    if (!g) continue;
    if (mod === 'lucide-react') {
      importLines.push('import {');
      for (const n of [...g.names].sort()) importLines.push(`  ${n},`);
      importLines.push(`} from 'lucide-react';`);
    } else {
      pushGroup(mod, [...g.names], g.typeOnly, g.namespace);
    }
  }

  // lazy page consts
  const lazyLines = ["const AdminPage = lazy(() => import('./AdminPage'));"];
  for (const [file, names] of Object.entries(pageFiles)) {
    for (const n of names) {
      if (!keptUsed.has(n)) continue;
      lazyLines.push(`const ${n} = lazy(() => import('${file.replace(/^src\//, './').replace(/\.tsx$/, '')}').then((m) => ({ default: m.${n} })));`);
    }
  }

  const keptCode = keepStmts.map((s) => s.getText(sf)).join('\n');
  const out = [
    '/* Slimmed by BUILD-113 route-level code splitting; page modules live in src/pages/* and shared UI in src/ui.tsx. */',
    ...importLines,
    '',
    ...lazyLines,
    '',
    keptCode,
    'export default App;',
    '',
  ].join('\n');
  fs.writeFileSync(SRC, out, 'utf8');
  console.log('wrote slim src/App.tsx');
  console.log('--- plan ---');
  for (const [n, f] of [...plan.entries()].sort((a, b) => a[1].localeCompare(b[1]) || a[0].localeCompare(b[0]))) console.log(`${f}  <-  ${n}`);
}
