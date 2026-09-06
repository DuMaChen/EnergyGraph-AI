#!/usr/bin/env python3
"""Exercise the fixed assignment fixture through the public Adapter API."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "acceptance/test-fixtures/assignment-A-001.json"
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "fixture-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def assert_status(response: object, expected: int) -> dict:
    assert response.status_code == expected, (response.status_code, response.text)
    return response.json()["data"]


def main() -> None:
    with tempfile.NamedTemporaryFile(prefix="assignment-fixture-", suffix=".db") as db_file:
        os.environ["COURSE_DB"] = db_file.name
        import sys

        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        teacher = {"x-dev-role": "teacher", "x-dev-user": "fixture-teacher"}
        students = [
            {"x-dev-role": "student", "x-dev-user": "fixture-student-a"},
            {"x-dev-role": "student", "x-dev-user": "fixture-student-b"},
        ]

        # Translate the versioned fixture into normal API payloads; no test
        # writes directly to SQLite, so this covers the real permission gates.
        question_ids: list[str] = []
        for index, item in enumerate(fixture["questions"], start=1):
            point = item["knowledge_point"]
            question_type = item["type"]
            payload = {
                "question_type": question_type,
                "prompt": f"固定夹具 {point} 第{index}题",
                "chapter_id": 3,
                "node_id": f"kp-3-{int(point.split('.')[1])}",
                "max_score": item["max_score"],
            }
            if question_type in {"single_choice", "multiple_choice"}:
                payload.update(options=["A", "B"], answer=item["answer"])
            elif question_type == "true_false":
                payload["answer"] = item["answer"]
            else:
                payload["rubric"] = item["rubric"]
            created = assert_status(
                client.post(
                    "/api/teacher/questions",
                    headers={**teacher, "idempotency-key": f"fixture-question-{index}"},
                    json=payload,
                ),
                201,
            )
            question_ids.append(created["id"])
            assert_status(
                client.post(
                    f"/api/teacher/questions/{created['id']}/publish",
                    headers={**teacher, "idempotency-key": f"fixture-publish-{index}"},
                    json={},
                ),
                200,
            )

        assignment = assert_status(
            client.post(
                "/api/teacher/assignments",
                headers={**teacher, "idempotency-key": "fixture-assignment"},
                json={"title": "A-001 固定验收作业", "question_ids": question_ids, "allow_attempts": 1},
            ),
            201,
        )
        assignment_id = assignment["id"]
        assert_status(
            client.post(
                f"/api/teacher/assignments/{assignment_id}/publish",
                headers={**teacher, "idempotency-key": "fixture-assignment-publish"},
                json={},
            ),
            200,
        )

        # Published student views must not contain answer keys or rubrics.
        student_assignment = assert_status(client.get(f"/api/student/assignments/{assignment_id}", headers=students[0]), 200)
        assert all("answer_json" not in question and "rubric" not in question for question in student_assignment["questions"])

        answers = {question_ids[0]: "A", question_ids[1]: "A", question_ids[2]: True, question_ids[3]: "列出组成", question_ids[4]: "分析并网约束"}
        teacher_submit = client.post(
            f"/api/student/assignments/{assignment_id}/submit",
            headers={**teacher, "idempotency-key": "fixture-teacher-submit"},
            json={"attempt": 1, "answers": answers},
        )
        assert teacher_submit.status_code == 403
        submissions: list[str] = []
        for index, student in enumerate(students, start=1):
            submission_body = {"assignment_id": assignment_id, "attempt": 1, "answers": answers}
            wrong_attempt = client.post(
                f"/api/student/assignments/{assignment_id}/submit",
                headers={**student, "idempotency-key": f"fixture-wrong-attempt-{index}"},
                json={**submission_body, "attempt": 2},
            )
            assert wrong_attempt.status_code == 422
            first = client.post(
                f"/api/student/assignments/{assignment_id}/submit",
                headers={**student, "idempotency-key": f"fixture-submit-{index}"},
                json=submission_body,
            )
            submission = assert_status(first, 201)
            retry = assert_status(
                client.post(
                    f"/api/student/assignments/{assignment_id}/submit",
                    headers={**student, "idempotency-key": f"fixture-submit-{index}"},
                    json=submission_body,
                ),
                200,
            )
            assert retry["id"] == submission["id"]
            submissions.append(submission["id"])

        task = assert_status(
            client.post(
                f"/api/teacher/assignments/{assignment_id}/grade",
                headers={**teacher, "idempotency-key": "fixture-grade-task"},
                json={},
            ),
            202,
        )
        assert task["total"] == 2 and task["status"] == "needs_review"
        teacher_submissions = assert_status(
            client.get(f"/api/teacher/assignments/{assignment_id}/submissions", headers=teacher), 200
        )
        assert teacher_submissions["total"] == 2
        assert "answers" in teacher_submissions["items"][0]
        assert client.get(f"/api/teacher/assignments/{assignment_id}/submissions", headers=students[0]).status_code == 403

        graded = assert_status(
            client.post(
                f"/api/teacher/submissions/{submissions[0]}/grade",
                headers={**teacher, "idempotency-key": "fixture-grade-one"},
                json={},
            ),
            200,
        )
        assert graded["subjective_pending"] == 2
        repeated_graded = assert_status(
            client.post(
                f"/api/teacher/submissions/{submissions[0]}/grade",
                headers={**teacher, "idempotency-key": "fixture-grade-one"},
                json={},
            ),
            200,
        )
        assert repeated_graded["submission_id"] == graded["submission_id"]
        subjective_id = next(row["question_id"] for row in graded["grades"] if row["question_id"] == question_ids[0])
        assert subjective_id == question_ids[0]

        # The mock grading branch returns a bounded draft score, still marked
        # as an Agent initial result for mandatory teacher review.
        review = assert_status(
            client.post(
                f"/api/teacher/submissions/{submissions[0]}/subjective/{question_ids[3]}/agent-review",
                headers={**teacher, "idempotency-key": "fixture-agent-review"},
                json={},
            ),
            200,
        )
        assert review["status"] == "needs_teacher_review"
        assert review["grade"]["source"] == "agent_initial"

        # Students may inspect only their own grades and feedback after a
        # teacher action; answer keys, rubrics and review reasons remain out
        # of the student response even when the assignment ID is known.
        student_result = assert_status(client.get(f"/api/student/assignments/{assignment_id}", headers=students[0]), 200)
        assert student_result["my_submissions"] and student_result["my_submissions"][0]["grades"]
        assert all("answer_json" not in grade and "review_reason" not in grade for grade in student_result["my_submissions"][0]["grades"])

        expired = assert_status(
            client.post(
                "/api/teacher/assignments",
                headers={**teacher, "idempotency-key": "fixture-expired-assignment"},
                json={
                    "title": "已截止作业",
                    "question_ids": [question_ids[0]],
                    "due_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                    "allow_attempts": 1,
                },
            ),
            201,
        )
        assert_status(
            client.post(
                f"/api/teacher/assignments/{expired['id']}/publish",
                headers={**teacher, "idempotency-key": "fixture-expired-publish"},
                json={},
            ),
            200,
        )
        expired_submit = client.post(
            f"/api/student/assignments/{expired['id']}/submit",
            headers={**students[0], "idempotency-key": "fixture-expired-submit"},
            json={"attempt": 1, "answers": {question_ids[0]: "A"}},
        )
        assert expired_submit.status_code == 409

        recommendations = assert_status(client.get("/api/student/recommendations", headers=students[0]), 200)
        assert all(item.get("resource_id") and item.get("page", 0) >= 1 for item in recommendations["items"])
        own_profile = assert_status(client.get("/api/student/learning-profile", headers=students[0]), 200)
        other_profile = assert_status(client.get("/api/student/learning-profile", headers=students[1]), 200)
        assert own_profile["user_uid"] != other_profile["user_uid"]
        assert all("prerequisite_gap" in node and "recent_error" in node for node in own_profile["nodes"])

    print("ACCEPTANCE_FIXTURE_OK")


if __name__ == "__main__":
    main()
