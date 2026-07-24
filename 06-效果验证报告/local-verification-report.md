# 本地验证报告

## 范围

本报告只记录可以在当前工作区独立复现的代码、数据和协议验证，不把 Mock
结果当作讯飞真实主链路验收。测试日期：2026-07-22；最新全量运行号：
`local-regression-20260722-primary-v6`。

## 已通过

| 项目 | 命令/证据 | 结果 |
|---|---|---|
| 课程数据 | `python3 scripts/verify_course_data.py course-data/normalized` | 20 个 PDF、439 页、20 个知识点、17 条关系 |
| API 静态契约 | `python3 scripts/test_api_contract.py` | 通过；Adapter 路由和 HTTP/HTTPS Caddy API 前缀均存在 |
| 新增教学 API | `python3 scripts/test_api_contract.py`、`scripts/test_adapter_runtime.py` | 通过；知识点资源、教师学生学情接口存在，学生越权返回 403 |
| Store 规则 | `python3 -m unittest -v scripts.test_course_store` | 5/5 通过 |
| Adapter 协议 | `PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_adapter_runtime.py` | 通过 |
| Moodle 成绩 bridge 契约 | `agent-adapter/tests/test_main.py::test_moodle_grade_bridge_is_server_side_and_bounded` | 通过伪造 bridge 验证令牌、Cookie 和分数上限；未替代真实 Moodle 回写 |
| 讯飞 Workflow 协议夹具 | `PYTHONPATH=/tmp/jbgs-agent-deps:agent-adapter python3 -m unittest -v agent-adapter/tests/test_main.py` | 10/10 通过；覆盖官方结束帧、跨帧来源、Bearer 请求、讯飞错误码、未发布知识库阻断、请求体上限和策略边界；不替代真实网络验收 |
| 讯飞 Workflow HTTP 端到端夹具 | `RUN_HTTP_FIXTURE=1 PYTHONPATH=/tmp/jbgs-agent-deps bash scripts/run_local_acceptance.sh` | 通过；真实回环 HTTP 验证请求序列化、Authorization、SSE、来源核验和 `finish_reason=stop`；不替代真实讯飞网络验收 |
| 讯飞真实冒烟脚本夹具 | `python3 scripts/test_xingchen_smoke_script.py` | 通过；回环服务验证非流式非空答案、5 次流式成功、结束帧、鉴权头和请求次数；不替代真实讯飞网络验收 |
| 固定作业夹具 | `PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_acceptance_fixture.py` | 通过 |
| 知识库状态机与黄金命中门槛 | `PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_kb_lifecycle.py` | 通过；三道固定问题必须实际执行并返回可核验来源后，才允许 `tested/published`；重复测试和回滚仍保持幂等 |
| 知识库版本指纹 | `agent-adapter/app/main.py::manifest_digest`、知识库生命周期夹具 | 通过；版本记录使用服务器实际课程 manifest SHA-256，不接受浏览器伪造的指纹 |
| Adapter 并发 | `PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/performance_smoke.py` | Mock 30 请求通过；本次 P50/P95 见命令输出，不作为讯飞性能成绩 |
| 代码语法 | `compileall`、`node --check`、`bash -n` | 通过 |
| 本地全量验收入口 | `bash scripts/run_local_acceptance.sh` | 通过；按固定顺序执行语法、数据、API、Store、Adapter、作业、知识库和 Mock 性能检查；不替代讯飞真实验收 |
| Compose | 两个 `docker compose ... config` 命令 | 通过；本机 Docker daemon 未运行，未执行本机容器启动 |
| 资源上限 | 服务器 `docker inspect`、Compose 展开配置 | 通过；MariaDB 2 GiB、Moodle 1.5 GiB、Adapter 768 MiB、Agent UI/Caddy 各 128 MiB，CPU 上限已生效；重建后核心容器 healthy |
| 服务器部署 | `bash scripts/deploy_server.sh` | 通过；最新 Moodle、Adapter、UI 镜像已在 `168.144.36.82` 重建并启动 |
| 服务器冒烟 | `BASE_URL=http://127.0.0.1 BASE_HOST=168.144.36.82 bash scripts/smoke_acceptance.sh` | 通过；课程站点、Agent 页面、健康检查和未登录 API 权限均通过 |
| Moodle 课程种子 | 远端重复执行 `moodle-seed-course.php` | 通过；课程、6 个章节和 20 个课件资源保持幂等，容器 healthy |
| Moodle 资源桥接 | 远端 `php -l resource.php`、`php -l grade-sync.php` | 通过；中文来源名映射到内部归一化文件名，成绩桥接仅内网令牌访问 |
| Moodle 真实登录 | 远端 `scripts/moodle_login_smoke.sh deploy/.env` | 通过；管理员登录成功，独立课程 `/course/view.php?id=2` 展示 6 章、20 个课件和 Agent iframe |
| 重启恢复 | 远端重启 Moodle 和 Adapter 后检查健康状态、站点和未登录 API | 通过；两服务恢复 healthy，站点 `200`，无会话 API `401` |
| 公网监听 | 远端 `ss -ltn` | 通过；公网仅监听 22、80、443，数据库和 Adapter 未发布宿主机端口 |
| 防火墙基线 | 远端 `scripts/security_baseline.sh` + SSH/站点复测 | 通过；UFW active，默认拒绝入站，仅允许 22/80/443，复测冒烟通过 |
| 全量备份 | 远端 `scripts/backup.sh` + `scripts/verify_backup.sh` | 通过；最新备份 `/opt/jbgs-course-agent/backups/20260722-000306` 校验通过，tar 成员无 `.env`/私钥文件，包含非密钥源码归档；相对路径参数也已验证 |
| 隔离恢复演练 | 远端 `scripts/restore_rehearsal.sh` | 通过；从 `/opt/jbgs-course-agent/backups/20260722-000306` 临时恢复课程 1、用户 2、知识点 20、Moodle 文件 26，并验证源码模板，线上卷未被修改 |
| 完整隔离 Compose 恢复 | 远端 `scripts/full_restore_rehearsal.sh` | 通过；独立 project 启动 db/Moodle/Adapter/UI/Caddy，课程数为 1，Caddy 未绑定宿主机 80/443，临时网络和卷已清理 |
| 每日备份任务 | 远端 `/etc/cron.d/jbgs-course-agent-backup` + 手动触发 | 通过；每天 03:17 调用 `/bin/bash`；最新备份 `20260722-000306` 校验和及恢复演练通过 |
| 备份存量清理 | 远端 `scripts/prune_backups.sh backups --delete-invalid` | 通过；已删除 18 个包含历史服务敏感成员的无效备份，保留两份安全校验通过的恢复点 |
| 学情诊断来源 | `scripts/test_adapter_runtime.py`、`/api/student/learning-diagnosis` | 通过；诊断响应保留 Workflow 返回的 manifest-validated `sources`，不再固定丢弃来源 |
| 讯飞前置检查 | 远端 `scripts/check_xingchen_config.sh deploy/.env` | 通过脚本行为验证；仅输出四项凭证为 missing，不输出任何值；当前配置本身仍待账号负责人补齐 |
| 线上安全基线 | 远端 `scripts/security_baseline.sh`、端口和 Compose 复核 | 通过；UFW 默认拒绝入站，仅开放 22/80/443，核心服务无宿主机业务端口；详见 `acceptance/test-reports/automated/security-baseline-2026-07-22.md` |
| 情景演绎持久化 | `scripts/test_course_store.py`、`scripts/test_adapter_runtime.py` | 通过；Workflow 输出、来源和完成状态写入场景轮次，同一幂等键复用结果，失败轮次可安全重试 |
| 写接口幂等 | `scripts/test_adapter_runtime.py`、`scripts/test_acceptance_fixture.py`、`scripts/test_kb_lifecycle.py` | 通过；状态变更、单份批改、知识库版本和场景结束的重复请求复用原结果 |
| 统一 CSRF 校验 | `agent-adapter/tests/test_main.py::test_real_mode_mutation_requires_moodle_sesskey` | 通过；真实模式下所有写接口（含普通问答 POST）集中校验 Moodle sesskey，缺失或错误令牌返回 403 |
| 学情 Agent 解释 | `scripts/test_adapter_runtime.py`、`/api/student/learning-diagnosis` | 通过 Mock 协议验证；确定性学情指标由后端生成，解释由 Workflow 分支生成；真实讯飞结果待凭证 |
| 知识库 Markdown | `scripts/test_kb_lifecycle.py` | 通过；合法 Markdown 可进入版本处理链路，非法扩展名和内容仍被拒绝 |
| 请求体与上传安全边界 | `scripts/test_kb_lifecycle.py`、`agent-adapter/app/main.py::request_size_guard` | 通过；统一写请求体上限、伪造 PDF、路径穿越、控制字符文件名和非法 UTF-8 Markdown 被拒绝，合法文件才进入 processing |
| 发布版本 Workflow 绑定 | `scripts/test_kb_lifecycle.py`、`agent-adapter/app/main.py::xingchen_stream` | 通过；黄金命中测试使用版本记录的 Workflow ID，真实模式未发布课程知识库时返回明确阻断错误 |
| 本地安全边界 | `scripts/test_adapter_runtime.py`、`agent-adapter/app/main.py::policy_violation` | 通过；明确要求忽略课程资料或伪造实验数据时返回 `policy_blocked`，不产生完成事件；普通安全讨论不会被误拦 |
| CASE-005 作业/批改/学情 | `scripts/test_acceptance_fixture.py` | 通过本地固定夹具；覆盖作业发布、提交幂等、客观题批改、Agent 初评待复核、学生字段隔离和资源化学情建议 |
| CASE-006 图谱/教材/情景 | `scripts/test_graph_scenario_fixture.py` | 通过本地固定夹具；覆盖先修路径、页码定位、两个场景、来源保存、重试幂等和结束状态 |
| 作业边界和成绩展示 | `scripts/test_acceptance_fixture.py` | 通过；截止时间、尝试次数、学生提交角色、学生自有成绩/反馈和课程过滤均由服务端校验，学生响应不含答案、rubric 或教师修改原因 |
| 图谱状态展示 | `agent-ui/index.html`、`/api/learning/profile` | 通过代码和 UI 脚本检查；节点颜色使用后端确定性状态，缺少学情时保持未评估，不由模型猜测 |
| Agent UI 静态页面 | 服务器 `curl -H 'Host: 168.144.36.82' /agent/` | 通过；前端幂等修复后页面返回 45,809 字节，课程名、知识图谱、教师入口和 AI 标识均存在；真实浏览器截图仍待 Chrome 远程调试授权 |
| Agent UI 写操作幂等 | `agent-ui/index.html`、Node JavaScript 语法检查 | 通过；写操作改用业务签名复用的 `operationKey`，提交/批改按钮请求期间禁用；服务器 UI 重建后 healthy |
| Agent UI HTTP 兼容 | `agent-ui/index.html`、Node JavaScript 语法检查 | 通过；随机操作键不强依赖安全上下文中的 `randomUUID`，服务器仍以 IP/HTTP 运行时 UI healthy、入口 200 |
| Agent UI 静态契约 | `python3 scripts/test_ui_contract.py`、`RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh` | 通过；检查移动端教师布局、AI 标识、幂等键、文本安全渲染和禁止动态执行；完整回归输出 `LOCAL_ACCEPTANCE_OK` |
| 提交前审计 | `bash scripts/pre_submission_audit.sh` | 按服务器 `.env` 执行；本地/服务器底座检查通过，明确阻断讯飞凭据和正式域名 HTTPS 缺失，返回非零；正式域名模式还会核验 HTTPS URL、Compose overlay 和 443 实际响应，不产生假绿 |
| 人工验收记录模板 | `acceptance/test-reports/manual/README.md` | 通过；强制记录账号、Workflow/知识库版本、来源、request ID、证据和复测结论，明确 Mock 不得冒充真实人工证据 |
| 提交材料完整性 | `bash scripts/check_submission_materials.sh` | 按预期返回非零并列出 3 项真实缺口：正式 Demo 地址、实际录屏、真实人工验收汇总；七个提交目录和基线报告均存在 |
| 部署包卫生 | `bash -n scripts/deploy_server.sh`、服务器远端语法检查 | 通过；部署归档排除 `._*`、`.DS_Store`、Python 缓存和测试缓存，避免 macOS 元数据干扰远端审计 |

## 尚不能判定通过

- 尚未完成真实浏览器登录录屏；当前已完成服务器端 HTTP/容器级验收，待提供测试账号后执行人工页面验收。
- 尚未取得讯飞星辰 `flow_id`、API Key、API Secret 和实际输入参数。
- 尚未执行真实 Workflow 五次冒烟、真实知识库命中测试、真实用户试用和真实 Workflow 性能测试；备份校验与隔离恢复已完成。
- Moodle 容器已运行并完成课程种子，但尚未用真实学生/教师账号完成课程登录、PDF 回跳和 Moodle 成绩回写人工验收。
- 远端当前仅有 `AGENT_UID_SALT` 和 `AGENT_BRIDGE_TOKEN`；四项讯飞 Workflow 配置仍缺失，因此真实 Agent、讯飞知识库命中和流式验收仍为阻塞项。

## 复现上下文

- 课程 manifest：`course-data/normalized/manifest.json`
- 图谱基线：`course-data/normalized/graph-baseline.json`
- 固定作业：`acceptance/test-fixtures/assignment-A-001.json`
- 测试模式：`MOCK_AUTH_MODE=true`、`MOCK_WORKFLOW_MODE=true`
- 测试数据库和上传目录均使用临时路径，不修改生产数据。
