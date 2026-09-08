#!/usr/bin/env python3
"""
Comprehensive Live Goal Evaluation & Test Suite
Executes 4 distinct 5+ turn sessions against the live backend / API.
Captures full token streams, citations, latency, state transitions, and evaluates response quality.
"""
import asyncio
import json
import os
import time
import httpx

BASE_URL = "https://energygraph.icu"
LOGIN_URL = f"{BASE_URL}/login/index.php"
CHAT_URL = f"{BASE_URL}/api/course-agent/chat"
SESSION_URL = f"{BASE_URL}/local/course_agent/session.php"

def _student_password() -> str:
    pw = os.getenv("MOODLE_STUDENT_PASSWORD", "")
    if not pw:
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "deploy", ".env")
        try:
            with open(env_file, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("MOODLE_STUDENT_PASSWORD="):
                        pw = line.split("=", 1)[1].strip().strip('"')
                        break
        except OSError:
            pass
    if not pw:
        raise SystemExit("MOODLE_STUDENT_PASSWORD 未设置（环境变量或 deploy/.env）；安全整改 2026-09 移除内嵌密码")
    return pw

async def login_and_get_session(username="student", password=None):
    password = password or _student_password()
    async with httpx.AsyncClient(verify=False, timeout=30.0, follow_redirects=True) as client:
        # 1. Fetch login page to get logintoken
        resp = await client.get(LOGIN_URL)
        token = ""
        for line in resp.text.split("\n"):
            if 'name="logintoken"' in line:
                parts = line.split('value="')
                if len(parts) > 1:
                    token = parts[1].split('"')[0]
                    break
        
        # 2. Post credentials
        login_resp = await client.post(
            LOGIN_URL,
            data={
                "anchor": "",
                "logintoken": token,
                "username": username,
                "password": password
            }
        )
        
        # 3. Fetch session
        sess_resp = await client.post(SESSION_URL)
        session_info = sess_resp.json()
        
        # Get cookies
        cookies = dict(client.cookies)
        return cookies, session_info

async def send_chat_message(client, cookies, sess_info, question, session_id, mode="qa", quoted_text=None, messages=None):
    headers = {
        "Content-Type": "application/json",
        "X-Moodle-Sesskey": sess_info.get("sesskey", "")
    }
    payload = {
        "question": question,
        "session_id": session_id,
        "mode": mode,
    }
    if quoted_text:
        payload["quoted_text"] = quoted_text
    if messages:
        payload["messages"] = messages
        
    start_time = time.time()
    tokens = []
    events = []
    sources = []
    quiz_meta = None
    quiz_graded = None
    session_state = None
    
    async with client.stream("POST", CHAT_URL, json=payload, headers=headers, cookies=cookies, timeout=90.0) as resp:
        buffer = ""
        async for line in resp.aiter_lines():
            buffer += line + "\n"
            if line.startswith("event:"):
                ev_type = line.replace("event:", "").strip()
            elif line.startswith("data:"):
                data_str = line.replace("data:", "").strip()
                try:
                    data = json.loads(data_str)
                    events.append({"event": ev_type, "data": data})
                    if ev_type == "token":
                        tokens.append(data.get("text", ""))
                    elif ev_type == "source":
                        sources.append(data)
                    elif ev_type == "quiz_meta":
                        quiz_meta = data
                    elif ev_type == "quiz_graded":
                        quiz_graded = data
                    elif ev_type == "session_state":
                        session_state = data
                except Exception:
                    pass
                    
    duration = time.time() - start_time
    full_text = "".join(tokens)
    return {
        "duration": duration,
        "full_text": full_text,
        "events": events,
        "sources": sources,
        "quiz_meta": quiz_meta,
        "quiz_graded": quiz_graded,
        "session_state": session_state
    }

async def run_session_1(cookies, sess_info):
    """Session 1: Deep QA & Engineering Concept Verification (5 turns)"""
    print("\n" + "="*70)
    print("SESSION 1: Deep QA & Engineering Calculation (5 Turns)")
    print("="*70)
    client = httpx.AsyncClient(verify=False, timeout=90.0)
    session_id = f"eval_s1_{int(time.time())}"
    history = []
    
    turns = [
        ("第1问: 储能变流器(PCS)拓扑与控制", "请详细讲解双向储能变流器（PCS）在储能电站中的拓扑结构（如三相电压型桥式逆变器）及其工作原理，给出交直流侧电压与调制比的关系式。"),
        ("第2问: 构网型(GFM)与跟网型(GFL)控制", "在新能源高比例并网与弱电网环境下，构网型（GFM）与跟网型（GFL）储能变流器的核心控制差异是什么？请从锁相环（PLL）、电压源/电流源特性及暂态同步稳定性展开深入对比。"),
        ("第3问: 虚拟同步发电机(VSG)数学建模", "请推导虚拟同步发电机（VSG）的有功-频率和无功-电压控制方程，说明转动惯量J和阻尼系数D对电网暂态频率支撑的具体影响机理。"),
        ("第4问: 电池全寿命周期衰减与热失控机理", "锂离子电池在长期充放电循环中容量衰减的微观物理化学机理是什么？当发生热失控时，SEI膜分解、正负极反应及可燃气体释放的演变过程是怎样的？"),
        ("第5问: 电网一次调频下垂控制与容量配置", "储能系统参与电网一次调频时，下垂控制系数与死区参数应如何设置？如何通过充放电状态（SOC）自适应调整调频出力，防止过充过放？")
    ]
    
    results = []
    for label, prompt in turns:
        print(f"\n---> [S1] {label}")
        res = await send_chat_message(client, cookies, sess_info, prompt, session_id, mode="qa", messages=history)
        print(f"Latency: {res['duration']:.2f}s | Output Chars: {len(res['full_text'])} | Sources: {len(res['sources'])}")
        print(f"Sample Output:\n{res['full_text'][:300]}...\n")
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": res['full_text']})
        results.append({"turn": label, "prompt": prompt, "result": res})
        await asyncio.sleep(1)
        
    await client.aclose()
    return results

async def run_session_2(cookies, sess_info):
    """Session 2: Unlimited Interactive Learning Diagnosis Flow (5 turns)"""
    print("\n" + "="*70)
    print("SESSION 2: Unlimited Interactive Diagnosis Flow (5 Turns)")
    print("="*70)
    client = httpx.AsyncClient(verify=False, timeout=90.0)
    session_id = f"eval_s2_{int(time.time())}"
    history = []
    
    results = []
    
    # Turn 1: Start diagnosis
    print("\n---> [S2] Turn 1: 启动互动学情诊断")
    res1 = await send_chat_message(client, cookies, sess_info, "进行学情诊断", session_id, mode="qa")
    print(f"Latency: {res1['duration']:.2f}s | Output Chars: {len(res1['full_text'])} | Quiz Meta: {bool(res1['quiz_meta'])}")
    print(f"Question 1 Text:\n{res1['full_text']}\n")
    results.append({"turn": "Turn 1: Start Diagnosis", "prompt": "进行学情诊断", "result": res1})
    
    # Turn 2: Answer Q1
    q1_opt = (res1['quiz_meta'] or {}).get("correct") or "B"
    print(f"\n---> [S2] Turn 2: 作答第 1 题 (选择 {q1_opt})")
    res2 = await send_chat_message(client, cookies, sess_info, q1_opt, session_id, mode="qa")
    print(f"Latency: {res2['duration']:.2f}s | Output Chars: {len(res2['full_text'])} | Quiz Meta: {bool(res2['quiz_meta'])}")
    print(f"Q1 Feedback & Q2 Output:\n{res2['full_text']}\n")
    results.append({"turn": "Turn 2: Answer Q1", "prompt": q1_opt, "result": res2})
    
    # Turn 3: Answer Q2
    q2_opt = (res2['quiz_meta'] or {}).get("correct") or "C"
    print(f"\n---> [S2] Turn 3: 作答第 2 题 (选择 {q2_opt})")
    res3 = await send_chat_message(client, cookies, sess_info, q2_opt, session_id, mode="qa")
    print(f"Latency: {res3['duration']:.2f}s | Output Chars: {len(res3['full_text'])} | Quiz Meta: {bool(res3['quiz_meta'])}")
    print(f"Q2 Feedback & Q3 Output:\n{res3['full_text']}\n")
    results.append({"turn": "Turn 3: Answer Q2", "prompt": q2_opt, "result": res3})
    
    # Turn 4: Answer Q3
    q3_opt = (res3['quiz_meta'] or {}).get("correct") or "A"
    print(f"\n---> [S2] Turn 4: 作答第 3 题 (选择 {q3_opt})")
    res4 = await send_chat_message(client, cookies, sess_info, q3_opt, session_id, mode="qa")
    print(f"Latency: {res4['duration']:.2f}s | Output Chars: {len(res4['full_text'])} | Quiz Meta: {bool(res4['quiz_meta'])}")
    print(f"Q3 Feedback & Q4 Output:\n{res4['full_text']}\n")
    results.append({"turn": "Turn 4: Answer Q3", "prompt": q3_opt, "result": res4})
    
    # Turn 5: Generate Report
    print("\n---> [S2] Turn 5: 生成学情诊断综合报告")
    res5 = await send_chat_message(client, cookies, sess_info, "生成诊断报告", session_id, mode="qa")
    print(f"Latency: {res5['duration']:.2f}s | Report Length: {len(res5['full_text'])}")
    print(f"Diagnostic Report Output:\n{res5['full_text']}\n")
    results.append({"turn": "Turn 5: Generate Report", "prompt": "生成诊断报告", "result": res5})
    
    await client.aclose()
    return results

async def run_session_3(cookies, sess_info):
    """Session 3: Scenario Roleplay & Practical Troubleshooting (5 turns)"""
    print("\n" + "="*70)
    print("SESSION 3: Scenario Roleplay & Practical Troubleshooting (5 Turns)")
    print("="*70)
    client = httpx.AsyncClient(verify=False, timeout=90.0)
    session_id = f"eval_s3_{int(time.time())}"
    history = []
    
    turns = [
        ("Turn 1: 进入电站师傅演练", "师傅情景演练"),
        ("Turn 2: 电池舱绝缘低与单体压差故障", "报告师傅！现场 3 号集装箱储能舱报出直流母线对地正极绝缘阻抗过低告警（<500Ω/V），且 2 号电池簇中第 14 号单体电芯压差达到 180mV，请问现场应急处置和排查步骤是什么？"),
        ("Turn 3: PCS变流柜IGBT过流与过压", "师傅，变流器 PCS 柜在电网电压突降时触发了 IGBT 桥臂硬件过流封锁，直流母线电压出现瞬时泵升，我们应该如何排查硬件吸收回路、驱动保护与控制策略？"),
        ("Turn 4: 全钒液流电池电解液与管路故障", "如果是全钒液流电池储能电站，巡检发现正极储液罐管路压力骤降、电解液颜色发生异常且伴随微量析氢，应该如何排查离子传导膜、循环泵及自放电故障？"),
        ("Turn 5: 结束演练并总结", "退出演练")
    ]
    
    results = []
    for label, prompt in turns:
        print(f"\n---> [S3] {label}")
        res = await send_chat_message(client, cookies, sess_info, prompt, session_id, mode="qa", messages=history)
        print(f"Latency: {res['duration']:.2f}s | Output Chars: {len(res['full_text'])} | Session State: {res['session_state']}")
        print(f"Sample Output:\n{res['full_text'][:300]}...\n")
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": res['full_text']})
        results.append({"turn": label, "prompt": prompt, "result": res})
        await asyncio.sleep(1)
        
    await client.aclose()
    return results

async def run_session_4(cookies, sess_info):
    """Session 4: Single Quiz, Quoted Selection & Deep Pedagogical Socratic Study (5 turns)"""
    print("\n" + "="*70)
    print("SESSION 4: Single Quiz, Quoted Text & Multi-turn Pedagogical Study (5 Turns)")
    print("="*70)
    client = httpx.AsyncClient(verify=False, timeout=90.0)
    session_id = f"eval_s4_{int(time.time())}"
    history = []
    
    results = []
    
    # Turn 1: Single Quiz
    print("\n---> [S4] Turn 1: 请求随堂自测单选题")
    res1 = await send_chat_message(client, cookies, sess_info, "出题考考我", session_id, mode="qa")
    print(f"Latency: {res1['duration']:.2f}s | Quiz Meta: {bool(res1['quiz_meta'])}")
    print(f"Quiz Output:\n{res1['full_text']}\n")
    results.append({"turn": "Turn 1: Request Quiz", "prompt": "出题考考我", "result": res1})
    
    # Turn 2: Submit Quiz Answer
    ans = (res1['quiz_meta'] or {}).get("correct") or "B"
    print(f"\n---> [S4] Turn 2: 提交单选题作答 ({ans})")
    res2 = await send_chat_message(client, cookies, sess_info, ans, session_id, mode="qa")
    print(f"Latency: {res2['duration']:.2f}s | Graded Event: {bool(res2['quiz_graded'])}")
    print(f"Grading Output:\n{res2['full_text']}\n")
    results.append({"turn": "Turn 2: Submit Answer", "prompt": ans, "result": res2})
    
    # Turn 3: Quoted selection followup
    quote = "构网型变流器（Grid-Forming, GFM）通过模拟同步发电机的转子运动方程与无功下垂特性，自主建立交流电网电压与频率支撑。"
    print(f"\n---> [S4] Turn 3: 划词精准追问 (引用: {quote[:30]}...)")
    res3 = await send_chat_message(client, cookies, sess_info, "请问在黑启动场景下，构网型变流器是如何实现无电网电压基准下的空载线路与变压器励磁投切的？", session_id, mode="qa", quoted_text=quote)
    print(f"Latency: {res3['duration']:.2f}s | Sources: {len(res3['sources'])}")
    print(f"Quoted Response:\n{res3['full_text'][:300]}...\n")
    results.append({"turn": "Turn 3: Quoted Followup", "prompt": "黑启动励磁投切", "result": res3})
    
    # Turn 4: Courseware Deep Linking Inquiry
    print("\n---> [S4] Turn 4: 课件溯源与工程算例提问")
    res4 = await send_chat_message(client, cookies, sess_info, "这部分知识在咱们课程的哪份课件第几页有详细推导？能否结合课件给出一个 100MW/200MWh 储能电站的典型算例？", session_id, mode="qa")
    print(f"Latency: {res4['duration']:.2f}s | Sources: {len(res4['sources'])}")
    print(f"Courseware Citation Response:\n{res4['full_text'][:300]}...\n")
    results.append({"turn": "Turn 4: Courseware Deep Dive", "prompt": "课件溯源与算例", "result": res4})
    
    # Turn 5: Chapter Synthesis & Concept Map
    print("\n---> [S4] Turn 5: 章节总结与思维导图关联")
    res5 = await send_chat_message(client, cookies, sess_info, "请帮我总结第3章和第4章知识点之间的逻辑递进关系，说明从电化学储能本体到变流器并网控制的核心学习路径。", session_id, mode="qa")
    print(f"Latency: {res5['duration']:.2f}s")
    print(f"Synthesis Output:\n{res5['full_text'][:300]}...\n")
    results.append({"turn": "Turn 5: Chapter Synthesis", "prompt": "章节逻辑递进与学习路径", "result": res5})
    
    await client.aclose()
    return results

async def main():
    cookies, sess_info = await login_and_get_session()
    print(f"Logged in as {sess_info.get('username')} (ID={sess_info.get('user_id')}, Fullname={sess_info.get('fullname')})")
    
    s1_results = await run_session_1(cookies, sess_info)
    s2_results = await run_session_2(cookies, sess_info)
    s3_results = await run_session_3(cookies, sess_info)
    s4_results = await run_session_4(cookies, sess_info)
    
    # Output evaluation summary
    all_runs = {
        "session_1": s1_results,
        "session_2": s2_results,
        "session_3": s3_results,
        "session_4": s4_results,
    }
    
    with open("/tmp/goal_eval_results.json", "w", encoding="utf-8") as f:
        # Filter raw objects for serialization
        serializable = {}
        for k, v in all_runs.items():
            serializable[k] = [
                {
                    "turn": r["turn"],
                    "prompt": r["prompt"],
                    "duration": r["result"]["duration"],
                    "output_len": len(r["result"]["full_text"]),
                    "text_sample": r["result"]["full_text"][:500],
                    "sources_count": len(r["result"]["sources"]),
                    "quiz_meta": bool(r["result"]["quiz_meta"]),
                    "quiz_graded": bool(r["result"]["quiz_graded"]),
                    "session_state": r["result"]["session_state"]
                }
                for r in v
            ]
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print("\nSaved evaluation results to /tmp/goal_eval_results.json")

if __name__ == "__main__":
    asyncio.run(main())
