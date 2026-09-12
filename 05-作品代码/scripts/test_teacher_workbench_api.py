#!/usr/bin/env python3
"""BUILD-070 API acceptance for teacher question, publishing and gradebook flows."""

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
os.environ.setdefault("AGENT_UID_SALT", "teacher-workbench-api-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def data(response: httpx.Response, expected: int) -> dict:
    assert response.status_code == expected, response.text
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="teacher-workbench-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, store

        teacher = {"x-dev-role": "teacher", "x-dev-user": "build070-teacher"}
        student = {"x-dev-role": "student", "x-dev-user": "build070-student"}
        admin = {"x-dev-role": "admin", "x-dev-user": "build070-admin"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/teacher/questions", headers=student)).status_code == 403
            assert (await client.get("/api/teacher/gradebook", headers=student)).status_code == 403

            first_payload = {"question_type": "single_choice", "prompt": "储能系统的首要作用？", "options": ["平衡供需", "取消电网"], "answer": "平衡供需", "max_score": 10, "chapter_id": 3, "node_id": "kp-3-1"}
            first = data(await client.post("/api/teacher/questions", headers={**teacher, "Idempotency-Key": "build070-question-1"}, json=first_payload), 201)
            replay = data(await client.post("/api/teacher/questions", headers={**teacher, "Idempotency-Key": "build070-question-1"}, json=first_payload), 200)
            assert replay["id"] == first["id"]

            edited = data(await client.patch(f"/api/teacher/questions/{first['id']}", headers={**teacher, "Idempotency-Key": "build070-question-edit-1"}, json={"base_version": 1, "prompt": "储能系统首先承担什么作用？"}), 200)
            assert edited["version"] == 2 and edited["prompt"] == "储能系统首先承担什么作用？"
            stale = await client.patch(f"/api/teacher/questions/{first['id']}", headers={**teacher, "Idempotency-Key": "build070-question-edit-stale"}, json={"base_version": 1, "prompt": "过期编辑"})
            assert stale.status_code == 409 and stale.json()["error"]["code"] == "question_version_conflict"

            second = data(await client.post("/api/teacher/questions", headers={**teacher, "Idempotency-Key": "build070-question-2"}, json={"question_type": "essay", "prompt": "说明并网控制的关键约束。", "rubric": "包含功率目标和电流约束", "max_score": 20, "chapter_id": 3}), 201)
            listed = data(await client.get("/api/teacher/questions", headers=teacher), 200)
            assert {item["id"] for item in listed["items"]} >= {first["id"], second["id"]}
            assert listed["items"][0].get("answer") is not None or any(item["id"] == first["id"] for item in listed["items"])

            published_first = data(await client.post(f"/api/teacher/questions/{first['id']}/publish", headers={**teacher, "Idempotency-Key": "build070-question-publish-1"}, json={}), 200)
            published_second = data(await client.post(f"/api/teacher/questions/{second['id']}/publish", headers={**teacher, "Idempotency-Key": "build070-question-publish-2"}, json={}), 200)
            assert published_first["status"] == "published" and published_second["status"] == "published"

            assignment = data(await client.post("/api/teacher/assignments", headers={**teacher, "Idempotency-Key": "build070-assignment-create"}, json={"title": "BUILD-070 发布验收作业", "question_ids": [first["id"], second["id"]], "allow_attempts": 1}), 201)
            assignment_id = assignment["id"]
            teacher_assignments = data(await client.get("/api/teacher/assignments", headers=teacher), 200)
            assert any(item["id"] == assignment_id and item["status"] == "draft" for item in teacher_assignments["items"])
            data(await client.post(f"/api/teacher/assignments/{assignment_id}/publish", headers={**teacher, "Idempotency-Key": "build070-assignment-publish"}, json={}), 200)
            student_detail = data(await client.get(f"/api/student/assignments/{assignment_id}", headers=student), 200)
            assert len(student_detail["questions"]) == 2
            assert all("answer_json" not in item and "rubric" not in item for item in student_detail["questions"])

            submission = data(await client.post(f"/api/student/assignments/{assignment_id}/submit", headers={**student, "Idempotency-Key": "build070-submit"}, json={"attempt": 1, "answers": {first["id"]: "平衡供需", second["id"]: "说明功率目标和电流约束"}}), 201)
            batch = data(await client.post(f"/api/teacher/assignments/{assignment_id}/grade", headers={**teacher, "Idempotency-Key": "build070-grade"}, json={}), 202)
            assert batch["status"] in {"needs_review", "partial_failure"}
            gradebook = data(await client.get("/api/teacher/gradebook", headers=teacher), 200)
            summary = next(item for item in gradebook["assignments"] if item["id"] == assignment_id)
            assert summary["submitted_count"] == 1 and summary["graded_count"] == 1 and summary["average_ratio"] > 0
            assert any(item["user_uid"].startswith("u_") for item in gradebook["students"])
            assert gradebook["knowledge_points"]

            withdrawn = data(await client.post(f"/api/teacher/assignments/{assignment_id}/withdraw", headers={**teacher, "Idempotency-Key": "build070-assignment-withdraw"}, json={}), 200)
            assert withdrawn["status"] == "withdrawn"
            assert (await client.get(f"/api/student/assignments/{assignment_id}", headers=student)).status_code == 404
            republished = data(await client.post(f"/api/teacher/assignments/{assignment_id}/publish", headers={**teacher, "Idempotency-Key": "build070-assignment-republish"}, json={}), 200)
            assert republished["status"] == "published"

            archived_question = data(await client.post(f"/api/teacher/questions/{second['id']}/archive", headers={**teacher, "Idempotency-Key": "build070-question-archive"}, json={}), 200)
            assert archived_question["status"] == "archived"
            archived_publish = await client.post(f"/api/teacher/questions/{second['id']}/publish", headers={**teacher, "Idempotency-Key": "build070-question-publish-archived"}, json={})
            assert archived_publish.status_code == 409, archived_publish.text
            admin_book = data(await client.get("/api/teacher/gradebook", headers=admin), 200)
            assert "assignments" in admin_book

            audit_ids = {item["object_id"] for item in store.audit_logs(first["id"])}
            assert first["id"] in audit_ids

    print("TEACHER_WORKBENCH_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
