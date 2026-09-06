#!/usr/bin/env python3
"""Exercise user-scoped resource favorites and page notes."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]
os.environ["MOCK_AUTH_MODE"] = "true"
os.environ["MOCK_WORKFLOW_MODE"] = "true"
os.environ["AGENT_UID_SALT"] = "resource-annotations-fixture-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")


def data(response: object) -> dict:
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-annotations-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        import httpx
        from app.main import Identity, app

        transport = httpx.ASGITransport(app=app)
        client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
        student = {"x-dev-role": "student", "x-dev-user": "annotations-student"}
        other_student = {"x-dev-role": "student", "x-dev-user": "annotations-other"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "annotations-teacher"}
        resource = data(await client.get("/api/textbook/resources?chapter_id=3", headers=student))["items"][0]
        resource_id = resource["id"]
        note_page = max(1, int(resource.get("page_start") or 1))

        initial = data(await client.get(f"/api/student/resources/{resource_id}/annotations", headers=student))
        assert initial == {"resource_id": resource_id, "favorite": False, "notes": []}
        assert (await client.get(f"/api/student/resources/{resource_id}/annotations", headers=teacher)).status_code == 403

        favorite_body = {"favorite": True}
        favorite_headers = {**student, "idempotency-key": "annotation-favorite"}
        first_favorite = data(await client.put(f"/api/student/resources/{resource_id}/favorite", headers=favorite_headers, json=favorite_body))
        assert first_favorite["favorite"] is True
        assert data(await client.put(f"/api/student/resources/{resource_id}/favorite", headers=favorite_headers, json=favorite_body))["favorite"] is True
        assert data(await client.get(f"/api/student/resources/{resource_id}/annotations", headers=other_student))["favorite"] is False
        assert (await client.put(f"/api/student/resources/{resource_id}/favorite", headers={**favorite_headers, "idempotency-key": "annotation-favorite"}, json={"favorite": False})).status_code == 409

        note_body = {"text": "重点：并网控制的功率平衡", "base_version": 0}
        note_headers = {**student, "idempotency-key": "annotation-note"}
        saved = data(await client.put(f"/api/student/resources/{resource_id}/notes/{note_page}", headers=note_headers, json=note_body))
        assert saved["version"] == 1
        assert data(await client.put(f"/api/student/resources/{resource_id}/notes/{note_page}", headers=note_headers, json=note_body))["version"] == 1
        assert (await client.put(f"/api/student/resources/{resource_id}/notes/{note_page}", headers={**student, "idempotency-key": "annotation-note-stale"}, json={"text": "过期", "base_version": 0})).status_code == 409
        assert data(await client.get(f"/api/student/resources/{resource_id}/annotations", headers=student))["notes"][0]["text"] == "重点：并网控制的功率平衡"
        assert data(await client.get(f"/api/student/resources/{resource_id}/annotations", headers=other_student))["notes"] == []
        deleted = data(await client.request("DELETE", f"/api/student/resources/{resource_id}/notes/{note_page}", headers={**student, "idempotency-key": "annotation-note-delete"}, json={"base_version": 1}))
        assert deleted["deleted"] is True and deleted["version"] == 2
        assert data(await client.get(f"/api/student/resources/{resource_id}/annotations", headers=student))["notes"] == []
        assert (await client.put(f"/api/student/resources/{resource_id}/notes/{note_page}", headers={**teacher, "idempotency-key": "teacher-note"}, json=note_body)).status_code == 403
        assert (await client.put(f"/api/student/resources/{resource_id}/notes/{note_page}", headers={"idempotency-key": "mock-note"}, json=note_body)).status_code == 200
        assert (await client.put(f"/api/student/resources/{resource_id}/notes/0", headers={**student, "idempotency-key": "invalid-note"}, json=note_body)).status_code == 422

        secure_identity = Identity("u_secure_annotations", "student", 1, "sesskey-annotations")
        with patch.dict(os.environ, {"MOCK_AUTH_MODE": "false"}, clear=False):
            with patch("app.main.resolve_identity", new=AsyncMock(return_value=secure_identity)):
                secure_headers = {"idempotency-key": "secure-favorite"}
                assert (await client.put(f"/api/student/resources/{resource_id}/favorite", headers=secure_headers, json={"favorite": True})).status_code == 403
                assert (await client.put(f"/api/student/resources/{resource_id}/favorite", headers={**secure_headers, "X-Moodle-Sesskey": "sesskey-annotations"}, json={"favorite": True})).status_code == 200
        await client.aclose()

    print("RESOURCE_ANNOTATIONS_API_OK")


if __name__ == "__main__":
    asyncio.run(main())
