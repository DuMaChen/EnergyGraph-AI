#!/usr/bin/env python3
"""Deterministic ASGI checks for the unified student task center."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ["MOCK_AUTH_MODE"] = "true"
os.environ["MOCK_WORKFLOW_MODE"] = "true"
os.environ["MOCK_COURSE_ID"] = "1"
os.environ["AGENT_UID_SALT"] = "task-center-api-test-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")

NOW = datetime(2026, 7, 29, 8, 0, tzinfo=timezone.utc)
os.environ["TASK_CENTER_NOW"] = NOW.isoformat()


def payload(response: httpx.Response, expected: int = 200) -> dict:
    assert response.status_code == expected, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


def seed(store: object, uid: str) -> None:
    with store.connect() as db:
        assignments = [
            ("task-a-pending", 1, "待完成作业", "published", "2026-08-02T08:00:00+00:00", "2026-07-29T01:00:00+00:00"),
            ("task-a-progress", 1, "进行中作业", "published", "2026-08-03T08:00:00+00:00", "2026-07-29T02:00:00+00:00"),
            ("task-a-expired", 1, "过期作业", "published", "2026-07-28T08:00:00+00:00", "2026-07-28T01:00:00+00:00"),
            ("task-a-complete", 1, "已完成作业", "published", "2026-07-28T07:00:00+00:00", "2026-07-27T01:00:00+00:00"),
            ("task-a-course-two", 2, "其他课程作业", "published", "2026-08-01T08:00:00+00:00", "2026-07-29T03:00:00+00:00"),
        ]
        for item_id, course_id, title, status, due_at, updated_at in assignments:
            db.execute(
                "INSERT INTO assignments(id,course_id,title,question_ids_json,status,due_at,allow_attempts,created_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (item_id, course_id, title, "[]", status, due_at, 1, "teacher-fixture", updated_at),
            )
        for assignment_id, updated_at in (
            ("task-a-progress", "2026-07-29T07:00:00+00:00"),
            ("task-a-expired", "2026-07-29T06:00:00+00:00"),
        ):
            db.execute(
                "INSERT INTO assignment_drafts(user_uid,assignment_id,attempt,answers_json,version,updated_at) VALUES(?,?,?,?,?,?)",
                (uid, assignment_id, 1, "{}", 1, updated_at),
            )
        db.execute(
            "INSERT INTO submissions(id,assignment_id,user_uid,answers_json,attempt,status,created_at) VALUES(?,?,?,?,?,?,?)",
            ("task-sub-complete", "task-a-complete", uid, "{}", 1, "submitted", "2026-07-29T07:30:00+00:00"),
        )
        db.execute(
            "INSERT INTO submissions(id,assignment_id,user_uid,answers_json,attempt,status,created_at) VALUES(?,?,?,?,?,?,?)",
            ("task-sub-other-user", "task-a-pending", "another-user", "{}", 1, "submitted", "2026-07-29T07:40:00+00:00"),
        )

        exams = [
            ("task-e-pending", 1, "待开始考试", "2026-07-30T08:00:00+00:00", "2026-08-04T08:00:00+00:00", "2026-07-29T01:10:00+00:00"),
            ("task-e-progress", 1, "进行中考试", "2026-07-28T08:00:00+00:00", "2026-08-05T08:00:00+00:00", "2026-07-29T02:10:00+00:00"),
            ("task-e-expired", 1, "已结束考试", "2026-07-27T08:00:00+00:00", "2026-07-28T08:00:00+00:00", "2026-07-28T02:10:00+00:00"),
            ("task-e-complete", 1, "已完成考试", "2026-07-27T08:00:00+00:00", "2026-07-28T07:00:00+00:00", "2026-07-27T02:10:00+00:00"),
            ("task-e-course-two", 2, "其他课程考试", "2026-07-28T08:00:00+00:00", "2026-08-06T08:00:00+00:00", "2026-07-29T03:10:00+00:00"),
        ]
        for item_id, course_id, title, open_at, close_at, updated_at in exams:
            db.execute(
                "INSERT INTO exams(id,course_id,title,question_ids_json,status,open_at,close_at,duration_seconds,allow_attempts,created_by,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (item_id, course_id, title, "[]", "published", open_at, close_at, 1800, 1, "teacher-fixture", updated_at),
            )
        for exam_id, deadline_at in (
            ("task-e-progress", "2026-08-05T08:00:00+00:00"),
            ("task-e-expired", "2026-07-28T08:00:00+00:00"),
        ):
            db.execute(
                "INSERT INTO exam_attempts(id,exam_id,user_uid,attempt,started_at,deadline_at,status) VALUES(?,?,?,?,?,?,?)",
                (f"attempt-{exam_id}", exam_id, uid, 1, "2026-07-29T06:00:00+00:00", deadline_at, "in_progress"),
            )
            db.execute(
                "INSERT INTO exam_drafts(user_uid,exam_id,attempt,answers_json,version,updated_at) VALUES(?,?,?,?,?,?)",
                (uid, exam_id, 1, "{}", 1, "2026-07-29T06:30:00+00:00"),
            )
        db.execute(
            "INSERT INTO exam_submissions(id,exam_id,user_uid,attempt,answers_json,submitted_at,status,score,max_score,needs_review) VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("task-exam-sub", "task-e-complete", uid, 1, "{}", "2026-07-29T07:20:00+00:00", "submitted", 0, 0, 0),
        )

        topics = [
            ("task-d-pending", 1, "待参与讨论", "请发表观点", "open", "teacher-fixture", "2026-07-29T05:00:00+00:00"),
            ("task-d-complete", 1, "已参与讨论", "已回复主题", "open", "teacher-fixture", "2026-07-29T05:10:00+00:00"),
            ("task-d-expired", 1, "已关闭讨论", "主题已关闭", "closed", "teacher-fixture", "2026-07-29T05:20:00+00:00"),
            ("task-d-hidden", 1, "审核中讨论", "学生不可见", "pending_review", "teacher-fixture", "2026-07-29T05:30:00+00:00"),
            ("task-d-course-two", 2, "其他课程讨论", "不得泄漏", "open", "teacher-fixture", "2026-07-29T05:40:00+00:00"),
        ]
        for topic in topics:
            db.execute(
                "INSERT INTO discussion_topics(id,course_id,title,body,status,author_uid,updated_at) VALUES(?,?,?,?,?,?,?)",
                topic,
            )
        db.execute(
            "INSERT INTO discussion_replies(id,topic_id,author_uid,body,status,created_at) VALUES(?,?,?,?,?,?)",
            ("task-reply", "task-d-complete", uid, "我的回复", "visible", "2026-07-29T06:40:00+00:00"),
        )

        notices = [
            ("task-n-pending", 1, "course_students", "未读通知", "请查看课程更新", "2026-07-29T06:00:00+00:00"),
            ("task-n-complete", 1, "course_all", "已读通知", "已查看的课程更新", "2026-07-29T06:10:00+00:00"),
            ("task-n-teacher", 1, "course_teachers", "教师通知", "学生不可见", "2026-07-29T06:20:00+00:00"),
            ("task-n-course-two", 2, "course_students", "其他课程通知", "不得泄漏", "2026-07-29T06:30:00+00:00"),
        ]
        for item_id, course_id, audience, title, body, created_at in notices:
            db.execute(
                "INSERT INTO notifications(id,course_id,audience,title,body,created_by,created_at) VALUES(?,?,?,?,?,?,?)",
                (item_id, course_id, audience, title, body, "teacher-fixture", created_at),
            )
        db.execute(
            "INSERT INTO notification_reads(notification_id,user_uid,read_at) VALUES(?,?,?)",
            ("task-n-complete", uid, "2026-07-29T07:10:00+00:00"),
        )
        db.commit()


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="task-center-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, stable_uid, store

        student_uid = stable_uid("task-center-student")
        seed(store, student_uid)

        direct = store.student_task_center(student_uid, 1, now=NOW)
        assert direct["total"] == 13
        assert direct["counts"] == {
            "by_status": {"pending": 4, "in_progress": 2, "completed": 4, "expired": 3},
            "by_kind": {"assignment": 4, "exam": 4, "discussion": 3, "notification": 2},
        }
        by_id = {item["id"]: item for item in direct["items"]}
        assert by_id["assignment:task-a-expired"]["status"] == "expired"
        assert by_id["exam:task-e-expired"]["status"] == "expired"
        assert by_id["assignment:task-a-pending"]["status"] == "pending"
        assert by_id["discussion:task-d-complete"]["status"] == "completed"
        assert by_id["notification:task-n-complete"]["status"] == "completed"
        assert not any("course-two" in item["source_id"] or "hidden" in item["source_id"] or "teacher" in item["source_id"] for item in direct["items"])
        terminal_seen = False
        for item in direct["items"]:
            if item["status"] == "completed":
                terminal_seen = True
            elif terminal_seen:
                raise AssertionError("completed task sorted before unfinished task")
            assert not ({"user_uid", "author_uid", "answers", "score", "audience", "created_by"} & set(item))

        headers = {"x-dev-role": "student", "x-dev-user": "task-center-student"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "task-center-teacher"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            page_one = payload(await client.get("/api/student/tasks?page=1&page_size=2", headers=headers))
            assert page_one["page"] == 1 and page_one["page_size"] == 2 and page_one["total"] == 13
            assert len(page_one["items"]) == 2 and page_one["counts"] == direct["counts"]
            expired_exams = payload(await client.get("/api/student/tasks?kind=exam&status=expired", headers=headers))
            assert expired_exams["total"] == 1 and expired_exams["items"][0]["source_id"] == "task-e-expired"
            assert expired_exams["counts"] == direct["counts"]
            assert (await client.get("/api/student/tasks?kind=grade", headers=headers)).status_code == 422
            assert (await client.get("/api/student/tasks?status=unknown", headers=headers)).status_code == 422
            assert (await client.get("/api/student/tasks?page=0", headers=headers)).status_code == 422
            assert (await client.get("/api/student/tasks", headers=teacher)).status_code == 403

        print("TASK_CENTER_API_OK cases=four_kinds,user_state,deadlines,filters,pagination,counts,ordering,privacy,course_scope,role")


if __name__ == "__main__":
    asyncio.run(run())
