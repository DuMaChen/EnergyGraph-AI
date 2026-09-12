#!/usr/bin/env python3
"""ASGI contract tests for discussions, moderation and notifications."""

from __future__ import annotations

import asyncio
import concurrent.futures
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "social-api-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def data(response: httpx.Response, expected: int) -> dict:
    assert response.status_code == expected, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="social-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.course_store import CourseStore
        from app.main import app, store

        student = {"x-dev-role": "student", "x-dev-user": "social-student"}
        other_student = {"x-dev-role": "student", "x-dev-user": "social-other"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "social-teacher"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            dangerous = await client.post("/api/discussions", headers={**student, "Idempotency-Key": "social-xss"}, json={"title": "<script>alert(1)</script>", "body": "危险"})
            assert dangerous.status_code == 422
            created = data(await client.post("/api/discussions", headers={**student, "Idempotency-Key": "social-topic"}, json={"title": "如何理解并网控制？", "body": "想和同学讨论储能变流器的控制目标。"}), 201)
            topic_id = created["id"]
            replay = data(await client.post("/api/discussions", headers={**student, "Idempotency-Key": "social-topic"}, json={"title": "如何理解并网控制？", "body": "想和同学讨论储能变流器的控制目标。"}), 200)
            assert replay["id"] == topic_id
            assert (await client.post(f"/api/discussions/{topic_id}/replies", headers={**student, "Idempotency-Key": "social-reply-xss"}, json={"body": "<img src=x onerror=alert(1)>"})).status_code == 422
            reply = data(await client.post(f"/api/discussions/{topic_id}/replies", headers={**other_student, "Idempotency-Key": "social-reply"}, json={"body": "可以从功率平衡和约束条件两个角度分析。"}), 201)
            reply_replay = data(await client.post(f"/api/discussions/{topic_id}/replies", headers={**other_student, "Idempotency-Key": "social-reply"}, json={"body": "可以从功率平衡和约束条件两个角度分析。"}), 200)
            assert reply_replay["id"] == reply["id"]

            listing = data(await client.get("/api/discussions?query=并网", headers=student), 200)
            assert listing["total"] == 1 and listing["items"][0]["reply_count"] == 1
            detail = data(await client.get(f"/api/discussions/{topic_id}", headers=student), 200)
            assert len(detail["replies"]) == 1 and detail["can_moderate"] is False
            assert (await client.patch(f"/api/discussions/{topic_id}", headers={**student, "Idempotency-Key": "social-student-moderate"}, json={"pinned": True})).status_code == 403

            moderated = data(await client.patch(f"/api/discussions/{topic_id}", headers={**teacher, "Idempotency-Key": "social-moderate"}, json={"pinned": True, "status": "solved", "reason": "教师确认问题已解决"}), 200)
            assert moderated["pinned"] is True and moderated["status"] == "solved"
            assert len(store.audit_logs(topic_id)) >= 2
            closed = data(await client.patch(f"/api/discussions/{topic_id}", headers={**teacher, "Idempotency-Key": "social-close"}, json={"status": "closed", "reason": "讨论归档"}), 200)
            assert closed["status"] == "closed"
            assert (await client.post(f"/api/discussions/{topic_id}/replies", headers={**other_student, "Idempotency-Key": "social-closed-reply"}, json={"body": "补充回复"})).status_code == 409

            all_notice = data(await client.post("/api/teacher/notifications", headers={**teacher, "Idempotency-Key": "notice-all"}, json={"title": "课程公告", "body": "本周完成章节练习。", "audience": "course_all"}), 201)
            student_notice = data(await client.post("/api/teacher/notifications", headers={**teacher, "Idempotency-Key": "notice-student"}, json={"title": "学生提醒", "body": "请检查作业草稿。", "audience": "course_students"}), 201)
            teacher_notice = data(await client.post("/api/teacher/notifications", headers={**teacher, "Idempotency-Key": "notice-teacher"}, json={"title": "教师提醒", "body": "请完成批改。", "audience": "course_teachers"}), 201)
            course_two_notice = store.create_notification("teacher-course-two", "第二课程公告", "不得泄漏到课程一", "course_students", course_id=2)
            assert (await client.post("/api/teacher/notifications", headers={**student, "Idempotency-Key": "notice-student-forbidden"}, json={"title": "越权", "body": "不可发布"})).status_code == 403
            student_notifications = data(await client.get("/api/notifications", headers=student), 200)
            teacher_notifications = data(await client.get("/api/notifications", headers=teacher), 200)
            assert {item["id"] for item in student_notifications["items"]} == {all_notice["id"], student_notice["id"]}
            assert {item["id"] for item in teacher_notifications["items"]} == {all_notice["id"], teacher_notice["id"]}
            assert student_notifications["total"] == 2 and student_notifications["unread_count"] == 2
            page_one = data(await client.get("/api/notifications?page=1&page_size=1", headers=student), 200)
            page_two = data(await client.get("/api/notifications?page=2&page_size=1", headers=student), 200)
            assert page_one["page"] == 1 and page_one["page_size"] == 1 and page_one["total"] == 2
            assert {page_one["items"][0]["id"], page_two["items"][0]["id"]} == {all_notice["id"], student_notice["id"]}
            focused = data(await client.get(f"/api/notifications?page=1&page_size=1&focus_id={page_two['items'][0]['id']}", headers=student), 200)
            assert focused["page"] == 2 and focused["focus_found"] is True
            assert focused["focused_id"] == page_two["items"][0]["id"]
            assert focused["items"][0]["id"] == focused["focused_id"] and focused["unread_count"] == 2
            hidden_focuses = [
                data(await client.get(f"/api/notifications?page=1&page_size=1&focus_id={teacher_notice['id']}", headers=student), 200),
                data(await client.get(f"/api/notifications?page=1&page_size=1&focus_id={course_two_notice['id']}", headers=student), 200),
                data(await client.get("/api/notifications?page=1&page_size=1&focus_id=notice-does-not-exist", headers=student), 200),
            ]
            for hidden_focus in hidden_focuses:
                assert hidden_focus["focus_found"] is False and hidden_focus["focused_id"] is None
                assert hidden_focus["page"] == 1 and hidden_focus["items"] == page_one["items"]
            assert (await client.get("/api/notifications?page=0", headers=student)).status_code == 422
            assert (await client.get("/api/notifications?page=1000001", headers=student)).status_code == 422
            assert (await client.get("/api/notifications?page_size=101", headers=student)).status_code == 422
            assert (await client.get("/api/notifications?focus_id=invalid%20focus", headers=student)).status_code == 422
            read = data(await client.put(f"/api/notifications/{student_notice['id']}/read", headers={**student, "Idempotency-Key": "notice-read"}, json={}), 200)
            assert read["is_read"] is True and read["unread_count"] == 1
            read_replay = data(await client.put(f"/api/notifications/{student_notice['id']}/read", headers={**student, "Idempotency-Key": "notice-read"}, json={}), 200)
            assert read_replay == read
            assert (await client.put(f"/api/notifications/{teacher_notice['id']}/read", headers={**student, "Idempotency-Key": "notice-read-hidden"}, json={})).status_code == 404
            unread = data(await client.get("/api/notifications?unread_only=true", headers=student), 200)
            assert unread["total"] == 1 and unread["unread_count"] == 1 and unread["items"][0]["id"] == all_notice["id"]
            assert (await client.put("/api/notifications/read-all", headers=student, json={})).status_code == 422
            read_all = data(await client.put("/api/notifications/read-all", headers={**student, "Idempotency-Key": "notice-read-all"}, json={}), 200)
            assert read_all == {"marked_count": 1, "unread_count": 0}
            read_all_replay = data(await client.put("/api/notifications/read-all", headers={**student, "Idempotency-Key": "notice-read-all"}, json={}), 200)
            assert read_all_replay == read_all
            assert (await client.put("/api/notifications/read-all", headers={"x-dev-role": "teacher", "x-dev-user": "social-student", "Idempotency-Key": "notice-read-all"}, json={})).status_code == 409
            after_read_all = data(await client.get("/api/notifications", headers=student), 200)
            assert after_read_all["unread_count"] == 0 and all(item["is_read"] for item in after_read_all["items"])
            assert data(await client.get("/api/notifications?unread_only=true", headers=student), 200)["total"] == 0
            assert data(await client.get("/api/notifications", headers=other_student), 200)["unread_count"] == 2
            assert store.count_unread_notifications("course-two-student", "student", course_id=2) == 1
            assert course_two_notice["id"] not in {item["id"] for item in after_read_all["items"]}
            assert any(item["action"] == "notification.read" for item in store.audit_logs(student_notice["id"]))
            assert any(item["action"] == "notification.read_all" and item["request_id"] for item in store.audit_logs("*"))

            first_store = CourseStore()
            second_store = CourseStore()

            def create_notification(target_store: CourseStore) -> tuple[dict, bool]:
                return target_store.create_notification_idempotent(
                    "notification-multi-instance-teacher",
                    "多实例通知",
                    "同一幂等键只能发布一次。",
                    "course_students",
                    "notification-multi-instance-create",
                    "notification-create-request",
                    1,
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                create_results = [future.result(timeout=5) for future in [pool.submit(create_notification, target) for target in (first_store, second_store)]]
            assert create_results[0][0]["id"] == create_results[1][0]["id"]
            assert sorted(item[1] for item in create_results) == [False, True]
            concurrent_notice_id = create_results[0][0]["id"]

            def read_notification(target_store: CourseStore) -> tuple[dict | None, bool]:
                return target_store.mark_notification_read_idempotent(
                    "notification-multi-instance-student",
                    "student",
                    concurrent_notice_id,
                    "notification-multi-instance-read",
                    "notification-read-request",
                    1,
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                read_results = [future.result(timeout=5) for future in [pool.submit(read_notification, target) for target in (first_store, second_store)]]
            assert read_results[0][0] == read_results[1][0]
            assert sorted(item[1] for item in read_results) == [False, True]

            def read_all_notifications(target_store: CourseStore) -> tuple[dict, bool]:
                return target_store.mark_all_notifications_read_idempotent(
                    "notification-multi-instance-bulk-student",
                    "student",
                    "notification-multi-instance-read-all",
                    "notification-read-all-request",
                    1,
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                read_all_results = [future.result(timeout=5) for future in [pool.submit(read_all_notifications, target) for target in (first_store, second_store)]]
            assert read_all_results[0][0] == read_all_results[1][0]
            assert sorted(item[1] for item in read_all_results) == [False, True]
            with store.connect() as db:
                assert db.execute("SELECT COUNT(*) FROM notifications WHERE title=?", ("多实例通知",)).fetchone()[0] == 1
                assert db.execute("SELECT COUNT(*) FROM audit_log WHERE action='notification.create' AND object_id=?", (concurrent_notice_id,)).fetchone()[0] == 1
                assert db.execute("SELECT COUNT(*) FROM audit_log WHERE action='notification.read' AND object_id=?", (concurrent_notice_id,)).fetchone()[0] == 1
                assert db.execute("SELECT COUNT(*) FROM audit_log WHERE action='notification.read_all' AND request_id='notification-read-all-request'").fetchone()[0] == 1

            try:
                store.notification_page("invalid-role-user", "unknown", course_id=1)
            except PermissionError:
                pass
            else:  # pragma: no cover - fail closed is mandatory
                raise AssertionError("unknown notification role did not fail closed")

    print("SOCIAL_API_OK cases=audience,course_scope,sql_pagination,unread_count,atomic_idempotency,multi_instance_idempotency,audit")


if __name__ == "__main__":
    asyncio.run(run())
