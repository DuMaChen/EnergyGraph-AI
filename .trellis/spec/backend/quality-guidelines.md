# Backend Quality & Security Guidelines

> Code standards, forbidden patterns, security constraints, and testing criteria for `agent-adapter`.

---

## 1. Security Invariants

### 1.1 Authentication & Authorization
- Every API endpoint under `/api/` (except `/healthz` and `/api/session/login-mock` in test mode) must validate the session token.
- Role checks must be enforced explicitly via dependency injection:
  ```python
  async def require_teacher(session: SessionData = Depends(get_current_session)):
      if session.role not in ("teacher", "admin"):
          raise HTTPException(status_code=403, detail="Teacher role required")
      return session
  ```

### 1.2 CSRF & Injection Prevention
- State-modifying requests (`POST`, `PUT`, `DELETE`) must validate the `X-CSRF-Token` against the session.
- SQL queries executed directly must use parameterized queries. Raw string interpolation is forbidden.
- PDF file paths must be strictly checked to prevent path traversal (`../` forbidden; resolve within `course-data/` root).

---

## 2. Forbidden Patterns

| Forbidden Pattern | Reason | Compliant Alternative |
|-------------------|--------|-----------------------|
| Storing secrets in source files | Security leak risk | Load via `os.getenv` or `.env` |
| `eval()` or `exec()` | Remote code execution vulnerability | Use `json.loads` or explicit parsers |
| Unbounded in-memory collections | Memory exhaustion (OOM) | Enforce maximum cache size and LRU eviction |
| Non-atomic file writes for state | Corrupted state on crash | Write to `.tmp` then `os.replace` |
| Unhandled async exceptions in SSE generator | Hanging client connection | Wrap streaming loops in `try...finally` with error event |

---

## 3. Testing Standards

- **Unit Tests**: Coverage must be maintained above 85% for `app/main.py`, `app/course_store.py`, and `app/course_retrieval.py`.
- **Mock Tests**: All test suites must execute cleanly in offline environments (`MOCK_AUTH_MODE=true`, `MOCK_WORKFLOW_MODE=true`).
- **Regression Invariants**: Run `python3 scripts/run_local_acceptance.sh` before any commit to ensure all contract tests pass.
