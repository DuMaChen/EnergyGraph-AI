#!/usr/bin/env python3
"""Exercise the current-course, role-aware global-search contract."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.update(
    {
        "MOCK_AUTH_MODE": "true",
        "MOCK_WORKFLOW_MODE": "true",
        "AGENT_UID_SALT": "global-search-fixture-only",
        "COURSE_MANIFEST": str(ROOT / "course-data/normalized/manifest.json"),
        "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
        "COURSE_ID": "1",
        "MOCK_COURSE_ID": "1",
        "COURSE_STATUS": "active",
        "COURSE_NAME": "Unified Course",
    }
)
sys.path.insert(0, str(ROOT / "agent-adapter"))
sys.path.insert(0, str(ROOT / "scripts"))

from asgi_sync_client import SyncASGIClient  # noqa: E402


def data(response: object) -> dict:
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


def seed_search_records(store: object) -> None:
    with store.connect() as db:
        db.execute("INSERT INTO chapters(id,name,sort_order,course_id) VALUES(?,?,?,?)", (7, "Unified Chapter", 7, 1))
        db.execute("INSERT INTO knowledge_nodes(id,chapter_id,name,node_type,category,description) VALUES(?,?,?,?,?,?)", ("kp-unified", 7, "Unified Knowledge", "knowledge_point", "概念", "Unified search knowledge"))
        resources = [
            ("res-unified-published", "Unified Resource", "published"),
            ("res-unified-draft", "Unified Resource Draft", "draft"),
            ("res-unified-archived", "Unified Resource Archived", "archived"),
        ]
        db.executemany(
            "INSERT INTO resources(id,chapter_id,source_file,normalized_file,page_start,page_end,version,title,status) VALUES(?,?,?,?,?,?,?,?,?)",
            [(resource_id, 7, f"{resource_id}.pdf", f"{resource_id}.pdf", 1, 10, "test-v1", title, status) for resource_id, title, status in resources],
        )
        assignments = [
            ("assignment-unified-published", "Unified Assignment", "published"),
            ("assignment-unified-draft", "Unified Assignment Draft", "draft"),
            ("assignment-unified-withdrawn", "Unified Assignment Withdrawn", "withdrawn"),
            ("assignment-unified-archived", "Unified Assignment Archived", "archived"),
        ]
        db.executemany(
            "INSERT INTO assignments(id,course_id,title,question_ids_json,status,created_by) VALUES(?,?,?,?,?,?)",
            [(item_id, 1, title, "[]", status, "teacher-fixture") for item_id, title, status in assignments],
        )
        exams = [
            ("exam-unified-published", "Unified Exam", "published"),
            ("exam-unified-draft", "Unified Exam Draft", "draft"),
            ("exam-unified-withdrawn", "Unified Exam Withdrawn", "withdrawn"),
            ("exam-unified-archived", "Unified Exam Archived", "archived"),
        ]
        db.executemany(
            "INSERT INTO exams(id,course_id,title,question_ids_json,status,open_at,close_at,duration_seconds,allow_attempts,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)",
            [(item_id, 1, title, "[]", status, "2026-01-01T00:00:00+00:00", "2099-01-01T00:00:00+00:00", 3600, 1, "teacher-fixture") for item_id, title, status in exams],
        )
        discussions = [
            ("topic-unified-open", "Unified Discussion", "open"),
            ("topic-unified-solved", "Unified Discussion Solved", "solved"),
            ("topic-unified-closed", "Unified Discussion Closed", "closed"),
            ("topic-unified-pending", "Unified Discussion Pending", "pending_review"),
        ]
        db.executemany(
            "INSERT INTO discussion_topics(id,course_id,author_uid,title,body,status) VALUES(?,?,?,?,?,?)",
            [(topic_id, 1, "student-fixture", title, "Unified discussion body", status) for topic_id, title, status in discussions],
        )
        db.execute("INSERT INTO chapters(id,name,sort_order,course_id) VALUES(?,?,?,?)", (21, "Unified Other Chapter", 21, 2))
        db.execute("INSERT INTO knowledge_nodes(id,chapter_id,name,node_type,category,description) VALUES(?,?,?,?,?,?)", ("kp-unified-other", 21, "Unified Other Knowledge", "knowledge_point", "概念", "Other course"))
        db.execute(
            "INSERT INTO resources(id,chapter_id,source_file,normalized_file,page_start,page_end,version,title,status) VALUES(?,?,?,?,?,?,?,?,?)",
            ("res-unified-other", 21, "other.pdf", "other.pdf", 1, 10, "test-v1", "Unified Other Resource", "published"),
        )
        db.commit()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="global-search-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        from app.main import app, store

        seed_search_records(store)
        client = SyncASGIClient(app)
        student = {"x-dev-role": "student", "x-dev-user": "global-search-student"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "global-search-teacher"}
        admin = {"x-dev-role": "admin", "x-dev-user": "global-search-admin"}

        for invalid_course_id in (0, -1, 1 << 63):
            try:
                store.global_search("Unified", "all", 1, 20, invalid_course_id, "student", "Unified Course", "Teacher", "Class", "active")
            except ValueError:
                continue
            raise AssertionError(f"invalid course id accepted: {invalid_course_id}")

        page_one = data(client.get("/api/search?q=Unified&page=1&page_size=2", headers=student))
        page_two = data(client.get("/api/search?q=Unified&page=2&page_size=2", headers=student))
        page_three = data(client.get("/api/search?q=Unified&page=3&page_size=2", headers=student))
        page_four = data(client.get("/api/search?q=Unified&page=4&page_size=2", headers=student))
        page_five = data(client.get("/api/search?q=Unified&page=5&page_size=2", headers=student))
        complete = data(client.get("/api/search?q=Unified&page=1&page_size=50", headers=student))
        paged_ids = [item["id"] for page in (page_one, page_two, page_three, page_four, page_five) for item in page["items"]]
        assert paged_ids == [item["id"] for item in complete["items"]]
        assert [item["kind"] for item in complete["items"]] == ["course", "chapter", "resource", "assignment", "exam", "discussion", "discussion", "discussion", "knowledge"]
        assert complete["total"] == 9
        assert complete["counts"] == {"course": 1, "chapter": 1, "resource": 1, "assignment": 1, "exam": 1, "discussion": 3, "knowledge": 1}
        assert all(set(item) == {"kind", "id", "title", "summary", "chapter_id"} for item in complete["items"])

        student_ids = {item["id"] for item in complete["items"]}
        assert "res-unified-draft" not in student_ids
        assert "assignment-unified-archived" not in student_ids
        assert "assignment-unified-withdrawn" not in student_ids
        assert "exam-unified-archived" not in student_ids
        assert "exam-unified-withdrawn" not in student_ids
        assert "topic-unified-pending" not in student_ids

        for role_headers in (teacher, admin):
            staff = data(client.get("/api/search?q=Unified&kind=resource&page_size=50", headers=role_headers))
            assert {item["id"] for item in staff["items"]} == {"res-unified-published", "res-unified-draft", "res-unified-archived"}
            for lifecycle_kind, expected_ids in {
                "assignment": {"assignment-unified-published", "assignment-unified-draft", "assignment-unified-withdrawn", "assignment-unified-archived"},
                "exam": {"exam-unified-published", "exam-unified-draft", "exam-unified-withdrawn", "exam-unified-archived"},
                "discussion": {"topic-unified-open", "topic-unified-solved", "topic-unified-closed", "topic-unified-pending"},
            }.items():
                lifecycle = data(client.get(f"/api/search?q=Unified&kind={lifecycle_kind}&page_size=2", headers=role_headers))
                lifecycle_page_two = data(client.get(f"/api/search?q=Unified&kind={lifecycle_kind}&page=2&page_size=2", headers=role_headers))
                lifecycle_complete = data(client.get(f"/api/search?q=Unified&kind={lifecycle_kind}&page_size=50", headers=role_headers))
                assert {item["id"] for item in lifecycle_complete["items"]} == expected_ids
                assert [item["id"] for item in lifecycle["items"] + lifecycle_page_two["items"]] == [item["id"] for item in lifecycle_complete["items"]]
            staff_all = data(client.get("/api/search?q=Unified&page_size=50", headers=role_headers))
            assert "topic-unified-pending" in {item["id"] for item in staff_all["items"]}
            assert staff_all["counts"]["discussion"] == 4
            staff_pages = []
            for staff_page in range(1, 7):
                staff_pages.append(data(client.get(f"/api/search?q=Unified&page={staff_page}&page_size=3", headers=role_headers)))
            assert [item["id"] for page in staff_pages for item in page["items"]] == [item["id"] for item in staff_all["items"]]

        os.environ["COURSE_STATUS"] = "archived"
        for role_headers in (student, teacher, admin):
            archived = data(client.get("/api/search?q=Unified&page_size=50", headers=role_headers))
            assert archived["items"] == []
            assert archived["total"] == 0
            assert all(value == 0 for value in archived["counts"].values())
        os.environ["COURSE_STATUS"] = "active"

        os.environ["COURSE_ID"] = "2"
        os.environ["MOCK_COURSE_ID"] = "2"
        os.environ["COURSE_NAME"] = "Other Course"
        course_two = data(client.get("/api/search?q=Unified&page_size=50", headers=student))
        assert {item["id"] for item in course_two["items"]} == {"21", "res-unified-other", "kp-unified-other"}
        assert all(item["id"] not in {"res-unified-published", "kp-unified"} for item in course_two["items"])
        os.environ["COURSE_ID"] = "1"
        os.environ["MOCK_COURSE_ID"] = "999"
        assert client.get("/api/search?q=Unified", headers=student).status_code == 403
        os.environ["MOCK_COURSE_ID"] = "1"
        os.environ["COURSE_NAME"] = "Unified Course"

        assert client.get("/api/search?q=", headers=student).status_code == 422
        assert client.get("/api/search?q=Unified&kind=invalid", headers=student).status_code == 422
        assert client.get("/api/search?q=Unified%0AChapter", headers=student).status_code == 422
        assert client.get("/api/search?q=Unified&page=0", headers=student).status_code == 422
        assert client.get("/api/search?q=Unified&page=999999999999999999&page_size=50", headers=student).status_code == 422
        os.environ["MOCK_AUTH_MODE"] = "false"
        try:
            assert client.get("/api/search?q=Unified", headers={}).status_code == 401
        finally:
            os.environ["MOCK_AUTH_MODE"] = "true"

    print("GLOBAL_SEARCH_API_OK roles=3 kinds=7 stable_pagination=verified archived_isolation=verified")


if __name__ == "__main__":
    main()
