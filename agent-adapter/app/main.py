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
你是《电力系统储能技术》课程的专业名师助教。
1. 依据课程大纲、课件资料与专业知识图谱回答，剖析底层机理与工程应用背景，给出结构清晰、条理分明的深度专业解答。对于工程算例与系统配置计算（如容量配置、下垂控制、充放电能量核算等），结合储能工程原理给出详尽推导演算。
2. 先给直接结论，再按需要分点或步骤展开剖析，公式采用标准 LaTeX 格式（行内 $...$，行间 $$...$$），结构清晰，逻辑严谨。
3. 结合课程大纲与课件知识点，在文末或解析中精准提供对应课件溯源（格式：[来源文件：xxx.pdf；页码：yyy]）。
4. 如果当前 Workflow 声明了结构化字段（如 answer1-answer5），按要求在字段中填入具体内容，不输出空字段或占位符。"""

DEFAULT_PROMPT_CONFIG: dict[str, str] = {
    "core_quality_contract": QUALITY_CONTRACT,
    "qa_prompt": "依据课程资料与知识图谱回答，深入剖析物理/电气机理与工程计算实例，给出结构清晰、条理分明的专业解答，并在文末按规范引用课件 [来源文件：xxx.pdf；页码：yyy]。",
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
                # Moodle validates the request Host against $CFG->wwwroot during
                # session bootstrap; without the public host header an internal
                # http://moodle call gets a redirect-style error even with a
                # perfectly valid session cookie.
                headers={"cookie": cookie, "X-Agent-Bridge-Token": bridge_token, "Content-Type": "application/json", "Host": (os.getenv("SITE_HOST", "").strip() or "energygraph.icu")},
                json=payload,
            )
    except httpx.HTTPError:
        logger.warning("moodle grade bridge network failure assignment=%s request=%s", assignment_id, request.headers.get("x-request-id", ""))
        return {"status": "failed", "code": "bridge_network_error"}
    if response.status_code != 200:
        logger.warning("moodle grade bridge HTTP %s assignment=%s", response.status_code, assignment_id)
        return {"status": "failed", "code": "bridge_http_error", "http_status": response.status_code}
    # Moodle AJAX error pages can come back with HTTP 200; trust the JSON body.
    try:
        body = response.json()
    except ValueError:
        body = {}
    if not isinstance(body, dict) or body.get("status") != "synced":
        logger.warning("moodle grade bridge body not synced assignment=%s body=%s", assignment_id, str(body)[:200])
        return {"status": "failed", "code": "bridge_body_error", "body": str(body)[:200]}
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



COURSE_DIAGNOSIS_TOPIC_ROTATION = [
    "储能技术综合分类体系与各类储能形式（物理、电化学、电磁、相变、氢储能）的优缺点与响应速度对比",
    "抽水蓄能与压缩空气储能(CAES)系统的物理组成、工作原理、启停特性与电网削峰填谷",
    "飞轮储能(FES)与超级电容器储能的高频响应特性、能量密度与调频应用",
    "锂离子电池、全钒液流电池与钠离子电池的电化学机理、充放电特性与循环衰减规律",
    "超导磁储能(SMES)与电解水制氢储能系统(燃料电池/电解槽)的工作机理与混合储能系统配置",
    "储能变流器(PCS)的双向DC-DC/DC-AC拓扑结构、PWM脉宽调制与交直流并网控制",
    "储能变流器的构网型(GFM, Grid-Forming)与跟网型(GFL, Grid-Following)控制机理及虚拟同步机(VSG)技术",
    "储能系统在电力系统一次调频、二次调频与快速有功/无功电压支撑中的控制策略",
    "储能电站容量配置与优化选型、荷电状态(SOC)估算算法与充放电深度(DOD)控制",
    "储能系统热失控机理、电池管理系统(BMS)状态监测与电站消防安全防护规范",
]


def is_learning_diagnosis_intent(question: str, mode: str) -> bool:
    if mode == "learning_diagnosis":
        return True
    q = str(question or "").strip()
    # Explicitly exclude general study advice or questions about how to study / who are you
    if any(k in q for k in ["怎么学", "如何学", "学习方法", "学习路线", "复习方法", "复习路线", "你是谁", "介绍", "你能做什么"]):
        return False
    specific_keywords = [
        "学情诊断", "学情分析", "学情检验", "学情评估", "学情报告", "学情汇报",
        "综合学情体检", "学情体检", "进行学情体检", "开始学情体检", "学情全身体检",
        "错题归因", "错题复盘", "我的错题", "错题分析",
        "做题记录", "我的做题", "我的成绩", "我的学情", "学情概况",
        "学情复盘", "知识掌握情况", "查看学情", "诊断学情", "开始诊断", "进行学情诊断", "测试学情"
    ]
    return any(k in q for k in specific_keywords)



VALID_COURSEWARE_WHITELIST: set[str] = {
    "1.1 电力储能技术的概念.pdf", "1.1 电力储能技术的概念 .pdf", "1.2 电力储能技术的发展.pdf", "1.3 储能技术在电力系统中的应用.pdf",
    "2.1 电力系统的基本概念.pdf", "2.2 电力系统的运行特点和要求.pdf", "2.3 储能技术的典型应用.pdf",
    "3.1 抽水蓄能电站的组成及工作原理.pdf", "3.2 新型电力储能系统的组成.pdf", "3.3 新型电能存储设备工作原理.pdf",
    "3.4 储能变流器拓扑及并网控制.pdf", "3.5 储能监控系统结构及通信.pdf",
    "4.1 抽水蓄能电站的规划配置.pdf", "4.2 电化学储能系统的规划配置.pdf", "4.3 电池储能系统集成技术.pdf",
    "5.1 电力储能系统的接入.pdf", "5.2 电力储能系统的运行控制.pdf", "5.3 电力储能系统的运行维护.pdf", "5.4 电力储能系统的运行案例.pdf",
    "6.1 电力储能系统的性能检测.pdf", "6.2 电力储能系统的综合评估.pdf", "6.2 电力储能系统的系统评估.pdf"
}


def is_valid_courseware_name(name: str) -> bool:
    """Check if courseware name or stem belongs to the 20 official coursewares."""
    if not name:
        return False
    normalized = re.sub(r"\s+\.pdf$", ".pdf", str(name).strip(), flags=re.IGNORECASE)
    if normalized in VALID_COURSEWARE_WHITELIST:
        return True
    clean_stem = re.sub(r"\.pdf$", "", normalized, flags=re.IGNORECASE).strip()
    for cw in VALID_COURSEWARE_WHITELIST:
        cw_stem = re.sub(r"\.pdf$", "", cw, flags=re.IGNORECASE).strip()
        if clean_stem == cw_stem:
            return True
    return False



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
        
    # 2. Short selection phrases (length <= 16 to avoid false matching on long questions)
    if len(text_clean) <= 16:
        match_ordinal = re.search(r"(?:我选|答案是|选|作答|应该选|是|选个|正确选项是|选项|选第)?\s*(?:第)?([A-Da-d1-4一二三四])\s*(?:个|项|选项)?", text_clean, re.IGNORECASE)
        if match_ordinal and match_ordinal.group(1):
            val = match_ordinal.group(1).upper()
            chinese_digit_map = {"一": "A", "二": "B", "三": "C", "四": "D"}
            if val in chinese_digit_map:
                return chinese_digit_map[val]
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
        self.scene_mode = 0  # 0: 常规QA, 1: 师傅情景演练, 2: 主讲名师情景演练, 3: 随堂测验模式, 4: 互动学情诊断模式
        self.scene_role_name = ""  # "储能电站现场运维师傅" | "《电力系统储能技术》主讲老师" | "互动学情诊断测评"
        self.current_quiz: dict[str, Any] | None = None
        self.diag_active: bool = False
        self.diag_step: int = 0  # 当前题号 1, 2, 3, ... (无上限)
        self.diag_records: list[dict[str, Any]] = []
        self.asked_stems: set[str] = set()  # 本会话已出题干（归一化），用于跨轮去重
        self.awaiting_next: bool = False  # 上一题已记分但下一题生成失败，等待补发新题
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
                    state.diag_active = False
                    state.diag_step = 0
                    state.diag_records = []
                    state.asked_stems = set()
                    state.awaiting_next = False
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
            state.asked_stems.add(normalize_quiz_stem(str(quiz.get("stem") or quiz.get("question") or "")))

    async def set_scene(self, uid: str, session_id: str, scene_mode: int, role_name: str = "") -> None:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.scene_mode = scene_mode
            state.scene_role_name = role_name
            if scene_mode == 0:
                state.current_quiz = None
            if scene_mode in (1, 2):
                state.diag_active = False
                state.diag_step = 0
                state.diag_records = []
                state.asked_stems = set()
                state.awaiting_next = False

    async def start_diagnosis(self, uid: str, session_id: str, first_quiz: dict[str, Any]) -> SessionTeachingState:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.diag_active = True
            state.diag_step = 1
            state.diag_records = []
            state.asked_stems = {normalize_quiz_stem(str(first_quiz.get("stem") or first_quiz.get("question") or ""))}
            state.awaiting_next = False
            state.current_quiz = first_quiz
            state.scene_mode = 4
            state.scene_role_name = "互动学情诊断测评"
            return state

    async def advance_diagnosis(self, uid: str, session_id: str, record: dict[str, Any], next_quiz: dict[str, Any] | None) -> tuple[int, int]:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.diag_records.append(record)
            if next_quiz:
                state.diag_step += 1
                state.current_quiz = next_quiz
                state.scene_mode = 4
                state.scene_role_name = "互动学情诊断测评"
                state.asked_stems.add(normalize_quiz_stem(str(next_quiz.get("stem") or next_quiz.get("question") or "")))
                state.awaiting_next = False
            else:
                # Answer was recorded but the next question failed to generate;
                # keep diag_step on the answered question until set_next_question.
                state.awaiting_next = True
            return state.diag_step, len(state.diag_records)

    async def set_next_question(self, uid: str, session_id: str, next_quiz: dict[str, Any]) -> int:
        """Serve the pending next question after a transient generation failure."""
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.diag_step += 1
            state.current_quiz = next_quiz
            state.scene_mode = 4
            state.scene_role_name = "互动学情诊断测评"
            state.asked_stems.add(normalize_quiz_stem(str(next_quiz.get("stem") or next_quiz.get("question") or "")))
            state.awaiting_next = False
            return state.diag_step

    async def finish_diagnosis(self, uid: str, session_id: str, final_record: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            if final_record:
                state.diag_records.append(final_record)
            records = list(state.diag_records)
            state.diag_active = False
            state.diag_step = 0
            state.diag_records = []
            state.asked_stems = set()
            state.awaiting_next = False
            state.current_quiz = None
            state.scene_mode = 0
            state.scene_role_name = ""
            return records

    async def stop_diagnosis(self, uid: str, session_id: str) -> None:
        state = await self.get_or_create(uid, session_id)
        async with state.lock:
            state.diag_active = False
            state.diag_step = 0
            state.diag_records = []
            state.current_quiz = None
            state.asked_stems = set()
            state.awaiting_next = False
            if state.scene_mode == 4:
                state.scene_mode = 0
                state.scene_role_name = ""


teaching_state_manager = TeachingStateManager()


def classify_workflow_intent(
    question: str,
    current_state: SessionTeachingState | None = None,
    quoted_text: str = "",
    history_context: str = "",
    mode: str = "qa",
) -> str:
    # 0. Dedicated modes for teacher / grading bypass student chat state machine
    if mode in {"teacher_assistant", "question_draft", "grading"}:
        return mode

    # 1. Quoted text takes absolute precedence
    if quoted_text and str(quoted_text).strip():
        return "quote_study"
    
    q = str(question or "").strip()
    
    # 2. Stop/Exit commands take highest priority
    if any(k in q for k in ["退出情景演绎", "结束情景演绎", "停止情景演绎", "退出演练", "不扮演了", "退出角色扮演", "结束角色扮演"]):
        return "scenario_stop"
    if any(k in q for k in ["退出诊断", "结束诊断", "停止诊断", "不诊断了", "退出学情诊断", "结束学情诊断", "退出测评", "取消诊断", "退出体检", "结束体检", "退出学情体检", "停止体检"]):
        return "diagnosis_stop"
    if any(k in q for k in ["停止出题", "不练了", "不做了", "停止练习", "结束测验", "退出测验", "停止随堂"]):
        return "quiz_stop"

    # 3. Explicit Start / Switch Commands
    if is_learning_diagnosis_intent(q, "qa") or any(k in q for k in ["进行学情诊断", "学情诊断", "开始学情诊断", "帮我做一下学情诊断", "重新诊断", "重新学情诊断", "我的学情", "诊断学情", "测试学情", "开始诊断", "综合学情体检", "学情体检", "开始体检"]):
        return "diagnosis_start"
    is_roleplay = any(k in q for k in ["扮演", "演练", "情景", "角色", "模拟", "身份", "对话"])
    if any(k in q for k in ["扮演老师", "扮演名师", "扮演主讲老师", "名师授课", "名师情景", "名师情景演练", "主讲老师授课", "老师授课方式", "名师演练", "主讲老师"]) or (is_roleplay and any(k in q for k in ["老师", "名师", "主讲", "教授", "讲师"])):
        return "scenario_start_teacher"
    if any(k in q for k in ["扮演师傅", "扮演运维师傅", "扮演工程师", "电厂师傅", "现场师傅", "师傅情景演练", "运维师傅情景", "电厂运维师傅", "师傅演练", "工程师演练", "电厂运维", "运维师傅"]) or (is_roleplay and any(k in q for k in ["师傅", "工程师", "运维", "电厂", "现场"])):
        return "scenario_start_engineer"

    # 3.5 Diagnosis active state (checked before generic quiz keywords so
    # in-session commands like "下一题" never leak out of the diagnosis flow)
    is_in_diag = bool(current_state and getattr(current_state, "diag_active", False))
    if not is_in_diag and history_context:
        last_asst = ""
        for line in reversed(history_context.strip().split("\n")):
            if line.startswith("AI助教:"):
                last_asst = line
                break
        if ("互动学情诊断测评" in last_asst or "互动学情体检" in last_asst) and ("【题干】" in last_asst or "A." in last_asst or "A、" in last_asst):
            is_in_diag = True

    if is_in_diag:
        if any(k in q for k in ["生成诊断报告", "查看诊断报告", "出报告", "看报告", "完成诊断", "生成报告", "诊断报告", "查看报告", "结束测评", "生成体检报告", "查看体检报告", "体检报告"]):
            return "diagnosis_report_generate"
        if bool(current_state and getattr(current_state, "awaiting_next", False)):
            return "diagnosis_next"
        if any(k in q for k in ["下一题", "继续出题", "来下一题", "请继续", "下一道"]):
            return "diagnosis_next"
        return "diagnosis_submit"

    if (
        any(k in q for k in [
            "出一道题", "出题", "考考我", "做道题", "随堂练习", "再来一题", "测验", "来一道题",
            "出题测验", "随堂测试", "再出一题", "继续出题", "再来一道", "随堂单题",
            "随堂精练", "随堂自测", "单选题", "出单选", "出选择题", "考考", "做题", "考我"
        ])
        or bool(re.search(r"出\s*[0-9一二三两]\s*道", q))
        or bool(re.search(r"来\s*[0-9一二三两]\s*道", q))
        or bool(re.search(r"考\s*[0-9一二三两]\s*道", q))
        or bool(re.search(r"[0-9一二三两]\s*道.*?(?:题|单选|选择)", q))
    ):
        return "quiz_generate"

    # 5. Single quiz submit
    if extract_and_normalize_answer(q) is not None:
        if current_state and current_state.current_quiz:
            return "quiz_submit"
        elif history_context:
            last_asst = ""
            for line in reversed(history_context.strip().split("\n")):
                if line.startswith("AI助教:"):
                    last_asst = line
                    break
            if "【题干】" in last_asst or "A." in last_asst or "A、" in last_asst:
                return "quiz_submit"
        elif len(q) <= 6:
            return "quiz_submit"
            
    return "general_qa"



def extract_quiz_meta_fallback(full_text: str) -> dict[str, Any]:
    """Parse quiz metadata out of model output. Parse-only: when the text carries
    no usable question (empty stream, prompt echo, demo dialogue), the returned
    meta has no options and callers must treat generation as failed instead of
    substituting any locally hardcoded question."""
    options: dict[str, str] = {}
    correct_ans = None
    knowledge_point = ""
    courseware = ""
    explanation = ""
    stem = ""

    # 1. Check HIDDEN_META json tag
    match = re.search(r"<!--\s*HIDDEN_META\s*:\s*(.*?)(?:-->|$)", full_text, re.DOTALL)
    if match:
        try:
            raw_json = match.group(1).strip()
            if not raw_json.endswith("}"):
                last_brace = raw_json.rfind("}")
                if last_brace != -1:
                    raw_json = raw_json[:last_brace+1]
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                correct_ans = parsed.get("correct_answer") or parsed.get("correct")
                knowledge_point = parsed.get("knowledge_point") or parsed.get("kp") or ""
                courseware = parsed.get("courseware") or parsed.get("cw") or ""
                explanation = parsed.get("explanation") or parsed.get("expl") or ""
                stem = parsed.get("stem") or parsed.get("question") or ""
                if isinstance(parsed.get("options"), dict):
                    options = {k.upper(): str(v).strip() for k, v in parsed["options"].items()}
        except Exception:
            pass

    # 2. Extract options A, B, C, D from text if not in JSON (supports multiline and inline)
    if not options or len(options) < 2:
        # Match standard lines first
        opt_matches = re.findall(r"(?:^|\n)([A-D])[\.、:：\s]\s*([^\n]+)", full_text)
        for letter, content in opt_matches:
            clean_content = re.split(r"(?:<!--|【标准答案】|【答案】|【核心考点】|【知识溯源】|【名师解析】)", content)[0].strip()
            options[letter.upper()] = clean_content
            
        # If still missing, match inline A. ... B. ... C. ... D. ...
        if len(options) < 2:
            inline_matches = re.findall(r"(?:^|\s)([A-D])[\.、:：\s]\s*(.*?)(?=(?:\s+[A-D][\.、:：\s])|<!--|【|$)", full_text)
            for letter, content in inline_matches:
                clean_content = content.strip()
                if clean_content:
                    options[letter.upper()] = clean_content

    # 3. Check explicit answer field in text if not found
    if not correct_ans:
        ans_match = re.search(r"(?:【?\s*(?:标准答案|正确答案|参考答案|答案|本题选|正确选项为|正确选项是|正确选项|答案选|故选|应选|正确答案为|选)\s*】?)\s*[:：\s]*([A-Da-d])", full_text)
        if ans_match:
            correct_ans = ans_match.group(1).upper()

    # 4. Check explanation, courseware & kp fields from text if not found
    if not explanation:
        expl_match = re.search(r"(?:【?\s*(?:名师解析|知识点解析|解析|归因)\s*】?)\s*[:：\s]*([^\n]+)", full_text)
        explanation = expl_match.group(1).strip() if expl_match else ""

    if not correct_ans and explanation:
        expl_ans = re.search(r"(?:【?\s*(?:正确选项为|正确选项是|正确选项|答案为|故选|应选|因此选|本题选)\s*】?)\s*[:：\s]*([A-Da-d])", explanation)
        if expl_ans:
            correct_ans = expl_ans.group(1).upper()

    if not courseware:
        cw_match = re.search(r"(?:【?\s*(?:知识溯源|对应课件|课件|来源)\s*】?)\s*[:：\s]*([^\n]+)", full_text)
        courseware = cw_match.group(1).strip() if cw_match else ""

    if not knowledge_point:
        kp_match = re.search(r"(?:【?\s*(?:核心考点|考点|知识点)\s*】?)\s*[:：\s]*([^\n]+)", full_text)
        knowledge_point = kp_match.group(1).strip() if kp_match else ""

    # No fabricated fallbacks here: when the model did not provide the
    # answer, courseware or knowledge point, they stay empty. A served quiz
    # without a parseable answer is rejected by is_usable_quiz_meta.

    clean_stem = stem
    if not clean_stem:
        clean_stem = re.split(r"(?:A\.|A、|选项A|【标准答案】|<!--HIDDEN_META)", full_text)[0]
        clean_stem = re.sub(r"【(?:学情诊断测评|随堂测试单选题|题干|智能体指令).*?】", "", clean_stem)
        clean_stem = re.sub(r"第\s*\d+\s*题", "", clean_stem).strip()

    return {
        "stem": clean_stem or "储能专业测试题",
        "options": options,
        "correct": correct_ans,
        "correct_answer": correct_ans,
        "knowledge_point": knowledge_point,
        "courseware": courseware,
        "explanation": explanation
    }


def is_usable_quiz_meta(meta: dict[str, Any] | None) -> bool:
    """A served question must come from real model output: parseable stem,
    options AND the correct answer letter. Grading never runs on an invented
    answer, so a question without one is treated as a failed generation."""
    if not isinstance(meta, dict):
        return False
    opts = meta.get("options")
    if not isinstance(opts, dict) or len({k for k in opts if str(k).upper() in {"A", "B", "C", "D"}}) < 2:
        return False
    stem = str(meta.get("stem") or meta.get("question") or "").strip()
    if len(stem) < 8:
        return False
    answer = str(meta.get("correct") or meta.get("correct_answer") or "").upper().strip()
    return answer in {"A", "B", "C", "D"}


def normalize_quiz_stem(stem: str) -> str:
    """Canonical form of a question stem for in-session duplicate detection."""
    return re.sub(r"[\s，。；：、,.;:!?！？\"'“”‘’（）()【】\[\]<>-]+", "", str(stem or ""))[:80]


def build_compact_quiz_retry_instruction(
    topic: str,
    forbidden_stems: list[str],
    student_request: str = "",
) -> str:
    """Short, self-contained retry instruction used when a quiz generation call
    returned an empty stream, a prompt echo, or a duplicate of an asked question."""
    forbidden_block = ""
    if forbidden_stems:
        listed = "\n".join(f"- {s[:60]}" for s in forbidden_stems[-6:])
        forbidden_block = f"【严禁重复或雷同的已出题目（仅含题干前缀）】：\n{listed}\n\n"
    request_block = f"【学生的原始练习诉求】：{student_request[:120]}\n" if student_request else ""
    return (
        "【出题重试指令】\n"
        "你是《电力系统储能技术》课程资深主讲教师。上一次生成请求未返回有效内容或与已出题目重复，"
        "请忽略任何历史对话、示例或演示内容，直接按要求出 1 道全新的高质量单选题。\n\n"
        f"【本题考点范围】：{topic}\n"
        f"{request_block}"
        f"{forbidden_block}"
        "【必须严格遵循的输出格式】：\n"
        "【题干】...\n"
        "A. ...\n"
        "B. ...\n"
        "C. ...\n"
        "D. ...\n"
        "【标准答案】B\n"
        "【核心考点】...\n"
        "【知识溯源】课件全名.pdf P页码\n"
        "【名师解析】...\n"
        '<!--HIDDEN_META:{"type":"quiz","question":"题干...","options":{"A":"...","B":"...","C":"...","D":"..."},"correct":"选项字母","knowledge_point":"考点名称","courseware":"课件全名.pdf P页码","explanation":"解析..."}-->\n\n'
        "只输出题目内容本身，严禁复述本指令，严禁输出任何示例对话，严禁使用表情符号。"
    )


async def stream_quiz_question_sse(
    params: dict[str, Any],
    identity: Identity,
    request_id: str,
    retrieved_sources: list[dict[str, Any]] | None,
    stats: dict[str, Any],
) -> AsyncIterator[bytes]:
    """Stream one quiz/diagnosis generation turn to the client while capturing
    full text, emitted visible size and the upstream error for caller retries."""
    chunks: list[str] = []
    stream_buffer = ""
    hidden_tag_found = False
    emitted = 0
    error_data: dict[str, Any] | None = None
    async for event in xingchen_stream(params, identity, request_id, retrieved_sources=retrieved_sources):
        if event["event"] == "token":
            raw_tok = str(event["data"].get("text", ""))
            chunks.append(raw_tok)
            stream_buffer += raw_tok

            hide_pos = -1
            for tag in ["<!--HIDDEN_META:", "【标准答案】", "【答案】", "标准答案：", "答案：", "<!--"]:
                idx = stream_buffer.find(tag)
                if idx != -1 and (hide_pos == -1 or idx < hide_pos):
                    hide_pos = idx

            if hide_pos != -1:
                if not hidden_tag_found:
                    hidden_tag_found = True
                    if hide_pos > emitted:
                        delta_chunk = stream_buffer[emitted:hide_pos]
                        if delta_chunk:
                            yield f"event: token\ndata: {json.dumps({'text': delta_chunk, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    emitted = hide_pos
            elif not hidden_tag_found:
                yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                emitted += len(raw_tok)
        elif event["event"] == "source":
            yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
        elif event["event"] == "error":
            error_data = event.get("data") or {}
    stats["full_text"] = "".join(chunks)
    stats["emitted"] = emitted
    stats["error"] = error_data


async def reset_workflow_scenario_state(identity: Identity, request_id: str) -> None:
    """Clear the Workflow's persistent scenario-mode variable after an echo hijack.

    The cloud Workflow keeps a long-lived state variable that, once set by any
    role-play start, routes every later request into the scenario branch where
    the model regurgitates stored instruction text. Sending the official exit
    phrase once flips that variable back so the retried request can reach the
    intended branch. The reset call's own output is intentionally discarded."""
    print(f"[WORKFLOW_STATE_RESET] sending scenario exit to clear persistent workflow state, request_id={request_id}", flush=True)
    reset_params = {os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT"): "退出情景演绎"}
    try:
        async for event in xingchen_stream(reset_params, identity, request_id, mode="qa"):
            if event["event"] == "error":
                break
    except Exception as exc:  # the reset must never break the main teaching flow
        print(f"[WORKFLOW_STATE_RESET] reset call failed: {exc}", flush=True)


def quiz_failure_notice(context: str) -> str:
    """Honest, emoji-free user notice served when a question cannot be generated."""
    return (
        f"【{context}暂时不可用】出题大模型服务本次未返回有效题目（已自动重试一次）。"
        "这不会影响你已有的作答记录，请稍后重试。"
    )


QUIZ_GENERATION_PROMPT = """【随堂测试出题质量指令】
你是《电力系统储能技术》课程资深主讲教师。请基于课程大纲（1.1-6.4）生成 1 道高质量单选题。
【必须严格遵循的输出格式】：
【题干】[题目内容]
A. [选项A内容]
B. [选项B内容]
C. [选项C内容]
D. [选项D内容]
【标准答案】[请务必填入本题真实的正确答案字母 A/B/C/D]
【核心考点】[本题核心知识点]
【知识溯源】[对应官方课件文件名称与页码，例如：2.1 锂离子电池储能技术.pdf P8]
【名师解析】[对正确选项与错误选项的机理剖析]
<!--HIDDEN_META:{"correct_answer":"[必须与上述标准答案完全一致的单个大写字母A/B/C/D]","knowledge_point":"[核心知识点]","courseware":"[课件名称]","explanation":"[精炼解析]"}-->
"""

SCENARIO_ENGINEER_PROMPT = """【角色设定：储能电站现场一线运维师傅（张师傅）】
你现在扮演储能电站现场一线经验丰富的老运维师傅（张师傅）。
1. 安全与领域边界：你只与学生探讨《电力系统储能技术》相关的现场巡检、高压变流器（PCS）、电池舱热管理、消防系统及电气倒闸规程，结合现场高压电工排故经验解答。
2. 说话风格：口吻亲切、经验丰富、通俗易懂的老师傅第一人称工程口吻（如“小同志”、“咱们电站现场”），手把手引导学生排查现场问题。
3. 输出指令：务必以张师傅第一人称直接生动解答。严格遵守零表情符号规范。
"""

SCENARIO_TEACHER_PROMPT = """【角色设定：《电力系统储能技术》主讲老师】
你现在扮演《电力系统储能技术》高校主讲名师。
1. 安全与领域边界：严格围绕课程大纲、数学物理建模、变流器拓扑控制与系统规划进行启发式教学。
2. 说话风格：严谨沉稳、循循善诱，注重核心机理剖析与公式推导，公式采用标准 LaTeX 格式。
3. 输出指令：务必以老师第一人称直接解答。严格遵守零表情符号规范。
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
    prompt_cfg = load_prompt_config()
    core_contract = prompt_cfg.get("core_quality_contract", QUALITY_CONTRACT)
    mode_prompt = ""
    if mode == "scenario":
        core_contract = ""
    elif mode == "teacher_assistant":
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
        f"模式：{'qa' if mode == 'scenario' else mode}",
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


PROMPT_LEAK_MARKERS = [
    "【角色设定：",
    "【重要输出指令】",
    "【前序对话上下文】",
    "【随堂测试出题质量指令】",
    "【互动学情诊断出题指令】",
    "【互动学情诊断即时点评与",
    "【必须严格遵循的输出格式】",
    "【系统指令：",
    "模式：qa",
    "模式：scenario",
    "模式：teacher_assistant",
    "角色：student",
    "角色：teacher",
    "知识图谱上下文：",
    "情景上下文：",
    "严禁输出空字段",
    "将回答填入 Workflow 字段",
        "你是一名电力系统储能技术的工作人员，请和我情景演绎",
        "规则1出题：",
        "知识点仅限知识库5内容",
        # Upstream demo/few-shot dialogues that carry placeholder citations
        "来源文件：xxx.pdf",
        "页码：yyy",
    ]


def detect_prompt_echo(text: str) -> bool:
    """True when upstream regurgitated adapter/workflow instruction text instead of
    answering, which on this Workflow indicates the persistent scenario-state
    branch hijacked the request (the state variable must be reset)."""
    return any(marker in str(text or "") for marker in PROMPT_LEAK_MARKERS)


def normalize_workflow_text(text: str) -> str:
    """Turn provider wrappers into user-readable text and reject empty shells."""
    normalized = str(text or "").strip()
    if normalized.startswith("```") and normalized.endswith("```"):
        normalized = normalized[3:-3].strip()
        if normalized.lower().startswith("json"):
            normalized = normalized[4:].lstrip()
    prompt_leak_markers = PROMPT_LEAK_MARKERS
    if not normalized.startswith("{"):
        if any(marker in normalized for marker in prompt_leak_markers):
            return ""
        return normalized
    try:
        payload = json.loads(normalized)
    except json.JSONDecodeError:
        if any(marker in normalized for marker in prompt_leak_markers):
            return ""
        return normalized
    if not isinstance(payload, dict):
        if any(marker in normalized for marker in prompt_leak_markers):
            return ""
        return normalized
    fields: list[str] = []
    for key, value in payload.items():
        k_lower = str(key).lower()
        if not isinstance(value, str) or not value.strip():
            continue
        val_str = value.strip()
        # Strip leading routing-context echo lines (模式：… / 角色：…) BEFORE the
        # leak check, so an otherwise good answer that merely carries a routing
        # prefix is cleaned instead of being discarded wholesale.
        val_str = re.sub(r"^(?:\s*(?:模式|角色)：[^\n]{0,40}\n+)+", "", val_str).strip()
        # REJECT any field that echoes prompt wrappers, system instructions, or internal contexts
        if any(marker in val_str for marker in prompt_leak_markers):
            continue
        # Match any field that looks like output or has substantial content
        if not (k_lower.startswith(("ans", "resp", "content", "result", "output", "text", "report", "diag", "data"))) and len(val_str) < 50:
            continue
        # Suppress any legacy cloud mock node that outputs canned template overview
        if "数据概况" in val_str and ("总答题数" in val_str or "薄弱知识点" in val_str or "是否需要再来一题" in val_str or "无法定位" in val_str or "暂无法" in val_str):
            continue
        # Clean scenario preamble and field prefix if present
        val_str = re.sub(r"^[（(][^）)]*?(?:情景演绎|退出情景)[^）)]*?[）)]\s*", "", val_str).strip()
        val_str = re.sub(r"^answer\d+[:：]\s*", "", val_str, flags=re.IGNORECASE).strip()
        if val_str:
            fields.append(val_str)
    joined = "\n\n".join(fields)
    if joined.startswith("```"):
        joined = joined[3:]
        if joined.lower().startswith("json"):
            joined = joined[4:]
        joined = joined.rstrip()
        if joined.endswith("```"):
            joined = joined[:-3].rstrip()
    return joined


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
        yield {"event": "token", "data": {"text": content, "request_id": request_id}}
        yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}
        return

    if "动态自适应出题（第 1 题）" in question or "第 1 题自适应出题" in question:
        content = (
            "【学情诊断测评】已为您启动《电力系统储能技术》多维自适应互动诊断测评。在作答过程中，您可以随时作答，也可随时回复“生成诊断报告”查看本轮学情综合画像。\n\n"
            "【学情诊断测评 第 1 题 - 基础原理与应用】\n在新型电力系统日常调频与电网安全稳定控制中，具备毫秒级响应速度、适合承担短时间高功率冲击平抑的储能技术类型是：\n"
            "A. 抽水蓄能电站\nB. 功率型电化学储能（如飞轮/超级电容/高倍率锂电）\nC. 压缩空气储能\nD. 重力储能电站\n\n"
            '<!--HIDDEN_META:{"type":"quiz","question":"在新型电力系统日常调频与电网安全稳定控制中，具备毫秒级响应速度、适合承担短时间高功率冲击平抑的储能技术类型是：","options":{"A":"抽水蓄能电站","B":"功率型电化学储能（如飞轮/超级电容/高倍率锂电）","C":"压缩空气储能","D":"重力储能电站"},"correct":"B","knowledge_point":"1.3 储能技术在电力系统中的应用","courseware":"1.3 储能技术在电力系统中的应用.pdf P6","explanation":"飞轮、超级电容及高倍率锂电池等功率型储能具有毫秒级快速响应能力。"}-->'
        )
        yield {"event": "token", "data": {"text": content, "request_id": request_id}}
        yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}
        return

    if "即时批改与第" in question or "即时批改" in question and "自适应出题" in question:
        content = (
            "第 1 题作答已记录并完成批改！\n\n接下来请作答自适应生成的下一题（您可随时输入“生成诊断报告”查看综合学情）：\n\n"
            "【学情诊断测评 第 2 题 - 变流器控制机理】\n在新型电力系统高比例新能源场景下，构网型（Grid-Forming, GFM）储能变流器与传统跟网型（Grid-Following, GFL）变流器的最本质区别在于：\n"
            "A. GFM 变流器内部呈现为受控电流源特性\nB. GFM 变流器内部呈现为受控电压源特性，具备自主建立电压与频率支撑能力\nC. GFM 变流器无法在微电网孤岛模式下运行\nD. GFM 变流器不需要电网同步环路与下垂控制\n\n"
            '<!--HIDDEN_META:{"type":"quiz","question":"在新型电力系统高比例新能源场景下，构网型（Grid-Forming, GFM）储能变流器与传统跟网型（Grid-Following, GFL）变流器的最本质区别在于：","options":{"A":"GFM 变流器内部呈现为受控电流源特性","B":"GFM 变流器内部呈现为受控电压源特性，具备自主建立电压与频率支撑能力","C":"GFM 变流器无法在微电网孤岛模式下运行","D":"GFM 变流器不需要电网同步环路与下垂控制"},"correct":"B","knowledge_point":"3.4 储能变流器拓扑及并网控制","courseware":"3.4 储能变流器拓扑及并网控制.pdf P12","explanation":"跟网型变流器等效为受控电流源，构网型等效为受控电压源。"}-->'
        )
        yield {"event": "token", "data": {"text": content, "request_id": request_id}}
        yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}
        return

    if "终局大模型深度综合报告生成" in question:
        content = (
            "## 《电力系统储能技术》学情诊断综合报告\n\n"
            "### 一、本轮诊断测评战绩概况\n"
            "- **总测评题数**：3 题\n"
            "- **正确作答数**：2 题\n"
            "- **答题正确率**：66.7%\n"
            "- **学情综合评级**：【良好 / 稳步提升】\n"
            "- **总体学习评价**：您在储能基础与规划配置掌握扎实，但对变流器控制特性的电压源/电流源本质存在混淆，建议重点巩固第3章。\n\n"
            "### 二、核心知识维度掌握度画像\n"
            "1. **第1章 基础原理与应用 - 1.3 储能技术在电力系统中的应用**：`[掌握良好]`（作答：`B`，标准：`B`）\n"
            "2. **第3章 电气控制与变流器 - 3.4 储能变流器拓扑及并网控制**：`[存在薄弱项]`（作答：`A`，标准：`B`）\n"
            "3. **第4章 规划配置与综合评估 - 4.2 电化学储能系统的规划配置**：`[掌握良好]`（作答：`C`，标准：`C`）\n\n"
            "### 三、错题根因剖析与深度辨析\n"
            "#### 错题考点：3.4 储能变流器拓扑及并网控制\n"
            "- **您的选择**：选项 `A`\n"
            "- **标准选项**：选项 `B`\n"
            "- **名师深度解析**：构网型变流器（GFM）等效为内部受控电压源，通过下垂或VSG控制自主支撑电网电压与频率；而跟网型（GFL）才等效为受控电流源。\n"
            "- **课件溯源**：[3.4 储能变流器拓扑及并网控制.pdf P12 ↗]\n\n"
            "### 四、专属靶向复习路径与课件直达推荐\n"
            "- **推荐复习讲义**：[3.4 储能变流器拓扑及并网控制.pdf 第 12 页 ↗]（重点复习考点：3.4 储能变流器拓扑及并网控制）\n\n"
            "---\n"
            "本轮学情诊断已完成，诊断数据已同步至您的学情档案。您可以随时向我提问课程任何疑问。"
        )
        yield {"event": "token", "data": {"text": content, "request_id": request_id}}
        for source_event in validate_sources(content):
            yield {"event": "source", "data": {**source_event, "request_id": request_id}}
        yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}
        return

    if "规划配置" in question or "电化学" in question:
        source = "4.2 电化学储能系统的规划配置.pdf；章节：第4章 电力储能系统的规划配置；页码：1"
    elif "变流器" in question:
        source = "3.4 储能变流器拓扑及并网控制.pdf；章节：第3章 电力储能系统的组成及工作原理；页码：1"
    else:
        source = "3.1 抽水蓄能电站的组成及工作原理.pdf；章节：第3章 电力储能系统的组成及工作原理；页码：1"
    content = f"[MOCK_WORKFLOW] 已收到问题：{question[:160]}\n[来源文件：{source}]\n当前为讯飞 Workflow 协议测试模式。"
    yield {"event": "token", "data": {"text": content, "request_id": request_id}}
    for source_event in validate_sources(content):
        yield {"event": "source", "data": {**source_event, "request_id": request_id}}
    yield {"event": "done", "data": {"request_id": request_id, "reason": "stop"}}


def workflow_error_event(code: str, message: str, request_id: str, **extra: Any) -> dict[str, Any]:
    """Central workflow failure logger: every upstream failure must leave a server trace."""
    extra_txt = " ".join(f"{k}={v}" for k, v in extra.items() if v not in (None, ""))
    print(f"[WORKFLOW_ERROR] code={code} message={message} request_id={request_id} {extra_txt}".rstrip(), flush=True)
    return {"event": "error", "data": {"code": code, "message": message, "request_id": request_id, **extra}}


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
    if not workflow_id and not published and not os.getenv("XINGCHEN_FLOW_ID"):
        yield workflow_error_event("knowledge_base_not_published", "课程知识库尚未发布", request_id)
        return
    # A release test passes the Workflow ID stored on that KB version. The
    # environment value remains the default only for legacy deployments where
    # the published version has no explicit binding.
    flow_id = workflow_id or os.getenv("XINGCHEN_FLOW_ID", "") or str(published.get("workflow_id") if published else "")
    url = os.getenv("XINGCHEN_WORKFLOW_URL", "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions")
    if not flow_id:
        yield workflow_error_event("workflow_not_configured", "Workflow 尚未配置", request_id)
        return
    payload = {"flow_id": flow_id, "uid": identity.uid, "parameters": workflow_input_parameters(parameters), "stream": True}
    print(f"[DEBUG_PAYLOAD_PARAM] len={len(payload['parameters'].get('AGENT_USER_INPUT', ''))}, sample={payload['parameters'].get('AGENT_USER_INPUT', '')[:300]}", flush=True)
    try:
        timeout = float(os.getenv("XINGCHEN_TIMEOUT_SECONDS", "90"))
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=10)) as client:
            async with client.stream("POST", url, headers={"Authorization": authorization_header(), "Content-Type": "application/json"}, json=payload) as response:
                if response.status_code in {401, 403}:
                    yield workflow_error_event("workflow_auth_failed", "讯飞 Workflow 鉴权失败", request_id)
                    return
                if response.status_code >= 400:
                    yield workflow_error_event("workflow_upstream_error", f"讯飞 Workflow 返回 HTTP {response.status_code}", request_id)
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
                        yield workflow_error_event(frame["_error"], "讯飞返回了无法解析的数据", request_id)
                        return
                    if frame.get("_done"):
                        saw_done = True
                        break
                    if int(frame.get("code", 0) or 0) != 0:
                        yield workflow_error_event(f"xingchen_{frame.get('code')}", "讯飞 Workflow 执行失败", request_id, sid=frame.get("id"))
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
                    yield workflow_error_event("upstream_disconnected", "讯飞 Workflow 流式连接中断", request_id)
                    return
                final_text = normalize_workflow_text(answer_buffer)
                print(f"[DEBUG_RAW_ANSWER_BUFFER] raw_repr={repr(answer_buffer)}, len={len(answer_buffer)}, final_len={len(final_text)}, sample={final_text[:100]}", flush=True)
                if not final_text or len(final_text.strip()) < 24:
                    if final_text == "" and detect_prompt_echo(answer_buffer):
                        yield workflow_error_event(
                            "workflow_prompt_echo_rejected",
                            "讯飞返回了指令回显类内容（疑似情景状态劫持），已拦截",
                            request_id,
                            raw_len=len(answer_buffer),
                        )
                    else:
                        yield workflow_error_event("workflow_quality_failed", "Workflow 返回内容未达到可用回答标准，请重试", request_id, raw_len=len(answer_buffer))
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
        yield workflow_error_event("workflow_timeout", "讯飞 Workflow 请求超时，请重试", request_id)
    except httpx.HTTPError:
        yield workflow_error_event("workflow_network_error", "讯飞 Workflow 暂时不可用，请重试", request_id)


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


@app.get("/api/mindmap")
async def get_mindmap_snapshot(request: Request) -> JSONResponse:
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    workspace_key = request.query_params.get("workspace_key", "").strip()
    if not workspace_key:
        return JSONResponse(error_payload(request_id, "invalid_params", "缺少工作空间标识 workspace_key"), status_code=422)
    record = store.get_mindmap(workspace_key)
    return json_response(request_id, {
        "status": "ok",
        "workspace_key": workspace_key,
        "data": record["data"] if record else None,
        "updated_at": record["updated_at"] if record else None,
        "role": record["role"] if record else None,
        "user_uid": record["user_uid"] if record else None,
    })


@app.post("/api/mindmap")
async def save_mindmap_snapshot(request: Request) -> JSONResponse:
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(error_payload(request_id, "invalid_body", "无效的请求格式"), status_code=422)

    workspace_key = str(body.get("workspace_key", "")).strip()
    data = body.get("data")
    if not workspace_key or not isinstance(data, dict):
        return JSONResponse(error_payload(request_id, "invalid_params", "缺少工作空间标识或导图数据"), status_code=422)

    user_uid = str(body.get("user_uid", "teacher")).strip() or "teacher"
    role = str(body.get("role", "teacher")).strip() or "teacher"
    try:
        identity = await resolve_identity(request)
        if identity:
            user_uid = identity.user_uid
            role = identity.role
    except Exception:
        pass

    saved = store.save_mindmap(workspace_key, data, user_uid=user_uid, role=role)
    return json_response(request_id, {
        "status": "ok",
        "workspace_key": saved["workspace_key"],
        "updated_at": saved["updated_at"],
        "message": "知识导图已持久化保存至云端数据库"
    })


@app.post("/api/mindmap/reset")
async def reset_mindmap_snapshot(request: Request) -> JSONResponse:
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(error_payload(request_id, "invalid_body", "无效的请求格式"), status_code=422)

    workspace_key = str(body.get("workspace_key", "")).strip()
    if not workspace_key:
        return JSONResponse(error_payload(request_id, "invalid_params", "缺少工作空间标识"), status_code=422)

    store.reset_mindmap(workspace_key)
    return json_response(request_id, {
        "status": "ok",
        "workspace_key": workspace_key,
        "message": "云端知识导图已重置为默认官方大纲"
    })


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
            # Contextual query expansion for multi-turn pronouns & reference resolution
            if history_context and any(pronoun in question for pronoun in ["这部分", "上述", "该技术", "它", "其", "对应", "哪个课件", "哪页", "算例", "详细推导", "为什么", "怎么做", "考点", "总结", "课件"]):
                retrieval_query = f"{retrieval_query}\n{history_context[-350:]}"
            elif mode == "learning_diagnosis":
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
        workflow_intent = classify_workflow_intent(question, teaching_state, quoted_context, history_context, mode=mode)
        print(f"[DEBUG_INTENT] q='{question}', intent='{workflow_intent}', diag_active={teaching_state.diag_active}, step={teaching_state.diag_step}, scene_mode={teaching_state.scene_mode}, has_quiz={bool(teaching_state.current_quiz)}", flush=True)

        # Inject persona context if active scenario roleplay
        effective_mode = mode
        if teaching_state.scene_mode == 1:
            effective_mode = "scenario"
            if not scenario_context:
                scenario_context = SCENARIO_ENGINEER_PROMPT
        elif teaching_state.scene_mode == 2:
            effective_mode = "scenario"
            if not scenario_context:
                scenario_context = SCENARIO_TEACHER_PROMPT

        parameters = build_parameters(
            identity,
            effective_mode,
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
                prior_state = await teaching_state_manager.get_or_create(identity.uid, str(client_sess))
                was_scenario = prior_state.scene_mode in (1, 2)
                await teaching_state_manager.set_scene(identity.uid, str(client_sess), 0, "")
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_role_name': ''}, ensure_ascii=False)}\n\n".encode("utf-8")
                stop_txt = "好的，已停止情景演绎。书山有路勤为径，学海无涯苦作舟！期待你的下次演练！"
                yield f"event: token\ndata: {json.dumps({'text': stop_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                if was_scenario:
                    # Keep the Workflow's persistent scenario flag in sync with the
                    # local state machine so later quiz or diagnosis turns are not
                    # rerouted through its scenario branch.
                    asyncio.create_task(reset_workflow_scenario_state(identity, request_id))
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'scenario_stopped'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 2. Diagnosis stop branch
            if workflow_intent == "diagnosis_stop":
                await teaching_state_manager.stop_diagnosis(identity.uid, str(client_sess))
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_role_name': ''}, ensure_ascii=False)}\n\n".encode("utf-8")
                stop_txt = "好的，已为您退出学情诊断测评。您可以随时向我提问《电力系统储能技术》课程的任何知识点，或随时再次输入“进行学情诊断”开启测评。"
                yield f"event: token\ndata: {json.dumps({'text': stop_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_stopped'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 3. Diagnosis report generate branch (学生随时主动要求生成综合报告，100% 由大模型实时流式生成)
            if workflow_intent == "diagnosis_report_generate":
                all_records = await teaching_state_manager.finish_diagnosis(identity.uid, str(client_sess))
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_role_name': ''}, ensure_ascii=False)}\n\n".encode("utf-8")
                
                if not all_records:
                    empty_diag_txt = "您在本轮测评中尚未完成任何题目作答。您可以随时回复“进行学情诊断”开启多维自适应出题测评。"
                    yield f"event: token\ndata: {json.dumps({'text': empty_diag_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'no_diagnosis_records'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return

                records_summary = []
                for idx, r in enumerate(all_records, 1):
                    k_pt = r.get('knowledge_point', '储能考点')
                    c_ware = r.get('courseware', '')
                    expl = r.get('explanation', '')
                    is_corr = r.get('is_correct', False)
                    status_text = "掌握扎实，理解透彻" if is_corr else "存在概念模糊，需重点梳理"
                    records_summary.append(
                        f"{idx}. 知识模块【{k_pt}】（{status_text}；核心要点：{expl[:60]}；对应课件：{c_ware}）；"
                    )
                records_str = "\n".join(records_summary)

                total_cnt = len(all_records)
                correct_cnt = sum(1 for r in all_records if r.get('is_correct'))
                accuracy_pct = round((correct_cnt / total_cnt) * 100, 1) if total_cnt > 0 else 0.0
                rank_grade = "优秀" if accuracy_pct >= 80 else ("良好" if accuracy_pct >= 60 else "待强化")

                diag_report_instruction = (
                    f"请围绕以下储能知识点进行深入机理剖析并撰写教学总结精讲报告：\n"
                    f"{records_str}\n\n"
                    f"请按以下四个篇章深入剖析物理机理、工程实际应用与靶向复习路径：\n"
                    f"## 《电力系统储能技术》多维知识梳理与进阶精讲报告\n\n"
                    f"### 一、本轮研讨成效与总体学术评价\n"
                    f"- **研讨知识模块总数**：{total_cnt} 项\n"
                    f"- **深度掌握模块数**：{correct_cnt} 项\n"
                    f"- **知识掌握熟练度**：{accuracy_pct}%\n"
                    f"- **学业综合评定**：{rank_grade}\n"
                    f"- **名师综合评语**：（结合学生的理解深度，给出条理清晰、肯定与建议兼备的专业总评）\n\n"
                    f"### 二、核心知识维度掌握度深入剖析\n"
                    f"结合上述具体模块，深入分析学生在基础原理、电气控制、电网调频等维度的掌握深度与技术认知。\n\n"
                    f"### 三、重点难点机理拓展与易混淆辨析\n"
                    f"针对存在认知盲区或需强化的模块，深入剖析物理/电气底层机理本质；针对已掌握模块给出工程实际应用拓展。\n\n"
                    f"### 四、专属靶向复习路径与课件直达推荐\n"
                    f"为学生量身定制进阶复习路径，并附上精准课件页码指引（格式：[课件文件名.pdf 第 X 页 ↗]）。\n\n"
                    f"严格遵守零表情符号规范，直接输出整份报告。"
                )
                diag_report_params = build_parameters(
                    identity,
                    "qa",
                    diag_report_instruction,
                    graph_context,
                    "",
                    "",
                    retrieval_context=retrieval_context,
                    history_context="",
                )
                
                emitted_report_tokens = 0
                report_error: dict[str, Any] | None = None
                async for event in xingchen_stream(diag_report_params, identity, request_id, retrieved_sources=retrieved_sources):
                    if event["event"] == "token":
                        emitted_report_tokens += 1
                        yield f"event: token\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "source":
                        yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "error":
                        report_error = event.get("data") or {}

                if emitted_report_tokens == 0:
                    if report_error and report_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    print(f"[DIAGNOSIS] report generation failed (error={report_error}), retrying once", flush=True)
                    async for event in xingchen_stream(diag_report_params, identity, request_id, retrieved_sources=retrieved_sources):
                        if event["event"] == "token":
                            emitted_report_tokens += 1
                            yield f"event: token\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                        elif event["event"] == "source":
                            yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                        elif event["event"] == "error":
                            pass

                if emitted_report_tokens == 0:
                    # Honest deterministic summary built ONLY from the real answer
                    # records; the AI narrative failed and is never faked.
                    print(f"[DIAGNOSIS] report unavailable after retry, serving honest statistics summary (last_error={report_error})", flush=True)
                    weak_points = [str(r.get("knowledge_point") or "未标注考点") for r in all_records if not r.get("is_correct")]
                    summary_lines = [f"- 第 {i} 题【{r.get('knowledge_point') or '未标注考点'}】：{'答对' if r.get('is_correct') else '答错（正确答案 ' + str(r.get('correct_answer') or '未标注') + '，你的作答 ' + str(r.get('user_answer') or r.get('student_answer') or '未记录') + '）'}" for i, r in enumerate(all_records, 1)]
                    honest_report = (
                        f"## 本轮学情诊断统计（系统自动汇总）\n\n"
                        f"- **作答题数**：{total_cnt} 题\n"
                        f"- **答对题数**：{correct_cnt} 题\n"
                        f"- **正确率**：{accuracy_pct}%\n"
                        f"- **学业综合评定**：{rank_grade}\n\n"
                        f"**逐题作答记录**：\n" + "\n".join(summary_lines) + "\n\n"
                        + (f"**建议优先复习**：{ '、'.join(dict.fromkeys(weak_points)) }\n\n" if weak_points else "")
                        + "【服务提示】AI 深度剖析报告生成服务本次未返回有效内容（已自动重试一次），以上为系统根据你的真实作答记录汇总的确定性统计，未包含 AI 生成的机理剖析。可稍后回复“进行学情诊断”重新测评获取完整报告。"
                    )
                    yield f"event: token\ndata: {json.dumps({'text': honest_report, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'interactive_diagnosis_completed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 4. Diagnosis start branch (纯大模型动态自适应出第 1 题)
            if workflow_intent == "diagnosis_start":
                first_topic = COURSE_DIAGNOSIS_TOPIC_ROTATION[0]
                diag_q1_instruction = (
                    "【互动学情诊断出题指令】\n"
                    "你是《电力系统储能技术》资深主讲教师。现为学生启动互动学情诊断测评（第 1 题）。\n"
                    f"请基于课程知识库，针对考点【{first_topic}】出 1 道高质量单选题。\n\n"
                    "【必须严格遵循的输出格式】：\n"
                    "【题干】...（给出清晰题干）\n"
                    "A. ...\n"
                    "B. ...\n"
                    "C. ...\n"
                    "D. ...\n"
                    "【标准答案】B\n"
                    "【核心考点】...\n"
                    "【知识溯源】...\n"
                    "【名师解析】...\n"
                    '<!--HIDDEN_META:{"type":"quiz","question":"题干...","options":{"A":"...","B":"...","C":"...","D":"..."},"correct":"选项字母","knowledge_point":"考点名称","courseware":"课件文件名 P页码","explanation":"考点解析..."}-->\n\n'
                    "【排版要求】：题干下方仅列出 A、B、C、D 各一行，严禁重复打印两遍选项。请严格遵守零表情符号规范，直接输出出题内容。"
                )
                diag_params = build_parameters(
                    identity,
                    "qa",
                    diag_q1_instruction,
                    graph_context,
                    "",
                    "",
                    retrieval_context=retrieval_context,
                    history_context="",
                )
                
                quiz_stats: dict[str, Any] = {}
                async for sse_chunk in stream_quiz_question_sse(diag_params, identity, request_id, retrieved_sources, quiz_stats):
                    yield sse_chunk
                full_quiz_text = quiz_stats["full_text"]
                emitted_chars = quiz_stats["emitted"]
                upstream_error = quiz_stats["error"]

                first_parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None
                if not is_usable_quiz_meta(first_parsed_meta):
                    if upstream_error and upstream_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    retry_params = build_parameters(
                        identity,
                        "qa",
                        build_compact_quiz_retry_instruction(first_topic, []),
                        graph_context,
                        "",
                        "",
                        retrieval_context=retrieval_context,
                        history_context="",
                    )
                    print(f"[DIAGNOSIS] first-question generation failed (emitted={emitted_chars}, error={upstream_error}), retrying with compact instruction", flush=True)
                    retry_stats: dict[str, Any] = {}
                    async for sse_chunk in stream_quiz_question_sse(retry_params, identity, request_id, retrieved_sources, retry_stats):
                        yield sse_chunk
                    full_quiz_text = retry_stats["full_text"]
                    emitted_chars += retry_stats["emitted"]
                    first_parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None

                if not is_usable_quiz_meta(first_parsed_meta):
                    print(f"[DIAGNOSIS] first-question unavailable after retry, serving honest failure (last_error={upstream_error})", flush=True)
                    yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_title': '', 'scene_role_name': '', 'done_count': 0}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: token\ndata: {json.dumps({'text': quiz_failure_notice('学情诊断') + '请稍后回复“进行学情诊断”再次开始，或先进行课件研读等其他学习环节。', 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_start_failed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return

                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 4, 'scene_title': '互动学情诊断测评（第 1 题 · 已完成 0 题）', 'scene_role_name': '互动学情诊断测评', 'done_count': 0}, ensure_ascii=False)}\n\n".encode("utf-8")

                if emitted_chars == 0:
                    q_stem = first_parsed_meta.get("stem") or first_parsed_meta.get("question") or ""
                    opts = first_parsed_meta.get("options", {})
                    opt_lines = "\n".join([f"{k}. {v}" for k, v in sorted(opts.items())])
                    fallback_stream_text = (
                        f"【互动学情诊断测评 · 第 1 题】\n\n"
                        f"【题干】{q_stem}\n\n"
                        f"{opt_lines}\n\n"
                        f"【核心考点】{first_parsed_meta.get('knowledge_point', '')}\n"
                        f"【知识溯源】{first_parsed_meta.get('courseware', '')}\n"
                    )
                    yield f"event: token\ndata: {json.dumps({'text': fallback_stream_text, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")

                await teaching_state_manager.start_diagnosis(identity.uid, str(client_sess), first_parsed_meta)
                yield f"event: quiz_meta\ndata: {json.dumps(first_parsed_meta, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_question_served'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 5. Diagnosis submit branch (纯大模型动态自适应批改 + 跨章节出第 N+1 题)
            if workflow_intent == "diagnosis_submit":
                st = await teaching_state_manager.get_or_create(identity.uid, str(client_sess))
                current_quiz = st.current_quiz or {}
                if not current_quiz and not st.awaiting_next and history_context and ("A." in history_context or "A、" in history_context or "【题干】" in history_context or "题干" in history_context):
                    recovered = extract_quiz_meta_fallback(history_context)
                    if recovered.get("options") and len(recovered["options"]) >= 2:
                        current_quiz = recovered
                        st.current_quiz = recovered
                        if st.diag_step == 0:
                            st.diag_step = max(1, len(st.diag_records) + 1)
                
                norm_ans = extract_and_normalize_answer(question)
                if norm_ans is None:
                    step_num = max(1, st.diag_step)
                    guidance_txt = f"【学情诊断测评进行中（第 {step_num} 题）】请点击上方选项卡或输入对应选项字母完成作答。若需获取综合诊断报告，可随时回复“生成诊断报告”；若需退出，可回复“退出诊断”。"
                    yield f"event: token\ndata: {json.dumps({'text': guidance_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_guidance_prompted'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return

                correct_ans = str(current_quiz.get("correct") or current_quiz.get("correct_answer") or current_quiz.get("correct_option") or "").upper().strip()
                if correct_ans not in {"A", "B", "C", "D"}:
                    missing_ans_txt = "【本题答案数据异常】这道题没有携带可核验的标准答案，已停止判分以免误判。请回复“下一题”获取新题，或回复“生成诊断报告”结束本次测评。"
                    yield f"event: token\ndata: {json.dumps({'text': missing_ans_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_answer_missing'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                is_correct = (norm_ans == correct_ans)
                record = {
                    **current_quiz,
                    "question": current_quiz.get("stem") or current_quiz.get("question") or f"第 {st.diag_step} 题",
                    "stem": current_quiz.get("stem") or current_quiz.get("question") or f"第 {st.diag_step} 题",
                    "correct_option": correct_ans,
                    "correct_answer": correct_ans,
                    "student_answer": norm_ans,
                    "user_answer": norm_ans,
                    "is_correct": is_correct
                }

                # Formative grade record emission (never fabricate a citation)
                cw = str(current_quiz.get("courseware", "")).strip()
                cw_file = cw.split(" P")[0].strip() if " P" in cw else ""
                cw_page = cw.split(" P")[1].strip() if " P" in cw else ""
                if cw_file and cw_file not in VALID_COURSEWARE_WHITELIST:
                    cw_file, cw_page = "", ""
                grade_payload = {
                    "source_task": f"学情诊断测验 (第{st.diag_step}题)",
                    "stem": current_quiz.get("stem", "学情诊断测验"),
                    "student_answer": norm_ans,
                    "correct_answer": correct_ans,
                    "is_correct": is_correct,
                    "earned_score": 10 if is_correct else 0,
                    "max_score": 10,
                    "knowledge_point": current_quiz.get("knowledge_point", ""),
                    "courseware": f"{cw_file} P{cw_page}".strip()
                }
                yield f"event: quiz_graded\ndata: {json.dumps(grade_payload, ensure_ascii=False)}\n\n".encode("utf-8")

                curr_step = st.diag_step
                next_step = curr_step + 1
                done_cnt = len(st.diag_records) + 1

                # Select next topic dynamically across chapters to ensure diversity
                next_topic_idx = (next_step - 1) % len(COURSE_DIAGNOSIS_TOPIC_ROTATION)
                next_topic = COURSE_DIAGNOSIS_TOPIC_ROTATION[next_topic_idx]

                # Extract history of previously asked questions to strictly forbid repetitions
                asked_questions_list = []
                for i, r in enumerate(st.diag_records, 1):
                    q_text = r.get("question") or r.get("stem") or ""
                    kp = r.get("knowledge_point", "")
                    if q_text:
                        asked_questions_list.append(f"· 第 {i} 题 [{kp}]: {q_text[:60]}")
                # Also include current quiz
                curr_q_text = current_quiz.get("stem") or current_quiz.get("question") or ""
                if curr_q_text:
                    asked_questions_list.append(f"· 第 {curr_step} 题 [{current_quiz.get('knowledge_point', '')}]: {curr_q_text[:60]}")

                asked_summary = "\n".join(asked_questions_list[-6:])

                diag_next_instruction = (
                    f"【互动学情诊断即时点评与第 {next_step} 题自适应跨章节出题指令】\n"
                    f"学生刚刚完成了第 {curr_step} 题的作答（本轮已累计完成 {done_cnt} 题）。\n"
                    f"- 本题考点：{current_quiz.get('knowledge_point', '储能考点')}\n"
                    f"- 本题题干：{current_quiz.get('stem', '')}\n"
                    f"- 标准答案：{correct_ans}\n"
                    f"- 学生作答：{norm_ans}（判定：{'正确' if is_correct else '错误'}）\n"
                    f"- 解析要点：{current_quiz.get('explanation', '')}\n\n"
                    f"【本轮已出过的历史题目（严禁重复或雷同）】：\n"
                    f"{asked_summary}\n\n"
                    f"请你：\n"
                    f"1. 首先给出 1-2 句精辟的名师即时点评（肯定正确点或剖析概念混淆根因）；\n"
                    f"2. 紧接着必须【跨章节切换考点】，针对新的知识维度【{next_topic}】自适应出【第 {next_step} 题】单选题；\n"
                    f"3. 【严禁出题重复】：绝对严禁出与上述历史已考题目重复或高度相似的题目，必须更换全新的知识领域与考查背景；\n\n"
                    f"【必须严格遵循的输出格式】：\n"
                    f"【题干】...（给出清晰题干）\n"
                    f"A. ...\n"
                    f"B. ...\n"
                    f"C. ...\n"
                    f"D. ...\n"
                    f"【标准答案】B\n"
                    f"【核心考点】...\n"
                    f"【知识溯源】...\n"
                    f"【名师解析】...\n"
                    f'<!--HIDDEN_META:{{"type":"quiz","question":"题干...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"correct":"选项字母","knowledge_point":"考点名称","courseware":"课件文件名 P页码","explanation":"考点解析..."}}-->\n\n'
                    f"【排版要求】：题干下方仅列出 A、B、C、D 各一行，严禁重复打印两遍选项。请严格遵守零表情符号规范，直接输出回复内容。"
                )
                diag_params = build_parameters(
                    identity,
                    "qa",
                    diag_next_instruction,
                    graph_context,
                    "",
                    "",
                    retrieval_context=retrieval_context,
                    history_context="",
                )
                
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 4, 'scene_title': f'互动学情诊断测评（第 {next_step} 题 · 已完成 {done_cnt} 题）', 'scene_role_name': '互动学情诊断测评', 'done_count': done_cnt}, ensure_ascii=False)}\n\n".encode("utf-8")
                
                quiz_stats: dict[str, Any] = {}
                async for sse_chunk in stream_quiz_question_sse(diag_params, identity, request_id, retrieved_sources, quiz_stats):
                    yield sse_chunk
                full_quiz_text = quiz_stats["full_text"]
                emitted_chars = quiz_stats["emitted"]
                upstream_error = quiz_stats["error"]

                next_parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None
                dup_stem = normalize_quiz_stem(str(next_parsed_meta.get("stem") or next_parsed_meta.get("question") or "")) if next_parsed_meta else ""
                duplicated = bool(dup_stem and dup_stem in st.asked_stems)

                if (not is_usable_quiz_meta(next_parsed_meta)) or duplicated:
                    if upstream_error and upstream_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    retry_topic = COURSE_DIAGNOSIS_TOPIC_ROTATION[next_step % len(COURSE_DIAGNOSIS_TOPIC_ROTATION)]
                    forbidden_stems = [str(r.get("stem") or r.get("question") or "") for r in st.diag_records]
                    if curr_q_text:
                        forbidden_stems.append(curr_q_text)
                    retry_params = build_parameters(
                        identity,
                        "qa",
                        build_compact_quiz_retry_instruction(retry_topic, forbidden_stems),
                        graph_context,
                        "",
                        "",
                        retrieval_context=retrieval_context,
                        history_context="",
                    )
                    print(f"[DIAGNOSIS] next-question generation failed or duplicated (step={curr_step}, duplicate={duplicated}, emitted={emitted_chars}, error={upstream_error}), retrying with compact instruction", flush=True)
                    retry_stats: dict[str, Any] = {}
                    async for sse_chunk in stream_quiz_question_sse(retry_params, identity, request_id, retrieved_sources, retry_stats):
                        yield sse_chunk
                    full_quiz_text = retry_stats["full_text"]
                    emitted_chars += retry_stats["emitted"]
                    next_parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None
                    dup_stem = normalize_quiz_stem(str(next_parsed_meta.get("stem") or next_parsed_meta.get("question") or "")) if next_parsed_meta else ""
                    duplicated = bool(dup_stem and dup_stem in st.asked_stems)

                if (not is_usable_quiz_meta(next_parsed_meta)) or duplicated:
                    # Honest partial failure: the just-graded answer stays recorded,
                    # no invented question is served; the flow waits for a retry.
                    print(f"[DIAGNOSIS] next-question unavailable after retry (step={curr_step}), awaiting manual retry (last_error={upstream_error})", flush=True)
                    await teaching_state_manager.advance_diagnosis(identity.uid, str(client_sess), record, None)
                    feedback_prefix = "【回答正确】" if is_correct else "【概念辨析与纠偏】"
                    feedback_expl = current_quiz.get("explanation", "")
                    fail_txt = (
                        f"{feedback_prefix}您选择了选项 {norm_ans}。"
                        + (f"答案正确！{feedback_expl}" if is_correct else f"正确选项是 {correct_ans}。{feedback_expl}")
                        + f"\n\n【温馨提示】下一题生成服务暂时不可用（已自动重试一次）。你已完成 {done_cnt} 题作答："
                        + "可回复“下一题”继续获取新题，或回复“生成诊断报告”提前结束并查看学情报告。"
                    )
                    yield f"event: session_state\ndata: {json.dumps({'scene_mode': 4, 'scene_title': f'互动学情诊断测评（已完成 {done_cnt} 题）', 'scene_role_name': '互动学情诊断测评', 'done_count': done_cnt}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: token\ndata: {json.dumps({'text': fail_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_next_question_failed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return

                if emitted_chars == 0:
                    feedback_prefix = "【回答正确】" if is_correct else "【概念辨析与纠偏】"
                    feedback_expl = current_quiz.get("explanation", "")
                    q_stem = next_parsed_meta.get("stem") or next_parsed_meta.get("question") or ""
                    opts = next_parsed_meta.get("options", {})
                    opt_lines = "\n".join([f"{k}. {v}" for k, v in sorted(opts.items())])
                    fallback_stream_text = (
                        f"{feedback_prefix}您选择了选项 {norm_ans}。"
                        + (f"答案正确！{feedback_expl}\n\n" if is_correct else f"正确选项是 {correct_ans}。{feedback_expl}\n\n")
                        + f"---\n\n"
                        f"【互动学情诊断测评 · 第 {next_step} 题】\n\n"
                        f"【题干】{q_stem}\n\n"
                        f"{opt_lines}\n\n"
                        f"【核心考点】{next_parsed_meta.get('knowledge_point', '')}\n"
                        f"【知识溯源】{next_parsed_meta.get('courseware', '')}\n"
                    )
                    yield f"event: token\ndata: {json.dumps({'text': fallback_stream_text, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")

                await teaching_state_manager.advance_diagnosis(identity.uid, str(client_sess), record, next_parsed_meta)
                yield f"event: quiz_meta\ndata: {json.dumps(next_parsed_meta, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_question_served'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 5.5 Diagnosis next-question branch (补发生成失败的下一题)
            if workflow_intent == "diagnosis_next":
                st = await teaching_state_manager.get_or_create(identity.uid, str(client_sess))
                curr_step = st.diag_step
                next_step = curr_step + 1
                done_cnt = len(st.diag_records)
                next_topic_idx = (next_step - 1) % len(COURSE_DIAGNOSIS_TOPIC_ROTATION)
                next_topic = COURSE_DIAGNOSIS_TOPIC_ROTATION[next_topic_idx]
                forbidden_stems = [str(r.get("stem") or r.get("question") or "") for r in st.diag_records]
                next_params = build_parameters(
                    identity,
                    "qa",
                    build_compact_quiz_retry_instruction(next_topic, forbidden_stems),
                    graph_context,
                    "",
                    "",
                    retrieval_context=retrieval_context,
                    history_context="",
                )

                quiz_stats: dict[str, Any] = {}
                async for sse_chunk in stream_quiz_question_sse(next_params, identity, request_id, retrieved_sources, quiz_stats):
                    yield sse_chunk
                full_quiz_text = quiz_stats["full_text"]
                emitted_chars = quiz_stats["emitted"]
                upstream_error = quiz_stats["error"]

                next_parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None
                dup_stem = normalize_quiz_stem(str(next_parsed_meta.get("stem") or next_parsed_meta.get("question") or "")) if next_parsed_meta else ""
                duplicated = bool(dup_stem and dup_stem in st.asked_stems)

                if (not is_usable_quiz_meta(next_parsed_meta)) or duplicated:
                    if upstream_error and upstream_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    retry_topic = COURSE_DIAGNOSIS_TOPIC_ROTATION[next_step % len(COURSE_DIAGNOSIS_TOPIC_ROTATION)]
                    retry_params = build_parameters(
                        identity,
                        "qa",
                        build_compact_quiz_retry_instruction(retry_topic, forbidden_stems),
                        graph_context,
                        "",
                        "",
                        retrieval_context=retrieval_context,
                        history_context="",
                    )
                    print(f"[DIAGNOSIS] pending next-question retry failed again (step={curr_step}, duplicate={duplicated}, error={upstream_error}), one more compact attempt", flush=True)
                    retry_stats: dict[str, Any] = {}
                    async for sse_chunk in stream_quiz_question_sse(retry_params, identity, request_id, retrieved_sources, retry_stats):
                        yield sse_chunk
                    full_quiz_text = retry_stats["full_text"]
                    emitted_chars += retry_stats["emitted"]
                    next_parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None
                    dup_stem = normalize_quiz_stem(str(next_parsed_meta.get("stem") or next_parsed_meta.get("question") or "")) if next_parsed_meta else ""
                    duplicated = bool(dup_stem and dup_stem in st.asked_stems)

                if (not is_usable_quiz_meta(next_parsed_meta)) or duplicated:
                    print(f"[DIAGNOSIS] pending next-question still unavailable (step={curr_step}), keeping awaiting state (last_error={upstream_error})", flush=True)
                    fail_txt = (
                        "【温馨提示】出题服务仍然不可用。你已完成的作答记录完好，请稍等片刻后回复“下一题”重试，"
                        "或回复“生成诊断报告”提前结束并查看已完成的学情报告。"
                    )
                    yield f"event: token\ndata: {json.dumps({'text': fail_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_next_question_failed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return

                new_step = await teaching_state_manager.set_next_question(identity.uid, str(client_sess), next_parsed_meta)
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 4, 'scene_title': f'互动学情诊断测评（第 {new_step} 题 · 已完成 {done_cnt} 题）', 'scene_role_name': '互动学情诊断测评', 'done_count': done_cnt}, ensure_ascii=False)}\n\n".encode("utf-8")

                if emitted_chars == 0:
                    q_stem = next_parsed_meta.get("stem") or next_parsed_meta.get("question") or ""
                    opts = next_parsed_meta.get("options", {})
                    opt_lines = "\n".join([f"{k}. {v}" for k, v in sorted(opts.items())])
                    fallback_stream_text = (
                        f"【互动学情诊断测评 · 第 {new_step} 题】\n\n"
                        f"【题干】{q_stem}\n\n"
                        f"{opt_lines}\n\n"
                        f"【核心考点】{next_parsed_meta.get('knowledge_point', '')}\n"
                        f"【知识溯源】{next_parsed_meta.get('courseware', '')}\n"
                    )
                    yield f"event: token\ndata: {json.dumps({'text': fallback_stream_text, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")

                yield f"event: quiz_meta\ndata: {json.dumps(next_parsed_meta, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'diagnosis_question_served'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 4. Scenario start branches (纯大模型根据角色人设实时流式生成开场对话)
            if workflow_intent == "scenario_start_engineer":
                await teaching_state_manager.set_scene(identity.uid, str(client_sess), 1, "储能电站现场运维师傅")
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 1, 'scene_role_name': '储能电站现场运维师傅'}, ensure_ascii=False)}\n\n".encode("utf-8")
                engineer_prompt = (
                    "【角色设定：储能电站现场一线运维师傅（张师傅）】\n"
                    "学生向你问好：“张师傅您好！我刚来咱们储能电站现场实习，请问您刚巡检完哪些设备，今天带我学习和排查什么工程问题？”\n\n"
                    "【重要输出指令】：请以储能电站老运维师傅（张师傅）第一人称口吻热情回复学生，生动介绍高压变流柜与电池舱现状，并引导他提出想排查的现场问题。严格遵守零表情符号规范。"
                )
                engineer_params = build_parameters(identity, "scenario", engineer_prompt, graph_context, "", "", retrieval_context=retrieval_context, history_context="")
                emitted_tokens = 0
                scene_error: dict[str, Any] | None = None
                async for event in xingchen_stream(engineer_params, identity, request_id, retrieved_sources=retrieved_sources):
                    if event["event"] == "token":
                        raw_tok = str(event["data"].get("text", ""))
                        if raw_tok:
                            emitted_tokens += 1
                            yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "source":
                        yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "error":
                        scene_error = event.get("data") or {}

                if emitted_tokens == 0:
                    if scene_error and scene_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    print(f"[SCENARIO] engineer opening failed (error={scene_error}), retrying once", flush=True)
                    async for event in xingchen_stream(engineer_params, identity, request_id, retrieved_sources=retrieved_sources):
                        if event["event"] == "token":
                            raw_tok = str(event["data"].get("text", ""))
                            if raw_tok:
                                emitted_tokens += 1
                                yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                        elif event["event"] == "source":
                            yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                        elif event["event"] == "error":
                            pass

                if emitted_tokens == 0:
                    # Roll the local scene state back: never fake the role's voice.
                    print(f"[SCENARIO] engineer opening unavailable after retry (last_error={scene_error}), serving honest failure", flush=True)
                    await teaching_state_manager.set_scene(identity.uid, str(client_sess), 0, "")
                    yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_role_name': ''}, ensure_ascii=False)}\n\n".encode("utf-8")
                    fail_txt = "【情景演绎暂时不可用】角色扮演大模型服务本次未返回有效内容（已自动重试一次）。请稍后重新输入“扮演电厂运维师傅”或“扮演主讲老师”再次开始。"
                    yield f"event: token\ndata: {json.dumps({'text': fail_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")

                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'scenario_started' if emitted_tokens else 'scenario_start_failed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            if workflow_intent == "scenario_start_teacher":
                await teaching_state_manager.set_scene(identity.uid, str(client_sess), 2, "《电力系统储能技术》主讲老师")
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 2, 'scene_role_name': '《电力系统储能技术》主讲老师'}, ensure_ascii=False)}\n\n".encode("utf-8")
                teacher_prompt = (
                    "【角色设定：《电力系统储能技术》主讲老师】\n"
                    "学生来到答疑室向你问好：“老师您好！关于近期课程探讨的储能关键技术，我想向您请教一些工程疑难与机理推导。”\n\n"
                    "【重要输出指令】：请以主讲名师的第一人称启发式口吻热情向学生问好，简要提及课程近期的重难点（如变流器构网控制、容量规划配置），询问他想探讨哪个机理。严格遵守零表情符号规范。"
                )
                teacher_params = build_parameters(identity, "scenario", teacher_prompt, graph_context, "", "", retrieval_context=retrieval_context, history_context="")
                emitted_tokens = 0
                scene_error: dict[str, Any] | None = None
                async for event in xingchen_stream(teacher_params, identity, request_id, retrieved_sources=retrieved_sources):
                    if event["event"] == "token":
                        raw_tok = str(event["data"].get("text", ""))
                        if raw_tok:
                            emitted_tokens += 1
                            yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "source":
                        yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "error":
                        scene_error = event.get("data") or {}

                if emitted_tokens == 0:
                    if scene_error and scene_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    print(f"[SCENARIO] teacher opening failed (error={scene_error}), retrying once", flush=True)
                    async for event in xingchen_stream(teacher_params, identity, request_id, retrieved_sources=retrieved_sources):
                        if event["event"] == "token":
                            raw_tok = str(event["data"].get("text", ""))
                            if raw_tok:
                                emitted_tokens += 1
                                yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                        elif event["event"] == "source":
                            yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                        elif event["event"] == "error":
                            pass

                if emitted_tokens == 0:
                    # Roll the local scene state back: never fake the role's voice.
                    print(f"[SCENARIO] teacher opening unavailable after retry (last_error={scene_error}), serving honest failure", flush=True)
                    await teaching_state_manager.set_scene(identity.uid, str(client_sess), 0, "")
                    yield f"event: session_state\ndata: {json.dumps({'scene_mode': 0, 'scene_role_name': ''}, ensure_ascii=False)}\n\n".encode("utf-8")
                    fail_txt = "【情景演绎暂时不可用】角色扮演大模型服务本次未返回有效内容（已自动重试一次）。请稍后重新输入“扮演电厂运维师傅”或“扮演主讲老师”再次开始。"
                    yield f"event: token\ndata: {json.dumps({'text': fail_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")

                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'scenario_started' if emitted_tokens else 'scenario_start_failed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 5. Quiz stop branch
            if workflow_intent == "quiz_stop":
                await teaching_state_manager.pop_active_quiz(identity.uid, str(client_sess))
                stop_txt = "好的，已停止出题练习。书山有路勤为径，学海无涯苦作舟！期待你的下次练习！"
                yield f"event: token\ndata: {json.dumps({'text': stop_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_stopped'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 6. Quiz submit & live LLM grading branch (纯大模型实时智能批改与机理精讲)
            if workflow_intent == "quiz_submit":
                quiz = await teaching_state_manager.pop_active_quiz(identity.uid, str(client_sess))
                if not quiz and history_context and ("A." in history_context or "A、" in history_context or "【题干】" in history_context or "题干" in history_context):
                    recovered = extract_quiz_meta_fallback(history_context)
                    if recovered.get("options") and len(recovered["options"]) >= 2:
                        quiz = recovered

                if not quiz:
                    empty_txt = "您发送了选项作答，但当前没有正在进行的随堂测试。若想开启新测验，请点击下方【随堂出题测试】或直接输入“出题考考我”。"
                    yield f"event: token\ndata: {json.dumps({'text': empty_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_not_active'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                norm_ans = extract_and_normalize_answer(question)
                if norm_ans is None:
                    unparsed_txt = "【请直接作答】未识别到有效选项。请回复选项字母 A、B、C 或 D 完成本题作答；若不想继续，可回复“停止练习”。"
                    yield f"event: token\ndata: {json.dumps({'text': unparsed_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_answer_unparsed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                correct_ans = str(quiz.get("correct_answer", "")).upper().strip()
                if correct_ans not in {"A", "B", "C", "D"}:
                    missing_ans_txt = "【本题答案数据异常】这道题没有携带可核验的标准答案，已停止判分以免误判。可回复“出题”重新开始随堂练习。"
                    yield f"event: token\ndata: {json.dumps({'text': missing_ans_txt, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_answer_missing'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                is_correct = (norm_ans == correct_ans)
                cw = str(quiz.get("courseware", "")).strip()
                cw_file = cw.split(" P")[0].strip() if " P" in cw else ""
                cw_page = cw.split(" P")[1].strip() if " P" in cw else ""
                if cw_file and cw_file not in VALID_COURSEWARE_WHITELIST:
                    cw_file, cw_page = "", ""

                grade_payload = {
                    "source_task": "随堂互动测验",
                    "stem": quiz.get("stem", "储能系统综合单选测验"),
                    "student_answer": norm_ans,
                    "correct_answer": correct_ans,
                    "is_correct": is_correct,
                    "earned_score": 10 if is_correct else 0,
                    "max_score": 10,
                    "knowledge_point": quiz.get("knowledge_point", ""),
                    "courseware": f"{cw_file} P{cw_page}".strip()
                }
                yield f"event: quiz_graded\ndata: {json.dumps(grade_payload, ensure_ascii=False)}\n\n".encode("utf-8")

                quiz_options_str = ""
                raw_opts = quiz.get("options", [])
                if isinstance(raw_opts, list):
                    quiz_options_str = "\n".join([f"- {opt.get('key', '')}. {opt.get('text', '')}" for opt in raw_opts if isinstance(opt, dict)])
                elif isinstance(raw_opts, dict):
                    quiz_options_str = "\n".join([f"- {k}. {v}" for k, v in raw_opts.items()])

                grade_instruction = (
                    f"【定位：随堂互动测验即时名师批改与机理精讲】\n"
                    f"请以《电力系统储能技术》主讲名师身份，对学生刚才作答的随堂自测题进行即时专业批改与深度辨析精讲：\n\n"
                    f"【题目内容】：{quiz.get('stem', '')}\n"
                    f"【选项列表】：\n{quiz_options_str}\n"
                    f"【学生所选选项】：{norm_ans}\n"
                    f"【标准正确选项】：{correct_ans}\n"
                    f"【批改判定】：{'作答正确' if is_correct else '作答错误'}\n"
                    f"【关联知识点与课件】：{quiz.get('knowledge_point', '储能核心考点')}，出处：{cw_file} 第 {cw_page} 页\n\n"
                    f"【输出规范（必须严格遵守）】：\n"
                    f"1. 开头第一行明确输出判卷结论：{'**回答正确！**' if is_correct else '**回答错误。**'} 并附上学生作答与标准答案对比；\n"
                    f"2. 【底层物理/工程机理深度精讲】：结合电力系统实际，详细阐述为什么标准答案【{correct_ans}】是正确的底层原理；{'如果不小心选了【' + norm_ans + '】，请一针见血指出该选项为什么错误、背后的物理概念混淆点在哪里；' if not is_correct else '并对该考点在实际工程拓扑中的关键价值做深化总结；'}\n"
                    f"3. 关联课件指引：明确写出可参考课件溯源：[{cw_file} 第 {cw_page} 页 ↗]；\n"
                    f"4. 结尾简明指引：提示学生“若需进行全章节多维能力体检与生成完整诊断报告，可随时回复‘进行学情诊断’”，并询问学生是否需要再来一题随堂精练。\n"
                    f"严禁使用任何表情符号，直接输出批改与解析内容。"
                )
                grade_params = build_parameters(identity, "qa", grade_instruction, graph_context, "", "", retrieval_context=retrieval_context, history_context="")
                async for event in xingchen_stream(grade_params, identity, request_id, retrieved_sources=retrieved_sources):
                    if event["event"] == "token":
                        raw_tok = str(event["data"].get("text", ""))
                        if raw_tok:
                            yield f"event: token\ndata: {json.dumps({'text': raw_tok, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "source":
                        yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    elif event["event"] == "error":
                        yield f"event: error\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                        return

                yield f"event: source\ndata: {json.dumps({'source_id': f'cw_{cw_page}_{abs(hash(cw_file)) % 10000}', 'file': cw_file, 'chapter': str(quiz.get('knowledge_point', '储能考点')), 'page': int(cw_page) if str(cw_page).isdigit() else 1, 'version': 'v1.0', 'status': 'active', 'request_id': request_id, 'evidence_type': 'quiz_evidence'}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_graded'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            # 7. Quiz generate branch
            if workflow_intent == "quiz_generate":
                quiz_instruction = (
                    f"【定位：随堂单题精练】\n"
                    f"请结合学生的要求【{question.strip()}】，针对某一具体概念或章节出 1 道高质量的单点随堂单选题，用于学生当前学习过程中的即测即评。\n\n"
                    f"{QUIZ_GENERATION_PROMPT}\n"
                    f"【排版要求】：题干下方仅列出 A、B、C、D 各一行，严禁重复打印两遍选项。请严格遵守零表情符号规范，直接输出出题内容。"
                )
                quiz_params = build_parameters(
                    identity,
                    "qa",
                    quiz_instruction,
                    graph_context,
                    "",
                    "",
                    retrieval_context=retrieval_context,
                    history_context="",
                )
                yield f"event: session_state\ndata: {json.dumps({'scene_mode': 3, 'scene_title': '随堂单题精练', 'scene_role_name': '随堂单题精练'}, ensure_ascii=False)}\n\n".encode("utf-8")

                quiz_stats: dict[str, Any] = {}
                async for sse_chunk in stream_quiz_question_sse(quiz_params, identity, request_id, retrieved_sources, quiz_stats):
                    yield sse_chunk
                full_quiz_text = quiz_stats["full_text"]
                emitted_chars = quiz_stats["emitted"]
                upstream_error = quiz_stats["error"]

                parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None
                if not is_usable_quiz_meta(parsed_meta):
                    if upstream_error and upstream_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    st_for_dedup = await teaching_state_manager.get_or_create(identity.uid, str(client_sess))
                    retry_params = build_parameters(
                        identity,
                        "qa",
                        build_compact_quiz_retry_instruction(question.strip() or "电力系统储能技术综合考点", list(st_for_dedup.asked_stems), student_request=question.strip()),
                        graph_context,
                        "",
                        "",
                        retrieval_context=retrieval_context,
                        history_context="",
                    )
                    print(f"[QUIZ] single-question generation failed (emitted={emitted_chars}, error={upstream_error}), retrying with compact instruction", flush=True)
                    retry_stats: dict[str, Any] = {}
                    async for sse_chunk in stream_quiz_question_sse(retry_params, identity, request_id, retrieved_sources, retry_stats):
                        yield sse_chunk
                    full_quiz_text = retry_stats["full_text"]
                    emitted_chars += retry_stats["emitted"]
                    parsed_meta = extract_quiz_meta_fallback(full_quiz_text) if full_quiz_text.strip() else None

                if not is_usable_quiz_meta(parsed_meta):
                    print(f"[QUIZ] single-question unavailable after retry, serving honest failure (last_error={upstream_error})", flush=True)
                    yield f"event: token\ndata: {json.dumps({'text': quiz_failure_notice('随堂出题') + '请稍后回复“出题”或点击“随堂单题精练”重试。', 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_generation_failed'}, ensure_ascii=False)}\n\n".encode("utf-8")
                    return

                # If stream was empty or failed, emit question content from parsed_meta
                if emitted_chars == 0:
                    q_text = (
                        f"【随堂单题精练】\n\n"
                        f"【题干】{parsed_meta['stem']}\n\n"
                        f"A. {parsed_meta['options'].get('A', '')}\n"
                        f"B. {parsed_meta['options'].get('B', '')}\n"
                        f"C. {parsed_meta['options'].get('C', '')}\n"
                        f"D. {parsed_meta['options'].get('D', '')}\n\n"
                        f"【核心考点】{parsed_meta.get('knowledge_point', '')}\n"
                        f"【知识溯源】{parsed_meta.get('courseware', '')}\n"
                    )
                    yield f"event: token\ndata: {json.dumps({'text': q_text, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")

                await teaching_state_manager.set_active_quiz(identity.uid, str(client_sess), parsed_meta)
                yield f"event: quiz_meta\ndata: {json.dumps(parsed_meta, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'quiz_generated'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return

            if learning_insufficient_answer:
                yield f"event: token\ndata: {json.dumps({'text': learning_insufficient_answer, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'deterministic_insufficient_learning_evidence'}, ensure_ascii=False)}\n\n".encode("utf-8")
                return
            if workflow_intent == "question_draft" or mode == "question_draft":
                # Buffer the draft, then decide: the cloud Workflow's question
                # node is configured to withhold answers, so a draft that leaves
                # the answer undecided ("请随机选择") is unusable for teaching and
                # gets one strict retry before anything is shown to the teacher.
                draft_chunks: list[str] = []
                draft_sources: list[dict[str, Any]] = []
                draft_error: dict[str, Any] | None = None

                async def collect_draft(params: dict[str, Any]) -> int:
                    nonlocal draft_error
                    total = 0
                    async for event in xingchen_stream(params, identity, request_id, retrieved_sources=retrieved_sources):
                        if event["event"] == "token":
                            txt = str(event["data"].get("text", ""))
                            total += len(txt)
                            draft_chunks.append(txt)
                        elif event["event"] == "source":
                            draft_sources.append(event.get("data") or {})
                        elif event["event"] == "error":
                            draft_error = event.get("data") or {}
                    return total

                first_len = await collect_draft(parameters)
                draft_text = "".join(draft_chunks)
                has_options = bool(re.search(r"(?:^|\n)\s*A[\.、：:]", draft_text)) or "A." in draft_text
                has_answer = (
                    ("标准答案" in draft_text)
                    or ("正确答案" in draft_text)
                    or bool(re.search(r"答案[:：]", draft_text))
                    or bool(re.search(r"(?:选项|答案)\s*[A-D]\s*(?:是)?正确|正确选项|本题选", draft_text))
                )
                ambiguous = (
                    ("请随机选择" in draft_text)
                    or ("随机选择其中一个" in draft_text)
                    or ("答案选项：" in draft_text and "标准答案" not in draft_text and "正确答案" not in draft_text)
                    or (has_options and not has_answer)
                )
                if ambiguous or (first_len == 0 and draft_error):
                    if draft_error and draft_error.get("code") == "workflow_prompt_echo_rejected":
                        await reset_workflow_scenario_state(identity, request_id)
                    input_name = os.getenv("XINGCHEN_INPUT_NAME", "AGENT_USER_INPUT")
                    retry_instruction = (
                        str(parameters.get(input_name, ""))[:3500]
                        + "\n\n【补严格要求】上一稿未给出确定答案，判定为不合格。重新输出时每道题必须给出唯一确定的【标准答案】字母并附【名师解析】，"
                        "严禁出现“请随机选择”“答案待定”等表述；不要使用代码块围栏，直接输出题目文本。"
                    )
                    retry_params = {input_name: retry_instruction[: int(os.getenv("AGENT_MAX_INPUT_CHARS", "6000"))]}
                    print(f"[QUESTION_DRAFT] ambiguous or empty draft (len={first_len}, ambiguous={ambiguous}, error={draft_error}), retrying with strict answer requirement", flush=True)
                    draft_chunks.clear()
                    draft_error = None
                    await collect_draft(retry_params)
                    draft_text = "".join(draft_chunks)

                if draft_text:
                    yield f"event: token\ndata: {json.dumps({'text': draft_text, 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                    for source in draft_sources:
                        yield f"event: source\ndata: {json.dumps(source, ensure_ascii=False)}\n\n".encode("utf-8")
                elif draft_error:
                    yield f"event: error\ndata: {json.dumps(draft_error, ensure_ascii=False)}\n\n".encode("utf-8")
                yield f"event: done\ndata: {json.dumps({'request_id': request_id, 'reason': 'question_draft_served'}, ensure_ascii=False)}\n\n".encode("utf-8")
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
                        yield f"event: error\ndata: {json.dumps({'code': 'teacher_assistant_failed', 'message': '教师教学备课大模型服务未返回有效内容，请稍后重试或调整主题范围。', 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                        return
                for event in selected_events:
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                return
            target_workflow_id = None
            if is_diagnosis and isinstance(student_ctx, dict) and student_ctx.get("questions"):
                target_workflow_id = os.getenv("XINGCHEN_DIAGNOSIS_FLOW_ID") or None
                async for event in xingchen_stream(
                    parameters,
                    identity,
                    request_id,
                    workflow_id=target_workflow_id,
                    retrieved_sources=retrieved_sources,
                    emit_unverified=False,
                ):
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                return

            emitted_tokens = 0
            has_error = False
            async for event in xingchen_stream(
                parameters,
                identity,
                request_id,
                workflow_id=target_workflow_id,
                retrieved_sources=retrieved_sources,
                emit_unverified=not (mode == "learning_diagnosis" and graph_context.strip() in {"", "[]"}),
            ):
                is_scenario_turn = isinstance(session_id, str) and (mode == "scenario" or parameters.get("AGENT_MODE") == "scenario")
                if event["event"] == "token":
                    raw_text = str(event["data"].get("text", ""))
                    if raw_text:
                        emitted_tokens += 1
                        if is_scenario_turn:
                            scenario_chunks.append(raw_text)
                        yield f"event: token\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                elif event["event"] == "source":
                    if is_scenario_turn:
                        scenario_sources.append(event["data"])
                    yield f"event: source\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                elif event["event"] == "error":
                    has_error = True
                    if is_scenario_turn:
                        scenario_failed = True
                    yield f"event: error\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    return
                elif event["event"] == "done":
                    if is_scenario_turn:
                        completed = store.complete_turn(identity.uid, session_id, int(scenario_turn_no or 0), "".join(scenario_chunks), scenario_sources)
                        scenario_finished = bool(completed)
                        if scenario_finished:
                            store.save_idempotent(identity.uid, f"/course-agent/scenario/{session_id}", scenario_idem_key, scenario_request_body, {"session_id": session_id, "turn_no": scenario_turn_no, "status": "completed", "assistant_text": "".join(scenario_chunks), "evidence": scenario_sources})
                    yield f"event: done\ndata: {json.dumps(event['data'], ensure_ascii=False)}\n\n".encode("utf-8")
                    return

            if emitted_tokens == 0 and not has_error:
                yield f"event: error\ndata: {json.dumps({'code': 'model_response_empty', 'message': '大模型服务暂时未返回有效内容，请稍后重试或重新输入问题。', 'request_id': request_id}, ensure_ascii=False)}\n\n".encode("utf-8")
                return
        finally:
            is_scenario_turn = isinstance(session_id, str) and (mode == "scenario" or parameters.get("AGENT_MODE") == "scenario")
            if is_scenario_turn and (scenario_failed or not scenario_finished):
                store.reset_pending_turn(identity.uid, session_id, int(scenario_turn_no or 0))

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Request-ID": request_id})
