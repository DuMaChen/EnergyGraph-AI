# Frontend State Management Guidelines

> Client-side application state, session persistence, and synchronization.

---

## 1. Global State Structure

The application maintains a single, reactive state store object:

```javascript
const state = {
  // Session & User
  user: null,          // { id: 'u101', name: '张同学', role: 'student' }
  csrfToken: '',
  sessionId: '',
  
  // Navigation & View
  activeTab: 'chat',   // 'chat' | 'graph' | 'textbook' | 'exam' | 'teacher' | 'profile'
  currentChapter: 1,
  
  // Chat History & Active Stream
  messages: [],        // Array of { id, role, content, citations, timestamp }
  isGenerating: false,
  
  // Knowledge Graph Data
  graphData: {
    nodes: [],
    edges: [],
    selectedNode: null
  },
  
  // Textbook Viewer
  pdfManifest: [],
  activePdf: null,
  activePage: 1,
  
  // Exam & Submissions
  currentExam: null,
  examAnswers: {},
  
  // Teacher Workbench
  assignments: [],
  selectedSubmission: null
};
```

---

## 2. State Mutation Conventions

1. **Explicit Reducer/Mutator Functions**: State should be modified through dedicated helper functions (e.g. `setActiveTab(tabName)`, `appendMessage(msg)`, `updateLastMessageChunk(chunk)`).
2. **Local Storage Synchronization**: User preferences (e.g. theme preference, last viewed textbook chapter) are stored in `localStorage` under key namespace `eg_ai_*`.
3. **Session Refresh**: On page load, `initSession()` queries `/api/session` to validate cookies, fetch CSRF token, and populate user roles before mounting UI views.
