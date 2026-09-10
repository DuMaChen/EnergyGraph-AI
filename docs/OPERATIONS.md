# 运维与故障排查手册（EnergyGraph-AI）

> 面向：平台运维 / 后续开发接手者
> 配套文档：[MAINTENANCE_2026-09.md](./MAINTENANCE_2026-09.md)（可靠性维护记录）、[SECURITY_MAINTENANCE_2026-09.md](./SECURITY_MAINTENANCE_2026-09.md)（安全整改记录）、[PROJECT_STATUS.md](../PROJECT_STATUS.md)（项目现状）

---

## 1. 系统拓扑与容器

```text
用户浏览器 → Caddy 2 (:80/:443, energygraph.icu)
    ├── Moodle 4.5 (deploy-moodle-1, 内网:80)      教学/身份/成绩册
    ├── Agent UI (deploy-agent-ui-1, 内网:80)      /agent/ 单页工作台
    ├── Agent Adapter (deploy-agent-adapter-1, 内网:8081)  /api/* 网关
    └── MariaDB 10.11 (deploy-db-1, 内网:3306)     持久化
Agent Adapter → 讯飞星辰 Workflow (7494978072491315200) + 星火模型 + 课程知识库
```

- 部署目录：`/opt/jbgs-course-agent`（已初始化 git 仓库，main 分支）
- 环境与密钥：`deploy/.env`（不入库）
- 健康检查：`curl http://127.0.0.1:8081/health`（容器内网）或各容器 `docker ps` 状态

## 2. 对话链路错误码对照表

适配器对讯飞上游的所有失败都会以 `[WORKFLOW_ERROR]` 打入容器日志（`docker logs deploy-agent-adapter-1`），并向 SSE 客户端下发同码 error 事件：

| 错误码 | 含义 | 处置 |
| :--- | :--- | :--- |
| `workflow_prompt_echo_rejected` | 上游回显了指令/演示内容（疑似情景状态劫持） | 系统已自动复位+重试；频发时检查工作流"状态"变量与决策节点记忆轮数 |
| `workflow_quality_failed` | 返回内容清洗后不足 24 字符（空壳/无效） | 系统自动重试；偶发属上游抖动，频发时检查工作流节点配置 |
| `workflow_timeout` | 讯飞请求超时（默认 90s） | 重试；检查 `XINGCHEN_TIMEOUT_SECONDS` |
| `upstream_disconnected` | 流式连接中断未收到结束帧 | 重试；检查网络与讯飞平台状态 |
| `workflow_auth_failed` | 鉴权失败（401/403） | 核对 `deploy/.env` 中 `XINGCHEN_API_KEY/SECRET` |
| `workflow_upstream_error` | 讯飞返回 HTTP 4xx/5xx | 查讯飞平台发布状态 |
| `knowledge_base_not_published` / `workflow_not_configured` | 知识库未发布 / Flow 未配置 | 检查知识库发布状态与 `XINGCHEN_FLOW_ID` |
| `bridge_body_error` | Moodle 成绩桥接应答非 synced | 见第 4 节成绩链路 |
| `csrf_rejected` | 缺少/错误 `X-Moodle-Sesskey` | 前端正常携带；手工调用需先取 sesskey |

出题链路专用日志标记：`[DIAGNOSIS]`、`[QUIZ]`（含 `recovered missing answer via grading probe` 答案探针命中、`duplicate=True` 去重命中）、`[SCENARIO]`、`[QUESTION_DRAFT]`、`[WORKFLOW_STATE_RESET]`（向工作流发送情景复位）。

## 3. 对话功能排查路径

| 现象 | 首查 | 次查 |
| :--- | :--- | :--- |
| 出题提示"暂时不可用" | 日志中两次尝试的 `DEBUG_RAW_ANSWER_BUFFER` 原始返回 | 上游是否回显（劫持）/缺答案（探针是否命中）/缺选项 |
| 普通问答回问候语 | 工作流"知识问答模型"的 input 是否仍误绑知识库结果（控制台修复，见维护日志第 7 节） | 决策_1 意图命中 |
| 诊断中途缺题 | 学生回复"下一题"即可补发（awaiting_next 机制） | 日志确认 `awaiting manual retry` |
| 情景演绎开场是告别语 | 系统已自动复位重试；频发检查工作流决策_3/决策_1 的意图描述 | 容器日志 `[SCENARIO]` |
| 拒答伪造数据请求（422 `policy_blocked`） | 预期行为（POLICY_PATTERN 边界拦截） | — |

## 4. 成绩链路

链路：教师批改（`POST /api/teacher/submissions/{id}/grade`）→ 适配器本地记分 → `grade-sync.php`（内网桥接，`AGENT_BRIDGE_TOKEN` 鉴权）→ Moodle 成绩册（人工成绩项 + `update_final_grade`）。

