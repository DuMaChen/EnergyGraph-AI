#!/usr/bin/env python3
"""Verify that a newly-created Moodle user can log in and reach the course Agent."""

from __future__ import annotations

import argparse
import html
import sys
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from urllib.parse import urlencode, urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener


class LoginFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.action = "/login/index.php"
        self.hidden: dict[str, str] = {}
        self._in_login_form = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = dict(attrs)
        if tag == "form" and "login" in (fields.get("id") or "").lower():
            self._in_login_form = True
            self.action = fields.get("action") or self.action
        elif tag == "input" and self._in_login_form:
            if fields.get("type", "").lower() == "hidden" and fields.get("name"):
                self.hidden[fields["name"]] = html.unescape(fields.get("value") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self._in_login_form:
            self._in_login_form = False


def fetch(opener, url: str, data: bytes | None = None):
    request = Request(
        url,
        data=data,
        headers={"User-Agent": "codex-real-autoenrol-acceptance/1.0"},
    )
    return opener.open(request, timeout=30)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://energygraph.icu")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    login_url = f"{base}/login/index.php"
    with fetch(opener, login_url) as response:
        login_html = response.read().decode("utf-8", "replace")

    form = LoginFormParser()
    form.feed(login_html)
    payload = dict(form.hidden)
    payload.update(
        {
            "username": args.username,
            "password": args.password,
            "rememberusername": "1",
        }
    )
    with fetch(opener, urljoin(login_url, form.action), urlencode(payload).encode()) as response:
        response.read()

    course_url = f"{base}/course/view.php?id=2"
    with fetch(opener, course_url) as response:
        course_html = response.read().decode("utf-8", "replace")
        course_status = response.status

    with fetch(opener, f"{base}/?redirect=0") as response:
        home_html = response.read().decode("utf-8", "replace")
        home_status = response.status

    agent_url = f"{base}/agent/"
    with fetch(opener, agent_url) as response:
        agent_html = response.read().decode("utf-8", "replace")
        agent_status = response.status

    required = ("电力系统储能技术", "课程 Agent")
    if course_status != 200 or any(marker not in course_html for marker in required):
        print("AUTOENROL_WEB_COURSE_FAIL", file=sys.stderr)
        return 1
    if home_status != 200 or "电力系统储能技术" not in home_html:
        print("AUTOENROL_WEB_HOME_EMPTY", file=sys.stderr)
        return 1
    if "您不能注册本课程" in course_html or "选课选项" in course_html:
        print("AUTOENROL_WEB_NOT_ENROLLED", file=sys.stderr)
        return 1
    if agent_status != 200 or "储能学习空间" not in agent_html:
        print("AUTOENROL_WEB_AGENT_FAIL", file=sys.stderr)
        return 1

    print("AUTOENROL_WEB_OK home=course-visible course=2 agent=200")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
