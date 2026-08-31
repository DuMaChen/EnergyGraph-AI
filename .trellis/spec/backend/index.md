# Backend Development Guidelines: EnergyGraph-AI Agent Adapter

> Technical standards, architecture patterns, and conventions for the FastAPI backend adapter of the EnergyGraph-AI platform.

---

## 1. Overview & Architectural Role

The backend service (`agent-adapter`) is a high-concurrency FastAPI service positioned between the student/teacher UI (`agent-ui`), the Moodle LMS platform, and the iFlytek Xingchen (讯飞星辰) Workflow engine.

### Core Responsibilities
1. **Security & Session Management**: Validates Moodle authentication tokens, manages role-based access control (RBAC: Admin, Teacher, Student), enforces CSRF protection, and prevents token tampering using SHA-256 salted hashing.
2. **Workflow Proxy & Streaming**: Translates front-end user queries into iFlytek Xingchen API requests, streaming back Server-Sent Events (SSE) in real time while attaching verified citations from the course knowledge base.
3. **Course Data & Knowledge Graph Store**: Provides query interfaces for 20 courseware PDFs (439 pages), 20 knowledge nodes across 6 chapters, and 17 graph relationship edges.
4. **Teaching Business Logic**: Manages assignment submissions, automated and AI-assisted grading, student learning profile tracking, question bank generation, and scenario dialogues.
5. **Reliability & Resilience**: Enforces strict rate-limiting (token bucket per user), request concurrency control, idempotency key verification, and graceful fallback to local retrieval when upstream workflows are degraded.

---

## 2. Guidelines Index

| Guide | Description | Key Modules |
|-------|-------------|-------------|
| [Directory Structure](./directory-structure.md) | File organization, modular layout, entry points | `agent-adapter/app/`, `tests/` |
| [Database Guidelines](./database-guidelines.md) | Thread-safe in-memory store, MariaDB schema, persistence | `course_store.py`, `MariaDB` |
| [Error Handling](./error-handling.md) | Unified error formats, HTTP statuses, workflow fallbacks | `main.py`, `app.exception_handlers` |
| [Quality Guidelines](./quality-guidelines.md) | Security constraints, zero-leak secrets, unit testing | `tests/`, `pytest`, `unittest` |
| [Logging Guidelines](./logging-guidelines.md) | Structured JSON logging, audit trails, masking API keys | `logging`, audit logs |

---

## 3. Technology Stack & Dependencies

- **Framework**: FastAPI `>=0.115.0`
- **ASGI Server**: Uvicorn `[standard]`
- **HTTP Client**: HTTPX `0.28.1` (async/sync with streaming support)
- **PDF Processing**: PyPDF `6.10.0`
- **Testing**: `pytest`, `unittest`, FastAPI `TestClient`
- **Containerization**: Docker with Python 3.11-slim baseline

---

## 4. Key Architectural Invariants

1. **Zero Secret Leakage**: All upstream credentials (`XINGCHEN_API_KEY`, `XINGCHEN_API_SECRET`, `MARIADB_PASSWORD`) must be read from environment variables or `deploy/.env` and must never be exposed to the client or committed into the repository.
2. **Idempotency Guard**: All mutating state requests (e.g. assignment submission, grade sync) must require an `Idempotency-Key` header. Duplicate requests within the TTL window must return cached responses without re-executing.
3. **Streaming First**: Long-form AI responses must use SSE (`text/event-stream`) with heartbeat packets (`: ping`) to prevent gateway timeout during multi-step reasoning.
4. **Source Attribution**: All AI-generated answers referencing textbook knowledge must append verified citations with Chapter, Section, Title, and Page Number.
