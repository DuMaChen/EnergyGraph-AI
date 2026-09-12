#!/usr/bin/env python3
"""Verify the isolated course-scoped discussion moderation workflow."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]


def data(response: httpx.Response, expected: int) -> dict:
    assert response.status_code == expected, response.text
    payload = response.json()
    assert payload.get("status") == "ok", payload
    return payload["data"]


def assert_no_sensitive_fields(response: httpx.Response) -> None:
    serialized = json.dumps(response.json(), ensure_ascii=False).casefold()
    for field in ("email", "password", "secret", "cookie", "authorization", "bridge_token"):
        assert field not in serialized, (field, response.text)


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="admin-moderation-") as directory:
        os.environ.update({
            "COURSE_DB": str(Path(directory) / "course.db"),
            "COURSE_MANIFEST": str(ROOT / "course-data/normalized/manifest.json"),
            "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
            "MOCK_AUTH_MODE": "true",
            "MOCK_COURSE_ID": "1",
            "COURSE_ID": "1",
            "AGENT_UID_SALT": "admin-moderation-test-only",
        })
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, store

        student = {"x-dev-role": "student", "x-dev-user": "moderation-student"}
        other_student = {"x-dev-role": "student", "x-dev-user": "moderation-other"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "moderation-teacher"}
        admin = {"x-dev-role": "admin", "x-dev-user": "moderation-admin"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/admin/moderation", headers=teacher)).status_code == 403

            topic = data(await client.post(
                "/api/discussions",
                headers={**student, "Idempotency-Key": "moderation-topic"},
                json={"title": "待审核主题", "body": "请核对这个课程问题。"},
            ), 201)
            topic_id = topic["id"]
            reply = data(await client.post(
                f"/api/discussions/{topic_id}/replies",
                headers={**other_student, "Idempotency-Key": "moderation-reply"},
                json={"body": "这是待审核的补充说明。"},
            ), 201)
            reply_id = reply["id"]
            other_topic = data(await client.post(
                "/api/discussions",
                headers={**student, "Idempotency-Key": "moderation-other-topic"},
                json={"title": "另一个主题", "body": "不能跨主题举报回复。"},
            ), 201)
            assert (await client.post(
                f"/api/discussions/{other_topic['id']}/report",
                headers={**student, "Idempotency-Key": "moderation-cross-topic"},
                json={"reply_id": reply_id, "reason": "跨主题测试。"},
            )).status_code == 404

            reported_reply = await client.post(
                f"/api/discussions/{topic_id}/report",
                headers={**student, "Idempotency-Key": "moderation-report-reply", "X-Request-ID": "report-reply-request"},
                json={"reply_id": reply_id, "reason": "需要管理员核对该回复。"},
            )
            reply_report = data(reported_reply, 202)
            assert reply_report == {"id": reply_id, "topic_id": topic_id, "content_type": "reply", "status": "pending_review"}
            replay = data(await client.post(
                f"/api/discussions/{topic_id}/report",
                headers={**student, "Idempotency-Key": "moderation-report-reply"},
                json={"reply_id": reply_id, "reason": "需要管理员核对该回复。"},
            ), 200)
            assert replay == reply_report
            assert (await client.post(
                f"/api/discussions/{topic_id}/report",
                headers={**student, "Idempotency-Key": "moderation-report-reply-again"},
                json={"reply_id": reply_id, "reason": "重复举报。"},
            )).status_code == 409

            topic_report = data(await client.post(
                f"/api/discussions/{topic_id}/report",
                headers={**other_student, "Idempotency-Key": "moderation-report-topic"},
                json={"reason": "需要管理员核对主题。"},
            ), 202)
            assert topic_report["content_type"] == "topic"
            student_hidden = await client.get(f"/api/discussions/{topic_id}", headers=student)
            assert student_hidden.status_code == 404

            queue_response = await client.get("/api/admin/moderation?page_size=10", headers=admin)
            queue = data(queue_response, 200)
            assert_no_sensitive_fields(queue_response)
            assert queue["total"] == 2
            assert {item["content_type"] for item in queue["items"]} == {"topic", "reply"}
            assert all(item["status"] == "pending_review" and item["topic_id"] == topic_id for item in queue["items"])
            assert data(await client.get("/api/admin/moderation?content_type=reply", headers=admin), 200)["total"] == 1
            assert data(await client.get("/api/admin/moderation?query=待审核", headers=admin), 200)["total"] == 2
            assert (await client.get("/api/admin/moderation?content_type=unknown", headers=admin)).status_code == 422
            assert (await client.get("/api/admin/moderation?page=0", headers=admin)).status_code == 422

            approved_reply = data(await client.patch(
                f"/api/admin/moderation/reply/{reply_id}",
                headers={**admin, "Idempotency-Key": "moderation-approve-reply", "X-Request-ID": "moderation-reply-request"},
                json={"decision": "approve", "reason": "内容核对通过。"},
            ), 200)
            assert approved_reply["decision"] == "approve" and approved_reply["status"] == "visible"
            approved_replay = data(await client.patch(
                f"/api/admin/moderation/reply/{reply_id}",
                headers={**admin, "Idempotency-Key": "moderation-approve-reply"},
                json={"decision": "approve", "reason": "内容核对通过。"},
            ), 200)
            assert approved_replay == approved_reply
            assert (await client.patch(
                f"/api/admin/moderation/reply/{reply_id}",
                headers={**admin, "Idempotency-Key": "moderation-approve-reply"},
                json={"decision": "reject", "reason": "不同请求复用幂等键。"},
            )).status_code == 409

            rejected_topic = data(await client.patch(
                f"/api/admin/moderation/topic/{topic_id}",
                headers={**admin, "Idempotency-Key": "moderation-reject-topic"},
                json={"decision": "reject", "reason": "主题不符合课程讨论规范。"},
            ), 200)
            assert rejected_topic["decision"] == "reject" and rejected_topic["status"] == "closed"
            assert data(await client.get("/api/admin/moderation", headers=admin), 200)["total"] == 0
            visible_detail = data(await client.get(f"/api/discussions/{topic_id}", headers=student), 200)
            assert len(visible_detail["replies"]) == 1 and visible_detail["replies"][0]["id"] == reply_id

            os.environ["MOCK_COURSE_ID"] = "2"
            os.environ["COURSE_ID"] = "2"
            assert data(await client.get("/api/admin/moderation", headers=admin), 200)["total"] == 0
            os.environ["MOCK_COURSE_ID"] = "1"
            os.environ["COURSE_ID"] = "1"

            audits = store.audit_logs(topic_id)
            assert any(item["action"] == "discussion.report" for item in audits)
            assert any(item["action"] == "discussion.moderate" and item["request_id"] == "moderation-reply-request" for item in store.audit_logs(reply_id))

    for name in ("COURSE_DB", "COURSE_MANIFEST", "GRAPH_BASELINE", "MOCK_AUTH_MODE", "MOCK_COURSE_ID", "COURSE_ID", "AGENT_UID_SALT"):
        os.environ.pop(name, None)
    print("ADMIN_MODERATION_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
