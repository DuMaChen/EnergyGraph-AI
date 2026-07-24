from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import math
import os
import re
import sqlite3
import time
import uuid
from urllib.parse import quote, urlparse
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from .course_store import store


app = FastAPI(title="Course Agent Adapter", version="0.1.0")
logger = logging.getLogger("course-agent")


@app.middleware("http")
async def request_size_guard(request: Request, call_next: Any) -> Any:
    """Reject oversized writes before a route parses or persists their body.

    The raw knowledge-base upload endpoint has its own 20 MiB limit.  All
    other writes use a smaller JSON limit so a client cannot reserve memory by
    sending an unexpectedly large prompt, idempotency payload, or scenario
    context.  Route-level validation remains necessary for chunked requests.
    """
    if request.method in {"POST", "PUT", "PATCH"}:
        upload_path = request.url.path.endswith("/files")
        default_limit = int(os.getenv("AGENT_MAX_BODY_BYTES", str(1024 * 1024)))
        max_bytes = 20 * 1024 * 1024 if upload_path else default_limit
        declared = request.headers.get("content-length")
        if declared:
            try:
                if int(declared) > max_bytes:
                    return JSONResponse(
                        error_payload(request.headers.get("x-request-id", uuid.uuid4().hex), "request_too_large", "请求体超过大小限制"),
                        status_code=413,
                    )
            except ValueError:
                return JSONResponse(
                    error_payload(request.headers.get("x-request-id", uuid.uuid4().hex), "invalid_content_length", "请求体长度无效"),
                    status_code=400,
                )
    return await call_next(request)


@app.middleware("http")
async def same_origin_guard(request: Request, call_next: Any) -> Any:
    """Reject browser cross-site writes before they reach a state-changing API."""
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        host = request.headers.get("host", "")
        origin_host = urlparse(origin).netloc if origin else ""
        if origin and origin_host.split(":", 1)[0] != host.split(":", 1)[0]:
            return JSONResponse(error_payload(request.headers.get("x-request-id", uuid.uuid4().hex), "csrf_rejected", "请求来源不受信任"), status_code=403)
    return await call_next(request)

ALLOWED_MODES = {
    "student": {"qa", "scenario", "learning_diagnosis"},
    "teacher": {"qa", "scenario", "learning_diagnosis", "teacher_assistant", "question_draft", "grading"},
    "admin": {"qa", "scenario", "learning_diagnosis", "teacher_assistant", "question_draft", "grading"},
}
SOURCE_PATTERN = re.compile(
    r"\[来源文件：(?P<file>[^；\]]+)(?:；章节：(?P<chapter>[^；\]]+))?；页码：(?P<page>\d+)\]"
)
# This narrow guard catches explicit requests to discard course boundaries or
# fabricate evidence before either Mock or real Workflow output is displayed.
# It complements, rather than replaces, the Workflow safety branch.
POLICY_PATTERN = re.compile(r"(?:忽略|绕过|覆盖)(?:课程资料|知识库|系统规则)|(?:编造|伪造|捏造)(?:实验数据|数据集|文献|页码|引用)", re.IGNORECASE)
# These fixed questions make a release decision reproducible.  A teacher may
# inspect the wording, but cannot replace the cases with a self-authored
# "passed" flag; each case must be executed against the configured Workflow.
KB_GOLDEN_CASES = {
    "qa-001": {"question": "请解释抽水蓄能电站的组成和工作原理。", "chapter": "第3章"},
    "qa-002": {"question": "请说明储能变流器在并网控制中的作用。", "chapter": "第3章"},
    "qa-003": {"question": "请概述电化学储能系统的规划配置要点。", "chapter": "第4章"},
}


@dataclass(frozen=True)
class Identity:
    """The adapter keeps only a stable pseudonymous ID, never a real name."""

    uid: str
    role: str
    course_id: int
    csrf_token: str = ""
    moodle_user_id: int | None = None


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int, concurrent: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._timestamps: dict[str, deque[float]] = defaultdict(deque)
        self._locks: dict[str, asyncio.Semaphore] = {}
        self._guard = asyncio.Lock()
        self.concurrent = concurrent

    async def acquire(self, uid: str) -> asyncio.Semaphore | None:
        now = time.monotonic()
        async with self._guard:
            timestamps = self._timestamps[uid]
            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return None
            timestamps.append(now)
            semaphore = self._locks.setdefault(uid, asyncio.Semaphore(self.concurrent))
        await semaphore.acquire()
        return semaphore


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.lower() in {"1", "true", "yes", "on"}


def error_payload(request_id: str, code: str, message: str) -> dict[str, Any]:
    return {"request_id": request_id, "status": "error", "data": None, "error": {"code": code, "message": message}}


def policy_violation(text: str) -> bool:
    """Identify only explicit boundary-bypass or fabrication requests."""
    return bool(POLICY_PATTERN.search(text[:4000]))


