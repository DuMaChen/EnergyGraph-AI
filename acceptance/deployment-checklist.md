# 部署验收清单

## 当前记录（2026-07-22）

已通过的服务器底座项目：

- 服务器代码同步、镜像重建、Caddy 重载和远端冒烟已由 `bash scripts/deploy_server.sh` 一次性完成。
- `db`、`moodle`、`agent-adapter`、`agent-ui`、`caddy` 均运行并通过健康检查。
- 公网监听复核仅发现 22、80、443；数据库、Adapter、历史组件没有宿主机发布端口。
- UFW 已启用：默认拒绝入站，仅放行 22/tcp、80/tcp、443/tcp；启用后 SSH、站点和冒烟验收复测通过。
- Moodle 已幂等创建课程、6 个章节和 20 个课件；Adapter 使用持久化数据卷。
- 已生成并验证最新备份：服务器路径 `/opt/jbgs-course-agent/backups/20260722-000306`；验证命令为 `bash scripts/verify_backup.sh <BACKUP_DIR>`，tar 成员级敏感文件检查通过，并包含非密钥源码归档。
- 真实 Moodle 登录冒烟已通过：管理员进入独立课程 `/course/view.php?id=2`，6 章、20 份课件和 Agent iframe 均可见。
- 已完成隔离恢复演练：`bash scripts/restore_rehearsal.sh /opt/jbgs-course-agent/backups/20260722-000306`，结果为课程 1、用户 2、知识点 20、Moodle 文件 26，源码模板检查通过，临时资源自动清理。
- 恢复演练使用当前 Compose 解析出的 Adapter 镜像 ID，不依赖浮动的 `:latest` 标签；镜像版本固定检查通过。
- 每日备份任务已安装为 `/etc/cron.d/jbgs-course-agent-backup`，每天 03:17 执行；最新备份 `20260722-000306` 校验和及隔离恢复均通过。
- 历史 Flowise/Qdrant 卷不属于本期 P0/P1 恢复对象，备份脚本默认不归档它们，以避免携带历史服务生成的签名密钥。
- 已用 `scripts/prune_backups.sh` 清理旧的无效备份，当前保留两份通过安全校验的恢复点。
- `scripts/full_restore_rehearsal.sh` 已在独立 Compose project 中完整启动恢复服务，未绑定线上端口，退出后自动清理临时资源。

待前置条件或尚未完成的项目：

- UFW 状态已完成命令复核；汇总证据见 `acceptance/test-reports/automated/security-baseline-2026-07-22.md`，最终材料仍可补充截图。
- 讯飞 Workflow、知识库 ID、真实黄金问题和流式响应尚未验收。
- 学生/教师/管理员真实账号人工流程、独立环境恢复和正式域名 HTTPS 尚未验收。
- 已完成不触碰线上卷的隔离恢复演练；正式提交前仍应在独立环境按相同备份执行完整服务启动和人工登录复测。

以下复选框是最终提交前的逐项签字清单；“当前记录”不替代证据文件。

- [ ] `cp deploy/.env.example deploy/.env` 后所有示例密钥已替换
- [x] `docker compose config` 无变量警告
- [x] HTTP 和 HTTPS Caddy 配置均将完整 `/api/*` 转发至 Agent Adapter
- [x] 知识点资源和教师学生学情接口已纳入静态 API 契约
- [x] 关键写接口的 Idempotency-Key 会复用已完成结果
- [x] 服务器仅开放 SSH、HTTP、HTTPS
- [x] 以 root 执行 `scripts/security_baseline.sh` 后保存 `ufw status verbose`
- [x] `db`、`moodle`、`agent-adapter`、`agent-ui`、`caddy` healthy
- [x] 课程数据 manifest 为 20 个 PDF，SHA-256 和页数齐全
- [x] graph baseline 为 6 个章节、20 个知识点，错误数为 0
- [ ] 讯飞 Workflow 已发布，`flow_id`、API Key、Secret 由管理员保管
- [ ] `bash scripts/pre_submission_audit.sh` 输出 `PRE_SUBMISSION_READY`
- [ ] 讯飞凭证配置前先执行 `bash scripts/check_xingchen_config.sh deploy/.env`，仅输出存在性，不输出密钥
- [ ] `AGENT_BRIDGE_TOKEN` 已在 Moodle/Adapter 服务端配置，成绩回写 bridge 可用
- [ ] 真实黄金问题命中并能核验来源
- [ ] 按 `acceptance/test-reports/manual/README.md` 完成学生、教师、管理员和安全人工记录
- [ ] 学生/教师/管理员账号对象级权限复测通过
- [x] 备份中不含明文 `deploy/.env`
- [x] 已安装每日备份任务并检查最近一次日志和校验和
- [x] 在独立环境执行 `scripts/verify_backup.sh`，恢复 Moodle/Agent 数据并启动完整隔离 Compose 服务
- [ ] 在独立环境复跑三个正式案例（真实讯飞和人工账号仍待前置条件）
- [ ] 干净环境恢复并复跑三个正式案例
- [ ] `bash scripts/check_submission_materials.sh` 输出 `SUBMISSION_MATERIALS_READY`

本地代码级回归证据：

- `scripts/test_adapter_runtime.py`：Adapter、流式问答、CSRF、角色和场景
- `scripts/test_acceptance_fixture.py`：A-001 五题作业、提交幂等和批改
- `scripts/test_kb_lifecycle.py`：知识库发布门槛、版本归档和回滚
- `/api/knowledge-base/versions/{version_id}/hit-tests`：服务端执行三道黄金问题并保存来源证据，禁止仅提交 `hit_status=passed`

以上 Mock 证据不能替代真实讯飞 Workflow、服务器和人工用户证据。

每项记录 `TEST_RUN_ID`、代码版本、manifest 哈希、Workflow 发布版本、操作者和证据路径。
