#!/usr/bin/env python3
"""ASGI contract tests for the independent timed-exam workflow."""

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
os.environ["AGENT_UID_SALT"] = "exam-api-test-only"
os.environ["COURSE_MANIFEST"] = str(ROOT / "course-data/normalized/manifest.json")
os.environ["GRAPH_BASELINE"] = str(ROOT / "course-data/normalized/graph-baseline.json")


def data(response: httpx.Response, status: int) -> dict:
    assert response.status_code == status, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def main() -> None:
    with tempfile.TemporaryDirectory(prefix="exam-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        teacher = {"x-dev-role": "teacher", "x-dev-user": "exam-teacher"}
        student = {"x-dev-role": "student", "x-dev-user": "exam-student"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            question = data(await client.post(
                "/api/teacher/questions",
                headers={**teacher, "Idempotency-Key": "exam-question"},
                json={"question_type": "single_choice", "prompt": "储能系统的主要作用？", "options": ["平衡供需", "取消电网"], "answer": "平衡供需", "max_score": 10},
            ), 201)
            question_id = question["id"]
            data(await client.post(f"/api/teacher/questions/{question_id}/publish", headers={**teacher, "Idempotency-Key": "exam-question-publish"}, json={}), 200)

            now = datetime.now(timezone.utc)
            exam = data(await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "exam-create"},
                json={"title": "第 3 章限时考试", "question_ids": [question_id], "open_at": (now - timedelta(seconds=5)).isoformat(), "close_at": (now + timedelta(seconds=120)).isoformat(), "duration_seconds": 60, "allow_attempts": 1},
            ), 201)
            exam_id = exam["id"]
            data(await client.post(f"/api/teacher/exams/{exam_id}/publish", headers={**teacher, "Idempotency-Key": "exam-publish"}, json={}), 200)

            listed = data(await client.get("/api/student/exams", headers=student), 200)
            assert any(item["id"] == exam_id and item["question_count"] == 1 for item in listed["items"])
            detail = data(await client.get(f"/api/student/exams/{exam_id}", headers=student), 200)
            assert detail["questions"][0]["id"] == question_id
            assert "answer_json" not in detail["questions"][0]
            assert (await client.get(f"/api/student/exams/{exam_id}", headers=teacher)).status_code == 403

            start_headers = {**student, "Idempotency-Key": "exam-start"}
            started = data(await client.post(f"/api/student/exams/{exam_id}/start", headers=start_headers, json={}), 200)
            assert started["attempt"]["attempt"] == 1
            assert started["attempt"]["status"] == "in_progress"
            repeated_start = data(await client.post(f"/api/student/exams/{exam_id}/start", headers=start_headers, json={}), 200)
            assert repeated_start["attempt"] == started["attempt"]

            initial = data(await client.get(f"/api/student/exams/{exam_id}/draft", headers=student), 200)
            assert initial["version"] == 0
            draft_body = {"attempt": 1, "answers": {question_id: "平衡供需"}, "base_version": 0}
            saved = data(await client.put(f"/api/student/exams/{exam_id}/draft", headers={**student, "Idempotency-Key": "exam-draft"}, json=draft_body), 200)
            assert saved["version"] == 1
            assert data(await client.put(f"/api/student/exams/{exam_id}/draft", headers={**student, "Idempotency-Key": "exam-draft"}, json=draft_body), 200)["version"] == 1
            conflict = await client.put(f"/api/student/exams/{exam_id}/draft", headers={**student, "Idempotency-Key": "exam-draft-stale"}, json={**draft_body, "answers": {question_id: "取消电网"}})
            assert conflict.status_code == 409 and conflict.json()["error"]["code"] == "exam_draft_conflict"

            submission = data(await client.post(f"/api/student/exams/{exam_id}/submit", headers={**student, "Idempotency-Key": "exam-submit"}, json={"attempt": 1, "answers": {question_id: "平衡供需"}}), 201)
            assert submission["score"] == 10 and submission["max_score"] == 10
            replay = data(await client.post(f"/api/student/exams/{exam_id}/submit", headers={**student, "Idempotency-Key": "exam-submit"}, json={"attempt": 1, "answers": {question_id: "平衡供需"}}), 200)
            assert replay["id"] == submission["id"]
            assert (await client.post(f"/api/student/exams/{exam_id}/submit", headers={**student, "Idempotency-Key": "exam-submit-second"}, json={"attempt": 1, "answers": {question_id: "平衡供需"}})).status_code == 409
            assert (await client.post(f"/api/student/exams/{exam_id}/start", headers={**student, "Idempotency-Key": "exam-start-second"}, json={})).status_code == 409

            early = data(await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "exam-early-create"},
                json={"title": "尚未开放考试", "question_ids": [question_id], "open_at": (now + timedelta(seconds=60)).isoformat(), "close_at": (now + timedelta(seconds=120)).isoformat(), "duration_seconds": 60},
            ), 201)
            data(await client.post(f"/api/teacher/exams/{early['id']}/publish", headers={**teacher, "Idempotency-Key": "exam-early-publish"}, json={}), 200)
            early_start = await client.post(f"/api/student/exams/{early['id']}/start", headers={**student, "Idempotency-Key": "exam-early-start"}, json={})
            assert early_start.status_code == 409 and early_start.json()["error"]["code"] == "exam_not_open"

            closed = data(await client.post(
                "/api/teacher/exams",
                headers={**teacher, "Idempotency-Key": "exam-closed-create"},
                json={"title": "已结束考试", "question_ids": [question_id], "open_at": (now - timedelta(seconds=120)).isoformat(), "close_at": (now - timedelta(seconds=60)).isoformat(), "duration_seconds": 60},
            ), 201)
            data(await client.post(f"/api/teacher/exams/{closed['id']}/publish", headers={**teacher, "Idempotency-Key": "exam-closed-publish"}, json={}), 200)
            closed_start = await client.post(f"/api/student/exams/{closed['id']}/start", headers={**student, "Idempotency-Key": "exam-closed-start"}, json={})
            assert closed_start.status_code == 409 and closed_start.json()["error"]["code"] == "exam_closed"

        print("EXAM_API_OK")


if __name__ == "__main__":
    asyncio.run(main())