def json_response(request_id: str, data: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse({"request_id": request_id, "status": "ok", "data": data, "error": None}, status_code=status_code)


async def sync_moodle_grade(
    request: Request,
    identity: Identity,
    assignment_id: str,
    moodle_user_id: int | None,
    score: float,
    max_score: float,
) -> dict[str, Any]:
    """Write a final grade to Moodle without exposing a database credential.

    The bridge is intentionally best-effort for local/mock mode, but a real
    deployment reports a failed bridge instead of claiming gradebook parity.
    """
    if env_bool("MOCK_AUTH_MODE"):
        return {"status": "mock_skipped"}
    cookie = request.headers.get("cookie", "")
    bridge_token = os.getenv("AGENT_BRIDGE_TOKEN", "")
    if not moodle_user_id or not cookie or not bridge_token:
        return {"status": "not_configured"}
    url = os.getenv("MOODLE_GRADE_SYNC_URL", "http://moodle/local/course_agent/grade-sync.php")
    payload = {
        "course_id": identity.course_id,
        "assignment_id": assignment_id,
        "user_id": moodle_user_id,
        "score": max(0.0, min(float(score), float(max_score))),
        "max_score": float(max_score),
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                headers={"cookie": cookie, "X-Agent-Bridge-Token": bridge_token, "Content-Type": "application/json"},
                json=payload,
            )
    except httpx.HTTPError:
        logger.warning("moodle grade bridge network failure assignment=%s request=%s", assignment_id, request.headers.get("x-request-id", ""))
        return {"status": "failed", "code": "bridge_network_error"}
    if response.status_code != 200:
        logger.warning("moodle grade bridge HTTP %s assignment=%s", response.status_code, assignment_id)
        return {"status": "failed", "code": "bridge_http_error", "http_status": response.status_code}
    return {"status": "synced"}


def stable_uid(raw_user_id: Any) -> str:
    salt = os.getenv("AGENT_UID_SALT", "development-only-change-me").encode("utf-8")
    digest = hmac.new(salt, str(raw_user_id).encode("utf-8"), hashlib.sha256).hexdigest()
    return f"u_{digest[:24]}"


def load_manifest() -> dict[str, Any]:
    path = Path(os.getenv("COURSE_MANIFEST", "/app/course-data/manifest.json"))
    if not path.exists():
        return {"files": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"files": []}


MANIFEST = load_manifest()


def manifest_digest() -> str:
    """Return the server-owned course manifest digest for version tracking."""
    path = Path(os.getenv("COURSE_MANIFEST", "/app/course-data/manifest.json"))
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "unavailable"


def validate_sources(text: str) -> list[dict[str, Any]]:
    """Accept source events only when they match the versioned local manifest."""
    allowed = {str(item.get("source_file")): item for item in MANIFEST.get("files", [])}
    sources: list[dict[str, Any]] = []
    published = store.published_kb()
    version_name = str(published["version_name"]) if published else str(MANIFEST.get("source_archive", "unknown"))
    version_id = str(published["id"]) if published else "local-manifest"
    for match in SOURCE_PATTERN.finditer(text):
        file_name = match.group("file").strip()
        page = int(match.group("page"))
        item = allowed.get(file_name)
        if not item:
            continue
        page_count = item.get("page_count")
        if isinstance(page_count, int) and page_count > 0 and page > page_count:
            # A model-generated page number outside the manifest is not an
            # evidence link, even when the filename itself is valid.
            continue
        expected_chapter = str(item.get("chapter", ""))
        chapter = match.group("chapter") or expected_chapter
        if expected_chapter and chapter != expected_chapter:
            # A valid filename paired with a fabricated chapter is still not
            # evidence; the UI must show the answer as awaiting verification.
            continue
        sources.append(
            {
                "source_id": hashlib.sha256(f"{file_name}:{page}".encode("utf-8")).hexdigest()[:20],
                "file": file_name,
                "chapter": chapter,
                "page": page,
                "sha256": str(item.get("sha256", "")),
                "resource_id": "res-" + hashlib.sha256(f"{item.get('normalized_file', '')}:{item.get('chapter_id', '')}".encode()).hexdigest()[:20],
                "version": version_name,
                "kb_version_id": version_id,
            }
        )
    unique: dict[str, dict[str, Any]] = {source["source_id"]: source for source in sources}
    return list(unique.values())


async def resolve_identity(request: Request) -> Identity:
    if env_bool("MOCK_AUTH_MODE"):
        role = request.headers.get("x-dev-role", "student")
        user_id = request.headers.get("x-dev-user", "demo-student")
        if role not in ALLOWED_MODES:
            raise PermissionError("invalid role")
        return Identity(stable_uid(user_id), role, int(os.getenv("MOCK_COURSE_ID", "1")), "mock-csrf", None)

    cookie = request.headers.get("cookie")
    if not cookie:
        raise PermissionError("login required")
    session_url = os.getenv("MOODLE_SESSION_URL", "http://moodle/local/course_agent/session.php")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(session_url, headers={"cookie": cookie})
    except httpx.HTTPError as exc:
        raise ConnectionError("Moodle session service unavailable") from exc
    if response.status_code in {301, 302, 303, 307, 308, 401, 403}:
        raise PermissionError("login required")
    if response.status_code != 200:
        raise ConnectionError("Moodle session service returned an error")
    try:
        data = response.json()
        return Identity(
            stable_uid(data["user_id"]),
            str(data["role"]),
            int(data["course_id"]),
            str(data.get("sesskey", "")),
            int(data["user_id"]),
        )
    except (ValueError, KeyError, TypeError) as exc:
        raise ConnectionError("invalid Moodle session response") from exc


def mode_from_request(identity: Identity, body: dict[str, Any]) -> str:
    mode = body.get("mode")
    if not isinstance(mode, str) or mode not in ALLOWED_MODES.get(identity.role, set()):
        raise ValueError("mode is not allowed for this role")
    return mode


def build_parameters(
    identity: Identity,
    mode: str,
    question: str,
    graph_context: str = "",
    learning_profile: str = "",
    scenario_context: str = "",
    rubric: str = "",
) -> dict[str, Any]:
    # These values are server-owned. Client-supplied graph/profile/rubric fields
    # are deliberately ignored; callers must provide IDs and the Adapter loads
    # the permission-filtered records itself, preventing prompt injection through
    # trusted context slots.
    return {
        os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT"): question,
        "AGENT_MODE": mode,
        # The Workflow must receive the role from the authenticated session,
        # never from a browser field. This keeps scenario and diagnosis
        # prompts consistent when the same page is used by students or staff.
        "STUDENT_ROLE": identity.role,
        "KNOWLEDGE_GRAPH_CONTEXT": graph_context,
        "LEARNING_PROFILE": learning_profile,
        "SCENARIO_CONTEXT": scenario_context,
        "RUBRIC": rubric,
    }


def authorization_header() -> str:
    key = os.getenv("XINGCHEN_API_KEY", "")
    secret = os.getenv("XINGCHEN_API_SECRET", "")
    if not key or not secret:
        raise RuntimeError("Xingchen credentials are not configured")
    return f"Bearer {key}:{secret}"


def parse_frame(raw: str) -> dict[str, Any] | None:
    line = raw.strip()
    if not line:
        return None
    if line.startswith("data:"):
        line = line[5:].strip()
    if line in {"[DONE]", "[done]"}:
        return {"_done": True}
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return {"_error": "malformed_upstream_frame"}
    if not isinstance(payload, dict):
        return {"_error": "invalid_upstream_frame"}
    return payload


def frame_content(frame: dict[str, Any]) -> str:
    choices = frame.get("choices") or []
    if not choices or not isinstance(choices[0], dict):
        return ""
    delta = choices[0].get("delta") or choices[0].get("message") or {}
    return str(delta.get("content") or "") if isinstance(delta, dict) else ""


async def mock_stream(question: str, request_id: str, mode: str = "qa") -> AsyncIterator[dict[str, Any]]:
    # The grading branch uses the same JSON contract expected from the real
    # Workflow, which lets local tests exercise score bounds and review state.
    if mode == "grading":
        content = json.dumps({"score": 6, "feedback": "Mock 初评：覆盖部分评分要点，需教师复核。"}, ensure_ascii=False)
    else:
        if "规划配置" in question or "电化学" in question:
            source = "4.2 电化学储能系统的规划配置.pdf；章节：第4章 电力储能系统的规划配置；页码：1"
        elif "变流器" in question:
            source = "3.4 储能变流器拓扑及并网控制.pdf；章节：第3章 电力储能系统的组成及工作原理；页码：1"
        else:
            source = "3.1 抽水蓄能电站的组成及工作原理.pdf；章节：第3章 电力储能系统的组成及工作原理；页码：1"
        content = f"[MOCK_WORKFLOW] 已收到问题：{question[:160]}\n[来源文件：{source}]\n当前为讯飞 Workflow 协议测试模式。"
    yield {"event": "token", "data": {"text": content, "request_id": request_id}}
    # Keep mock and real Workflow event contracts identical.  The local KB
    # release fixture must exercise source evidence, not merely text output.
    for source_event in validate_sources(content):
        yield {"event": "source", "data": {**source_event, "request_id": request_id}}
    yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}


async def xingchen_stream(
    parameters: dict[str, Any], identity: Identity, request_id: str, workflow_id: str | None = None
) -> AsyncIterator[dict[str, Any]]:
    if env_bool("MOCK_WORKFLOW_MODE"):
        async for event in mock_stream(
            str(parameters.get(os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT"), "")),
            request_id,
            str(parameters.get("AGENT_MODE", "qa")),
        ):
            yield event
        return

    published = store.published_kb()
    # A real answer must be tied to a released course KB. A Workflow
    # credential alone is not enough: otherwise a general-purpose Flow could
    # appear healthy while never using the course material.
    if not workflow_id and not published:
        yield {"event": "error", "data": {"code": "knowledge_base_not_published", "message": "课程知识库尚未发布", "request_id": request_id}}
        return
    # A release test passes the Workflow ID stored on that KB version. The
    # environment value remains the default only for legacy deployments where
    # the published version has no explicit binding.
    flow_id = workflow_id or str(published.get("workflow_id") if published else "") or os.getenv("XINGCHEN_FLOW_ID", "")
    url = os.getenv("XINGCHEN_WORKFLOW_URL", "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions")
    if not flow_id:
        yield {"event": "error", "data": {"code": "workflow_not_configured", "message": "Workflow 尚未配置", "request_id": request_id}}
        return
    payload = {"flow_id": flow_id, "uid": identity.uid, "parameters": parameters, "stream": True}
    try:
        timeout = float(os.getenv("XINGCHEN_TIMEOUT_SECONDS", "90"))
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=10)) as client:
            async with client.stream("POST", url, headers={"Authorization": authorization_header(), "Content-Type": "application/json"}, json=payload) as response:
                if response.status_code in {401, 403}:
                    yield {"event": "error", "data": {"code": "workflow_auth_failed", "message": "讯飞 Workflow 鉴权失败", "request_id": request_id}}
                    return
                if response.status_code >= 400:
                    yield {"event": "error", "data": {"code": "workflow_upstream_error", "message": f"讯飞 Workflow 返回 HTTP {response.status_code}", "request_id": request_id}}
                    return
                saw_done = False
                source_buffer = ""
                emitted_source_ids: set[str] = set()
                async for line in response.aiter_lines():
                    frame = parse_frame(line)
                    if frame is None:
                        continue
                    if frame.get("_error"):
                        yield {"event": "error", "data": {"code": frame["_error"], "message": "讯飞返回了无法解析的数据", "request_id": request_id}}
                        return
                    if frame.get("_done"):
                        saw_done = True
                        break
                    if int(frame.get("code", 0) or 0) != 0:
                        yield {"event": "error", "data": {"code": f"xingchen_{frame.get('code')}", "message": "讯飞 Workflow 执行失败", "sid": frame.get("id"), "request_id": request_id}}
                        return
                    text = frame_content(frame)
                    if text:
                        yield {"event": "token", "data": {"text": text, "request_id": request_id}}
                        # Markers can be split across upstream frames. Keep a
                        # bounded buffer so a valid citation is not lost, but
                        # never allow a long model response to grow memory.
                        source_buffer = (source_buffer + text)[-12000:]
                    for source in validate_sources(source_buffer):
                        if source["source_id"] in emitted_source_ids:
                            continue
                        emitted_source_ids.add(source["source_id"])
                        yield {"event": "source", "data": {**source, "request_id": request_id}}
                    choices = frame.get("choices") or []
                    finish_reason = choices[0].get("finish_reason") if choices and isinstance(choices[0], dict) else None
                    if finish_reason == "stop":
                        saw_done = True
                        break
                if not saw_done:
                    yield {"event": "error", "data": {"code": "upstream_disconnected", "message": "讯飞 Workflow 流式连接中断", "request_id": request_id}}
                    return
                if not emitted_source_ids:
                    # Never invent a citation when the Workflow did not return
                    # a marker. The UI can then present an explicit review
                    # state instead of treating the answer as course evidence.
                    published = store.published_kb()
                    yield {"event": "source", "data": {"source_id": "unverified", "file": "", "chapter": "", "page": 0, "version": str(published["version_name"] if published else MANIFEST.get("source_archive", "unknown")), "status": "unverified", "request_id": request_id}}
                yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}
    except httpx.TimeoutException:
        yield {"event": "error", "data": {"code": "workflow_timeout", "message": "讯飞 Workflow 请求超时，请重试", "request_id": request_id}}
    except httpx.HTTPError:
        yield {"event": "error", "data": {"code": "workflow_network_error", "message": "讯飞 Workflow 暂时不可用，请重试", "request_id": request_id}}


