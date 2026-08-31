# Backend Logging Guidelines

> Structured logging, security masking, and audit log conventions for `agent-adapter`.

---

## 1. Structured Log Format

All backend logs must use structured output with context tags:

```json
{
  "timestamp": "2026-08-31T18:57:00.123Z",
  "level": "INFO",
  "logger": "agent_adapter.chat",
  "request_id": "req-9c4b1234",
  "user_id_hash": "a1b2c3d4...",
  "role": "student",
  "endpoint": "/api/chat",
  "status_code": 200,
  "duration_ms": 142.5,
  "message": "Chat stream completed successfully"
}
```

---

## 2. Security Masking Rules (Strictly Enforced)

1. **Never Log Secrets**:
   - `XINGCHEN_API_KEY`, `XINGCHEN_API_SECRET`, Bearer Tokens, and passwords must NEVER appear in logs.
   - Any header containing `Authorization`, `Cookie`, or `X-Api-Key` must be redacted (`Bearer ***`).
2. **Pseudonymize User Identifiers**:
   - Student/Teacher real names or emails must not be logged. Use salted SHA-256 hash (`AGENT_UID_SALT`) for traceability.
3. **Truncate Query Payloads in Debug Logs**:
   - Limit prompt preview in logs to the first 64 characters to avoid sensitive data exposure.

---

## 3. Log Levels

| Level | Usage Scenario |
|-------|----------------|
| `DEBUG` | Local development tracing (disabled by default in production) |
| `INFO` | Standard lifecycle events, request start/finish, auth successes, grade syncs |
| `WARNING` | Rate limit warnings, cache misses requiring expensive fallback, retried requests |
| `ERROR` | Upstream Xingchen API failures, parse errors, unhandled exceptions |
| `CRITICAL` | Disk write failures, database connection loss, integrity violations |
