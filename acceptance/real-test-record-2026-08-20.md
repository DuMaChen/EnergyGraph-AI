# 真实线上回归测试留档

日期：2026-08-20（Asia/Shanghai）  
目标环境：`root@139.196.45.2`，公网地址 `https://energygraph.icu`

本记录只保存测试范围、结果和脱敏错误码，不保存 API Secret、API Key、密码、Cookie、姓名、邮箱或模型回答原文。

## 已执行并通过

### 部署与课程基础设施

- `SMOKE ACCEPTANCE PASSED`
- `MOODLE_LOGIN_SMOKE_OK path=https://energygraph.icu/course/view.php?id=2 chapters=6 resources=20`
- `REAL_WORKFLOW_PREFLIGHT_OK`
- `XFYUN_REAL_SMOKE success=5/5`：讯飞真实 Workflow 非流式 1 次、流式 5 次均通过。
- `PRE_SUBMISSION_READY`
- Agent Adapter 健康状态：`status=ok`、`workflow_configured=true`、`mock_workflow=false`、安全配置已启用。
- 课程数据校验：20 份 PDF、439 页、20 个知识点、17 条边。
- 本地静态契约：`API_CONTRACT_OK routes=48`、`UI_CONTRACT_OK`。
- 云端部署契约复核：`API_CONTRACT_OK routes=113`、`UI_CONTRACT_OK`；知识库发布脚本离线回归 `Ran 10 tests ... OK`。
- 云端备份：`BACKUP_VERIFY_OK 20260820-020138`；数据库、Moodle 数据、Agent 数据、Caddy 数据/配置、课程数据和应用源码归档均通过 SHA256 与敏感成员校验。
- 知识库正式发布：版本 `kb-b6cbd41439a14fb3a6ce62c8081280aa`，`source_count=20`、20 份课件哈希一致（重复项均 `UPLOAD_SKIP`）、三道黄金题 `passed=3/3`，最终 `status=published`。

### 管理员视角

脚本：`scripts/real_admin_smoke.py`

- 真实管理员 HTTPS 登录通过。
- Moodle 课程页通过。
- `/api/admin/status` 返回 200。
- 生产 Workflow 配置为真实模式，未回退 Mock。

### 教师/学生登录与作业闭环

脚本：`scripts/real_business_smoke.py`

- 真实教师、学生账号登录和 Moodle 会话角色映射通过。
- 教师创建题目、发布题目、创建作业、发布作业通过。
- 学生读取作业，响应中未泄露答案或 rubric。
- 学生提交作业通过。
- 教师读取提交并批改通过。
- 成绩真实回写 Moodle：`moodle_sync=synced`。
- 学生侧再次读取到成绩通过。
- 教师/学生越权边界通过。
- 幂等键重复执行路径通过（脚本可重复运行，不会重复提交同一尝试）。

### 学习与图谱视角

脚本：`scripts/real_learning_smoke.py`、`scripts/real_surface_smoke.py`

- 6 章知识图谱读取通过。
- 20+ 课件资源读取、资源详情和页码校验通过。
- 学习画像、推荐读取通过。
- 学生启动/结束情景通过。
- 教师查看学生脱敏学情通过；学生访问教师学情接口返回 403。
- 图谱搜索、节点、邻居、路径接口通过。
- 超长查询、无效资源、无效页码校验通过。
- 跨站 Origin 防护通过。
- 缺少 Moodle sesskey 的写请求返回 403。
- 策略拦截（要求忽略课程边界、伪造页码/引用）返回 `policy_blocked`。
- 发布后普通 Agent 请求返回真实 SSE：`token → source×2 → done`；来源事件包含课程版本、sha256、resource_id、归一化文件名和页码。

### browser-harness 真实网页流程

