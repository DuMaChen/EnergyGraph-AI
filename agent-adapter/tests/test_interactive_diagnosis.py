import unittest
import asyncio
import json
from app.main import (
    teaching_state_manager,
    classify_workflow_intent,
    extract_and_normalize_answer,
    DIAGNOSTIC_QUESTION_BANK,
    build_interactive_diagnosis_report
)


class TestInteractiveDiagnosisFlow(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.uid = "test_diag_user_001"
        self.sess_id = "test_diag_sess_001"
        # Reset state before each test
        await teaching_state_manager.stop_diagnosis(self.uid, self.sess_id)

    async def test_intent_classification_for_diagnosis(self):
        # 1. Start intent
        self.assertEqual(classify_workflow_intent("进行学情诊断"), "diagnosis_start")
        self.assertEqual(classify_workflow_intent("帮我做一下学情诊断"), "diagnosis_start")
        self.assertEqual(classify_workflow_intent("学情诊断"), "diagnosis_start")

        # 2. Start diagnosis
        st = await teaching_state_manager.start_diagnosis(self.uid, self.sess_id, DIAGNOSTIC_QUESTION_BANK[0])
        self.assertTrue(st.diag_active)
        self.assertEqual(st.diag_step, 1)
        self.assertEqual(st.scene_mode, 4)

        # 3. Answering while diag_active should route to diagnosis_submit
        self.assertEqual(classify_workflow_intent("B", st), "diagnosis_submit")
        self.assertEqual(classify_workflow_intent("我选B", st), "diagnosis_submit")
        self.assertEqual(classify_workflow_intent("第2个", st), "diagnosis_submit")

        # 4. Stop command while in diagnosis
        self.assertEqual(classify_workflow_intent("退出诊断", st), "diagnosis_stop")
        self.assertEqual(classify_workflow_intent("结束诊断", st), "diagnosis_stop")

    async def test_three_step_diagnosis_lifecycle(self):
        # Step 1: Start
        q1 = DIAGNOSTIC_QUESTION_BANK[0]
        st = await teaching_state_manager.start_diagnosis(self.uid, self.sess_id, q1)
        self.assertTrue(st.diag_active)
        self.assertEqual(st.diag_step, 1)

        # Step 1 submission (correct: B)
        rec1 = {**q1, "user_answer": "B", "is_correct": True}
        q2 = DIAGNOSTIC_QUESTION_BANK[1]
        step, total = await teaching_state_manager.advance_diagnosis(self.uid, self.sess_id, rec1, q2)
        self.assertEqual(step, 2)
        self.assertEqual(total, 3)

        # Step 2 submission (wrong: A, correct: B)
        rec2 = {**q2, "user_answer": "A", "is_correct": False}
        q3 = DIAGNOSTIC_QUESTION_BANK[2]
        step, total = await teaching_state_manager.advance_diagnosis(self.uid, self.sess_id, rec2, q3)
        self.assertEqual(step, 3)

        # Step 3 submission (correct: C)
        rec3 = {**q3, "user_answer": "C", "is_correct": True}
        all_records = await teaching_state_manager.finish_diagnosis(self.uid, self.sess_id, rec3)
        self.assertEqual(len(all_records), 3)

        # Verify state is cleanly reset
        st_after = await teaching_state_manager.get_or_create(self.uid, self.sess_id)
        self.assertFalse(st_after.diag_active)
        self.assertEqual(st_after.scene_mode, 0)
        self.assertEqual(st_after.diag_step, 0)

        # Generate report
        report_text, sources = build_interactive_diagnosis_report(all_records)
        self.assertIn("《电力系统储能技术》学情诊断综合报告", report_text)
        self.assertIn("总测评题数**：3 题", report_text)
        self.assertIn("正确作答数**：2 题", report_text)
        self.assertIn("66.7%", report_text)
        self.assertIn("错题根因剖析", report_text)
        self.assertIn("3.4 储能变流器拓扑及并网控制", report_text)
        self.assertTrue(len(sources) >= 1)

    async def test_diagnosis_early_exit(self):
        q1 = DIAGNOSTIC_QUESTION_BANK[0]
        await teaching_state_manager.start_diagnosis(self.uid, self.sess_id, q1)
        st = await teaching_state_manager.get_or_create(self.uid, self.sess_id)
        self.assertTrue(st.diag_active)

        # Exit early
        await teaching_state_manager.stop_diagnosis(self.uid, self.sess_id)
        st_after = await teaching_state_manager.get_or_create(self.uid, self.sess_id)
        self.assertFalse(st_after.diag_active)
        self.assertEqual(st_after.scene_mode, 0)
        self.assertEqual(len(st_after.diag_records), 0)


if __name__ == "__main__":
    unittest.main()
