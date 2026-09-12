#!/usr/bin/env python3
"""Exercise the local COURSE-001..008 course-list contract."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
os.environ["MOCK_AUTH_MODE"] = "true"
os.environ["MOCK_WORKFLOW_MODE"] = "true"
os.environ["AGENT_UID_SALT"] = "course-list-fixture-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")
os.environ["COURSE_ID"] = "1"

sys.path.insert(0, str(ROOT / "agent-adapter"))
sys.path.insert(0, str(ROOT / "scripts"))

from asgi_sync_client import SyncASGIClient


def payload(response: object) -> dict:
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="course-list-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        from app.main import app

        client = SyncASGIClient(app)
        os.environ["MOCK_AUTH_MODE"] = "false"
        try:
            assert client.get("/api/courses").status_code == 401
        finally:
            os.environ["MOCK_AUTH_MODE"] = "true"

        student = {"x-dev-role": "student", "x-dev-user": "course-list-student"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "course-list-teacher"}
        admin = {"x-dev-role": "admin", "x-dev-user": "course-list-admin"}

        listing = client.get("/api/courses?sort=name&page=1&page_size=20", headers=student)
        assert listing.status_code == 200
        data = payload(listing)
        assert data["page"] == 1 and data["page_size"] == 20 and data["total"] == 1
        assert len(data["items"]) == 1
        course = data["items"][0]
        assert {"id", "name", "teacher", "class_name", "status", "progress", "chapter_count", "resource_count", "last_accessed_at"} <= set(course)
        assert course["id"] == 1 and course["chapter_count"] == 6 and course["resource_count"] == 20

        for role_headers in (teacher, admin):
            role_listing = client.get("/api/courses?sort=id", headers=role_headers)
            assert role_listing.status_code == 200
            assert payload(role_listing)["items"][0]["id"] == 1

        detail = client.get("/api/courses/1", headers=student)
        assert detail.status_code == 200
        assert len(payload(detail)["chapters"]) == 6

        assert client.get("/api/courses/999", headers=student).status_code == 404

        with patch("app.main.configured_course_summary", return_value=None):
            empty = client.get("/api/courses", headers=student)
            assert empty.status_code == 200
            assert payload(empty) == {"items": [], "total": 0, "page": 1, "page_size": 20}

        assert client.get("/api/courses?sort=name%20DESC", headers=student).status_code == 422
        assert client.get("/api/courses?page=1&page_size=101", headers=student).status_code == 422
        assert client.get("/api/courses?sort=progress", headers=student).status_code == 200
        assert payload(client.get("/api/courses?sort=id&page=1&page_size=20", headers=student)) == payload(listing)

        os.environ["MOCK_COURSE_ID"] = "999"
        try:
            assert client.get("/api/courses", headers=student).status_code == 403
        finally:
            os.environ.pop("MOCK_COURSE_ID", None)

    print("COURSE_LIST_API_OK cases=8 single_configured_course_boundary=explicit")


if __name__ == "__main__":
    main()
