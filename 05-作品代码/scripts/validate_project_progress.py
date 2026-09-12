#!/usr/bin/env python3
"""Validate the project status ledger and redacted acceptance metadata."""

from __future__ import annotations

import json
import hashlib
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency failure is reported clearly
    raise SystemExit("PyYAML is required to validate PROJECT_PROGRESS.yaml") from exc


ROOT = Path(__file__).resolve().parents[1]
SENSITIVE_ENV_NAMES = ("TEST_API_KEY", "TEST_API_SECRET")
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", "dist", "build"}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
EVIDENCE_REF_RE = re.compile(
    r"(?:acceptance/frontend/[A-Za-z0-9._/-]+|"
    r"XUEXITONG_STYLE_FRONTEND_PLAN_V2\.md|PROJECT_PROGRESS\.yaml|PROJECT_STATUS\.md)"
)
T0_T6_REVIEW_ROW_RE = re.compile(
    r"^\|\s*(T[0-6])\s*\|\s*`?([A-Z_]+)`?\s*\|", re.MULTILINE
)
REQUIRED_METADATA_FIELDS = {
    "build",
    "run_id",
    "attempt",
    "authoritative_result",
    "supersedes",
    "environment",
    "t0_t6",
}
T0_T6_KEYS = tuple(f"T{index}" for index in range(7))
ALLOWED_T0_T6_STATUSES = {
    "PASS",
    "OBSERVED_PASS",
    "BLOCKED_INPUT",
    "BLOCKED_TEST_INFRA",
    "BLOCKED_DEPENDENCY",
    "NOT_RUN",
    "NOT_IMPLEMENTED",
    "NOT_APPLICABLE",
    "REVIEW_REQUIRED",
}


