#!/usr/bin/env python3
"""Normalize the course ZIP and write a reproducible manifest.

The source archive was produced by a Windows tool that stored GBK file names
without the UTF-8 flag.  Python therefore initially sees the names as CP437.
This script repairs those names, rejects path traversal, and gives every PDF a
stable ASCII filename for container mounts while preserving the original name
in the manifest used for citations and the Moodle UI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path


CHAPTERS = {
    1: "第1章 概述",
    2: "第2章 电力系统与储能技术的应用",
    3: "第3章 电力储能系统的组成及工作原理",
    4: "第4章 电力储能系统的规划配置",
    5: "第5章 电力储能系统的接入与运行控制",
    6: "第6章 电力储能系统的性能检测与评估",
}


def display_name(info: zipfile.ZipInfo) -> str:
    """Decode the archive member name without trusting its display encoding."""
    if info.flag_bits & 0x800:
        return info.filename
    raw = info.filename.encode("cp437")
    for encoding in ("gb18030", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return info.filename


def chapter_number(name: str) -> int | None:
    match = re.search(r"(?:^|[/\\])([1-6])(?:\.|章|[-_])", name)
    return int(match.group(1)) if match else None


def safe_member_name(name: str) -> Path:
    path = Path(name.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe archive member path: {name!r}")
    return path


def page_count(pdf: bytes) -> int | None:
    """Return a conservative page count without requiring a PDF package.

    The count is only used to reject obviously impossible citation pages.  A
    later PDF parser may replace it with a precise count; unknown remains
    preferable to inventing a page boundary.
    """
    matches = re.findall(rb"/Type\s*/Page(?:\s|/|>)", pdf)
    return len(matches) or None


def normalize_archive(archive: Path, output: Path) -> list[dict[str, object]]:
    output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    used_names: set[str] = set()
    with zipfile.ZipFile(archive) as source:
        for info in source.infolist():
            name = display_name(info)
            member = safe_member_name(name)
            if info.is_dir() or member.suffix.lower() != ".pdf":
                continue
            chapter = chapter_number(name)
            if chapter is None:
                raise ValueError(f"could not infer chapter from PDF name: {name}")
            stem = member.stem.strip() or f"document-{len(manifest) + 1}"
            # The chapter prefix is used by ingestion and remains stable even
            # if the human-readable title changes in a future source archive.
            normalized = f"chapter-{chapter}-{stem}.pdf"
            normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized)
            if normalized in used_names:
                normalized = f"chapter-{chapter}-{len(manifest) + 1}.pdf"
            used_names.add(normalized)
            target = output / normalized
            content = source.read(info)
            target.write_bytes(content)
            file_hash = hashlib.sha256(content).hexdigest()
            manifest.append(
                {
                    "archive_file": name,
                    "source_file": member.name,
                    "normalized_file": normalized,
                    "chapter_id": chapter,
                    "chapter": CHAPTERS[chapter],
                    "sha256": file_hash,
                    "page_count": page_count(content),
                }
            )
    manifest.sort(key=lambda item: (int(item["chapter_id"]), str(item["normalized_file"])))
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "source_archive": archive.name,
                "pdf_count": len(manifest),
                "files": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if args.clean and args.output.exists():
        shutil.rmtree(args.output)
    manifest = normalize_archive(args.archive, args.output)
    print(json.dumps({"pdf_count": len(manifest), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
