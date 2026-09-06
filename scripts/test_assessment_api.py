#!/usr/bin/env python3
"""ASGI contract tests for the student submission and teacher grading loop."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "assessment-api-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def payload(response: httpx.Response, status: int) -> dict:
    assert response.status_code == status, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="assessment-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        teacher = {"x-dev-role": "teacher", "x-dev-user": "assessment-teacher"}
        student = {"x-dev-role": "student", "x-dev-user": "assessment-student"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            question_ids: list[str] = []
            for index, body in enumerate([
                {"question_type": "single_choice", "prompt": "储能系统的作用？", "options": ["平衡供需", "取消电网"], "answer": "平衡供需", "max_score": 10},
                {"question_type": "essay", "prompt": "说明并网控制要点。", "rubric": "包含控制目标和约束", "max_score": 20},
            ], start=1):
                created = payload(await client.post("/api/teacher/questions", headers={**teacher, "Idempotency-Key": f"assessment-question-{index}"}, json=body), 201)
                question_ids.append(created["id"])
                payload(await client.post(f"/api/teacher/questions/{created['id']}/publish", headers={**teacher, "Idempotency-Key": f"assessment-question-publish-{index}"}, json={}), 200)
            assignment = payload(await client.post("/api/teacher/assignments", headers={**teacher, "Idempotency-Key": "assessment-assignment"}, json={"title": "作业闭环验收", "question_ids": question_ids, "allow_attempts": 1}), 201)
            assignment_id = assignment["id"]
            payload(await client.post(f"/api/teacher/assignments/{assignment_id}/publish", headers={**teacher, "Idempotency-Key": "assessment-assignment-publish"}, json={}), 200)

            expired = payload(
                await client.post(
                    "/api/teacher/assignments",
                    headers={**teacher, "Idempotency-Key": "assessment-expired-assignment"},
                    json={"title": "截止边界验收作业", "question_ids": [question_ids[0]], "allow_attempts": 1, "due_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()},
                ),
                201,
            )
            payload(await client.post(f"/api/teacher/assignments/{expired['id']}/publish", headers={**teacher, "Idempotency-Key": "assessment-expired-publish"}, json={}), 200)

            detail = payload(await client.get(f"/api/student/assignments/{assignment_id}", headers=student), 200)
            assert len(detail["questions"]) == 2
            assert all("answer_json" not in question and "rubric" not in question for question in detail["questions"])
            assert (await client.get(f"/api/teacher/assignments/{assignment_id}/submissions", headers=student)).status_code == 403

            answers = {question_ids[0]: "平衡供需", question_ids[1]: "说明控制目标和约束"}
            submission_body = {"attempt": 1, "answers": answers}
            first = payload(await client.post(f"/api/student/assignments/{assignment_id}/submit", headers={**student, "Idempotency-Key": "assessment-submit"}, json=submission_body), 201)
            replay = payload(await client.post(f"/api/student/assignments/{assignment_id}/submit", headers={**student, "Idempotency-Key": "assessment-submit"}, json=submission_body), 200)
            assert replay["id"] == first["id"]
            assert (await client.post(f"/api/student/assignments/{assignment_id}/submit", headers={**student, "Idempotency-Key": "assessment-submit-second"}, json=submission_body)).status_code == 409
            assert (await client.post(f"/api/student/assignments/{assignment_id}/submit", headers={**teacher, "Idempotency-Key": "assessment-teacher-submit"}, json=submission_body)).status_code == 403
            expired_submit = await client.post(
                f"/api/student/assignments/{expired['id']}/submit",
                headers={**student, "Idempotency-Key": "assessment-expired-submit"},
                json={"attempt": 1, "answers": {question_ids[0]: "平衡供需"}},
            )
            assert expired_submit.status_code == 409
            assert expired_submit.json()["error"]["code"] == "deadline_passed"

            before_grade = payload(await client.get(f"/api/teacher/assignments/{assignment_id}/submissions", headers=teacher), 200)
            assert before_grade["total"] == 1 and before_grade["items"][0]["answers"] == answers
            batch = payload(await client.post(f"/api/teacher/assignments/{assignment_id}/grade", headers={**teacher, "Idempotency-Key": "assessment-batch-grade"}, json={}), 202)
            assert batch["status"] in {"needs_review", "partial_failure"}
            after_grade = payload(await client.get(f"/api/teacher/assignments/{assignment_id}/submissions", headers=teacher), 200)
            grades = after_grade["items"][0]["grades"]
            assert any(grade["question_id"] == question_ids[0] and grade["source"] == "deterministic" for grade in grades)
            assert (await client.post(f"/api/teacher/submissions/{first['id']}/grade", headers={**teacher, "Idempotency-Key": "assessment-grade-repeat"}, json={})).status_code == 200

            agent_review = payload(
                await client.post(
                    f"/api/teacher/submissions/{first['id']}/subjective/{question_ids[1]}/agent-review",
                    headers={**teacher, "Idempotency-Key": "assessment-subjective-review"},
                    json={},
                ),
                200,
            )
            assert agent_review["status"] == "needs_teacher_review"
            assert agent_review["grade"]["source"] == "agent_initial"
            reviewed = payload(
                await client.patch(
                    f"/api/teacher/grade-items/{agent_review['grade']['id']}",
                    headers={**teacher, "Idempotency-Key": "assessment-teacher-review"},
                    json={"score": 18, "reason": "教师已按评分标准复核"},
                ),
                200,
            )
            assert reviewed["source"] == "teacher_review"
            assert reviewed["score"] == 18

            student_result = payload(await client.get(f"/api/student/assignments/{assignment_id}", headers=student), 200)
            assert student_result["my_submissions"]
            assert all("answer_json" not in grade and "review_reason" not in grade for grade in student_result["my_submissions"][0]["grades"])
            assert (await client.post(f"/api/teacher/assignments/{assignment_id}/grade", headers={**student, "Idempotency-Key": "assessment-student-grade"}, json={})).status_code == 403

    print("ASSESSMENT_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
