#!/usr/bin/env python3
"""Verify the redacted administrator user/course directory contract."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]


def body(response: httpx.Response, expected_status: int) -> dict:
    assert response.status_code == expected_status, response.text
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


def assert_redacted(response: httpx.Response) -> None:
    serialized = json.dumps(response.json(), ensure_ascii=False).casefold()
    for secret_field in ("email", "password", "secret", "cookie", "authorization", "bridge_token"):
        assert secret_field not in serialized, (secret_field, response.text)


async def run() -> None:
    manifest_path = ROOT / "course-data/normalized/manifest.json"
    fixture = {
        "users": [
            {"id": "student-c1", "display_name": "课程一学生", "role": "student", "course_id": 1, "status": "active", "email": "student-c1@example.test", "secret": "do-not-return"},
            {"id": "teacher-c1", "display_name": "课程一教师", "role": "teacher", "course_id": 1, "status": "active", "cookie": "do-not-return"},
            {"id": "admin-c1", "display_name": "课程一管理员", "role": "admin", "course_id": 1, "status": "active", "authorization": "do-not-return"},
            {"id": "student-c2", "display_name": "课程二学生", "role": "student", "course_id": 2, "status": "suspended", "email": "student-c2@example.test"},
            {"id": "teacher-c2", "display_name": "课程二教师", "role": "teacher", "course_id": 2, "status": "active"},
        ],
        "courses": [
            {"id": 1, "name": "课程一", "teacher": "课程一教师", "class_name": "课程一班", "enrollment_count": 3},
            {"id": 2, "name": "课程二", "teacher": "课程二教师", "class_name": "课程二班", "enrollment_count": 2},
        ],
    }

    with tempfile.TemporaryDirectory(prefix="admin-directory-") as directory:
        os.environ.update({
            "COURSE_DB": str(Path(directory) / "course.db"),
            "COURSE_MANIFEST": str(manifest_path),
            "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
            "MOCK_AUTH_MODE": "true",
            "MOCK_COURSE_ID": "1",
            "COURSE_ID": "1",
            "AGENT_UID_SALT": "admin-directory-test-only",
            "MOCK_ADMIN_DIRECTORY_JSON": json.dumps(fixture, ensure_ascii=False),
        })
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        admin = {"x-dev-role": "admin", "x-dev-user": "admin-directory-admin"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "admin-directory-teacher"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            forbidden = await client.get("/api/admin/users", headers=teacher)
            assert forbidden.status_code == 403, forbidden.text

            users_c1_response = await client.get("/api/admin/users", headers=admin)
            users_c1 = body(users_c1_response, 200)
            assert_redacted(users_c1_response)
            assert users_c1["source"] == "mock_fixture" and users_c1["configured"] is True
            assert users_c1["total"] == 3
            assert {item["id"] for item in users_c1["items"]} == {"student-c1", "teacher-c1", "admin-c1"}
            assert all(item["course_id"] == 1 for item in users_c1["items"])

            teacher_rows = body(await client.get("/api/admin/users?role=teacher", headers=admin), 200)
            assert [item["id"] for item in teacher_rows["items"]] == ["teacher-c1"]
            search_rows = body(await client.get("/api/admin/users?query=课程一学生", headers=admin), 200)
            assert [item["id"] for item in search_rows["items"]] == ["student-c1"]
            page_two = body(await client.get("/api/admin/users?page=2&page_size=1", headers=admin), 200)
            assert page_two["page"] == 2 and page_two["page_size"] == 1 and len(page_two["items"]) == 1
            invalid_role = await client.get("/api/admin/users?role=owner", headers=admin)
            assert invalid_role.status_code == 422
            assert invalid_role.json()["error"]["code"] == "invalid_input"

            course_c1_response = await client.get("/api/admin/courses", headers=admin)
            courses_c1 = body(course_c1_response, 200)
            assert_redacted(course_c1_response)
            assert courses_c1["total"] == 1
            assert courses_c1["items"][0]["id"] == 1
            assert courses_c1["items"][0]["name"] == "课程一"

            os.environ["MOCK_COURSE_ID"] = "2"
            os.environ["COURSE_ID"] = "2"
            users_c2_response = await client.get("/api/admin/users", headers=admin)
            users_c2 = body(users_c2_response, 200)
            assert_redacted(users_c2_response)
            assert {item["id"] for item in users_c2["items"]} == {"student-c2", "teacher-c2"}
            assert all(item["course_id"] == 2 for item in users_c2["items"])
            courses_c2 = body(await client.get("/api/admin/courses?query=课程二", headers=admin), 200)
            assert courses_c2["total"] == 1 and courses_c2["items"][0]["id"] == 2

            os.environ.pop("MOCK_ADMIN_DIRECTORY_JSON")
            os.environ["MOCK_COURSE_ID"] = "1"
            os.environ["COURSE_ID"] = "1"
            unconfigured_response = await client.get("/api/admin/users", headers=admin)
            unconfigured = body(unconfigured_response, 200)
            assert unconfigured["configured"] is False
            assert unconfigured["source"] == "not_configured"
            assert unconfigured["items"] == []
            assert "尚未配置" in str(unconfigured["message"])

            configured_courses = body(await client.get("/api/admin/courses", headers=admin), 200)
            assert configured_courses["total"] == 1
            assert configured_courses["items"][0]["id"] == 1

    for name in (
        "COURSE_DB", "COURSE_MANIFEST", "GRAPH_BASELINE", "MOCK_AUTH_MODE",
        "MOCK_COURSE_ID", "COURSE_ID", "AGENT_UID_SALT", "MOCK_ADMIN_DIRECTORY_JSON",
    ):
        os.environ.pop(name, None)
    print("ADMIN_DIRECTORY_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
