# 线上安全基线复核

## 环境

- 服务器：`168.144.36.82`
- 复核日期：2026-07-22（Asia/Shanghai）
- 执行身份：服务器 root；凭据值未输出
- 代码目录：`/opt/jbgs-course-agent`

## 结果

| 检查项 | 结果 | 证据 |
|---|---|---|
| UFW 默认入站策略 | 通过 | `deny` |
| 公网放行端口 | 通过 | 仅 `22/tcp`、`80/tcp`、`443/tcp` |
| 数据库公网监听 | 通过 | MariaDB 仅 Docker 网络端口 |
| Adapter 公网监听 | 通过 | Adapter 仅 Docker 网络端口 |
| Qdrant/Flowise 公网监听 | 通过 | 仅 Docker 网络端口 |
| Compose 配置 | 通过 | `docker compose config` 无错误 |
| 核心容器健康 | 通过 | Moodle、MariaDB、Adapter、Agent UI 健康；Caddy 运行 |
| 课程页面 | 通过 | 6 章、20 份课件、Agent iframe |
| 备份校验 | 通过 | `/opt/jbgs-course-agent/backups/20260722-000306`；tar 成员敏感文件检查通过，旧无效备份已清理 |
| 资源上限 | 通过 | 核心容器 CPU/内存上限已生效，重建后服务保持 healthy |
| 讯飞主链路 | 阻断 | Workflow URL、flow_id、API Key、API Secret 均待账号负责人配置 |

## 复核命令

```text
bash scripts/security_baseline.sh
docker compose --project-directory deploy --env-file deploy/.env config
BASE_URL=http://127.0.0.1 BASE_HOST=<SITE_HOST> bash scripts/smoke_acceptance.sh
BASE_URL=http://127.0.0.1 SITE_HOST=<SITE_HOST> bash scripts/moodle_login_smoke.sh deploy/.env
bash scripts/check_xingchen_config.sh deploy/.env
bash scripts/verify_backup.sh /opt/jbgs-course-agent/backups/20260722-000306
```

## 结论

基础设施和课程壳达到当前计划的可部署状态，但由于真实讯飞 Workflow 和知识库尚未配置，不能将本记录解释为 Agent 主链路通过，也不能替代真实学生/教师人工验收。
