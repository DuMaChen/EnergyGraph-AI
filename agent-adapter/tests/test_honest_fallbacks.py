import unittest
from app.main import (
    classify_workflow_intent,
    detect_prompt_echo,
    extract_quiz_meta_fallback,
    is_usable_quiz_meta,
    normalize_quiz_stem,
    normalize_workflow_text,
    teaching_state_manager,
)


QUESTION_WITH_EVERYTHING = (
    "【题干】关于构网型变流器与跟网型变流器的本质区别，下列说法正确的是：\n"
    "A. 构网型变流器必须依赖外部电网提供电压基准\n"
    "B. 构网型变流器等效为内部受控电压源，可自主建立电压与频率\n"
    "C. 跟网型变流器不需要锁相环即可稳定运行\n"
    "D. 两者完全等价\n"
    "【标准答案】B\n"
    "【核心考点】3.4 储能变流器拓扑及并网控制\n"
    "【知识溯源】3.4 储能变流器拓扑及并网控制.pdf P12\n"
)


class TestHonestFallbacks(unittest.IsolatedAsyncioTestCase):
    def test_parse_only_no_canned_question(self):
        """Garbage/echo/demo input must NOT yield any fabricated question."""
        for garbage in ("", "好的。", "【角色设定：储能电站现场一线运维师傅（张师傅）】学生向你问好"):
            meta = extract_quiz_meta_fallback(garbage)
            self.assertFalse(is_usable_quiz_meta(meta), msg=f"garbage became usable: {garbage!r}")

    def test_no_keyword_answer_guessing(self):
        """A question whose options parsed but whose answer line is missing must
        NOT receive a keyword-guessed answer (old behaviour guessed A/B)."""
        text = (
            "【题干】抽水蓄能电站与压缩空气储能的启停特性，下列说法正确的是：\n"
            "A. 抽水蓄能启动更快\n"
            "B. 压缩空气储能启动更快\n"
            "C. 两者相同\n"
            "D. 都无法启动\n"
        )
        meta = extract_quiz_meta_fallback(text)
        self.assertIn(meta.get("correct_answer"), (None, ""))
        self.assertFalse(is_usable_quiz_meta(meta))

    def test_usable_requires_answer_letter(self):
        meta = extract_quiz_meta_fallback(QUESTION_WITH_EVERYTHING)
        self.assertTrue(is_usable_quiz_meta(meta))
        self.assertEqual(meta["correct_answer"], "B")

        no_answer = extract_quiz_meta_fallback(
            QUESTION_WITH_EVERYTHING.split("【标准答案】")[0]
        )
        self.assertFalse(is_usable_quiz_meta(no_answer))

    def test_placeholder_citation_demo_dialogue_rejected(self):
        """The workflow demo dialogue with placeholder citations must be detected
        and sanitized to empty instead of shown to students."""
        demo = (
            "学生: 请问电力系统储能技术有哪些类型？\n\n"
            "老师: 主要分为蓄电池、超级电容器等类型。[来源文件：xxx.pdf；页码：yyy]"
        )
        self.assertTrue(detect_prompt_echo(demo))
        self.assertEqual(normalize_workflow_text(demo), "")

    def test_normalize_stem_dedup(self):
        a = "储能系统在新型电力系统中发挥着多时间尺度的调节作用，以下关于各类储能响应速度的排序正确的是："
        b = "储能系统在新型电力系统中发挥着  多时间尺度的调节作用，以下关于各类储能响应速度的排序正确的是"
        self.assertEqual(normalize_quiz_stem(a), normalize_quiz_stem(b))
        self.assertNotEqual(normalize_quiz_stem(a), normalize_quiz_stem("完全不同的另一道题干"))

    async def test_awaiting_next_routing(self):
        uid, sess = "u_honest", "s_honest"
        await teaching_state_manager.stop_diagnosis(uid, sess)
        st = await teaching_state_manager.get_or_create(uid, sess)
        st.diag_active = True
        st.awaiting_next = True
        self.assertEqual(classify_workflow_intent("下一题", st), "diagnosis_next")
        self.assertEqual(classify_workflow_intent("随便说点什么", st), "diagnosis_next")
        self.assertEqual(classify_workflow_intent("生成诊断报告", st), "diagnosis_report_generate")
        self.assertEqual(classify_workflow_intent("退出诊断", st), "diagnosis_stop")
        await teaching_state_manager.stop_diagnosis(uid, sess)


if __name__ == "__main__":
    unittest.main()
