# 2026-09 安全专项整改全记录（凭证泄漏治理）

> 整改时间：2026-09-09（Asia/Shanghai）
> 范围：前端凭证泄漏、Bridge Token 泄漏、admin 口令公开、后端源码暴露、仓库冗余与 git 历史密钥
> 原则：**已泄漏的凭证一律轮换**（历史清除只消除存量，轮换才让旧值失效）；**线上零停机**（moodle/db/caddy 容器全程未重启）
> 执行基线：整改前 HEAD `c026d67`，整改后 HEAD 以 `b2b78c4` 起的新历史（全量 SHA 已重写）

---

## 1. 背景

外部安全检测确认三类凭证随公开仓库（GitHub `DuMaChen/EnergyGraph-AI`，main）与线上页面暴露：

1. 讯飞完整凭证（appId/apiKey/apiSecret/flowId）硬编码于 `agent-ui/index.html`，本地工作区 12 处、GitHub main 8 处，自 `a0b7e29` 起全程携带；学生"查看网页源代码"即可提取并冒用讯飞账号消耗配额。
2. `scripts/stress_test_and_eval.py:10` 将生产 `AGENT_BRIDGE_TOKEN` 写成 `os.getenv` 默认值——该 token 可绕过 Moodle 会话直接仿冒任意用户/角色调用全部 `/api/*`（含写操作）。
3. `Moodle2026!` 同时是线上 admin 真实口令（已在生产库 `password_verify` 实测命中），却公开写在三份手册、archive 副本、跟踪中的 `TEACHER_MANUAL.pdf` 与 `agent-adapter/tests/run_goal_eval_sessions.py`。

排查另发现一项未报告问题：`agent-ui/main.py`（后端应用旧副本）被 `COPY .` 打进纯静态 nginx 镜像，`https://energygraph.icu/agent/main.py` 可直接下载 211KB 全量后端源码。

复核确认安全：`deploy/.env` 系列未被跟踪；以生产真实值反查全部历史 blob，MariaDB 口令、`AGENT_UID_SALT`、Flowise/Qdrant 密钥均未进入仓库；无 AWS/GitHub/Slack/OpenAI 等第三方密钥；14 条提交信息均干净。

## 2. 关键判定（决定修复方式）

- **前端讯飞凭证是装饰性配置**：管理面板"连通性测试"为 `Math.random()` 伪造，配置仅存 localStorage，前端从不携带凭证发起请求；真实调用全部由适配器从 `deploy/.env` 的 `XINGCHEN_*` 发起。⇒ 删除前端凭证对功能零影响，实测验证成立。
- **admin 口令必须直接在 Moodle 重置**：`deploy/.env` 的 `MOODLE_ADMIN_PASSWORD`（64 位随机值）仅安装期生效，线上实际口令为手册公开值。
- **Bridge Token 同时注入 moodle 与 adapter**（`grade-sync.php` 侧校验同一 token），轮换须同步重建两容器。

## 3. 整改内容

### 3.1 源码与仓库（提交 `b2b78c4`，历史改写后为现 HEAD 祖先）

| 对象 | 处置 |
| :--- | :--- |
| `agent-ui/index.html` | SPARK_PRESETS 6 组预设、currentSparkConfig 默认值、handleResetSparkConfig、3 个管理面板输入框 value 中的 appId/apiKey/apiSecret/flowId 全部清空（12+12 处） |
| `scripts/stress_test_and_eval.py` | `AGENT_BRIDGE_TOKEN` 改为空默认值 + 缺失即退出 |
| `agent-adapter/tests/run_goal_eval_sessions.py` | 学生口令改为 `MOODLE_STUDENT_PASSWORD` 环境变量或 `deploy/.env` 读取 |
| `USER_MANUAL.md`（含 archive 副本） | 删除 admin 公开口令行与维护指南中的口令明文，改为"由系统管理员单独保管" |
| `agent-ui/main.py` | 从仓库与静态镜像删除（新增 `agent-ui/.dockerignore` 拦截 main.py 与 `._*`） |
| 5 个 `*.orig` | 删除跟踪 |
| `acceptance/` | 出库改本地证据目录（与 `archive/` 重复 31MB），`.gitignore` 增 `/acceptance/` |

teacher/student 的 `Moodle2026!` 按设计保留为公开教学口令；admin 轮换后该字符串不再具有任何后台权限。

### 3.2 git 历史改写（git-filter-repo，先彩排后实做）

- 替换三类密钥字面量为 `***REDACTED-***`；从全部历史移除 `acceptance/`、`agent-ui/main.py`、`*.orig` 路径；
- 彩排（克隆副本）通过三重验收（全历史 blob 零命中 / 提交信息零命中 / 新旧 HEAD 树一致）后才对正式仓库实做；
- 结果：15 个提交完整保留，`git fsck` 干净，`Moodle2026!` 有意不做历史替换（见 3.1 说明）。

