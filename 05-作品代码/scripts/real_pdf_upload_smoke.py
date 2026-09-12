#!/usr/bin/env python3
"""Exercise the production PDF upload contract with a synthetic fixture.

The fixture is deliberately uploaded to a separate draft/processing version;
it is never sent through the formal release gate or published as courseware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
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
    sesskey = str(bridge.get("sesskey") or "")
    if not sesskey:
        raise RuntimeError(f"{role}_sesskey_missing")
    return session, sesskey


def run(args: argparse.Namespace) -> None:
    fixture = pathlib.Path(args.pdf).resolve()
    content = fixture.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    filename = fixture.name
    version_name = args.version_name

    teacher, teacher_key = session_for(args.base_url, args.teacher, args.teacher_password, "teacher")
    student, _ = session_for(args.base_url, args.student, args.student_password, "student")
    common = {"X-Moodle-Sesskey": teacher_key}

    before_status, before_payload = teacher.json_request("/api/knowledge-base/versions?page=1&page_size=100", method="GET")
    if before_status != 200:
        raise RuntimeError(f"kb_list_before_http_{before_status}")
    before_items = data_of(before_payload, "kb_list_before").get("items")
    if not isinstance(before_items, list):
        raise RuntimeError("kb_list_before_items_invalid")
    published_before = next((item for item in before_items if isinstance(item, dict) and item.get("status") == "published"), None)
    published_id_before = str(published_before.get("id") or "") if isinstance(published_before, dict) else ""
    if not published_id_before:
        raise RuntimeError("published_version_missing_before_upload")

    version = next((item for item in before_items if isinstance(item, dict) and item.get("version_name") == version_name), None)
    if not isinstance(version, dict):
        status, created = teacher.json_request(
            "/api/knowledge-base/versions",
            payload={"version_name": version_name, "workflow_id": args.workflow_id, "manifest_sha256": "fixture-only"},
            headers={**common, "Idempotency-Key": f"codex-pdf-create-{version_name}"},
        )
        if status not in {200, 201}:
            raise RuntimeError(f"kb_fixture_create_http_{status}")
        version = data_of(created, "kb_fixture_create")
    version_id = str(version.get("id") or "")
    version_state = str(version.get("status") or "")
    if not version_id or version_state not in {"draft", "processing"}:
        raise RuntimeError(f"fixture_version_not_uploadable_{version_state}")

    query = urllib.parse.urlencode({"filename": filename})
    upload_headers = {
        **common,
        "Idempotency-Key": f"codex-pdf-upload-{version_id}-{digest[:16]}",
        "Content-Type": "application/pdf",
    }
    status, _, body = teacher.request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/files?{query}",
        method="PUT",
        data=content,
        headers=upload_headers,
        timeout=60,
    )
    if status not in {200, 201}:
        raise RuntimeError(f"fixture_upload_http_{status}")
    uploaded = json.loads(body.decode("utf-8"))
    record = data_of(uploaded, "fixture_upload")
    if record.get("filename") != filename or record.get("sha256") != digest or int(record.get("size_bytes") or 0) != len(content):
        raise RuntimeError("fixture_upload_metadata_mismatch")

    # Same idempotency key must return the same record and must not add a file.
    repeated_status, _, repeated_body = teacher.request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/files?{query}",
        method="PUT",
        data=content,
        headers=upload_headers,
        timeout=60,
    )
    if repeated_status not in {200, 201}:
        raise RuntimeError(f"fixture_upload_repeat_http_{repeated_status}")
    repeated = data_of(json.loads(repeated_body.decode("utf-8")), "fixture_upload_repeat")
    if repeated.get("id") != record.get("id"):
        raise RuntimeError("fixture_upload_idempotency_mismatch")

    files_status, files_payload = teacher.json_request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/files",
        method="GET",
    )
    files = data_of(files_payload, "fixture_files").get("items")
    if files_status != 200 or not isinstance(files, list) or len(files) != 1:
        raise RuntimeError(f"fixture_file_count_http_{files_status}")
    final_state = "processing"

    fake_status, _, _ = teacher.request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/files?filename=fake.pdf",
        method="PUT",
        data=b"%PDF-1.7\nnot really a PDF\n%%EOF\n",
        headers={**common, "Idempotency-Key": f"codex-pdf-fake-{version_id}", "Content-Type": "application/pdf"},
    )
    if fake_status != 422:
        raise RuntimeError(f"fake_pdf_guard_http_{fake_status}")

    traversal_status, _, _ = teacher.request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/files?filename={urllib.parse.quote('../escape.pdf')}",
        method="PUT",
        data=content,
        headers={**common, "Idempotency-Key": f"codex-pdf-traversal-{version_id}", "Content-Type": "application/pdf"},
    )
    if traversal_status != 422:
        raise RuntimeError(f"path_traversal_guard_http_{traversal_status}")

    student_status, _ = student.json_request("/api/knowledge-base/versions?page=1&page_size=100", method="GET")
    if student_status != 403:
        raise RuntimeError(f"student_kb_boundary_http_{student_status}")

    after_status, after_payload = teacher.json_request("/api/knowledge-base/versions?page=1&page_size=100", method="GET")
    after_items = data_of(after_payload, "kb_list_after").get("items")
    published_after = next((item for item in after_items if isinstance(item, dict) and item.get("status") == "published"), None) if isinstance(after_items, list) else None
    if after_status != 200 or not isinstance(published_after, dict) or published_after.get("id") != published_id_before or published_after.get("status") != "published":
        raise RuntimeError("published_version_changed_by_fixture_upload")

    print(
        "REAL_PDF_UPLOAD_SMOKE_OK "
        f"version={version_id} state={final_state} files=1 "
        f"bytes={len(content)} sha256={digest[:16]} idempotency=ok fake_pdf=422 traversal=422 "
        "student_boundary=403 published_unchanged=ok"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--teacher", required=True)
    parser.add_argument("--teacher-password", required=True)
    parser.add_argument("--student", required=True)
    parser.add_argument("--student-password", required=True)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--workflow-id", default="7494978072491315200")
    parser.add_argument("--version-name", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except (OSError, RuntimeError, json.JSONDecodeError, ValueError) as error:
        print(f"REAL_PDF_UPLOAD_SMOKE_FAILED code={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
