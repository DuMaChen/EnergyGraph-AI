#!/usr/bin/env python3
"""Release driver for the real Xingchen knowledge base.

Logs into Moodle through the public site, resolves the Adapter session,
uploads any missing manifest PDFs, runs the three golden hit-tests against
the real Workflow, then advances the KB version to published.

Design rules (mirror the project security ledger):
- Credentials are read only from the deploy .env; values are never printed.
- Idempotency keys are stable per operation so re-runs are safe.
- --check performs login/session/version/manifest validation and (with
  --probe) a direct Workflow citation-marker probe without running hit-tests.
  Missing provider markers are informational when server-side course retrieval supplies evidence.
- Exit code 0 only when the version reaches published; anything else prints
  a bounded BLOCKED_* reason and exits non-zero.
"""
from __future__ import annotations

import argparse
import hashlib
import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_VERSION_ID = "kb-b6cbd41439a14fb3a6ce62c8081280aa"
GOLDEN_CASES = (
    ("qa-001", "请解释抽水蓄能电站的组成和工作原理。", "第3章"),
    ("qa-002", "请说明储能变流器在并网控制中的作用。", "第3章"),
    ("qa-003", "请概述电化学储能系统的规划配置要点。", "第4章"),
)
SOURCE_MARKER = re.compile(r"\[来源文件：[^；\]]+(?:；章节：[^；\]]+)?；页码：\d+\]")


def env_value(path: Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(key + "="):
            return line[len(key) + 1:].strip()
    return ""


def load_env(env_file: str) -> dict[str, str]:
    path = Path(env_file).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"ENV_FILE_MISSING {path}")
    keys = ("SITE_HOST", "MOODLE_WWWROOT", "MOODLE_ADMIN_USER", "MOODLE_ADMIN_PASSWORD",
            "XINGCHEN_WORKFLOW_URL", "XINGCHEN_FLOW_ID", "XINGCHEN_API_KEY",
            "XINGCHEN_API_SECRET", "XINGCHEN_INPUT_NAME", "COURSE_ID")
    return {key: env_value(path, key) for key in keys}


def request(opener, base: str, path: str, *, sesskey: str = "", method: str = "GET",
            payload=None, raw=None, ctype: str = "", idem: str = "", timeout: int = 60):
    headers = {"User-Agent": "EnergyGraph-AI-KB-Release/1.0"}
    if sesskey and method in ("POST", "PUT", "PATCH", "DELETE"):
        headers["X-Moodle-Sesskey"] = sesskey
    if idem:
        headers["Idempotency-Key"] = idem
    data = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
    if ctype:
        headers["Content-Type"] = ctype
    elif data is not None and raw is None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def login(opener, base: str, user: str, password: str) -> tuple[str, list[str]]:
    status, html = request(opener, base, "/login/index.php")
    match = re.search(r'name="logintoken"\s+value="([^"]+)"', html)
    form = urllib.parse.urlencode({
        "username": user, "password": password,
        "logintoken": match.group(1) if match else "",
    }).encode()
    request(opener, base, "/login/index.php", method="POST", raw=form,
            ctype="application/x-www-form-urlencoded")
    jar = next((handler.cookiejar for handler in opener.handlers
                if isinstance(handler, urllib.request.HTTPCookieProcessor)), None)
    names = sorted({cookie.name for cookie in jar}) if jar is not None else []
    return names, [name for name in names if name in ("MoodleSession", "MOODLEID1_")]


def session_bridge(opener, base: str) -> dict:
    status, text = request(opener, base, "/local/course_agent/session.php",
                          method="POST", raw=b"")
    try:
        session = json.loads(text)
    except json.JSONDecodeError:
        raise SystemExit(f"SESSION_BRIDGE_BAD status={status}")
    if not isinstance(session.get("sesskey"), str) or not session["sesskey"]:
        raise SystemExit(f"SESSION_BRIDGE_NO_SESSKEY status={status}")
    return session


