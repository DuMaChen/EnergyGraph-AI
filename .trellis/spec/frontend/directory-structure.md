# Frontend Directory Structure & Assets

> Directory organization and asset management for `agent-ui`.

---

## 1. Directory Tree

```text
agent-ui/
├── Dockerfile                  # Nginx Alpine container definition (port 80)
├── nginx.conf                  # Nginx web server configuration with /api reverse proxy
├── index.html                  # Single-page application containing UI layout, styles, and scripts
└── marked.min.js               # Self-contained offline Markdown rendering library
```

---

## 2. File Responsibilities

### `index.html`
- **Head Section**: Viewport meta, CDN fallbacks for DomPurify and MathJax, CSS design system definitions.
- **Header & Navigation Bar**:
  - Course title: *电力系统储能技术* (Energy Storage Technology for Power Systems).
  - Navigation tabs: 课程问答 (Q&A), 知识图谱 (Knowledge Graph), 电子教材 (Textbook), 随堂测验 (Quizzes), 教师工作台 (Teacher Workbench), 学情分析 (Analytics).
  - User profile badge with role indicator (Student / Teacher / Admin).
- **Main Viewport Panels**:
  - `tab-chat`: Conversation stream, input box, scenario role selector, citation inspector.
  - `tab-graph`: Interactive SVG / Canvas graph of 20 knowledge nodes with search & zoom.
  - `tab-textbook`: 6-chapter PDF reader with page selector and highlighted excerpts.
  - `tab-exam`: Dynamic assessment questionnaire with single-choice, multiple-choice, and open questions.
  - `tab-teacher`: Assignment list, student submission viewer, AI score comparison, and approve button.
  - `tab-profile`: Mastery progress bars and personalized review recommendations.
- **Script Sections**:
  - API Client & SSE Stream Parser.
  - Markdown / MathJax rendering pipeline.
  - Knowledge Graph rendering engine.
  - Modal managers (Login, Settings, Citation Details).

### `nginx.conf`
- Configures static file caching headers for HTML/JS/CSS assets.
- Sets up upstream proxy to `http://agent-adapter:8081/api/` with buffering disabled (`proxy_buffering off`) for instantaneous SSE streaming.
