import unittest
import asyncio
import time
import sys
import os

# Ensure app package is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import (
    SessionTeachingState,
    TeachingStateManager,
    extract_and_normalize_answer,
    classify_workflow_intent,
    extract_quiz_meta_fallback,
    VALID_COURSEWARE_WHITELIST,
)


class TestWorkflowStateMachine(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_extract_and_normalize_answer(self):
        # 1. Single letters
        self.assertEqual(extract_and_normalize_answer("A"), "A")
        self.assertEqual(extract_and_normalize_answer("b"), "B")
        self.assertEqual(extract_and_normalize_answer(" C "), "C")
        self.assertEqual(extract_and_normalize_answer("d"), "D")

        # 2. Chinese numerals & order
        self.assertEqual(extract_and_normalize_answer("1"), "A")
        self.assertEqual(extract_and_normalize_answer("2"), "B")
        self.assertEqual(extract_and_normalize_answer("3"), "C")
        self.assertEqual(extract_and_normalize_answer("4"), "D")
        self.assertEqual(extract_and_normalize_answer("第1个"), "A")
        self.assertEqual(extract_and_normalize_answer("第2个"), "B")
        self.assertEqual(extract_and_normalize_answer("第一个"), "A")
        self.assertEqual(extract_and_normalize_answer("第二个"), "B")
        self.assertEqual(extract_and_normalize_answer("第三个"), "C")
        self.assertEqual(extract_and_normalize_answer("第四个"), "D")

        # 3. Prefixes with punctuation
        self.assertEqual(extract_and_normalize_answer("我选B"), "B")
        self.assertEqual(extract_and_normalize_answer("我选 B"), "B")
        self.assertEqual(extract_and_normalize_answer("选【C】"), "C")
        self.assertEqual(extract_and_normalize_answer("答案应该是B。"), "B")
        self.assertEqual(extract_and_normalize_answer("作答: A"), "A")
        self.assertEqual(extract_and_normalize_answer("选项D"), "D")
        self.assertEqual(extract_and_normalize_answer("A选项"), "A")
        self.assertEqual(extract_and_normalize_answer("正确选项是B"), "B")

        # 4. True/False
        self.assertEqual(extract_and_normalize_answer("正确"), "正确")
        self.assertEqual(extract_and_normalize_answer("对"), "正确")
        self.assertEqual(extract_and_normalize_answer("是对的"), "正确")
        self.assertEqual(extract_and_normalize_answer("错误"), "错误")
        self.assertEqual(extract_and_normalize_answer("错"), "错误")
        self.assertEqual(extract_and_normalize_answer("是不对的"), "错误")

        # 5. Natural language non-answer questions should return None
        self.assertIsNone(extract_and_normalize_answer("请问选项A中提到的PCS工作原理是什么？"))
        self.assertIsNone(extract_and_normalize_answer("抽水蓄能电站由哪些部分组成？"))
        self.assertIsNone(extract_and_normalize_answer(""))

    def test_classify_workflow_intent(self):
        state = SessionTeachingState(uid="student_1", session_id="sess_1")

        # 1. Quoted text takes absolute precedence
        self.assertEqual(
            classify_workflow_intent("请详细解释一下", state, quoted_text="构网型变流器"),
            "quote_study",
        )
        self.assertEqual(
            classify_workflow_intent("B", state, quoted_text="构网型变流器"),
            "quote_study",
        )

        # 2. Scenario control
        self.assertEqual(classify_workflow_intent("扮演储能电厂运维师傅与我对话", state), "scenario_start_engineer")
        self.assertEqual(classify_workflow_intent("扮演主讲老师授课", state), "scenario_start_teacher")
        self.assertEqual(classify_workflow_intent("退出情景演绎", state), "scenario_stop")
        self.assertEqual(classify_workflow_intent("退出演练", state), "scenario_stop")

        # 3. Quiz generate and stop
        self.assertEqual(classify_workflow_intent("出一道单选题考考我", state), "quiz_generate")
        self.assertEqual(classify_workflow_intent("停止出题练习", state), "quiz_stop")

        # 4. Active quiz answering
        state.current_quiz = {
            "stem": "关于构网型储能变流器的描述，正确的是？",
            "correct_answer": "B",
            "knowledge_point": "构网型PCS控制",
            "courseware": "3.4 储能变流器拓扑及并网控制.pdf P12",
        }
        self.assertEqual(classify_workflow_intent("B", state), "quiz_submit")
        self.assertEqual(classify_workflow_intent("我选B", state), "quiz_submit")
        self.assertEqual(classify_workflow_intent("第2个", state), "quiz_submit")
        self.assertEqual(classify_workflow_intent("答案应该是B。", state), "quiz_submit")

        # Questions about options during quiz should NOT trigger quiz_submit
        self.assertEqual(
            classify_workflow_intent("请问选项A中提到的锁相环机理是什么？", state),
            "general_qa",
        )

        # 5. Learning diagnosis
        self.assertEqual(
            classify_workflow_intent("请根据我的做题记录进行全面学情诊断与错题归因分析", state),
            "learning_diagnosis",
        )

    def test_teaching_state_manager_concurrency_and_ttl(self):
        async def run_state_manager_test():
            manager = TeachingStateManager(ttl_seconds=1, max_sessions=5)
            
            # Create session
            s1 = await manager.get_or_create("u1", "s1")
            self.assertEqual(s1.scene_mode, 0)
            
            # Set scenario
            await manager.set_scene("u1", "s1", 1, "储能电站现场运维师傅")
            s1_check = await manager.get_or_create("u1", "s1")
            self.assertEqual(s1_check.scene_mode, 1)
            self.assertEqual(s1_check.scene_role_name, "储能电站现场运维师傅")

            # Set quiz and atomic pop
            await manager.set_active_quiz("u1", "s1", {"correct_answer": "C", "stem": "Test"})
            quiz1 = await manager.pop_active_quiz("u1", "s1")
            self.assertIsNotNone(quiz1)
            self.assertEqual(quiz1["correct_answer"], "C")
            
            # Second pop should be None (atomic consumption)
            quiz2 = await manager.pop_active_quiz("u1", "s1")
            self.assertIsNone(quiz2)

            # Test TTL expiry
            await manager.set_scene("u1", "s1", 2, "名师")
            time.sleep(1.1)
            s1_expired = await manager.get_or_create("u1", "s1")
            self.assertEqual(s1_expired.scene_mode, 0)

        self.loop.run_until_complete(run_state_manager_test())

    def test_extract_quiz_meta_fallback(self):
        # 1. Standard hidden tag
        text_with_tag = (
            "【随堂测试单选题】\n"
            "题干：构网型变流器具备何种特性？\n"
            "A. 等效为受控电流源\n"
            "B. 等效为内部受控电压源\n"
            "C. 必须依赖强电网锁相环\n"
            "D. 无法提供惯量支撑\n"
            '<!--HIDDEN_META:{"correct_answer":"B","knowledge_point":"构网型变流器控制","courseware":"3.4 储能变流器拓扑及并网控制.pdf P12","explanation":"构网型变流器对外呈现受控电压源特性"}-->'
        )
        meta = extract_quiz_meta_fallback(text_with_tag)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["correct_answer"], "B")
        self.assertEqual(meta["knowledge_point"], "构网型变流器控制")

        # 2. Tag missing, fallback regex
        text_fallback = (
            "【随堂测试单选题】\n"
            "题干：抽水蓄能属于哪类储能？\n"
            "A. 物理储能\nB. 电化学储能\nC. 电磁储能\nD. 相变储能\n"
            "正确答案：A"
        )
        meta_fb = extract_quiz_meta_fallback(text_fallback)
        self.assertIsNotNone(meta_fb)
        self.assertEqual(meta_fb["correct_answer"], "A")

    def test_courseware_whitelist(self):
        self.assertIn("3.4 储能变流器拓扑及并网控制.pdf", VALID_COURSEWARE_WHITELIST)
        self.assertIn("1.1 电力储能技术的概念 .pdf", VALID_COURSEWARE_WHITELIST)
        self.assertIn("2.1 电力系统的基本概念.pdf", VALID_COURSEWARE_WHITELIST)
        self.assertNotIn("non_existent_slide.pdf", VALID_COURSEWARE_WHITELIST)


if __name__ == "__main__":
    unittest.main()
