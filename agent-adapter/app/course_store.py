"""Small, durable course data store used by the competition adapter.

The store deliberately keeps structured teaching state outside the LLM.  The
first deployment uses SQLite because it is easy to back up and sufficient for
the two-vCPU demo server; the tables use stable IDs so the same API can later
be moved to MariaDB without changing the page contract.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


CHAPTER_NAMES = {
    1: "第1章 概述",
    2: "第2章 电力系统与储能技术的应用",
    3: "第3章 电力储能系统的组成及工作原理",
    4: "第4章 电力储能系统的规划配置",
    5: "第5章 电力储能系统的接入与运行控制",
    6: "第6章 电力储能系统的性能检测与评估",
}


def parse_due_at(value: Any) -> datetime | None:
    """Parse an explicit ISO-8601 deadline and normalize it to UTC."""
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("invalid_due_at")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid_due_at") from exc
    if parsed.tzinfo is None:
        raise ValueError("due_at_requires_timezone")
    return parsed.astimezone(timezone.utc)


class ClosingConnection(sqlite3.Connection):
    """Make ``with connect()`` close the handle as well as commit/rollback."""

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        try:
            super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


class CourseStore:
    """Thread-safe SQLite access with idempotent bootstrap data."""

    def __init__(self) -> None:
        # /tmp keeps local protocol tests usable; the container overrides this
        # to the persistent /app/data volume in docker-compose.
        # Keep the database filename separate from the graph path() method;
        # using the same attribute name would shadow the callable at runtime.
        self.db_path = Path(os.getenv("COURSE_DB", "/tmp/course-agent/course.db"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False, factory=ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._lock, self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    sort_order INTEGER NOT NULL UNIQUE,
                    course_id INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    id TEXT PRIMARY KEY,
                    chapter_id INTEGER NOT NULL REFERENCES chapters(id),
                    name TEXT NOT NULL,
                    node_type TEXT NOT NULL DEFAULT 'knowledge_point',
                    category TEXT,
                    description TEXT,
                    UNIQUE(chapter_id, name)
                );
                CREATE TABLE IF NOT EXISTS knowledge_edges (
                    from_id TEXT NOT NULL REFERENCES knowledge_nodes(id),
                    to_id TEXT NOT NULL REFERENCES knowledge_nodes(id),
                    relation_type TEXT NOT NULL CHECK(relation_type IN ('prerequisite','related','postrequisite')),
                    PRIMARY KEY(from_id, to_id, relation_type),
                    CHECK(from_id <> to_id)
                );
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    chapter_id INTEGER NOT NULL REFERENCES chapters(id),
                    node_id TEXT REFERENCES knowledge_nodes(id),
                    source_file TEXT NOT NULL,
                    normalized_file TEXT NOT NULL,
                    page_start INTEGER NOT NULL DEFAULT 1,
                    page_end INTEGER,
                    sha256 TEXT,
                    version TEXT NOT NULL DEFAULT 'local-v1'
                );
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    chapter_id INTEGER REFERENCES chapters(id),
                    node_id TEXT REFERENCES knowledge_nodes(id),
                    question_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    options_json TEXT,
                    answer_json TEXT,
                    rubric TEXT,
                    max_score REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    version INTEGER NOT NULL DEFAULT 1,
                    created_by TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS assignments (
                    id TEXT PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    question_ids_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    due_at TEXT,
                    allow_attempts INTEGER NOT NULL DEFAULT 1,
                    created_by TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS submissions (
                    id TEXT PRIMARY KEY,
                    assignment_id TEXT NOT NULL REFERENCES assignments(id),
                    user_uid TEXT NOT NULL,
                    moodle_user_id INTEGER,
                    answers_json TEXT NOT NULL,
                    attempt INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL DEFAULT 'submitted',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(assignment_id, user_uid, attempt)
                );
                CREATE TABLE IF NOT EXISTS grades (
                    id TEXT PRIMARY KEY,
                    submission_id TEXT NOT NULL REFERENCES submissions(id),
                    question_id TEXT NOT NULL REFERENCES questions(id),
                    score REAL NOT NULL,
                    max_score REAL NOT NULL,
                    feedback TEXT,
                    source TEXT NOT NULL DEFAULT 'deterministic',
                    reviewed_by TEXT,
                    review_reason TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(submission_id, question_id)
                );
                CREATE TABLE IF NOT EXISTS grade_audit (
                    id TEXT PRIMARY KEY,
                    grade_id TEXT NOT NULL REFERENCES grades(id),
                    old_score REAL NOT NULL,
                    new_score REAL NOT NULL,
                    reason TEXT NOT NULL,
                    changed_by TEXT NOT NULL,
                    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS grading_tasks (
                    id TEXT PRIMARY KEY,
                    assignment_id TEXT NOT NULL REFERENCES assignments(id),
                    status TEXT NOT NULL,
                    total INTEGER NOT NULL DEFAULT 0,
                    completed INTEGER NOT NULL DEFAULT 0,
                    failed INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS scenario_sessions (
                    id TEXT PRIMARY KEY,
                    user_uid TEXT NOT NULL,
                    scenario_key TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'active',
                    context_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS scenario_turns (
                    session_id TEXT NOT NULL REFERENCES scenario_sessions(id),
                    turn_no INTEGER NOT NULL,
                    user_text TEXT NOT NULL,
                    assistant_text TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    evidence_json TEXT NOT NULL DEFAULT '[]',
                    request_id TEXT NOT NULL,
                    PRIMARY KEY(session_id, turn_no)
                );
                CREATE TABLE IF NOT EXISTS kb_versions (
                    id TEXT PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    version_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    manifest_sha256 TEXT,
                    workflow_id TEXT,
                    source_count INTEGER NOT NULL DEFAULT 0,
                    hit_status TEXT,
                    created_by TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS kb_files (
                    id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL REFERENCES kb_versions(id),
                    filename TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'accepted',
                    error_message TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(version_id, sha256)
                );
                CREATE TABLE IF NOT EXISTS kb_audit (
                    id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    actor_uid TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS kb_hit_tests (
                    id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL REFERENCES kb_versions(id),
                    case_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    expected_chapter TEXT NOT NULL,
                    actual_sources_json TEXT NOT NULL DEFAULT '[]',
                    status TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    actor_uid TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(version_id, case_id)
                );
                CREATE TABLE IF NOT EXISTS idempotency (
                    user_uid TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    idem_key TEXT NOT NULL,
                    request_hash TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    PRIMARY KEY(user_uid, endpoint, idem_key)
                );
                """
            )
            # Existing demo volumes may have been created by an earlier
            # adapter build. SQLite's CREATE IF NOT EXISTS does not alter an
            # existing table, so apply the small additive migration explicitly.
            columns = {row["name"] for row in db.execute("PRAGMA table_info(assignments)")}
            if "allow_attempts" not in columns:
                db.execute("ALTER TABLE assignments ADD COLUMN allow_attempts INTEGER NOT NULL DEFAULT 1")
            submission_columns = {row["name"] for row in db.execute("PRAGMA table_info(submissions)")}
            if "moodle_user_id" not in submission_columns:
                db.execute("ALTER TABLE submissions ADD COLUMN moodle_user_id INTEGER")
            # Scenario turns were initially input-only rows. Keep this
            # migration additive so existing demo volumes retain their history
            # while new calls can persist validated Workflow evidence.
            turn_columns = {row["name"] for row in db.execute("PRAGMA table_info(scenario_turns)")}
            if "status" not in turn_columns:
                db.execute("ALTER TABLE scenario_turns ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")
            if "evidence_json" not in turn_columns:
                db.execute("ALTER TABLE scenario_turns ADD COLUMN evidence_json TEXT NOT NULL DEFAULT '[]'")
            self._seed_graph(db)
            self._seed_resources(db)
            db.commit()

    def _seed_graph(self, db: sqlite3.Connection) -> None:
        for number, name in CHAPTER_NAMES.items():
            db.execute(
                "INSERT OR IGNORE INTO chapters(id,name,sort_order) VALUES(?,?,?)",
                (number, name, number),
            )
        # The fallback graph is deterministic and mirrors the supplied workbook.
        # A generated graph-baseline.json can replace it without changing APIs.
        baseline = Path(os.getenv("GRAPH_BASELINE", "/app/course-data/graph-baseline.json"))
        nodes: list[dict[str, Any]] = []
        baseline_edges: list[dict[str, Any]] = []
        if baseline.exists():
            try:
                baseline_data = json.loads(baseline.read_text(encoding="utf-8"))
                nodes = baseline_data.get("nodes", [])
                baseline_edges = baseline_data.get("edges", [])
            except (OSError, json.JSONDecodeError):
                nodes = []
        if not nodes:
            # This fallback lets a clean deployment expose the approved
            # twenty-point course outline before the workbook is mounted.
            names = {
                1: ["1.1 电力储能技术的概念", "1.2 电力储能技术的发展", "1.3 储能技术在电力系统中的应用"],
                2: ["2.1 电力系统的概念", "2.2 电力系统的运行特点和要求", "2.3 储能技术的典型应用"],
                3: ["3.1 抽水蓄能电站的组成及工作原理", "3.2 新型电力储能系统的组成", "3.3 新型电能存储设备工作原理", "3.4 储能变流器拓扑及并网控制", "3.5 储能监控系统结构及通信"],
                4: ["4.1 抽水蓄能电站的规划配置", "4.2 电化学储能系统的规划配置", "4.3 电池储能系统集成技术"],
                5: ["5.1 电力储能系统的接入", "5.2 电力储能系统的运行控制", "5.3 电力储能系统的运行维护", "5.4 电力储能系统的运行案例"],
                6: ["6.1 电力储能系统的性能检测", "6.2 电力储能系统的系统评估"],
            }
            for chapter, chapter_nodes in names.items():
                for index, name in enumerate(chapter_nodes, start=1):
                    nodes.append({"id": f"kp-{chapter}-{index}", "chapter_id": chapter, "name": name, "category": "概念性"})
        for item in nodes:
            db.execute(
                "INSERT OR IGNORE INTO knowledge_nodes(id,chapter_id,name,node_type,category,description) VALUES(?,?,?,?,?,?)",
                (str(item["id"]), int(item["chapter_id"]), str(item["name"]),
                 str(item.get("node_type", "knowledge_point")), str(item.get("category", "")),
                 str(item.get("description", ""))),
            )
        if baseline_edges:
            for edge in baseline_edges:
                db.execute("INSERT OR IGNORE INTO knowledge_edges VALUES(?,?,?)", (str(edge["from_id"]), str(edge["to_id"]), str(edge.get("relation_type", "prerequisite"))))
        else:
            # Chapter -> first point and sequential points are deterministic
            # fallback edges used before the workbook baseline is mounted.
            for chapter in range(1, 7):
                rows = db.execute("SELECT id FROM knowledge_nodes WHERE chapter_id=? ORDER BY id", (chapter,)).fetchall()
                for left, right in zip(rows, rows[1:]):
                    db.execute("INSERT OR IGNORE INTO knowledge_edges VALUES(?,?,?)", (left["id"], right["id"], "prerequisite"))

    def _seed_resources(self, db: sqlite3.Connection) -> None:
        manifest_path = Path(os.getenv("COURSE_MANIFEST", "/app/course-data/manifest.json"))
        if not manifest_path.exists():
            return
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for item in manifest.get("files", []):
            source = str(item.get("source_file", ""))
            normalized = str(item.get("normalized_file", ""))
            chapter = int(item.get("chapter_id", 0) or 0)
            if not source or not normalized or chapter not in CHAPTER_NAMES:
                continue
            resource_id = "res-" + hashlib.sha256(f"{normalized}:{chapter}".encode()).hexdigest()[:20]
            point_match = re.search(r"(\d+\.\d+)", source)
            node_id = None
            if point_match:
                node = db.execute("SELECT id FROM knowledge_nodes WHERE name LIKE ? LIMIT 1", (point_match.group(1) + "%",)).fetchone()
                node_id = node["id"] if node else None
            db.execute(
                "INSERT INTO resources(id,chapter_id,node_id,source_file,normalized_file,page_start,page_end,sha256,version) VALUES(?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET chapter_id=excluded.chapter_id,node_id=excluded.node_id,source_file=excluded.source_file,normalized_file=excluded.normalized_file,page_end=excluded.page_end,sha256=excluded.sha256,version=excluded.version",
                (resource_id, chapter, node_id, source, normalized, 1, item.get("page_count"), str(item.get("sha256", "")), str(manifest.get("source_archive", "local-v1"))),
            )

    def chapters(self) -> list[dict[str, Any]]:
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM chapters ORDER BY sort_order")]

    def node(self, node_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM knowledge_nodes WHERE id=?", (node_id,)).fetchone()
            if not row:
                return None
            result = dict(row)
            result["neighbors"] = [dict(item) for item in db.execute(
                "SELECT e.relation_type,n.id,n.name,n.chapter_id FROM knowledge_edges e JOIN knowledge_nodes n ON n.id=e.to_id WHERE e.from_id=? UNION ALL SELECT e.relation_type,n.id,n.name,n.chapter_id FROM knowledge_edges e JOIN knowledge_nodes n ON n.id=e.from_id WHERE e.to_id=?",
                (node_id, node_id),
            )]
            result["resources"] = [dict(item) for item in db.execute("SELECT * FROM resources WHERE node_id=? OR chapter_id=?", (node_id, result["chapter_id"]))]
            return result

    def search_nodes(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        query = query.strip()[:100]
        with self.connect() as db:
            rows = db.execute("SELECT * FROM knowledge_nodes WHERE name LIKE ? OR description LIKE ? ORDER BY chapter_id,id LIMIT ?", (f"%{query}%", f"%{query}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def path(self, start_id: str, end_id: str, max_depth: int = 8) -> list[str] | None:
        """Find a bounded prerequisite path without allowing unbounded graph walks."""
        with self.connect() as db:
            queue: list[tuple[str, list[str]]] = [(start_id, [start_id])]
            visited = {start_id}
            while queue:
                current, chain = queue.pop(0)
                if current == end_id:
                    return chain
                if len(chain) > max_depth:
                    continue
                children = db.execute("SELECT to_id FROM knowledge_edges WHERE from_id=? AND relation_type='prerequisite'", (current,)).fetchall()
                for child in children:
                    child_id = str(child["to_id"])
                    if child_id not in visited:
                        visited.add(child_id)
                        queue.append((child_id, chain + [child_id]))
        return None

    def resources(self, chapter_id: int | None = None, node_id: str | None = None) -> list[dict[str, Any]]:
        with self.connect() as db:
            if node_id:
                rows = db.execute("SELECT r.* FROM resources r JOIN chapters c ON c.id=r.chapter_id WHERE r.node_id=? AND c.course_id=1", (node_id,)).fetchall()
            elif chapter_id:
                rows = db.execute("SELECT r.* FROM resources r JOIN chapters c ON c.id=r.chapter_id WHERE r.chapter_id=? AND c.course_id=1 ORDER BY r.source_file", (chapter_id,)).fetchall()
            else:
                rows = db.execute("SELECT r.* FROM resources r JOIN chapters c ON c.id=r.chapter_id WHERE c.course_id=1 ORDER BY r.chapter_id,r.source_file").fetchall()
            return [dict(row) for row in rows]

    def resource(self, resource_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT r.* FROM resources r JOIN chapters c ON c.id=r.chapter_id WHERE r.id=? AND c.course_id=1", (resource_id,)).fetchone()
            return dict(row) if row else None

    def kb_versions(self) -> list[dict[str, Any]]:
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM kb_versions WHERE course_id=1 ORDER BY updated_at DESC")]

    def published_kb(self) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM kb_versions WHERE course_id=1 AND status='published' LIMIT 1").fetchone()
            return dict(row) if row else None

    def create_kb_version(self, uid: str, payload: dict[str, Any]) -> dict[str, Any]:
        version_id = "kb-" + uuid.uuid4().hex
        with self._lock, self.connect() as db:
            db.execute("INSERT INTO kb_versions(id,course_id,version_name,status,manifest_sha256,workflow_id,source_count,hit_status,created_by) VALUES(?,?,?,?,?,?,?,?,?)", (version_id, 1, payload["version_name"], "draft", payload.get("manifest_sha256"), payload.get("workflow_id"), int(payload.get("source_count", 0)), "not_tested", uid))
            db.commit()
        return next(item for item in self.kb_versions() if item["id"] == version_id)

    def add_kb_file(self, version_id: str, filename: str, content: bytes) -> dict[str, Any]:
        """Store a validated file record; the raw bytes stay under agent_data."""
        digest = hashlib.sha256(content).hexdigest()
        with self._lock, self.connect() as db:
            version = db.execute("SELECT status FROM kb_versions WHERE id=? AND course_id=1", (version_id,)).fetchone()
            if not version:
                raise LookupError("kb_version_not_found")
            if version["status"] not in {"draft", "processing"}:
                raise ValueError("kb_version_not_uploadable")
            existing = db.execute("SELECT * FROM kb_files WHERE version_id=? AND sha256=?", (version_id, digest)).fetchone()
            if existing:
                return dict(existing)
            file_id = "kb-file-" + uuid.uuid4().hex
            db.execute("INSERT INTO kb_files(id,version_id,filename,sha256,size_bytes) VALUES(?,?,?,?,?)", (file_id, version_id, filename, digest, len(content)))
            db.execute("UPDATE kb_versions SET status='processing',source_count=source_count+1,updated_at=CURRENT_TIMESTAMP WHERE id=?", (version_id,))
            db.commit()
            row = db.execute("SELECT * FROM kb_files WHERE id=?", (file_id,)).fetchone()
            return dict(row) if row else None

    def kb_files(self, version_id: str) -> list[dict[str, Any]]:
        with self.connect() as db:
            return [dict(row) for row in db.execute("SELECT f.* FROM kb_files f JOIN kb_versions v ON v.id=f.version_id WHERE f.version_id=? AND v.course_id=1 ORDER BY f.filename", (version_id,))]

    def kb_manifest_valid(self, version_id: str) -> bool:
        """Verify uploaded course files against the server-owned manifest.

        Publishing is a release operation, so a browser-provided filename or
        hash is not evidence. PDF uploads must match a manifest source name
        (original or normalized) and its SHA-256. Markdown uploads are allowed
        for merged chapter exports, but they must contain at least one source
        marker that points back to a manifest file.
        """
        manifest_path = Path(os.getenv("COURSE_MANIFEST", "/app/course-data/manifest.json"))
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        by_name: dict[str, dict[str, Any]] = {}
        for item in manifest.get("files", []):
            for name in (item.get("source_file"), item.get("normalized_file")):
                if name:
                    by_name[str(name)] = item

        storage_root = Path(os.getenv("KB_STORAGE_DIR", "/app/data/kb-files")) / version_id
        files = self.kb_files(version_id)
        if not files:
            return False
        valid_pdf = False
        valid_markdown = False
        marker = re.compile(r"\[来源文件：([^；\]]+)")
        for item in files:
            filename = str(item["filename"])
            suffix = Path(filename).suffix.lower()
            path = storage_root / filename
            try:
                content = path.read_bytes()
            except OSError:
                return False
            if hashlib.sha256(content).hexdigest() != str(item["sha256"]):
                return False
            if suffix == ".pdf":
                expected = by_name.get(filename)
                if not expected or str(expected.get("sha256", "")) != str(item["sha256"]):
                    return False
                valid_pdf = True
            elif suffix == ".md":
                try:
                    text = content.decode("utf-8")
                except UnicodeDecodeError:
                    return False
                names = [match.group(1).strip() for match in marker.finditer(text)]
                if not names or any(name not in by_name for name in names):
                    return False
                valid_markdown = True
            else:
                return False
        return valid_pdf or valid_markdown

    def update_kb_status(self, version_id: str, status: str, uid: str, hit_status: str | None = None) -> dict[str, Any] | None:
        allowed = {"draft": {"processing"}, "processing": {"tested", "failed"}, "tested": {"published", "failed"}, "published": {"archived"}, "failed": {"processing"}, "archived": set()}
        with self._lock, self.connect() as db:
            current = db.execute("SELECT status FROM kb_versions WHERE id=? AND course_id=1", (version_id,)).fetchone()
            if not current:
                return None
            if current["status"] == status:
                row = db.execute("SELECT * FROM kb_versions WHERE id=?", (version_id,)).fetchone()
                return dict(row) if row else None
            if status not in allowed.get(current["status"], set()):
                raise ValueError("invalid_kb_transition")
            version = db.execute("SELECT source_count,workflow_id FROM kb_versions WHERE id=?", (version_id,)).fetchone()
            passed_tests = db.execute(
                "SELECT COUNT(*) FROM kb_hit_tests WHERE version_id=? AND status='passed'",
                (version_id,),
            ).fetchone()[0]
            required_tests = 3
            # The caller cannot skip the real golden-question records by
            # sending hit_status=passed; the database is the release gate.
            manifest_valid = self.kb_manifest_valid(version_id)
            if status == "tested" and (not version["source_count"] or not manifest_valid or passed_tests < required_tests):
                raise ValueError("kb_test_gate_failed")
            if status == "published" and (not version["source_count"] or not manifest_valid or not version["workflow_id"] or passed_tests < required_tests):
                raise ValueError("kb_publish_gate_failed")
            if status == "published":
                db.execute("UPDATE kb_versions SET status='archived',updated_at=CURRENT_TIMESTAMP WHERE course_id=1 AND status='published' AND id<>?", (version_id,))
            db.execute("UPDATE kb_versions SET status=?,hit_status=COALESCE(?,hit_status),updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, hit_status, version_id))
            # Status changes are part of the release audit trail. Keeping them
            # in the same transaction as the version update prevents a
            # published version from existing without an operator record.
            db.execute(
                "INSERT INTO kb_audit(id,version_id,action,reason,actor_uid) VALUES(?,?,?,?,?)",
                ("kb-audit-" + uuid.uuid4().hex, version_id, "status:" + status, "状态变更", uid),
            )
            db.commit()
            row = db.execute("SELECT * FROM kb_versions WHERE id=?", (version_id,)).fetchone()
            return dict(row) if row else None

    def save_kb_hit_test(
        self,
        version_id: str,
        case_id: str,
        question: str,
        expected_chapter: str,
        sources: list[dict[str, Any]],
        status: str,
        request_id: str,
        uid: str,
    ) -> dict[str, Any]:
        """Persist one executed golden case and its bounded source evidence."""
        with self._lock, self.connect() as db:
            db.execute(
                "INSERT INTO kb_hit_tests(id,version_id,case_id,question,expected_chapter,actual_sources_json,status,request_id,actor_uid) "
                "VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(version_id,case_id) DO UPDATE SET question=excluded.question,expected_chapter=excluded.expected_chapter,actual_sources_json=excluded.actual_sources_json,status=excluded.status,request_id=excluded.request_id,actor_uid=excluded.actor_uid,created_at=CURRENT_TIMESTAMP",
                (
                    "kb-hit-" + uuid.uuid4().hex,
                    version_id,
                    case_id,
                    question,
                    expected_chapter,
                    json.dumps(sources, ensure_ascii=False),
                    status,
                    request_id,
                    uid,
                ),
            )
            db.execute("UPDATE kb_versions SET hit_status=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND course_id=1", ("passed" if status == "passed" else "failed", version_id))
            db.execute(
                "INSERT INTO kb_audit(id,version_id,action,reason,actor_uid) VALUES(?,?,?,?,?)",
                ("kb-audit-" + uuid.uuid4().hex, version_id, "hit-test:" + case_id + ":" + status, "黄金问题实际执行", uid),
            )
            db.commit()
            row = db.execute("SELECT * FROM kb_hit_tests WHERE version_id=? AND case_id=?", (version_id, case_id)).fetchone()
            result = dict(row)
            result["actual_sources"] = json.loads(result.pop("actual_sources_json") or "[]")
            return result

    def kb_hit_tests(self, version_id: str) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT id,version_id,case_id,question,expected_chapter,actual_sources_json,status,request_id,actor_uid,created_at FROM kb_hit_tests WHERE version_id=? ORDER BY case_id",
                (version_id,),
            ).fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["actual_sources"] = json.loads(item.pop("actual_sources_json") or "[]")
                result.append(item)
            return result

    def rollback_kb(self, version_id: str, uid: str, reason: str) -> dict[str, Any] | None:
        with self._lock, self.connect() as db:
            target = db.execute("SELECT * FROM kb_versions WHERE id=? AND course_id=1", (version_id,)).fetchone()
            current = db.execute("SELECT id FROM kb_versions WHERE course_id=1 AND status='published' AND id<>?", (version_id,)).fetchone()
            if not target or target["status"] not in {"tested", "archived"} or target["hit_status"] != "passed" or not target["workflow_id"]:
                raise ValueError("kb_rollback_gate_failed")
            if current:
                db.execute("UPDATE kb_versions SET status='archived',updated_at=CURRENT_TIMESTAMP WHERE id=?", (current["id"],))
            db.execute("UPDATE kb_versions SET status='published',updated_at=CURRENT_TIMESTAMP WHERE id=?", (version_id,))
            db.execute("INSERT INTO kb_audit(id,version_id,action,reason,actor_uid) VALUES(?,?,?,?,?)", ("kb-audit-" + uuid.uuid4().hex, version_id, "rollback", reason[:500], uid))
            db.commit()
            row = db.execute("SELECT * FROM kb_versions WHERE id=?", (version_id,)).fetchone()
            return dict(row) if row else None

    def create_scenario(self, uid: str, scenario_key: str) -> dict[str, Any]:
        scenarios = {
            "grid-dispatch": {"title": "储能电站并网调度", "goal": "在约束条件下完成削峰填谷调度", "assumptions": "以下功率和电价均为模拟数据"},
            "battery-fault": {"title": "电化学储能异常诊断", "goal": "根据告警和测量值定位排查方向", "assumptions": "以下告警和测量值均为模拟数据"},
        }
        context = scenarios.get(scenario_key, scenarios["grid-dispatch"])
        session_id = "sim-" + uuid.uuid4().hex
        with self._lock, self.connect() as db:
            db.execute("INSERT INTO scenario_sessions(id,user_uid,scenario_key,context_json) VALUES(?,?,?,?)", (session_id, uid, scenario_key, json.dumps(context, ensure_ascii=False)))
            db.commit()
        return {"session_id": session_id, "state": "active", **context}

    def scenario(self, uid: str, session_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM scenario_sessions WHERE id=? AND user_uid=?", (session_id, uid)).fetchone()
            if not row:
                return None
            result = dict(row)
            result["context"] = json.loads(result.pop("context_json"))
            turns = []
            for item in db.execute("SELECT * FROM scenario_turns WHERE session_id=? ORDER BY turn_no", (session_id,)):
                turn = dict(item)
                turn["evidence"] = json.loads(turn.pop("evidence_json", "[]") or "[]")
                turns.append(turn)
            result["turns"] = turns
            return result

    def add_turn(self, uid: str, session_id: str, turn_no: int, user_text: str, request_id: str) -> dict[str, Any]:
        with self._lock, self.connect() as db:
            row = db.execute("SELECT state FROM scenario_sessions WHERE id=? AND user_uid=?", (session_id, uid)).fetchone()
            if not row:
                raise LookupError("scenario_not_found")
            if row["state"] != "active":
                raise ValueError("scenario_not_active")
            existing = db.execute("SELECT * FROM scenario_turns WHERE session_id=? AND turn_no=?", (session_id, turn_no)).fetchone()
            if existing:
                return dict(existing)
            db.execute("INSERT INTO scenario_turns(session_id,turn_no,user_text,status,evidence_json,request_id) VALUES(?,?,?, 'pending', '[]', ?)", (session_id, turn_no, user_text[:4000], request_id))
            db.execute("UPDATE scenario_sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (session_id,))
            db.commit()
            return {"session_id": session_id, "turn_no": turn_no, "state": "active", "status": "pending", "request_id": request_id}

    def complete_turn(self, uid: str, session_id: str, turn_no: int, assistant_text: str, evidence: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Persist a successful Workflow result and validated source events."""
        with self._lock, self.connect() as db:
            changed = db.execute(
                "UPDATE scenario_turns SET assistant_text=?,status='completed',evidence_json=? "
                "WHERE session_id=? AND turn_no=? AND status='pending' "
                "AND EXISTS (SELECT 1 FROM scenario_sessions WHERE id=? AND user_uid=? AND state='active')",
                (assistant_text[:12000], json.dumps(evidence[:20], ensure_ascii=False), session_id, turn_no, session_id, uid),
            ).rowcount
            if not changed:
                row = db.execute(
                    "SELECT t.* FROM scenario_turns t JOIN scenario_sessions s ON s.id=t.session_id "
                    "WHERE t.session_id=? AND t.turn_no=? AND s.user_uid=?",
                    (session_id, turn_no, uid),
                ).fetchone()
                return dict(row) if row else None
            db.execute("UPDATE scenario_sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_uid=?", (session_id, uid))
            db.commit()
            row = db.execute("SELECT * FROM scenario_turns WHERE session_id=? AND turn_no=?", (session_id, turn_no)).fetchone()
            return dict(row) if row else None

    def reset_pending_turn(self, uid: str, session_id: str, turn_no: int) -> None:
        """Remove only an unfinished turn so a failed upstream call can retry."""
        with self._lock, self.connect() as db:
            db.execute(
                "DELETE FROM scenario_turns WHERE session_id=? AND turn_no=? AND status='pending' "
                "AND EXISTS (SELECT 1 FROM scenario_sessions WHERE id=? AND user_uid=? AND state='active')",
                (session_id, turn_no, session_id, uid),
            )
            db.commit()

    def end_scenario(self, uid: str, session_id: str, state: str = "completed") -> dict[str, Any]:
        if state not in {"completed", "aborted"}:
            raise ValueError("invalid_scenario_state")
        with self._lock, self.connect() as db:
            changed = db.execute("UPDATE scenario_sessions SET state=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_uid=? AND state='active'", (state, session_id, uid)).rowcount
            if not changed:
                raise LookupError("scenario_not_found_or_closed")
            db.commit()
        return {"session_id": session_id, "state": state}

    def learning_profile(self, uid: str) -> dict[str, Any]:
        # Scores are computed from stored grades, never inferred by the model.
        # First select the last valid attempt per assignment, then aggregate by
        # knowledge point so a retry cannot inflate mastery or erase an error.
        with self.connect() as db:
            nodes = [dict(row) for row in db.execute("SELECT id,name,chapter_id FROM knowledge_nodes ORDER BY chapter_id,id")]
            prerequisite_rows = db.execute(
                "SELECT from_id,to_id FROM knowledge_edges WHERE relation_type='prerequisite'"
            ).fetchall()
            rows = db.execute(
                "SELECT n.id node_id,n.name,n.chapter_id,g.score,g.max_score,g.question_id,"
                "s.id submission_id,s.assignment_id,s.attempt,s.created_at,s.answers_json "
                "FROM grades g JOIN questions q ON q.id=g.question_id "
                "JOIN knowledge_nodes n ON n.id=q.node_id "
                "JOIN submissions s ON s.id=g.submission_id "
                "WHERE s.user_uid=? AND s.attempt=(SELECT MAX(s2.attempt) FROM submissions s2 "
                "WHERE s2.assignment_id=s.assignment_id AND s2.user_uid=?) "
                "ORDER BY s.created_at,s.id,g.question_id",
                (uid, uid),
            ).fetchall()

        # Collapse multiple questions for one node within one submission into
        # one effective record; mastery needs two different submissions.
        records: dict[str, dict[str, dict[str, Any]]] = {}
        for row in rows:
            item = dict(row)
            node_records = records.setdefault(item["node_id"], {})
            record = node_records.setdefault(
                item["submission_id"],
                {"submission_id": item["submission_id"], "created_at": item["created_at"], "score": 0.0, "max_score": 0.0, "error": False},
            )
            record["score"] += float(item["score"] or 0)
            record["max_score"] += float(item["max_score"] or 0)
            answers = json.loads(item["answers_json"] or "{}")
            answer = answers.get(item["question_id"])
            if answer is None or answer == "" or float(item["score"] or 0) < float(item["max_score"] or 0):
                record["error"] = True

        prerequisites: dict[str, list[str]] = {}
        for edge in prerequisite_rows:
            prerequisites.setdefault(str(edge["to_id"]), []).append(str(edge["from_id"]))

        result = []
        for node in nodes:
            node_records = sorted(records.get(node["id"], {}).values(), key=lambda value: (value["created_at"], value["submission_id"]))
            score = sum(float(item["score"]) for item in node_records)
            maximum = sum(float(item["max_score"]) for item in node_records)
            record_count = len(node_records)
            ratio = score / maximum if maximum else None
            recent = node_records[-2:]
            two_clean = len(recent) == 2 and all(not item["error"] for item in recent)
            two_errors = len(recent) == 2 and all(item["error"] for item in recent)
            if record_count == 0 or ratio is None:
                status = "unassessed"
            elif ratio < 0.60 or two_errors:
                status = "weak"
            elif record_count >= 2 and ratio >= 0.80 and two_clean:
                status = "mastered"
            else:
                status = "learning"
            result.append({
                **node,
                "score": score,
                "max_score": maximum,
                "ratio": ratio,
                "grade_count": record_count,
                "effective_submission_count": record_count,
                "status": status,
                "recent_error": bool(node_records and node_records[-1]["error"]),
                "prerequisite_ids": prerequisites.get(node["id"], []),
            })
        status_by_id = {item["id"]: item["status"] for item in result}
        for item in result:
            item["prerequisite_gap"] = [
                prerequisite_id for prerequisite_id in item["prerequisite_ids"]
                if status_by_id.get(prerequisite_id) in {"weak", "unassessed"}
            ]
        return {"rule_version": "learning-rule-v1", "user_uid": uid, "nodes": result}

    def list_questions(self, published_only: bool = False) -> list[dict[str, Any]]:
        with self.connect() as db:
            where = " WHERE course_id=1 AND status='published'" if published_only else " WHERE course_id=1"
            rows = db.execute("SELECT id,course_id,chapter_id,node_id,question_type,prompt,options_json,max_score,status,version,created_by,updated_at FROM questions" + where + " ORDER BY updated_at DESC").fetchall()
            result = []
            for row in rows:
                item = dict(row)
                if item.get("options_json"):
                    item["options"] = json.loads(item.pop("options_json"))
                result.append(item)
            return result

    def create_question(self, uid: str, payload: dict[str, Any]) -> dict[str, Any]:
        question_type = str(payload.get("question_type", ""))
        prompt = str(payload.get("prompt", "")).strip()
        maximum = float(payload.get("max_score", 0))
        if question_type not in {"single_choice", "multiple_choice", "true_false", "short_answer", "essay"} or not prompt or not math.isfinite(maximum) or not 0 < maximum <= 100:
            raise ValueError("invalid_question_schema")
        if question_type in {"single_choice", "multiple_choice"}:
            options = payload.get("options")
            if not isinstance(options, list) or len(options) < 2 or not payload.get("answer"):
                raise ValueError("invalid_objective_question")
            if question_type == "single_choice" and payload["answer"] not in options:
                raise ValueError("invalid_objective_answer")
        elif question_type == "true_false" and not isinstance(payload.get("answer"), bool):
            raise ValueError("invalid_objective_answer")
        elif question_type in {"short_answer", "essay"} and not str(payload.get("rubric", "")).strip():
            raise ValueError("missing_rubric")
        # Validate references before persistence so a client cannot create an
        # apparently valid question pointing at an orphan or wrong-course node.
        chapter_id = payload.get("chapter_id")
        node_id = payload.get("node_id")
        if chapter_id is not None or node_id is not None:
            if chapter_id is not None and (isinstance(chapter_id, bool) or not isinstance(chapter_id, int)):
                raise ValueError("invalid_question_reference")
            if node_id is not None and (not isinstance(node_id, str) or not node_id.strip()):
                raise ValueError("invalid_question_reference")
            with self.connect() as db:
                chapter = db.execute("SELECT id FROM chapters WHERE id=? AND course_id=1", (chapter_id,)).fetchone() if chapter_id is not None else None
                node = db.execute("SELECT id,chapter_id FROM knowledge_nodes WHERE id=?", (node_id,)).fetchone() if node_id else None
            if chapter_id is not None and not chapter:
                raise ValueError("invalid_question_reference")
            if node_id and not node:
                raise ValueError("invalid_question_reference")
            if node_id and chapter_id is not None and int(node["chapter_id"]) != int(chapter_id):
                raise ValueError("invalid_question_reference")
        question_id = "q-" + uuid.uuid4().hex
        with self._lock, self.connect() as db:
            db.execute(
                "INSERT INTO questions(id,course_id,chapter_id,node_id,question_type,prompt,options_json,answer_json,rubric,max_score,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (question_id, 1, payload.get("chapter_id"), payload.get("node_id"), question_type, prompt, json.dumps(payload.get("options", []), ensure_ascii=False), json.dumps(payload.get("answer"), ensure_ascii=False), payload.get("rubric", ""), maximum, uid),
            )
            db.commit()
        return {"id": question_id, **payload, "status": "draft", "created_by": uid}

    def publish_question(self, question_id: str, uid: str) -> dict[str, Any] | None:
        with self._lock, self.connect() as db:
            existing = db.execute("SELECT id,status,version,updated_at FROM questions WHERE id=? AND course_id=1", (question_id,)).fetchone()
            if not existing:
                return None
            if existing["status"] == "published":
                return dict(existing)
            changed = db.execute("UPDATE questions SET status='published',updated_at=CURRENT_TIMESTAMP WHERE id=? AND course_id=1", (question_id,)).rowcount
            if not changed:
                return None
            row = db.execute("SELECT id,status,version,updated_at FROM questions WHERE id=?", (question_id,)).fetchone()
            db.commit()
            return dict(row) if row else None

    def create_assignment(self, uid: str, payload: dict[str, Any]) -> dict[str, Any]:
        assignment_id = "a-" + uuid.uuid4().hex
        question_ids = [str(item) for item in payload.get("question_ids", [])]
        due_at = parse_due_at(payload.get("due_at"))
        try:
            allow_attempts = int(payload.get("allow_attempts", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid_attempt_limit") from exc
        if not 1 <= allow_attempts <= 10:
            raise ValueError("invalid_attempt_limit")
        with self._lock, self.connect() as db:
            placeholders = ",".join("?" for _ in question_ids) or "''"
            count = db.execute(f"SELECT COUNT(*) FROM questions WHERE id IN ({placeholders}) AND course_id=1 AND status='published'", question_ids).fetchone()[0] if question_ids else 0
            if count != len(question_ids) or not question_ids:
                raise ValueError("questions_not_published")
            db.execute("INSERT INTO assignments(id,course_id,title,question_ids_json,due_at,allow_attempts,created_by) VALUES(?,?,?,?,?,?,?)", (assignment_id, 1, payload["title"], json.dumps(question_ids), due_at.isoformat() if due_at else None, allow_attempts, uid))
            db.commit()
        return {"id": assignment_id, "title": payload["title"], "question_ids": question_ids, "due_at": due_at.isoformat() if due_at else None, "allow_attempts": allow_attempts, "status": "draft", "created_by": uid}

    def list_assignments(self, published_only: bool = False) -> list[dict[str, Any]]:
        with self.connect() as db:
            where = " WHERE course_id=1 AND status='published'" if published_only else " WHERE course_id=1"
            rows = db.execute("SELECT * FROM assignments" + where + " ORDER BY updated_at DESC").fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["question_ids"] = json.loads(item.pop("question_ids_json"))
                result.append(item)
            return result

    def teacher_submissions(self, assignment_id: str) -> list[dict[str, Any]]:
        """Return course-scoped submissions for staff review, never for students."""
        with self.connect() as db:
            rows = db.execute(
                "SELECT s.id,s.assignment_id,s.user_uid,s.attempt,s.status,s.created_at,s.answers_json "
                "FROM submissions s JOIN assignments a ON a.id=s.assignment_id "
                "WHERE s.assignment_id=? AND a.course_id=1 ORDER BY s.created_at,s.id",
                (assignment_id,),
            ).fetchall()
            result: list[dict[str, Any]] = []
            for row in rows:
                item = dict(row)
                item["answers"] = json.loads(item.pop("answers_json") or "{}")
                item["grades"] = [
                    dict(grade)
                    for grade in db.execute(
                        "SELECT id,question_id,score,max_score,feedback,source,reviewed_by,review_reason FROM grades WHERE submission_id=? ORDER BY question_id",
                        (row["id"],),
                    ).fetchall()
                ]
                item["score"] = round(sum(float(grade["score"] or 0) for grade in item["grades"]), 4) if item["grades"] else None
                result.append(item)
            return result

    def assignment(self, assignment_id: str, published_only: bool = False, user_uid: str | None = None) -> dict[str, Any] | None:
        with self.connect() as db:
            condition = " AND course_id=1"
            if published_only:
                condition += " AND status='published'"
            row = db.execute("SELECT * FROM assignments WHERE id=?" + condition, (assignment_id,)).fetchone()
            if not row:
                return None
            result = dict(row)
            question_ids = json.loads(result.pop("question_ids_json"))
            result["question_ids"] = question_ids
            questions = []
            for question_id in question_ids:
                columns = "id,course_id,chapter_id,node_id,question_type,prompt,options_json,max_score,status,version"
                if not published_only:
                    columns += ",answer_json,rubric"
                question = db.execute(f"SELECT {columns} FROM questions WHERE id=? AND course_id=1", (question_id,)).fetchone()
                if question:
                    item = dict(question)
                    if item.get("options_json"):
                        item["options"] = json.loads(item.pop("options_json"))
                    questions.append(item)
            result["questions"] = questions
            if user_uid and published_only:
                result["my_submissions"] = self._student_submission_results(db, assignment_id, user_uid)
            return result

    @staticmethod
    def _student_submission_results(db: sqlite3.Connection, assignment_id: str, user_uid: str) -> list[dict[str, Any]]:
        """Return only a student's own score/feedback, never answer keys or rubrics."""
        assignment = db.execute("SELECT question_ids_json FROM assignments WHERE id=? AND course_id=1", (assignment_id,)).fetchone()
        question_ids = json.loads(assignment["question_ids_json"]) if assignment else []
        placeholders = ",".join("?" for _ in question_ids) or "''"
        full_max = float(db.execute(f"SELECT COALESCE(SUM(max_score),0) FROM questions WHERE course_id=1 AND id IN ({placeholders})", question_ids).fetchone()[0])
        rows = db.execute(
            "SELECT id,attempt,status,created_at FROM submissions "
            "WHERE assignment_id=? AND user_uid=? ORDER BY attempt",
            (assignment_id, user_uid),
        ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            grades = db.execute(
                "SELECT question_id,score,max_score,feedback,source FROM grades "
                "WHERE submission_id=? ORDER BY question_id",
                (row["id"],),
            ).fetchall()
            item["grades"] = [dict(grade) for grade in grades]
            item["score"] = round(sum(float(grade["score"] or 0) for grade in grades), 4) if grades else None
            # The maximum is the assignment maximum, not only the items that
            # have already been graded; otherwise pending subjective items
            # would make a student's percentage look artificially complete.
            item["max_score"] = round(full_max, 4)
            item["needs_review"] = any(grade["source"] in {"agent_initial"} for grade in grades)
            results.append(item)
        return results

    def publish_assignment(self, assignment_id: str) -> dict[str, Any] | None:
        with self._lock, self.connect() as db:
            existing = db.execute("SELECT * FROM assignments WHERE id=? AND course_id=1", (assignment_id,)).fetchone()
            if not existing:
                return None
            if existing["status"] == "published":
                item = dict(existing)
                item["question_ids"] = json.loads(item.pop("question_ids_json"))
                return item
            changed = db.execute("UPDATE assignments SET status='published',updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='draft'", (assignment_id,)).rowcount
            row = db.execute("SELECT * FROM assignments WHERE id=?", (assignment_id,)).fetchone()
            db.commit()
            if not changed or not row:
                return None
            item = dict(row)
            item["question_ids"] = json.loads(item.pop("question_ids_json"))
            return item

    def submit(self, uid: str, assignment_id: str, answers: dict[str, Any], attempt: int, moodle_user_id: int | None = None) -> dict[str, Any]:
        submission_id = "sub-" + uuid.uuid4().hex
        with self._lock, self.connect() as db:
            assignment = db.execute("SELECT id,due_at,allow_attempts FROM assignments WHERE id=? AND course_id=1 AND status='published'", (assignment_id,)).fetchone()
            if not assignment:
                raise LookupError("assignment_not_found")
            used = db.execute("SELECT COUNT(*) FROM submissions WHERE assignment_id=? AND user_uid=?", (assignment_id, uid)).fetchone()[0]
            if used >= int(assignment["allow_attempts"]):
                raise ValueError("attempt_limit_reached")
            if attempt != used + 1:
                raise ValueError("invalid_attempt_number")
            due_at = parse_due_at(assignment["due_at"])
            if due_at and datetime.now(timezone.utc) > due_at:
                raise ValueError("deadline_passed")
            db.execute("INSERT INTO submissions(id,assignment_id,user_uid,moodle_user_id,answers_json,attempt) VALUES(?,?,?,?,?,?)", (submission_id, assignment_id, uid, moodle_user_id, json.dumps(answers, ensure_ascii=False), attempt))
            db.commit()
        return {"id": submission_id, "assignment_id": assignment_id, "attempt": attempt, "status": "submitted"}

    def submission_moodle_user_id(self, submission_id: str) -> int | None:
        with self.connect() as db:
            row = db.execute("SELECT moodle_user_id FROM submissions WHERE id=?", (submission_id,)).fetchone()
            return int(row["moodle_user_id"]) if row and row["moodle_user_id"] is not None else None

    def assignment_submission_ids(self, assignment_id: str) -> list[str]:
        with self.connect() as db:
            return [str(row["id"]) for row in db.execute("SELECT s.id FROM submissions s JOIN assignments a ON a.id=s.assignment_id WHERE s.assignment_id=? AND a.course_id=1 ORDER BY s.created_at,s.id", (assignment_id,))]

    def submission_context(self, submission_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT s.id,s.assignment_id,s.moodle_user_id FROM submissions s JOIN assignments a ON a.id=s.assignment_id WHERE s.id=? AND a.course_id=1", (submission_id,)).fetchone()
            return dict(row) if row else None

    def submission_totals(self, submission_id: str) -> tuple[float, float]:
        with self.connect() as db:
            row = db.execute(
                "SELECT s.assignment_id,COALESCE(SUM(g.score),0) score "
                "FROM submissions s LEFT JOIN grades g ON g.submission_id=s.id "
                "WHERE s.id=? GROUP BY s.id,s.assignment_id",
                (submission_id,),
            ).fetchone()
            if not row:
                return 0.0, 0.0
            assignment = db.execute("SELECT question_ids_json FROM assignments WHERE id=?", (row["assignment_id"],)).fetchone()
            question_ids = json.loads(assignment["question_ids_json"]) if assignment else []
            placeholders = ",".join("?" for _ in question_ids) or "''"
            maximum = db.execute(f"SELECT COALESCE(SUM(max_score),0) FROM questions WHERE id IN ({placeholders})", question_ids).fetchone()[0]
            return float(row["score"]), float(maximum)

    def grade_submission(self, submission_id: str, uid: str) -> dict[str, Any] | None:
        """Grade objective items deterministically; subjective items await review."""
        with self._lock, self.connect() as db:
            submission = db.execute("SELECT s.* FROM submissions s JOIN assignments a ON a.id=s.assignment_id WHERE s.id=? AND a.course_id=1", (submission_id,)).fetchone()
            if not submission:
                return None
            assignment = db.execute("SELECT question_ids_json FROM assignments WHERE id=?", (submission["assignment_id"],)).fetchone()
            answers = json.loads(submission["answers_json"])
            total = 0.0
            maximum = 0.0
            pending = 0
            for question_id in json.loads(assignment["question_ids_json"]):
                question = db.execute("SELECT * FROM questions WHERE id=?", (question_id,)).fetchone()
                if not question:
                    continue
                maximum += float(question["max_score"])
                answer = answers.get(question_id)
                if question["question_type"] in {"single_choice", "true_false", "multiple_choice"}:
                    expected = json.loads(question["answer_json"] or "null")
                    score = float(question["max_score"]) if answer == expected else 0.0
                    db.execute(
                        "INSERT INTO grades(id,submission_id,question_id,score,max_score,feedback,source) VALUES(?,?,?,?,?,?,?) "
                        "ON CONFLICT(submission_id,question_id) DO UPDATE SET score=excluded.score,max_score=excluded.max_score,feedback=excluded.feedback,source=excluded.source,updated_at=CURRENT_TIMESTAMP",
                        ("g-" + uuid.uuid4().hex, submission_id, question_id, score, question["max_score"], "客观题按固定答案评分", "deterministic"),
                    )
                    total += score
                else:
                    pending += 1
            db.commit()
            grade_rows = [dict(row) for row in db.execute("SELECT * FROM grades WHERE submission_id=? ORDER BY question_id", (submission_id,))]
            return {
                "submission_id": submission_id,
                "assignment_id": submission["assignment_id"],
                "moodle_user_id": submission["moodle_user_id"],
                "score": total,
                "max_score": maximum,
                "subjective_pending": pending,
                "grades": grade_rows,
                "status": "needs_review" if pending else "graded",
            }

    def review_grade(self, grade_id: str, uid: str, score: float, reason: str) -> dict[str, Any] | None:
        """Apply a teacher correction while retaining an immutable audit row."""
        with self._lock, self.connect() as db:
            grade = db.execute(
                "SELECT g.* FROM grades g JOIN submissions s ON s.id=g.submission_id "
                "JOIN assignments a ON a.id=s.assignment_id WHERE g.id=? AND a.course_id=1",
                (grade_id,),
            ).fetchone()
            if not grade:
                return None
            bounded = max(0.0, min(float(score), float(grade["max_score"])))
            db.execute("UPDATE grades SET score=?,source='teacher_review',reviewed_by=?,review_reason=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (bounded, uid, reason[:500], grade_id))
            db.execute("INSERT INTO grade_audit(id,grade_id,old_score,new_score,reason,changed_by) VALUES(?,?,?,?,?,?)", ("audit-" + uuid.uuid4().hex, grade_id, grade["score"], bounded, reason[:500], uid))
            db.commit()
            row = db.execute("SELECT * FROM grades WHERE id=?", (grade_id,)).fetchone()
            return dict(row) if row else None

    def subjective_item(self, submission_id: str, question_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT s.id submission_id,s.answers_json,q.id question_id,q.prompt,q.rubric,q.max_score,q.question_type "
                "FROM submissions s JOIN assignments a ON a.id=s.assignment_id "
                "JOIN questions q ON q.id=? AND q.course_id=1 "
                "WHERE s.id=? AND a.course_id=1 AND q.question_type IN ('short_answer','essay')",
                (question_id, submission_id),
            ).fetchone()
            if not row:
                return None
            result = dict(row)
            result["answer"] = json.loads(result.pop("answers_json")).get(question_id, "")
            return result

    def save_agent_grade(self, item: dict[str, Any], score: float, feedback: str) -> dict[str, Any]:
        bounded = max(0.0, min(float(score), float(item["max_score"])))
        with self._lock, self.connect() as db:
            db.execute(
                "INSERT INTO grades(id,submission_id,question_id,score,max_score,feedback,source) VALUES(?,?,?,?,?,?,?) "
                "ON CONFLICT(submission_id,question_id) DO UPDATE SET score=excluded.score,max_score=excluded.max_score,feedback=excluded.feedback,source=excluded.source,updated_at=CURRENT_TIMESTAMP",
                ("g-" + uuid.uuid4().hex, item["submission_id"], item["question_id"], bounded, item["max_score"], feedback[:2000], "agent_initial"),
            )
            db.commit()
            row = db.execute("SELECT * FROM grades WHERE submission_id=? AND question_id=?", (item["submission_id"], item["question_id"])).fetchone()
            return dict(row)

    def start_grading_task(self, assignment_id: str, uid: str) -> dict[str, Any] | None:
        """Create one auditable batch task and make each submission idempotent."""
        with self._lock, self.connect() as db:
            assignment = db.execute("SELECT id FROM assignments WHERE id=? AND course_id=1", (assignment_id,)).fetchone()
            if not assignment:
                return None
            submissions = db.execute("SELECT id FROM submissions WHERE assignment_id=? ORDER BY created_at,id", (assignment_id,)).fetchall()
            task_id = "task-grade-" + uuid.uuid4().hex
            db.execute("INSERT INTO grading_tasks(id,assignment_id,status,total,created_by) VALUES(?,?,?,?,?)", (task_id, assignment_id, "processing", len(submissions), uid))
            db.commit()
        completed = 0
        failed = 0
        for submission in submissions:
            try:
                if self.grade_submission(str(submission["id"]), uid):
                    completed += 1
                else:
                    failed += 1
            except (sqlite3.Error, ValueError, TypeError, json.JSONDecodeError):
                failed += 1
            with self._lock, self.connect() as db:
                db.execute("UPDATE grading_tasks SET completed=?,failed=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (completed, failed, task_id))
                db.commit()
        status = "needs_review" if failed == 0 else "partial_failure"
        with self._lock, self.connect() as db:
            db.execute("UPDATE grading_tasks SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, task_id))
            db.commit()
        return self.grading_task(task_id)

    def grading_task(self, task_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM grading_tasks WHERE id=?", (task_id,)).fetchone()
            return dict(row) if row else None

    def idempotent(self, uid: str, endpoint: str, key: str, body: Any) -> tuple[dict[str, Any] | None, bool]:
        digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        with self._lock, self.connect() as db:
            row = db.execute("SELECT request_hash,response_json FROM idempotency WHERE user_uid=? AND endpoint=? AND idem_key=?", (uid, endpoint, key)).fetchone()
            if row:
                if row["request_hash"] != digest:
                    raise ValueError("idempotency_key_reused")
                return json.loads(row["response_json"]), True
            return None, False

    def save_idempotent(self, uid: str, endpoint: str, key: str, body: Any, response: dict[str, Any]) -> None:
        digest = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        with self._lock, self.connect() as db:
            db.execute("INSERT OR IGNORE INTO idempotency(user_uid,endpoint,idem_key,request_hash,response_json) VALUES(?,?,?,?,?)", (uid, endpoint, key, digest, json.dumps(response, ensure_ascii=False)))
            db.commit()


store = CourseStore()
