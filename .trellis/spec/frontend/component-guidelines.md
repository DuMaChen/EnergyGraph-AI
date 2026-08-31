# Frontend Component Guidelines

> Component patterns, UI design systems, and interaction rules for `agent-ui`.

---

## 1. Visual Design Tokens

```css
:root {
  /* Brand Theme: Academic Forest Green & Warm Energy Orange */
  --brand-green: #0b6b59;
  --brand-green-hover: #085244;
  --brand-green-light: #e8f5f1;
  --brand-green-border: #a3d9cb;
  --brand-orange: #ea580c;
  --brand-blue: #0284c7;
  --brand-purple: #7c3aed;
  
  /* Neutral Grays */
  --bg-page: #f5f6f8;
  --bg-card: #ffffff;
  --text-main: #1f2937;
  --text-muted: #6b7280;
  --text-light: #9ca3af;
  --border-color: #e5e7eb;
  
  /* Elevations & Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

---

## 2. Core UI Components

### 2.1 Chat Message Bubble
- **User Message**: Aligned right, background `--brand-green`, text white.
- **AI Assistant Message**: Aligned left, background white, border `--border-color`, includes:
  - Role badge (e.g. *“智能助教”* or *“电网调度专家”*).
  - Streamed Markdown content rendered via `marked.parse()`.
  - LaTeX mathematical equations rendered via `MathJax.typesetPromise()`.
  - Expandable Citation Cards (`.citation-badge`) showing Chapter, Section, Page number, and excerpt.
  - Mandatory AI disclaimer: *“AI 生成内容，请核验课程来源”*.

### 2.2 Knowledge Graph Canvas
- Interactive SVG / Canvas rendering 20 knowledge nodes color-coded by chapter (1 to 6).
- Node click triggers side-drawer showing:
  - Key definitions and formulas.
  - Prerequisite & subsequent concept connections.
  - Direct button to *“在电子教材中打开此知识点”* or *“向 AI 提问此知识点”*.

### 2.3 Exam & Quiz Modal
- Clean multi-step questionnaire layout.
- Instant feedback mode showing correct answers, explanations, and knowledge point links after submission.
