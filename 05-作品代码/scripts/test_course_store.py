#!/usr/bin/env python3
"""Dependency-free regression tests for the structured course data layer."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "agent-adapter"))


class CourseStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        os.environ["COURSE_DB"] = str(Path(self.directory.name) / "course.db")
        # Import after COURSE_DB is set so each test owns an isolated database.
        from app.course_store import CourseStore
        self.store = CourseStore()

    def tearDown(self) -> None:
        self.directory.cleanup()
        os.environ.pop("COURSE_DB", None)

    def test_graph_has_six_chapters_and_twenty_points(self) -> None:
        self.assertEqual(len(self.store.chapters()), 6)
        self.assertEqual(len(self.store.search_nodes("", 50)), 20)

    def test_scenario_turn_is_idempotent_and_user_scoped(self) -> None:
        session = self.store.create_scenario("u-1", "grid-dispatch")
        first = self.store.add_turn("u-1", session["session_id"], 1, "输入", "r-1")
        second = self.store.add_turn("u-1", session["session_id"], 1, "输入", "r-2")
        self.assertEqual(first["turn_no"], second["turn_no"])
        completed = self.store.complete_turn("u-1", session["session_id"], 1, "回答", [{"source_id": "s-1"}])
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(self.store.scenario("u-1", session["session_id"])["turns"][0]["evidence"], [{"source_id": "s-1"}])
        self.assertIsNone(self.store.scenario("u-2", session["session_id"]))

    def test_objective_grade_is_repeatable(self) -> None:
        question = self.store.create_question("teacher", {"question_type": "single_choice", "prompt": "2+2?", "options": ["3", "4"], "answer": "4", "max_score": 10})
        self.store.publish_question(question["id"], "teacher")
        assignment = self.store.create_assignment("teacher", {"title": "作业", "question_ids": [question["id"]]})
        self.store.publish_assignment(assignment["id"])
        submission = self.store.submit("student", assignment["id"], {question["id"]: "4"}, 1)
        self.assertEqual(self.store.grade_submission(submission["id"], "teacher")["score"], 10)
        self.assertEqual(self.store.grade_submission(submission["id"], "teacher")["score"], 10)

    def test_learning_profile_is_user_scoped_and_needs_two_records_to_master(self) -> None:
        question = self.store.create_question("teacher", {"question_type": "single_choice", "prompt": "2+2?", "options": ["3", "4"], "answer": "4", "max_score": 10, "node_id": "kp-1-1"})
        self.store.publish_question(question["id"], "teacher")
        assignment = self.store.create_assignment("teacher", {"title": "作业", "question_ids": [question["id"]], "allow_attempts": 2})
        self.store.publish_assignment(assignment["id"])
        first = self.store.submit("student", assignment["id"], {question["id"]: "4"}, 1)
        self.store.grade_submission(first["id"], "teacher")
        profile = next(item for item in self.store.learning_profile("student")["nodes"] if item["id"] == "kp-1-1")
        self.assertEqual(profile["status"], "learning")
        second_assignment = self.store.create_assignment("teacher", {"title": "第二次作业", "question_ids": [question["id"]]})
        self.store.publish_assignment(second_assignment["id"])
        second = self.store.submit("student", second_assignment["id"], {question["id"]: "4"}, 1)
        self.store.grade_submission(second["id"], "teacher")
        mastered = next(item for item in self.store.learning_profile("student")["nodes"] if item["id"] == "kp-1-1")
        self.assertEqual(mastered["status"], "mastered")
        self.assertEqual(mastered["effective_submission_count"], 2)
        self.assertEqual(next(item for item in self.store.learning_profile("other")["nodes"] if item["id"] == "kp-1-1")["status"], "unassessed")

    def test_subjective_grade_is_bounded_and_kept_as_agent_initial(self) -> None:
        question = self.store.create_question("teacher", {"question_type": "essay", "prompt": "解释原理", "rubric": "包含组成和过程", "max_score": 20})
        self.store.publish_question(question["id"], "teacher")
        assignment = self.store.create_assignment("teacher", {"title": "主观题", "question_ids": [question["id"]]})
        self.store.publish_assignment(assignment["id"])
        submission = self.store.submit("student", assignment["id"], {question["id"]: "答案"}, 1)
        item = self.store.subjective_item(submission["id"], question["id"])
        grade = self.store.save_agent_grade(item, 18, "按 rubric 给出初评")
        self.assertEqual(grade["source"], "agent_initial")
        self.assertEqual(grade["score"], 18)
        self.assertEqual(self.store.submission_totals(submission["id"]), (18.0, 20.0))


if __name__ == "__main__":
    unittest.main()
