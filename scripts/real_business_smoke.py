#!/usr/bin/env python3
"""Exercise the real teacher/student assignment lifecycle over HTTPS."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse

from real_role_smoke import Session


def data_of(payload: dict[str, object], label: str) -> dict[str, object]:
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{label}_invalid_data")
    return data


def list_items(payload: dict[str, object], label: str) -> list[dict[str, object]]:
    items = data_of(payload, label).get("items")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise RuntimeError(f"{label}_invalid_items")
    return [item for item in items if isinstance(item, dict)]


def session_for(base_url: str, username: str, password: str, expected_role: str) -> tuple[Session, str]:
    session = Session(base_url)
    session.login(username, password)
    status, bridge = session.json_request("/local/course_agent/session.php")
    if status != 200 or bridge.get("role") != expected_role:
        raise RuntimeError(f"{expected_role}_login_or_role_failed")
    sesskey = str(bridge.get("sesskey") or "")
    if not sesskey:
        raise RuntimeError(f"{expected_role}_sesskey_missing")
    return session, sesskey


def post_json(session: Session, path: str, sesskey: str, key: str, payload: dict[str, object]) -> tuple[int, dict[str, object]]:
    return session.json_request(
        path,
        payload=payload,
        headers={"X-Moodle-Sesskey": sesskey, "Idempotency-Key": key},
        timeout=60,
    )


def run(args: argparse.Namespace) -> None:
    teacher, teacher_key = session_for(args.base_url, args.teacher, args.teacher_password, "teacher")
    student, student_key = session_for(args.base_url, args.student, args.student_password, "student")

    teacher_open_status, teacher_open = teacher.json_request("/api/course/session/open")
    student_open_status, student_open = student.json_request("/api/course/session/open")
    if teacher_open_status != 200 or student_open_status != 200:
        raise RuntimeError("course_session_open_failed")
    if data_of(teacher_open, "teacher_open").get("role") != "teacher" or data_of(student_open, "student_open").get("role") != "student":
        raise RuntimeError("course_session_role_mismatch")

    # Confirm server-side authorization boundaries before doing any writes.
    student_kb_status, _ = student.json_request("/api/knowledge-base/versions?page=1&page_size=20", method="GET")
    teacher_submit_status, _ = post_json(
        teacher,
        "/api/student/assignments/not-a-real-assignment/submit",
        teacher_key,
        "codex-real-teacher-submit-boundary-20260820",
        {"answers": {}, "attempt": 1},
    )
    if student_kb_status != 403 or teacher_submit_status != 403:
        raise RuntimeError("role_boundary_failed")

    prompt = "Codex真实回归题：储能变流器并网控制测试题（20260820）"
    title = "Codex真实回归作业（20260820）"
    q_status, q_listing = teacher.json_request("/api/questions?page=1&page_size=100", method="GET")
    if q_status != 200:
        raise RuntimeError(f"question_list_http_{q_status}")
    question = next((item for item in list_items(q_listing, "question_list") if item.get("prompt") == prompt), None)
    if not question:
        q_status, created = post_json(
            teacher,
            "/api/teacher/questions",
            teacher_key,
            "codex-real-question-create-20260820",
            {"question_type": "true_false", "prompt": prompt, "answer": True, "max_score": 10},
        )
        if q_status not in {200, 201}:
            raise RuntimeError(f"question_create_http_{q_status}")
        question = data_of(created, "question_create")
    question_id = str(question.get("id") or "")
    if not question_id:
        raise RuntimeError("question_id_missing")
    if question.get("status") != "published":
        q_status, published = post_json(
            teacher,
            f"/api/teacher/questions/{urllib.parse.quote(question_id, safe='')}/publish",
            teacher_key,
            "codex-real-question-publish-20260820",
            {},
        )
        if q_status != 200 or published.get("status") != "ok":
            raise RuntimeError(f"question_publish_http_{q_status}")

    a_status, a_listing = teacher.json_request("/api/assignments?page=1&page_size=100", method="GET")
    if a_status != 200:
        raise RuntimeError(f"assignment_list_http_{a_status}")
    assignment = next((item for item in list_items(a_listing, "assignment_list") if item.get("title") == title), None)
    if not assignment:
        a_status, created = post_json(
            teacher,
            "/api/teacher/assignments",
            teacher_key,
            "codex-real-assignment-create-20260820",
            {"title": title, "question_ids": [question_id], "allow_attempts": 1},
        )
        if a_status not in {200, 201}:
            raise RuntimeError(f"assignment_create_http_{a_status}")
        assignment = data_of(created, "assignment_create")
    assignment_id = str(assignment.get("id") or "")
    if not assignment_id:
        raise RuntimeError("assignment_id_missing")
    if assignment.get("status") != "published":
        a_status, published = post_json(
            teacher,
            f"/api/teacher/assignments/{urllib.parse.quote(assignment_id, safe='')}/publish",
            teacher_key,
            "codex-real-assignment-publish-20260820",
            {},
        )
        if a_status != 200 or published.get("status") != "ok":
            raise RuntimeError(f"assignment_publish_http_{a_status}")

    student_detail_status, student_detail = student.json_request(
        f"/api/student/assignments/{urllib.parse.quote(assignment_id, safe='')}",
        method="GET",
    )
    if student_detail_status != 200:
        raise RuntimeError(f"student_assignment_detail_http_{student_detail_status}")
    student_data = data_of(student_detail, "student_assignment_detail")
    questions = student_data.get("questions")
    if not isinstance(questions, list) or not questions:
        raise RuntimeError("student_assignment_questions_missing")
    if any(isinstance(item, dict) and ("answer" in item or "answer_json" in item or "rubric" in item) for item in questions):
        raise RuntimeError("student_answer_key_leaked")
    submissions = student_data.get("my_submissions")
    if not isinstance(submissions, list):
        raise RuntimeError("student_submission_list_missing")
    if not submissions:
        submit_status, submitted = post_json(
            student,
            f"/api/student/assignments/{urllib.parse.quote(assignment_id, safe='')}/submit",
            student_key,
            "codex-real-submission-20260820",
            {"answers": {question_id: True}, "attempt": 1},
        )
        if submit_status not in {200, 201} or submitted.get("status") != "ok":
            raise RuntimeError(f"student_submit_http_{submit_status}")

    teacher_sub_status, teacher_submissions = teacher.json_request(
        f"/api/teacher/assignments/{urllib.parse.quote(assignment_id, safe='')}/submissions?page=1&page_size=100",
        method="GET",
    )
    if teacher_sub_status != 200:
        raise RuntimeError(f"teacher_submissions_http_{teacher_sub_status}")
    teacher_items = list_items(teacher_submissions, "teacher_submissions")
    submission = next((item for item in teacher_items if item.get("user_uid")), None)
    if not submission:
        raise RuntimeError("teacher_submission_missing")
    submission_id = str(submission.get("id") or "")
    if not submission_id:
        raise RuntimeError("submission_id_missing")

    grade_status, graded = post_json(
        teacher,
        f"/api/teacher/submissions/{urllib.parse.quote(submission_id, safe='')}/grade",
        teacher_key,
        "codex-real-submission-grade-20260820",
        {},
    )
    if grade_status != 200 or graded.get("status") != "ok":
        raise RuntimeError(f"teacher_grade_http_{grade_status}")
    grade_data = data_of(graded, "graded")
    sync = grade_data.get("moodle_sync")
    if not isinstance(sync, dict) or sync.get("status") not in {"synced", "mock_skipped"}:
        raise RuntimeError("moodle_grade_sync_not_confirmed")

    student_after_status, student_after = student.json_request(
        f"/api/student/assignments/{urllib.parse.quote(assignment_id, safe='')}",
        method="GET",
    )
    if student_after_status != 200:
        raise RuntimeError(f"student_after_grade_http_{student_after_status}")
    after_submissions = data_of(student_after, "student_after").get("my_submissions")
    if not isinstance(after_submissions, list) or not any(item.get("score") is not None for item in after_submissions if isinstance(item, dict)):
        raise RuntimeError("student_grade_not_visible")

    print(f"REAL_BUSINESS_SMOKE_OK teacher=teacher student=student assignment=published submission=graded moodle_sync={sync.get('status')} boundary=ok")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--teacher", required=True)
    parser.add_argument("--teacher-password", required=True)
    parser.add_argument("--student", required=True)
    parser.add_argument("--student-password", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except RuntimeError as error:
        print(f"REAL_BUSINESS_SMOKE_FAILED code={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
