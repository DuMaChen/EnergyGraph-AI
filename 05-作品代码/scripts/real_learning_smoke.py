#!/usr/bin/env python3
"""Exercise graph, resources, learning profile, and scenario lifecycle."""

from __future__ import annotations

import argparse
import sys
import urllib.parse

from real_role_smoke import Session


def data_of(payload: dict[str, object], label: str) -> dict[str, object]:
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{label}_invalid_data")
    return data


def session_for(base_url: str, username: str, password: str, role: str) -> tuple[Session, str]:
    session = Session(base_url)
    session.login(username, password)
    status, bridge = session.json_request("/local/course_agent/session.php")
    if status != 200 or bridge.get("role") != role:
        raise RuntimeError(f"{role}_role_failed")
    key = str(bridge.get("sesskey") or "")
    if not key:
        raise RuntimeError(f"{role}_sesskey_missing")
    return session, key


def run(args: argparse.Namespace) -> None:
    student, student_key = session_for(args.base_url, args.student, args.student_password, "student")
    teacher, teacher_key = session_for(args.base_url, args.teacher, args.teacher_password, "teacher")

    status, chapters = student.json_request("/api/knowledge-graph/chapters", method="GET")
    chapter_data = data_of(chapters, "chapters")
    if status != 200 or len(chapter_data.get("items", [])) != 6:
        raise RuntimeError("chapter_graph_failed")

    status, resources = student.json_request("/api/textbook/resources?page=1&page_size=100", method="GET")
    resource_data = data_of(resources, "resources")
    if status != 200 or int(resource_data.get("total", 0)) < 20:
        raise RuntimeError("textbook_resources_failed")

    status, profile = student.json_request("/api/learning/profile", method="GET")
    profile_data = data_of(profile, "profile")
    student_uid = str(profile_data.get("user_uid") or "")
    if status != 200 or not student_uid.startswith("u_"):
        raise RuntimeError("learning_profile_failed")

    status, recommendations = student.json_request("/api/learning/recommendations", method="GET")
    if status != 200 or not isinstance(data_of(recommendations, "recommendations").get("items"), list):
        raise RuntimeError("learning_recommendations_failed")

    status, started = student.json_request(
        "/api/scenarios/start",
        payload={"scenario_key": "grid-dispatch"},
        headers={"X-Moodle-Sesskey": student_key, "Idempotency-Key": "codex-real-scenario-start-20260820"},
    )
    if status not in {200, 201}:
        raise RuntimeError(f"scenario_start_http_{status}")
    scenario_id = str(data_of(started, "scenario_start").get("session_id") or "")
    if not scenario_id:
        raise RuntimeError("scenario_id_missing")
    status, ended = student.json_request(
        f"/api/scenarios/{urllib.parse.quote(scenario_id, safe='')}/end",
        payload={"state": "completed"},
        headers={"X-Moodle-Sesskey": student_key, "Idempotency-Key": "codex-real-scenario-end-20260820"},
    )
    if status != 200 or data_of(ended, "scenario_end").get("state") not in {"completed", "ended"}:
        raise RuntimeError(f"scenario_end_http_{status}")

    status, teacher_profile = teacher.json_request(
        f"/api/teacher/students/{urllib.parse.quote(student_uid, safe='')}/learning-profile",
        method="GET",
    )
    if status != 200 or data_of(teacher_profile, "teacher_profile").get("user_uid") != student_uid:
        raise RuntimeError("teacher_student_profile_failed")

    status, student_forbidden = student.json_request(
        f"/api/teacher/students/{urllib.parse.quote(student_uid, safe='')}/learning-profile",
        method="GET",
    )
    if status != 403:
        raise RuntimeError("student_profile_privacy_boundary_failed")

    print("REAL_LEARNING_SMOKE_OK chapters=6 resources>=20 profile=ok recommendations=ok scenario=start_end teacher_view=ok privacy=ok")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--student", required=True)
    parser.add_argument("--student-password", required=True)
    parser.add_argument("--teacher", required=True)
    parser.add_argument("--teacher-password", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except RuntimeError as error:
        print(f"REAL_LEARNING_SMOKE_FAILED code={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
