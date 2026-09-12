#!/usr/bin/env python3
"""STAFF-010 isolated acceptance for teacher resource editing."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "teacher-resource-api-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def payload(response: httpx.Response, expected: int) -> dict:
    assert response.status_code == expected, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


def error_code(response: httpx.Response, expected: int) -> str:
    assert response.status_code == expected, response.text
    return str(response.json()["error"]["code"])


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="teacher-resource-api-") as directory:
        root = Path(directory)
        os.environ["COURSE_DB"] = str(root / "course.db")
        os.environ["RESOURCE_STORAGE_DIR"] = str(root / "resource-files")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, store

        teacher = {"x-dev-role": "teacher", "x-dev-user": "staff010-teacher"}
        student = {"x-dev-role": "student", "x-dev-user": "staff010-student"}
        outsider = {"x-dev-role": "student", "x-dev-user": "staff010-outsider"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/teacher/resources", headers=student)).status_code == 403
            assert error_code(await client.post("/api/teacher/resources", headers={**student, "Idempotency-Key": "student-create"}, json={"title": "越权", "chapter_id": 3}), 403) == "forbidden"

            metadata = {"title": "教师上传验收资料", "chapter_id": 3, "node_id": "kp-3-1", "source_reference": "教师补充来源"}
            resource = payload(await client.post("/api/teacher/resources", headers={**teacher, "Idempotency-Key": "staff010-create"}, json=metadata), 201)
            replay = payload(await client.post("/api/teacher/resources", headers={**teacher, "Idempotency-Key": "staff010-create"}, json=metadata), 200)
            assert replay["id"] == resource["id"] and resource["status"] == "draft" and resource["revision"] == 0
            resource_id = resource["id"]

            assert error_code(await client.post(f"/api/teacher/resources/{resource_id}/publish", headers={**teacher, "Idempotency-Key": "staff010-publish-empty"}, json={}), 409) == "conflict"
            assert error_code(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=../escape.md", headers={**teacher, "Idempotency-Key": "staff010-traversal"}, content=b"safe text"), 422) == "invalid_file"
            assert error_code(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=unsafe.txt", headers={**teacher, "Idempotency-Key": "staff010-type"}, content=b"safe text"), 422) == "invalid_file"
            assert error_code(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=bad.pdf", headers={**teacher, "Idempotency-Key": "staff010-fake-pdf"}, content=b"not a pdf"), 422) == "invalid_file"
            oversized = b"x" * (20 * 1024 * 1024 + 1)
            oversized_response = await client.put(f"/api/teacher/resources/{resource_id}/file?filename=large.md", headers={**teacher, "Idempotency-Key": "staff010-large"}, content=oversized)
            assert oversized_response.status_code in {413, 422}, oversized_response.text

            first_content = b"# STAFF-010\nTeacher-owned resource.\n"
            first = payload(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=staff010.md", headers={**teacher, "Idempotency-Key": "staff010-upload-1"}, content=first_content), 201)
            assert first["revision"] == 1 and first["status"] == "draft" and first["revisions"][0]["size_bytes"] == len(first_content)
            assert "storage_path" not in first and all("storage_path" not in item for item in first["revisions"])
            stored = list((root / "resource-files" / resource_id).glob("1-staff010.md"))
            assert len(stored) == 1 and stored[0].read_bytes() == first_content

            duplicate = payload(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=renamed.md", headers={**teacher, "Idempotency-Key": "staff010-upload-duplicate"}, content=first_content), 200)
            assert duplicate["deduplicated"] is True and duplicate["revision"] == 1
            assert not list((root / "resource-files" / resource_id).glob("2-*"))

            published = payload(await client.post(f"/api/teacher/resources/{resource_id}/publish", headers={**teacher, "Idempotency-Key": "staff010-publish-1"}, json={}), 200)
            assert published["status"] == "published"
            student_resources = payload(await client.get("/api/textbook/resources", headers=student), 200)
            assert any(item["id"] == resource_id for item in student_resources["items"])
            assert payload(await client.get(f"/api/textbook/resources/{resource_id}", headers=student), 200)["resource"]["status"] == "published"

            second_content = b"# STAFF-010 v2\nReplacement revision.\n"
            replaced = payload(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=staff010-v2.md", headers={**teacher, "Idempotency-Key": "staff010-upload-2"}, content=second_content), 201)
            assert replaced["revision"] == 2 and replaced["status"] == "draft"
            revisions = {item["revision"]: item for item in replaced["revisions"]}
            assert revisions[1]["status"] == "superseded" and revisions[2]["status"] == "active"
            student_after_replace = payload(await client.get("/api/textbook/resources", headers=student), 200)
            assert all(item["id"] != resource_id for item in student_after_replace["items"])

            republished = payload(await client.post(f"/api/teacher/resources/{resource_id}/publish", headers={**teacher, "Idempotency-Key": "staff010-publish-2"}, json={}), 200)
            assert republished["status"] == "published" and republished["revision"] == 2
            archived = payload(await client.post(f"/api/teacher/resources/{resource_id}/archive", headers={**teacher, "Idempotency-Key": "staff010-archive"}, json={}), 200)
            assert archived["status"] == "archived"
            assert all(item["id"] != resource_id for item in payload(await client.get("/api/textbook/resources", headers=student), 200)["items"])
            assert (await client.get(f"/api/textbook/resources/{resource_id}", headers=student)).status_code == 404
            assert (await client.get(f"/api/student/resources/{resource_id}/progress", headers=student)).status_code == 404
            assert error_code(await client.put(f"/api/teacher/resources/{resource_id}/file?filename=blocked.md", headers={**teacher, "Idempotency-Key": "staff010-upload-archived"}, content=b"blocked"), 409) == "conflict"

            audit_actions = {item["action"] for item in store.audit_logs(resource_id)}
            assert {"resource.create", "resource.upload", "resource.replace", "resource.publish", "resource.archive"} <= audit_actions
            teacher_list = payload(await client.get("/api/teacher/resources?status=archived", headers=teacher), 200)
            assert any(item["id"] == resource_id and item["status"] == "archived" for item in teacher_list["items"])
            assert all("storage_path" not in item for item in teacher_list["items"])

    print("TEACHER_RESOURCE_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
