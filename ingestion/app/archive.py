from __future__ import annotations

import re
import tempfile
import zipfile
from pathlib import Path


def _display_name(info: zipfile.ZipInfo) -> str:
    if info.flag_bits & 0x800:
        return info.filename
    raw = info.filename.encode("cp437")
    for encoding in ("gb18030", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return info.filename


def _chapter_number(name: str) -> int | None:
    match = re.search(r"(?:^|[/\\])([1-6])(?:\.|章|[-_])", name)
    return int(match.group(1)) if match else None


def archive_pdfs(data_dir: Path) -> tuple[Path, dict[str, str]]:
    """Extract PDFs from the first course ZIP into a temporary safe directory."""
    archives = sorted(data_dir.glob("*.zip"))
    if not archives:
        raise FileNotFoundError("no PDF files or course ZIP archive found")
    workdir = Path(tempfile.mkdtemp(prefix="course-materials-"))
    source_names: dict[str, str] = {}
    with zipfile.ZipFile(archives[0]) as source:
        index = 0
        for info in source.infolist():
            name = _display_name(info)
            if info.is_dir() or not name.lower().endswith(".pdf"):
                continue
            if _chapter_number(name) is None:
                continue
            index += 1
            target = workdir / f"chapter-{_chapter_number(name)}-{index}.pdf"
            target.write_bytes(source.read(info))
            source_names[target.name] = Path(name).name
    if not source_names:
        raise ValueError(f"archive contains no chapter PDF files: {archives[0]}")
    return workdir, source_names
