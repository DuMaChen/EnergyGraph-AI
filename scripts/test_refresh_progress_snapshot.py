from __future__ import annotations

import unittest

from scripts.refresh_progress_snapshot import refresh_text, status_counts


class ProgressSnapshotRefreshTests(unittest.TestCase):
    def test_status_counts_separate_tracked_and_untracked(self) -> None:
        output = " M tracked.py\n?? new.py\n?? new-dir/\n"
        self.assertEqual(
            status_counts(output),
            {"tracked_modified_count": 1, "untracked_count": 2, "total_count": 3},
        )

    def test_refresh_text_changes_only_snapshot_counts(self) -> None:
        source = (
            "project: fixture\n"
            "    observed_git_status:\n"
            "      tracked_modified_count: 1\n"
            "      untracked_count: 2\n"
            "      total_count: 3\n"
            "status: unchanged\n"
        )
        refreshed = refresh_text(
            source,
            {"tracked_modified_count": 4, "untracked_count": 5, "total_count": 9},
        )
        self.assertIn("project: fixture", refreshed)
        self.assertIn("status: unchanged", refreshed)
        self.assertIn("tracked_modified_count: 4", refreshed)
        self.assertIn("untracked_count: 5", refreshed)
        self.assertIn("total_count: 9", refreshed)


if __name__ == "__main__":
    unittest.main()
