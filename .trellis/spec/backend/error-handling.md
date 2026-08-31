# Backend Error Handling Guidelines

> Standardized error formats, status codes, and recovery strategies for `agent-adapter`.

---

## 1. Unified JSON Error Response Format

All error responses returned to clients must strictly adhere to the unified JSON schema:

```json
{
  "code": "ERROR_CODE_ENUM",
  "detail": "Human readable error message",
  "data": null,
  "request_id": "req-uuid4-string",
  "timestamp": 1756543200
}
```

---

## 2. Standard Error Codes & HTTP Mapping

| HTTP Status | Error Code | Scenario / Meaning | Client Handling |
|-------------|------------|-------------------|-----------------|
| `400 Bad Request` | `INVALID_PAYLOAD` | Missing required fields, schema mismatch, or input exceeding max length (`4000` chars) | Prompt user to fix input |
| `401 Unauthorized` | `UNAUTHORIZED` | Invalid or expired Moodle session token, missing CSRF token | Redirect to Moodle login |
| `403 Forbidden` | `FORBIDDEN_ROLE` | Student attempting to access teacher grading or admin metrics | Display permission denied |
| `404 Not Found` | `RESOURCE_NOT_FOUND` | PDF page, knowledge node, or assignment ID does not exist | Show resource not found badge |
| `429 Too Many Requests` | `RATE_LIMIT_EXCEEDED` | Request rate exceeded (`AGENT_RATE_LIMIT` per window) or concurrency limit (`AGENT_USER_CONCURRENCY`) hit | Show cooldown countdown |
| `502 Bad Gateway` | `UPSTREAM_WORKFLOW_ERROR` | iFlytek Xingchen API timed out, returned non-200, or invalid payload | Fallback to local RAG retrieval |
| `500 Internal Error` | `INTERNAL_SERVER_ERROR` | Unhandled server exception | Mask stack trace, log error with request ID |

---

## 3. Upstream Degradation & Fallback Strategy

When calling external AI APIs (iFlytek Xingchen):
1. **Timeout Control**: Requests to Xingchen Workflow must use an explicit timeout (`XINGCHEN_TIMEOUT_SECONDS=90`).
2. **Circuit Breaker / Fallback**: If Xingchen API fails, the adapter must not crash or return a raw 500 error. Instead, it falls back to `course_retrieval.py` to extract local textbook context and generate an informative structured response.
3. **SSE Heartbeat**: During streaming generation, the server sends `: ping\n\n` comments every 5 seconds to keep the connection alive through reverse proxies and load balancers.
