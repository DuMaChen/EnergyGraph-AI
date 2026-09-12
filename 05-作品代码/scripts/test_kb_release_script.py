#!/usr/bin/env python3
"""Unit tests for the KB release driver's pure decision helpers.

Covers the release-plan gate without touching the network: a version can
only advance to published when files are uploaded, the manifest is valid,
the Workflow ID is bound and all three golden hit-tests passed.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kb_release import SOURCE_MARKER, release_plan  # noqa: E402


class ReleasePlanTest(unittest.TestCase):
    def base_version(self, status: str = "failed", workflow_id: str = "wf", source_count: int = 20) -> dict:
        return {"id": "kb-test", "status": status, "workflow_id": workflow_id,
                "source_count": source_count}

    def test_blocked_when_files_missing(self) -> None:
        plan = release_plan(self.base_version(source_count=0), 3, True)
        self.assertEqual(plan, "BLOCKED_MANIFEST_OR_FILES_MISSING")

    def test_blocked_when_manifest_invalid(self) -> None:
        plan = release_plan(self.base_version(), 3, False)
        self.assertEqual(plan, "BLOCKED_MANIFEST_OR_FILES_MISSING")

    def test_blocked_when_workflow_not_bound(self) -> None:
        plan = release_plan(self.base_version(workflow_id=None), 3, True)
        self.assertEqual(plan, "BLOCKED_WORKFLOW_ID_MISSING")

    def test_blocked_when_hits_not_passed(self) -> None:
        plan = release_plan(self.base_version(), 2, True)
        self.assertEqual(plan, "BLOCKED_HIT_TESTS_NOT_PASSED")

    def test_failed_advances_through_processing(self) -> None:
        plan = release_plan(self.base_version(status="failed"), 3, True)
        self.assertEqual(plan, ["processing", "tested", "published"])

    def test_processing_advances_to_published(self) -> None:
        plan = release_plan(self.base_version(status="processing"), 3, True)
        self.assertEqual(plan, ["processing", "tested", "published"])

    def test_published_is_terminal(self) -> None:
        plan = release_plan(self.base_version(status="published"), 3, True)
        self.assertEqual(plan, [])

    def test_unexpected_status_is_blocked(self) -> None:
        plan = release_plan(self.base_version(status="draft"), 3, True)
        self.assertTrue(plan.startswith("BLOCKED_UNEXPECTED_STATUS:"))


class SourceMarkerTest(unittest.TestCase):
    def test_matches_required_marker_shape(self) -> None:
        text = "答案内容[来源文件：3.1 抽水蓄能电站的组成及工作原理.pdf；章节：第3章 电力储能系统的组成及工作原理；页码：12]结束"
        self.assertEqual(len(SOURCE_MARKER.findall(text)), 1)

    def test_ignores_answer_without_marker(self) -> None:
        text = "这是一个没有引用标记的普通回答。"
        self.assertEqual(len(SOURCE_MARKER.findall(text)), 0)


if __name__ == "__main__":
    unittest.main()