def local_env_values(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.is_file():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def artifact_paths() -> list[Path]:
    paths: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == ".env.test.local":
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 2 * 1024 * 1024:
            paths.append(path)
    return paths


def validate_redaction(errors: list[str], env_path: Path) -> None:
    values = local_env_values(env_path)
    artifacts = artifact_paths()
    for name in SENSITIVE_ENV_NAMES:
        value = values.get(name, "")
        if len(value) < 8:
            continue
        for artifact in artifacts:
            try:
                content = artifact.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if value in content:
                errors.append(
                    f"sensitive value for {name} appears in {artifact.relative_to(ROOT)}"
                )


def validate_working_tree_snapshot(errors: list[str], progress: object) -> None:
    """Ensure the recorded git status counts are still current."""
    # Deployment archives intentionally exclude .git. Keep the local snapshot
    # check strict by default, but allow an explicit server-side validation
    # mode that leaves all other ledger checks enabled.
    if os.environ.get("PROJECT_PROGRESS_REMOTE") == "1":
        return
    if not isinstance(progress, dict):
        return
    snapshot = progress.get("snapshot")
    working_tree = snapshot.get("working_tree") if isinstance(snapshot, dict) else None
    observed = working_tree.get("observed_git_status") if isinstance(working_tree, dict) else None
    required = {"captured_by", "tracked_modified_count", "untracked_count", "total_count"}
    if not isinstance(observed, dict) or not required.issubset(observed):
        errors.append("snapshot.working_tree.observed_git_status is missing required fields")
        return
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        errors.append(f"cannot read git status for snapshot: {type(error).__name__}")
        return
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    untracked = sum(line.startswith("??") for line in lines)
    tracked_modified = len(lines) - untracked
    actual = {
        "tracked_modified_count": tracked_modified,
        "untracked_count": untracked,
        "total_count": len(lines),
    }
    for field, value in actual.items():
        recorded = observed.get(field)
        if not isinstance(recorded, int) or isinstance(recorded, bool) or recorded != value:
            errors.append(
                f"snapshot git status {field} is stale: recorded={recorded!r} actual={value}"
            )


def validate_unique_progress_identifiers(errors: list[str], progress: object) -> None:
    """Reject duplicate scope paths and ledger identifiers."""
    if not isinstance(progress, dict):
        return

    def report_duplicates(label: str, values: list[object]) -> None:
        seen: set[object] = set()
        duplicates: list[object] = []
        for value in values:
            if value in seen and value not in duplicates:
                duplicates.append(value)
            seen.add(value)
        if duplicates:
            errors.append(f"{label} contains duplicate identifiers: {','.join(map(str, duplicates))}")

    plan_review = progress.get("plan_review")
    if isinstance(plan_review, dict):
        scope = plan_review.get("scope")
        if isinstance(scope, list):
            report_duplicates("plan_review.scope", scope)
        findings = plan_review.get("findings")
        if isinstance(findings, list):
            report_duplicates(
                "plan_review.findings",
                [item.get("id") for item in findings if isinstance(item, dict)],
            )
    for section in ("test_runs", "known_blockers"):
        entries = progress.get(section)
        if isinstance(entries, list):
            report_duplicates(
                section,
                [item.get("id") for item in entries if isinstance(item, dict)],
            )


def validate_evidence_references(errors: list[str], progress: object) -> int:
    if not isinstance(progress, dict):
        return 0
    runs = progress.get("test_runs")
    if not isinstance(runs, list):
        return 0
    checked = 0
    for index, run in enumerate(runs):
        if not isinstance(run, dict) or not isinstance(run.get("evidence"), str):
            continue
        references = EVIDENCE_REF_RE.findall(run["evidence"])
        for reference in references:
            reference = reference.rstrip(".,;)")
            checked += 1
            if not (ROOT / reference).exists():
                errors.append(f"test_runs[{index}] evidence path is missing: {reference}")
    return checked


def validate_build_metadata(errors: list[str], metadata_paths: list[Path]) -> int:
    """Validate stable identity fields used to distinguish current evidence."""
    seen_run_ids: dict[str, Path] = {}
    valid_count = 0
    for metadata_path in metadata_paths:
        relative = metadata_path.relative_to(ROOT)
        entry_valid = True
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative} cannot be parsed: {type(exc).__name__}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{relative} root must be an object")
            continue

        missing = sorted(REQUIRED_METADATA_FIELDS - metadata.keys())
        if missing:
            errors.append(f"{relative} missing metadata fields: {','.join(missing)}")
            continue

        build_dir = metadata_path.parent.name
        if metadata.get("build") != build_dir:
            errors.append(
                f"{relative} build does not match directory: {metadata.get('build')} != {build_dir}"
            )
            entry_valid = False
        run_id = metadata.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            errors.append(f"{relative} run_id must be a non-empty string")
            entry_valid = False
        elif run_id in seen_run_ids:
            errors.append(
                f"duplicate metadata run_id {run_id}: {seen_run_ids[run_id].relative_to(ROOT)} and {relative}"
            )
            entry_valid = False
        else:
            seen_run_ids[run_id] = metadata_path

        attempt = metadata.get("attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            errors.append(f"{relative} attempt must be a positive integer")
            entry_valid = False
        if not isinstance(metadata.get("authoritative_result"), bool):
            errors.append(f"{relative} authoritative_result must be boolean")
            entry_valid = False
        if not isinstance(metadata.get("supersedes"), list):
            errors.append(f"{relative} supersedes must be a list")
            entry_valid = False
        if not isinstance(metadata.get("environment"), str) or not metadata["environment"].strip():
            errors.append(f"{relative} environment must be a non-empty string")
            entry_valid = False
        t0_t6 = metadata.get("t0_t6")
        if not isinstance(t0_t6, dict) or set(t0_t6) != set(T0_T6_KEYS):
            errors.append(f"{relative} t0_t6 must contain exactly T0,T1,T2,T3,T4,T5,T6")
            entry_valid = False
        elif any(status not in ALLOWED_T0_T6_STATUSES for status in t0_t6.values()):
            errors.append(f"{relative} t0_t6 contains an unknown status")
            entry_valid = False
        if entry_valid:
            valid_count += 1
    return valid_count


def validate_metadata_evidence_consistency(errors: list[str], metadata_paths: list[Path]) -> None:
    """Ensure every standard evidence artifact identifies the same run."""
    for metadata_path in metadata_paths:
        relative = metadata_path.relative_to(ROOT)
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(metadata, dict) or not isinstance(metadata.get("run_id"), str):
            continue
        run_id = metadata["run_id"]
        build_dir = metadata_path.parent
        artifacts = {
            "scope.md": build_dir / "scope.md",
            "review.md": build_dir / "review.md",
            "test-output.txt": build_dir / "test-output.txt",
            "manual-acceptance.md": build_dir / "manual-acceptance.md",
            "rollback.md": build_dir / "rollback.md",
        }
        for name, artifact in artifacts.items():
            if not artifact.is_file():
                errors.append(f"{relative} missing evidence artifact: {artifact.relative_to(ROOT)}")
                continue
            try:
                content = artifact.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                errors.append(f"{relative} evidence artifact cannot be read: {artifact.relative_to(ROOT)}")
                continue
            if run_id not in content:
                errors.append(f"{relative} run_id missing from {artifact.relative_to(ROOT)}")
            if name == "review.md":
                review_statuses = {
                    layer: status for layer, status in T0_T6_REVIEW_ROW_RE.findall(content)
                }
                expected_statuses = metadata.get("t0_t6")
                if set(review_statuses) != set(T0_T6_KEYS):
                    missing = sorted(set(T0_T6_KEYS) - set(review_statuses))
                    extra = sorted(set(review_statuses) - set(T0_T6_KEYS))
                    errors.append(
                        f"{relative} T0-T6 review matrix mismatch: missing={','.join(missing) or '-'} extra={','.join(extra) or '-'}"
                    )
                elif isinstance(expected_statuses, dict):
                    for layer in T0_T6_KEYS:
                        if review_statuses[layer] != expected_statuses.get(layer):
                            errors.append(
                                f"{relative} {layer} status differs between metadata and review: "
                                f"{expected_statuses.get(layer)} != {review_statuses[layer]}"
                            )
            if name == "test-output.txt" and "exit code" not in content.lower():
                errors.append(f"{relative} exit code summary missing from {artifact.relative_to(ROOT)}")


def merge_history_sections(errors: list[str], progress: object) -> object:
    """Load immutable run/blocker history without replacing current status."""
    if not isinstance(progress, dict):
        return progress
    history = progress.get("history")
    if not isinstance(history, dict):
        return progress
    filename = history.get("file")
    expected_sha256 = history.get("sha256")
    if not isinstance(filename, str) or not filename.strip():
        errors.append("history.file must be a non-empty relative path")
        return progress
    relative = Path(filename)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append("history.file must stay inside the project root")
        return progress
    archive_path = ROOT / relative
    try:
        content = archive_path.read_bytes()
    except OSError as exc:
        errors.append(f"history archive cannot be read: {type(exc).__name__}")
        return progress
    actual_sha256 = hashlib.sha256(content).hexdigest()
    if not isinstance(expected_sha256, str) or expected_sha256 != actual_sha256:
        errors.append("history archive sha256 does not match PROJECT_PROGRESS.yaml")
        return progress
    try:
        archived = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"history archive cannot be parsed: {type(exc).__name__}")
        return progress
    if not isinstance(archived, dict):
        errors.append("history archive root must be a mapping")
        return progress
    merged = dict(progress)
    for section in ("test_runs", "known_blockers"):
        if section not in merged:
            merged[section] = archived.get(section)
    return merged


