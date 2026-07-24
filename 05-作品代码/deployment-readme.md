# 电力系统储能技术课程 Agent 部署

本期主链路是 **Moodle + Agent Adapter + 讯飞星辰 Workflow**。Flowise、Qdrant
和旧的 OpenAI-compatible 网关保留在仓库中仅供历史实验，不能作为本期 Demo
的功能证据，也不会被 Caddy 暴露给普通用户。

## 1. 首次部署

```bash
cp .env.example .env
# 修改所有 replace-with-* 值；真实密钥只写入服务器端 .env
docker compose config
docker compose up -d --build db moodle agent-adapter agent-ui caddy
docker compose ps
```

服务器可达后，也可以从项目根目录执行 `bash scripts/deploy_server.sh`。该
脚本不会上传本地 `deploy/.env`，并会在远端缺少配置时主动停止。
部署结束时还会自动运行 `smoke_acceptance.sh` 和真实 Moodle 登录课程页
验收；登录验收会按课程短名称解析课程 ID，不依赖固定的数据库自增 ID。

首轮可以使用服务器 IP 的 HTTP 做联调。比赛展示前应改为域名并启用 Caddy
HTTPS，`MOODLE_WWWROOT` 必须与最终域名一致。

启用正式域名时，修改 `deploy/.env` 中的 `SITE_HOST` 和
`MOODLE_WWWROOT=https://你的域名`，再使用 HTTPS 覆盖文件重建 Caddy：

```bash
docker compose -f docker-compose.yml -f docker-compose.https.yml \
  --env-file .env up -d --build caddy moodle agent-adapter agent-ui
```

## 2. 课程数据

先在项目根目录修复 Windows/GBK 文件名并生成 manifest：

```bash
python3 scripts/prepare_course_data.py \
  --archive 教材课件分章节pdf版.zip \
  --output course-data/normalized --clean
python3 scripts/build_course_baseline.py \
  --xlsx '电力系统储能技术 知识图谱.xlsx' \
  --output course-data/normalized/graph-baseline.json
python3 scripts/export_xingchen_sources.py \
  --normalized course-data/normalized \
  --output course-data/xingchen-sources
```

manifest 保存人类可读文件名、归一化文件名、SHA-256、章节和页数。图谱
baseline 保存 6 章、20 个知识点、关系和导入错误；有错误时脚本返回非零，
不能带着不完整图谱发布。

`xingchen-sources/upload-manifest.json` 将每页文本前置来源标记，并按每批不
超过 10 个文件生成讯飞知识库上传清单。上传后需把实际平台知识库 ID 回填到
知识库版本记录，不能只保存本地批次名称。

Moodle 启动脚本会幂等创建课程和章节，并将归一化课件挂入对应章节。Adapter
使用持久化 `agent_data` 保存图谱、教材映射、作业、成绩、学情、场景和知识库
版本状态；容器重启不会重新生成一套不同的课程对象。

## 3. 讯飞 Workflow 配置

星辰工作流必须在控制台创建、调试并发布后再配置：

```text
XINGCHEN_WORKFLOW_URL=https://xingchen-api.xf-yun.com/workflow/v1/chat/completions
XINGCHEN_FLOW_ID=发布后的工作流 ID
XINGCHEN_API_KEY=Workflow API_KEY
XINGCHEN_API_SECRET=Workflow API_SECRET
XINGCHEN_INPUT_NAME=AGENT_USER_INPUT
```

最终成绩回写通过 Moodle 内网 bridge 完成。`AGENT_BRIDGE_TOKEN` 必须在 Moodle
和 Adapter 两个容器中配置为同一随机值；它不写入前端，且远程部署脚本会拒绝
空值或示例占位符。

Adapter 在服务端拼接 `Authorization: Bearer API_KEY:API_SECRET`，浏览器只
访问同源 `/api/course-agent/chat`。上游流式帧会转换为 `token`、`source`、
`done`、`error` 四类 SSE 事件；来源只有与 manifest 文件名和页码核验通过后
才会显示。

写操作由 Adapter 统一校验 Moodle `sesskey`；管理员可通过同源
`GET /api/admin/status` 查看脱敏的 Workflow、已发布知识库和备份核验提示，
该接口不会返回凭证或平台管理地址。知识库版本上传支持 `.pdf` 和 `.md`，原始
文件保存在 Adapter 数据卷，不进入前端静态目录。

