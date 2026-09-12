#!/usr/bin/env python3
"""Measure local Adapter concurrency and rate-limit behavior in mock mode."""

from __future__ import annotations

import asyncio
import os
import statistics
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "performance-test-only")
os.environ.setdefault("AGENT_RATE_LIMIT", "20")
os.environ.setdefault("AGENT_USER_CONCURRENCY", "1")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


async def main() -> None:
    with tempfile.NamedTemporaryFile(prefix="adapter-performance-", suffix=".db") as db_file:
        os.environ["COURSE_DB"] = db_file.name
        import sys

        sys.path.insert(0, str(ROOT / "agent-adapter"))
        import httpx
        from app.main import app

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            async def request(index: int) -> tuple[float, int, str]:
                user = f"performance-user-{index % 3}"
                started = time.perf_counter()
                response = await client.post(
                    "/api/course-agent/chat",
                    headers={"x-dev-role": "student", "x-dev-user": user},
                    json={"question": f"固定性能问题 {index}", "mode": "qa"},
                )
                elapsed = time.perf_counter() - started
                return elapsed, response.status_code, response.text

            # Three users make ten requests each, matching the plan's small
            # concurrency scenario while respecting the per-user limiter.
            results = await asyncio.gather(*(request(index) for index in range(30)))

        assert all(status == 200 and "event: done" in body for _, status, body in results)
        timings = sorted(elapsed for elapsed, _, _ in results)
        p50 = statistics.median(timings)
        p95 = timings[max(0, int(len(timings) * 0.95) - 1)]
        print(f"PERFORMANCE_MOCK_OK samples={len(timings)} p50_ms={p50 * 1000:.2f} p95_ms={p95 * 1000:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
