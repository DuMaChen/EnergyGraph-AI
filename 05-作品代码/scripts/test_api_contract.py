#!/usr/bin/env python3
"""Static contract audit for required plan endpoints.

This runs on a developer machine without FastAPI installed; container tests
still exercise the application at runtime when dependencies are available.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]


def routes() -> set[str]:
    tree = ast.parse((ROOT / "agent-adapter/app/main.py").read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
                result.add(decorator.args[0].value)
    return result


def main() -> int:
    actual = routes()
    required = {
        "/health", "/api/admin/status", "/api/course/session/open", "/api/course-agent/chat",
        "/api/knowledge-graph/chapters", "/api/knowledge-graph/nodes/{node_id}",
        "/api/knowledge-graph/nodes/{node_id}/neighbors", "/api/knowledge-graph/paths",
        "/api/textbook/resources", "/api/textbook/resources/{resource_id}",
        "/api/textbook/resources/{resource_id}/pages/{page_number}",
        "/api/knowledge-points/{node_id}/resources",
        "/api/student/learning-profile", "/api/student/recommendations",
        "/api/student/learning-diagnosis", "/api/teacher/students/{student_uid}/learning-profile", "/api/student/assignments",
        "/api/student/assignments/{assignment_id}/submit", "/api/teacher/questions",
        "/api/teacher/assignments/{assignment_id}/submissions",
        "/api/teacher/questions/{question_id}/publish", "/api/teacher/assignments/{assignment_id}/publish",
        "/api/teacher/assignments", "/api/teacher/assignments/{assignment_id}/grade",
        "/api/teacher/assignments/{assignment_id}/grading-status", "/api/teacher/submissions/{submission_id}/grade",
        "/api/teacher/grade-items/{grade_id}", "/api/teacher/submissions/{submission_id}/subjective/{question_id}/agent-review", "/api/knowledge-base/versions",
        "/api/knowledge-base/versions/{version_id}/status",
        "/api/knowledge-base/versions/{version_id}/files",
        "/api/knowledge-base/versions/{version_id}/hit-tests",
        "/api/knowledge-base/versions/{version_id}/rollback",
    }
    missing = sorted(required - actual)
    if missing:
        raise SystemExit("missing routes: " + ", ".join(missing))
    env = (ROOT / "deploy/.env.example").read_text(encoding="utf-8")
    for variable in ("XINGCHEN_WORKFLOW_URL", "XINGCHEN_FLOW_ID", "XINGCHEN_API_KEY", "XINGCHEN_API_SECRET", "AGENT_UID_SALT", "AGENT_BRIDGE_TOKEN"):
        if f"{variable}=" not in env:
            raise SystemExit(f"missing env variable: {variable}")
    for caddy_path in (ROOT / "deploy/caddy/Caddyfile", ROOT / "deploy/caddy/Caddyfile.https"):
        caddy = caddy_path.read_text(encoding="utf-8")
        if "path /api/*" not in caddy:
            raise SystemExit(f"{caddy_path.name} must route the complete /api/* prefix to the Adapter")
    print(f"API_CONTRACT_OK routes={len(actual)}")


if __name__ == "__main__":
    main()
