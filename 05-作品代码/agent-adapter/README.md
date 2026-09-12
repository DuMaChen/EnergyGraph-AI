# Agent Adapter

Adapter 是 Moodle 和讯飞星辰 Workflow 之间唯一的服务端入口。它不把 API
Key/Secret 发给浏览器，也不接受浏览器直接提交的知识图谱上下文、成绩或
评分规则。

## 本地协议测试

```bash
export MOCK_AUTH_MODE=true
export MOCK_WORKFLOW_MODE=true
export AGENT_UID_SALT=local-test-salt
export COURSE_DB=/tmp/course-agent.db
PYTHONPATH=agent-adapter uvicorn app.main:app --host 127.0.0.1 --port 8081
```

请求头可使用 `X-Dev-Role: student` 和 `X-Dev-User: demo-student`，仅在
`MOCK_AUTH_MODE=true` 时生效。生产环境必须关闭 Mock 鉴权，使用 Moodle
session bridge。

## API 约束

- 普通 JSON 使用 `{request_id,status,data,error}` 包络。
- Agent 流式输出只有 `token/source/done/error` SSE 事件。
- 来源必须匹配挂载 manifest 的人类可读文件名和页码范围。
- 课程状态写操作携带 `Idempotency-Key`；学生提交还会按用户、作业和尝试次数限制。
- `agent_data` SQLite 卷保存图谱、教材映射、题目、成绩、场景和知识库版本。
- 情景轮次同时保存学生输入、Workflow 回答、来源证据和完成状态；失败的
  pending 轮次会被清理后才能重试，已完成轮次不会被第二次上游调用覆盖。
- 最终成绩经 Adapter 调用 Moodle 内网 grade bridge 回写；真实环境需要配置
  `AGENT_BRIDGE_TOKEN`，回写失败会以明确错误返回，不能静默当作同步成功。

讯飞 Workflow 请求格式遵循官方接口：
`POST /workflow/v1/chat/completions`，请求体含 `flow_id`、伪匿名 `uid`、
`parameters` 和 `stream=true`，鉴权头由服务端拼接。