def main() -> int:
    errors: list[str] = []
    progress_path = ROOT / "PROJECT_PROGRESS.yaml"

    if not progress_path.is_file():
        errors.append("PROJECT_PROGRESS.yaml is missing")
        progress: object = None
    else:
        try:
            progress = yaml.safe_load(progress_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            errors.append(f"PROJECT_PROGRESS.yaml cannot be parsed: {type(exc).__name__}")
            progress = None

    if not isinstance(progress, dict):
        errors.append("PROJECT_PROGRESS.yaml root must be a mapping")
        progress = {}
    progress = merge_history_sections(errors, progress)

    plan = progress.get("plan")
    plan_file = plan.get("file") if isinstance(plan, dict) else None
    if not isinstance(plan_file, str) or not (ROOT / plan_file).is_file():
        errors.append("configured plan file is missing")

    latest_frontend = progress.get("latest_frontend_revalidation")
    required_latest_fields = {"date", "build", "status", "results", "open_release_gates"}
    if not isinstance(latest_frontend, dict) or not required_latest_fields.issubset(latest_frontend):
        errors.append("latest_frontend_revalidation is missing required fields")
    elif not isinstance(latest_frontend.get("results"), dict):
        errors.append("latest_frontend_revalidation.results must be a mapping")

    status = progress.get("status")
    gates = progress.get("gates")
    gate_map = {
        gate.get("id"): gate
        for gate in gates or []
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    current_gate = status.get("current_gate") if isinstance(status, dict) else None
    current_gate_status = status.get("current_gate_status") if isinstance(status, dict) else None
    if not isinstance(current_gate, str) or current_gate not in gate_map:
        errors.append("status.current_gate does not reference a configured gate")
    else:
        gate_status = gate_map[current_gate].get("status")
        if gate_status != current_gate_status:
            errors.append("status.current_gate_status differs from the configured gate status")
        evidence_dir = ROOT / "acceptance" / "frontend" / current_gate
        if not evidence_dir.is_dir():
            errors.append(f"current gate evidence directory is missing: {current_gate}")

    blockers = progress.get("known_blockers")
    required_blocker_fields = {"id", "severity", "status", "description", "required_action"}
    if not isinstance(blockers, list) or not blockers:
        errors.append("known_blockers must be a non-empty list")
    else:
        for index, blocker in enumerate(blockers):
            if not isinstance(blocker, dict) or not required_blocker_fields.issubset(blocker):
                errors.append(f"known_blockers[{index}] is missing required fields")

    env_path = ROOT / ".env.test.local"
    if env_path.exists():
        mode = stat.S_IMODE(os.stat(env_path).st_mode)
        if mode != 0o600:
            errors.append(f".env.test.local must have mode 600, found {mode:o}")
    validate_redaction(errors, env_path)
    validate_working_tree_snapshot(errors, progress)
    validate_unique_progress_identifiers(errors, progress)
    evidence_reference_count = validate_evidence_references(errors, progress)

    metadata_paths = sorted((ROOT / "acceptance" / "frontend").glob("BUILD-*/metadata.json"))
    if not metadata_paths:
        errors.append("no frontend acceptance metadata files found")
    valid_metadata_count = validate_build_metadata(errors, metadata_paths)
    validate_metadata_evidence_consistency(errors, metadata_paths)
    for metadata_path in metadata_paths:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(metadata, dict) and (
            metadata.get("sensitive_values_recorded") is True
            or metadata.get("secrets_recorded") is True
        ):
            errors.append(f"sensitive recording flag is true: {metadata_path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"PROJECT_PROGRESS_VALIDATION_ERROR {error}", file=sys.stderr)
        return 1

    print(
        "PROJECT_PROGRESS_VALIDATION_OK "
        f"gate={current_gate} metadata={valid_metadata_count} blockers={len(blockers)} "
        f"evidence_refs={evidence_reference_count} redaction_scan=PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
