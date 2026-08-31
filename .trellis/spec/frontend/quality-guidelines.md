# Frontend Quality & Responsive Design Guidelines

> Usability standards, responsive breakpoints, and performance optimization for `agent-ui`.

---

## 1. Responsive Breakpoints

The application must render cleanly across mobile, tablet, and desktop viewports:

| Breakpoint | Target Devices | Layout Adaptations |
|------------|----------------|-------------------|
| `< 768px` (Mobile) | Smartphones | Single-column layout, bottom navigation bar, collapsed side drawer, full-width buttons |
| `768px - 1024px` (Tablet) | iPads, Tablets | Collapsible sidebar, 2-column grid for dashboard and quizzes |
| `> 1024px` (Desktop) | Laptops, Monitors | Full dual-pane view (Chat + Knowledge Graph/Textbook side by side) |

---

## 2. Performance & Network Optimization

1. **Zero Render-Blocking Dependencies**: Critical CSS is embedded in `index.html`. External scripts (`DomPurify`, `MathJax`) use `async`/`defer`.
2. **SVG Graph Virtualization**: Knowledge graph nodes use lightweight SVG elements rather than heavy 3D WebGL scenes to ensure instant loading on mobile devices.
3. **Optimized Event Debouncing**: Search input and viewport resizing listeners must be debounced with a 200ms threshold.
