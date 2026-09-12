#!/usr/bin/env python3
"""Exercise the student favorite-resource list contract."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["MOCK_AUTH_MODE"] = "true"
os.environ["MOCK_WORKFLOW_MODE"] = "true"
os.environ["AGENT_UID_SALT"] = "resource-favorites-fixture-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")


def data(response: object) -> dict:
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-favorites-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        import httpx

        from app.main import app

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            student = {"x-dev-role": "student", "x-dev-user": "favorites-student"}
            other_student = {"x-dev-role": "student", "x-dev-user": "favorites-other"}
            teacher = {"x-dev-role": "teacher", "x-dev-user": "favorites-teacher"}
            resources = data(await client.get("/api/textbook/resources", headers=student))["items"]
            resource_id = resources[0]["id"]

            assert data(await client.get("/api/student/resources/favorites", headers=student)) == {"items": [], "page": 1, "page_size": 20, "total": 0}
            assert (await client.get("/api/student/resources/favorites", headers=teacher)).status_code == 403
            assert (await client.get("/api/student/resources/favorites?page=0", headers=student)).status_code == 422

            favorite_headers = {**student, "idempotency-key": "favorites-write"}
            assert (await client.put(f"/api/student/resources/{resource_id}/favorite", headers=favorite_headers, json={"favorite": True})).status_code == 200
            note_headers = {**student, "idempotency-key": "favorites-note"}
            assert (await client.put(f"/api/student/resources/{resource_id}/notes/2", headers=note_headers, json={"text": "收藏页笔记", "base_version": 0})).status_code == 200

            listed = data(await client.get("/api/student/resources/favorites?page_size=1", headers=student))
            assert listed["total"] == 1 and listed["page_size"] == 1
            assert listed["items"][0]["id"] == resource_id
            assert listed["items"][0]["note_count"] == 1
            assert listed["items"][0]["favorite_at"]
            assert data(await client.get("/api/student/resources/favorites", headers=other_student))["items"] == []

            unfavorite_headers = {**student, "idempotency-key": "favorites-remove"}
            assert (await client.put(f"/api/student/resources/{resource_id}/favorite", headers=unfavorite_headers, json={"favorite": False})).status_code == 200
            assert data(await client.get("/api/student/resources/favorites", headers=student))["items"] == []

    print("RESOURCE_FAVORITES_API_OK")


if __name__ == "__main__":
    asyncio.run(main())
