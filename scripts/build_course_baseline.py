#!/usr/bin/env python3
"""Build a versioned graph baseline from the supplied XLSX template.

The workbook is an OOXML zip, so this utility intentionally uses only the
standard library.  That keeps the import reproducible on the server and makes
malformed rows visible instead of silently dropping them through a spreadsheet
engine's coercion rules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def workbook_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as workbook:
        shared_root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
        shared = ["".join(text.text or "" for text in item.findall(".//x:t", NS)) for item in shared_root.findall("x:si", NS)]
        sheet = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in sheet.findall(".//x:row", NS):
            values: dict[int, str] = {}
            for cell in row.findall("x:c", NS):
                ref = cell.get("r", "A1")
                column = 0
                for char in ref:
                    if char.isalpha():
                        column = column * 26 + ord(char.upper()) - 64
                    else:
                        break
                value = cell.find("x:v", NS)
                text = value.text if value is not None else ""
                if cell.get("t") == "s" and text:
                    text = shared[int(text)]
                values[column] = text.strip()
            rows.append([values.get(index, "") for index in range(1, max(values, default=1) + 1)])
        return rows


def build(path: Path) -> dict[str, object]:
    rows = workbook_rows(path)
    current_chapter = 0
    nodes: list[dict[str, object]] = []
    by_name: dict[str, str] = {}
    errors: list[dict[str, object]] = []
    for row_number, row in enumerate(rows[2:], start=3):
        node_type = row[0] if row else ""
        if node_type == "分类":
            title = next((value for value in row[1:] if value), "")
            current_chapter += 1
            if not title:
                errors.append({"row": row_number, "error": "empty chapter name"})
            continue
        # A few rows in the teacher workbook omit the type cell while still
        # containing a valid point name; treat that as a recoverable template
        # omission and preserve the row rather than losing a knowledge point.
        if node_type == "" and len(row) > 2 and row[2]:
            node_type = "知识点"
        if node_type != "知识点":
            continue
        name = next((value for value in row[1:3] if value), "")
        if not name or not current_chapter:
            errors.append({"row": row_number, "error": "knowledge point has no chapter/name"})
            continue
        node_id = f"kp-{current_chapter}-{len([n for n in nodes if n['chapter_id'] == current_chapter]) + 1}"
        nodes.append({"id": node_id, "chapter_id": current_chapter, "name": name, "category": "概念性"})
        by_name[name] = node_id

    # The workbook may use shortened names in prerequisite cells. Resolve by
    # exact match first, then by a unique suffix/title match.
    edges: list[dict[str, str]] = []
    for row_number, row in enumerate(rows[2:], start=3):
        if not row or (row[0] not in {"知识点", ""} and not (len(row) > 2 and row[2])):
            continue
        name = next((value for value in row[1:3] if value), "")
        target = by_name.get(name)
        if not target:
            continue
        prerequisites = row[3] if len(row) > 3 else ""
        for token in filter(None, (item.strip() for item in prerequisites.replace("；", ";").replace("、", ";").replace("，", ";").split(";"))):
            source = by_name.get(token)
            if source is None and token.startswith("第"):
                chapter_match = re.match(r"第\s*(\d+)\s*章", token)
                if chapter_match:
                    source = next((item["id"] for item in nodes if item["chapter_id"] == int(chapter_match.group(1))), None)
            if source is None:
                candidates = [node_id for node_name, node_id in by_name.items() if token in node_name or node_name in token]
                source = candidates[0] if len(candidates) == 1 else None
            if source == target:
                # The workbook occasionally lists the current point as a
                # descriptive prerequisite; it is not a graph self-loop.
                continue
            if source:
                edges.append({"from_id": source, "to_id": target, "relation_type": "prerequisite"})
            elif token:
                errors.append({"row": row_number, "error": f"unresolved prerequisite: {token}"})
    # A prerequisite cycle makes deterministic learning paths impossible.
    outgoing: dict[str, list[str]] = {}
    for edge in edges:
        outgoing.setdefault(edge["from_id"], []).append(edge["to_id"])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str, chain: list[str]) -> None:
        if node_id in visiting:
            errors.append({"row": 0, "error": "prerequisite cycle: " + " -> ".join(chain + [node_id])})
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for child in outgoing.get(node_id, []):
            visit(child, chain + [node_id])
        visiting.remove(node_id)
        visited.add(node_id)

    for node in nodes:
        visit(str(node["id"]), [])
    return {"version": "graph-v1", "source": path.name, "nodes": nodes, "edges": edges, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.xlsx)
    result["sha256"] = hashlib.sha256(args.xlsx.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"nodes": len(result["nodes"]), "edges": len(result["edges"]), "errors": len(result["errors"]), "output": str(args.output)}, ensure_ascii=False))
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