- 使用 `browser-harness` 建立 CDP 连接；本轮只创建测试用的登录、个人主页、Agent 和资源标签，未修改用户原有标签、账号资料或 Chrome 配置，收尾时已关闭本轮创建的标签。
- 真实管理员登录通过：登录后进入 `/my/`，存在退出控件且无登录失败页。
- 真实课程页打开通过：`/course/view.php?id=2`，课程标题和章节内容可见。
- 真实 Agent 页面打开通过：`/agent/`，AI 助教输入框、场景按钮和发送按钮均已渲染。
- 发布后学生真实 Agent 对话通过：答案完成，页面展示 `3.4 储能变流器拓扑及并网控制.pdf`、第 3 章、第 3/4 页来源。
- 教师真实页面会话返回 `role=teacher`，教师备课模式可见；学生真实页面会话返回 `role=student`，教师模式隐藏。
- 教师在网页创建并发布带 `codex/acceptance` 前缀的题目和作业；学生在网页打开同一作业并提交；教师在网页打开提交并执行批量批改。
- 课程页资源链接真实可见；管理员、教师、学生登录结果、课程页、Agent、教师工作台、作业抽屉、批改结果及发布后 Agent 均保存了截图，当前截图 46 张，目录为 `acceptance/screenshots/`。
- 登出后匿名 Agent 请求及过期 Moodle Cookie 请求均返回 `401 unauthorized`；修复前过期 Cookie 曾返回 `502 auth_service_unavailable`，已部署修复并重新验证。
- 发布后浏览器来源链接的 DOM href 已指向归一化 Moodle 文件名；携带真实学生会话访问该地址返回 PDF `HTTP 200`（`chapter-3-3.4-.pdf`，页码片段 `#page=3`）。

## 本次发现并修复

### 图谱零跳路径错误

现象：真实请求从某知识点查询到自身的路径时返回 404。  
原因：线上 `CourseStore.path()` 使用 `len(valid_nodes) != 2`，而 SQLite 对相同参数的 `IN (?, ?)` 只返回一行。  
修复：允许合法的零跳路径；未知节点仍返回无路径。修复已应用到线上 `/opt/jbgs-course-agent/agent-adapter/app/course_store.py` 并重建 Agent Adapter。

证据：

- `REAL_SURFACE_SMOKE_OK ... graph=ok ...`
- `REAL_BUSINESS_SMOKE_OK ...`
- `LOCAL_GRAPH_PATH_REGRESSION_OK`
- 重建后容器健康检查和发布前审计再次通过。

### 知识库发布脚本与页级检索

- 修复云端 `scripts/kb_release.py` 使用 HTTP 导致 Moodle 308 会话桥接失败的问题，改为读取正式 HTTPS 站点。
- 上传并挂载 20 份课件的页级 Markdown 索引到云端 Adapter，只读挂载为 `/app/course-sources`。
- 新增服务器端关键词检索：三道黄金题分别命中第 3、3、4 章的真实课件页；证据来源由服务器从课件索引生成，不接受浏览器提交的页码。
- Adapter 仍调用真实 Workflow；当 Workflow 不返回引用标记时，使用本地检索证据并保留真实答案流，不切换 Mock。
- 来源 metadata 复核：真实检索来源均带有课程 `sha256` 和 `resource_id`；发布脚本 `--check --probe` 对第三方未返回引用标记改为 `PROBE_NOTE`，不再误报失败。
- 本地检索单元回归：`Ran 2 tests ... OK`；云端发布状态机回归：`Ran 10 tests ... OK`；重建后 `SMOKE ACCEPTANCE PASSED`。
- 发布脚本幂等性修复：云端已备份原脚本；对已存在且 SHA256 一致的课件改为 `UPLOAD_SKIP`，只上传缺失或哈希不一致的文件，避免重复发送。

### 登出后的匿名边界修复

- 根因：Moodle `AJAX_SCRIPT` 对过期会话返回 HTTP 200 的 `redirecterrordetected` JSON，Adapter 原先将缺少身份字段的 JSON 误判为会话服务故障并返回 502。
- 修复：识别 Moodle 过期登录 HTML 和 `redirecterrordetected/requireloginerror` JSON，统一转换为未授权 401；云端已备份源码并重建 Agent Adapter。
- 回归：无 Cookie `401 unauthorized`；过期 Cookie `401 unauthorized`；容器健康为 `healthy`。

### 来源链接归一化修复

- 根因：真实 Workflow 和本地页级检索都返回人类可读的中文课件名，而 Moodle 文件存储使用归一化文件名；来源 UI 原先将显示名直接放入跳转地址，导致来源点击返回 404。
- 修复：来源事件同时保留 `source_file`（显示名）和 `file`（归一化文件名）；真实 Workflow 来源和本地检索来源统一使用可访问的 Moodle 文件名。
- 本地回归：`Ran 2 tests ... OK`；远端 Agent Adapter 重建并健康；发布后教师/学生 SSE 与真实来源链接回归通过。

## 2026-08-20 追加回归：自建 PDF、全表面 API 与临时浏览器

### 自建 PDF 与知识库上传

