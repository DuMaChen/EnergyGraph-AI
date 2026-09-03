import json
import os
import sys
import unittest
from unittest.mock import patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.main import app, TeachingStateManager, teaching_state_manager, stable_uid, store
from fastapi.testclient import TestClient

HEADERS = {
    "Content-Type": "application/json",
    "x-dev-role": "student",
    "x-dev-user": "demo-student-e2e",
    "X-Moodle-Sesskey": "mock-csrf",
}

class TestWorkflowE2ELive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._prev_mock_auth = os.environ.get("MOCK_AUTH_MODE")
        os.environ["MOCK_AUTH_MODE"] = "true"

    @classmethod
    def tearDownClass(cls):
        if cls._prev_mock_auth is not None:
            os.environ["MOCK_AUTH_MODE"] = cls._prev_mock_auth
        else:
            os.environ.pop("MOCK_AUTH_MODE", None)

    def setUp(self):
        self.published_patch = patch.object(
            store,
            "published_kb",
            return_value={"id": "kb_v1", "version_name": "v1.0", "status": "active"},
        )
        self.published_patch.start()

    def tearDown(self):
        self.published_patch.stop()

    def test_01_quiz_generation_and_hidden_meta(self):
        """Scenario 1: Quiz generation returns clean stem and quiz_meta SSE event without leaking raw tag"""
        session_id = "test_sess_e2e_01"
        client = TestClient(app)
        
        async def mock_stream(*args, **kwargs):
            yield {"event": "token", "data": {"text": "【随堂测试单选题】\n题干：在储能变流器控制中，下垂控制主要用于什么场景？\nA. 孤岛运行与自主调频\nB. 仅用于直流充电\nC. 仅用于过温保护\nD. 仅用于切断电源\n<!--HIDDEN_META:{\"correct_answer\":\"A\",\"courseware\":\"3.4 储能变流器拓扑及并网控制.pdf P12\",\"explanation\":\"下垂控制用于微电网与构网控制下的有功调频与无功调压。\"}-->", "request_id": "req_1"}}
            yield {"event": "done", "data": {"request_id": "req_1"}}

        with patch("app.main.xingchen_stream", side_effect=mock_stream):
            resp = client.post(
                "/api/course-agent/chat",
                headers=HEADERS,
                json={"question": "出一道单选题考考我", "session_id": session_id, "mode": "qa"},
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("event: token", resp.text)
            self.assertIn("event: quiz_meta", resp.text)
            self.assertIn("event: done", resp.text)
            self.assertNotIn("<!--HIDDEN_META:", resp.text)
            print("Scenario 1 (Quiz Generation): PASS")

    def test_02_quiz_grading_and_atomic_consumption(self):
        """Scenario 2: Quiz submission evaluates answer, returns quiz_graded, and consumes quiz atomically"""
        session_id = "test_sess_e2e_02"
        client = TestClient(app)
        uid = stable_uid("demo-student-e2e")
        
        # 1. Manually set an active quiz in state manager for determinism
        import asyncio
        asyncio.run(
            teaching_state_manager.set_active_quiz(
                uid,
                session_id,
                {
                    "stem": "储能变流器主要功能是什么？",
                    "correct_answer": "B",
                    "courseware": "3.4 储能变流器拓扑及并网控制.pdf P12",
                    "explanation": "储能变流器实现交直流能量双向变换与并网控制。",
                },
            )
        )

        # 2. Submit normalized answer "选B。"
        resp = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "选B。", "session_id": session_id, "mode": "qa"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("event: quiz_graded", resp.text)
        self.assertIn("回答正确！", resp.text)
        self.assertIn("3.4 储能变流器拓扑及并网控制.pdf", resp.text)

        # 3. Immediate repeat answer should be consumed
        resp_repeat = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "选A", "session_id": session_id, "mode": "qa"},
        )
        self.assertEqual(resp_repeat.status_code, 200)
        self.assertIn("当前没有正在进行的随堂测试", resp_repeat.text)
        print("Scenario 2 (Quiz Grading & Atomic Consumption): PASS")

    def test_03_quiz_stop(self):
        """Scenario 3: Stop quiz stops test and returns polite closing"""
        session_id = "test_sess_e2e_03"
        client = TestClient(app)
        resp = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "停止出题练习", "session_id": session_id, "mode": "qa"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("已停止出题练习", resp.text)
        print("Scenario 3 (Quiz Stop): PASS")

    def test_04_scenario_engineer_flow(self):
        """Scenario 4: Scenario start engineer -> question answering in persona"""
        session_id = "test_sess_e2e_04"
        client = TestClient(app)
        
        # 1. Start scenario
        resp1 = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "扮演储能电厂运维师傅与我对话", "session_id": session_id, "mode": "qa"},
        )
        self.assertEqual(resp1.status_code, 200)
        self.assertIn("session_state", resp1.text)
        self.assertIn("储能电站现场运维师傅", resp1.text)

        # 2. Ask persona-specific technical question
        async def mock_persona_stream(*args, **kwargs):
            yield {"event": "token", "data": {"text": "小同志，PCS过温排查第一步先看水冷循环泵和风机滤网！", "request_id": "req_2"}}
            yield {"event": "done", "data": {"request_id": "req_2"}}

        with patch("app.main.xingchen_stream", side_effect=mock_persona_stream):
            resp2 = client.post(
                "/api/course-agent/chat",
                headers=HEADERS,
                json={"question": "PCS变流器报过温故障怎么排查？", "session_id": session_id, "mode": "qa"},
            )
            self.assertEqual(resp2.status_code, 200)
            self.assertIn("event: token", resp2.text)
            self.assertIn("PCS过温排查", resp2.text)
            print("Scenario 4 (Engineer Scenario Flow): PASS")

    def test_05_scenario_stop(self):
        """Scenario 5: Scenario stop resets scene_mode to 0"""
        session_id = "test_sess_e2e_05"
        client = TestClient(app)
        # Start
        client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "扮演储能电厂运维师傅与我对话", "session_id": session_id, "mode": "qa"},
        )
        # Stop
        resp = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "退出情景演绎", "session_id": session_id, "mode": "qa"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('"scene_mode": 0', resp.text)
        self.assertIn("已停止情景演绎", resp.text)
        print("Scenario 5 (Scenario Stop): PASS")

    def test_06_scenario_teacher_flow(self):
        """Scenario 6: Teacher scenario start"""
        session_id = "test_sess_e2e_06"
        client = TestClient(app)
        resp = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "扮演主讲老师授课", "session_id": session_id, "mode": "qa"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("《电力系统储能技术》主讲老师", resp.text)
        self.assertIn('"scene_mode": 2', resp.text)
        print("Scenario 6 (Teacher Scenario Flow): PASS")

    def test_07_quoted_text_precedence(self):
        """Scenario 7: Quoted text takes absolute precedence over quiz option input"""
        session_id = "test_sess_e2e_07"
        client = TestClient(app)
        uid = stable_uid("demo-student-e2e")
        
        # Active quiz in session
        import asyncio
        asyncio.run(
            teaching_state_manager.set_active_quiz(
                uid,
                session_id,
                {
                    "stem": "储能变流器主要功能是什么？",
                    "correct_answer": "B",
                    "courseware": "3.4 储能变流器拓扑及并网控制.pdf P12",
                    "explanation": "储能变流器实现交直流能量双向变换与并网控制。",
                },
            )
        )
        
        async def mock_quote_stream(*args, **kwargs):
            yield {"event": "token", "data": {"text": "针对您引用的虚拟同步机下垂方程解析如下...", "request_id": "req_3"}}
            yield {"event": "done", "data": {"request_id": "req_3"}}

        with patch("app.main.xingchen_stream", side_effect=mock_quote_stream):
            resp = client.post(
                "/api/course-agent/chat",
                headers=HEADERS,
                json={
                    "question": "B",
                    "quoted_text": "构网型变流器虚拟同步机下垂方程",
                    "session_id": session_id,
                    "mode": "qa",
                },
            )
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("回答正确", resp.text)
            self.assertNotIn("回答错误", resp.text)
            self.assertIn("针对您引用的虚拟同步机下垂方程解析如下", resp.text)
            print("Scenario 7 (Quoted Text Precedence): PASS")

    def test_08_interactive_diagnosis_e2e_full_flow(self):
        """Scenario 8: Multi-step interactive diagnosis from Q1 -> Q2 -> Q3 -> Comprehensive Report"""
        session_id = "test_sess_e2e_08_diag"
        client = TestClient(app)

        # 1. Start diagnosis
        resp1 = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "进行学情诊断", "session_id": session_id, "mode": "qa"}
        )
        self.assertEqual(resp1.status_code, 200)
        self.assertIn("【学情诊断测评】", resp1.text)
        self.assertIn("【学情诊断测评 第 1/3 题 - 基础原理与应用】", resp1.text)
        self.assertIn('"scene_mode": 4', resp1.text)
        self.assertIn('"correct_answer": "B"', resp1.text)

        # 2. Answer Question 1 (B - correct)
        resp2 = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "B", "session_id": session_id, "mode": "qa"}
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertIn("第 1 题作答已记录", resp2.text)
        self.assertIn("【学情诊断测评 第 2/3 题 - 变流器控制机理】", resp2.text)
        self.assertIn('"is_correct": true', resp2.text)
        self.assertIn('"scene_mode": 4', resp2.text)

        # 3. Answer Question 2 (A - wrong)
        resp3 = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "我选A", "session_id": session_id, "mode": "qa"}
        )
        self.assertEqual(resp3.status_code, 200)
        self.assertIn("第 2 题作答已记录", resp3.text)
        self.assertIn("【学情诊断测评 第 3/3 题 - 规划配置与综合评估】", resp3.text)
        self.assertIn('"is_correct": false', resp3.text)

        # 4. Answer Question 3 (C - correct) -> Triggers Final Diagnosis Synthesis
        resp4 = client.post(
            "/api/course-agent/chat",
            headers=HEADERS,
            json={"question": "C", "session_id": session_id, "mode": "qa"}
        )
        self.assertEqual(resp4.status_code, 200)
        full_text4 = "".join([
            json.loads(line.replace("data:", "").strip()).get("text", "")
            for line in resp4.text.split("\n")
            if line.startswith("data:") and '"text"' in line
        ])
        self.assertIn("《电力系统储能技术》学情诊断综合报告", full_text4)
        self.assertIn("总测评题数**：3 题", full_text4)
        self.assertIn("正确作答数**：2 题", full_text4)
        self.assertIn("66.7%", full_text4)
        self.assertIn("错题考点：3.4 储能变流器拓扑及并网控制", full_text4)
        self.assertIn("专属靶向复习路径与课件直达推荐", full_text4)
        self.assertIn('"scene_mode": 0', resp4.text)
        self.assertIn('"reason": "interactive_diagnosis_completed"', resp4.text)
        print("Scenario 8 (Interactive Diagnosis 3-Step Flow & Report): PASS")


if __name__ == "__main__":
    unittest.main()
