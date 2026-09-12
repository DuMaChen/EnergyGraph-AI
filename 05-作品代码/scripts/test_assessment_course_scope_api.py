#!/usr/bin/env python3
"""Verify assessment routes bind reads and writes to the authenticated course."""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]


def data(response: httpx.Response, expected_status: int) -> dict:
    assert response.status_code == expected_status, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="assessment-course-scope-") as directory:
        os.environ.update({
            "COURSE_DB": str(Path(directory) / "course.db"),
            "COURSE_MANIFEST": str(ROOT / "course-data/normalized/manifest.json"),
            "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
            "MOCK_AUTH_MODE": "true",
            "MOCK_WORKFLOW_MODE": "true",
            "AGENT_UID_SALT": "assessment-course-scope-test-only",
            "COURSE_ID": "2",
            "MOCK_COURSE_ID": "2",
        })
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        teacher = {"x-dev-role": "teacher", "x-dev-user": "scope-teacher"}
        student = {"x-dev-role": "student", "x-dev-user": "scope-student"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            question = data(
                await client.post(
                    "/api/teacher/questions",
                    headers={**teacher, "Idempotency-Key": "scope-question"},
                    json={
                        "question_type": "single_choice",
                        "prompt": "课程二题目",
                        "options": ["A", "B"],
                        "answer": "A",
                        "max_score": 10,
                    },
                ),
                201,
            )
            question_id = question["id"]
            data(
                await client.post(
                    f"/api/teacher/questions/{question_id}/publish",
                    headers={**teacher, "Idempotency-Key": "scope-question-publish"},
                    json={},
                ),
                200,
            )
            assignment = data(
                await client.post(
                    "/api/teacher/assignments",
                    headers={**teacher, "Idempotency-Key": "scope-assignment"},
                    json={"title": "课程二作业", "question_ids": [question_id]},
                ),
                201,
            )
            assignment_id = assignment["id"]
            data(
                await client.post(
                    f"/api/teacher/assignments/{assignment_id}/publish",
                    headers={**teacher, "Idempotency-Key": "scope-assignment-publish"},
                    json={},
                ),
                200,
            )
            listing = data(await client.get("/api/student/assignments", headers=student), 200)
            assert [item["id"] for item in listing["items"]] == [assignment_id]
            assert data(await client.get(f"/api/student/assignments/{assignment_id}", headers=student), 200)["id"] == assignment_id

            os.environ["COURSE_ID"] = "1"
            os.environ["MOCK_COURSE_ID"] = "1"
            assert (await client.get(f"/api/student/assignments/{assignment_id}", headers=student)).status_code == 404
            assert data(await client.get("/api/student/assignments", headers=student), 200)["items"] == []

    for name in ("COURSE_DB", "COURSE_MANIFEST", "GRAPH_BASELINE", "MOCK_AUTH_MODE", "MOCK_WORKFLOW_MODE", "AGENT_UID_SALT", "COURSE_ID", "MOCK_COURSE_ID"):
        os.environ.pop(name, None)
    print("ASSESSMENT_COURSE_SCOPE_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