官方接口说明：

- https://www.xfyun.cn/doc/spark/workflow.html
- https://www.xfyun.cn/doc/spark/Agent04-API%E6%8E%A5%E5%85%A5.html

没有真实 Workflow 凭证时可设 `MOCK_WORKFLOW_MODE=true` 做协议、权限、流式
页面和异常测试，但不能把 Mock 结果写入比赛验收报告。

获得凭证后，在服务器受控终端执行五次真实冒烟：

```bash
bash scripts/check_xingchen_config.sh deploy/.env
set -a; . deploy/.env; set +a
bash scripts/xingchen_smoke.sh
```

前置检查只输出配置项是否存在和最终状态，不会回显 API Key 或 API Secret。

## 4. 自动化验收

本地不依赖讯飞凭据的固定验收可以使用统一入口；脚本会按计划顺序执行
语法、课程数据、API 契约、权限、作业、知识库和 Mock 性能检查，并保留每一步
的标题和退出状态：

```bash
bash scripts/run_local_acceptance.sh
```

```bash
bash scripts/smoke_acceptance.sh
RUN_UP=1 bash scripts/smoke_acceptance.sh
```

Smoke 脚本只验收本期必需服务：MariaDB、Moodle、Adapter、课程页面和 Caddy。
它会检查 Compose、健康状态、公共路由、Adapter 健康检查和明显密钥泄露。
完整的图谱、作业、成绩、学情、场景和讯飞真实链路测试按
`IMPLEMENTATION_PLAN.md` 中的编号执行，并保存 request ID 和复测证据。

提交前可运行统一审计入口。它会以服务器端 `.env` 和站点 Host 为准检查外部
前置条件；条件不足时返回非零并列出阻断项，不会把本地 Mock 结果判为可提交：

```bash
bash scripts/pre_submission_audit.sh
```

最终提交材料目录可用以下脚本检查。它会保留缺失项并返回非零，不能用占位
README、Mock 输出或空文件替代正式 Demo、录屏和人工验收汇总：

```bash
bash scripts/check_submission_materials.sh
```

所有 `/api/*` 请求都必须由 Caddy 转发到 Adapter；Adapter 再通过 Moodle
session bridge 校验角色和 `sesskey`。如果只配置 `/api/course-agent/*`，图谱、
教材、作业、场景和知识库接口会错误落到 Moodle，属于部署阻断问题。

本地 Mock 回归可运行：

```bash
PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_adapter_runtime.py
PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_acceptance_fixture.py
PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_kb_lifecycle.py
```

## 5. 备份

```bash
bash scripts/backup.sh /var/backups/jbgs-course-agent
bash scripts/verify_backup.sh /var/backups/jbgs-course-agent/<timestamp>
```

备份包括 MariaDB、Moodle data、Agent SQLite、课程 manifest/图谱基线和
Caddy 状态，但不复制明文 `deploy/.env`。恢复必须在另一套环境演练，不能
只检查压缩包存在。

服务器上可使用隔离恢复演练脚本验证备份内容；脚本会创建临时 MariaDB 和
临时目录，导入课程数据库并检查课程、用户、知识点、Moodle 文件树和 Caddy
状态，退出时自动清理临时资源：

```bash
bash scripts/restore_rehearsal.sh /opt/jbgs-course-agent/backups/<timestamp>
```

需要验证完整服务启动时，使用独立 Compose project 的恢复演练。它会恢复
数据库和持久化卷，启动 db、Moodle、Agent Adapter、UI 和 Caddy；Caddy 不绑定
宿主机端口，退出时自动删除临时容器、网络和卷：

```bash
bash scripts/full_restore_rehearsal.sh /opt/jbgs-course-agent/backups/<timestamp>
```

该演练证明本地服务可以从备份重新启动，不替代讯飞知识库重新绑定、真实凭证
配置、人工登录和正式案例复跑。

## 6. 维护入口

Flowise 等历史服务即使启动，也只在 Docker 内网可见。普通参赛用户只访问
Moodle 课程和 `/agent/` 页面；管理员操作必须走 Moodle 登录态和服务端角色
校验，不能因为前端隐藏按钮就放行。
