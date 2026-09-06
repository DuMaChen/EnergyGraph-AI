#!/usr/bin/env python3
"""Run a real Workflow answer-quality evaluation through the course API.

The script prints only aggregate scores by default.  With --report it writes a
JSON report containing prompts, normalized answers, source metadata, and the
rule-based observations needed for review.  Credentials are runtime inputs
and are never written by this script.
"""

from __future__ import annotations

import argparse
import html.parser
import http.cookiejar
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


@dataclass(frozen=True)
class Case:
    case_id: str
    mode: str
    question: str
    required: tuple[str, ...]
    expected_shape: tuple[str, ...]
    forbidden: tuple[str, ...] = ()
    needs_verified_source: bool = True


CASES = (
    Case(
        "qa_pcs_topology",
        "qa",
        "请依据课程资料解释储能变流器的作用，并对比单级式和双级式拓扑：列出核心差异、适用场景和各自代价。",
        ("双向", "DC/AC", "单级式", "双级式", "适用"),
        ("差异", "场景"),
    ),
    Case(
        "qa_pumped_storage",
        "qa",
        "请按抽水和发电两个模式，说明抽水蓄能电站中上水库、下水库、输水系统、水泵水轮机和发电电动机的能量流向与作用。",
        ("上水库", "下水库", "抽水", "发电", "水泵水轮机"),
        ("抽水", "发电"),
    ),
    Case(
        "qa_three_level_boundary",
        "qa",
        "三电平变流器相较两电平变流器，在输出谐波、开关频率、损耗、效率和控制复杂度方面有什么课程依据？不要编造课件没有的具体数值。",
        ("三电平", "两电平", "谐波", "开关频率", "控制"),
        ("对比",),
        ("99%", "精确为", "额定为"),
    ),
    Case(
        "qa_engineering_judgment",
        "qa",
        "如果电池电压变化范围较宽，同时要求并网运行适应性较强，依据课程资料应优先考察哪类储能变流器拓扑？请说明依据、代价和仍需核验的工程条件。",
        ("双级式", "DC/DC", "电压", "适应性", "核验"),
        ("依据", "代价"),
    ),
    Case(
        "qa_out_of_scope",
        "qa",
        "课程资料是否给出了某具体厂商在2026年的储能变流器价格、质保条款和现场故障率？如果没有，请明确说明资料未覆盖，不要猜测。",
        ("未覆盖",),
        ("说明",),
        ("价格是", "故障率为", "质保期是"),
        False,
    ),
    Case(
        "qa_ambiguous",
        "qa",
        "储能系统好不好？",
        (),
        ("需要", "取决于", "场景", "明确"),
        ("一定好", "一定不好"),
        False,
    ),
    Case(
        "teacher_lesson_design",
        "teacher_assistant",
        "请围绕第3章储能变流器并网控制，设计一个可执行的课堂讨论活动，包含教学目标、课前材料、讨论步骤、评价标准和学生容易混淆的概念。只使用课程资料能支持的内容。",
        ("教学目标", "步骤", "评价", "并网", "混淆"),
        ("目标", "步骤", "评价"),
    ),
    Case(
        "learning_action",
        "learning_diagnosis",
        "根据我的课程学习画像，指出当前最值得优先补齐的两个知识点，并为每个知识点给出一个具体复习动作和验证方式。不要只给泛泛的鼓励。",
        ("知识", "复习", "验证"),
        ("优先", "动作"),
        needs_verified_source=False,
    ),
)


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
        timeout: float = 120,
    ) -> tuple[int, str, bytes]:
        req = urllib.request.Request(self.url(path), data=data, method=method, headers=headers or {})
        try:
            with self.opener.open(req, timeout=timeout) as response:
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
        status, final_url, body = self.request(
            "/login/index.php",
            method="POST",
            data=urllib.parse.urlencode(form).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        text = body.decode("utf-8", errors="replace").lower()
        if status != 200 or "/login/index.php" in final_url or "invalid login" in text or "loginerror" in text:
            raise RuntimeError(f"login_failed_http_{status}")

    def json_request(
        self,
        path: str,
        *,
        method: str = "POST",
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 120,
    ) -> tuple[int, dict[str, Any]]:
        merged = {"Content-Type": "application/json", **(headers or {})}
        status, _, body = self.request(
            path,
            method=method,
            data=json.dumps(payload or {}, ensure_ascii=False).encode("utf-8"),
            headers=merged,
            timeout=timeout,
        )
        try:
            return status, json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError(f"invalid_json_http_{status}") from error

    def open_session(self) -> tuple[str, str]:
        status, bridge = self.json_request("/local/course_agent/session.php")
        if status != 200:
            raise RuntimeError(f"session_bridge_http_{status}")
        sesskey = str(bridge.get("sesskey") or "")
        role = str(bridge.get("role") or "")
        if not sesskey or not role:
            raise RuntimeError("session_bridge_missing_role_or_sesskey")
        status, payload = self.json_request("/api/course/session/open")
        if status != 200:
            raise RuntimeError(f"agent_session_http_{status}")
        return role, sesskey

    def sse(self, question: str, mode: str, sesskey: str) -> dict[str, Any]:
        payload = {"question": question, "mode": mode, "session_id": None, "turn_no": None}
        req = urllib.request.Request(
            self.url("/api/course-agent/chat"),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json", "Accept": "text/event-stream", "X-Moodle-Sesskey": sesskey},
        )
        try:
            response = self.opener.open(req, timeout=180)
        except urllib.error.HTTPError as error:
            return {"http_status": error.code, "error": error.read().decode("utf-8", errors="replace")}
        event = ""
        tokens: list[str] = []
        sources: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        done = False
        with response:
            for raw in response:
                line = raw.decode("utf-8", errors="replace").rstrip("\n")
                if line.startswith("event:"):
                    event = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    try:
                        data = json.loads(line.split(":", 1)[1].strip())
                    except json.JSONDecodeError:
                        data = {"raw": line}
                    if event == "token":
                        tokens.append(str(data.get("text") or ""))
                    elif event == "source":
                        sources.append(data if isinstance(data, dict) else {"value": data})
                    elif event == "error":
                        errors.append(data if isinstance(data, dict) else {"value": data})
                    elif event == "done":
                        done = True
        return {"http_status": 200, "raw_answer": "".join(tokens), "sources": sources, "errors": errors, "done": done}


def normalize_answer(raw: str) -> str:
    text = raw.strip()
    if not text.startswith("{"):
        return text
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    if not isinstance(payload, dict):
        return text
    fields = []
    for key, value in payload.items():
        if key.lower().startswith(("answer", "response", "content", "result")) and str(value).strip():
            fields.append(str(value).strip())
    return "\n\n".join(fields) or text


def score_case(case: Case, result: dict[str, Any]) -> dict[str, Any]:
    answer = normalize_answer(str(result.get("raw_answer") or ""))
    lowered = answer.lower()
    required_hits = [term for term in case.required if term.lower() in lowered]
    shape_hits = [term for term in case.expected_shape if term.lower() in lowered]
    forbidden_hits = [term for term in case.forbidden if term.lower() in lowered]
    verified_sources = [source for source in result.get("sources", []) if source.get("status") != "unverified" and source.get("page", 0)]
    dimensions = {
        "nonempty": bool(answer.strip()),
        "substantive": len(answer.strip()) >= 120 if case.case_id != "qa_ambiguous" else len(answer.strip()) >= 40,
        "required_coverage": len(required_hits) / max(len(case.required), 1),
        "structure": len(shape_hits) / max(len(case.expected_shape), 1),
        "no_forbidden_claim": not forbidden_hits,
        "verified_source": bool(verified_sources) if case.needs_verified_source else True,
        "completed": bool(result.get("done")) and not result.get("errors") and result.get("http_status") == 200,
    }
    numeric = [float(value) for value in dimensions.values() if isinstance(value, (int, float)) and not isinstance(value, bool)]
    boolean_values = [1.0 if value else 0.0 for value in dimensions.values() if isinstance(value, bool)]
    score = round(100 * (sum(numeric) + sum(boolean_values)) / (len(numeric) + len(boolean_values)), 1)
    return {
        "case_id": case.case_id,
        "mode": case.mode,
        "question": case.question,
        "answer": answer,
        "sources": result.get("sources", []),
        "errors": result.get("errors", []),
        "dimensions": dimensions,
        "required_hits": required_hits,
        "shape_hits": shape_hits,
        "forbidden_hits": forbidden_hits,
        "score": score,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--case", action="append", dest="case_ids", help="run only the named case; repeatable")
    args = parser.parse_args()

    session = Session(args.base_url)
    try:
        session.login(args.username, args.password)
        role, sesskey = session.open_session()
        selected_cases = [case for case in CASES if not args.case_ids or case.case_id in set(args.case_ids)]
        if not selected_cases:
            raise RuntimeError("quality_case_not_found")
        if role not in {"teacher", "admin"} and not (role == "student" and all(case.mode == "learning_diagnosis" for case in selected_cases)):
            raise RuntimeError(f"quality_role_not_allowed_{role}")
        results = []
        for case in selected_cases:
            print(f"QUALITY_PROGRESS_START case={case.case_id}", flush=True)
            results.append(score_case(case, session.sse(case.question, case.mode, sesskey)))
            print(f"QUALITY_PROGRESS_DONE case={case.case_id}", flush=True)
        passed = [item for item in results if item["score"] >= 75 and item["dimensions"]["completed"]]
        avg = round(sum(item["score"] for item in results) / len(results), 1)
        payload = {"role": role, "case_count": len(results), "passed_count": len(passed), "average_score": avg, "cases": results}
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"REAL_QUALITY_EVAL {'OK' if len(passed) == len(results) else 'REVIEW'} role={role} cases={len(results)} passed={len(passed)} average={avg}")
        for item in results:
            dims = item["dimensions"]
            print(
                f"QUALITY_CASE case={item['case_id']} score={item['score']} completed={int(dims['completed'])} "
                f"coverage={dims['required_coverage']:.2f} structure={dims['structure']:.2f} "
                f"source={int(dims['verified_source'])} forbidden={int(dims['no_forbidden_claim'])}"
            )
        return 0 if len(passed) == len(results) else 2
    except RuntimeError as error:
        print(f"REAL_QUALITY_EVAL_FAILED code={error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
