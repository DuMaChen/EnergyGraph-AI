#!/usr/bin/env python3
"""Fail-fast DATA/KG checks for the local course release artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def verify(root: Path) -> dict[str, int]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    graph = json.loads((root / "graph-baseline.json").read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    if len(files) != 20 or manifest.get("pdf_count") != 20:
        raise ValueError(f"expected 20 PDFs, got {len(files)}")
    if len(graph.get("nodes", [])) != 20 or len(graph.get("errors", [])):
        raise ValueError("graph baseline is not 20 points with zero errors")
    seen = set()
    for item in files:
        name = str(item["normalized_file"])
        if name in seen or "/" in name or "\\" in name:
            raise ValueError(f"unsafe or duplicate normalized file: {name}")
        seen.add(name)
        path = root / name
        if not path.is_file():
            raise ValueError(f"missing PDF: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item.get("sha256"):
            raise ValueError(f"hash mismatch: {name}")
        if not isinstance(item.get("page_count"), int) or item["page_count"] < 1:
            raise ValueError(f"invalid page count: {name}")
    if sum(item["page_count"] for item in files) != 439:
        raise ValueError("course page total changed; update baseline deliberately")
    source_manifest = root.parent / "xingchen-sources" / "upload-manifest.json"
    if source_manifest.exists():
        exported = json.loads(source_manifest.read_text(encoding="utf-8"))
        if len(exported.get("files", [])) != 20 or exported.get("errors"):
            raise ValueError("Xingchen source export is incomplete")
        source_root = source_manifest.parent
        for item in exported["files"]:
            exported_file = source_root / str(item["upload_file"])
            if not exported_file.is_file() or "[来源文件：" not in exported_file.read_text(encoding="utf-8"):
                raise ValueError(f"missing citation marker: {exported_file.name}")
    return {"pdfs": len(files), "pages": sum(item["page_count"] for item in files), "nodes": len(graph["nodes"]), "edges": len(graph.get("edges", []))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
