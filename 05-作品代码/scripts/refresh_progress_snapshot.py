#!/usr/bin/env python3
"""Refresh only the git-status counts in PROJECT_PROGRESS.yaml."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_PATH = ROOT / "PROJECT_PROGRESS.yaml"
COUNT_FIELDS = (
    "tracked_modified_count",
    "untracked_count",
    "total_count",
)


def status_counts(status_output: str) -> dict[str, int]:
    lines = [line for line in status_output.splitlines() if line.strip()]
    untracked = sum(line.startswith("??") for line in lines)
    tracked_modified = len(lines) - untracked
    return {
        "tracked_modified_count": tracked_modified,
        "untracked_count": untracked,
        "total_count": len(lines),
    }


def refresh_text(text: str, counts: dict[str, int]) -> str:
    refreshed = text
    for field in COUNT_FIELDS:
        pattern = re.compile(rf"(^      {field}: )\d+$", re.MULTILINE)
        refreshed, replacements = pattern.subn(rf"\g<1>{counts[field]}", refreshed)
        if replacements != 1:
            raise ValueError(f"expected one snapshot field: {field}; found {replacements}")
    return refreshed


def main() -> int:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    counts = status_counts(result.stdout)
    current = PROGRESS_PATH.read_text(encoding="utf-8")
    refreshed = refresh_text(current, counts)
    if refreshed != current:
        PROGRESS_PATH.write_text(refreshed, encoding="utf-8")
    print(
        "PROGRESS_SNAPSHOT_REFRESHED "
        f"tracked_modified={counts['tracked_modified_count']} "
        f"untracked={counts['untracked_count']} total={counts['total_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
