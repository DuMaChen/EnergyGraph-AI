"""Small, dependency-free page retrieval for the mounted course source index.

The external Workflow remains the answer generator. This module only selects
bounded, server-owned evidence from the course files uploaded by a teacher so
that a provider Workflow without its own KB can still receive the right course
context. It never accepts source names or page numbers from the browser.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


_MARKER = re.compile(
    r"\[来源文件：(?P<file>[^；\]]+)(?:；章节：(?P<chapter>[^；\]]+))?；页码：(?P<page>\d+)\]"
)
_TERM = re.compile(r"[A-Za-z0-9][A-Za-z0-9_+-]*|[\u4e00-\u9fff]+")
_STOPWORDS = {
    "请",
    "解释",
    "说明",
    "概述",
    "介绍",
    "什么是",
    "如何",
    "以及",
    "的",
    "和",
    "在",
    "中",
    "作用",
    "要点",
}


@dataclass(frozen=True)
class CourseChunk:
    source_file: str
    chapter: str
    page: int
    text: str

    @property
    def source_id(self) -> str:
        return hashlib.sha256(f"{self.source_file}:{self.page}".encode("utf-8")).hexdigest()[:20]

    @property
    def marker(self) -> str:
        return f"[来源文件：{self.source_file}；章节：{self.chapter}；页码：{self.page}]"


@dataclass(frozen=True)
class RetrievalResult:
    chunks: tuple[CourseChunk, ...]
    max_chars: int

    @property
    def prompt_context(self) -> str:
        if not self.chunks:
            return ""
        parts: list[str] = ["以下是服务器从本课程课件中检索出的资料。回答必须优先依据这些资料；不要编造资料之外的页码或引用。"]
        remaining = max(self.max_chars - len(parts[0]), 0)
        for chunk in self.chunks:
            part = f"\n\n{chunk.marker}\n{chunk.text.strip()}"
            if remaining <= 0:
                break
            if len(part) > remaining:
                part = part[:remaining]
            parts.append(part)
            remaining -= len(part)
        return "".join(parts)

    def sources(
        self,
        version_name: str,
        version_id: str,
        manifest_by_source: dict[str, dict[str, object]] | None = None,
    ) -> list[dict[str, object]]:
        manifest_by_source = manifest_by_source or {}
        return [
            {
                "source_id": chunk.source_id,
                # Keep the human-readable source name for display while
                # exposing Moodle's normalized filename for the locator URL.
                "file": str(manifest_by_source.get(chunk.source_file, {}).get("normalized_file") or chunk.source_file),
                "source_file": chunk.source_file,
                "chapter": chunk.chapter,
                "page": chunk.page,
                "sha256": str(manifest_by_source.get(chunk.source_file, {}).get("sha256") or ""),
                "resource_id": "res-"
                + hashlib.sha256(
                    f"{manifest_by_source.get(chunk.source_file, {}).get('normalized_file', '')}:"
                    f"{manifest_by_source.get(chunk.source_file, {}).get('chapter_id', '')}".encode()
                ).hexdigest()[:20]
                if manifest_by_source.get(chunk.source_file)
                else "",
                "version": version_name,
                "kb_version_id": version_id,
                "evidence_type": "server_retrieval",
            }
            for chunk in self.chunks
        ]


class CourseRetriever:
    """Load page-addressable Markdown files and return ranked evidence."""

    def __init__(self, source_dir: str | Path, *, max_files: int = 100) -> None:
        self.source_dir = Path(source_dir)
        self.max_files = max_files
        self._chunks: tuple[CourseChunk, ...] | None = None

    def _load(self) -> tuple[CourseChunk, ...]:
        if self._chunks is not None:
            return self._chunks
        chunks: list[CourseChunk] = []
        if self.source_dir.is_dir():
            for path in sorted(self.source_dir.glob("*.md"))[: self.max_files]:
                text = path.read_text(encoding="utf-8", errors="replace")
                matches = list(_MARKER.finditer(text))
                for index, match in enumerate(matches):
                    body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                    body = text[match.end() : body_end].strip()
                    if body:
                        chunks.append(
                            CourseChunk(
                                source_file=match.group("file").strip(),
                                chapter=(match.group("chapter") or "").strip(),
                                page=int(match.group("page")),
                                text=body,
                            )
                        )
        self._chunks = tuple(chunks)
        return self._chunks

    @staticmethod
    def _terms(question: str) -> set[str]:
        terms: set[str] = set()
        for token in _TERM.findall(question.lower()):
            if token in _STOPWORDS or len(token) < 2:
                continue
            terms.add(token)
            if re.fullmatch(r"[\u4e00-\u9fff]+", token):
                for width in (2, 3, 4):
                    terms.update(token[index : index + width] for index in range(len(token) - width + 1))
        return {term for term in terms if term not in _STOPWORDS}

    def search(self, question: str, *, max_chunks: int = 2, max_chars: int = 6000) -> RetrievalResult:
        terms = self._terms(question)
        ranked: list[tuple[int, int, CourseChunk]] = []
        for index, chunk in enumerate(self._load()):
            haystack = f"{chunk.source_file} {chunk.chapter} {chunk.text}".lower()
            score = sum(min(haystack.count(term), 4) * (len(term) if len(term) > 2 else 1) for term in terms)
            if score:
                ranked.append((score, -index, chunk))
        ranked.sort(reverse=True, key=lambda item: (item[0], item[1]))
        return RetrievalResult(tuple(item[2] for item in ranked[: max(1, max_chunks)]), max_chars)
