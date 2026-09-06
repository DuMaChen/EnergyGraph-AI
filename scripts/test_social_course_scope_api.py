#!/usr/bin/env python3
"""Verify social and classroom-activity routes stay inside the session course."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]


def data(response: httpx.Response, expected_status: int) -> dict:
    assert response.status_code == expected_status, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="social-course-scope-") as directory:
        os.environ.update({
            "COURSE_DB": str(Path(directory) / "course.db"),
            "COURSE_MANIFEST": str(ROOT / "course-data/normalized/manifest.json"),
            "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
            "MOCK_AUTH_MODE": "true",
            "MOCK_WORKFLOW_MODE": "true",
            "AGENT_UID_SALT": "social-course-scope-test-only",
            "COURSE_ID": "2",
            "MOCK_COURSE_ID": "2",
        })
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        teacher = {"x-dev-role": "teacher", "x-dev-user": "social-scope-teacher"}
        student = {"x-dev-role": "student", "x-dev-user": "social-scope-student"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            topic = data(
                await client.post(
                    "/api/discussions",
                    headers={**student, "Idempotency-Key": "scope-topic"},
                    json={"title": "课程二讨论", "body": "课程二内容"},
                ),
                201,
            )
            notice = data(
                await client.post(
                    "/api/teacher/notifications",
                    headers={**teacher, "Idempotency-Key": "scope-notice"},
                    json={"title": "课程二公告", "body": "仅课程二可见", "audience": "course_all"},
                ),
                201,
            )
            activity = data(
                await client.post(
                    "/api/teacher/activities",
                    headers={**teacher, "Idempotency-Key": "scope-activity"},
                    json={
                        "kind": "poll",
                        "title": "课程二活动",
                        "body": "请选择",
                        "options": [{"id": "a", "label": "选项 A"}, {"id": "b", "label": "选项 B"}],
                        "status": "published",
                    },
                ),
                201,
            )
            assert data(await client.get("/api/discussions", headers=student), 200)["items"][0]["id"] == topic["id"]
            assert {item["id"] for item in data(await client.get("/api/notifications", headers=student), 200)["items"]} == {notice["id"]}
            assert [item["id"] for item in data(await client.get("/api/activities", headers=student), 200)["items"]] == [activity["id"]]

            os.environ["COURSE_ID"] = "1"
            os.environ["MOCK_COURSE_ID"] = "1"
            assert (await client.get(f"/api/discussions/{topic['id']}", headers=student)).status_code == 404
            assert (await client.get(f"/api/activities/{activity['id']}", headers=student)).status_code == 404
            assert data(await client.get("/api/notifications", headers=student), 200)["items"] == []

    for name in ("COURSE_DB", "COURSE_MANIFEST", "GRAPH_BASELINE", "MOCK_AUTH_MODE", "MOCK_WORKFLOW_MODE", "AGENT_UID_SALT", "COURSE_ID", "MOCK_COURSE_ID"):
        os.environ.pop(name, None)
    print("SOCIAL_COURSE_SCOPE_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
