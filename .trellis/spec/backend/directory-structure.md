# Backend Directory Structure & File Layout

> Directory layout and responsibilities of the `agent-adapter` service.

---

## 1. Directory Tree

```text
agent-adapter/
├── Dockerfile                  # Container definition (Python 3.11-slim, port 8081)
├── README.md                   # Service overview and local setup instructions
├── requirements.txt            # Pinned dependencies (fastapi, httpx, pypdf, uvicorn)
├── app/
│   ├── __init__.py             # Package marker
│   ├── main.py                 # FastAPI application, route handlers, middleware, SSE streamer
│   ├── course_store.py         # Thread-safe in-memory business state store & disk persistence
│   └── course_retrieval.py     # Local textbook search, PDF page extraction, knowledge graph querying
└── tests/
    ├── __init__.py             # Test package marker
    ├── test_main.py            # Unit & integration tests for API routes and auth contracts
    ├── test_course_retrieval.py # Unit tests for PDF search, keyword matching, and citation extraction
    ├── test_workflow_state_machine.py # State machine validation for scenario and learning paths
    └── test_e2e_live_scenarios.py # End-to-end integration tests for user journeys
```

---

## 2. Module Responsibilities

### `app/main.py`
- **Application Factory**: Initializes FastAPI app with CORS middleware, lifespan events, and global exception handlers.
- **Session & Auth Middleware**: Extracts and verifies session cookie / bearer token against Moodle session endpoint or local dev mock.
- **Route Groups**:
  - `/api/session`: Current user profile, role validation, CSRF token issuance.
  - `/api/chat`: Chat completion endpoint (supporting both standard JSON and SSE streaming).
  - `/api/graph`: Knowledge graph nodes and edges query endpoint.
  - `/api/textbook`: Course PDF page retrieval and search.
  - `/api/assignments`: Assignment list, details, student submissions, and grading.
  - `/api/exam`: Adaptive question bank generation, exam submission, and auto-scoring.
  - `/api/scenarios`: Interactive situational learning roleplay and step progression.
  - `/api/learning-profile`: Student mastery metrics and weak knowledge point tracking.
  - `/api/admin`: System metrics, rate-limit status, audit logs, and cache controls.
  - `/healthz`: Liveness and readiness probe for Docker / Caddy reverse proxy.

### `app/course_store.py`
- Implements `CourseStore` class with `threading.RLock()` for thread safety.
- Handles in-memory caching of assignments, submissions, exam records, user notes, and scenario sessions.
- Supports periodic JSON snapshot serialization and restore from disk.

### `app/course_retrieval.py`
- Parses and indexes normalized courseware manifests (`course-data/normalized/manifest.json`).
- Extracts text chunks and page metadata from PDF assets using `pypdf`.
- Implements keyword-based BM25 / TF-IDF style local retrieval fallback when external vector DB is unavailable.
- Constructs structured citations: `{"source": "1.1-储能技术概论.pdf", "page": 12, "chapter": 1, "title": "抽水蓄能基本原理"}`.