- 本地生成脱敏三页 PDF：`output/pdf/codex-functional-regression-courseware-20260820.pdf`。
- PDF 校验：3 页、A4、未加密；`pdfinfo`、`pdftotext` 和三页渲染检查均通过；本地 SHA256 为 `18d88c03b3935d9449f9a297014d444409b4548daff745edb69f40c9c2e19829`。
- 真实教师上传至独立测试版本 `kb-c6675386534744df869bca093f4b0408`：远端文件 125632 bytes，SHA256 与本地一致；文件列表为 1 项。
- 重复相同 `Idempotency-Key` 返回同一上传结果；伪造 PDF、目录穿越文件名均返回 422；学生上传知识库返回 403；正式发布版本 `kb-b6cbd41439a14fb3a6ce62c8081280aa` 未改变。
- 该独立版本保持 `processing` 作为上传/幂等审计样本，未将回归文件发布到正式知识库；早期发现结构伪造 PDF 的测试版本已标记 `failed`，没有覆盖正式版本。

### 本次实际修复并重新部署

- PDF 上传从“头尾字节检查”升级为 `pypdf` 结构解析并要求至少一页，修复伪造 EOF 文件可上传的问题。
- Moodle 内部会话桥接补齐公网 Host、Forwarded Host/Proto，修复重启后真实 Cookie 被误判为会话服务故障的问题。
- Workflow 请求只发送正式 Flow 起始节点声明的 `AGENT_USER_INPUT`，将服务端上下文合并进该字段并做长度限制；修复真实调用返回 `22500`（起始节点参数不匹配）的问题。
- 每次部署前在云端 `/opt/jbgs-course-agent/backups/20260820-pdf-validator/` 留有源码和配置前版本备份。

### 全功能回归结果

- 本地：18 个 Adapter 单测通过；`LOCAL_ACCEPTANCE_OK`、`KB_LIFECYCLE_OK`、`API_CONTRACT_OK routes=48`。
- 云端：`REAL_ADMIN_SMOKE_OK`、`REAL_LEARNING_SMOKE_OK`、`REAL_BUSINESS_SMOKE_OK`；教师/学生真实 SSE 均为 `token/source/done`，真实模式且未回退 Mock。
- 云端扩展表面回归：`POST_PUBLISH_SURFACE_SMOKE_OK graph=ok resources=ok learning=ok policy=ok student_sse=ok teacher_sse=ok scenario_turn=ok kb_boundary=ok csrf=ok origin=ok`。
- 临时 browser-harness 实测：学生真实登录、个人主页、课程页、20 份课件列表、Agent 页面和学生问答完成；教师真实登录、教师备课模式、教师 AI 问答和教师工作台完成。当前真实 Workflow 返回的回答未携带可解析的文件/章节/页码标记，网页因此显示“来源待核验”，没有凭空补造引用；接口仍正常完成并保留该审查状态。
- 本轮只使用独立 CDP 端口 `9224` 的临时 Chrome；测试标签已关闭，临时 Chrome 进程已停止，用户原有浏览器端口和标签未触碰。

可重复脚本：`scripts/create_regression_pdf.py`、`scripts/real_pdf_upload_smoke.py`、`scripts/post_publish_surface_smoke.py`。

### 2026-08-20 追加：开放公网注册入口

- Moodle 生产配置已将 `registerauth` 从空值设为 `email`；已有 `auth=email` 且 `authpreventaccountcreation=0` 保持不变。
- `https://energygraph.icu/login/index.php` 已验证出现“注册新帐号”，链接为 `/login/signup.php`；注册页 HTTP 200。
- 未提交真实注册表单，避免在生产库创建未经确认的账号。
- 当前 SMTP 主机配置为空，因此只确认“注册入口已开放、页面可达”；邮箱确认投递链路需后续配置 SMTP 后再做端到端测试。
- 清理 Moodle 缓存后发现 root 创建的缓存子目录导致短暂权限错误（HTTP 500）；已恢复 `moodledata/cache` 与 `moodledata/localcache` 为 `www-data:www-data`，登录页复测 HTTP 200。

### 2026-08-20 追加：配置注册确认邮件

- 已配置 QQ SMTP：`smtp.qq.com:465`、SSL、LOGIN；SMTP 用户名和无回复地址使用用户提供的邮箱；授权码不写入留档。
- 远端 SMTP 认证通过：`235 Authentication successful`。
- Moodle 实际调用 `email_to_user()` 投递测试邮件成功：`MOODLE_EMAIL_SEND_OK`。
- 用户确认已实际收到测试邮件，注册确认邮件链路闭环通过。
- 查询确认：之前失败的注册没有在 Moodle 用户表留下未确认账号；可直接重新注册。

