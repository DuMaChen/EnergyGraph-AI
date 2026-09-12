#!/usr/bin/env python3
"""Exercise BUILD-090 Agent context ownership and role boundaries locally."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, AsyncIterator

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "agent-context-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


async def main() -> None:
    with tempfile.NamedTemporaryFile(prefix="agent-context-", suffix=".db") as db_file:
        os.environ["COURSE_DB"] = db_file.name
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app import main as adapter  # noqa: E402

        captured: list[dict[str, Any]] = []

        async def fixture_stream(parameters: dict[str, Any], _identity: Any, request_id: str, _workflow_id: str | None = None) -> AsyncIterator[dict[str, Any]]:
            captured.append(parameters)
            yield {"event": "token", "data": {"text": "上下文回答", "request_id": request_id}}
            yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}

        adapter.xingchen_stream = fixture_stream
        resource = adapter.store.resources()[0]
        resource_id = str(resource["id"])
        page = int(resource.get("page_start") or 1)

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=adapter.app), base_url="http://test") as client:
            student = {"x-dev-role": "student", "x-dev-user": "agent-context-student"}
            teacher = {"x-dev-role": "teacher", "x-dev-user": "agent-context-teacher"}

            valid = await client.post(
                "/api/course-agent/chat",
                headers=student,
                json={"question": "解释这个资源", "mode": "qa", "resource_id": resource_id, "resource_page": page, "node_ids": ["kp-1"]},
            )
            assert valid.status_code == 200
            assert "event: done" in valid.text
            assert captured[0]["COURSE_ID"] == 1
            assert len(str(captured[0]["AGENT_CONTEXT_HASH"])) == 24
            resource_context = json.loads(str(captured[0]["RESOURCE_CONTEXT"]))
            assert resource_context["resource_id"] == resource_id
            assert resource_context["page"] == page

            invalid_resource = await client.post(
                "/api/course-agent/chat",
                headers=student,
                json={"question": "测试", "mode": "qa", "resource_id": "missing-resource", "resource_page": 1},
            )
            assert invalid_resource.status_code == 404
            invalid_page = await client.post(
                "/api/course-agent/chat",
                headers=student,
                json={"question": "测试", "mode": "qa", "resource_id": resource_id, "resource_page": 999999},
            )
            assert invalid_page.status_code == 422
            student_teacher_mode = await client.post(
                "/api/course-agent/chat",
                headers=student,
                json={"question": "生成备课提纲", "mode": "teacher_assistant"},
            )
            assert student_teacher_mode.status_code == 422
            teacher_mode = await client.post(
                "/api/course-agent/chat",
                headers=teacher,
                json={"question": "生成备课提纲", "mode": "teacher_assistant"},
            )
            assert teacher_mode.status_code == 200

    print("AGENT_CONTEXT_API_OK")


if __name__ == "__main__":
    asyncio.run(main())
