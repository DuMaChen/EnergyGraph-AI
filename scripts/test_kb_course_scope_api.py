#!/usr/bin/env python3
"""Verify knowledge-base release state stays inside the authenticated course."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]


def data(response: httpx.Response, expected_status: int) -> dict:
    assert response.status_code == expected_status, response.text
    body = response.json()
    assert body.get("status") == "ok", body
    return body["data"]


async def run() -> None:
    manifest_path = ROOT / "course-data/normalized/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = manifest["files"][0]
    source_name = str(source["source_file"])
    marker = f"[来源文件：{source_name}；章节：{source['chapter']}；页码：1]"

    with tempfile.TemporaryDirectory(prefix="kb-course-scope-") as directory:
        os.environ.update({
            "COURSE_DB": str(Path(directory) / "course.db"),
            "COURSE_MANIFEST": str(manifest_path),
            "GRAPH_BASELINE": str(ROOT / "course-data/normalized/graph-baseline.json"),
            "KB_STORAGE_DIR": str(Path(directory) / "kb-files"),
            "MOCK_AUTH_MODE": "true",
            "MOCK_WORKFLOW_MODE": "true",
            "AGENT_UID_SALT": "kb-course-scope-test-only",
            "COURSE_ID": "2",
            "MOCK_COURSE_ID": "2",
        })
        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from app.main import app, validate_sources

        teacher = {"x-dev-role": "teacher", "x-dev-user": "kb-scope-teacher"}
        admin = {"x-dev-role": "admin", "x-dev-user": "kb-scope-admin"}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            version = data(
                await client.post(
                    "/api/knowledge-base/versions",
                    headers={**teacher, "Idempotency-Key": "kb-scope-create-course-2"},
                    json={"version_name": "course-2-kb", "workflow_id": "flow-course-2"},
                ),
                201,
            )
            version_id = version["id"]
            data(
                await client.put(
                    f"/api/knowledge-base/versions/{version_id}/files?filename=notes.md",
                    headers={**teacher, "Idempotency-Key": "kb-scope-upload-course-2"},
                    content=f"# 课程二知识库\n\n{marker}\n".encode("utf-8"),
                ),
                201,
            )
            assert [item["id"] for item in data(await client.get("/api/knowledge-base/versions", headers=teacher), 200)["items"]] == [version_id]
            assert len(data(await client.get(f"/api/knowledge-base/versions/{version_id}/files", headers=teacher), 200)["items"]) == 1

            for case_id in ("qa-001", "qa-002", "qa-003"):
                data(
                    await client.post(
                        f"/api/knowledge-base/versions/{version_id}/hit-tests",
                        headers={**teacher, "Idempotency-Key": f"kb-scope-hit-course-2-{case_id}"},
                        json={"case_id": case_id},
                    ),
                    200,
                )
            data(
                await client.post(
                    f"/api/knowledge-base/versions/{version_id}/status",
                    headers={**teacher, "Idempotency-Key": "kb-scope-tested-course-2"},
                    json={"status": "tested"},
                ),
                200,
            )
            data(
                await client.post(
                    f"/api/knowledge-base/versions/{version_id}/status",
                    headers={**teacher, "Idempotency-Key": "kb-scope-published-course-2"},
                    json={"status": "published"},
                ),
                200,
            )
            scoped_source = validate_sources(marker, 2)
            assert scoped_source and scoped_source[0]["kb_version_id"] == version_id
            audit_course_2 = data(await client.get("/api/admin/audit-log", headers=admin), 200)
            assert any(item["object_id"] == version_id for item in audit_course_2["items"])

            os.environ["COURSE_ID"] = "1"
            os.environ["MOCK_COURSE_ID"] = "1"
            assert data(await client.get("/api/knowledge-base/versions", headers=teacher), 200)["items"] == []
            assert data(await client.get(f"/api/knowledge-base/versions/{version_id}/files", headers=teacher), 200)["items"] == []
            assert data(await client.get(f"/api/knowledge-base/versions/{version_id}/hit-tests", headers=teacher), 200)["items"] == []
            assert (await client.post(
                f"/api/knowledge-base/versions/{version_id}/status",
                headers={**teacher, "Idempotency-Key": "kb-scope-cross-status"},
                json={"status": "archived"},
            )).status_code == 404
            assert (await client.post(
                f"/api/knowledge-base/versions/{version_id}/hit-tests",
                headers={**teacher, "Idempotency-Key": "kb-scope-cross-hit"},
                json={"case_id": "qa-001"},
            )).status_code == 404
            assert (await client.post(
                f"/api/knowledge-base/versions/{version_id}/rollback",
                headers={**teacher, "Idempotency-Key": "kb-scope-cross-rollback"},
                json={"reason": "跨课程隔离测试"},
            )).status_code == 404
            assert validate_sources(marker, 1)[0]["kb_version_id"] == "local-manifest"
            status_course_1 = data(await client.get("/api/admin/status", headers=admin), 200)
            assert status_course_1["published_kb"] is None
            audit_course_1 = data(await client.get("/api/admin/audit-log", headers=admin), 200)
            assert not any(item["object_id"] == version_id for item in audit_course_1["items"])

            os.environ["COURSE_ID"] = "2"
            os.environ["MOCK_COURSE_ID"] = "2"
            versions = data(await client.get("/api/knowledge-base/versions", headers=teacher), 200)["items"]
            assert len(versions) == 1 and versions[0]["id"] == version_id and versions[0]["status"] == "published"
            assert len(data(await client.get(f"/api/knowledge-base/versions/{version_id}/hit-tests", headers=teacher), 200)["items"]) == 3

    for name in (
        "COURSE_DB", "COURSE_MANIFEST", "GRAPH_BASELINE", "KB_STORAGE_DIR",
        "MOCK_AUTH_MODE", "MOCK_WORKFLOW_MODE", "AGENT_UID_SALT", "COURSE_ID", "MOCK_COURSE_ID",
    ):
        os.environ.pop(name, None)
    print("KB_COURSE_SCOPE_API_OK")


if __name__ == "__main__":
    asyncio.run(run())