### 2026-08-20 追加：新注册用户自动入课闭环

发现：邮件确认成功后的新用户只能看到站点首页和日程，原因是课程已有
`manual` enrollment，但没有任何自动入课逻辑，`self` enrollment 也处于关闭状态。

实现：

- 新增 Moodle 本地插件 `local_course_agent`，监听 `core\\event\\user_created`；仅对
  `auth=email` 的新用户，将其幂等加入 `storage-course` 的 `student` 角色。
- Docker 镜像完整复制插件，启动时运行 Moodle CLI upgrade，确保已有数据卷注册事件
  observer；播种/升级后恢复 `moodledata` 为 `www-data:www-data`，避免 root CLI 缓存导致登录页 500。
- 新增可重复验收脚本：`scripts/test_moodle_autoenrol_contract.py`、
  `scripts/real_autoenrol_acceptance.py`。

测试证据：

- TDD 红灯：插件尚不存在时自动入课契约测试失败；实现后
  `MOODLE_AUTOENROL_CONTRACT_OK`。
- 云端 Moodle 插件升级输出成功；插件 PHP 语法检查
  `REMOTE_MOODLE_PHP_LINT_OK`。
- 全新 `auth=email` 测试用户经 Moodle 正式用户创建事件后自动入课：
  `AUTOENROL_OK course=2`；重复触发事件保持单条 enrollment：
  `AUTOENROL_IDEMPOTENT_OK count=1`。
- 使用全新测试用户通过公网 HTTPS 登录，站点首页显示课程、课程页显示 6 章和课程
  Agent、`/agent/` 返回 200：
  `AUTOENROL_WEB_OK home=course-visible course=2 agent=200`。
- 重建后的公共回归再次通过：`SMOKE ACCEPTANCE PASSED`、
  `MOODLE_LOGIN_SMOKE_OK ... chapters=6 resources=20`；登录页重启后 HTTP 200，
  缓存目录属主复核为 `www-data:www-data`。
- 本次部署前备份：`/opt/jbgs-course-agent/backups/20260820-182323`。

本次自动入课验收使用的测试账号保留在云端用于复测，没有删除生产数据；密码、邮箱和
授权码不写入留档。

### 备份敏感文件排除

首次备份校验发现 `caddy-data.tar.gz` 包含 Caddy ACME 私钥，校验器正确拒绝。已修复云端 `scripts/backup.sh`，所有持久卷归档统一排除 `.env`、`*.key`、`*.secret`；旧的失败备份保留未删，新备份 `20260820-020138` 已重新创建并通过完整校验。

## 已留下的可重复测试脚本

- `scripts/real_role_smoke.py`：真实 Moodle 登录、角色桥接和同源 Agent SSE。
- `scripts/real_admin_smoke.py`：管理员角色和运维状态。
- `scripts/real_business_smoke.py`：教师创建/发布、学生提交、教师批改、Moodle 成绩回写。
- `scripts/real_learning_smoke.py`：图谱、资源、画像、推荐、情景和学情权限。
- `scripts/real_surface_smoke.py`：认证、路径、校验、Origin、CSRF、策略和 SSE 契约。
- `scripts/real_kb_release.py`：教师知识库版本、课件上传、三题命中测试和发布流程；正式第三方发布授权后复用执行。
- `agent-adapter/app/course_retrieval.py`、`agent-adapter/tests/test_course_retrieval.py`：页级课件检索和服务器来源证据回归。
- `acceptance/screenshots/browser-postfix-student-ai-result.png`：发布后学生真实 Agent 答案和来源页码。

## 尚未开放的产品边界

1. 公网自助注册入口已开放：`registerauth=email`，登录页存在 `signup.php` 入口；SMTP 已配置并完成 Moodle 实际投递测试；新邮箱注册用户会自动进入储能课程。邀请码和教师审核策略仍需后续确定。

当前已完成正式课件发布、真实 Workflow 命中、教师/学生真实 SSE 对话、来源页码显示、资源跳转、作业提交/批改/成绩回写及安全边界回归，可作为上线验收留档。

## 运行安全

- 未改动防火墙、SSH 密钥、系统服务或用户原有浏览器资料。
- 测试账号和测试作业保留在云端，便于后续复测；没有删除生产数据。
- 本轮创建的 browser-harness 测试标签已在收尾时关闭；保留用户原有浏览器标签不动。后续回归以云端 SSH/容器为主，避免持续占用本机资源。
