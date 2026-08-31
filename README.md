# 电力系统储能技术课程 AI Agent 平台 (EnergyGraph-AI)

> 基于 Moodle + 讯飞星辰 Workflow + 知识图谱 + 智能教学场景的“电力系统储能技术”课程 Agent 平台与竞赛交付系统。
> 本项目已接入 [Trellis](https://github.com/mindfold-ai/Trellis) AI Agent 协同工程框架，提供端到端标准化 Spec 规范与多智能体工作流。

---

## 🌟 核心特性与架构

- **Moodle 教学平台集成**：Moodle 4.5 LMS 深度集成，涵盖 6 个章节、20 份课件、学生/教师/管理员三角色权限体系。
- **课程知识图谱与数字教材**：20 个专业 PDF、439 页深度教材切片、20 个核心知识点与 17 条前后序及包含关系拓扑。
- **FastAPI 适配器中间件 (`agent-adapter`)**：提供 Moodle 会话透传、RBAC 鉴权、CSRF 防护、令牌桶限流、幂等校验、实时 SSE 流式转发与知识溯源引用校验。
- **沉浸式交互前端 (`agent-ui`)**：采用智慧树/学习通风格设计，支持实时 Markdown/LaTeX 数学公式渲染、交互式知识图谱可视化、在线随堂测验与教师智能批改工作台。
- **生产级云端部署**：基于 Docker Compose、MariaDB 10.11 与 Caddy 2 自动 HTTPS 证书（线上地址：[https://energygraph.icu](https://energygraph.icu)）。
- **Trellis 工程规范**：在 `.trellis/` 中持久化后端、前端、部署、测试和知识图谱规范，无缝赋能 Claude Code、Antigravity、Cursor、Codex 等 AI 智能体协同开发。

---

## 🚀 线上预览

- **生产环境 (HTTPS)**：[https://energygraph.icu](https://energygraph.icu)
- **Agent 交互工作台**：[https://energygraph.icu/agent/](https://energygraph.icu/agent/)
- **备用 IP 预览**：<http://168.144.36.82/>

---

## 🛠️ 快速开始

### 1. 本地容器化启动

```bash
# 复制环境变量配置模版
cp deploy/.env.example deploy/.env

# 校验 Docker Compose 配置
docker compose --project-directory deploy --env-file deploy/.env config

# 启动核心服务集群
docker compose --project-directory deploy --env-file deploy/.env up -d --build db moodle agent-adapter agent-ui caddy

# 运行基础冒烟验收
bash scripts/smoke_acceptance.sh
```

### 2. 本地确定性验收套件

```bash
# 执行本地全链路回归套件
bash scripts/run_local_acceptance.sh

# 开启本地 HTTP Fixture 进行闭环测试
RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh
```

---

## 🔑 讯飞星辰 Workflow 接入

生产环境下需在服务器 `deploy/.env` 中配置以下凭据（严禁提交到代码仓库）：

```text
XINGCHEN_WORKFLOW_URL=https://xingchen-api.xf-yun.com/workflow/v1/chat/completions
XINGCHEN_FLOW_ID=your-flow-id
XINGCHEN_API_KEY=your-api-key
XINGCHEN_API_SECRET=your-api-secret
XINGCHEN_INPUT_NAME=AGENT_USER_INPUT
```

配置完成后执行预检审计：

```bash
bash scripts/real_workflow_preflight.sh deploy/.env
bash scripts/pre_submission_audit.sh
```

---

## 📚 目录与规范索引

- **Trellis 规范体系**：[`.trellis/spec/`](.trellis/spec/)
  - [后端架构规范](.trellis/spec/backend/)
  - [前端交互规范](.trellis/spec/frontend/)
  - [运维与部署指南](.trellis/spec/guides/deployment-and-ops.md)
  - [验收测试指南](.trellis/spec/guides/testing-and-acceptance.md)
- **实施与验收计划**：[`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md)
- **项目状态快照**：[`PROJECT_STATUS.md`](PROJECT_STATUS.md)
- **竞赛申报材料**：`01-参赛信息/` 至 `07-其他材料/`

