#!/usr/bin/env python3
"""Create, upload, golden-test, and publish a KB through the teacher API."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.parse

from real_role_smoke import Session


def require_data(payload: dict[str, object], label: str) -> dict[str, object]:
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{label}_invalid_response")
    return data


def run(args: argparse.Namespace) -> None:
    session = Session(args.base_url)
    session.login(args.username, args.password)
    bridge_status, bridge = session.json_request("/local/course_agent/session.php")
    if bridge_status != 200 or bridge.get("role") != "teacher":
        raise RuntimeError(f"teacher_bridge_http_{bridge_status}")
    sesskey = str(bridge.get("sesskey") or "")
    if not sesskey:
        raise RuntimeError("missing_moodle_sesskey")

    common = {"Content-Type": "application/json", "X-Moodle-Sesskey": sesskey}
    version_name = args.version_name
    list_status, listed = session.json_request("/api/knowledge-base/versions?page=1&page_size=100", method="GET")
    if list_status != 200:
        raise RuntimeError(f"kb_list_http_{list_status}")
    items = require_data(listed, "kb_list").get("items")
    if not isinstance(items, list):
        raise RuntimeError("kb_list_items_invalid")
    version = next((item for item in items if isinstance(item, dict) and item.get("version_name") == version_name), None)
    if not isinstance(version, dict):
        create_status, created = session.json_request(
            "/api/knowledge-base/versions",
            payload={"version_name": version_name, "workflow_id": args.workflow_id, "manifest_sha256": "local-manifest"},
            headers={**common, "Idempotency-Key": f"codex-kb-create-{version_name}"},
            timeout=30,
        )
        if create_status not in {200, 201}:
            raise RuntimeError(f"kb_create_http_{create_status}")
        version = require_data(created, "kb_create")
    version_id = str(version.get("id") or "")
    if not version_id:
        raise RuntimeError("kb_version_id_missing")

    files = sorted(pathlib.Path(args.course_data).glob("*.pdf"))
    if not files:
        raise RuntimeError("course_files_missing")
    upload_count = 0
    for path in files:
        query = urllib.parse.urlencode({"filename": path.name})
        request_body = path.read_bytes()
        status, _, body = session.request(
            f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/files?{query}",
            method="PUT",
            data=request_body,
            headers={
                "X-Moodle-Sesskey": sesskey,
                "Idempotency-Key": f"codex-kb-upload-{version_id}-{path.name}-{len(request_body)}",
                "Content-Type": "application/pdf",
            },
            timeout=60,
        )
        if status not in {200, 201}:
            raise RuntimeError(f"kb_upload_http_{status}_{path.suffix.lower()}")
        try:
            response = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise RuntimeError("kb_upload_invalid_response") from error
        if response.get("status") != "ok":
            raise RuntimeError("kb_upload_rejected")
        upload_count += 1

    for case_id in ("qa-001", "qa-002", "qa-003"):
        status, result = session.json_request(
            f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/hit-tests",
            payload={"case_id": case_id},
            headers={**common, "Idempotency-Key": f"codex-kb-hit-{version_id}-{case_id}"},
            timeout=120,
        )
        if status != 200 or result.get("status") != "ok":
            raise RuntimeError(f"kb_hit_test_{case_id}_http_{status}")

    status, tested = session.json_request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/status",
        payload={"status": "tested"},
        headers={**common, "Idempotency-Key": f"codex-kb-status-{version_id}-tested"},
    )
    if status != 200 or tested.get("status") != "ok":
        raise RuntimeError(f"kb_mark_tested_http_{status}")

    status, published = session.json_request(
        f"/api/knowledge-base/versions/{urllib.parse.quote(version_id, safe='')}/status",
        payload={"status": "published"},
        headers={**common, "Idempotency-Key": f"codex-kb-status-{version_id}-published"},
    )
    if status != 200 or published.get("status") != "ok":
        raise RuntimeError(f"kb_publish_http_{status}")
    published_data = require_data(published, "kb_publish")
    if published_data.get("status") != "published":
        raise RuntimeError("kb_publish_state_invalid")
    print(f"REAL_KB_RELEASE_OK status=published files={upload_count} hit_tests=3")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--course-data", required=True)
    parser.add_argument("--version-name", default=f"codex-real-release-{time.strftime('%Y%m%d')}")
    args = parser.parse_args()
    try:
        run(args)
    except RuntimeError as error:
        print(f"REAL_KB_RELEASE_FAILED code={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
