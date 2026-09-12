from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_project_progress import (
    validate_build_metadata,
    validate_evidence_references,
    merge_history_sections,
    validate_redaction,
    validate_metadata_evidence_consistency,
    validate_unique_progress_identifiers,
    validate_working_tree_snapshot,
)


class ProjectProgressValidationTests(unittest.TestCase):
    def test_history_archive_merges_only_runs_and_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "PROJECT_PROGRESS_HISTORY.yaml"
            content = (
                "status:\n  overall: stale\n"
                "test_runs:\n  - id: RUN-1\n"
                "known_blockers:\n  - id: BLOCK-1\n"
            ).encode("utf-8")
            archive.write_bytes(content)
            import hashlib

            current = {
                "status": {"overall": "current"},
                "history": {
                    "file": archive.name,
                    "sha256": hashlib.sha256(content).hexdigest(),
                },
            }
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                merged = merge_history_sections(errors, current)
            self.assertEqual(errors, [])
            self.assertEqual(merged["status"], {"overall": "current"})
            self.assertEqual(merged["test_runs"], [{"id": "RUN-1"}])
            self.assertEqual(merged["known_blockers"], [{"id": "BLOCK-1"}])

    def test_redaction_scan_rejects_secret_in_text_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env_path = root / ".env.test.local"
            env_path.write_text("TEST_API_KEY=fixture-key-that-must-not-leak\n", encoding="utf-8")
            evidence = root / "acceptance" / "frontend" / "BUILD-090"
            evidence.mkdir(parents=True)
            (evidence / "test-output.txt").write_text(
                "accidental TEST_API_KEY=fixture-key-that-must-not-leak\n", encoding="utf-8"
            )
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                validate_redaction(errors, env_path)
            self.assertEqual(len(errors), 1)
            self.assertIn("TEST_API_KEY", errors[0])
            self.assertIn("test-output.txt", errors[0])
            self.assertNotIn("fixture-key-that-must-not-leak", errors[0])

    def test_evidence_reference_check_rejects_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            errors: list[str] = []
            progress = {
                "test_runs": [
                    {"evidence": "acceptance/frontend/BUILD-090/missing.txt"},
                ]
            }
            with patch("scripts.validate_project_progress.ROOT", root):
                checked = validate_evidence_references(errors, progress)
            self.assertEqual(checked, 1)
            self.assertEqual(
                errors,
                ["test_runs[0] evidence path is missing: acceptance/frontend/BUILD-090/missing.txt"],
            )

    def test_build_metadata_requires_unique_run_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "acceptance" / "frontend" / "BUILD-090" / "metadata.json"
            second = root / "acceptance" / "frontend" / "BUILD-100" / "metadata.json"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            metadata = {
                "build": "BUILD-090",
                "run_id": "same-run",
                "attempt": 1,
                "authoritative_result": True,
                "supersedes": [],
                "environment": "local",
                "t0_t6": {f"T{i}": "PASS" for i in range(7)},
            }
            first.write_text(json.dumps(metadata), encoding="utf-8")
            metadata["build"] = "BUILD-100"
            second.write_text(json.dumps(metadata), encoding="utf-8")
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                valid = validate_build_metadata(errors, [first, second])
            self.assertEqual(valid, 1)
            self.assertTrue(any("duplicate metadata run_id same-run" in error for error in errors))

    def test_build_metadata_rejects_missing_identity_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "acceptance" / "frontend" / "BUILD-020" / "metadata.json"
            metadata_path.parent.mkdir(parents=True)
            metadata_path.write_text('{"build":"BUILD-020"}', encoding="utf-8")
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                valid = validate_build_metadata(errors, [metadata_path])
            self.assertEqual(valid, 0)
            self.assertEqual(
                errors,
                [
                    "acceptance/frontend/BUILD-020/metadata.json missing metadata fields: "
                    "attempt,authoritative_result,environment,run_id,supersedes,t0_t6"
                ],
            )

    def test_build_metadata_accepts_blocked_test_infra(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = root / "acceptance" / "frontend" / "BUILD-060" / "metadata.json"
            metadata_path.parent.mkdir(parents=True)
            metadata_path.write_text(
                json.dumps(
                    {
                        "build": "BUILD-060",
                        "run_id": "activity-lifecycle-run",
                        "attempt": 1,
                        "authoritative_result": True,
                        "supersedes": [],
                        "environment": "local-browser-infrastructure-blocked",
                        "t0_t6": {
                            "T0": "PASS",
                            "T1": "PASS",
                            "T2": "PASS",
                            "T3": "OBSERVED_PASS",
                            "T4": "BLOCKED_TEST_INFRA",
                            "T5": "BLOCKED_INPUT",
                            "T6": "REVIEW_REQUIRED",
                        },
                    }
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                valid = validate_build_metadata(errors, [metadata_path])
            self.assertEqual(valid, 1)
            self.assertEqual(errors, [])

    def test_metadata_evidence_requires_shared_run_id_and_t0_t6_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_dir = root / "acceptance" / "frontend" / "BUILD-090"
            build_dir.mkdir(parents=True)
            metadata_path = build_dir / "metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "build": "BUILD-090",
                        "run_id": "shared-run",
                        "attempt": 1,
                        "authoritative_result": True,
                        "supersedes": [],
                        "environment": "local",
                        "t0_t6": {f"T{i}": "PASS" for i in range(7)},
                    }
                ),
                encoding="utf-8",
            )
            (build_dir / "review.md").write_text(
                "shared-run\n" + "\n".join(f"| T{i} | `PASS` |" for i in range(6)),
                encoding="utf-8",
            )
            (build_dir / "test-output.txt").write_text("wrong-run", encoding="utf-8")
            (build_dir / "manual-acceptance.md").write_text("shared-run", encoding="utf-8")
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                validate_metadata_evidence_consistency(errors, [metadata_path])
            self.assertIn(
                "acceptance/frontend/BUILD-090/metadata.json run_id missing from acceptance/frontend/BUILD-090/test-output.txt",
                errors,
            )
            self.assertIn(
                "acceptance/frontend/BUILD-090/metadata.json T0-T6 review matrix mismatch: missing=T6 extra=-",
                errors,
            )
            self.assertIn(
                "acceptance/frontend/BUILD-090/metadata.json exit code summary missing from acceptance/frontend/BUILD-090/test-output.txt",
                errors,
            )

    def test_metadata_evidence_requires_scope_and_rollback_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_dir = root / "acceptance" / "frontend" / "BUILD-090"
            build_dir.mkdir(parents=True)
            metadata_path = build_dir / "metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "build": "BUILD-090",
                        "run_id": "shared-run",
                        "attempt": 1,
                        "authoritative_result": True,
                        "supersedes": [],
                        "environment": "local",
                        "t0_t6": {f"T{i}": "PASS" for i in range(7)},
                    }
                ),
                encoding="utf-8",
            )
            (build_dir / "review.md").write_text(
                "shared-run\n" + "\n".join(f"| T{i} | `PASS` |" for i in range(7)),
                encoding="utf-8",
            )
            (build_dir / "test-output.txt").write_text(
                "shared-run\nExit code summary: PASS", encoding="utf-8"
            )
            (build_dir / "manual-acceptance.md").write_text("shared-run", encoding="utf-8")
            errors: list[str] = []
            with patch("scripts.validate_project_progress.ROOT", root):
                validate_metadata_evidence_consistency(errors, [metadata_path])
            self.assertIn(
                "acceptance/frontend/BUILD-090/metadata.json missing evidence artifact: acceptance/frontend/BUILD-090/scope.md",
                errors,
            )
            self.assertIn(
                "acceptance/frontend/BUILD-090/metadata.json missing evidence artifact: acceptance/frontend/BUILD-090/rollback.md",
                errors,
            )

    def test_working_tree_snapshot_rejects_stale_counts(self) -> None:
        errors: list[str] = []
        progress = {
            "snapshot": {
                "working_tree": {
                    "observed_git_status": {
                        "captured_by": "git status --short",
                        "tracked_modified_count": 0,
                        "untracked_count": 0,
                        "total_count": 0,
                    }
                }
            }
        }
        git_status = subprocess.CompletedProcess(
            args=["git", "status", "--short"],
            returncode=0,
            stdout=" M tracked.py\n?? untracked.txt\n",
            stderr="",
        )
        with patch("scripts.validate_project_progress.ROOT", Path.cwd()):
            with patch("scripts.validate_project_progress.subprocess.run", return_value=git_status):
                validate_working_tree_snapshot(errors, progress)
        self.assertTrue(any("snapshot git status" in error for error in errors))

    def test_working_tree_snapshot_skips_only_for_explicit_remote_mode(self) -> None:
        errors: list[str] = []
        progress = {
            "snapshot": {
                "working_tree": {
                    "observed_git_status": {
                        "captured_by": "git status --short",
                        "tracked_modified_count": 0,
                        "untracked_count": 0,
                        "total_count": 0,
                    }
                }
            }
        }
        with patch.dict(os.environ, {"PROJECT_PROGRESS_REMOTE": "1"}):
            with patch("scripts.validate_project_progress.ROOT", Path("/nonexistent")):
                validate_working_tree_snapshot(errors, progress)
        self.assertEqual(errors, [])

    def test_progress_identifiers_reject_duplicates(self) -> None:
        progress = {
            "plan_review": {
                "scope": ["README.md", "README.md"],
                "findings": [{"id": "F-1"}, {"id": "F-1"}],
            },
            "test_runs": [{"id": "RUN-1"}, {"id": "RUN-1"}],
            "known_blockers": [{"id": "B-1"}, {"id": "B-1"}],
        }
        errors: list[str] = []
        validate_unique_progress_identifiers(errors, progress)
        self.assertIn("plan_review.scope contains duplicate identifiers: README.md", errors)
        self.assertIn("plan_review.findings contains duplicate identifiers: F-1", errors)
        self.assertIn("test_runs contains duplicate identifiers: RUN-1", errors)
        self.assertIn("known_blockers contains duplicate identifiers: B-1", errors)


if __name__ == "__main__":
    unittest.main()