def probe_workflow(env: dict[str, str]) -> dict:
    """Direct streaming call; returns bounded marker statistics only."""
    url, flow = env["XINGCHEN_WORKFLOW_URL"], env["XINGCHEN_FLOW_ID"]
    key, secret = env["XINGCHEN_API_KEY"], env["XINGCHEN_API_SECRET"]
    input_name = env["XINGCHEN_INPUT_NAME"] or "AGENT_USER_INPUT"
    if not all((url, flow, key, secret)):
        return {"blocked": "credentials_incomplete"}
    payload = {"flow_id": flow, "uid": "kb-release-probe",
               "parameters": {input_name: "请解释抽水蓄能电站的组成和工作原理。"},
               "stream": True}
    req = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode(),
                                 headers={"Authorization": f"Bearer {key}:{secret}",
                                          "Content-Type": "application/json"},
                                 method="POST")
    content, frames, code_error = "", 0, None
    with urllib.request.urlopen(req, timeout=120) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if line.startswith("data:"):
                line = line[5:].strip()
            if not line or line in ("[DONE]", "[done]"):
                continue
            try:
                frame = json.loads(line)
            except json.JSONDecodeError:
                continue
            frames += 1
            if int(frame.get("code", 0) or 0) != 0:
                code_error = frame.get("code")
            choices = frame.get("choices") or []
            if choices and isinstance(choices[0], dict):
                delta = choices[0].get("delta") or {}
                content += str(delta.get("content") or "")
    return {"frames": frames, "content_len": len(content),
            "marker_count": len(SOURCE_MARKER.findall(content)),
            "code_error": code_error}