limiter = SlidingWindowLimiter(
    int(os.getenv("AGENT_RATE_LIMIT", "20")),
    int(os.getenv("AGENT_RATE_WINDOW_SECONDS", "60")),
    int(os.getenv("AGENT_USER_CONCURRENCY", "1")),
)


@app.get("/health")
async def health() -> dict[str, Any]:
    salt = os.getenv("AGENT_UID_SALT", "")
    credentials_ready = bool(os.getenv("XINGCHEN_FLOW_ID") and os.getenv("XINGCHEN_API_KEY") and os.getenv("XINGCHEN_API_SECRET"))
    return {
        "status": "ok",
        "service": "course-agent-adapter",
        "workflow_configured": credentials_ready,
        "security_configured": bool(salt and "replace-with" not in salt and "development-only" not in salt),
        "mock_workflow": env_bool("MOCK_WORKFLOW_MODE"),
    }


@app.get("/api/admin/status")
async def admin_status(request: Request) -> JSONResponse:
    """Expose a redacted operations view; never return credentials or raw URLs."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"admin"})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "只有管理员可以查看服务状态"), status_code=403)
    workflow_ready = bool(os.getenv("XINGCHEN_FLOW_ID") and os.getenv("XINGCHEN_API_KEY") and os.getenv("XINGCHEN_API_SECRET"))
    published = store.published_kb()
    return json_response(request_id, {
        "adapter": "healthy",
        "workflow_configured": workflow_ready,
        "mock_workflow": env_bool("MOCK_WORKFLOW_MODE"),
        "published_kb": {
            "id": published["id"],
            "version_name": published["version_name"],
            "status": published["status"],
            "hit_status": published["hit_status"],
        } if published else None,
        # Host-level backup jobs are intentionally not controlled from the
        # browser. This flag tells the admin where the authoritative check is.
        "backup": {"managed_by": "host-cron", "status": "verify_on_server"},
    })


@app.post("/api/course/session/open")
async def session_open(request: Request) -> JSONResponse:
    request_id = uuid.uuid4().hex
    try:
        identity = await resolve_identity(request)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "unauthorized", "请先登录课程平台"), status_code=401)
    except ConnectionError:
        return JSONResponse(error_payload(request_id, "auth_service_unavailable", "课程会话服务暂不可用"), status_code=502)
    features = {
        "qa": "qa" in ALLOWED_MODES.get(identity.role, set()),
        "scenario": "scenario" in ALLOWED_MODES.get(identity.role, set()),
        "learning_diagnosis": "learning_diagnosis" in ALLOWED_MODES.get(identity.role, set()),
        "teacher_assistant": "teacher_assistant" in ALLOWED_MODES.get(identity.role, set()),
        "question_draft": "question_draft" in ALLOWED_MODES.get(identity.role, set()),
        "grading": "grading" in ALLOWED_MODES.get(identity.role, set()),
    }
    return json_response(request_id, {
        "role": identity.role,
        "course_id": identity.course_id,
        "csrf_token": identity.csrf_token,
        "features": features,
        "chapters": store.chapters(),
        "graph_summary": {"chapters": len(store.chapters()), "knowledge_points": len(store.search_nodes("", 100))},
    })


async def authenticated(request: Request) -> tuple[Identity | None, JSONResponse | None, str]:
    """Resolve Moodle identity once per request and keep errors uniform."""
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    try:
        identity = await resolve_identity(request)
        # Same-origin cookies alone are not enough for browser writes. Moodle's
        # sesskey is checked centrally so a newly added POST/PATCH endpoint
        # cannot accidentally omit its CSRF protection.
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not env_bool("MOCK_AUTH_MODE"):
            supplied = request.headers.get("x-moodle-sesskey", "")
            if not supplied or not identity.csrf_token or not hmac.compare_digest(supplied, identity.csrf_token):
                return None, JSONResponse(error_payload(request_id, "csrf_rejected", "缺少有效的课程防重放令牌"), status_code=403), request_id
        return identity, None, request_id
    except PermissionError:
        return None, JSONResponse(error_payload(request_id, "unauthorized", "请先登录课程平台"), status_code=401), request_id
    except ConnectionError:
        return None, JSONResponse(error_payload(request_id, "auth_service_unavailable", "课程会话服务暂不可用"), status_code=502), request_id


def require_role(identity: Identity, roles: set[str]) -> None:
    if identity.role not in roles:
        raise PermissionError("permission_denied")


def idempotency_error(request: Request, request_id: str, identity: Identity) -> JSONResponse | None:
    """All state-changing teaching operations must be safe to retry."""
    if not env_bool("MOCK_AUTH_MODE") and request.headers.get("x-moodle-sesskey", "") != identity.csrf_token:
        return JSONResponse(error_payload(request_id, "csrf_rejected", "课程会话令牌无效或已过期"), status_code=403)
    key = request.headers.get("idempotency-key", "")
    if not key or len(key) > 128:
        return JSONResponse(error_payload(request_id, "missing_idempotency_key", "写操作必须携带 Idempotency-Key"), status_code=422)
    return None


def paginate(items: list[Any], page: int, page_size: int) -> tuple[dict[str, Any] | None, int]:
    """Apply a hard page-size cap before serializing any list response."""
    if page < 1 or page_size < 1 or page_size > 100:
        return None, 422
    total = len(items)
    start = (page - 1) * page_size
    return {"items": items[start : start + page_size], "total": total, "page": page, "page_size": page_size}, 200


def deterministic_recommendations(profile: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Choose only existing course resources from the versioned rule output."""
    recommendations: list[dict[str, Any]] = []
    unavailable: list[str] = []
    for node in profile["nodes"]:
        status = node["status"]
        if status == "weak" and node.get("prerequisite_gap"):
            recommendation_type = "基础补齐"
            reason = "先修知识点存在薄弱或未评估状态"
        elif node.get("recent_error"):
            recommendation_type = "错题复习"
            reason = "最近一次有效提交存在错误或空答"
        elif status in {"weak", "learning"}:
            recommendation_type = "章节巩固"
            reason = "知识点尚未达到掌握门槛"
        elif status == "mastered" and not node.get("prerequisite_gap"):
            recommendation_type = "综合应用"
            reason = "知识点已掌握且先修关系满足"
        else:
            continue
        resources = store.resources(node_id=node["id"])
        if not resources:
            unavailable.append(node["id"])
            continue
        resource = resources[0]
        recommendations.append({
            "type": recommendation_type,
            "node_id": node["id"],
            "title": node["name"],
            "reason": reason,
            "resource_id": resource["id"],
            "source_file": resource["source_file"],
            "page": resource["page_start"],
        })
    return recommendations[:20], unavailable