- 桥接源码：`deploy/moodle/grade-sync.php`（构建时 COPY 进镜像的 `local/course_agent/`）——**修改后必须重建 moodle 镜像**；
- 常见失败：`redirecterrordetected`（内网调用缺 Host 头，适配器已自动补 `SITE_HOST`）；`grade_update_failed`（写库路径问题，勿改回 `grade_update`，人工项必须走 `update_final_grade`）；
- 验证 SQL：`SELECT gi.itemname, gg.finalgrade FROM moodle.grade_items gi JOIN moodle.grade_grades gg ON gg.itemid=gi.id WHERE gi.itemname LIKE '%Agent%';`

## 5. 测试与发布流程（强制）

**任何推送到生产前，必须完成：**

1. 编译与单测：
   ```bash
   python3 -m py_compile agent-adapter/app/main.py
   docker cp agent-adapter/app/main.py deploy-agent-adapter-1:/app/app/main.py
   docker cp agent-adapter/tests deploy-agent-adapter-1:/app/tests
   docker exec -w /app deploy-agent-adapter-1 python -m unittest \
     tests.test_honest_fallbacks tests.test_interactive_diagnosis tests.test_workflow_state_machine
   ```
2. 多轮实机验证：师生两角色各约 7 轮，每轮覆盖**正常问答、单题检验、学情诊断、情景演绎**四类功能（可用 `/tmp/soak.sh` 套路：登录→`/api/course-agent/chat` SSE→断言题干数/判分事件/诚实提示），统计 PASS 率与问候语/垃圾内容告警；
3. 构建 + 滚动重启对应容器（`docker compose build/up -d <service>`），健康确认；
4. **推送后回归**：每角色至少 2 轮 × 4 功能，确认零退化后再收尾。

UI 类改动额外要求：强刷后人工核对目标视图（本环境无图形浏览器，无法自动截图，需教师端确认）。

## 6. 常用操作

```bash
# 查看对话服务实时日志（过滤上游错误）
docker logs deploy-agent-adapter-1 --since 30m --timestamps 2>&1 | grep -E "WORKFLOW_ERROR|DIAGNOSIS|QUIZ"

# 重建单个服务
cd /opt/jbgs-course-agent/deploy && docker compose build <svc> && docker compose up -d <svc>

# 数据库直查（成绩核验等）
PW=$(grep -E "^MARIADB_ROOT_PASSWORD=" deploy/.env | cut -d= -f2 | tr -d '"')
docker exec deploy-db-1 mariadb -uroot -p"$PW" -N -e "<SQL>" 2>/dev/null
```

## 7. 已知约束

- `agent-adapter`、`agent-ui` 代码打进镜像，**无卷挂载**：改代码必须重建容器；容器重建后 `/app/tests` 丢失，跑测试前需重新 `docker cp`；
- 适配器与工作流之间的"退出情景演绎"探针会进入工作流决策节点的对话记忆（rounds=6），属已知特性，靠 farewell/echo 识别兜底；
- 讯飞控制台侧待修项见 [MAINTENANCE_2026-09.md](./MAINTENANCE_2026-09.md) 第 7 节，其中"知识问答模型 input 改回 AGENT_USER_INPUT"是普通问答恢复的前提。

## 8. 密钥管理与轮换 SOP（2026-09 安全整改后确立）

**密钥只允许存在于**：`deploy/.env`（0600，不入库）、`/root/new-secrets-*.txt`（0600，轮换交接用）。严禁出现在：前端源码、git 历史（含提交信息）、镜像内容、日志、手册。红线由来与整改全记录见 [SECURITY_MAINTENANCE_2026-09.md](./SECURITY_MAINTENANCE_2026-09.md)。

| 密钥 | 轮换方式 | 生效动作 |
| :--- | :--- | :--- |
| `AGENT_BRIDGE_TOKEN` | `openssl rand -hex 32` 更新 `.env` | **必须同时** `docker compose up -d agent-adapter moodle`（grade-sync.php 侧校验同一 token，只重建 adapter 会导致成绩回写 401） |
| admin 口令 | `docker exec -it deploy-moodle-1 php admin/cli/reset_password.php`（**改 `.env` 无效**，该值仅安装期生效；改后同步更新 `.env` 供登录冒烟脚本读取） | 无需重启 |
| 讯飞 APIKey/Secret | 讯飞开放平台控制台重置，更新 `.env` 的 `XINGCHEN_API_KEY/SECRET` | `docker compose up -d agent-adapter`，跑 `scripts/xingchen_smoke.sh` 确认 5/5 |

- 轮换前必做：`mariadb-dump` 全库备份 + `tar` 仓库备份 + 旧镜像打 `rollback-*` 标签；
- 验证套路：旧值调 `/api/*` 应 401、新值 200；admin 旧口令登录被拒；`xingchen_smoke.sh` 通过；
- 任何人不得把真实密钥贴进终端输出/工单/文档——展示时截断（如 `c6f5…`）；
- 静态镜像内容自检：`docker run --rm <agent-ui镜像> sh -c 'grep -c <key前缀> /usr/share/nginx/html/index.html'` 应为 0，且 `/usr/share/nginx/html/main.py` 不存在。
