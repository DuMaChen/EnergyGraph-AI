from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.course_retrieval import CourseRetriever


class CourseRetrievalTest(unittest.TestCase):
    def test_search_returns_page_addressable_course_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "3.1.md").write_text(
                "[来源文件：3.1 抽水蓄能电站的组成及工作原理.pdf；章节：第3章；页码：4]\n"
                "抽水蓄能电站的组成和工作原理：以水为储能介质，实现水的势能与电能相互转换。\n"
                "[来源文件：3.1 抽水蓄能电站的组成及工作原理.pdf；章节：第3章；页码：5]\n"
                "抽水蓄能电站可以削峰填谷。\n",
                encoding="utf-8",
            )
            (root / "4.2.md").write_text(
                "[来源文件：4.2 电化学储能系统的规划配置.pdf；章节：第4章；页码：1]\n"
                "电化学储能系统需要进行规划配置。\n",
                encoding="utf-8",
            )

            result = CourseRetriever(root).search("请解释抽水蓄能电站的组成和工作原理。")

            self.assertGreaterEqual(len(result.chunks), 1)
            self.assertEqual(result.chunks[0].source_file, "3.1 抽水蓄能电站的组成及工作原理.pdf")
            self.assertEqual(result.chunks[0].page, 4)
            self.assertIn("[来源文件：3.1 抽水蓄能电站的组成及工作原理.pdf；章节：第3章；页码：4]", result.prompt_context)

    def test_context_and_sources_are_bounded_and_server_addressable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "3.4.md").write_text(
                "[来源文件：3.4 储能变流器拓扑及并网控制.pdf；章节：第3章；页码：12]\n"
                + ("储能变流器并网控制。" * 2000),
                encoding="utf-8",
            )

            result = CourseRetriever(root).search("储能变流器并网控制", max_chunks=1, max_chars=1200)
            sources = result.sources(
                "kb-test",
                "version-test",
                {
                    "3.4 储能变流器拓扑及并网控制.pdf": {
                        "sha256": "course-sha",
                        "normalized_file": "chapter-3-3.4-.pdf",
                        "chapter_id": 3,
                    }
                },
            )

            self.assertLessEqual(len(result.prompt_context), 1200)
            self.assertEqual(len(sources), 1)
            self.assertEqual(sources[0]["file"], "chapter-3-3.4-.pdf")
            self.assertEqual(sources[0]["source_file"], "3.4 储能变流器拓扑及并网控制.pdf")
            self.assertEqual(sources[0]["chapter"], "第3章")
            self.assertEqual(sources[0]["page"], 12)
            self.assertEqual(sources[0]["kb_version_id"], "version-test")
            self.assertEqual(sources[0]["sha256"], "course-sha")
            self.assertTrue(str(sources[0]["resource_id"]).startswith("res-"))


if __name__ == "__main__":
    unittest.main()
