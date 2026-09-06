#!/usr/bin/env python3
"""Exercise the live administrator session without printing account data."""

from __future__ import annotations

import argparse
import sys

from real_role_smoke import Session


def run(args: argparse.Namespace) -> None:
    session = Session(args.base_url)
    session.login(args.username, args.password)
    bridge_status, bridge = session.json_request("/local/course_agent/session.php")
    if bridge_status != 200 or bridge.get("role") != "admin":
        raise RuntimeError("admin_role_bridge_failed")
    status, opened = session.json_request("/api/course/session/open")
    data = opened.get("data") if isinstance(opened, dict) else None
    if status != 200 or not isinstance(data, dict) or data.get("role") != "admin":
        raise RuntimeError("admin_course_session_failed")
    status, health = session.json_request("/api/admin/status", method="GET")
    data = health.get("data") if isinstance(health, dict) else None
    if status != 200 or not isinstance(data, dict):
        raise RuntimeError(f"admin_status_http_{status}")
    if data.get("workflow_configured") is not True or data.get("mock_workflow") is not False:
        raise RuntimeError("admin_status_configuration_mismatch")
    course_status, _, course_page = session.request("/course/view.php?id=2")
    if course_status != 200 or b"\xe7\x94\xb5\xe5\x8a\x9b\xe7\xb3\xbb\xe7\xbb\x9f\xe5\x82\xa8\xe8\x83\xbd\xe6\x8a\x80\xe6\x9c\xaf" not in course_page:
        raise RuntimeError(f"admin_course_page_http_{course_status}")
    print("REAL_ADMIN_SMOKE_OK role=admin course_page=200 admin_status=200 workflow=real mock=false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    try:
        run(args)
    except RuntimeError as error:
        print(f"REAL_ADMIN_SMOKE_FAILED code={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
