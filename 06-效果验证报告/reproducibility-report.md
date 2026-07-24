# 可复现性报告

## 干净环境命令

```bash
git clone <repository>
cp deploy/.env.example deploy/.env
docker compose --project-directory deploy --env-file deploy/.env config
docker compose --project-directory deploy --env-file deploy/.env up -d --build db moodle agent-adapter agent-ui caddy
bash scripts/smoke_acceptance.sh
```

## 记录

- 环境/系统：服务器 Ubuntu 24.04，2 vCPU，8 GB RAM
- Docker 版本：Docker Engine 29.6.2，Docker Compose v5.3.1
- 开始/结束时间：2026-07-22（服务器日志以 UTC 记录）
- 是否依赖个人路径：否；远端固定目录为 `/opt/jbgs-course-agent`
- 是否依赖隐藏配置：平台底座否；讯飞真实主链路依赖服务器端 `deploy/.env` 中的外部凭证
- 基础部署耗时：本次同步、构建、重载 Caddy 和冒烟约 1 分钟级完成
- 服务器底座结果：通过；Moodle、Adapter、UI、MariaDB、Caddy healthy，`/` 为 200，未登录 API 为 401
- 三个案例结果：尚未执行真实讯飞案例；本地固定夹具已通过，Mock 结果不计入讯飞验收
- 备份证据：`/opt/jbgs-course-agent/backups/20260722-000306`，`verify_backup.sh` 通过 tar 成员级敏感文件检查，包含非密钥源码归档；相对备份路径已验证会规范化为绝对路径
- 恢复脚本从部署 Compose 解析实际 Adapter 镜像 ID，不依赖本机 `:latest` 标签；服务器隔离恢复复测通过。
- 恢复演练证据：`restore_rehearsal.sh` 通过，恢复课程 1、用户 2、Adapter 知识点 20、Moodle 文件 26 及关键源码模板；演练使用临时容器和目录，未修改线上数据卷
- 定时备份证据：`/etc/cron.d/jbgs-course-agent-backup` 每天 03:17 执行；`20260722-000306` 已校验并完成恢复演练
- 完整隔离恢复证据：`scripts/full_restore_rehearsal.sh` 启动独立 db/Moodle/Adapter/UI/Caddy，健康检查和课程恢复计数通过，临时资源退出时清理
- 失败和复测记录：初次 Moodle CLI 种子缺少 CLI 会话用户，已增加 `core\session\manager::set_user()` 并复测通过；Caddy 配置变更未自动 reload，部署脚本已增加显式重启并复测通过