@app.get("/api/knowledge-graph/chapters")
async def graph_chapters(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    return json_response(request_id, {"items": store.chapters(), "total": len(store.chapters())})


@app.get("/api/knowledge-graph/nodes/{node_id}")
async def graph_node(node_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    node = store.node(node_id)
    if not node:
        return JSONResponse(error_payload(request_id, "not_found", "知识点不存在"), status_code=404)
    return json_response(request_id, node)


@app.get("/api/knowledge-graph/search")
async def graph_search(request: Request, q: str = "", limit: int = 20, page: int = 1, page_size: int = 20) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if limit < 1 or limit > 100 or len(q) > 100:
        return JSONResponse(error_payload(request_id, "invalid_input", "搜索参数超出限制"), status_code=422)
    items = store.search_nodes(q, limit)
    data, status = paginate(items, page, page_size)
    if data is None:
        return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
    return json_response(request_id, data)


@app.get("/api/knowledge-graph/nodes/{node_id}/neighbors")
async def graph_neighbors(node_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    node = store.node(node_id)
    if not node:
        return JSONResponse(error_payload(request_id, "not_found", "知识点不存在"), status_code=404)
    return json_response(request_id, {"items": node["neighbors"]})


@app.get("/api/knowledge-graph/paths")
async def graph_path(request: Request, start_id: str = "", end_id: str = "", from_: str = "", to: str = "", max_depth: int = 8) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    start_id = start_id or request.query_params.get("from", "") or from_
    end_id = end_id or to
    if not start_id or not end_id or max_depth < 1 or max_depth > 12:
        return JSONResponse(error_payload(request_id, "invalid_input", "路径参数无效"), status_code=422)
    path = store.path(start_id, end_id, max_depth)
    if path is None:
        return JSONResponse(error_payload(request_id, "not_found", "未找到有限先修路径"), status_code=404)
    return json_response(request_id, {"path": path, "depth": len(path) - 1})


@app.get("/api/textbook/resources")
async def textbook_resources(request: Request, chapter_id: int | None = None, node_id: str | None = None, page: int = 1, page_size: int = 20) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if chapter_id is not None and chapter_id not in range(1, 7):
        return JSONResponse(error_payload(request_id, "invalid_input", "章节参数无效"), status_code=422)
    data, status = paginate(store.resources(chapter_id, node_id), page, page_size)
    if data is None:
        return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
    return json_response(request_id, data)


@app.get("/api/knowledge-points/{node_id}/resources")
async def knowledge_point_resources(node_id: str, request: Request, page: int = 1, page_size: int = 20) -> JSONResponse:
    """Return resources attached to a graph node after session validation."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if not store.node(node_id):
        return JSONResponse(error_payload(request_id, "not_found", "知识点不存在"), status_code=404)
    data, status = paginate(store.resources(node_id=node_id), page, page_size)
    if data is None:
        return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
    return json_response(request_id, data)


@app.get("/api/textbook/resources/{resource_id}")
async def textbook_resource(resource_id: str, request: Request, page: int = 1) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    resource = store.resource(resource_id)
    if not resource:
        return JSONResponse(error_payload(request_id, "not_found", "教材资源不存在"), status_code=404)
    if page < 1 or (resource.get("page_end") and page > int(resource["page_end"])):
        return JSONResponse(error_payload(request_id, "invalid_input", "教材页码待核验"), status_code=422)
    # The PDF remains Moodle-owned; return a constrained locator rather than
    # exposing a filesystem path from the Adapter container.
    locator = "/local/course_agent/resource.php?source=" + quote(str(resource["normalized_file"]), safe="") + f"&page={page}"
    return json_response(request_id, {"resource": resource, "page": page, "locator": locator})


@app.get("/api/textbook/resources/{resource_id}/pages/{page_number}")
async def textbook_resource_page(resource_id: str, page_number: int, request: Request) -> JSONResponse:
    # Keep the page form as an explicit alias so clients cannot accidentally
    # treat a missing page as a valid citation.
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    if page_number < 1:
        return JSONResponse(error_payload(request_id, "invalid_input", "教材页码待核验"), status_code=422)
    return await textbook_resource(resource_id, request, page_number)


@app.get("/api/knowledge-base/versions")
async def kb_list(request: Request, page: int = 1, page_size: int = 20) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库管理权限"), status_code=403)
    data, status = paginate(store.kb_versions(), page, page_size)
    if data is None:
        return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
    return json_response(request_id, data)


@app.post("/api/knowledge-base/versions")
async def kb_create(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        name = str(body.get("version_name", "")).strip()
        if not name or len(name) > 100:
            raise ValueError
        idem_key = request.headers["idempotency-key"]
        previous, found = store.idempotent(identity.uid, "/knowledge-base/versions", idem_key, body)
        if found:
            return json_response(request_id, previous)
        # A browser may supply a label, but the release record must point to
        # the exact manifest mounted by this Adapter instance.
        version_payload = {**body, "manifest_sha256": manifest_digest()}
        result = store.create_kb_version(identity.uid, version_payload)
        store.save_idempotent(identity.uid, "/knowledge-base/versions", idem_key, body, result)
        return json_response(request_id, result, 201)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库管理权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "知识库版本名称无效"), status_code=422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_input", "知识库版本名称无效"), status_code=422)


@app.post("/api/knowledge-base/versions/{version_id}/status")
async def kb_status(version_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        idem_key = request.headers["idempotency-key"]
        request_body = {"version_id": version_id, "status": body.get("status"), "hit_status": body.get("hit_status")}
        previous, found = store.idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/status", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.update_kb_status(version_id, str(body.get("status")), identity.uid, str(body.get("hit_status", "")) or None)
        if not result:
            return JSONResponse(error_payload(request_id, "not_found", "知识库版本不存在"), status_code=404)
        store.save_idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/status", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库管理权限"), status_code=403)
    except ValueError as exc:
        code = "conflict" if str(exc) == "invalid_kb_transition" else "invalid_input"
        return JSONResponse(error_payload(request_id, code, "知识库状态不能直接跳转"), status_code=409 if code == "conflict" else 422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_body", "请求格式错误"), status_code=422)


@app.get("/api/knowledge-base/versions/{version_id}/hit-tests")
async def kb_hit_test_list(version_id: str, request: Request) -> JSONResponse:
    """Show bounded golden-test evidence without exposing credentials or text logs."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})
        return json_response(request_id, {"items": store.kb_hit_tests(version_id), "required": list(KB_GOLDEN_CASES)})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库测试权限"), status_code=403)


@app.post("/api/knowledge-base/versions/{version_id}/hit-tests")
async def kb_hit_test(version_id: str, request: Request) -> JSONResponse:
    """Run one fixed question through the real configured Workflow before release."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        case_id = str(body.get("case_id", ""))
        case = KB_GOLDEN_CASES.get(case_id)
        if not case:
            return JSONResponse(error_payload(request_id, "invalid_input", "黄金问题编号无效"), status_code=422)
        version = next((item for item in store.kb_versions() if item["id"] == version_id), None)
        if not version or version["status"] not in {"processing", "tested", "failed"}:
            return JSONResponse(error_payload(request_id, "conflict", "当前版本不可执行命中测试"), status_code=409)
        idem_key = request.headers["idempotency-key"]
        request_body = {"version_id": version_id, "case_id": case_id}
        previous, found = store.idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/hit-tests", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        parameters = build_parameters(identity, "qa", str(case["question"]))
        sources: list[dict[str, Any]] = []
        upstream_error: dict[str, Any] | None = None
        async for event in xingchen_stream(parameters, identity, request_id, str(version.get("workflow_id") or "") or None):
            if event["event"] == "source" and event["data"].get("status") != "unverified":
                sources.append(event["data"])
            elif event["event"] == "error":
                upstream_error = event["data"]
        passed = bool(sources) and all(str(source.get("chapter", "")).startswith(str(case["chapter"])) for source in sources)
        result = store.save_kb_hit_test(version_id, case_id, str(case["question"]), str(case["chapter"]), sources, "passed" if passed else "failed", request_id, identity.uid)
        store.save_idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/hit-tests", idem_key, request_body, result)
        if upstream_error:
            return JSONResponse(error_payload(request_id, "workflow_test_failed", "Workflow 命中测试失败，请检查发布状态和来源标记"), status_code=502)
        return json_response(request_id, result, 200 if passed else 422)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库测试权限"), status_code=403)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_body", "测试请求格式错误"), status_code=422)


@app.get("/api/knowledge-base/versions/{version_id}/files")
async def kb_files(version_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})
        return json_response(request_id, {"items": store.kb_files(version_id)})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库管理权限"), status_code=403)


@app.post("/api/knowledge-base/versions/{version_id}/rollback")
async def kb_rollback(version_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        reason = str(body.get("reason", "")).strip()
        if not reason:
            return JSONResponse(error_payload(request_id, "invalid_input", "回滚必须填写原因"), status_code=422)
        idem_key = request.headers["idempotency-key"]
        request_body = {"version_id": version_id, "reason": reason}
        previous, found = store.idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/rollback", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.rollback_kb(version_id, identity.uid, reason)
        if not result:
            return JSONResponse(error_payload(request_id, "not_found", "知识库版本不存在"), status_code=404)
        store.save_idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/rollback", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库管理权限"), status_code=403)
    except ValueError:
        return JSONResponse(error_payload(request_id, "conflict", "该版本未通过回滚门槛"), status_code=409)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_body", "请求格式错误"), status_code=422)


@app.put("/api/knowledge-base/versions/{version_id}/files")
async def kb_upload(version_id: str, request: Request, filename: str = "") -> JSONResponse:
    """Accept a raw PDF body and keep it outside the public web root."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        safe_name = Path(filename).name
        suffix = Path(filename).suffix.lower()
        if (
            not filename
            or safe_name != filename
            or "\\" in filename
            or any(ord(char) < 32 for char in filename)
            or len(filename) > 180
            or suffix not in {".pdf", ".md"}
        ):
            return JSONResponse(error_payload(request_id, "invalid_file", "只允许使用安全的 PDF 或 Markdown 文件名"), status_code=422)
        declared_length = request.headers.get("content-length")
        if declared_length:
            try:
                if int(declared_length) > 20 * 1024 * 1024:
                    return JSONResponse(error_payload(request_id, "invalid_file", "文件超过 20MB 限制"), status_code=422)
            except ValueError:
                return JSONResponse(error_payload(request_id, "invalid_file", "文件长度无效"), status_code=422)
        content = await request.body()
        max_bytes = 20 * 1024 * 1024
        if suffix == ".pdf":
            # A magic header alone accepts arbitrary bytes renamed to .pdf.
            # Requiring an EOF marker in the tail catches the common fake-file
            # case while keeping the check dependency-free in the API image.
            valid_content = content.startswith(b"%PDF-") and b"%%EOF" in content[-4096:]
        else:
            try:
                content.decode("utf-8")
                valid_content = bool(content.strip()) and b"\x00" not in content
            except UnicodeDecodeError:
                valid_content = False
        if not content or len(content) > max_bytes or not valid_content:
            return JSONResponse(error_payload(request_id, "invalid_file", "文件为空、超过 20MB 或不是有效 PDF/Markdown"), status_code=422)
        idem_key = request.headers["idempotency-key"]
        request_body = {"version_id": version_id, "filename": safe_name, "sha256": hashlib.sha256(content).hexdigest()}
        previous, found = store.idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/files", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        record = store.add_kb_file(version_id, safe_name, content)
        storage_root = Path(os.getenv("KB_STORAGE_DIR", "/app/data/kb-files")) / version_id
        storage_root.mkdir(parents=True, exist_ok=True)
        target = storage_root / safe_name
        if not target.exists():
            target.write_bytes(content)
        store.save_idempotent(identity.uid, f"/knowledge-base/versions/{version_id}/files", idem_key, request_body, record)
        return json_response(request_id, record, 201)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有知识库管理权限"), status_code=403)
    except LookupError:
        return JSONResponse(error_payload(request_id, "not_found", "知识库版本不存在"), status_code=404)
    except ValueError:
        return JSONResponse(error_payload(request_id, "conflict", "该知识库版本当前不可上传"), status_code=409)


@app.get("/api/student/learning-profile")
@app.get("/api/learning/profile")
async def learning_profile(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    profile = store.learning_profile(identity.uid)
    return json_response(request_id, profile)


@app.get("/api/student/recommendations")
@app.get("/api/learning/recommendations")
async def learning_recommendations(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    profile = store.learning_profile(identity.uid)
    recommendations, unavailable = deterministic_recommendations(profile)
    return json_response(request_id, {"rule_version": "learning-rule-v1", "items": recommendations, "unavailable_nodes": unavailable})


@app.post("/api/student/learning-diagnosis")
async def learning_diagnosis(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    profile = store.learning_profile(identity.uid)
    recommendations, unavailable = deterministic_recommendations(profile)
    # Keep the recommendation set deterministic and let the Workflow explain
    # it. The model therefore cannot invent a knowledge point or alter a
    # mastery status calculated by CourseStore.
    graph_context = json.dumps(
        [{"id": item["node_id"], "name": item["title"], "resource_id": item["resource_id"]} for item in recommendations[:20]],
        ensure_ascii=False,
    )
    try:
        request_body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    except (TypeError, json.JSONDecodeError):
        request_body = {}
    question = str(request_body.get("question", "请解释我的学习状态并给出复习建议。"))[:int(os.getenv("AGENT_MAX_INPUT_CHARS", "4000"))]
    if policy_violation(question):
        return JSONResponse(error_payload(request_id, "policy_blocked", "不能要求系统伪造学习证据或课程来源"), status_code=422)
    parameters = build_parameters(
        identity,
        "learning_diagnosis",
        question,
        graph_context=graph_context,
        learning_profile=json.dumps({"rule_version": profile["rule_version"], "nodes": profile["nodes"]}, ensure_ascii=False),
    )
    chunks: list[str] = []
    sources: list[dict[str, Any]] = []
    upstream_error: dict[str, Any] | None = None
    async for event in xingchen_stream(parameters, identity, request_id):
        if event["event"] == "token":
            chunks.append(str(event["data"].get("text", "")))
        elif event["event"] == "source" and event["data"].get("status") != "unverified":
            # Preserve the same manifest-validated evidence contract as QA;
            # diagnosis text must not become an untraceable exception.
            sources.append(event["data"])
        elif event["event"] == "error":
            upstream_error = event["data"]
    if upstream_error:
        return JSONResponse(error_payload(request_id, "learning_agent_failed", "学习诊断 Agent 暂不可用，请稍后重试"), status_code=502)
    return json_response(request_id, {
        "rule_version": "learning-rule-v1",
        "profile": profile,
        "recommendations": recommendations[:20],
        "unavailable_nodes": unavailable,
        "ai_explanation": "".join(chunks),
        "ai_generated": True,
        "sources": sources,
    })


@app.get("/api/teacher/students/{student_uid}/learning-profile")
async def teacher_student_learning_profile(student_uid: str, request: Request) -> JSONResponse:
    """Expose only pseudonymous student metrics to authorized course staff."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})
        if not re.fullmatch(r"u_[0-9a-f]{24}", student_uid):
            return JSONResponse(error_payload(request_id, "not_found", "学生学情不存在"), status_code=404)
        return json_response(request_id, store.learning_profile(student_uid))
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有查看学生学情的权限"), status_code=403)


@app.post("/api/scenarios/start")
async def scenario_start(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        body = await request.json()
        scenario_key = str(body.get("scenario_key", "grid-dispatch"))
        if scenario_key not in {"grid-dispatch", "battery-fault"}:
            raise ValueError
        idem_key = request.headers["idempotency-key"]
        request_body = {"scenario_key": scenario_key}
        previous, found = store.idempotent(identity.uid, "/scenarios/start", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.create_scenario(identity.uid, scenario_key)
        store.save_idempotent(identity.uid, "/scenarios/start", idem_key, request_body, result)
        return json_response(request_id, result, 201)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "场景参数无效"), status_code=422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_input", "场景参数无效"), status_code=422)


@app.post("/api/scenarios/{session_id}/turn")
async def scenario_turn(session_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        body = await request.json()
        turn_no = int(body.get("turn_no"))
        # Accept the public `text` field and the older test/client alias.
        text_value = str(body.get("text", body.get("user_input", ""))).strip()
        if turn_no < 1 or not text_value or len(text_value) > int(os.getenv("AGENT_MAX_INPUT_CHARS", "4000")):
            raise ValueError
        if policy_violation(text_value):
            raise ValueError("policy_blocked")
        idem_key = request.headers["idempotency-key"]
        request_body = {"session_id": session_id, "turn_no": turn_no, "text": text_value}
        previous, found = store.idempotent(identity.uid, f"/scenarios/{session_id}/turn", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        scenario = store.scenario(identity.uid, session_id)
        if not scenario:
            raise LookupError("scenario_not_found")
        turn = store.add_turn(identity.uid, session_id, turn_no, text_value, request_id)
        if turn.get("status") == "completed":
            # A different idempotency key must not replay a completed turn as a
            # new upstream call; the client should reuse its original key.
            return JSONResponse(error_payload(request_id, "conflict", "该场景轮次已经完成，请使用原幂等键查询结果"), status_code=409)
        if turn.get("request_id") != request_id:
            return JSONResponse(error_payload(request_id, "conflict", "该场景轮次正在处理，请稍后重试"), status_code=409)

        parameters = build_parameters(identity, "scenario", text_value, scenario_context=json.dumps(scenario, ensure_ascii=False))
        chunks: list[str] = []
        sources: list[dict[str, Any]] = []
        upstream_error: dict[str, Any] | None = None
        async for event in xingchen_stream(parameters, identity, request_id):
            if event["event"] == "token":
                chunks.append(str(event["data"].get("text", "")))
            elif event["event"] == "source":
                sources.append(event["data"])
            elif event["event"] == "error":
                upstream_error = event["data"]
        if upstream_error:
            store.reset_pending_turn(identity.uid, session_id, turn_no)
            return JSONResponse(error_payload(request_id, "scenario_agent_failed", "情景 Agent 暂不可用，请重试"), status_code=502)
        completed = store.complete_turn(identity.uid, session_id, turn_no, "".join(chunks), sources)
        if not completed:
            return JSONResponse(error_payload(request_id, "conflict", "场景轮次未能完成，请重试"), status_code=409)
        result = {"session_id": session_id, "turn_no": turn_no, "state": "active", "status": "completed", "assistant_text": "".join(chunks), "evidence": sources}
        store.save_idempotent(identity.uid, f"/scenarios/{session_id}/turn", idem_key, request_body, result)
        return json_response(request_id, result)
    except LookupError:
        return JSONResponse(error_payload(request_id, "not_found", "场景会话不存在或无权访问"), status_code=404)
    except ValueError as exc:
        if str(exc) == "policy_blocked":
            return JSONResponse(error_payload(request_id, "policy_blocked", "不能要求场景忽略课程边界或伪造实验数据"), status_code=422)
        code = "scenario_not_active" if str(exc) == "scenario_not_active" else "invalid_input"
        return JSONResponse(error_payload(request_id, code, "场景已结束" if code == "scenario_not_active" else "场景轮次无效"), status_code=409 if code == "scenario_not_active" else 422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_body", "请求格式错误"), status_code=422)


@app.post("/api/scenarios/{session_id}/end")
async def scenario_end(session_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        body = await request.json()
        idem_key = request.headers["idempotency-key"]
        request_body = {"session_id": session_id, "state": str(body.get("state", "completed"))}
        previous, found = store.idempotent(identity.uid, f"/scenarios/{session_id}/end", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.end_scenario(identity.uid, session_id, request_body["state"])
        # Return the stored turn count and a short, non-model summary so the
        # end screen remains useful even when the upstream Workflow is down.
        history = store.scenario(identity.uid, session_id) or {}
        result["turn_count"] = len(history.get("turns", []))
        result["summary"] = {
            "status": "AI 生成内容，请结合课程来源复核。" if history.get("turns") else "本次场景没有完成对话。",
            "knowledge_points": sorted({source.get("chapter", "") for turn in history.get("turns", []) for source in turn.get("evidence", []) if source.get("chapter")}),
        }
        store.save_idempotent(identity.uid, f"/scenarios/{session_id}/end", idem_key, request_body, result)
        return json_response(request_id, result)
    except LookupError:
        return JSONResponse(error_payload(request_id, "not_found", "场景会话不存在或已结束"), status_code=404)
    except (ValueError, TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_input", "场景状态无效"), status_code=422)


@app.get("/api/questions")
async def question_list(request: Request, page: int = 1, page_size: int = 20) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    # Students see only reviewed questions; staff can inspect drafts.
    data, status = paginate(store.list_questions(published_only=identity.role == "student"), page, page_size)
    if data is None:
        return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
    return json_response(request_id, data)


@app.get("/api/student/assignments")
@app.get("/api/assignments")
async def assignment_list(request: Request, page: int = 1, page_size: int = 20) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    data, status = paginate(store.list_assignments(published_only=identity.role == "student"), page, page_size)
    if data is None:
        return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
    return json_response(request_id, data)


@app.get("/api/student/assignments/{assignment_id}")
@app.get("/api/assignments/{assignment_id}")
async def assignment_detail(assignment_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    assignment = store.assignment(assignment_id, published_only=identity.role == "student", user_uid=identity.uid if identity.role == "student" else None)
    if not assignment:
        return JSONResponse(error_payload(request_id, "not_found", "作业不存在或尚未发布"), status_code=404)
    return json_response(request_id, assignment)


@app.get("/api/teacher/assignments/{assignment_id}/submissions")
async def teacher_assignment_submissions(assignment_id: str, request: Request, page: int = 1, page_size: int = 20) -> JSONResponse:
    """Expose only course-scoped review data to teacher/admin sessions."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})
        data, status = paginate(store.teacher_submissions(assignment_id), page, page_size)
        if data is None:
            return JSONResponse(error_payload(request_id, "invalid_input", "分页参数无效"), status_code=status)
        return json_response(request_id, data)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师批改权限"), status_code=403)


@app.post("/api/teacher/questions")
@app.post("/api/questions")
async def question_create(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        question_type = str(body.get("question_type", ""))
        prompt = str(body.get("prompt", "")).strip()
        max_score = float(body.get("max_score", 0))
        if question_type not in {"single_choice", "multiple_choice", "true_false", "short_answer", "essay"} or not prompt or not 0 < max_score <= 100:
            raise ValueError
        normalized = {**body, "question_type": question_type, "prompt": prompt, "max_score": max_score}
        idem_key = request.headers["idempotency-key"]
        previous, found = store.idempotent(identity.uid, "/teacher/questions", idem_key, normalized)
        if found:
            return json_response(request_id, previous)
        result = store.create_question(identity.uid, normalized)
        store.save_idempotent(identity.uid, "/teacher/questions", idem_key, normalized, result)
        return json_response(request_id, result, 201)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "题目格式或分值无效"), status_code=422)


@app.post("/api/teacher/questions/{question_id}/publish")
@app.post("/api/questions/{question_id}/publish")
async def question_publish(question_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        idem_key = request.headers["idempotency-key"]
        request_body = {"question_id": question_id}
        previous, found = store.idempotent(identity.uid, "/teacher/questions/publish", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.publish_question(question_id, identity.uid)
        if not result:
            return JSONResponse(error_payload(request_id, "not_found", "题目不存在"), status_code=404)
        store.save_idempotent(identity.uid, "/teacher/questions/publish", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "发布请求无效"), status_code=422)


@app.post("/api/teacher/assignments")
@app.post("/api/assignments")
async def assignment_create(request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        if not str(body.get("title", "")).strip() or not isinstance(body.get("question_ids"), list):
            raise ValueError
        idem_key = request.headers["idempotency-key"]
        previous, found = store.idempotent(identity.uid, "/teacher/assignments", idem_key, body)
        if found:
            return json_response(request_id, previous)
        result = store.create_assignment(identity.uid, body)
        store.save_idempotent(identity.uid, "/teacher/assignments", idem_key, body, result)
        return json_response(request_id, result, 201)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        message = "题目必须先审核发布" if str(exc) == "questions_not_published" else "截止时间或允许次数无效" if str(exc) in {"invalid_due_at", "due_at_requires_timezone", "invalid_attempt_limit"} else "作业格式无效"
        return JSONResponse(error_payload(request_id, "invalid_input", message), status_code=422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_body", "请求格式错误"), status_code=422)


@app.post("/api/teacher/assignments/{assignment_id}/publish")
@app.post("/api/assignments/{assignment_id}/publish")
async def assignment_publish(assignment_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        idem_key = request.headers["idempotency-key"]
        request_body = {"assignment_id": assignment_id}
        previous, found = store.idempotent(identity.uid, "/teacher/assignments/publish", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.publish_assignment(assignment_id)
        if not result:
            return JSONResponse(error_payload(request_id, "conflict", "作业不存在或已发布"), status_code=409)
        store.save_idempotent(identity.uid, "/teacher/assignments/publish", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "发布请求无效"), status_code=422)


@app.post("/api/student/assignments/{assignment_id}/submit")
@app.post("/api/assignments/{assignment_id}/submissions")
async def assignment_submit(assignment_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    if identity.role != "student":
        return JSONResponse(error_payload(request_id, "forbidden", "只有学生可以提交作业"), status_code=403)
    key = request.headers["idempotency-key"]
    try:
        body = await request.json()
        previous, found = store.idempotent(identity.uid, "/submissions", key, {"assignment_id": assignment_id, **body})
        if found:
            return json_response(request_id, previous)
        answers = body.get("answers")
        attempt = int(body.get("attempt", 1))
        if not isinstance(answers, dict) or attempt < 1:
            raise ValueError
        result = store.submit(identity.uid, assignment_id, answers, attempt, identity.moodle_user_id)
        store.save_idempotent(identity.uid, "/submissions", key, {"assignment_id": assignment_id, **body}, result)
        return json_response(request_id, result, 201)
    except LookupError:
        return JSONResponse(error_payload(request_id, "not_found", "作业不存在或尚未发布"), status_code=404)
    except sqlite3.IntegrityError:
        return JSONResponse(error_payload(request_id, "conflict", "该尝试已提交"), status_code=409)
    except ValueError as exc:
        if str(exc) == "attempt_limit_reached":
            return JSONResponse(error_payload(request_id, "conflict", "已达到作业允许的提交次数"), status_code=409)
        if str(exc) == "deadline_passed":
            return JSONResponse(error_payload(request_id, "deadline_passed", "作业已超过截止时间"), status_code=409)
        if str(exc) == "invalid_attempt_number":
            return JSONResponse(error_payload(request_id, "invalid_input", "提交次数与当前尝试不一致"), status_code=422)
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "提交格式无效"), status_code=422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_input", "提交格式无效"), status_code=422)


@app.post("/api/teacher/submissions/{submission_id}/grade")
@app.post("/api/submissions/{submission_id}/grade")
async def submission_grade(submission_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        idem_key = request.headers["idempotency-key"]
        request_body = {"submission_id": submission_id}
        previous, found = store.idempotent(identity.uid, f"/teacher/submissions/{submission_id}/grade", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.grade_submission(submission_id, identity.uid)
        if not result:
            return JSONResponse(error_payload(request_id, "not_found", "提交不存在"), status_code=404)
        sync = await sync_moodle_grade(request, identity, str(result["assignment_id"]), result.get("moodle_user_id"), float(result["score"]), float(result["max_score"]))
        if sync["status"] not in {"mock_skipped", "synced"}:
            return JSONResponse(error_payload(request_id, "moodle_grade_sync_failed", "本地成绩已保存，但 Moodle 成绩回写失败，请重试"), status_code=502)
        result["moodle_sync"] = sync
        store.save_idempotent(identity.uid, f"/teacher/submissions/{submission_id}/grade", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师权限"), status_code=403)


@app.post("/api/teacher/assignments/{assignment_id}/grade")
async def assignment_grade(assignment_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        idem_key = request.headers["idempotency-key"]
        previous, found = store.idempotent(identity.uid, f"/teacher/assignments/{assignment_id}/grade", idem_key, {"assignment_id": assignment_id})
        if found:
            return json_response(request_id, previous)
        result = store.start_grading_task(assignment_id, identity.uid)
        if not result:
            return JSONResponse(error_payload(request_id, "not_found", "作业不存在"), status_code=404)
        sync_results = []
        for submission_id in store.assignment_submission_ids(assignment_id):
            graded = store.grade_submission(submission_id, identity.uid)
            if not graded:
                continue
            sync = await sync_moodle_grade(
                request,
                identity,
                assignment_id,
                graded.get("moodle_user_id"),
                float(graded["score"]),
                float(graded["max_score"]),
            )
            sync_results.append({"submission_id": submission_id, **sync})
        if any(item["status"] not in {"mock_skipped", "synced"} for item in sync_results):
            return JSONResponse(error_payload(request_id, "moodle_grade_sync_failed", "批改已保存，但至少一条 Moodle 成绩回写失败，请重试"), status_code=502)
        result["moodle_sync"] = sync_results
        store.save_idempotent(identity.uid, f"/teacher/assignments/{assignment_id}/grade", idem_key, {"assignment_id": assignment_id}, result)
        return json_response(request_id, result, 202)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师批改权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "批改任务参数无效"), status_code=422)


@app.post("/api/teacher/submissions/{submission_id}/subjective/{question_id}/agent-review")
async def subjective_agent_review(submission_id: str, question_id: str, request: Request) -> JSONResponse:
    """Ask the Workflow for a bounded draft score; teacher review remains required."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        item = store.subjective_item(submission_id, question_id)
        if not item:
            return JSONResponse(error_payload(request_id, "not_found", "主观题提交不存在"), status_code=404)
        idem_key = request.headers["idempotency-key"]
        request_body = {"submission_id": submission_id, "question_id": question_id}
        previous, found = store.idempotent(identity.uid, f"/teacher/submissions/{submission_id}/subjective/{question_id}/agent-review", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        parameters = build_parameters(identity, "grading", str(item["answer"]), rubric=str(item["rubric"] or ""))
        chunks: list[str] = []
        upstream_error: dict[str, Any] | None = None
        async for event in xingchen_stream(parameters, identity, request_id):
            if event["event"] == "token":
                chunks.append(str(event["data"].get("text", "")))
            elif event["event"] == "error":
                upstream_error = event["data"]
        if upstream_error:
            return JSONResponse(error_payload(request_id, "agent_review_failed", "Agent 初评暂不可用，请转人工复核"), status_code=502)
        try:
            result = json.loads("".join(chunks))
            score = float(result["score"])
            feedback = str(result["feedback"])
            if not isinstance(result, dict) or not feedback.strip() or score < 0 or score > float(item["max_score"]):
                raise ValueError
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return JSONResponse(error_payload(request_id, "manual_review_required", "Agent 输出未通过评分格式校验，需人工复核"), status_code=422)
        grade = store.save_agent_grade(item, score, feedback)
        result = {"grade": grade, "status": "needs_teacher_review", "ai_generated": True}
        store.save_idempotent(identity.uid, f"/teacher/submissions/{submission_id}/subjective/{question_id}/agent-review", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师批改权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "初评请求无效"), status_code=422)


@app.get("/api/teacher/assignments/{assignment_id}/grading-status")
async def grading_status(assignment_id: str, request: Request, task_id: str = "") -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})
        if not task_id:
            return JSONResponse(error_payload(request_id, "invalid_input", "缺少 task_id"), status_code=422)
        task = store.grading_task(task_id)
        if not task or task["assignment_id"] != assignment_id:
            return JSONResponse(error_payload(request_id, "not_found", "批改任务不存在"), status_code=404)
        return json_response(request_id, task)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师批改权限"), status_code=403)


@app.patch("/api/teacher/grade-items/{grade_id}")
async def grade_review(grade_id: str, request: Request) -> JSONResponse:
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    if (missing := idempotency_error(request, request_id, identity)):
        return missing
    try:
        require_role(identity, {"teacher", "admin"})
        body = await request.json()
        score = float(body.get("score"))
        reason = str(body.get("reason", "")).strip()
        if not reason or not math.isfinite(score) or score < 0:
            raise ValueError
        idem_key = request.headers["idempotency-key"]
        request_body = {"grade_id": grade_id, "score": score, "reason": reason}
        previous, found = store.idempotent(identity.uid, f"/teacher/grade-items/{grade_id}", idem_key, request_body)
        if found:
            return json_response(request_id, previous)
        result = store.review_grade(grade_id, identity.uid, score, reason)
        if not result:
            return JSONResponse(error_payload(request_id, "not_found", "成绩项不存在"), status_code=404)
        context = store.submission_context(str(result["submission_id"]))
        total, maximum = store.submission_totals(str(result["submission_id"]))
        sync = await sync_moodle_grade(request, identity, str(context["assignment_id"] if context else ""), context.get("moodle_user_id") if context else None, total, maximum)
        if sync["status"] not in {"mock_skipped", "synced"}:
            return JSONResponse(error_payload(request_id, "moodle_grade_sync_failed", "教师修改已保存，但 Moodle 成绩回写失败，请重试"), status_code=502)
        result["moodle_sync"] = sync
        store.save_idempotent(identity.uid, f"/teacher/grade-items/{grade_id}", idem_key, request_body, result)
        return json_response(request_id, result)
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "没有教师权限"), status_code=403)
    except ValueError as exc:
        if str(exc) == "idempotency_key_reused":
            return JSONResponse(error_payload(request_id, "conflict", "幂等键已用于不同请求"), status_code=409)
        return JSONResponse(error_payload(request_id, "invalid_input", "成绩或修改原因无效"), status_code=422)
    except (TypeError, json.JSONDecodeError):
        return JSONResponse(error_payload(request_id, "invalid_input", "成绩或修改原因无效"), status_code=422)


# The endpoint may return either an error JSON response or an SSE stream.
# Disable FastAPI response-model inference so the union is not treated as a Pydantic field.
@app.post("/api/course-agent/chat", response_model=None)
async def chat(request: Request) -> StreamingResponse | JSONResponse:
    request_id = uuid.uuid4().hex
    scenario_turn_no: int | None = None
    scenario_idem_key = ""
    scenario_request_body: dict[str, Any] = {}
    try:
        # Chat is a POST even for read-like Q&A. Resolve it through the same
        # authenticated helper as every other endpoint so real Moodle sesskey
        # validation cannot be bypassed by selecting the qa mode.
        identity, auth_error, auth_request_id = await authenticated(request)
        if auth_error:
            return auth_error
        request_id = auth_request_id
        assert identity is not None
        body = await request.json()
        if not isinstance(body, dict):
            raise ValueError("invalid body")
        question = body.get("question")
        if not isinstance(question, str) or not question.strip():
            return JSONResponse(error_payload(request_id, "invalid_input", "问题不能为空"), status_code=422)
        max_chars = int(os.getenv("AGENT_MAX_INPUT_CHARS", "4000"))
        if len(question) > max_chars:
            return JSONResponse(error_payload(request_id, "input_too_long", "问题超过长度限制"), status_code=422)
        if policy_violation(question):
            return JSONResponse(error_payload(request_id, "policy_blocked", "不能忽略课程边界或伪造数据、文献和引用；可以改为请求模拟方案或实验设计"), status_code=422)
        mode = mode_from_request(identity, body)
        semaphore = await limiter.acquire(identity.uid)
        if semaphore is None:
            return JSONResponse(error_payload(request_id, "rate_limited", "请求过于频繁，请稍后重试"), status_code=429)
        graph_context = ""
        node_ids = body.get("node_ids", [])
        if isinstance(node_ids, list):
            # Only IDs resolved by the server enter the trusted Workflow slot.
            graph_nodes = [store.node(str(node_id)) for node_id in node_ids[:10]]
            graph_context = json.dumps([node for node in graph_nodes if node], ensure_ascii=False)
        profile_context = ""
        if mode == "learning_diagnosis":
            profile_context = json.dumps(store.learning_profile(identity.uid), ensure_ascii=False)
        scenario_context = ""
        session_id = body.get("session_id")
        if mode == "scenario" and isinstance(session_id, str):
            if (missing := idempotency_error(request, request_id, identity)):
                semaphore.release()
                return missing
            idem_key = request.headers["idempotency-key"]
            scenario_request_body = {"session_id": session_id, "turn_no": body.get("turn_no"), "question": question.strip(), "mode": mode}
            scenario_idem_key = idem_key
            previous, found = store.idempotent(identity.uid, f"/course-agent/scenario/{session_id}", idem_key, scenario_request_body)
            if found:
                semaphore.release()
                return json_response(request_id, previous)
            scenario = store.scenario(identity.uid, session_id)
            if not scenario:
                semaphore.release()
                return JSONResponse(error_payload(request_id, "not_found", "场景会话不存在或无权访问"), status_code=404)
            turn_no = body.get("turn_no")
            if not isinstance(turn_no, int) or turn_no < 1:
                semaphore.release()
                return JSONResponse(error_payload(request_id, "invalid_input", "场景轮次无效"), status_code=422)
            try:
                turn = store.add_turn(identity.uid, session_id, turn_no, question.strip(), request_id)
            except ValueError:
                semaphore.release()
                return JSONResponse(error_payload(request_id, "conflict", "场景已结束或轮次已存在"), status_code=409)
            if turn.get("status") == "completed" or turn.get("request_id") != request_id:
                semaphore.release()
                return JSONResponse(error_payload(request_id, "conflict", "该场景轮次正在处理或已经完成，请复用原幂等键"), status_code=409)
            scenario_context = json.dumps(scenario, ensure_ascii=False)
        parameters = build_parameters(identity, mode, question.strip(), graph_context, profile_context, scenario_context)
        if isinstance(session_id, str) and mode == "scenario":
            scenario_turn_no = turn_no
    except PermissionError:
        return JSONResponse(error_payload(request_id, "unauthorized", "请先登录课程平台"), status_code=401)
    except ValueError as exc:
        return JSONResponse(error_payload(request_id, "invalid_mode", str(exc)), status_code=422)
    except (ConnectionError, httpx.HTTPError):
        return JSONResponse(error_payload(request_id, "auth_service_unavailable", "课程会话服务暂不可用"), status_code=502)
    except (json.JSONDecodeError, TypeError):
        return JSONResponse(error_payload(request_id, "invalid_body", "请求格式错误"), status_code=422)

    async def event_stream() -> AsyncIterator[bytes]:
        scenario_chunks: list[str] = []
        scenario_sources: list[dict[str, Any]] = []
        scenario_failed = False
        scenario_finished = False
        try:
            async for event in xingchen_stream(parameters, identity, request_id):
                if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario":
                    if event["event"] == "token":
                        scenario_chunks.append(str(event["data"].get("text", "")))
                    elif event["event"] == "source":
                        scenario_sources.append(event["data"])
                    elif event["event"] == "error":
                        scenario_failed = True
                    elif event["event"] == "done":
                        completed = store.complete_turn(identity.uid, session_id, int(scenario_turn_no or 0), "".join(scenario_chunks), scenario_sources)
                        scenario_finished = bool(completed)
                        if scenario_finished:
                            # The key is known only in the scenario branch;
                            # save the same business result used by retries.
                            store.save_idempotent(identity.uid, f"/course-agent/scenario/{session_id}", scenario_idem_key, scenario_request_body, {"session_id": session_id, "turn_no": scenario_turn_no, "status": "completed", "assistant_text": "".join(scenario_chunks), "evidence": scenario_sources})
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
        finally:
            if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario" and (scenario_failed or not scenario_finished):
                store.reset_pending_turn(identity.uid, session_id, int(scenario_turn_no or 0))
            semaphore.release()

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Request-ID": request_id})