def release_plan(version: dict, passed: int, manifest_valid: bool) -> list[str] | str:
    """Pure decision helper: ordered status transitions or BLOCKED reason."""
    status = version.get("status")
    source_count = int(version.get("source_count") or 0)
    workflow_bound = bool(version.get("workflow_id"))
    if not source_count or not manifest_valid:
        return "BLOCKED_MANIFEST_OR_FILES_MISSING"
    if not workflow_bound:
        return "BLOCKED_WORKFLOW_ID_MISSING"
    if passed < 3:
        return "BLOCKED_HIT_TESTS_NOT_PASSED"
    if status == "published":
        return []
    if status in ("failed", "processing"):
        return ["processing", "tested", "published"]
    return f"BLOCKED_UNEXPECTED_STATUS:{status}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default="deploy/.env")
    parser.add_argument("--version-id", default=DEFAULT_VERSION_ID)
    parser.add_argument("--check", action="store_true",
                        help="validate login/session/version/manifest only")
    parser.add_argument("--probe", action="store_true",
                        help="with --check, also probe workflow citation markers")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    env = load_env(str(root / args.env_file))
    site = env["SITE_HOST"] or "139.196.45.2"
    base = env["MOODLE_WWWROOT"].rstrip("/") or f"https://{site}"
    if not base.startswith(("http://", "https://")):
        base = f"https://{base}"
    if not env["MOODLE_ADMIN_USER"] or not env["MOODLE_ADMIN_PASSWORD"]:
        print("BLOCKED_ENV_CREDENTIALS_INCOMPLETE"); return 1

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    _, session_cookies = login(opener, base, env["MOODLE_ADMIN_USER"], env["MOODLE_ADMIN_PASSWORD"])
    if "MoodleSession" not in session_cookies:
        print(f"LOGIN_FAILED cookies={session_cookies}"); return 1
    session = session_bridge(opener, base)
    sesskey = str(session["sesskey"])
    role, course_id = session.get("role"), session.get("course_id")
    expected_course = int(env.get("COURSE_ID") or 1)
    print(f"LOGIN_OK role={role} course_id={course_id} sesskey_len={len(sesskey)}")
    if role not in ("teacher", "admin") or course_id != expected_course:
        print(f"SESSION_BLOCKED role={role} course_id={course_id}"); return 1

    status, text = request(opener, base, "/api/knowledge-base/versions?page_size=100", sesskey=sesskey)
    data = (json.loads(text).get("data") or {}).get("items", [])
    version = next((item for item in data if item["id"] == args.version_id), None)
    if not version:
        print("VERSION_NOT_FOUND"); return 1
    print(f"VERSION {args.version_id} status={version.get('status')} "
          f"source_count={version.get('source_count')} hit_status={version.get('hit_status')}")

    manifest_path = root / "course-data" / "normalized" / "manifest.json"
    if not manifest_path.is_file():
        print("BLOCKED_MANIFEST_MISSING"); return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if digest != version.get("manifest_sha256"):
        print(f"MANIFEST_MISMATCH local={digest[:12]} db={str(version.get('manifest_sha256'))[:12]}")
        return 1

    status, text = request(opener, base, f"/api/knowledge-base/versions/{args.version_id}/files",
                           sesskey=sesskey)
    uploaded_records = {
        str(item.get("filename")): item
        for item in (json.loads(text).get("data") or {}).get("items", [])
    }
    uploaded = set(uploaded_records)
    missing = [str(item["normalized_file"]) for item in manifest["files"]
               if str(item["normalized_file"]) not in uploaded]

    if args.check:
        print(f"CHECK_OK files_uploaded={len(uploaded)} files_missing={len(missing)} "
              f"manifest_digest={digest[:16]}")
        if args.probe:
            probe = probe_workflow(env)
            print(f"PROBE {json.dumps(probe, ensure_ascii=False)}")
            if probe.get("marker_count", 0) == 0:
                print("PROBE_NOTE provider citation markers absent; server-side course retrieval remains authoritative")
        return 0

    for item in manifest["files"]:
        fname = str(item["normalized_file"])
        path = root / "course-data" / "normalized" / fname
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != str(item["sha256"]):
            print(f"FILE_SHA_MISMATCH {fname}"); return 1
        remote_sha = str((uploaded_records.get(fname) or {}).get("sha256") or "")
        if remote_sha == str(item["sha256"]):
            print(f"UPLOAD_SKIP {fname} sha256={remote_sha[:12]}")
            continue
        query = urllib.parse.urlencode({"filename": fname})
        idem = f"kb-release-{args.version_id}-{fname}"
        status, text = request(opener, base,
                               f"/api/knowledge-base/versions/{args.version_id}/files?{query}",
                               sesskey=sesskey, method="PUT", raw=content,
                               ctype="application/pdf", idem=idem, timeout=120)
        rec = (json.loads(text).get("data") or {})
        if status not in (200, 201) or str(rec.get("sha256") or "") != str(item["sha256"]):
            print(f"UPLOAD_FAILED {fname} status={status}"); return 1

    results = {}
    for case_id, question, expected in GOLDEN_CASES:
        idem = f"kb-release-{args.version_id}-{case_id}"
        status, text = request(opener, base,
                               f"/api/knowledge-base/versions/{args.version_id}/hit-tests",
                               sesskey=sesskey, method="POST",
                               payload={"case_id": case_id}, idem=idem, timeout=300)
        resp = json.loads(text)
        rec = resp.get("data") or {}
        sources = rec.get("actual_sources") or []
        passed = rec.get("status") == "passed" and all(
            str(s.get("chapter") or "").startswith(expected) for s in sources)
        results[case_id] = passed
        print(f"HIT {case_id} status={rec.get('status')} sources={len(sources)}")
    passed = sum(results.values())
    print(f"HITS_SUMMARY passed={passed}/3")
    if passed != 3:
        print("BLOCKED_HIT_TESTS_NOT_PASSED"); return 1

    plan = release_plan(version, passed, True)
    if isinstance(plan, str):
        print(plan); return 1
    for target in plan:
        idem = f"kb-release-{args.version_id}-status-{target}"
        status, text = request(opener, base,
                               f"/api/knowledge-base/versions/{args.version_id}/status",
                               sesskey=sesskey, method="POST",
                               payload={"status": target}, idem=idem, timeout=60)
        rec = (json.loads(text).get("data") or {})
        if status not in (200, 201) or rec.get("status") != target:
            print(f"STATUS_FAILED {target} status={status}"); return 1
        print(f"STATUS_OK {target}")
    print(f"PUBLISH_OK {args.version_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
