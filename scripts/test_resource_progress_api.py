#!/usr/bin/env python3
"""Exercise the student resource-progress API with isolated course state."""

from __future__ import annotations

import os
import sys
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch


ROOT = Path(__file__).resolve().parents[1]
os.environ["MOCK_AUTH_MODE"] = "true"
os.environ["MOCK_WORKFLOW_MODE"] = "true"
os.environ["AGENT_UID_SALT"] = "resource-progress-fixture-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")


def expected_mount_state(normalized_file: str) -> tuple[bool, str]:
    """Derive availability from the manifest-mounted artifact, not a fixture assumption."""
    manifest_path = Path(os.environ["COURSE_MANIFEST"]).resolve()
    if (manifest_path.parent / normalized_file).is_file():
        return True, "ready"
    return False, "pending_mount"


def data(response: object) -> dict:
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="resource-progress-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        import httpx
        from app.main import Identity, app, stable_uid, store

        transport = httpx.ASGITransport(app=app)
        client = httpx.AsyncClient(transport=transport, base_url="http://testserver")
        student = {"x-dev-role": "student", "x-dev-user": "progress-student"}
        other_student = {"x-dev-role": "student", "x-dev-user": "progress-other"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "progress-teacher"}

        resources = data(await client.get("/api/textbook/resources?chapter_id=3", headers=student))
        assert resources["items"], resources
        resource = resources["items"][0]
        resource_id = resource["id"]
        expected_available, expected_mount_status = expected_mount_state(resource["normalized_file"])
        assert resource["available"] is expected_available
        assert resource["mount_status"] == expected_mount_status

        empty_position = data(await client.get("/api/student/learning-position", headers=student))
        assert empty_position["position"] is None
        assert (await client.get("/api/student/learning-position", headers=teacher)).status_code == 403

        with store.connect() as db:
            db.execute(
                "INSERT INTO resource_progress(user_uid,resource_id,page,percent,completed,version,updated_at) VALUES(?,?,?,?,?,?,?)",
                (stable_uid("progress-other"), resource_id, 3, 60, 0, 1, "2098-01-01 00:00:00"),
            )
        assert data(await client.get("/api/student/learning-position", headers=student))["position"] is None
        other_position = data(await client.get("/api/student/learning-position", headers=other_student))["position"]
        assert other_position["resource"]["id"] == resource_id
        assert other_position["progress"]["page"] == 3
        with store.connect() as db:
            db.execute(
                "DELETE FROM resource_progress WHERE user_uid=? AND resource_id=?",
                (stable_uid("progress-other"), resource_id),
            )

        initial = data(await client.get(f"/api/student/resources/{resource_id}/progress", headers=student))
        assert initial["progress"]["version"] == 0
        assert initial["progress"]["percent"] == 0
        assert (await client.get(f"/api/student/resources/{resource_id}/progress", headers=teacher)).status_code == 403
        assert (await client.put(
            f"/api/student/resources/{resource_id}/progress",
            headers=student,
            json={"page": 2, "percent": 50, "completed": False, "base_version": 0},
        )).status_code == 422

        body = {"page": 2, "percent": 50, "completed": False, "base_version": 0}
        first = await client.put(
            f"/api/student/resources/{resource_id}/progress",
            headers={**student, "idempotency-key": "resource-progress-first"},
            json=body,
        )
        saved = data(first)
        assert saved["version"] == 1
        saved_position = data(await client.get("/api/student/learning-position", headers=student))["position"]
        assert saved_position["course_id"] == 1
        assert saved_position["resource"]["id"] == resource_id
        assert saved_position["resource"]["status"] == "published"
        assert saved_position["resource"]["available"] is expected_available
        assert saved_position["resource"]["mount_status"] == expected_mount_status
        assert saved_position["progress"]["page"] == 2
        assert saved_position["progress"]["has_saved_progress"] is True
        repeated = data(await client.put(
            f"/api/student/resources/{resource_id}/progress",
            headers={**student, "idempotency-key": "resource-progress-first"},
            json=body,
        ))
        assert repeated["version"] == 1
        reused = await client.put(
            f"/api/student/resources/{resource_id}/progress",
            headers={**student, "idempotency-key": "resource-progress-first"},
            json={**body, "page": 3},
        )
        assert reused.status_code == 409
        stale = await client.put(
            f"/api/student/resources/{resource_id}/progress",
            headers={**student, "idempotency-key": "resource-progress-stale"},
            json={**body, "page": 3},
        )
        assert stale.status_code == 409
        assert data(await client.get(f"/api/student/resources/{resource_id}/progress", headers=student))["progress"]["version"] == 1
        assert data(await client.get(f"/api/student/resources/{resource_id}/progress", headers=other_student))["progress"]["version"] == 0
        assert (await client.put(
            f"/api/student/resources/{resource_id}/progress",
            headers={**teacher, "idempotency-key": "teacher-progress"},
            json=body,
        )).status_code == 403
        assert (await client.get("/api/student/resources/unknown-resource/progress", headers=student)).status_code == 404

        with store.connect() as db:
            db.execute(
                "UPDATE resource_progress SET updated_at=? WHERE user_uid=? AND resource_id=?",
                ("2097-01-01 00:00:00", stable_uid("progress-student"), resource_id),
            )
            db.execute("INSERT INTO chapters(id,name,sort_order,course_id) VALUES(?,?,?,?)", (301, "课程二", 301, 2))
            resources_to_insert = [
                ("res-recent-a", 3, "recent-a.pdf", "published"),
                ("res-recent-b", 3, "recent-b.pdf", "published"),
                ("res-recent-archived", 3, "recent-archived.pdf", "archived"),
                ("res-recent-draft", 3, "recent-draft.pdf", "draft"),
                ("res-recent-invalid-page", 3, "recent-invalid-page.pdf", "published"),
                ("res-recent-course-two", 301, "recent-course-two.pdf", "published"),
            ]
            db.executemany(
                "INSERT INTO resources(id,chapter_id,source_file,normalized_file,page_start,page_end,version,title,status) VALUES(?,?,?,?,?,?,?,?,?)",
                [(item_id, chapter_id, filename, filename, 1, 10, "test-v1", filename, status) for item_id, chapter_id, filename, status in resources_to_insert],
            )
            student_uid = stable_uid("progress-student")
            progress_to_insert = [
                (student_uid, "res-recent-a", 4, 40, 0, 2, "2099-01-01 00:00:00"),
                (student_uid, "res-recent-b", 5, 50, 0, 3, "2099-01-01 00:00:00"),
                (student_uid, "res-recent-archived", 6, 60, 0, 4, "2099-03-01 00:00:00"),
                (student_uid, "res-recent-draft", 7, 70, 0, 5, "2099-04-01 00:00:00"),
                (student_uid, "res-recent-invalid-page", 11, 90, 0, 6, "2099-04-02 00:00:00"),
                (student_uid, "res-recent-course-two", 8, 80, 0, 6, "2099-05-01 00:00:00"),
            ]
            db.executemany(
                "INSERT INTO resource_progress(user_uid,resource_id,page,percent,completed,version,updated_at) VALUES(?,?,?,?,?,?,?)",
                progress_to_insert,
            )

        position = data(await client.get("/api/student/learning-position", headers=student))["position"]
        assert position["course_id"] == 1
        assert position["resource"]["id"] == "res-recent-a"
        assert position["resource"]["status"] == "published"
        recent_available, recent_mount_status = expected_mount_state("recent-a.pdf")
        assert position["resource"]["available"] is recent_available
        assert position["resource"]["mount_status"] == recent_mount_status
        assert "storage_path" not in position["resource"]
        assert position["progress"] == {
            "resource_id": "res-recent-a",
            "page": 4,
            "percent": 40.0,
            "completed": False,
            "version": 2,
            "updated_at": "2099-01-01 00:00:00",
            "has_saved_progress": True,
        }

        os.environ["COURSE_ID"] = "2"
        os.environ["MOCK_COURSE_ID"] = "2"
        course_two_position = data(await client.get("/api/student/learning-position", headers=student))["position"]
        assert course_two_position["course_id"] == 2
        assert course_two_position["resource"]["id"] == "res-recent-course-two"
        os.environ["COURSE_ID"] = "1"
        os.environ["MOCK_COURSE_ID"] = "1"

        secure_identity = Identity("u_secure_progress", "student", 1, "sesskey-fixture")
        with patch.dict(os.environ, {"MOCK_AUTH_MODE": "false"}, clear=False):
            with patch("app.main.resolve_identity", new=AsyncMock(return_value=secure_identity)):
                secure_headers = {"x-request-id": "progress-csrf-test", "idempotency-key": "resource-progress-csrf"}
                assert (await client.put(
                    f"/api/student/resources/{resource_id}/progress", headers=secure_headers, json=body
                )).status_code == 403
                assert (await client.put(
                    f"/api/student/resources/{resource_id}/progress", headers={**secure_headers, "X-Moodle-Sesskey": "wrong"}, json=body
                )).status_code == 403
                assert (await client.put(
                    f"/api/student/resources/{resource_id}/progress", headers={**secure_headers, "X-Moodle-Sesskey": "sesskey-fixture"}, json=body
                )).status_code == 200
        await client.aclose()

    print("RESOURCE_PROGRESS_API_OK")


if __name__ == "__main__":
    asyncio.run(main())
