#!/usr/bin/env python3
"""Verify reader progress, favorites and notes stay within the session course."""

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
    with tempfile.TemporaryDirectory(prefix="resource-course-scope-") as directory:
        os.environ.update({
            "COURSE_DB": str(Path(directory) / "course.db"),
            "COURSE_MANIFEST": str(ROOT / "course-data/normalized/manifest.json"),
            "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
            "MOCK_AUTH_MODE": "true",
            "MOCK_WORKFLOW_MODE": "true",
            "AGENT_UID_SALT": "resource-course-scope-test-only",
            "COURSE_ID": "2",
            "MOCK_COURSE_ID": "2",
        })
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, store

        with store.connect() as db:
            db.execute("INSERT INTO chapters(id,name,sort_order,course_id) VALUES(?,?,?,?)", (301, "课程二阅读章节", 301, 2))
            db.execute(
                "INSERT INTO resources(id,chapter_id,node_id,source_file,normalized_file,page_start,page_end,sha256,version,title,source_reference,status,revision) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("res-course-2-reader", 301, None, "course-2-reader.pdf", "course-2-reader.pdf", 1, 3, "scope-resource", "scope-v1", "课程二阅读资料", "scope", "published", 0),
            )

        student = {"x-dev-role": "student", "x-dev-user": "resource-scope-student"}
        resource_id = "res-course-2-reader"
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            progress = data(await client.get(f"/api/student/resources/{resource_id}/progress", headers=student), 200)
            assert progress["resource"]["id"] == resource_id and progress["progress"]["version"] == 0
            saved = data(
                await client.put(
                    f"/api/student/resources/{resource_id}/progress",
                    headers={**student, "Idempotency-Key": "scope-progress"},
                    json={"page": 2, "percent": 50, "completed": False, "base_version": 0},
                ),
                200,
            )
            assert saved["version"] == 1
            favorite = data(
                await client.put(
                    f"/api/student/resources/{resource_id}/favorite",
                    headers={**student, "Idempotency-Key": "scope-favorite"},
                    json={"favorite": True},
                ),
                200,
            )
            assert favorite["favorite"] is True
            note = data(
                await client.put(
                    f"/api/student/resources/{resource_id}/notes/2",
                    headers={**student, "Idempotency-Key": "scope-note"},
                    json={"text": "课程二重点", "base_version": 0},
                ),
                200,
            )
            assert note["text"] == "课程二重点"
            assert data(await client.get("/api/student/resources/favorites", headers=student), 200)["items"][0]["id"] == resource_id

            os.environ["COURSE_ID"] = "1"
            os.environ["MOCK_COURSE_ID"] = "1"
            assert (await client.get(f"/api/student/resources/{resource_id}/progress", headers=student)).status_code == 404
            assert data(await client.get("/api/student/resources/favorites", headers=student), 200)["items"] == []
            assert (await client.put(
                f"/api/student/resources/{resource_id}/favorite",
                headers={**student, "Idempotency-Key": "scope-cross-course-favorite"},
                json={"favorite": False},
            )).status_code == 404

    for name in ("COURSE_DB", "COURSE_MANIFEST", "GRAPH_BASELINE", "MOCK_AUTH_MODE", "MOCK_WORKFLOW_MODE", "AGENT_UID_SALT", "COURSE_ID", "MOCK_COURSE_ID"):
        os.environ.pop(name, None)
    print("RESOURCE_COURSE_SCOPE_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
