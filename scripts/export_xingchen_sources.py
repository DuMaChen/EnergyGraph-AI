#!/usr/bin/env python3
"""Export page-addressable Markdown files for Xingchen knowledge-base upload.

The output is intentionally separate from Moodle PDFs. Every page starts with
an immutable citation marker, so the Adapter can validate a model citation
against the local manifest instead of trusting free-form model text.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def extract_page(pdf: Path, page: int) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return re.sub(r"\n{3,}", "\n\n", result.stdout).strip()


def export(normalized: Path, output: Path, files_per_batch: int = 10) -> dict[str, object]:
    manifest = json.loads((normalized / "manifest.json").read_text(encoding="utf-8"))
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    entries: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for item in manifest.get("files", []):
        normalized_name = str(item["normalized_file"])
        source_name = str(item["source_file"])
        pdf = normalized / normalized_name
        target = output / (Path(normalized_name).stem + ".md")
        sections: list[str] = []
        try:
            for page in range(1, int(item["page_count"]) + 1):
                text = extract_page(pdf, page)
                if not text:
                    continue
                marker = f"[来源文件：{source_name}；章节：{item['chapter']}；页码：{page}]"
                sections.append(f"{marker}\n{text}")
            target.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
            entries.append({**item, "upload_file": target.name, "text_pages": len(sections)})
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append({"file": source_name, "error": str(exc)})
    batches = []
    for start in range(0, len(entries), files_per_batch):
        batch = entries[start : start + files_per_batch]
        batches.append({"batch": start // files_per_batch + 1, "files": [item["upload_file"] for item in batch], "source_files": [item["source_file"] for item in batch]})
    result = {"version": "xingchen-source-v1", "source_archive": manifest.get("source_archive"), "files": entries, "batches": batches, "errors": errors}
    (output / "upload-manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normalized", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--files-per-batch", type=int, default=10)
    args = parser.parse_args()
    if args.files_per_batch < 1 or args.files_per_batch > 10:
        parser.error("--files-per-batch must be 1..10")
    result = export(args.normalized, args.output, args.files_per_batch)
    print(json.dumps({"files": len(result["files"]), "batches": len(result["batches"]), "errors": len(result["errors"]), "output": str(args.output)}, ensure_ascii=False))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
