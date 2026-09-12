import unittest
import asyncio
import json
from app.main import (
    teaching_state_manager,
    classify_workflow_intent,
    extract_and_normalize_answer,
    extract_quiz_meta_fallback,
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

        # 2. Start diagnosis with dynamic quiz meta
        q1_meta = {
            "stem": "在新型电力系统日常调频中具备毫秒级响应速度的是：",
            "options": {"A": "抽水蓄能", "B": "功率型储能", "C": "压缩空气", "D": "重力储能"},
            "correct_answer": "B",
            "knowledge_point": "1.3 储能技术在电力系统中的应用",
            "courseware": "1.3 储能技术在电力系统中的应用.pdf P6",
            "explanation": "飞轮、超级电容等具有毫秒级响应能力。"
        }
        st = await teaching_state_manager.start_diagnosis(self.uid, self.sess_id, q1_meta)
        self.assertTrue(st.diag_active)
        self.assertEqual(st.diag_step, 1)
        self.assertEqual(st.scene_mode, 4)

        # 3. Answering while diag_active should route to diagnosis_submit
        self.assertEqual(classify_workflow_intent("B", st), "diagnosis_submit")
        self.assertEqual(classify_workflow_intent("我选B", st), "diagnosis_submit")
        self.assertEqual(classify_workflow_intent("第2个", st), "diagnosis_submit")

        # 4. Request report generation
        self.assertEqual(classify_workflow_intent("生成诊断报告", st), "diagnosis_report_generate")
        self.assertEqual(classify_workflow_intent("查看诊断报告", st), "diagnosis_report_generate")
        self.assertEqual(classify_workflow_intent("出报告", st), "diagnosis_report_generate")

        # 5. Stop command while in diagnosis
        self.assertEqual(classify_workflow_intent("退出诊断", st), "diagnosis_stop")
        self.assertEqual(classify_workflow_intent("结束诊断", st), "diagnosis_stop")

    async def test_unlimited_diagnosis_lifecycle(self):
        # Step 1: Start dynamically
        q1 = {
            "stem": "在新型电力系统日常调频中具备毫秒级响应速度的是：",
            "options": {"A": "抽水蓄能", "B": "功率型储能", "C": "压缩空气", "D": "重力储能"},
            "correct_answer": "B",
            "knowledge_point": "1.3 储能技术在电力系统中的应用",
            "courseware": "1.3 储能技术在电力系统中的应用.pdf P6",
            "explanation": "飞轮、超级电容等具有毫秒级响应能力。"
        }
        st = await teaching_state_manager.start_diagnosis(self.uid, self.sess_id, q1)
        self.assertTrue(st.diag_active)
        self.assertEqual(st.diag_step, 1)

        # Step 1 submission (correct: B)
        rec1 = {**q1, "user_answer": "B", "is_correct": True}
        q2 = {
            "stem": "构网型变流器与跟网型最本质区别是：",
            "options": {"A": "受控电流源", "B": "受控电压源", "C": "无法孤岛", "D": "无同步环路"},
            "correct_answer": "B",
            "knowledge_point": "3.4 储能变流器拓扑及并网控制",
            "courseware": "3.4 储能变流器拓扑及并网控制.pdf P12",
            "explanation": "构网型等效为受控电压源。"
        }
        step, done_cnt = await teaching_state_manager.advance_diagnosis(self.uid, self.sess_id, rec1, q2)
        self.assertEqual(step, 2)
        self.assertEqual(done_cnt, 1)

        # Step 2 submission (wrong: A, correct: B)
        rec2 = {**q2, "user_answer": "A", "is_correct": False}
        q3 = {
            "stem": "LCOS模型主要衡量：",
            "options": {"A": "变压器损耗", "B": "库仑效率", "C": "单位电量综合折算成本", "D": "消防投资比重"},
            "correct_answer": "C",
            "knowledge_point": "4.2 电化学储能系统的规划配置",
            "courseware": "4.2 电化学储能系统的规划配置.pdf P8",
            "explanation": "LCOS用于计算生命周期单位放电成本。"
        }
        step, done_cnt = await teaching_state_manager.advance_diagnosis(self.uid, self.sess_id, rec2, q3)
        self.assertEqual(step, 3)
        self.assertEqual(done_cnt, 2)

        # Step 3 submission (correct: C)
        rec3 = {**q3, "user_answer": "C", "is_correct": True}
        # Student decides to generate report
        all_records = await teaching_state_manager.finish_diagnosis(self.uid, self.sess_id, rec3)
        self.assertEqual(len(all_records), 3)

        # Verify state is cleanly reset
        st_after = await teaching_state_manager.get_or_create(self.uid, self.sess_id)
        self.assertFalse(st_after.diag_active)
        self.assertEqual(st_after.scene_mode, 0)
        self.assertEqual(st_after.diag_step, 0)

    async def test_extract_quiz_meta_fallback_robustness(self):
        llm_sample = (
            "【名师助教】已为您动态出题：\n"
            "在电力系统中，构网型储能变流器的本质是：\n"
            "A. 受控电流源\n"
            "B. 受控电压源\n"
            "C. 纯电阻负载\n"
            "D. 电感滤波源\n\n"
            '<!--HIDDEN_META:{"type":"quiz","question":"在电力系统中，构网型储能变流器的本质是：","options":{"A":"受控电流源","B":"受控电压源","C":"纯电阻负载","D":"电感滤波源"},"correct":"B","knowledge_point":"3.4 储能变流器拓扑及并网控制","courseware":"3.4 储能变流器拓扑及并网控制.pdf P12","explanation":"构网型等效为受控电压源。"}-->'
        )
        meta = extract_quiz_meta_fallback(llm_sample)
        self.assertEqual(meta["correct_answer"], "B")
        self.assertEqual(meta["options"]["A"], "受控电流源")
        self.assertEqual(meta["options"]["B"], "受控电压源")
        self.assertEqual(meta["knowledge_point"], "3.4 储能变流器拓扑及并网控制")

    async def test_diagnosis_early_exit(self):
        q1 = {
            "stem": "测试题干",
            "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
            "correct_answer": "A"
        }
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
