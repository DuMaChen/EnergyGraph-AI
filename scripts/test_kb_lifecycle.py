#!/usr/bin/env python3
"""Verify the local knowledge-base version gates without calling Xingchen."""

from __future__ import annotations

import os
import hashlib
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MOCK_AUTH_MODE", "true")
os.environ.setdefault("MOCK_WORKFLOW_MODE", "true")
os.environ.setdefault("AGENT_UID_SALT", "kb-test-only")
os.environ.setdefault("COURSE_MANIFEST", str(ROOT / "course-data/normalized/manifest.json"))
os.environ.setdefault("GRAPH_BASELINE", str(ROOT / "course-data/normalized/graph-baseline.json"))


def main() -> None:
    with tempfile.NamedTemporaryFile(prefix="kb-lifecycle-", suffix=".db") as db_file, tempfile.TemporaryDirectory(prefix="kb-files-") as kb_dir:
        os.environ["COURSE_DB"] = db_file.name
        os.environ["KB_STORAGE_DIR"] = kb_dir
        import sys

        sys.path.insert(0, str(ROOT / "agent-adapter"))
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        student = {"x-dev-role": "student", "x-dev-user": "kb-student"}
        teacher = {"x-dev-role": "teacher", "x-dev-user": "kb-teacher"}
        # Use one real normalized course PDF so the release gate exercises the
        # same filename/hash mapping required in production.
        manifest = json.loads((ROOT / "course-data/normalized/manifest.json").read_text(encoding="utf-8"))
        pdf_entry = manifest["files"][0]
        pdf_name = str(pdf_entry["source_file"])
        pdf = (ROOT / "course-data/normalized" / str(pdf_entry["normalized_file"])).read_bytes()

        assert client.get("/api/knowledge-base/versions", headers=student).status_code == 403

        def create(name: str, workflow: str) -> str:
            response = client.post(
                "/api/knowledge-base/versions",
                headers={**teacher, "idempotency-key": f"create-{name}"},
                json={"version_name": name, "workflow_id": workflow, "manifest_sha256": "fixture"},
            )
            assert response.status_code == 201, response.text
            return response.json()["data"]["id"]

        def upload(version_id: str, filename: str = pdf_name) -> None:
            response = client.put(
                f"/api/knowledge-base/versions/{version_id}/files?filename={filename}",
                headers={**teacher, "idempotency-key": f"upload-{version_id}"},
                content=pdf,
            )
            assert response.status_code == 201, response.text

        def hit_test(version_id: str, case_id: str) -> None:
            response = client.post(
                f"/api/knowledge-base/versions/{version_id}/hit-tests",
                headers={**teacher, "idempotency-key": f"hit-{version_id}-{case_id}"},
                json={"case_id": case_id},
            )
            assert response.status_code == 200, response.text

        def status(version_id: str, value: str, key: str) -> dict:
            response = client.post(
                f"/api/knowledge-base/versions/{version_id}/status",
                headers={**teacher, "idempotency-key": key},
                json={"status": value},
            )
            assert response.status_code == 200, response.text
            return response.json()["data"]

        first = create("fixture-v1", "flow-v1")
        first_version = client.get("/api/knowledge-base/versions", headers=teacher).json()["data"]["items"][0]
        expected_manifest = hashlib.sha256((ROOT / "course-data/normalized/manifest.json").read_bytes()).hexdigest()
        assert first_version["manifest_sha256"] == expected_manifest
        # A draft cannot jump directly to published, even with a hit claim.
        blocked = client.post(
            f"/api/knowledge-base/versions/{first}/status",
            headers={**teacher, "idempotency-key": "blocked-publish"},
            json={"status": "published", "hit_status": "passed"},
        )
        assert blocked.status_code == 409
        upload(first)
        fake_pdf = client.put(
            f"/api/knowledge-base/versions/{first}/files?filename=fake.pdf",
            headers={**teacher, "idempotency-key": "upload-fake-pdf"},
            content=b"%PDF-1.7\nnot really a PDF\n",
        )
        assert fake_pdf.status_code == 422
        traversal = client.put(
            f"/api/knowledge-base/versions/{first}/files?filename=..%2Fescape.pdf",
            headers={**teacher, "idempotency-key": "upload-traversal"},
            content=pdf,
        )
        assert traversal.status_code == 422
        markdown = client.put(
            f"/api/knowledge-base/versions/{first}/files?filename=notes.md",
            headers={**teacher, "idempotency-key": "upload-markdown"},
            content=f"# 储能课程说明\n\n[来源文件：{pdf_name}；章节：第1章 概述；页码：1]\n".encode("utf-8"),
        )
        assert markdown.status_code == 201, markdown.text
        for case_id in ("qa-001", "qa-002", "qa-003"):
            hit_test(first, case_id)
        status(first, "tested", "v1-tested")
        status(first, "published", "v1-published")
        repeated = status(first, "published", "v1-published")
        assert repeated["id"] == first

        second = create("fixture-v2", "flow-v2")
        upload(second, pdf_name)
        for case_id in ("qa-001", "qa-002", "qa-003"):
            hit_test(second, case_id)
        status(second, "tested", "v2-tested")
        status(second, "published", "v2-published")

        rollback = client.post(
            f"/api/knowledge-base/versions/{first}/rollback",
            headers={**teacher, "idempotency-key": "rollback-v1"},
            json={"reason": "固定回归测试"},
        )
        assert rollback.status_code == 200, rollback.text
        assert rollback.json()["data"]["status"] == "published"

        versions = client.get("/api/knowledge-base/versions", headers=teacher).json()["data"]["items"]
        states = {item["version_name"]: item["status"] for item in versions}
        assert states == {"fixture-v1": "published", "fixture-v2": "archived"}

    print("KB_LIFECYCLE_OK")


if __name__ == "__main__":
    main()
