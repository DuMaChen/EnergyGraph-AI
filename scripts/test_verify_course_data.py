from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.verify_course_data import CourseDataInputError, main, verify


def write_incomplete_course(root: Path) -> None:
    files = [
        {
            "source_file": f"chapter-{index}.pdf",
            "normalized_file": f"chapter-{index}.pdf",
            "sha256": "unused",
            "page_count": 22,
        }
        for index in range(20)
    ]
    (root / "manifest.json").write_text(
        json.dumps({"pdf_count": 20, "files": files}), encoding="utf-8"
    )
    (root / "graph-baseline.json").write_text(
        json.dumps({"nodes": [{} for _ in range(20)], "errors": []}), encoding="utf-8"
    )


class CourseDataVerifierTests(unittest.TestCase):
    def test_missing_pdf_is_input_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_incomplete_course(root)
            with self.assertRaises(CourseDataInputError):
                verify(root)

    def test_cli_reports_controlled_input_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_incomplete_course(root)
            stderr = io.StringIO()
            with patch.object(sys, "argv", ["verify_course_data.py", str(root)]):
                with contextlib.redirect_stderr(stderr):
                    result = main()
            self.assertEqual(result, 2)
            self.assertIn("COURSE_DATA_BLOCKED_INPUT", stderr.getvalue())
            self.assertIn("missing PDF", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
