# 复现指南（REPRODUCTION）

> 目标：在一台全新服务器上从本目录复现《电力系统储能技术》AI Agent 教学平台并完成验收。
> 代码基准：本仓库 `05-作品代码/`（main 分支，2026-09 安全整改与教师端修复后）
> 预计耗时：30-45 分钟（含镜像构建；不含讯飞工作流申请审批时间）

---

## 1. 前置要求

- Linux 服务器（2C4G 起），Docker Engine ≥ 24 与 docker compose v2 插件；
- 80/443 端口空闲（域名可选，首次冒烟可先用 IP）；
- **外部依赖（唯一）**：讯飞星辰智能体平台账号与已发布工作流（AppID `1a31e771`，FlowID `7494978072491315200`；或自建等价工作流，分支结构见 `docs/OPERATIONS.md` 与 `PROJECT_STATUS.md`）。

## 2. 步骤

```bash
# 1) 获取代码（克隆本仓库或下载 ZIP 后进入 05-作品代码）
git clone git@github.com:DuMaChen/EnergyGraph-AI.git
cd EnergyGraph-AI/05-作品代码

# 2) 配置 deploy/.env（模板 deploy/.env.example，逐项替换）
cd deploy && cp .env.example .env && chmod 600 .env
```

必填项（三类）：

| 类别 | 变量 | 说明 |
| :--- | :--- | :--- |
| 站点 | `SITE_HOST` / `MOODLE_WWWROOT` | 域名或 IP（HTTPS 由 Caddy 自动签发） |
| 随机密钥（自行生成，如 `openssl rand -hex 32`） | `MARIADB_PASSWORD`、`MARIADB_ROOT_PASSWORD`、`MOODLE_ADMIN_PASSWORD`、`AGENT_UID_SALT`、`AGENT_BRIDGE_TOKEN` | 任何真实密钥不得写入仓库/文档 |
| 大模型 | `XINGCHEN_WORKFLOW_URL`、`XINGCHEN_FLOW_ID`、`XINGCHEN_API_KEY`、`XINGCHEN_API_SECRET` | 来自讯飞星辰平台；教学功能由此驱动 |

SMTP 为可选（平台内置注册免邮件自动激活补丁）；`MOCK_*` 保持 `false` 即真实链路。

```bash
# 3) 构建并启动（五容器：caddy/moodle/agent-ui/agent-adapter/db）
docker compose build && docker compose up -d
docker compose ps          # 等待全部 healthy（首次约 3-5 分钟，含 Moodle 安装与种子课程）

# 4) 健康检查与验收
curl -f http://127.0.0.1/health                 # 适配器健康（经 Caddy: https://<SITE_HOST>/health）
bash scripts/xingchen_smoke.sh                  # 讯飞链路冒烟，期望 5/5
python3 -m unittest discover -s agent-adapter/tests   # 单测（27/30，3 例已知过期断言）

# 5) 功能验收（按 ../03-作品Demo/DEMO_GUIDE.md 体验路线）
#    student / teacher 登录 → 问答/单题/诊断/情景/批改/成绩册逐项验证
#    自动化：scripts/stress_test_and_eval.py（需设 AGENT_BRIDGE_TOKEN 环境变量）
```

## 3. 知识库与工作流复建（可选，复用团队服务则跳过）

1. 登录讯飞星辰平台，导入 20 份课程课件建立知识库；
2. 按技术方案发布工作流（问答/出题判题/学情汇报/情景多分支，输入参数名 `AGENT_USER_INPUT`），或用 `scripts/kb_release.py`（compose `--profile ingest`）做版本化发布；
3. 将新 FlowID/Key/Secret 更新到 `deploy/.env` 并 `docker compose up -d agent-adapter`。

## 4. 已知差异说明

- 普通问答回问候语/出题重复属讯飞控制台侧工作流配置问题（2026-09-12 已修复实测全通），代码侧含识别-复位-重试与答案探针兜底；
- 首次启动 Moodle 自动安装并种子课程（`MOODLE_SEED_COURSE=true`）；预置 teacher/student 账号口令以部署时手册为准；
- 课件原始 PDF（版权材料）不入库，运行时挂载 `course-data/normalized/`（本地准备）。

## 5. 常见问题

| 现象 | 处置 |
| :--- | :--- |
| 容器启动慢/healthy 等待久 | 首次 Moodle 安装属正常；`docker compose logs -f moodle` 观察 |
| 冒烟脚本鉴权失败 | 核对 `.env` 的 `XINGCHEN_API_KEY/SECRET` 与 FlowID 是否为已发布工作流 |
| 成绩未回写 | 见 `docs/OPERATIONS.md` 成绩链路排查（人工成绩项必须走 `update_final_grade`） |
