#!/usr/bin/env python3
"""Static checks for BUILD-100 frontend recovery, lazy loading, and cache policy."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
app = (ROOT / "frontend/src/App.tsx").read_text(encoding="utf-8")
main = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
nginx = (ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
error_boundary = (ROOT / "frontend/src/ErrorBoundary.tsx").read_text(encoding="utf-8")
observability = (ROOT / "frontend/src/lib/observability.ts").read_text(encoding="utf-8")

assert "lazy(() => import('./AdminPage'))" in app
assert '<Suspense fallback={<RouteLoading />}>' in app
assert 'loading="lazy"' in app
assert 'referrerPolicy="no-referrer"' in app
assert "<ErrorBoundary>" in main
assert "reportClientError(error, 'render')" in error_boundary
assert "MAX_RECORDS = 20" in observability
assert 'add_header Cache-Control "no-store" always' in nginx
assert 'max-age=31536000, immutable' in nginx
print("FRONTEND_HARDENING_OK")
