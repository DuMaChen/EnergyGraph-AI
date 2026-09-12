#!/usr/bin/env python3
"""ASGI contract tests for classroom roster, random selection, and group tasks."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parents[1]


def data(response: httpx.Response, expected: int) -> dict[str, Any]:
    assert response.status_code == expected, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    assert body.get("request_id"), body
    assert isinstance(body.get("data"), dict), body
    return body["data"]


def error(response: httpx.Response, expected: int, code: str) -> None:
    assert response.status_code == expected, response.text
    body = response.json()
    assert body.get("status") == "error", body
    assert body.get("request_id"), body
    assert body.get("error", {}).get("code") == code, body


def contains_key(value: Any, target: str) -> bool:
    if isinstance(value, dict):
        return target in value or any(contains_key(item, target) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, target) for item in value)
    return False


def assert_no_raw_ids(value: Any, raw_ids: set[str]) -> None:
    serialized = json.dumps(value, ensure_ascii=False)
    assert all(raw_id not in serialized for raw_id in raw_ids), serialized


def assert_staff_random_state(
    state: dict[str, Any],
    activity_id: str,
    expected_refs: set[str],
) -> dict[str, Any]:
    assert state["activity_id"] == activity_id
    assert state["kind"] == "random_selection"
    assert isinstance(state["history"], list)
    latest = state["selection"]
    assert isinstance(latest, dict)
    assert {"cycle", "sequence", "user_ref", "display_name", "selected_at"}.issubset(latest)
    assert latest["cycle"] >= 1 and latest["sequence"] >= 1
    assert latest["user_ref"] in expected_refs
    assert latest["display_name"] and latest["selected_at"]
    return latest


def assert_staff_groups(
    state: dict[str, Any],
    activity_id: str,
    revision: int,
    expected_refs: set[str],
    expected_names: set[str],
) -> dict[str, dict[str, Any]]:
    assert state["activity_id"] == activity_id
    assert state["kind"] == "group_task"
    assert state["revision"] == revision
    groups = state["groups"]
    assert len(groups) == len(expected_names)
    assert {group["name"] for group in groups} == expected_names
    sizes = [len(group["members"]) for group in groups]
    assert max(sizes) - min(sizes) <= 1
    members = [member for group in groups for member in group["members"]]
    refs = [member["user_ref"] for member in members]
    assert len(refs) == len(expected_refs)
    assert len(set(refs)) == len(refs)
    assert set(refs) == expected_refs
    assert all(member["display_name"] for member in members)
    assert revision in {item["revision"] for item in state["available_revisions"]}
    return {member["user_ref"]: group for group in groups for member in group["members"]}


async def create_activity(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    key: str,
    kind: str,
    title: str,
    options: list[dict[str, str]],
) -> dict[str, Any]:
    return data(
        await client.post(
            "/api/teacher/activities",
            headers={**headers, "Idempotency-Key": key, "X-Request-ID": f"{key}-request"},
            json={
                "kind": kind,
                "title": title,
                "body": f"{title}契约测试。",
                "options": options,
                "status": "published",
                "max_attempts": 1,
            },
        ),
        201,
    )


async def run() -> None:
    raw_students = [f"classroom-student-{index}" for index in range(1, 6)]
    display_names = {raw_id: f"课堂学生 {index}" for index, raw_id in enumerate(raw_students, 1)}
    fixture = {
        "users": [
            *[
                {
                    "id": raw_id,
                    "display_name": display_names[raw_id],
                    "role": "student",
                    "course_id": 1,
                    "status": "active",
                }
                for raw_id in raw_students
            ],
            {
                "id": "classroom-student-suspended",
                "display_name": "停用学生",
                "role": "student",
                "course_id": 1,
                "status": "suspended",
            },
            {
                "id": "classroom-student-unknown",
                "display_name": "状态未知学生",
                "role": "student",
                "course_id": 1,
                "status": "unknown",
            },
            {
                "id": "classroom-teacher",
                "display_name": "课堂教师",
                "role": "teacher",
                "course_id": 1,
                "status": "active",
            },
            {
                "id": "classroom-admin",
                "display_name": "课堂管理员",
                "role": "admin",
                "course_id": 1,
                "status": "active",
            },
            {
                "id": "classroom-other-course-student",
                "display_name": "其他课程学生",
                "role": "student",
                "course_id": 2,
                "status": "active",
            },
        ],
        "courses": [
            {"id": 1, "name": "课堂事件课程", "status": "active"},
            {"id": 2, "name": "其他课程", "status": "active"},
        ],
    }

    with tempfile.TemporaryDirectory(prefix="classroom-events-api-") as directory:
        os.environ.update(
            {
                "COURSE_DB": str(Path(directory) / "course.db"),
                "COURSE_MANIFEST": str(ROOT / "course-data/normalized/manifest.json"),
                "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
                "MOCK_AUTH_MODE": "true",
                "MOCK_WORKFLOW_MODE": "true",
                "MOCK_COURSE_ID": "1",
                "COURSE_ID": "1",
                "AGENT_UID_SALT": "classroom-events-api-test-only",
                "MOCK_ADMIN_DIRECTORY_JSON": json.dumps(fixture, ensure_ascii=False),
                "MOODLE_ADMIN_DIRECTORY_URL": "",
            }
        )
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, stable_uid, store

        teacher = {"x-dev-role": "teacher", "x-dev-user": "classroom-teacher"}
        admin = {"x-dev-role": "admin", "x-dev-user": "classroom-admin"}
        student_headers = {
            raw_id: {"x-dev-role": "student", "x-dev-user": raw_id}
            for raw_id in raw_students
        }
        student = student_headers[raw_students[0]]
        stable_refs = {raw_id: stable_uid(raw_id) for raw_id in raw_students}
        expected_refs = set(stable_refs.values())
        all_raw_ids = set(raw_students) | {
            "classroom-student-suspended",
            "classroom-student-unknown",
            "classroom-other-course-student",
        }

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            error(await client.get("/api/teacher/classroom-roster", headers=student), 403, "forbidden")
            for staff in (teacher, admin):
                roster = data(await client.get("/api/teacher/classroom-roster", headers=staff), 200)
                assert roster["configured"] is True
                assert len(roster["items"]) == len(raw_students)
                assert {item["user_ref"] for item in roster["items"]} == expected_refs
                assert {item["display_name"] for item in roster["items"]} == set(display_names.values())
                assert all(set(item) == {"user_ref", "display_name"} for item in roster["items"])
                assert_no_raw_ids(roster, all_raw_ids)

            os.environ.pop("MOCK_ADMIN_DIRECTORY_JSON")
            unconfigured = data(await client.get("/api/teacher/classroom-roster", headers=teacher), 200)
            assert unconfigured["configured"] is False
            assert unconfigured["items"] == []
            assert unconfigured["message"]

            unavailable_random = await create_activity(
                client,
                teacher,
                "classroom-unconfigured-random-create",
                "random_selection",
                "未配置花名册随机选人",
                [],
            )
            unavailable_random_response = await client.post(
                f"/api/teacher/activities/{unavailable_random['id']}/random-select",
                headers={**teacher, "Idempotency-Key": "classroom-unconfigured-random-select"},
                json={},
            )
            error(unavailable_random_response, 503, "classroom_roster_unavailable")

            unavailable_groups = await create_activity(
                client,
                teacher,
                "classroom-unconfigured-groups-create",
                "group_task",
                "未配置花名册分组",
                [{"id": "one", "label": "第一组"}, {"id": "two", "label": "第二组"}],
            )
            unavailable_groups_response = await client.post(
                f"/api/teacher/activities/{unavailable_groups['id']}/groups/generate",
                headers={**teacher, "Idempotency-Key": "classroom-unconfigured-groups-generate"},
                json={},
            )
            error(unavailable_groups_response, 503, "classroom_roster_unavailable")
            with store.connect() as db:
                assert db.execute(
                    "SELECT COUNT(*) FROM random_selection_results WHERE activity_id=?",
                    (unavailable_random["id"],),
                ).fetchone()[0] == 0
                assert db.execute(
                    "SELECT COUNT(*) FROM group_task_revisions WHERE activity_id=?",
                    (unavailable_groups["id"],),
                ).fetchone()[0] == 0
            os.environ["MOCK_ADMIN_DIRECTORY_JSON"] = json.dumps(fixture, ensure_ascii=False)

            random_activity = await create_activity(
                client,
                teacher,
                "classroom-random-create",
                "random_selection",
                "课堂随机选人",
                [],
            )
            random_id = random_activity["id"]
            assert random_activity["kind"] == "random_selection"
            assert random_activity["options"] == [] and random_activity["can_respond"] is False
            error(
                await client.post(
                    f"/api/teacher/activities/{random_id}/random-select",
                    headers={**student, "Idempotency-Key": "classroom-random-student-forbidden"},
                    json={},
                ),
                403,
                "forbidden",
            )
            invalid_response = await client.post(
                f"/api/activities/{random_id}/responses",
                headers={**student, "Idempotency-Key": "classroom-random-student-response"},
                json={"answers": ["claim"], "attempt": 1},
            )
            assert invalid_response.status_code == 422, invalid_response.text

            random_headers = {
                **admin,
                "Idempotency-Key": "classroom-random-select-1",
                "X-Request-ID": "classroom-random-select-1-request",
            }
            first_pair = await asyncio.gather(
                client.post(
                    f"/api/teacher/activities/{random_id}/random-select",
                    headers=random_headers,
                    json={},
                ),
                client.post(
                    f"/api/teacher/activities/{random_id}/random-select",
                    headers=random_headers,
                    json={},
                ),
            )
            assert sorted(response.status_code for response in first_pair) == [200, 201]
            first_states = [data(response, response.status_code) for response in first_pair]
            assert first_states[0] == first_states[1]
            first = assert_staff_random_state(first_states[0], random_id, expected_refs)
            assert first["cycle"] == 1 and first["sequence"] == 1
            with store.connect() as db:
                assert db.execute(
                    "SELECT COUNT(*) FROM random_selection_results WHERE activity_id=?",
                    (random_id,),
                ).fetchone()[0] == 1
                selection_id = db.execute(
                    "SELECT id FROM random_selection_results WHERE activity_id=? AND sequence=1",
                    (random_id,),
                ).fetchone()["id"]
            selection_audit = store.audit_logs(selection_id)
            assert [item["action"] for item in selection_audit] == ["activity.random_select"]
            assert selection_audit[0]["request_id"] == "classroom-random-select-1-request"

            cycle_one = [first]
            for sequence in range(2, len(raw_students) + 1):
                selected = data(
                    await client.post(
                        f"/api/teacher/activities/{random_id}/random-select",
                        headers={
                            **teacher,
                            "Idempotency-Key": f"classroom-random-select-{sequence}",
                            "X-Request-ID": f"classroom-random-select-{sequence}-request",
                        },
                        json={},
                    ),
                    201,
                )
                latest = assert_staff_random_state(selected, random_id, expected_refs)
                assert latest["cycle"] == 1 and latest["sequence"] == sequence
                cycle_one.append(latest)
            assert {item["user_ref"] for item in cycle_one} == expected_refs
            assert len({item["user_ref"] for item in cycle_one}) == len(raw_students)

            cycle_two_first_state = data(
                await client.post(
                    f"/api/teacher/activities/{random_id}/random-select",
                    headers={**teacher, "Idempotency-Key": "classroom-random-select-cycle-2-first"},
                    json={},
                ),
                201,
            )
            cycle_two_first = assert_staff_random_state(cycle_two_first_state, random_id, expected_refs)
            assert cycle_two_first["cycle"] == 2
            assert cycle_two_first["sequence"] == len(raw_students) + 1

            data(
                await client.post(
                    f"/api/teacher/activities/{random_id}/close",
                    headers={**teacher, "Idempotency-Key": "classroom-random-close"},
                    json={},
                ),
                200,
            )
            error(
                await client.post(
                    f"/api/teacher/activities/{random_id}/random-select",
                    headers={**teacher, "Idempotency-Key": "classroom-random-closed-select"},
                    json={},
                ),
                409,
                "activity_not_open",
            )
            data(
                await client.post(
                    f"/api/teacher/activities/{random_id}/reopen",
                    headers={**teacher, "Idempotency-Key": "classroom-random-reopen"},
                    json={},
                ),
                200,
            )
            continued_state = data(
                await client.post(
                    f"/api/teacher/activities/{random_id}/random-select",
                    headers={**teacher, "Idempotency-Key": "classroom-random-after-reopen"},
                    json={},
                ),
                201,
            )
            continued = assert_staff_random_state(continued_state, random_id, expected_refs)
            assert continued["cycle"] == 2
            assert continued["sequence"] == len(raw_students) + 2
            assert continued["user_ref"] != cycle_two_first["user_ref"]

            for staff in (teacher, admin):
                staff_state = data(
                    await client.get(f"/api/activities/{random_id}/random-selection", headers=staff),
                    200,
                )
                assert_staff_random_state(staff_state, random_id, expected_refs)
                assert len(staff_state["history"]) == len(raw_students) + 2
                assert {record["user_ref"] for record in staff_state["history"]} == expected_refs
                assert_no_raw_ids(staff_state, all_raw_ids)

            selected_raw_id = next(
                raw_id for raw_id, user_ref in stable_refs.items() if user_ref == continued["user_ref"]
            )
            for raw_id, headers in student_headers.items():
                student_state = data(
                    await client.get(f"/api/activities/{random_id}/random-selection", headers=headers),
                    200,
                )
                assert student_state["activity_id"] == random_id
                assert student_state["kind"] == "random_selection"
                assert "history" not in student_state
                assert student_state["selection"]["display_name"] == continued["display_name"]
                assert student_state["selection"]["is_me"] is (raw_id == selected_raw_id)
                assert not contains_key(student_state, "user_ref")
                assert_no_raw_ids(student_state, all_raw_ids)

            group_options = [
                {"id": "alpha", "label": "甲组"},
                {"id": "beta", "label": "乙组"},
                {"id": "gamma", "label": "丙组"},
            ]
            group_names = {item["label"] for item in group_options}
            group_activity = await create_activity(
                client,
                teacher,
                "classroom-groups-create",
                "group_task",
                "课堂分组任务",
                group_options,
            )
            group_id = group_activity["id"]
            assert group_activity["kind"] == "group_task"
            assert {item["label"] for item in group_activity["options"]} == group_names
            error(
                await client.post(
                    f"/api/teacher/activities/{group_id}/groups/generate",
                    headers={**student, "Idempotency-Key": "classroom-groups-student-forbidden"},
                    json={},
                ),
                403,
                "forbidden",
            )

            group_headers = {
                **teacher,
                "Idempotency-Key": "classroom-groups-generate-1",
                "X-Request-ID": "classroom-groups-generate-1-request",
            }
            first_group_pair = await asyncio.gather(
                client.post(
                    f"/api/teacher/activities/{group_id}/groups/generate",
                    headers=group_headers,
                    json={},
                ),
                client.post(
                    f"/api/teacher/activities/{group_id}/groups/generate",
                    headers=group_headers,
                    json={},
                ),
            )
            assert sorted(response.status_code for response in first_group_pair) == [200, 201]
            first_group_states = [data(response, response.status_code) for response in first_group_pair]
            assert first_group_states[0] == first_group_states[1]
            assert_staff_groups(
                first_group_states[0], group_id, 1, expected_refs, group_names
            )
            with store.connect() as db:
                assert db.execute(
                    "SELECT COUNT(*) FROM group_task_revisions WHERE activity_id=?",
                    (group_id,),
                ).fetchone()[0] == 1
                first_revision_id = db.execute(
                    "SELECT id FROM group_task_revisions WHERE activity_id=? AND revision=1",
                    (group_id,),
                ).fetchone()["id"]
            group_audit = store.audit_logs(first_revision_id)
            assert [item["action"] for item in group_audit] == ["activity.groups.generate"]
            assert group_audit[0]["request_id"] == "classroom-groups-generate-1-request"

            second_group_state = data(
                await client.post(
                    f"/api/teacher/activities/{group_id}/groups/generate",
                    headers={**admin, "Idempotency-Key": "classroom-groups-generate-2"},
                    json={},
                ),
                201,
            )
            second_membership = assert_staff_groups(
                second_group_state, group_id, 2, expected_refs, group_names
            )
            admin_group_state = data(
                await client.get(f"/api/activities/{group_id}/groups", headers=admin),
                200,
            )
            assert_staff_groups(admin_group_state, group_id, 2, expected_refs, group_names)
            assert_no_raw_ids(admin_group_state, all_raw_ids)
            retained_first_revision = data(
                await client.get(
                    f"/api/activities/{group_id}/groups?revision=1",
                    headers=teacher,
                ),
                200,
            )
            assert_staff_groups(
                retained_first_revision, group_id, 1, expected_refs, group_names
            )

            for raw_id, headers in student_headers.items():
                student_groups = data(
                    await client.get(f"/api/activities/{group_id}/groups", headers=headers),
                    200,
                )
                expected_group = second_membership[stable_refs[raw_id]]
                assert student_groups["activity_id"] == group_id
                assert student_groups["kind"] == "group_task"
                assert student_groups["revision"] == 2
                assert "groups" not in student_groups
                assert "available_revisions" not in student_groups
                actual_group = student_groups["my_group"]
                assert actual_group["name"] == expected_group["name"]
                assert {member["display_name"] for member in actual_group["members"]} == {
                    member["display_name"] for member in expected_group["members"]
                }
                assert sum(member["is_me"] is True for member in actual_group["members"]) == 1
                assert not contains_key(student_groups, "user_ref")
                assert_no_raw_ids(student_groups, all_raw_ids)

            data(
                await client.post(
                    f"/api/teacher/activities/{group_id}/close",
                    headers={**teacher, "Idempotency-Key": "classroom-groups-close"},
                    json={},
                ),
                200,
            )
            error(
                await client.post(
                    f"/api/teacher/activities/{group_id}/groups/generate",
                    headers={**teacher, "Idempotency-Key": "classroom-groups-closed-generate"},
                    json={},
                ),
                409,
                "activity_not_open",
            )
            data(
                await client.post(
                    f"/api/teacher/activities/{group_id}/reopen",
                    headers={**teacher, "Idempotency-Key": "classroom-groups-reopen"},
                    json={},
                ),
                200,
            )
            third_group_state = data(
                await client.post(
                    f"/api/teacher/activities/{group_id}/groups/generate",
                    headers={**teacher, "Idempotency-Key": "classroom-groups-generate-3"},
                    json={},
                ),
                201,
            )
            assert_staff_groups(third_group_state, group_id, 3, expected_refs, group_names)
            with store.connect() as db:
                revisions = db.execute(
                    "SELECT revision,id FROM group_task_revisions WHERE activity_id=? ORDER BY revision",
                    (group_id,),
                ).fetchall()
                assert [row["revision"] for row in revisions] == [1, 2, 3]
                member_counts = [
                    db.execute(
                        "SELECT COUNT(*) FROM group_task_members WHERE revision_id=?",
                        (row["id"],),
                    ).fetchone()[0]
                    for row in revisions
                ]
                assert member_counts == [len(raw_students)] * 3

            other_random = store.create_activity(
                stable_uid("classroom-other-course-teacher"),
                {
                    "kind": "random_selection",
                    "title": "其他课程随机选人",
                    "body": "不得跨课程访问。",
                    "options": [],
                    "status": "published",
                    "max_attempts": 1,
                },
                course_id=2,
            )
            other_groups = store.create_activity(
                stable_uid("classroom-other-course-teacher"),
                {
                    "kind": "group_task",
                    "title": "其他课程分组任务",
                    "body": "不得跨课程访问。",
                    "options": group_options,
                    "status": "published",
                    "max_attempts": 1,
                },
                course_id=2,
            )
            for endpoint in (
                f"/api/activities/{other_random['id']}/random-selection",
                f"/api/activities/{other_groups['id']}/groups",
            ):
                error(await client.get(endpoint, headers=student), 404, "not_found")
            for endpoint, key in (
                (
                    f"/api/teacher/activities/{other_random['id']}/random-select",
                    "classroom-cross-course-random-select",
                ),
                (
                    f"/api/teacher/activities/{other_groups['id']}/groups/generate",
                    "classroom-cross-course-groups-generate",
                ),
            ):
                error(
                    await client.post(
                        endpoint,
                        headers={**teacher, "Idempotency-Key": key},
                        json={},
                    ),
                    404,
                    "not_found",
                )
            visible_ids = {
                item["id"]
                for item in data(await client.get("/api/activities", headers=student), 200)["items"]
            }
            assert other_random["id"] not in visible_ids and other_groups["id"] not in visible_ids

    print(
        "CLASSROOM_EVENTS_API_OK "
        "cases=active_roster,unconfigured_roster,stable_uid,staff_roles,student_privacy,"
        "random_cycle,atomic_idempotency,closed_reopen,balanced_groups,revision_history,audit,course_scope"
    )


if __name__ == "__main__":
    asyncio.run(run())
