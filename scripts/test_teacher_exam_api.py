#!/usr/bin/env python3
"""ASGI acceptance for the teacher exam management lifecycle."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ["MOCK_AUTH_MODE"] = "true"
os.environ["MOCK_WORKFLOW_MODE"] = "true"
os.environ["AGENT_UID_SALT"] = "teacher-exam-api-test-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")


def data(response: httpx.Response, expected: int) -> dict:
    assert response.status_code == expected, response.text
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="teacher-exam-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, store

        teacher = {"x-dev-role": "teacher", "x-dev-user": "teacher-exam-owner"}
        student = {"x-dev-role": "student", "x-dev-user": "teacher-exam-student"}
        admin = {"x-dev-role": "admin", "x-dev-user": "teacher-exam-admin"}

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Mock auth resolves a missing role as the default student; the
            # production Moodle path is covered by the formal 401 gate.
            assert (await client.get("/api/teacher/exams")).status_code == 403
            assert (await client.get("/api/teacher/exams", headers=student)).status_code == 403
            assert (await client.get("/api/teacher/exams?page_size=101", headers=teacher)).status_code == 422

            question = data(await client.post(
                "/api/teacher/questions",
                headers={**teacher, "Idempotency-Key": "teacher-exam-question"},
                json={
                    "question_type": "single_choice",
                    "prompt": "储能系统的首要作用？",
                    "options": ["平衡供需", "取消电网"],
                    "answer": "平衡供需",
                    "max_score": 10,
                },
            ), 201)
            question_id = question["id"]
            data(await client.post(
                f"/api/teacher/questions/{question_id}/publish",
                headers={**teacher, "Idempotency-Key": "teacher-exam-question-publish"},
                json={},
            ), 200)

            draft_question = data(await client.post(
                "/api/teacher/questions",
                headers={**teacher, "Idempotency-Key": "teacher-exam-draft-question"},
                json={"question_type": "short_answer", "prompt": "草稿题目", "rubric": "要点", "max_score": 10},
            ), 201)
            now = datetime.now(timezone.utc)
            exam_payload = {
                "title": "教师考试管理验收考试",
                "question_ids": [question_id],
                "open_at": (now - timedelta(seconds=5)).isoformat(),
                "close_at": (now + timedelta(minutes=30)).isoformat(),
                "duration_seconds": 900,
                "allow_attempts": 2,
            }
            assert (await client.post(
                "/api/teacher/exams",
                headers={**student, "Idempotency-Key": "teacher-exam-student-create"},
                json=exam_payload,
            )).status_code == 403
            exam = data(await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "teacher-exam-create"},
                json=exam_payload,
            ), 201)
            exam_id = exam["id"]
            replay = data(await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "teacher-exam-create"},
                json=exam_payload,
            ), 200)
            assert replay["id"] == exam_id and replay["status"] == "draft"
            reused = await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "teacher-exam-create"},
                json={**exam_payload, "title": "改写标题"},
            )
            assert reused.status_code == 409 and reused.json()["error"]["code"] == "conflict"

            invalid = await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "teacher-exam-unpublished-question"},
                json={**exam_payload, "title": "非法题目考试", "question_ids": [draft_question["id"]]},
            )
            assert invalid.status_code == 422

            listed = data(await client.get("/api/teacher/exams", headers=teacher), 200)
            row = next(item for item in listed["items"] if item["id"] == exam_id)
            assert row["status"] == "draft" and row["question_count"] == 1 and row["created_by"]
            assert row["created_by"] != teacher["x-dev-user"]
            assert "answer_json" not in row and "rubric" not in row
            page = data(await client.get("/api/teacher/exams?page=1&page_size=1", headers=admin), 200)
            assert page["page"] == 1 and page["page_size"] == 1 and page["total"] >= 1
            assert (await client.get("/api/student/exams", headers=student)).json()["data"]["items"] == []

            published = data(await client.post(
                f"/api/teacher/exams/{exam_id}/publish",
                headers={**teacher, "Idempotency-Key": "teacher-exam-publish"},
                json={},
            ), 200)
            replay_publish = data(await client.post(
                f"/api/teacher/exams/{exam_id}/publish",
                headers={**teacher, "Idempotency-Key": "teacher-exam-publish"},
                json={},
            ), 200)
            assert published["status"] == "published" and replay_publish["id"] == exam_id
            listed_after_publish = data(await client.get("/api/teacher/exams", headers=teacher), 200)
            assert next(item for item in listed_after_publish["items"] if item["id"] == exam_id)["status"] == "published"
            student_exams = data(await client.get("/api/student/exams", headers=student), 200)
            assert any(item["id"] == exam_id for item in student_exams["items"])

            withdrawn = data(await client.post(
                f"/api/teacher/exams/{exam_id}/withdraw",
                headers={**teacher, "Idempotency-Key": "teacher-exam-withdraw"},
                json={},
            ), 200)
            assert withdrawn["status"] == "withdrawn"
            assert not any(item["id"] == exam_id for item in data(await client.get("/api/student/exams", headers=student), 200)["items"])

            archived = data(await client.post(
                f"/api/teacher/exams/{exam_id}/archive",
                headers={**admin, "Idempotency-Key": "teacher-exam-archive"},
                json={},
            ), 200)
            assert archived["status"] == "archived"
            assert next(item for item in data(await client.get("/api/teacher/exams", headers=teacher), 200)["items"] if item["id"] == exam_id)["status"] == "archived"
            assert exam_id in {item["object_id"] for item in store.audit_logs(exam_id)}

    print("TEACHER_EXAM_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
