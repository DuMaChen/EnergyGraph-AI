#!/usr/bin/env python3
"""Validate the public demo's material metadata and read-only routing contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "course-data" / "normalized" / "manifest.json"
DEMO = ROOT / "agent-ui" / "index.html"
MOODLE_DOCKERFILE = ROOT / "deploy" / "moodle" / "Dockerfile"
CADDYFILE = ROOT / "deploy" / "caddy" / "Caddyfile"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 20:
        raise SystemExit("demo material manifest must contain 20 files")
    demo = DEMO.read_text(encoding="utf-8")
    for item in files:
        normalized = str(item["normalized_file"])
        source = str(item["source_file"])
        page_count = str(item["page_count"])
        if normalized not in demo or source not in demo or f"page_count: {page_count}" not in demo:
            raise SystemExit(f"demo metadata mismatch: {normalized}")
    dockerfile = MOODLE_DOCKERFILE.read_text(encoding="utf-8")
    if "chmod 0644" not in dockerfile or "resource.php" not in dockerfile:
        raise SystemExit("Moodle resource file mode is not hardened")
    caddy = CADDYFILE.read_text(encoding="utf-8")
    if "@demo path /demo /demo/*" not in caddy or "reverse_proxy agent-ui:80" not in caddy:
        raise SystemExit("public demo route is not configured")
    print("DEMO_MATERIALS_OK files=20 manifest_metadata=verified resource_mode=0644 public_route=/demo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
