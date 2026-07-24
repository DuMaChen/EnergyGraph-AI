# 电力系统储能技术课程 Agent 平台

这是“课程平台 + 讯飞星辰 Agent + 课程知识库 + 教学场景”竞赛 Demo 的当前版本。

## 当前版本

- Moodle 课程平台：6 个章节、20 份课件
- 课程数据：20 个 PDF、439 页、20 个知识点、17 条图谱关系
- Agent Adapter：负责 Moodle 会话、权限、CSRF、限流、幂等、流式转发和来源校验
- Agent UI：课程问答、知识图谱、教材、作业、批改、学情和情景入口
- 部署：Docker Compose、MariaDB、Caddy；服务器端密钥不进入仓库
- 自动化验收：`LOCAL-ACCEPTANCE_OK`

## 预览

- 课程平台：<http://168.144.36.82/>
- Agent 页面：<http://168.144.36.82/agent/>

当前预览使用 IP + HTTP。正式提交前仍需配置域名、HTTPS 和真实讯飞星辰 Workflow。

## 快速开始

```bash
cp deploy/.env.example deploy/.env
# 修改 deploy/.env 中的示例密码和服务配置
docker compose --project-directory deploy --env-file deploy/.env config
docker compose --project-directory deploy --env-file deploy/.env up -d --build db moodle agent-adapter agent-ui caddy
bash scripts/smoke_acceptance.sh
```

本地完整回归：

```bash
RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh
```

## 真实 Workflow 前置条件

需要在服务器端 `deploy/.env` 配置以下变量，不能提交到 GitHub：

```text
XINGCHEN_WORKFLOW_URL
XINGCHEN_FLOW_ID
XINGCHEN_API_KEY
XINGCHEN_API_SECRET
XINGCHEN_INPUT_NAME
```

配置后先运行：

```bash
bash scripts/real_workflow_preflight.sh deploy/.env
bash scripts/pre_submission_audit.sh
```

## 文档

- 实施与验收计划：`IMPLEMENTATION_PLAN.md`
- 部署说明：`deploy/README.md`
- 自动化和人工验收报告：`acceptance/`
- 提交材料目录：`01-参赛信息/` 至 `07-其他材料/`

真实星辰主链路、知识库命中、真实学生/教师验收和正式 Demo 材料尚未完成，不能把 Mock 结果当作最终竞赛证据。
