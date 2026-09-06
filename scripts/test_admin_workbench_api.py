#!/usr/bin/env python3
"""BUILD-080 isolated API acceptance for admin, KB, audit and recovery views."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "admin-workbench-api-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def payload(response: httpx.Response, status: int) -> dict:
    assert response.status_code == status, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def run() -> None:
    with tempfile.TemporaryDirectory(prefix="admin-workbench-api-") as directory:
        os.environ["COURSE_DB"] = str(Path(directory) / "course.db")
        os.environ["KB_STORAGE_DIR"] = str(Path(directory) / "kb-files")
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app

        admin = {"x-dev-role": "admin", "x-dev-user": "build080-admin"}
        student = {"x-dev-role": "student", "x-dev-user": "build080-student"}
        manifest = json.loads((ROOT / "course-data/normalized/manifest.json").read_text(encoding="utf-8"))
        source_name = str(manifest["files"][0]["source_file"])
        markdown = f"# 课程知识库测试\n\n[来源文件：{source_name}；章节：第1章 概述；页码：1]\n".encode("utf-8")

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/admin/status", headers=student)).status_code == 403
            status = payload(await client.get("/api/admin/status", headers=admin), 200)
            status_text = json.dumps(status).lower()
            assert "api_key" not in status_text and "secret" not in status_text
            assert (await client.get("/api/admin/audit-log", headers=student)).status_code == 403
            assert (await client.get("/api/admin/backup/status", headers=student)).status_code == 403
            backup = payload(await client.get("/api/admin/backup/status", headers=admin), 200)
            assert backup["secrets_excluded"] is True

            created = payload(await client.post(
                "/api/knowledge-base/versions",
                headers={**admin, "idempotency-key": "build080-create-v1"},
                json={"version_name": "BUILD-080 知识库 v1", "workflow_id": "workflow-fixture-v1"},
            ), 201)
            version_id = created["id"]
            expected_digest = hashlib.sha256((ROOT / "course-data/normalized/manifest.json").read_bytes()).hexdigest()
            assert created["manifest_sha256"] == expected_digest

            invalid = await client.put(
                f"/api/knowledge-base/versions/{version_id}/files?filename=../escape.md",
                headers={**admin, "idempotency-key": "build080-invalid-path"},
                content=markdown,
            )
            assert invalid.status_code == 422
            upload = payload(await client.put(
                f"/api/knowledge-base/versions/{version_id}/files?filename=notes.md",
                headers={**admin, "idempotency-key": "build080-upload-v1"},
                content=markdown,
            ), 201)
            duplicate = payload(await client.put(
                f"/api/knowledge-base/versions/{version_id}/files?filename=notes.md",
                headers={**admin, "idempotency-key": "build080-upload-v1"},
                content=markdown,
            ), 200)
            assert duplicate["id"] == upload["id"]

            for case_id in ("qa-001", "qa-002", "qa-003"):
                result = await client.post(
                    f"/api/knowledge-base/versions/{version_id}/hit-tests",
                    headers={**admin, "idempotency-key": "build080-hit-" + case_id},
                    json={"case_id": case_id},
                )
                assert result.status_code == 200, result.text

            tested = payload(await client.post(
                f"/api/knowledge-base/versions/{version_id}/status",
                headers={**admin, "idempotency-key": "build080-status-tested"},
                json={"status": "tested"},
            ), 200)
            assert tested["status"] == "tested"
            published = payload(await client.post(
                f"/api/knowledge-base/versions/{version_id}/status",
                headers={**admin, "idempotency-key": "build080-status-published"},
                json={"status": "published"},
            ), 200)
            assert published["status"] == "published"

            versions = payload(await client.get("/api/knowledge-base/versions", headers=admin), 200)
            assert versions["items"][0]["status"] == "published"
            audits = payload(await client.get("/api/admin/audit-log?page_size=100", headers=admin), 200)["items"]
            assert any(item["action"] == "create" and item["object_type"] == "knowledge_base" for item in audits)
            assert any(item["action"] == "status:published" and item["request_id"] for item in audits)
            assert all("authorization" not in json.dumps(item).lower() for item in audits)

    print("ADMIN_WORKBENCH_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
