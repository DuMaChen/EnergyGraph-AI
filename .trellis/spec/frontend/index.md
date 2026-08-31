# Frontend Development Guidelines: EnergyGraph-AI Agent UI

> Architecture, design system, and UI conventions for the EnergyGraph-AI single-page application.

---

## 1. Overview

The front-end (`agent-ui`) is a responsive Single-Page Application (SPA) designed with a modern academic and pedagogical aesthetic inspired by Zhihuishu (智慧树) and Xuexitong (超星学习通).

### Primary Capabilities
1. **Intelligent Course Assistant**: Real-time SSE streaming dialogue with Markdown formatting, LaTeX formula rendering (MathJax), and clickable knowledge citations.
2. **Interactive Knowledge Graph Canvas**: Visual graph visualization representing 20 core energy storage knowledge nodes across 6 chapters, highlighting prerequisite/subsequent learning pathways.
3. **Electronic Textbook & Courseware Reader**: Chapter-by-chapter PDF reader with keyword jumping and bidirectional sync with chat answers.
4. **Adaptive Assessment & Quiz System**: Chapter quizzes, mock exams, real-time grading, and mastery diagnosis.
5. **Teacher Workbench & Analytics**: Assignment review, AI grading assistance with human-in-the-loop override, and class learning distribution radar charts.

---

## 2. Guidelines Index

| Guide | Description | Key Topics |
|-------|-------------|------------|
| [Directory Structure](./directory-structure.md) | File organization, static assets, Nginx server config | `index.html`, `marked.min.js`, `nginx.conf` |
| [Component Guidelines](./component-guidelines.md) | UI layout, panels, modal dialogs, graph canvas | Chat box, knowledge graph, exam modal |
| [State Management](./state-management.md) | Client state, Moodle session sync, SSE stream accumulator | Auth tokens, chat history, graph state |
| [Hook & Modular Guidelines](./hook-guidelines.md) | Event listeners, API wrappers, stream parsers | `fetchStream`, `renderMarkdown` |
| [Type & Data Safety](./type-safety.md) | DOMPurify sanitization, XSS prevention, safe DOM updates | XSS filters, sanitization |
| [Quality Guidelines](./quality-guidelines.md) | Responsive breakpoints, accessibility, error toasts | Mobile support, performance |

---

## 3. Technology Stack

- **Core**: Vanilla HTML5 + Modern ES6+ JavaScript (zero build step required for maximum portability and zero bundle latency)
- **Styling**: Modern CSS3 (CSS Variables, Flexbox, CSS Grid, smooth transitions, responsive media queries)
- **Markdown & Math**: `marked.min.js` + `DOMPurify` + `MathJax 3`
- **Delivery**: Nginx Alpine container serving static files and proxying `/api/*` to `agent-adapter`.