### 3.3 凭证轮换与受控重建（2026-09-09 02:41 维护窗口）

1. `deploy/.env`：`AGENT_BRIDGE_TOKEN`（新 64 位 hex）、`MOODLE_ADMIN_PASSWORD` 同步更新；其余全部变量逐行 diff 确认零变更（含 `XINGCHEN_*`）。
2. Moodle 内直接重置 admin 口令（`update_internal_user_password`），实测新口令生效、`Moodle2026!` 被拒。
3. 滚动重建 `agent-ui`（新镜像，构建后验证内容：0 密钥、无 main.py、无 `._*`）、`agent-adapter`、`moodle`（env 注入新 token）；`caddy`、`db` 未动。

## 4. 验证记录（2026-09-09，重建后 35 小时复测）

### 4.1 安全项（全部通过）

| 项 | 结果 |
| :--- | :--- |
| 工作区/全历史 blob/提交信息三类密钥扫描 | 0 命中（含本地 acceptance/ 证据目录） |
| 线上 `/agent/` 页面源码 | 0 密钥 |
| `/agent/main.py` | 返回 SPA 兜底 HTML，源码暴露关闭 |
| 旧 Bridge Token 调 `/api/*` | 401 unauthorized |
| 新 Bridge Token（teacher/admin 仿冒头） | 200 正常，RBAC：student/teacher 访问 admin 端点 403、admin 200 |
| admin 旧口令登录 | 落回登录页报错；新口令进入 `/agent/` |
| token 三方一致性 | adapter 容器 = moodle 容器 = `deploy/.env`（sha256 一致） |
| 敏感文件权限 | `deploy/.env`、轮换前备份、新密钥文件、repo/db 备份全部 0600/600 |
| `deploy/.env` 跟踪状态 | 未跟踪（仅 `.env.example` 占位符在库） |

### 4.2 功能项（全部通过）

| 项 | 结果 |
| :--- | :--- |
| `/health`、`/agent/`、`/login/index.php`、课件图片 | 全部 200，页面内容标记正常 |
| student 登录 → 工作台 → 知识图谱 API | 登录落点 `/agent/`，API 200 |
| 真实问答 E2E（SSE，经 Moodle 会话+sesskey+讯飞） | 403（无 sesskey，CSRF 防御生效）→ 200 正常流出 token/source/done 事件 |
| 讯飞链路健康 | `xingchen_smoke.sh` 5/5 通过；适配器日志无 `workflow_auth_failed` |
| 容器 | 全部 healthy；caddy/db uptime 未中断 |
| 适配器错误日志 | 仅 2 条良性（防劫持拦截 1 条、验收探针故意触发 422 的堆栈 1 条） |

注：普通问答当前返回问候语开场白，属**整改前已归档的已知上游问题**（工作流"知识问答模型"input 误绑知识库结果，见 `MAINTENANCE_2026-09.md` 第 7 节与 `PROJECT_STATUS.md` 功能矩阵脚注）。本轮以"绕过适配器直连讯飞工作流返回同样内容"坐实与整改无关。

### 4.3 既有测试债（与整改无关，待后续处理）

适配器单测 30 个中 3 个失败：`test_main.py` 仍在导入已删除的 `build_teacher_fallback_answer`（阶段八清理死代码时未同步测试）；`test_e2e_live_scenarios.py` 两处 SSE 文案断言未随"诚实兜底"改造更新。

## 5. 备份与回滚资产（保留于 `/root/jbgs-course-agent-env-backups/`）

| 资产 | 文件 |
| :--- | :--- |
| 仓库全量（含改写前历史） | `repo-backup-20260909-022855.tar.gz`（311MB，600） |
| 数据库全量 | `db-backup-20260909-022855.sql.gz`（1.4MB，600） |
| 整改前镜像 | `rollback-{agent-ui,agent-adapter,moodle}:20260909-022855` |
| 新 admin 口令/新 token | `/root/new-secrets-20260909-022855.txt`（600） |
| 轮换前 .env | `deploy/.env.pre-rotation-20260909-022855`（600） |

## 6. 遗留人工待办

1. **GitHub force push**：服务器无推送凭证。在新历史上执行 `git remote add origin <URL> && git push --force --set-upstream origin main`；随后开启 Secret scanning + Push protection，并向 GitHub Support 申请旧 commit 缓存清除。推送完成前，GitHub 上的旧历史仍含三类密钥（旧 token/旧 admin 口令已失效，唯讯飞 key 未轮换，见 2）。
2. **讯飞 key 轮换**：控制台重置应用 `1a31e771` 的 APIKey/APISecret 后更新 `deploy/.env` 的 `XINGCHEN_API_KEY/SECRET` 并 `docker compose up -d agent-adapter`。在此之前旧 key 仍可被冒用消耗配额。
3. admin 新口令点对点告知管理员（不入库、不入手册）。
