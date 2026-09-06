#!/usr/bin/env python3
"""Run a real Moodle login and same-origin Agent smoke test.

This script intentionally prints only role/status evidence. Credentials are
passed at runtime and are never written to disk or echoed.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import html.parser
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


class HiddenInputs(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "input":
            return
        data = dict(attrs)
        if data.get("type") == "hidden" and data.get("name"):
            self.values[str(data["name"])] = str(data.get("value") or "")


class Session:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def url(self, path: str) -> str:
        return self.base_url + path

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30,
    ) -> tuple[int, str, bytes]:
        request = urllib.request.Request(self.url(path), data=data, method=method, headers=headers or {})
        try:
            with self.opener.open(request, timeout=timeout) as response:
                return response.status, response.geturl(), response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.geturl(), error.read()

    def login(self, username: str, password: str) -> None:
        status, _, page = self.request("/login/index.php")
        if status != 200:
            raise RuntimeError(f"login_page_http_{status}")
        parser = HiddenInputs()
        parser.feed(page.decode("utf-8", errors="replace"))
        form = {**parser.values, "username": username, "password": password}
        encoded = urllib.parse.urlencode(form).encode("utf-8")
        status, final_url, body = self.request(
            "/login/index.php",
            method="POST",
            data=encoded,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        text = body.decode("utf-8", errors="replace").lower()
        if status != 200 or "/login/index.php" in final_url or "invalid login" in text or "loginerror" in text:
            raise RuntimeError(f"login_failed_http_{status}")

    def json_request(
        self,
        path: str,
        *,
        method: str = "POST",
        payload: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30,
    ) -> tuple[int, dict[str, object]]:
        merged = {"Content-Type": "application/json", **(headers or {})}
        data = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        status, _, body = self.request(path, method=method, data=data, headers=merged, timeout=timeout)
        try:
            return status, json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError(f"invalid_json_http_{status}") from error


def run(args: argparse.Namespace) -> None:
    session = Session(args.base_url)
    session.login(args.username, args.password)

    course_status, _, course_body = session.request("/course/view.php?id=2")
    if course_status != 200 or len(course_body) < 1000:
        raise RuntimeError(f"course_page_http_{course_status}")

    bridge_status, bridge = session.json_request("/local/course_agent/session.php")
    if bridge_status != 200 or bridge.get("role") != args.expected_role:
        raise RuntimeError(f"role_bridge_failed_http_{bridge_status}")
    sesskey = str(bridge.get("sesskey") or "")
    if not sesskey:
        raise RuntimeError("missing_moodle_sesskey")

    open_status, opened = session.json_request("/api/course/session/open")
    data = opened.get("data") if isinstance(opened, dict) else None
    if open_status != 200 or not isinstance(data, dict) or data.get("role") != args.expected_role:
        raise RuntimeError(f"agent_session_failed_http_{open_status}")
    features = data.get("features") or {}
    if not isinstance(features, dict):
        raise RuntimeError("agent_features_invalid")
    expected_teacher_tools = args.expected_role == "teacher"
    if bool(features.get("teacher_assistant")) != expected_teacher_tools:
        raise RuntimeError("role_feature_boundary_failed")

    payload = json.dumps({"question": args.question, "mode": "qa", "session_id": None, "turn_no": None}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        session.url("/api/course-agent/chat"),
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Moodle-Sesskey": sesskey,
            "Accept": "text/event-stream",
        },
    )
    try:
        response = session.opener.open(request, timeout=120)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"agent_chat_http_{error.code}") from error
    event_counts: dict[str, int] = {}
    error_codes: list[str] = []
    saw_done = False
    saw_error = False
    pending_event = ""
    with response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if line.startswith("event:"):
                pending_event = line.split(":", 1)[1].strip()
                event_counts[pending_event] = event_counts.get(pending_event, 0) + 1
                saw_done = saw_done or pending_event == "done"
                saw_error = saw_error or pending_event == "error"
            elif line.startswith("data:") and pending_event == "error":
                try:
                    payload = json.loads(line.split(":", 1)[1].strip())
                    def collect_codes(value: object) -> None:
                        if isinstance(value, dict):
                            if value.get("code"):
                                error_codes.append(str(value["code"]))
                            for child in value.values():
                                collect_codes(child)
                        elif isinstance(value, list):
                            for child in value:
                                collect_codes(child)

                    collect_codes(payload)
                except json.JSONDecodeError:
                    error_codes.append("invalid_error_data")
    if not saw_done or saw_error:
        suffix = "_".join(error_codes[:3]) if error_codes else "no_error_code"
        raise RuntimeError(f"agent_stream_incomplete_or_error_events_{json.dumps(event_counts, sort_keys=True)}_{suffix}")

    print(
        "REAL_ROLE_SMOKE_OK "
        f"role={args.expected_role} course_page=200 session={open_status} "
        f"events={json.dumps(event_counts, sort_keys=True, ensure_ascii=True)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--expected-role", choices=("teacher", "student"), required=True)
    parser.add_argument("--question", default="请说明储能变流器在并网控制中的作用。")
    args = parser.parse_args()
    try:
        run(args)
    except RuntimeError as error:
        print(f"REAL_ROLE_SMOKE_FAILED code={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
