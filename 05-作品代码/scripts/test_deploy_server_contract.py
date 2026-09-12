#!/usr/bin/env python3
"""Check that deployment archives cannot include local environment secrets."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeployServerContractTests(unittest.TestCase):
    def test_archive_excludes_local_environment_files(self) -> None:
        script = (ROOT / "scripts/deploy_server.sh").read_text(encoding="utf-8")
        self.assertIn("--exclude='./deploy/.env'", script)
        self.assertIn("--exclude='./.env.test.local'", script)
        self.assertIn("--exclude='*/.env.test.local'", script)

    def test_material_sync_remains_manifest_scoped(self) -> None:
        script = (ROOT / "scripts/deploy_server.sh").read_text(encoding="utf-8")
        self.assertIn("EXPECTED_MATERIAL_FILES", script)
        self.assertIn("MATERIAL_NAMES=(manifest.json graph-baseline.json)", script)
        self.assertIn("tar czf - -C \"$COURSE_MATERIAL_SOURCE\" \"${MATERIAL_NAMES[@]}\"", script)


if __name__ == "__main__":
    result = unittest.main(exit=False)
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
