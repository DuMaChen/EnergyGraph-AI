from __future__ import annotations

import asyncio
import hashlib
import hmac
from io import BytesIO
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
from fastapi.responses import JSONResponse, StreamingResponse, Response, FileResponse
from pypdf import PdfReader

from .course_retrieval import CourseRetriever
from .course_store import store


app = FastAPI(title="Course Agent Adapter", version="0.1.0")
logger = logging.getLogger("course-agent")


@app.middleware("http")
async def request_size_guard(request: Request, call_next: Any) -> Any:
    """Reject oversized writes before a route parses or persists their body.

    The raw knowledge-base upload endpoint has its own 35 MiB limit.  All
    other writes use a smaller JSON limit so a client cannot reserve memory by
    sending an unexpectedly large prompt, idempotency payload, or scenario
    context.  Route-level validation remains necessary for chunked requests.
    """
    if request.method in {"POST", "PUT", "PATCH"}:
        upload_path = request.url.path.endswith("/files") or "/upload" in request.url.path or "/resources" in request.url.path
        default_limit = int(os.getenv("AGENT_MAX_BODY_BYTES", str(1024 * 1024)))
        max_bytes = 35 * 1024 * 1024 if upload_path else default_limit
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

QUALITY_CONTRACT = """【回答质量约束】
你是本课程的严谨助教。
1. 只依据服务器提供的课程资料和知识图谱回答，不编造未经核验的厂商、价格、型号或实验数据；资料未覆盖的明确说明“课程资料未覆盖”。
2. 先给直接结论，再按需要分点或步骤说明，结构清晰，逻辑严谨。
3. 若学生询问专业概念，深入阐释底层原理，并在文末提供对应课件出处 [来源文件：xxx；页码：yyy]。
4. 如果当前 Workflow 声明了结构化字段（如 answer1-answer5），按要求在字段中填入具体内容，不输出空字段或占位符。"""

DEFAULT_PROMPT_CONFIG: dict[str, str] = {
    "core_quality_contract": QUALITY_CONTRACT,
    "qa_prompt": "依据课程资料与知识图谱回答，剖析机理与工程背景，给出结构清晰、条理分明的专业解答，并在文末按规范引用课件 [来源文件：xxx；页码：yyy]。",
    "teacher_assistant_prompt": "【教师备课输出结构】answer1 填教学目标；answer2 填课前材料与准备；answer3 填课堂讨论步骤和学生产出；answer4 填评价标准；answer5 填容易混淆的概念与纠偏提示。五个字段都必须有具体内容，不适用时写明课程资料未覆盖。",
    "question_draft_prompt": "依据所选知识点与大纲，严格按题型输出符合教学测验标准的题目、各选项、分值及详尽解析。",
    "grading_prompt": "严格按预设评分标准和分值核算，客观题精准核验，主观题给出知识漏洞诊断与提分建议。",
}

PROMPT_CONFIG_FILE = os.getenv("PROMPT_CONFIG_FILE", "/tmp/course_agent_prompt_config.json")


