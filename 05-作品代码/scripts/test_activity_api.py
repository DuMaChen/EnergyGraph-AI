#!/usr/bin/env python3
"""ASGI contract tests for activity responses, lifecycle, and aggregate results."""

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
os.environ.setdefault("AGENT_UID_SALT", "activity-api-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def data(response: httpx.Response, expected: int) -> dict:
    assert response.status_code == expected, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    assert body.get("request_id"), body
    return body["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="activity-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, stable_uid, store
        from app.course_store import CourseStore

        student = {"x-dev-role": "student", "x-dev-user": "activity-student"}
        other_student = {"x-dev-role": "student", "x-dev-user": "activity-other"}
        quick_student_a = {"x-dev-role": "student", "x-dev-user": "quick-student-a"}
        quick_student_b = {"x-dev-role": "student", "x-dev-user": "quick-student-b"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "activity-teacher"}
        admin = {"x-dev-role": "admin", "x-dev-user": "activity-admin"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/activities", headers={"x-dev-role": "invalid"})).status_code == 401
            activities = data(await client.get("/api/activities", headers=student), 200)["items"]
            poll = next(item for item in activities if item["id"] == "activity-poll-1")
            assert poll["kind"] == "poll" and poll["has_responded"] is False
            detail = data(await client.get("/api/activities/activity-poll-1", headers=student), 200)
            assert {item["id"] for item in detail["options"]} == {"balance", "current", "communication"}
            assert detail["attempts_used"] == 0 and detail["can_respond"] is True and detail["next_attempt"] == 1
            hidden_results = data(await client.get("/api/activities/activity-poll-1/results", headers=student), 200)
            assert hidden_results["results_available"] is False
            assert hidden_results["total_responses"] == 0 and hidden_results["options"] == []

            invalid = await client.post(
                "/api/activities/activity-poll-1/responses",
                headers={**student, "Idempotency-Key": "activity-invalid"},
                json={"answers": ["not-an-option"]},
            )
            assert invalid.status_code == 422
            missing_key = await client.post("/api/activities/activity-poll-1/responses", headers=student, json={"answers": ["balance"]})
            assert missing_key.status_code == 422

            response = data(
                await client.post(
                    "/api/activities/activity-poll-1/responses",
                    headers={**student, "Idempotency-Key": "activity-poll-submit", "X-Request-ID": "activity-poll-submit-request"},
                    json={"answers": ["balance"]},
                ),
                201,
            )
            replay = data(
                await client.post(
                    "/api/activities/activity-poll-1/responses",
                    headers={**student, "Idempotency-Key": "activity-poll-submit"},
                    json={"answers": ["balance"]},
                ),
                200,
            )
            assert replay["id"] == response["id"]
            assert (await client.post(
                "/api/activities/activity-poll-1/responses",
                headers={**student, "Idempotency-Key": "activity-poll-submit"},
                json={"answers": ["current"]},
            )).status_code == 409
            assert (await client.post(
                "/api/activities/activity-poll-1/responses",
                headers={**student, "Idempotency-Key": "activity-poll-second"},
                json={"answers": ["current"]},
            )).status_code == 409
            assert store.audit_logs(response["id"])[0]["request_id"] == "activity-poll-submit-request"

            other_response = data(
                await client.post(
                    "/api/activities/activity-poll-1/responses",
                    headers={**other_student, "Idempotency-Key": "activity-other-poll"},
                    json={"answers": ["current"]},
                ),
                201,
            )
            results = data(await client.get("/api/activities/activity-poll-1/results", headers=student), 200)
            assert results["results_available"] is True
            assert results["total_responses"] == 2 and results["has_responded"] is True
            counts = {item["id"]: item["count"] for item in results["options"]}
            assert counts == {"balance": 1, "current": 1, "communication": 0}

            survey = data(await client.get("/api/activities/activity-survey-1", headers=student), 200)
            assert survey["kind"] == "survey"
            assert (await client.post(
                "/api/activities/activity-survey-1/responses",
                headers={**student, "Idempotency-Key": "activity-survey-duplicate"},
                json={"answers": ["control", "control"]},
            )).status_code == 422
            survey_response = data(await client.post(
                "/api/activities/activity-survey-1/responses",
                headers={**student, "Idempotency-Key": "activity-survey-submit"},
                json={"answers": ["topology", "control"]},
            ), 201)
            assert survey_response["answers"] == ["topology", "control"]

            assert (await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-checkin-invalid-options"},
                json={"kind": "checkin", "title": "无效签到", "body": "签到不接受自定义选项。", "options": [{"id": "x", "label": "X"}]},
            )).status_code == 422
            assert (await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-checkin-invalid-attempts"},
                json={"kind": "checkin", "title": "无效签到", "body": "签到只能记录一次。", "options": [], "max_attempts": 2},
            )).status_code == 422
            checkin = data(await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-checkin-create", "X-Request-ID": "activity-checkin-create-request"},
                json={"kind": "checkin", "title": "第 3 章课堂签到", "body": "请在课堂内完成签到。", "options": [], "status": "published", "max_attempts": 1},
            ), 201)
            checkin_id = checkin["id"]
            assert checkin["kind"] == "checkin" and checkin["options"] == []
            assert checkin["max_attempts"] == 1 and checkin["can_respond"] is False
            checkin_detail = data(await client.get(f"/api/activities/{checkin_id}", headers=student), 200)
            assert checkin_detail["can_respond"] is True and checkin_detail["next_attempt"] == 1
            hidden_checkin = data(await client.get(f"/api/activities/{checkin_id}/results", headers=other_student), 200)
            assert hidden_checkin["results_available"] is False and hidden_checkin["participants"] == []
            assert (await client.post(
                f"/api/activities/{checkin_id}/responses",
                headers={**student, "Idempotency-Key": "activity-checkin-empty"},
                json={"answers": [], "attempt": 1},
            )).status_code == 422
            checkin_response = data(await client.post(
                f"/api/activities/{checkin_id}/responses",
                headers={**student, "Idempotency-Key": "activity-checkin-submit", "X-Request-ID": "activity-checkin-submit-request"},
                json={"answers": ["present"], "attempt": 1},
            ), 201)
            checkin_replay = data(await client.post(
                f"/api/activities/{checkin_id}/responses",
                headers={**student, "Idempotency-Key": "activity-checkin-submit"},
                json={"answers": ["present"], "attempt": 1},
            ), 200)
            assert checkin_replay["id"] == checkin_response["id"]
            assert (await client.post(
                f"/api/activities/{checkin_id}/responses",
                headers={**student, "Idempotency-Key": "activity-checkin-duplicate"},
                json={"answers": ["present"], "attempt": 1},
            )).status_code == 409
            student_checkin_results = data(await client.get(f"/api/activities/{checkin_id}/results", headers=student), 200)
            assert student_checkin_results["total_responses"] == 1 and student_checkin_results["participants"] == []
            teacher_checkin_results = data(await client.get(f"/api/activities/{checkin_id}/results", headers=teacher), 200)
            assert teacher_checkin_results["options"] == [] and teacher_checkin_results["total_responses"] == 1
            assert teacher_checkin_results["participants"][0]["user_ref"] == stable_uid("activity-student")
            assert teacher_checkin_results["participants"][0]["submitted_at"]
            assert store.audit_logs(checkin_response["id"])[0]["request_id"] == "activity-checkin-submit-request"

            assert (await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-quick-invalid-options"},
                json={"kind": "quick_response", "title": "无效抢答", "body": "抢答不接受自定义选项。", "options": [{"id": "x", "label": "X"}]},
            )).status_code == 422
            assert (await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-quick-invalid-attempts"},
                json={"kind": "quick_response", "title": "无效抢答", "body": "抢答只允许首位响应。", "options": [], "max_attempts": 2},
            )).status_code == 422
            quick = data(await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-quick-create", "X-Request-ID": "activity-quick-create-request"},
                json={"kind": "quick_response", "title": "第 3 章课堂抢答", "body": "首位响应者获得回答机会。", "options": [], "status": "published", "max_attempts": 1},
            ), 201)
            quick_id = quick["id"]
            assert quick["kind"] == "quick_response" and quick["options"] == []
            assert quick["max_attempts"] == 1 and quick["can_reopen"] is False
            assert data(await client.get(f"/api/activities/{quick_id}", headers=quick_student_a), 200)["can_respond"] is True
            assert (await client.post(
                f"/api/activities/{quick_id}/responses",
                headers={**quick_student_a, "Idempotency-Key": "activity-quick-invalid-answer"},
                json={"answers": ["present"], "attempt": 1},
            )).status_code == 422
            assert (await client.post(
                f"/api/activities/{quick_id}/responses",
                headers={**quick_student_a, "Idempotency-Key": "activity-quick-invalid-attempt"},
                json={"answers": ["claim"], "attempt": 2},
            )).status_code == 422

            async def claim_quick(headers: dict[str, str], key: str) -> httpx.Response:
                return await client.post(
                    f"/api/activities/{quick_id}/responses",
                    headers={**headers, "Idempotency-Key": key, "X-Request-ID": f"{key}-request"},
                    json={"answers": ["claim"], "attempt": 1},
                )

            quick_claims = await asyncio.gather(
                claim_quick(quick_student_a, "activity-quick-claim-a"),
                claim_quick(quick_student_b, "activity-quick-claim-b"),
            )
            assert sorted(response.status_code for response in quick_claims) == [201, 409]
            winner_index = next(index for index, response in enumerate(quick_claims) if response.status_code == 201)
            winner_headers, loser_headers = (
                (quick_student_a, quick_student_b) if winner_index == 0 else (quick_student_b, quick_student_a)
            )
            winner_key = "activity-quick-claim-a" if winner_index == 0 else "activity-quick-claim-b"
            quick_response = data(quick_claims[winner_index], 201)
            loser_response = quick_claims[1 - winner_index]
            assert loser_response.json()["error"]["code"] == "quick_response_already_claimed"
            quick_replay = data(await claim_quick(winner_headers, winner_key), 200)
            assert quick_replay == quick_response
            reused = await client.post(
                f"/api/activities/{quick_id}/responses",
                headers={**winner_headers, "Idempotency-Key": winner_key},
                json={"answers": ["present"], "attempt": 1},
            )
            assert reused.status_code == 409 and reused.json()["error"]["code"] == "conflict"

            winner_detail = data(await client.get(f"/api/activities/{quick_id}", headers=winner_headers), 200)
            loser_detail = data(await client.get(f"/api/activities/{quick_id}", headers=loser_headers), 200)
            assert winner_detail["status"] == "closed" and winner_detail["has_responded"] is True
            assert winner_detail["can_respond"] is False and winner_detail["can_reopen"] is False
            assert loser_detail["status"] == "closed" and loser_detail["has_responded"] is False
            winner_results = data(await client.get(f"/api/activities/{quick_id}/results", headers=winner_headers), 200)
            loser_results = data(await client.get(f"/api/activities/{quick_id}/results", headers=loser_headers), 200)
            assert winner_results["has_responded"] is True and winner_results["participants"] == []
            assert loser_results["has_responded"] is False and loser_results["participants"] == []
            assert "user_ref" not in str(winner_results) and "user_ref" not in str(loser_results)
            expected_winner_ref = stable_uid(winner_headers["x-dev-user"])
            for staff_headers in (teacher, admin):
                staff_results = data(await client.get(f"/api/activities/{quick_id}/results", headers=staff_headers), 200)
                assert staff_results["total_responses"] == 1 and staff_results["options"] == []
                assert len(staff_results["participants"]) == 1
                assert set(staff_results["participants"][0]) == {"user_ref", "submitted_at"}
                assert staff_results["participants"][0]["user_ref"] == expected_winner_ref
            assert (await client.post(
                f"/api/teacher/activities/{quick_id}/reopen",
                headers={**teacher, "Idempotency-Key": "activity-quick-reopen-after-win"},
                json={},
            )).status_code == 409
            response_audit = store.audit_logs(quick_response["id"])
            activity_audit = store.audit_logs(quick_id)
            assert [item["action"] for item in response_audit] == ["activity.respond"]
            assert sum(item["action"] == "activity.quick_response.win" for item in activity_audit) == 1
            win_audit = next(item for item in activity_audit if item["action"] == "activity.quick_response.win")
            assert win_audit["request_id"] == f"{winner_key}-request"

            created = data(await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-teacher-create", "X-Request-ID": "activity-teacher-create-request"},
                json={"kind": "poll", "title": "教师创建活动", "body": "请选择一个选项。", "options": [{"id": "a", "label": "选项 A"}, {"id": "b", "label": "选项 B"}], "status": "published"},
            ), 201)
            created_replay = data(await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-teacher-create"},
                json={"kind": "poll", "title": "教师创建活动", "body": "请选择一个选项。", "options": [{"id": "a", "label": "选项 A"}, {"id": "b", "label": "选项 B"}], "status": "published"},
            ), 200)
            assert created_replay["id"] == created["id"]
            assert store.audit_logs(created["id"])[0]["request_id"] == "activity-teacher-create-request"
            assert (await client.post(
                "/api/teacher/activities",
                headers={**student, "Idempotency-Key": "activity-student-create"},
                json={"kind": "poll", "title": "越权活动", "body": "不可创建。", "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]},
            )).status_code == 403
            assert (await client.post(
                "/api/activities/activity-poll-1/responses",
                headers={**teacher, "Idempotency-Key": "activity-teacher-response"},
                json={"answers": ["balance"]},
            )).status_code == 403

            concurrent_payload = {
                "kind": "poll",
                "title": "并发幂等课堂活动",
                "body": "同一个幂等键只能创建一次。",
                "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                "status": "draft",
            }
            concurrent_headers = {
                **teacher,
                "Idempotency-Key": "activity-concurrent-create",
                "X-Request-ID": "activity-concurrent-create-request",
            }
            concurrent_responses = await asyncio.gather(
                client.post("/api/teacher/activities", headers=concurrent_headers, json=concurrent_payload),
                client.post("/api/teacher/activities", headers=concurrent_headers, json=concurrent_payload),
            )
            assert sorted(item.status_code for item in concurrent_responses) == [200, 201]
            concurrent_items = [data(item, item.status_code) for item in concurrent_responses]
            assert concurrent_items[0]["id"] == concurrent_items[1]["id"]
            assert len(store.audit_logs(concurrent_items[0]["id"])) == 1

            first_store = CourseStore()
            second_store = CourseStore()
            multi_instance_payload = {
                "kind": "poll",
                "title": "多实例原子幂等活动",
                "body": "两个 Store 实例只能提交一次。",
                "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                "status": "draft",
                "max_attempts": 1,
            }

            def create_from(target_store: CourseStore) -> tuple[dict, bool]:
                return target_store.create_activity_idempotent(
                    "multi-instance-teacher",
                    multi_instance_payload,
                    "/teacher/activities",
                    "activity-multi-instance-create",
                    "activity-multi-instance-request",
                    1,
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(create_from, target) for target in (first_store, second_store)]
                multi_instance_results = [future.result(timeout=5) for future in futures]
            assert multi_instance_results[0][0]["id"] == multi_instance_results[1][0]["id"]
            assert sorted(item[1] for item in multi_instance_results) == [False, True]
            multi_instance_id = multi_instance_results[0][0]["id"]
            assert len(store.audit_logs(multi_instance_id)) == 1
            with store.connect() as db:
                assert db.execute("SELECT COUNT(*) FROM activities WHERE title=?", ("多实例原子幂等活动",)).fetchone()[0] == 1

            def submit_checkin_from(target_store: CourseStore, key: str) -> tuple[str, str]:
                try:
                    result, _ = target_store.submit_activity_response_idempotent(
                        stable_uid("activity-concurrent-checkin"),
                        checkin_id,
                        ["present"],
                        1,
                        f"/activities/{checkin_id}/responses",
                        key,
                        {"activity_id": checkin_id, "answers": ["present"], "attempt": 1},
                        f"{key}-request",
                        1,
                    )
                    return "created", result["id"]
                except ValueError as exc:
                    return "conflict", str(exc)

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(submit_checkin_from, first_store, "activity-checkin-race-a"),
                    pool.submit(submit_checkin_from, second_store, "activity-checkin-race-b"),
                ]
                checkin_race = [future.result(timeout=5) for future in futures]
            assert sorted(item[0] for item in checkin_race) == ["conflict", "created"]
            assert next(item[1] for item in checkin_race if item[0] == "conflict") == "activity_already_answered"
            with store.connect() as db:
                race_uid = stable_uid("activity-concurrent-checkin")
                assert db.execute(
                    "SELECT COUNT(*) FROM activity_responses WHERE activity_id=? AND user_uid=?",
                    (checkin_id, race_uid),
                ).fetchone()[0] == 1

            quick_multi = store.create_activity(
                stable_uid("activity-teacher"),
                {
                    "kind": "quick_response",
                    "title": "多实例抢答",
                    "body": "两个 Store 只能产生一名胜出者。",
                    "options": [],
                    "status": "published",
                    "max_attempts": 1,
                },
                1,
                "activity-quick-multi-create",
            )

            def claim_quick_from(target_store: CourseStore, uid: str) -> tuple[str, str]:
                try:
                    result = target_store.submit_activity_response(
                        stable_uid(uid), quick_multi["id"], ["claim"], 1, 1, f"{uid}-request",
                    )
                    return "created", result["id"]
                except ValueError as exc:
                    return "conflict", str(exc)

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(claim_quick_from, first_store, "quick-multi-a"),
                    pool.submit(claim_quick_from, second_store, "quick-multi-b"),
                ]
                quick_multi_race = [future.result(timeout=5) for future in futures]
            assert sorted(item[0] for item in quick_multi_race) == ["conflict", "created"]
            assert next(item[1] for item in quick_multi_race if item[0] == "conflict") == "quick_response_already_claimed"
            with store.connect() as db:
                assert db.execute(
                    "SELECT COUNT(*) FROM activity_responses WHERE activity_id=?",
                    (quick_multi["id"],),
                ).fetchone()[0] == 1
                assert db.execute(
                    "SELECT status FROM activities WHERE id=?",
                    (quick_multi["id"],),
                ).fetchone()[0] == "closed"

            lifecycle = data(await client.post(
                "/api/teacher/activities",
                headers={**teacher, "Idempotency-Key": "activity-lifecycle-create"},
                json={
                    "kind": "poll",
                    "title": "课堂活动生命周期",
                    "body": "验证发布、重答、关闭和重新开放。",
                    "options": [{"id": "a", "label": "选项 A"}, {"id": "b", "label": "选项 B"}],
                    "status": "draft",
                    "max_attempts": 2,
                },
            ), 201)
            lifecycle_id = lifecycle["id"]
            assert lifecycle["status"] == "draft" and lifecycle["max_attempts"] == 2
            assert (await client.get(f"/api/activities/{lifecycle_id}", headers=student)).status_code == 404

            publish_headers = {
                **teacher,
                "Idempotency-Key": "activity-lifecycle-publish",
                "X-Request-ID": "activity-lifecycle-publish-request",
            }
            published = data(await client.post(
                f"/api/teacher/activities/{lifecycle_id}/publish",
                headers=publish_headers,
                json={},
            ), 200)
            publish_replay = data(await client.post(
                f"/api/teacher/activities/{lifecycle_id}/publish",
                headers=publish_headers,
                json={},
            ), 200)
            assert published["status"] == "published" and publish_replay["id"] == lifecycle_id
            assert (await client.post(
                f"/api/teacher/activities/{lifecycle_id}/reopen",
                headers={**teacher, "Idempotency-Key": "activity-invalid-reopen"},
                json={},
            )).status_code == 409
            assert (await client.post(
                f"/api/teacher/activities/{lifecycle_id}/close",
                headers={**student, "Idempotency-Key": "activity-student-close"},
                json={},
            )).status_code == 403

            first_attempt = data(await client.post(
                f"/api/activities/{lifecycle_id}/responses",
                headers={**student, "Idempotency-Key": "activity-lifecycle-attempt-1"},
                json={"answers": ["a"], "attempt": 1},
            ), 201)
            assert first_attempt["attempt"] == 1
            after_first = data(await client.get(f"/api/activities/{lifecycle_id}", headers=student), 200)
            assert after_first["attempts_used"] == 1 and after_first["can_respond"] is True and after_first["next_attempt"] == 2
            assert (await client.post(
                f"/api/activities/{lifecycle_id}/responses",
                headers={**student, "Idempotency-Key": "activity-lifecycle-skip-attempt"},
                json={"answers": ["b"], "attempt": 3},
            )).status_code == 422
            second_attempt = data(await client.post(
                f"/api/activities/{lifecycle_id}/responses",
                headers={**student, "Idempotency-Key": "activity-lifecycle-attempt-2"},
                json={"answers": ["b"], "attempt": 2},
            ), 201)
            assert second_attempt["attempt"] == 2
            exhausted = data(await client.get(f"/api/activities/{lifecycle_id}", headers=student), 200)
            assert exhausted["attempts_used"] == 2 and exhausted["can_respond"] is False and exhausted["next_attempt"] is None
            latest_results = data(await client.get(f"/api/activities/{lifecycle_id}/results", headers=student), 200)
            assert latest_results["total_responses"] == 1
            assert {item["id"]: item["count"] for item in latest_results["options"]} == {"a": 0, "b": 1}

            close_headers = {
                **teacher,
                "Idempotency-Key": "activity-lifecycle-close",
                "X-Request-ID": "activity-lifecycle-close-request",
            }
            closed = data(await client.post(
                f"/api/teacher/activities/{lifecycle_id}/close",
                headers=close_headers,
                json={},
            ), 200)
            close_replay = data(await client.post(
                f"/api/teacher/activities/{lifecycle_id}/close",
                headers=close_headers,
                json={},
            ), 200)
            assert closed["status"] == "closed" and close_replay["status"] == "closed"
            closed_detail = data(await client.get(f"/api/activities/{lifecycle_id}", headers=other_student), 200)
            assert closed_detail["can_respond"] is False and closed_detail["next_attempt"] is None
            assert (await client.post(
                f"/api/activities/{lifecycle_id}/responses",
                headers={**other_student, "Idempotency-Key": "activity-lifecycle-closed-response"},
                json={"answers": ["a"], "attempt": 1},
            )).status_code == 409
            closed_results = data(await client.get(f"/api/activities/{lifecycle_id}/results", headers=other_student), 200)
            assert closed_results["results_available"] is True and closed_results["total_responses"] == 1

            reopened = data(await client.post(
                f"/api/teacher/activities/{lifecycle_id}/reopen",
                headers={**teacher, "Idempotency-Key": "activity-lifecycle-reopen"},
                json={},
            ), 200)
            assert reopened["status"] == "published"
            closed_again = data(await client.post(
                f"/api/teacher/activities/{lifecycle_id}/close",
                headers={**teacher, "Idempotency-Key": "activity-lifecycle-close-again"},
                json={},
            ), 200)
            assert closed_again["status"] == "closed"
            audit = store.audit_logs(lifecycle_id)
            assert {"activity.publish", "activity.close", "activity.reopen"}.issubset({item["action"] for item in audit})
            assert sum(item["action"] == "activity.close" for item in audit) == 2
            assert next(item for item in audit if item["action"] == "activity.publish")["request_id"] == "activity-lifecycle-publish-request"

            other_course = store.create_activity(
                "course-two-teacher",
                {
                    "kind": "poll",
                    "title": "其他课程活动",
                    "body": "不得跨课程访问。",
                    "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                    "status": "draft",
                    "max_attempts": 1,
                },
                course_id=2,
            )
            assert (await client.post(
                f"/api/teacher/activities/{other_course['id']}/publish",
                headers={**teacher, "Idempotency-Key": "activity-cross-course-publish"},
                json={},
            )).status_code == 404
            assert (await client.get(f"/api/activities/{other_course['id']}/results", headers=student)).status_code == 404
            assert (await client.post(
                f"/api/activities/{other_course['id']}/responses",
                headers={**student, "Idempotency-Key": "activity-cross-course-response"},
                json={"answers": ["a"], "attempt": 1},
            )).status_code == 404

            legacy_gap = store.create_activity(
                "activity-teacher",
                {
                    "kind": "poll",
                    "title": "旧库尝试次数兼容",
                    "body": "验证非连续历史尝试号。",
                    "options": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                    "status": "published",
                    "max_attempts": 3,
                },
            )
            with store.connect() as db:
                db.execute(
                    "INSERT INTO activity_responses(id,activity_id,user_uid,attempt,answers_json) VALUES(?,?,?,?,?)",
                    ("legacy-attempt-gap", legacy_gap["id"], stable_uid("activity-other"), 2, '["a"]'),
                )
                db.commit()
            legacy_detail = data(await client.get(f"/api/activities/{legacy_gap['id']}", headers=other_student), 200)
            assert legacy_detail["attempts_used"] == 2
            assert legacy_detail["can_respond"] is True and legacy_detail["next_attempt"] == 3
            legacy_third = data(await client.post(
                f"/api/activities/{legacy_gap['id']}/responses",
                headers={**other_student, "Idempotency-Key": "activity-legacy-attempt-3"},
                json={"answers": ["b"], "attempt": 3},
            ), 201)
            assert legacy_third["attempt"] == 3

    print("ACTIVITY_API_OK cases=activity_visibility,checkin,checkin_participant_privacy,checkin_multi_instance_race,quick_response,quick_response_privacy,quick_response_race,quick_response_terminal_lifecycle,lifecycle,sequential_attempts,legacy_attempt_gap,latest_results,course_scope,atomic_idempotency,multi_instance_atomic_idempotency,audit")


if __name__ == "__main__":
    asyncio.run(run())
