# Frontend Hook & Modular Function Guidelines

> Reusable JavaScript patterns and event handling modules in `agent-ui`.

---

## 1. SSE Stream Consumer (`fetchSSE`)

Streaming responses from `/api/chat` must be parsed chunk-by-chunk using `ReadableStream`:

```javascript
async function fetchSSE(url, options, onChunk, onComplete, onError) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': state.csrfToken,
        'Idempotency-Key': operationKey('chat', options.body),
        ...options.headers
      }
    });

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errJson.detail || `HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep partial line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim();
          if (dataStr === '[DONE]') {
            onComplete && onComplete();
            return;
          }
          try {
            const data = JSON.parse(dataStr);
            onChunk(data);
          } catch (e) {
            console.warn('Failed to parse SSE data packet:', line);
          }
        }
      }
    }
    onComplete && onComplete();
  } catch (err) {
    onError && onError(err);
  }
}
```

---

## 2. Idempotency Key Derivation (`operationKey`)

To prevent replay attacks and duplicate submissions, all write requests generate deterministic operation keys:

```javascript
function operationKey(scope, payload) {
  const content = typeof payload === 'string' ? payload : JSON.stringify(payload);
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    hash = ((hash << 5) - hash) + content.charCodeAt(i);
    hash |= 0;
  }
  return `${scope}-${Math.abs(hash)}-${state.sessionId || 'anon'}`;
}
```