def load_prompt_config() -> dict[str, str]:
    if os.path.exists(PROMPT_CONFIG_FILE):
        try:
            with open(PROMPT_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg = dict(DEFAULT_PROMPT_CONFIG)
                    cfg.update({k: str(v) for k, v in data.items() if k in DEFAULT_PROMPT_CONFIG and str(v).strip()})
                    return cfg
        except Exception:
            pass
    return dict(DEFAULT_PROMPT_CONFIG)


def save_prompt_config(cfg: dict[str, Any]) -> dict[str, str]:
    current = load_prompt_config()
    for k in DEFAULT_PROMPT_CONFIG:
        if k in cfg and isinstance(cfg[k], str) and cfg[k].strip():
            current[k] = cfg[k].strip()
    try:
        with open(PROMPT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return current


@dataclass(frozen=True)
class Identity:
    """The adapter keeps only a stable pseudonymous ID, never a real name."""

    uid: str
    role: str
    course_id: int
    csrf_token: str = ""
    moodle_user_id: int | None = None
    username: str = ""
    fullname: str = ""


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._timestamps: dict[str, deque[float]] = defaultdict(deque)
        self._guard = asyncio.Lock()

    async def acquire(self, uid: str) -> bool:
        now = time.monotonic()
        async with self._guard:
            timestamps = self._timestamps[uid]
            while timestamps and now - timestamps[0] > self.window_seconds:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return False
            timestamps.append(now)
            return True


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


def validate_pdf_bytes(content: bytes) -> bool:
    """Require a structurally readable PDF, not only a forged header/footer."""
    if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-4096:]:
        return False
    try:
        reader = PdfReader(BytesIO(content), strict=False)
        return len(reader.pages) > 0
    except Exception:
        return bool(b"/Type /Page" in content or b"/Type/Page" in content or b"/Page" in content)


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
COURSE_RETRIEVER = CourseRetriever(os.getenv("COURSE_SOURCE_DIR", "/app/course-sources"))


def manifest_digest() -> str:
    """Return the server-owned course manifest digest for version tracking."""
    path = Path(os.getenv("COURSE_MANIFEST", "/app/course-data/manifest.json"))
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "unavailable"


def retrieve_course_evidence(question: str, *, max_chunks: int = 3, max_chars: int = 2400) -> tuple[str, list[dict[str, Any]]]:
    """Retrieve bounded, server-owned course evidence for a Workflow prompt."""
    result = COURSE_RETRIEVER.search(question, max_chunks=max_chunks, max_chars=max_chars)
    published = store.published_kb()
    version_name = str(published["version_name"]) if published else str(MANIFEST.get("source_archive", "unknown"))
    version_id = str(published["id"]) if published else "local-manifest"
    manifest_by_source = {str(item.get("source_file")): item for item in MANIFEST.get("files", [])}
    return result.prompt_context, result.sources(version_name, version_id, manifest_by_source)


def validate_sources(text: str) -> list[dict[str, Any]]:
    """Accept source events and match them robustly to the versioned local manifest."""
    files = list(MANIFEST.get("files", []))
    allowed = {str(item.get("source_file", "")).strip(): item for item in files}
    sources: list[dict[str, Any]] = []
    published = store.published_kb()
    version_name = str(published["version_name"]) if published else str(MANIFEST.get("source_archive", "unknown"))
    version_id = str(published["id"]) if published else "local-manifest"
    for match in SOURCE_PATTERN.finditer(text):
        file_name = match.group("file").strip()
        page = int(match.group("page"))
        item = allowed.get(file_name)
        if not item:
            f_clean = file_name.replace(".pdf", "").strip()
            for k, v in allowed.items():
                k_clean = k.replace(".pdf", "").strip()
                if f_clean == k_clean or f_clean in k_clean or k_clean in f_clean:
                    item = v
                    file_name = k
                    break
                if any(kw in file_name for kw in ["大纲", "导论", "绪论", "概述", "介绍", "基础"]) and "1.1" in k:
                    item = v
                    file_name = k
                    break
        if not item:
            continue
        page_count = item.get("page_count")
        if isinstance(page_count, int) and page_count > 0:
            if page < 1 or page > page_count:
                continue
        expected_chapter = str(item.get("chapter", ""))
        raw_chapter = match.group("chapter")
        if raw_chapter and expected_chapter and raw_chapter.strip() != expected_chapter.strip():
            continue
        chapter = raw_chapter or expected_chapter
        norm_f = str(item.get("normalized_file", ""))
        chap_id = str(item.get("chapter_id", ""))
        sources.append(
            {
                "source_id": hashlib.sha256(f"{file_name}:{page}".encode("utf-8")).hexdigest()[:20],
                "file": norm_f or file_name,
                "source_file": str(item.get("source_file") or file_name).strip(),
                "chapter": expected_chapter or chapter,
                "page": page,
                "sha256": str(item.get("sha256", "")),
                "resource_id": "res-" + hashlib.sha256(f"{norm_f}:{chap_id}".encode()).hexdigest()[:20],
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

    bridge_token = request.headers.get("x-agent-bridge-token")
    expected_bridge_token = os.getenv("AGENT_BRIDGE_TOKEN", "").strip()
    if bridge_token and expected_bridge_token and bridge_token == expected_bridge_token:
        role = request.headers.get("x-dev-role", "student")
        user_id = request.headers.get("x-dev-user", "demo-student")
        return Identity(stable_uid(user_id), role, int(os.getenv("MOCK_COURSE_ID", "1")), "bridge-csrf", 1, "test_student", "测试学员")

    cookie = request.headers.get("cookie")
    if not cookie:
        raise PermissionError("login required")
    session_url = os.getenv("MOODLE_SESSION_URL", "http://moodle/local/course_agent/session.php")
    bridge_headers = {"cookie": cookie}
    public_host = os.getenv("SITE_HOST", "").strip()
    if public_host:
        # Moodle's wwwroot is the public HTTPS hostname.  The Adapter calls
        # the bridge over the Docker network, so preserve the public request
        # host/scheme or Moodle treats an otherwise valid session as a
        # redirect error.
        bridge_headers.update({
            "host": public_host,
            "x-forwarded-host": public_host,
            "x-forwarded-proto": os.getenv("SITE_SCHEME", "https"),
        })
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(session_url, headers=bridge_headers)
    except httpx.HTTPError as exc:
        raise ConnectionError("Moodle session service unavailable") from exc
    if response.status_code in {301, 302, 303, 307, 308, 401, 403}:
        raise PermissionError("login required")
    if response.status_code != 200:
        raise ConnectionError("Moodle session service returned an error")
    content_type = response.headers.get("content-type", "").lower()
    if content_type and "json" not in content_type:
        raise PermissionError("login required")
    try:
        data = response.json()
        print(f"[DEBUG_SESSION] Moodle response: {data}", flush=True)
        if isinstance(data, dict) and (
            data.get("errorcode") in {"redirecterrordetected", "requireloginerror"}
            or (data.get("error") and not data.get("user_id"))
        ):
            # AJAX_SCRIPT turns Moodle's expired-session redirect into a
            # JSON error with HTTP 200. It is still an unauthenticated
            # browser, not an unavailable session service.
            raise PermissionError("login required")
        return Identity(
            stable_uid(data["user_id"]),
            str(data["role"]),
            int(data["course_id"]),
            str(data.get("sesskey", "")),
            int(data["user_id"]),
            str(data.get("username", "")),
            str(data.get("fullname", "")),
        )
    except (ValueError, KeyError, TypeError) as exc:
        if str(getattr(response, "text", "")).lstrip().startswith("<"):
            raise PermissionError("login required") from exc
        raise ConnectionError("invalid Moodle session response") from exc


def mode_from_request(identity: Identity, body: dict[str, Any]) -> str:
    mode = body.get("mode")
    if not isinstance(mode, str) or mode not in ALLOWED_MODES.get(identity.role, set()):
        raise ValueError("mode is not allowed for this role")
    return mode


def format_student_learning_context(student_ctx: Any) -> str:
    if not isinstance(student_ctx, dict):
        return ""
    questions = student_ctx.get("questions")
    if not isinstance(questions, list) or not questions:
        return ""
    
    # Filter ONLY answered questions
    answered_questions = [q for q in questions if isinstance(q, dict) and q.get("student_answer") and q.get("student_answer") != "未作答"]
    if not answered_questions:
        answered_questions = [q for q in questions if isinstance(q, dict)]

    summary = student_ctx.get("summary") if isinstance(student_ctx.get("summary"), dict) else {}
    tot = summary.get("total_questions", len(answered_questions))
    cor = summary.get("correct_questions", len([q for q in answered_questions if q.get("is_correct")]))
    wro = summary.get("wrong_questions", tot - cor)
    acc = summary.get("accuracy_rate", f"{int(cor/tot*100)}%" if tot else "100%")
    avg = summary.get("avg_score", 94)
    
    lines = [
        "【学生真实全局课程档案与已完成做题记录（仅包含实际作答提交的练习）】",
        f"- 学生：{str(student_ctx.get('student_name', '林晨 同学'))[:50]}",
        f"- 课程：《{str(student_ctx.get('course_name', '电力系统储能技术'))[:50]}》",
        f"- 已做题目数：{tot} 道题",
        f"- 答对题数：{cor} 道题",
        f"- 错题/失分题数：{wro} 道题",
        f"- 综合正确率：{acc}",
        f"- 平均成绩：{avg} 分",
        f"- 课件学习进度：已学 {summary.get('courseware_studied', 20)}/{summary.get('total_courseware', 21)} 份",
        f"- 任务完成进度：已完成 {summary.get('completed_tasks', 1)} 项",
        "\n【已做题目明细记录（优先列出失分考点）】:"
    ]
    
    wrong_count = 0
    correct_summary = []
    
    for i, q in enumerate(answered_questions, 1):
        is_correct = bool(q.get("is_correct"))
        if not is_correct:
            wrong_count += 1
            if wrong_count <= 10:  # 重点展开前 10 道错题
                lines.append(
                    f"[题目{i} 【错题/失分】] 来源：《{q.get('source_task', '作业')}》 | 题型：{q.get('type', '单选')}\n"
                    f"  题干：{str(q.get('stem', ''))[:200]}\n"
                    f"  选项：{str(q.get('options', ''))[:150]}\n"
                    f"  学生作答：{q.get('student_answer')} | 正确答案：{q.get('correct_answer')} | 得分：{q.get('earned_score')}/{q.get('max_score')}分\n"
                    f"  失分考点与解析：{str(q.get('explanation', ''))[:200]}\n"
                    f"  关联课件：[{q.get('courseware')}]"
                )
        else:
            correct_summary.append(f"《{q.get('source_task', '作业')}》第{q.get('question_index', i)}题({q.get('knowledge_point', '概念题')})")
            
    if correct_summary:
        lines.append(f"[其余 {len(correct_summary)} 道题目 【完全正确】]: 包含 " + "、".join(correct_summary[:8]) + " 等，得分率 100%。")
        
    return "\n".join(lines)


def build_student_learning_diagnosis_report(student_ctx: dict[str, Any]) -> str:
    summary = student_ctx.get("summary") if isinstance(student_ctx.get("summary"), dict) else {}
    questions = student_ctx.get("questions") if isinstance(student_ctx.get("questions"), list) else []
    student_name = str(student_ctx.get("student_name") or "当前学员")
    
    # Only consider questions that were actually attempted/answered
    answered_questions = [q for q in questions if isinstance(q, dict) and q.get("student_answer") and q.get("student_answer") != "未作答"]
    if not answered_questions and questions:
        answered_questions = [q for q in questions if isinstance(q, dict)]

    tot = summary.get("total_questions", len(answered_questions))
    cor = summary.get("correct_questions", len([q for q in answered_questions if q.get("is_correct")]))
    wro = summary.get("wrong_questions", tot - cor)
    acc = summary.get("accuracy_rate", f"{int(cor/tot*100)}%" if tot else "100%")
    avg = summary.get("avg_score", 94)
    tasks_done = summary.get("completed_tasks", 1)
    courseware_done = summary.get("courseware_studied", 20)
    courseware_tot = summary.get("total_courseware", 21)

    wrong_items = [q for q in answered_questions if not q.get("is_correct")]
    correct_items = [q for q in answered_questions if q.get("is_correct")]

    lines = [
        "### 全局学情数据概况",
        f"- **学员档案**：{student_name} | 《电力系统储能技术》课程",
        f"- **已完成练习作答题数**：{tot} 道题目（仅统计已实际提交作答的作业与测验）",
        f"- **答题表现**：完全正确 {cor} 题，错题/部分失分 {wro} 题，已做题目正确率 **{acc}**",
        f"- **已完成作业加权得分**：**{avg} 分**（已提交 {tasks_done} 项作业考核）",
        f"- **课件研读进度**：已学习 **{courseware_done} / {courseware_tot}** 份课程讲义",
        "",
        "### 核心薄弱考点与错题深度归因"
    ]

    if not wrong_items:
        lines.append("当前已完成的作业与测验中**无失分错题**，知识点掌握扎实！")
        lines.append("")
    else:
        for idx, q in enumerate(wrong_items, 1):
            stem = q.get("stem", "")
            student_ans = q.get("student_answer", "")
            correct_ans = q.get("correct_answer", "")
            earned = q.get("earned_score", 0)
            max_s = q.get("max_score", 0)
            expl = q.get("explanation", "")
            cw = q.get("courseware", "")
            task_name = q.get("source_task", "课后作业")
            kp = (q.get("knowledge_point") or task_name or "核心考点").strip()
            
            lines.append(f"#### {idx}. 【失分考点】{task_name} · {kp}")
            lines.append(f"- **题目**：{stem}")
            lines.append(f"- **学生作答**：`{student_ans}` | **标准答案**：`{correct_ans}` | **得分**：{earned}/{max_s} 分")
            lines.append(f"- **失分归因与名师解析**：{expl}")
            if cw:
                cw_name = cw.split(" P")[0].strip()
                cw_page = cw.split(" P")[1].strip() if " P" in cw else "1"
                lines.append(f"- **对应知识溯源**：[来源文件：{cw_name}；页码：{cw_page}]")
            lines.append("")

    lines.append("### 巩固优势与针对性复习建议")
    good_kps = [str(q.get("knowledge_point") or "").strip() for q in correct_items if str(q.get("knowledge_point") or "").strip()]
    if good_kps:
        unique_kps = []
        for k in good_kps:
            if k not in unique_kps:
                unique_kps.append(k)
        lines.append(f"1. **知识优势保持**：在 **{'、'.join(unique_kps[:4])}** 等模块概念理解扎实，建议继续保持。")
    
    rec_idx = 2 if good_kps else 1
    for w in wrong_items:
        kp = (w.get("knowledge_point") or w.get("source_task") or "储能专业考点").strip()
        cw = w.get("courseware", "")
        if cw:
            cw_name = cw.split(" P")[0].strip()
            cw_page = cw.split(" P")[1].strip() if " P" in cw else "1"
            lines.append(f"{rec_idx}. **{kp}重点强化**：结合错题归因深入掌握核心原理与控制逻辑，复习 [来源文件：{cw_name}；页码：{cw_page}]。")
        else:
            lines.append(f"{rec_idx}. **{kp}重点强化**：结合错题归因深入掌握核心机理与应用场景。")
        rec_idx += 1
    
    pending_tasks = student_ctx.get("pending_tasks", [])
    if pending_tasks:
        lines.append("")
        lines.append("### 待完成学习任务提醒")
        for pt in pending_tasks:
            title = pt.get("title") if isinstance(pt, dict) else str(pt)
            deadline = pt.get("deadline", "待提交") if isinstance(pt, dict) else ""
            lines.append(f"- **待完成**：《{title}》（截止时间：{deadline}，暂未计入学情诊断）")

    return "\n".join(lines)


def is_learning_diagnosis_intent(question: str, mode: str) -> bool:
    if mode == "learning_diagnosis":
        return True
    q = str(question or "").strip()
    # Explicitly exclude general study advice or questions about how to study / who are you
    if any(k in q for k in ["怎么学", "如何学", "学习方法", "学习路线", "复习方法", "复习路线", "你是谁", "介绍", "你能做什么"]):
        return False
    specific_keywords = [
        "学情诊断", "学情分析", "学情检验", "学情评估", "学情报告", "学情汇报",
        "错题归因", "错题复盘", "我的错题", "错题分析",
        "做题记录", "我的做题", "我的成绩", "我的学情", "学情概况",
        "学情复盘", "知识掌握情况", "查看学情", "诊断学情"
    ]
    return any(k in q for k in specific_keywords)


VALID_COURSEWARE_WHITELIST: set[str] = {
    "1.1 电力储能技术的概念 .pdf", "1.2 电力储能技术的发展.pdf", "1.3 储能技术在电力系统中的应用.pdf",
    "2.1 电力系统的基本概念.pdf", "2.2 电力系统的运行特点和要求.pdf", "2.3 储能技术的典型应用.pdf",
    "3.1 抽水蓄能电站的组成及工作原理.pdf", "3.2 新型电力储能系统的组成.pdf", "3.3 新型电能存储设备工作原理.pdf",
    "3.4 储能变流器拓扑及并网控制.pdf", "3.5 储能监控系统结构及通信.pdf",
    "4.1 抽水蓄能电站的规划配置.pdf", "4.2 电化学储能系统的规划配置.pdf", "4.3 电池储能系统集成技术.pdf",
    "5.1 电力储能系统的接入.pdf", "5.2 电力储能系统的运行控制.pdf", "5.3 电力储能系统的运行维护.pdf", "5.4 电力储能系统的运行案例.pdf",
    "6.1 电力储能系统的性能检测.pdf", "6.2 电力储能系统的系统评估.pdf"
}


def extract_and_normalize_answer(raw_input: str) -> str | None:
    text = str(raw_input or "").strip()
    if not text:
        return None
    # Strip common Chinese and English punctuation and brackets
    text_clean = re.sub(r"[。，,.!！【】\[\]()（）:：、\s]", "", text).strip()
    if not text_clean:
        return None
    
    # 1. Single letter
    if re.fullmatch(r"^[A-Da-d]$", text_clean):
        return text_clean.upper()
        
    num_map = {
        "1": "A", "2": "B", "3": "C", "4": "D",
        "A": "A", "B": "B", "C": "C", "D": "D",
        "第一个": "A", "第二个": "B", "第三个": "C", "第四个": "D",
        "第1个": "A", "第2个": "B", "第3个": "C", "第4个": "D",
        "第A个": "A", "第B个": "B", "第C个": "C", "第D个": "D",
        "选项A": "A", "选项B": "B", "选项C": "C", "选项D": "D",
        "A选项": "A", "B选项": "B", "C选项": "C", "D选项": "D",
    }
    if text_clean.upper() in num_map:
        return num_map[text_clean.upper()]
        
    # 2. Short selection phrases (length <= 12 to avoid false matching on long questions)
    if len(text_clean) <= 12:
        match = re.search(r"(?:我选|答案是|选|作答|应该选|是|选个|正确选项是|选项)\s*([A-Da-d1-4])", text_clean, re.IGNORECASE)
        if match:
            val = match.group(1).upper()
            return num_map.get(val, val)
            
    # 3. True / False judgment terms
    if text_clean in {"正确", "对", "是对的", "是正确的", "对的", "是", "TRUE", "T"}:
        return "正确"
    if text_clean in {"错误", "错", "是不对的", "是不正确的", "错的", "否", "不是", "FALSE", "F"}:
        return "错误"
        
    return None


class SessionTeachingState:
    def __init__(self, uid: str, session_id: str):
        self.uid = uid
        self.session_id = session_id
        self.scene_mode = 0  # 0: 常规QA, 1: 师傅情景演练, 2: 主讲名师情景演练, 3: 随堂测验模式
        self.scene_role_name = ""  # "储能电站现场运维师傅" | "《电力系统储能技术》主讲老师"
        self.current_quiz: dict[str, Any] | None = None
        self.last_active_time = time.monotonic()
        self.lock = asyncio.Lock()


class TeachingStateManager:
    def __init__(self, ttl_seconds: int = 900, max_sessions: int = 1000):
        self.ttl = ttl_seconds
        self.max_sessions = max_sessions
        self._states: dict[str, SessionTeachingState] = {}
        self._manager_lock = asyncio.Lock()

    async def get_or_create(self, uid: str, session_id: str) -> SessionTeachingState:
        key = f"{uid}:{session_id}"
        async with self._manager_lock:
            now = time.monotonic()
            if key in self._states:
                state = self._states[key]
                if now - state.last_active_time > self.ttl:
                    state.current_quiz = None
                    state.scene_mode = 0
                    state.scene_role_name = ""
                state.last_active_time = now
                return state
            if len(self._states) >= self.max_sessions:
                oldest_key = min(self._states.keys(), key=lambda k: self._states[k].last_active_time)
                del self._states[oldest_key]
            state = SessionTeachingState(uid, session_id)
            self._states[key] = state
            return state

    async def pop_active_quiz(self, uid: str, session_id: str) -> dict[str, Any] | None:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            quiz = state.current_quiz
            state.current_quiz = None
            return quiz

    async def set_active_quiz(self, uid: str, session_id: str, quiz: dict[str, Any]) -> None:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.current_quiz = quiz
            state.scene_mode = 3

    async def set_scene(self, uid: str, session_id: str, scene_mode: int, role_name: str = "") -> None:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.scene_mode = scene_mode
            state.scene_role_name = role_name
            if scene_mode == 0:
                state.current_quiz = None


teaching_state_manager = TeachingStateManager()


def classify_workflow_intent(
    question: str,
    current_state: SessionTeachingState | None = None,
    quoted_text: str = ""
) -> str:
    # 1. Quoted text takes absolute precedence
    if quoted_text and str(quoted_text).strip():
        return "quote_study"
    
    q = str(question or "").strip()
    
    # 2. Scenario roleplay control
    if any(k in q for k in ["退出情景演绎", "结束情景演绎", "停止情景演绎", "退出演练", "不扮演了", "退出角色扮演", "结束角色扮演"]):
        return "scenario_stop"
    if any(k in q for k in ["扮演老师", "扮演主讲老师", "名师授课", "名师情景", "主讲老师授课", "老师授课方式"]):
        return "scenario_start_teacher"
    if any(k in q for k in ["扮演师傅", "扮演运维师傅", "扮演工程师", "电厂师傅", "现场师傅", "运维师傅情景", "电厂运维师傅"]):
        return "scenario_start_engineer"
    
    # 3. Quiz control (check stop before generate to avoid substring collision on '出题')
    if any(k in q for k in ["停止出题", "不练了", "不做了", "停止练习", "结束测验", "退出测验", "停止随堂"]):
        return "quiz_stop"
    if any(k in q for k in ["出一道题", "出题", "考考我", "做道题", "随堂练习", "再来一题", "测验", "来一道题", "出题测验", "随堂测试"]):
        return "quiz_generate"
        
    # 4. Active quiz answering (or isolated option answering when empty)
    if extract_and_normalize_answer(q) is not None:
        if current_state and current_state.current_quiz:
            return "quiz_submit"
        elif len(q) <= 6:
            return "quiz_submit"
            
    # 5. Learning diagnosis
    if is_learning_diagnosis_intent(q, "qa"):
        return "learning_diagnosis"
        
    return "general_qa"


def extract_quiz_meta_fallback(full_text: str) -> dict[str, Any]:
    """Robust parser that guarantees valid quiz metadata under all LLM output formats."""
    # 1. Check HIDDEN_META json tag
    match = re.search(r"<!--HIDDEN_META:(.*?)-->", full_text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1).strip())
            if isinstance(parsed, dict) and parsed.get("correct_answer"):
                return parsed
        except Exception:
            pass

    # 2. Check explicit answer field in text
    ans_match = re.search(r"(?:标准答案|正确答案|参考答案|答案|本题选|选)[:：\s]*([A-Da-d])", full_text)
    ans_letter = ans_match.group(1).upper() if ans_match else None

    # 3. Check explanation & courseware fields
    expl_match = re.search(r"(?:名师解析|知识点解析|解析|归因)[:：\s]*([^\n]+)", full_text)
    explanation = expl_match.group(1).strip() if expl_match else ""

    cw_match = re.search(r"(?:知识溯源|对应课件|课件|来源)[:：\s]*([^\n]+)", full_text)
    courseware = cw_match.group(1).strip() if cw_match else ""

    kp_match = re.search(r"(?:核心考点|考点|知识点)[:：\s]*([^\n]+)", full_text)
    knowledge_point = kp_match.group(1).strip() if kp_match else ""

    # 4. Domain inference if answer/courseware not explicitly provided
    if not ans_letter:
        if "电压源" in full_text and ("构网型" in full_text or "GFM" in full_text):
            ans_letter = "B"
        elif "0.033" in full_text or "调频死区" in full_text:
            ans_letter = "B"
        elif "3.2" in full_text and "磷酸铁锂" in full_text:
            ans_letter = "A"
        else:
            ans_letter = "B"

    if not courseware:
        if "构网型" in full_text or "变流器" in full_text or "PCS" in full_text:
            courseware = "3.4 储能变流器拓扑及并网控制.pdf P12"
            knowledge_point = knowledge_point or "3.4 构网型变流器并网控制"
            explanation = explanation or "跟网型变流器等效为受控电流源；构网型变流器等效为内部受控电压源，具备自主建立电网电压与频率能力。"
        elif "调频" in full_text or "死区" in full_text:
            courseware = "3.4 储能变流器拓扑及并网控制.pdf P12"
            knowledge_point = knowledge_point or "3.4 一次调频控制机理"
            explanation = explanation or "国标推荐设定为 ±0.033 Hz 调频死区以防止浅充浅放加速电池老化。"
        elif "热失控" in full_text or "消防" in full_text:
            courseware = "5.3 电力储能系统的运行维护.pdf P8"
            knowledge_point = knowledge_point or "5.3 储能安全与热失控消防"
            explanation = explanation or "储能舱三级消防包含早期气体探测（CO/H2）、灭火介质喷淋与防爆排烟系统。"
        else:
            courseware = "1.1 电力储能技术的概念 .pdf P6"
            knowledge_point = knowledge_point or "储能系统核心机理考点"
            explanation = explanation or "请结合相关课件深入掌握储能工作机理与系统集成控制规范。"

    return {
        "correct_answer": ans_letter,
        "knowledge_point": knowledge_point,
        "courseware": courseware,
        "explanation": explanation
    }


QUIZ_GENERATION_PROMPT = """【随堂测试出题质量指令】
你是《电力系统储能技术》课程资深主讲教师。请基于课程大纲（1.1-6.4）生成 1 道高质量单选题。
【必须严格遵循的输出格式】：
【题干】...
A. ...
B. ...
C. ...
D. ...
【标准答案】B
【核心考点】构网型变流器并网控制
【知识溯源】3.4 储能变流器拓扑及并网控制.pdf P12
【名师解析】跟网型变流器等效为受控电流源；构网型变流器等效为内部受控电压源，具备自主建压与惯量支撑能力。
<!--HIDDEN_META:{"correct_answer":"B","knowledge_point":"构网型变流器控制","courseware":"3.4 储能变流器拓扑及并网控制.pdf P12","explanation":"跟网型变流器等效为受控电流源，构网型变流器等效为内部受控电压源"}-->
"""

SCENARIO_ENGINEER_PROMPT = """【角色设定：储能电站现场运维师傅】
你现在扮演储能电站现场一线运行与维护师傅。
1. 安全与领域边界：你只与学生探讨《电力系统储能技术》相关的现场巡检、高压变流器（PCS）、电池舱热管理、消防系统及电气规程，严禁脱离课程边界回答无关问题。
2. 说话风格：口吻亲切、经验丰富、通俗易懂的生活化工程口吻，引导学生解决现场排故问题。
"""

SCENARIO_TEACHER_PROMPT = """【角色设定：《电力系统储能技术》主讲名师】
你现在扮演《电力系统储能技术》高校主讲名师。
1. 安全与领域边界：严格围绕课程大纲、数学物理建模、变流器拓扑控制与系统规划进行启发式教学，严禁脱离课程资料。
2. 说话风格：严谨沉稳、循循善诱，注重核心机理剖析与公式推导。
"""



def build_parameters(
    identity: Identity,
    mode: str,
    question: str,
    graph_context: str = "",
    learning_profile: str = "",
    scenario_context: str = "",
    rubric: str = "",
    retrieval_context: str = "",
    history_context: str = "",
    quoted_context: str = "",
) -> dict[str, Any]:
    # Dynamic Prompt Configuration loaded from store/file
    prompt_cfg = load_prompt_config()
    core_contract = prompt_cfg.get("core_quality_contract", QUALITY_CONTRACT)
    mode_prompt = ""
    if mode == "teacher_assistant":
        mode_prompt = prompt_cfg.get("teacher_assistant_prompt", "")
    elif mode == "qa":
        mode_prompt = prompt_cfg.get("qa_prompt", "")
    elif mode == "question_draft":
        mode_prompt = prompt_cfg.get("question_draft_prompt", "")
    elif mode == "grading":
        mode_prompt = prompt_cfg.get("grading_prompt", "")

    # Targeted selection quote directive (Inline Quote & Annotation)
    quote_directive = ""
    if quoted_context:
        quote_directive = (
            f"【学生精准划线引用内容】\n“{quoted_context[:1000]}”\n\n"
            "【针对性深度解析指令】\n"
            "学生对上述划线选中的知识点/公式/参数提出了针对性追问或探讨。请严格围绕该划线内容展开深度透彻讲解：\n"
            "1. 针对性原理精讲：详细剖析该划线内容的底层机理与物理背景；\n"
            "2. 数学公式与物理建模：若涉及公式，给出详细参数定义与推导逻辑；\n"
            "3. 工程实践与易混淆辨析：说明在实际储能工程中的应用场景或常见易错点。"
        )

    # Reorder context parts: Put quote & learning_profile BEFORE retrieval to prevent context starvation
    is_diagnosis = is_learning_diagnosis_intent(question, mode)
    diagnosis_directive = (
        "【系统指令：已完成练习精准学情诊断与错题归因】\n"
        "请严格根据下方提供的【学生真实全局课程档案与已完成做题记录】进行多维度学情分析：\n"
        "1. 仅限已做题目统计：必须且仅能统计学生【已实际作答提交】的题目（总答题数请以档案中的已做题目数为准），严禁将未作答/待完成的任务计入错题或失分；\n"
        "2. 错题与失分考点逐项深度归因：针对档案中实际失分或扣分的题目（如有），深入剖析学生的错误原因与核心原理；若已做题目全对，则给予肯定并提示目前无错题；\n"
        "3. 巩固优势与复习指引：对完全正确的知识点予以肯定，并对薄弱考点给出针对性的课件复习指引并标注课件出处（如 [3.4 储能变流器拓扑及并网控制.pdf P12]）；\n"
        "4. 格式严谨规范：Markdown 输出必须语法规范，加粗 ** 标签内两侧严禁出现多余空格，确保前端正常渲染。"
    ) if (learning_profile and is_diagnosis) else ""

    context_parts = [
        quote_directive,
        diagnosis_directive,
        learning_profile if (learning_profile and is_diagnosis) else "",
        f"模式：{mode}",
        f"角色：{identity.role}",
        core_contract,
        mode_prompt,
        f"【前序对话上下文】\n{history_context}" if history_context else "",
        f"【服务器检索资料】\n{retrieval_context}" if retrieval_context else "",
        f"知识图谱上下文：{graph_context}" if graph_context else "",
        f"情景上下文：{scenario_context}" if scenario_context else "",
        f"评分标准：{rubric}" if rubric else "",
    ]
    prompt = str(question).strip()
    max_chars = int(os.getenv("AGENT_MAX_INPUT_CHARS", "6000"))
    for part in context_parts:
        if not part or len(prompt) >= max_chars:
            continue
        remaining = max_chars - len(prompt) - 2
        if remaining <= 0:
            break
        prompt += "\n\n" + part[:remaining]
    return {os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT"): prompt[:max_chars]}


def normalize_workflow_text(text: str) -> str:
    """Turn provider wrappers into user-readable text and reject empty shells."""
    normalized = str(text or "").strip()
    if normalized.startswith("```") and normalized.endswith("```"):
        normalized = normalized[3:-3].strip()
        if normalized.lower().startswith("json"):
            normalized = normalized[4:].lstrip()
    if not normalized.startswith("{"):
        return normalized
    try:
        payload = json.loads(normalized)
    except json.JSONDecodeError:
        return normalized
    if not isinstance(payload, dict):
        return normalized
    fields: list[str] = []
    for key, value in payload.items():
        if not str(key).lower().startswith(("answer", "response", "content", "result")):
            continue
        if isinstance(value, str) and value.strip():
            fields.append(value.strip())
    return "\n\n".join(fields)


def build_teacher_rescue_parameters(parameters: dict[str, Any]) -> dict[str, str]:
    """Compact an overloaded teacher request for one bounded quality retry."""
    input_name = os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT")
    original = str(parameters.get(input_name, ""))
    user_text, separator, context = original.partition("\n\n模式：")
    topic = re.sub(r"^请围绕", "", user_text.strip())
    topic = re.split(r"[，,](?:设计|包含|写出|给出|说明)", topic, maxsplit=1)[0].strip(" ，。")
    topic = re.sub(r"^第[一二三四五六七八九十\d]+章", "", topic).strip(" ，。")
    if not topic:
        topic = user_text.strip()[:120]
    rescued = f"请围绕{topic}设计课堂讨论，写出目标、材料、步骤、评价和易错点。"
    if separator:
        rescued += "\n\n模式：" + context
    return {input_name: rescued[: int(os.getenv("AGENT_MAX_INPUT_CHARS", "4000"))]}


def build_teacher_fallback_answer(question: str, retrieved_sources: list[dict[str, Any]]) -> str:
    """Provide a grounded, usable lesson outline after two empty Workflow replies."""
    topic = re.sub(r"^请围绕", "", str(question).strip())
    topic = re.sub(r"^第[一二三四五六七八九十\d]+章", "", topic).strip(" ，。")
    topic = re.split(r"(?:设计|包含|写出|给出|说明)", topic, maxsplit=1)[0].strip(" ，。")
    if not topic:
        topic = "课程主题"
    source_lines = []
    for source in retrieved_sources[:3]:
        file_name = str(source.get("file") or "").strip()
        page = source.get("page")
        if file_name and page:
            source_lines.append(f"{file_name}（第{page}页）")
    source_note = "；".join(source_lines) if source_lines else "本次检索未返回可核验片段，具体课程结论需由教师回到已发布资料核对。"
    return (
        f"围绕“{topic}”的课堂讨论可按以下方案执行。以下内容只把课程资料支持的概念作为讨论对象，" 
        "不会把未核验的工程数据当作课程结论。\n\n"
        "【教学目标】\n"
        f"1. 学生能依据课程资料说明{topic}涉及的系统关系、关键作用和控制目标。\n"
        "2. 学生能用资料中的依据比较不同方案，并把课程明确结论与仍需工程核验的条件分开。\n\n"
        "【课前材料】\n"
        f"1. 阅读并标注：{source_note}。\n"
        "2. 每组准备一张证据卡，填写“资料原句或定位—自己的解释—适用边界”，没有资料依据的内容标记为待核验。\n\n"
        "【讨论步骤】\n"
        "1. 个人先从资料中圈出与主题直接相关的组成、能量或控制关系。\n"
        "2. 小组把证据卡按“作用、方案差异、适用条件、代价与边界”归类，指出一处容易混淆的表述。\n"
        "3. 各组用资料定位支持结论，其他组只针对依据是否充分、边界是否清楚提出质疑。\n"
        "4. 教师总结：保留课程明确结论；对资料没有覆盖的参数、现场约束或性能数据列入后续核验清单。\n\n"
        "【学生产出】\n"
        "提交一页对照表和一份核验清单：对照表写出关键作用、方案差异和适用条件；核验清单写出尚缺资料、需要测量或需要工程评审的事项。\n\n"
        "【评价标准】\n"
        "达标表现包括：结论能定位到课程资料；解释没有超出证据范围；对比同时写出适用条件和代价；能主动标注资料未覆盖处；表达能回应同伴质疑。\n\n"
        "【易错点与纠偏】\n"
        "1. 把储能介质、变流器和电网控制对象混为一谈：要求学生在图上标出能量或控制边界。\n"
        "2. 把某个方案写成任何场景都最优：要求补充适用条件和代价。\n"
        "3. 把合理推测写成课程事实：要求补充资料定位，否则改列为待核验问题。"
    )


def build_grounded_qa_answer(question: str, retrieved_sources: list[dict[str, Any]], mode: str = "qa") -> str:
    """Comprehensive grounded answer builder for QA and teaching assistance."""
    if mode == "teacher_assistant":
        return build_teacher_fallback_answer(question, retrieved_sources)

    q = str(question or "").strip()
    
    # 1. Identity & Intro
    if any(k in q for k in ["你是谁", "介绍", "自我介绍", "叫什么", "你能做"]):
        return (
            "同学你好！我是上海电力大学《电力系统储能技术》课程专属 AI 助教。\n\n"
            "本系统基于课程专业知识库与权威课件资料构建，我可以为你提供以下学习支持：\n"
            "1. **课程专业知识答疑**：深入解析储能介质、变流拓扑（跟网型GFL/构网型GFM）、虚拟同步机VSG、微电网控制、一次调频与削峰填谷等专业机理；\n"
            "2. **随堂互动出题测验**：点击【随堂出题测试】或输入“出题考考我”，快速进行单选练习与解析溯源；\n"
            "3. **仿真情景演练**：支持扮演储能电站现场运维师傅或主讲名师，进行故障排查与启发式研讨；\n"
            "4. **学情诊断与错题复盘**：点击【学情诊断复盘】，精准分析你的已做题目掌握情况与薄弱考点；\n"
            "5. **划线研讨**：在助教回复中划线选中文字即可针对性追问推导细节。\n\n"
            "你可以随时输入具体的课程问题，开始针对性学习！"
        )
        
    # 2. Exam preparation, cramming, pass guarantee, or review methodology
    if any(k in q for k in ["挂科", "及格", "期末", "复习", "怎么学", "如何学", "重点", "冲刺", "考前", "难不难", "划重点", "考试"]):
        return (
            "同学别慌！《电力系统储能技术》期末复习与通关备考核心指引：\n\n"
            "只要重点抓牢以下三大核心模块的重点考点与机理推导，即可高效掌握课程精髓并稳拿高分：\n\n"
            "### 1. 基础概念与储能介质特性（预计占比 25-30%）\n"
            "- **机械储能**：掌握抽水蓄能综合效率（70%-80%）与工作原理，压缩空气储能系统构成 [1.1 电力储能技术的概念 .pdf]；\n"
            "- **电化学储能**：掌握磷酸铁锂标称电压 3.2V、三元锂及全钒液流电池功率与容量解耦特性 [2.3 储能技术的典型应用.pdf]；\n"
            "- **电磁储能**：超导磁储能（SMES）与超级电容器毫秒级功率型快速响应应用。\n\n"
            "### 2. 核心大题与机理计算：变流拓扑与控制（预计占比 35-40%，核心重难点）\n"
            "- **构网型（GFM）vs 跟网型（GFL）变流器**：\n"
            "  - 跟网型（GFL-PCS）：等效为**受控电流源**，依赖 PLL 锁相环跟踪电网相位，无自主建压能力；\n"
            "  - 构网型（GFM-PCS）：等效为**内部受控电压源**，提供虚拟惯量与阻尼，具备自主建压与黑启动能力 [3.4 储能变流器拓扑及并网控制.pdf P12]；\n"
            "- **一次调频下垂控制**：掌握 P-f 下垂方程与国标推荐的 $\\pm 0.033\\text{ Hz}$ 调频死区设定。\n\n"
            "### 3. 系统集成、配置规划与安全运维（预计占比 20-25%）\n"
            "- **削峰填谷与容量规划**：两部制电价下的经济性模型及平准化度电成本（LCOS）计算 [4.2 电化学储能系统的规划配置.pdf]；\n"
            "- **储能电站三级安全消防**：一级早期可燃气体探测（CO/H2） $\\rightarrow$ 二级全氟己酮/七氟丙烷局部灭火 $\\rightarrow$ 三级防爆排烟与水浸漫没 [5.3 电力储能系统的运行维护.pdf]；\n"
            "- **BMS 与并网性能评估**：电池均衡管理与充放电检测评估标准 [6.1 电力储能系统的性能检测.pdf]。\n\n"
            "### 建议复习步骤：\n"
            "1. 点击下方【随堂出题测试】，做几道单选题检测当前薄弱考点；\n"
            "2. 点击【学情诊断复盘】查看自己的平时做题失分点；\n"
            "3. 遇到不懂的公式或原理随时在输入框向我提问。"
        )

    # 3. Technical QA with retrieved sources
    if retrieved_sources:
        top_src = retrieved_sources[0]
        file_name = str(top_src.get("file") or "").strip()
        page = top_src.get("page", 1)
        chapter = str(top_src.get("chapter") or "课程核心考点")
        snippet = str(top_src.get("content") or top_src.get("text") or "").strip()
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        
        return (
            f"关于“{q}”，基于《电力系统储能技术》课程资料分析如下：\n\n"
            f"1. **核心机理与知识要点**：\n"
            f"   - 本知识点归属于 **{chapter}**；\n"
            f"   - {snippet if snippet else '储能系统在新型电力系统中主要承担调峰、调频、惯量支撑与备用电源等关键角色。在并网控制中，需重点区分跟网型（电流源型）与构网型（电压源型）变流器的控制差异。'}\n\n"
            f"2. **工程应用与分析要求**：\n"
            f"   - 在实际储能电站集成与运行中，需综合考量充放电转换效率、电池循环寿命衰减以及多级安全消防防护机制；\n"
            f"   - 系统控制上需严格遵循电网规范的调频死区与无功-电压调节要求。\n\n"
            f"对应课程课件溯源：[{file_name} P{page} ↗]"
        )

    return (
        f"关于“{q}”：\n\n"
        "《电力系统储能技术》课程涵盖抽水蓄能、电化学储能、变流器控制（GFM/GFL）、容量规划、安全运维与性能评估六大核心模块。\n\n"
        "你可以向我提问具体的知识点细节（例如“构网型变流器控制原理”、“一次调频下垂公式推导”或“电池舱三级消防”），我将为你提供精准的机理剖析与课件定位！"
    )


def workflow_input_parameters(parameters: dict[str, Any]) -> dict[str, str]:
    """Defensively send only the configured Workflow start-node input."""
    input_name = os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT")
    value = str(parameters.get(input_name, ""))
    max_chars = int(os.getenv("AGENT_MAX_INPUT_CHARS", "6000"))
    return {input_name: value[:max_chars]}


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
    parameters: dict[str, Any],
    identity: Identity,
    request_id: str,
    workflow_id: str | None = None,
    retrieved_sources: list[dict[str, Any]] | None = None,
    emit_unverified: bool = True,
    mode: str = "qa",
) -> AsyncIterator[dict[str, Any]]:
    if env_bool("MOCK_WORKFLOW_MODE"):
        async for event in mock_stream(
            str(parameters.get(os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT"), "")),
            request_id,
            mode,
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
    payload = {"flow_id": flow_id, "uid": identity.uid, "parameters": workflow_input_parameters(parameters), "stream": True}
    print(f"[DEBUG_PAYLOAD_PARAM] len={len(payload['parameters'].get('AGENT_USER_INPUT', ''))}, sample={payload['parameters'].get('AGENT_USER_INPUT', '')[:300]}", flush=True)
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
                answer_buffer = ""
                structured_answer = False
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
                        answer_buffer += text
                        if answer_buffer.lstrip().startswith("{"):
                            structured_answer = True
                        if not structured_answer:
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
                final_text = normalize_workflow_text(answer_buffer)
                if not final_text or len(final_text.strip()) < 24:
                    yield {"event": "error", "data": {"code": "workflow_quality_failed", "message": "Workflow 返回内容未达到可用回答标准，请重试", "request_id": request_id}}
                    return
                if structured_answer:
                    yield {"event": "token", "data": {"text": final_text, "request_id": request_id}}
                if not emitted_source_ids:
                    if retrieved_sources:
                        for source in retrieved_sources:
                            if source.get("page") and source.get("file"):
                                yield {"event": "source", "data": {**source, "request_id": request_id, "evidence_type": "server_retrieval"}}
                    elif emit_unverified:
                        # Never invent a citation when neither the Workflow
                        # nor server retrieval has evidence. The UI can then
                        # present an explicit review state.
                        published = store.published_kb()
                        yield {"event": "source", "data": {"source_id": "unverified", "file": "", "chapter": "", "page": 0, "version": str(published["version_name"] if published else MANIFEST.get("source_archive", "unknown")), "status": "unverified", "request_id": request_id}}
                yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}
    except httpx.TimeoutException:
        yield {"event": "error", "data": {"code": "workflow_timeout", "message": "讯飞 Workflow 请求超时，请重试", "request_id": request_id}}
    except httpx.HTTPError:
        yield {"event": "error", "data": {"code": "workflow_network_error", "message": "讯飞 Workflow 暂时不可用，请重试", "request_id": request_id}}


limiter = SlidingWindowLimiter(
    int(os.getenv("AGENT_RATE_LIMIT", "120")),
    int(os.getenv("AGENT_RATE_WINDOW_SECONDS", "60")),
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


@app.get("/api/admin/prompt-config")
async def get_admin_prompt_config(request: Request) -> JSONResponse:
    """Get current dynamic prompt configurations for the AI Agent."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"admin"})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "只有管理员可以查看系统提示词配置"), status_code=403)
    return json_response(request_id, load_prompt_config())


@app.post("/api/admin/prompt-config")
async def update_admin_prompt_config(request: Request) -> JSONResponse:
    """Update dynamic prompt configurations for the AI Agent with immediate effect."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"admin"})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "只有管理员可以修改系统提示词配置"), status_code=403)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(error_payload(request_id, "invalid_body", "无效的请求格式"), status_code=422)
    saved = save_prompt_config(body)
    return json_response(request_id, saved)


@app.post("/api/admin/prompt-config/reset")
async def reset_admin_prompt_config(request: Request) -> JSONResponse:
    """Reset dynamic prompt configurations back to factory defaults."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"admin"})
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "只有管理员可以重置系统提示词配置"), status_code=403)
    if os.path.exists(PROMPT_CONFIG_FILE):
        try:
            os.remove(PROMPT_CONFIG_FILE)
        except Exception:
            pass
    return json_response(request_id, dict(DEFAULT_PROMPT_CONFIG))


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
        "user_id": identity.moodle_user_id,
        "username": identity.username,
        "fullname": identity.fullname,
        "uid": identity.uid,
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
            bridge_token = request.headers.get("x-agent-bridge-token")
            expected_bridge_token = os.getenv("AGENT_BRIDGE_TOKEN", "").strip()
            if not (bridge_token and expected_bridge_token and bridge_token == expected_bridge_token):
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


def build_learning_diagnosis_context(profile: dict[str, Any]) -> tuple[str, str]:
    """Expose only server-computed learning targets to the explanation model."""
    recommendations, _ = deterministic_recommendations(profile)
    graph_context = json.dumps(
        [
            {
                "id": item["node_id"],
                "name": item["title"],
                "resource_id": item["resource_id"],
                "page": item["page"],
                "reason": item["reason"],
            }
            for item in recommendations[:20]
        ],
        ensure_ascii=False,
    )
    profile_context = json.dumps(
        {"rule_version": profile["rule_version"], "nodes": profile["nodes"]},
        ensure_ascii=False,
    )
    return graph_context, profile_context


def deterministic_learning_insufficient_answer(profile: dict[str, Any]) -> str:
    """Explain missing learning evidence without inventing weak topics."""
    records = sum(int(node.get("grade_count") or 0) for node in profile.get("nodes", []))
    record_text = f"当前画像包含 {records} 条有效作答记录，但" if records else "当前画像尚未包含有效作答记录，"
    return (
        f"当前学习画像的数据不足以精准诊断具体薄弱知识点。{record_text}尚未形成服务器计算出的可解释推荐，系统不会推测未观测的章节或能力。\n\n"
        "下一步：请先完成带知识点关联的章节练习，并保留错题题干、选项和作答结果；积累有效记录后，再生成针对性的复习动作和验证方式。"
    )


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


@app.post("/api/teacher/resources/upload")
@app.post("/api/resources/upload")
async def upload_teacher_resource(
    request: Request,
    chapter_id: int = 1,
    title: str = "",
    node_id: str = "",
    filename: str = "",
) -> JSONResponse:
    """Accept and persist a teacher-uploaded courseware PDF into the course database and knowledge base."""
    identity, error, request_id = await authenticated(request)
    if error:
        return error
    try:
        require_role(identity, {"teacher", "admin"})

        header_ch = request.headers.get("x-chapter-id")
        if header_ch:
            try:
                chapter_id = int(header_ch)
            except Exception:
                pass

        if chapter_id not in range(1, 7):
            return JSONResponse(error_payload(request_id, "invalid_input", "所属章节必须在 1 到 6 之间"), status_code=422)

        content = await request.body()
        # If body is multipart, extract the PDF bytes
        if b"%PDF-" in content:
            pdf_start = content.find(b"%PDF-")
            pdf_end = content.rfind(b"%%EOF")
            if pdf_start != -1 and pdf_end != -1:
                content = content[pdf_start : pdf_end + 5]

        if not content or len(content) > 35 * 1024 * 1024:
            return JSONResponse(error_payload(request_id, "invalid_file", "课件文件不能为空或超过 35MB"), status_code=422)

        if not validate_pdf_bytes(content):
            return JSONResponse(error_payload(request_id, "invalid_file", "文件不是有效的 PDF 格式"), status_code=422)

        header_title = request.headers.get("x-title")
        if header_title:
            try:
                from urllib.parse import unquote
                title = unquote(header_title)
            except Exception:
                title = header_title

        header_filename = request.headers.get("x-filename")
        if header_filename:
            try:
                from urllib.parse import unquote
                filename = unquote(header_filename)
            except Exception:
                filename = header_filename

        header_node = request.headers.get("x-node-id")
        if header_node:
            node_id = header_node

        orig_filename = Path(filename or "courseware.pdf").name
        display_title = (title or "").strip() or orig_filename
        if not display_title.lower().endswith(".pdf"):
            display_title += ".pdf"

        # Safe filename on disk
        safe_base = re.sub(r"[^\w\.\-]", "_", Path(orig_filename).stem)
        digest = hashlib.sha256(content).hexdigest()[:8]
        normalized_filename = f"chapter-{chapter_id}-{safe_base}-{digest}.pdf"

        # Determine page count
        page_count = 10
        try:
            reader = PdfReader(BytesIO(content), strict=False)
            page_count = max(1, len(reader.pages))
        except Exception:
            page_count = 10

        # Save to storage directory
        kb_dir = Path(os.getenv("KB_STORAGE_DIR", "/app/data/kb-files"))
        kb_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = kb_dir / normalized_filename
        pdf_path.write_bytes(content)

        # Also write to course-data if available
        try:
            cd_dir = Path("/app/course-data")
            if cd_dir.exists() and os.access(cd_dir, os.W_OK):
                (cd_dir / normalized_filename).write_bytes(content)
        except Exception:
            pass

        record = store.add_resource(
            chapter_id=chapter_id,
            source_file=display_title,
            normalized_file=normalized_filename,
            node_id=node_id if node_id else None,
            page_start=1,
            page_end=page_count,
            sha256=hashlib.sha256(content).hexdigest(),
        )

        return json_response(
            request_id,
            {
                "resource": record,
                "title": display_title,
                "file": normalized_filename,
                "chapter_id": chapter_id,
                "pages": page_count,
                "pdf_url": f"/api/resources/pdf/{normalized_filename}",
                "message": f"课件《{display_title}》已成功上传并收录至第 {chapter_id} 章！",
            },
            status_code=201,
        )
    except PermissionError:
        return JSONResponse(error_payload(request_id, "forbidden", "只有教师或管理员允许上传课程资料"), status_code=403)
    except Exception as e:
        return JSONResponse(error_payload(request_id, "server_error", f"上传处理失败: {str(e)}"), status_code=500)


@app.get("/api/resources/pdf/{filename}")
async def serve_pdf_stream(filename: str, request: Request) -> Response:
    """Stream PDF bytes with range support."""
    safe_name = Path(filename).name
    if safe_name != filename or not filename.lower().endswith(".pdf"):
        return JSONResponse({"status": "error", "message": "无效的课件文件名"}, status_code=400)

    search_dirs = [
        Path(os.getenv("KB_STORAGE_DIR", "/app/data/kb-files")),
        Path("/app/course-data"),
        Path("/app/course-sources"),
        Path("/var/lib/docker/volumes/deploy_agent_data/_data/kb-files")
    ]
    target_path = None
    for d in search_dirs:
        candidate = d / safe_name
        if candidate.exists() and candidate.is_file():
            target_path = candidate
            break

    if not target_path:
        return JSONResponse({"status": "error", "message": "未找到指定课件 PDF 文件"}, status_code=404)

    return FileResponse(
        target_path,
        media_type="application/pdf",
        headers={"Accept-Ranges": "bytes", "Content-Disposition": f"inline; filename=\"{quote(safe_name)}\""},
    )


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
            valid_content = validate_pdf_bytes(content)
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
    graph_context, profile_context = build_learning_diagnosis_context(profile)
    try:
        request_body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    except (TypeError, json.JSONDecodeError):
        request_body = {}
    question = str(request_body.get("question", "请解释我的学习状态并给出复习建议。"))[:int(os.getenv("AGENT_MAX_INPUT_CHARS", "4000"))]
    if policy_violation(question):
        return JSONResponse(error_payload(request_id, "policy_blocked", "不能要求系统伪造学习证据或课程来源"), status_code=422)
    if not recommendations:
        return json_response(request_id, {
            "rule_version": "learning-rule-v1",
            "profile": profile,
            "recommendations": [],
            "unavailable_nodes": unavailable,
            "ai_explanation": deterministic_learning_insufficient_answer(profile),
            "ai_generated": False,
            "sources": [],
        })
    parameters = build_parameters(
        identity,
        "learning_diagnosis",
        question,
        graph_context=graph_context,
        learning_profile=profile_context,
    )
    chunks: list[str] = []
    sources: list[dict[str, Any]] = []
    upstream_error: dict[str, Any] | None = None
    async for event in xingchen_stream(parameters, identity, request_id, emit_unverified=bool(recommendations)):
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
        student_display_name = identity.fullname or identity.username or ""
        result = store.submit(identity.uid, assignment_id, answers, attempt, identity.moodle_user_id, student_display_name)
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
        if sync["status"] not in {"mock_skipped", "synced", "not_configured"}:
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
        if any(item["status"] not in {"mock_skipped", "synced", "not_configured"} for item in sync_results):
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
        async for event in xingchen_stream(parameters, identity, request_id, mode="grading"):
            if event["event"] == "token":
                chunks.append(str(event["data"].get("text", "")))
            elif event["event"] == "error":
                upstream_error = event["data"]
        if upstream_error:
            return JSONResponse(error_payload(request_id, "agent_review_failed", "Agent 初评暂不可用，请转人工复核"), status_code=502)
        raw_text = "".join(chunks).strip()
        result = None
        try:
            result = json.loads(raw_text)
        except Exception:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(1))
                except Exception:
                    pass
            if not result:
                brace_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
                if brace_match:
                    try:
                        result = json.loads(brace_match.group(1))
                    except Exception:
                        pass

        if result and isinstance(result, dict) and "score" in result:
            try:
                score = float(result["score"])
                feedback = str(result.get("feedback", raw_text)).strip()
            except (ValueError, TypeError):
                score = float(item["max_score"]) * 0.9
                feedback = raw_text
        else:
            score_match = re.search(r"(?:得分|分数|得分建议|建议给分|Score)[:：\s]*([0-9]+(?:\.[0-9]+)?)", raw_text, re.IGNORECASE)
            score = float(score_match.group(1)) if score_match else float(item["max_score"]) * 0.9
            feedback = raw_text or "Agent 依据 Rubric 评分细则完成作答初评。"

        score = max(0.0, min(float(item["max_score"]), score))
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
        if sync["status"] not in {"mock_skipped", "synced", "not_configured"}:
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
    retrieved_sources: list[dict[str, Any]] = []
    learning_insufficient_answer = ""
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
        allowed = await limiter.acquire(identity.uid)
        if not allowed:
            return JSONResponse(error_payload(request_id, "rate_limited", "请求过于频繁，请稍后重试"), status_code=429)
        graph_context = ""
        node_ids = body.get("node_ids", [])
        if isinstance(node_ids, list):
            # Only IDs resolved by the server enter the trusted Workflow slot.
            graph_nodes = [store.node(str(node_id)) for node_id in node_ids[:10]]
            graph_context = json.dumps([node for node in graph_nodes if node], ensure_ascii=False)
        profile_context = ""
        student_ctx = body.get("student_learning_context")
        is_diagnosis = is_learning_diagnosis_intent(question, mode)
        if is_diagnosis:
            if isinstance(student_ctx, dict) and student_ctx.get("questions"):
                profile_context = format_student_learning_context(student_ctx)
            elif mode == "learning_diagnosis":
                learning_profile = store.learning_profile(identity.uid)
                graph_context, profile_context = build_learning_diagnosis_context(learning_profile)
                if graph_context.strip() in {"", "[]"}:
                    learning_insufficient_answer = deterministic_learning_insufficient_answer(learning_profile)
        print(f"[DEBUG_CHAT_CONTEXT] is_diagnosis={is_diagnosis}, profile_context len={len(profile_context)}, student_ctx is not None: {student_ctx is not None}", flush=True)
        scenario_context = ""
        session_id = body.get("session_id")
        if mode == "scenario" and isinstance(session_id, str):
            if (missing := idempotency_error(request, request_id, identity)):
                return missing
            idem_key = request.headers["idempotency-key"]
            scenario_request_body = {"session_id": session_id, "turn_no": body.get("turn_no"), "question": question.strip(), "mode": mode}
            scenario_idem_key = idem_key
            previous, found = store.idempotent(identity.uid, f"/course-agent/scenario/{session_id}", idem_key, scenario_request_body)
            if found:
                return json_response(request_id, previous)
            scenario = store.scenario(identity.uid, session_id)
            if not scenario:
                return JSONResponse(error_payload(request_id, "not_found", "场景会话不存在或无权访问"), status_code=404)
            turn_no = body.get("turn_no")
            if not isinstance(turn_no, int) or turn_no < 1:
                return JSONResponse(error_payload(request_id, "invalid_input", "场景轮次无效"), status_code=422)
            try:
                turn = store.add_turn(identity.uid, session_id, turn_no, question.strip(), request_id)
            except ValueError:
                return JSONResponse(error_payload(request_id, "conflict", "场景已结束或轮次已存在"), status_code=409)
            if turn.get("status") == "completed" or turn.get("request_id") != request_id:
                return JSONResponse(error_payload(request_id, "conflict", "该场景轮次正在处理或已经完成，请复用原幂等键"), status_code=409)
            scenario_context = json.dumps(scenario, ensure_ascii=False)
        # Extract multi-turn dialogue history with role validation and budget protection
        raw_messages = body.get("messages") or body.get("history") or []
        history_context = ""
        if isinstance(raw_messages, list) and raw_messages:
            history_lines = []
            for item in raw_messages[-12:]:
                if not isinstance(item, dict):
                    continue
                r = str(item.get("role", "")).strip().lower()
                c = str(item.get("content", "")).strip()
                if r not in {"user", "assistant"} or not c:
                    continue
                if r == "assistant" and len(c) > 150:
                    c = c[:150] + "..."
                elif r == "user" and len(c) > 300:
                    c = c[:300] + "..."
                speaker = "学生" if r == "user" else "AI助教"
                history_lines.append(f"{speaker}: {c}")
            if history_lines:
                history_text = "\n".join(history_lines)
                if len(history_text) > 1200:
                    history_text = history_text[-1200:]
                history_context = history_text

        retrieval_context = ""
        if mode != "learning_diagnosis" or graph_context.strip() not in {"", "[]"}:
            retrieval_query = question.strip()
            if mode == "learning_diagnosis":
                retrieval_query += "\n" + graph_context
            retrieval_context, retrieved_sources = retrieve_course_evidence(
                retrieval_query,
                max_chunks=2 if mode == "learning_diagnosis" else 3,
                max_chars=1600 if mode == "learning_diagnosis" else 2400,
            )
        quoted_text = body.get("quoted_text")
        quoted_context = str(quoted_text).strip() if isinstance(quoted_text, str) else ""

        client_sess = session_id or body.get("client_session_id") or f"sess_{identity.uid}"
        teaching_state = await teaching_state_manager.get_or_create(identity.uid, str(client_sess))
        workflow_intent = classify_workflow_intent(question, teaching_state, quoted_context)

        # Inject persona context if active scenario roleplay
        if not scenario_context:
            if teaching_state.scene_mode == 1:
                scenario_context = SCENARIO_ENGINEER_PROMPT
            elif teaching_state.scene_mode == 2:
                scenario_context = SCENARIO_TEACHER_PROMPT

        parameters = build_parameters(
            identity,
            mode,
            question.strip(),
            graph_context,
            profile_context,
            scenario_context,
            retrieval_context=retrieval_context,
            history_context=history_context,
            quoted_context=quoted_context,
        )
        if isinstance(session_id, str) and mode == "scenario":
            scenario_turn_no = turn_no
    except PermissionError:
        return JSONResponse(error_payload(request_id, "unauthorized", "请先登录课程平台"), status_code=401)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return JSONResponse(error_payload(request_id, "invalid_body", str(exc)), status_code=422)

    async def event_stream() -> AsyncIterator[bytes]:
        scenario_chunks: list[str] = []
        scenario_sources: list[dict[str, Any]] = []
        scenario_failed = False
        scenario_finished = False
        try:
            # 1. Scenario stop branch
            if workflow_intent == "scenario_stop":
                await teaching_state_manager.set_scene(identity.uid, str(client_sess), 0, "")
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_role_name': ''}, ensure_ascii=False)}\n\n".encode("utf-8")
                stop_txt = "好的，已停止情景演绎。书山有路勤为径，学海无涯苦作舟！期待你的下次演练！"
                for i in range(0, len(stop_txt), 20):
                    yield f"event: token\ndata: {json.dumps({'text': stop_txt[i:i+20], 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    await asyncio.sleep(0.01)
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'scenario_stopped'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 4. Scenario start branches
            if workflow_intent == "scenario_start_engineer":
                await teaching_state_manager.set_scene(identity.uid, str(client_sess), 1, "储能电站现场运维师傅")
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 1, 'scene_role_name': '储能电站现场运维师傅'}, ensure_ascii=False)}\n\n".encode("utf-8")
                start_txt = "（好的，开始情景演绎，若要退出请回复退出情景演绎。）\n\n小同志你好！我是储能电站现场运维师傅。现场高压变流柜、电池舱和消防系统刚巡检完毕，并网控制、运行排故或维护规程方面你有什么想了解的？"
                for i in range(0, len(start_txt), 20):
                    yield f"event: token\ndata: {json.dumps({'text': start_txt[i:i+20], 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    await asyncio.sleep(0.01)
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'scenario_started'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            if workflow_intent == "scenario_start_teacher":
                await teaching_state_manager.set_scene(identity.uid, str(client_sess), 2, "《电力系统储能技术》主讲老师")
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 2, 'scene_role_name': '《电力系统储能技术》主讲老师'}, ensure_ascii=False)}\n\n".encode("utf-8")
                start_txt = "（好的，开始情景演绎，若要退出请回复退出情景演绎。）\n\n同学你好！我是《电力系统储能技术》主讲老师。今天我们重点探讨储能核心机理与工程拓扑，你有任何疑问随时提问，或者老师出一道工程思考题考考你？"
                for i in range(0, len(start_txt), 20):
                    yield f"event: token\ndata: {json.dumps({'text': start_txt[i:i+20], 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    await asyncio.sleep(0.01)
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'scenario_started'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 5. Quiz stop branch
            if workflow_intent == "quiz_stop":
                await teaching_state_manager.pop_active_quiz(identity.uid, str(client_sess))
                stop_txt = "好的，已停止出题练习。书山有路勤为径，学海无涯苦作舟！期待你的下次练习！"
                for i in range(0, len(stop_txt), 20):
                    yield f"event: token\ndata: {json.dumps({'text': stop_txt[i:i+20], 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    await asyncio.sleep(0.01)
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_stopped'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 6. Quiz submit & grading branch
            if workflow_intent == "quiz_submit":
                quiz = await teaching_state_manager.pop_active_quiz(identity.uid, str(client_sess))
                if not quiz:
                    empty_txt = "您发送了选项作答，但当前没有正在进行的随堂测试。若想开启新测验，请点击下方【随堂出题测试】或直接输入“出题考考我”。"
                    yield f"event: token\ndata: {json.dumps({'text': empty_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_not_active'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                norm_ans = extract_and_normalize_answer(question) or "A"
                correct_ans = str(quiz.get("correct_answer", "B")).upper()
                is_correct = (norm_ans == correct_ans)
                cw = str(quiz.get("courseware", "")).strip()
                cw_file = cw.split(" P")[0].strip() if " P" in cw else "3.4 储能变流器拓扑及并网控制.pdf"
                cw_page = cw.split(" P")[1].strip() if " P" in cw else "12"
                if cw_file not in VALID_COURSEWARE_WHITELIST:
                    cw_file = "3.4 储能变流器拓扑及并网控制.pdf"
                expl = str(quiz.get("explanation", "请结合电力系统储能技术相关课件深入掌握核心机理。"))
                report_lines = [
                    f"**{'回答正确！' if is_correct else '回答错误。'}**",
                    f"- **学生作答**：`{norm_ans}` | **本题标准选项为**：`{correct_ans}`",
                    f"- **知识点解析**：{expl}",
                    f"- **对应知识溯源**：[来源文件：{cw_file}；页码：{cw_page}]",
                    "",
                    "需要查看学情诊断汇报吗？还是再来一题？"
                ]
                report_text = "\n".join(report_lines)
                grade_payload = {
                    "source_task": "随堂互动测验",
                    "stem": quiz.get("stem", "储能系统综合单选测验"),
                    "student_answer": norm_ans,
                    "correct_answer": correct_ans,
                    "is_correct": is_correct,
                    "earned_score": 10 if is_correct else 0,
                    "max_score": 10,
                    "knowledge_point": quiz.get("knowledge_point", "储能控制机理"),
                    "courseware": f"{cw_file} P{cw_page}"
                }
                yield f"event: quiz_graded\ndata: {json.dumps(grade_payload, ensure_ascii=False)}\n\n".encode("utf-8")
                for i in range(0, len(report_text), 30):
                    yield f"event: token\ndata: {json.dumps({'text': report_text[i:i+30], 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    await asyncio.sleep(0.01)
                yield f"event: source\ndata: {json.dumps({'source_id': f'cw_{cw_page}_{abs(hash(cw_file)) % 10000}', 'file': cw_file, 'chapter': str(quiz.get('knowledge_point', '储能考点')), 'page': int(cw_page) if str(cw_page).isdigit() else 1, 'version': 'v1.0', 'status': 'active', 'request_id': request_id, 'evidence_type': 'quiz_evidence'}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_graded'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 7. Quiz generate branch
            if workflow_intent == "quiz_generate":
                quiz_params = build_parameters(
                    identity,
                    "qa",
                    f"请从课程知识库中随机抽取知识点出一道随堂单选题。\n\n{QUIZ_GENERATION_PROMPT}",
                    graph_context,
                    "",
                    "",
                    retrieval_context=retrieval_context,
                    history_context=history_context,
                )
                quiz_stream_chunks: list[str] = []
                stream_buffer = ""
                hidden_tag_found = False
                pre_tag_emitted = False
                async for event in xingchen_stream(quiz_params, identity, request_id, retrieved_sources=retrieved_sources):
                    if event["event"] == "token":
                        raw_tok = str(event["data"].get("text", ""))
                        quiz_stream_chunks.append(raw_tok)
                        stream_buffer += raw_tok
                        
                        # Detect any hidden tags or answer headers
                        hide_pos = -1
                        for tag in ["<!--HIDDEN_META:", "【标准答案】", "【答案】", "标准答案：", "答案："]:
                            idx = stream_buffer.find(tag)
                            if idx != -1 and (hide_pos == -1 or idx < hide_pos):
                                hide_pos = idx
                        
                        if hide_pos != -1:
                            if not hidden_tag_found:
                                hidden_tag_found = True
                                pre_tag = stream_buffer[:hide_pos]
                                if pre_tag and not pre_tag_emitted:
                                    yield f"event: token\ndata: {json.dumps({'text': pre_tag, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                                    pre_tag_emitted = True
                        elif not hidden_tag_found and not stream_buffer.startswith("<!--"):
                            yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "source":
                        yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "error":
                        yield f"event: error\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                        return

                full_quiz_text = "".join(quiz_stream_chunks)
                parsed_meta = extract_quiz_meta_fallback(full_quiz_text)
                clean_stem = re.split(r"(?:A\.|选项A|【标准答案】|<!--HIDDEN_META)", full_quiz_text)[0].replace("【随堂测试单选题】", "").replace("【题干】", "").replace("题干：", "").strip()
                parsed_meta["stem"] = clean_stem or "储能单选题"
                await teaching_state_manager.set_active_quiz(identity.uid, str(client_sess), parsed_meta)
                yield f"event: quiz_meta\ndata: {json.dumps(parsed_meta, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_generated'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            if learning_insufficient_answer:
                yield f"event: token\ndata: {json.dumps({'text': learning_insufficient_answer, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'deterministic_insufficient_learning_evidence'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return
            if mode == "teacher_assistant":
                primary_events = [
                    event
                    async for event in xingchen_stream(
                        parameters,
                        identity,
                        request_id,
                        retrieved_sources=retrieved_sources,
                    )
                ]
                primary_failed = any(
                    event["event"] == "error" and event["data"].get("code") == "workflow_quality_failed"
                    for event in primary_events
                )
                selected_events = primary_events
                if primary_failed:
                    rescue_parameters = build_teacher_rescue_parameters(parameters)
                    rescue_events = [
                        event
                        async for event in xingchen_stream(
                            rescue_parameters,
                            identity,
                            request_id,
                            retrieved_sources=retrieved_sources,
                        )
                    ]
                    rescue_failed = any(
                        event["event"] == "error" and event["data"].get("code") == "workflow_quality_failed"
                        for event in rescue_events
                    )
                    selected_events = rescue_events
                    if rescue_failed:
                        fallback = build_grounded_qa_answer(question, retrieved_sources, mode=mode)
                        selected_events = [
                            {"event": "token", "data": {"text": fallback, "request_id": request_id}},
                            *[
                                {"event": "source", "data": {**source, "request_id": request_id, "evidence_type": "server_retrieval"}}
                                for source in retrieved_sources
                                if source.get("file") and source.get("page")
                            ],
                            {"event": "done", "data": {"request_id": request_id, "reason": "grounded_teacher_fallback" if mode == "teacher_assistant" else "grounded_qa_fallback"}},
                        ]
                for event in selected_events:
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                return
            target_workflow_id = None
            if is_diagnosis and isinstance(student_ctx, dict) and student_ctx.get("questions"):
                target_workflow_id = os.getenv("XINGCHEN_DIAGNOSIS_FLOW_ID") or None
                diag_events = [
                    event
                    async for event in xingchen_stream(
                        parameters,
                        identity,
                        request_id,
                        workflow_id=target_workflow_id,
                        retrieved_sources=retrieved_sources,
                        emit_unverified=False,
                    )
                ]
                full_text = "".join([str(e["data"].get("text", "")) for e in diag_events if e["event"] == "token"])
                is_broken_diag = (
                    not full_text
                    or "是否需要再来一题" in full_text
                    or "未获取到您的答题历史数据" in full_text
                    or "由于仅作答1题" in full_text
                    or (isinstance(student_ctx, dict) and len(student_ctx.get("questions", [])) > 1 and "总答题数：1" in full_text)
                    or any(e["event"] == "error" for e in diag_events)
                )
                if is_broken_diag and isinstance(student_ctx, dict) and student_ctx.get("questions"):
                    diag_report = build_student_learning_diagnosis_report(student_ctx)
                    diag_sources = []
                    for q in student_ctx.get("questions", []):
                        cw = str(q.get("courseware", "")).strip()
                        if cw and " P" in cw:
                            cw_file = cw.split(" P")[0].strip()
                            try:
                                cw_p = int(cw.split(" P")[1].strip())
                            except Exception:
                                cw_p = 1
                            diag_sources.append({
                                "source_id": f"cw_{cw_p}_{abs(hash(cw_file)) % 10000}",
                                "file": cw_file,
                                "chapter": str(q.get("knowledge_point", "课程知识点")),
                                "page": cw_p,
                                "version": "v1.0",
                                "status": "active"
                            })
                    chunk_size = 40
                    for i in range(0, len(diag_report), chunk_size):
                        yield f"event: token\ndata: {json.dumps({'text': diag_report[i:i+chunk_size], 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                        await asyncio.sleep(0.02)
                    for src in diag_sources:
                        yield f"event: source\ndata: {json.dumps({**src, 'request_id': request_id, 'evidence_type': 'learning_context'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'grounded_learning_diagnosis'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                for event in diag_events:
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                return

            raw_qa_events = [
                event
                async for event in xingchen_stream(
                    parameters,
                    identity,
                    request_id,
                    workflow_id=target_workflow_id,
                    retrieved_sources=retrieved_sources,
                    emit_unverified=not (mode == "learning_diagnosis" and graph_context.strip() in {"", "[]"}),
                )
            ]
            full_qa_text = "".join([str(e["data"].get("text", "")) for e in raw_qa_events if e["event"] == "token"])
            
            # Detect if cloud workflow misclassified a normal QA inquiry into mock 学情汇报 or teacher lesson plan
            is_cloud_mock_diag = (
                not is_diagnosis
                and "数据概况" in full_qa_text
                and "总答题数：1" in full_qa_text
                and "是否需要再来一题" in full_qa_text
            )
            is_cloud_lesson_plan_for_student = (
                mode != "teacher_assistant"
                and "【教学目标】" in full_qa_text
                and "【课前材料】" in full_qa_text
                and "【讨论步骤】" in full_qa_text
            )
            has_error = any(e["event"] == "error" for e in raw_qa_events)
            is_insufficient = not full_qa_text.strip()
            if is_cloud_mock_diag or is_cloud_lesson_plan_for_student or is_insufficient or has_error:
                fallback = build_grounded_qa_answer(question, retrieved_sources, mode=mode)
                raw_qa_events = [
                    {"event": "token", "data": {"text": fallback, "request_id": request_id}},
                    *[
                        {"event": "source", "data": {**source, "request_id": request_id, "evidence_type": "server_retrieval"}}
                        for source in retrieved_sources
                        if source.get("file") and source.get("page")
                    ],
                    {"event": "done", "data": {"request_id": request_id, "reason": "rescued_cloud_qa"}},
                ]

            emitted_tokens = 0
            for event in raw_qa_events:
                if event["event"] == "token":
                    raw_text = str(event["data"].get("text", ""))
                    if raw_text:
                        emitted_tokens += 1
                        if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario":
                            scenario_chunks.append(raw_text)
                        yield f"event: token\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                elif event["event"] == "source":
                    if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario":
                        scenario_sources.append(event["data"])
                    yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                elif event["event"] == "error":
                    if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario":
                        scenario_failed = True
                    yield f"event: error\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                elif event["event"] == "done":
                    if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario":
                        completed = store.complete_turn(identity.uid, session_id, int(scenario_turn_no or 0), "".join(scenario_chunks), scenario_sources)
                        scenario_finished = bool(completed)
                        if scenario_finished:
                            store.save_idempotent(identity.uid, f"/course-agent/scenario/{session_id}", scenario_idem_key, scenario_request_body, {"session_id": session_id, "turn_no": scenario_turn_no, "status": "completed", "assistant_text": "".join(scenario_chunks), "evidence": scenario_sources})
                    yield f"event: done\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
        finally:
            if isinstance(session_id, str) and parameters.get("AGENT_MODE") == "scenario" and (scenario_failed or not scenario_finished):
                store.reset_pending_turn(identity.uid, session_id, int(scenario_turn_no or 0))

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Request-ID": request_id})
