#!/usr/bin/env python3
"""ASGI contract tests for student assignment drafts and optimistic locking."""

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
os.environ.setdefault("AGENT_UID_SALT", "assignment-draft-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="assignment-draft-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        student = {"x-dev-role": "student", "x-dev-user": "draft-student"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "draft-teacher"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            question_response = await client.post(
                "/api/teacher/questions",
                headers={**teacher, "Idempotency-Key": "draft-question"},
                json={
                    "question_type": "single_choice",
                    "prompt": "储能系统的核心作用是什么？",
                    "options": ["平衡供需", "取消电网"],
                    "answer": "平衡供需",
                    "max_score": 10,
                },
            )
            assert question_response.status_code == 201, question_response.text
            question_id = question_response.json()["data"]["id"]
            publish_question = await client.post(
                f"/api/teacher/questions/{question_id}/publish",
                headers={**teacher, "Idempotency-Key": "draft-question-publish"},
                json={},
            )
            assert publish_question.status_code == 200, publish_question.text
            assignment_response = await client.post(
                "/api/teacher/assignments",
                headers={**teacher, "Idempotency-Key": "draft-assignment"},
                json={"title": "草稿验收作业", "question_ids": [question_id], "allow_attempts": 1},
            )
            assert assignment_response.status_code == 201, assignment_response.text
            assignment_id = assignment_response.json()["data"]["id"]
            publish_assignment = await client.post(
                f"/api/teacher/assignments/{assignment_id}/publish",
                headers={**teacher, "Idempotency-Key": "draft-assignment-publish"},
                json={},
            )
            assert publish_assignment.status_code == 200, publish_assignment.text

            initial = await client.get(f"/api/student/assignments/{assignment_id}/draft", headers=student)
            assert initial.status_code == 200, initial.text
            assert initial.json()["data"]["version"] == 0
            assert initial.json()["data"]["has_saved_draft"] is False

            body = {"attempt": 1, "answers": {question_id: "平衡供需"}, "base_version": 0}
            saved = await client.put(
                f"/api/student/assignments/{assignment_id}/draft",
                headers={**student, "Idempotency-Key": "draft-save-1"},
                json=body,
            )
            assert saved.status_code == 200, saved.text
            assert saved.json()["data"]["version"] == 1
            replay = await client.put(
                f"/api/student/assignments/{assignment_id}/draft",
                headers={**student, "Idempotency-Key": "draft-save-1"},
                json=body,
            )
            assert replay.status_code == 200, replay.text
            assert replay.json()["data"] == saved.json()["data"]

            conflict = await client.put(
                f"/api/student/assignments/{assignment_id}/draft",
                headers={**student, "Idempotency-Key": "draft-save-stale"},
                json={"attempt": 1, "answers": {question_id: "取消电网"}, "base_version": 0},
            )
            assert conflict.status_code == 409, conflict.text
            assert conflict.json()["error"]["code"] == "assignment_draft_conflict"
            assert conflict.json()["current"]["version"] == 1

            detail = await client.get(f"/api/student/assignments/{assignment_id}", headers=student)
            assert detail.status_code == 200, detail.text
            assert detail.json()["data"]["my_draft"]["answers"][question_id] == "平衡供需"
            assert "answer_json" not in detail.json()["data"]["questions"][0]
            assert (await client.get(f"/api/student/assignments/{assignment_id}/draft", headers=teacher)).status_code == 403
            assert (await client.put(f"/api/student/assignments/{assignment_id}/draft", headers={**teacher, "Idempotency-Key": "teacher-draft"}, json=body)).status_code == 403

    print("ASSIGNMENT_DRAFT_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
