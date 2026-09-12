# 学习通式课程平台前端实施计划

## 0. 文档定位

本计划用于把当前“电力系统储能技术课程 Agent 平台”从课程页面原型升级为一个接近学习通使用习惯的课程平台前端。

目标不是复制学习通的品牌、代码、图标或视觉素材，而是复用成熟的学习管理系统信息架构和主要教学工作流，形成具有自己课程内容、知识图谱和 Agent 能力的产品界面。

计划基于以下三类信息：

1. 当前仓库已有实现：Moodle、Agent UI、Agent Adapter、课程数据、图谱、教材、作业、学情和情景接口。
2. 学习通公开官方页面和公开教师/学生使用资料。
3. 需要在 browser-harness 成功连接登录态浏览器后补充的真实页面截图、尺寸、交互和响应细节。

browser-harness 已完成 Chrome 远程调试连接，并完成公开入口实测；当前浏览器没有学习通登录态，因此本文不把未实际观察到的登录后页面细节写成既成事实。公开资料已经确认学习通的核心课程工作流包括课程、章节、任务、讨论、作业、考试、资料、学习记录、考核比例和课堂互动；登录后页面复核仍作为阶段 0 的下一项工作。

## 1. 建设目标

### 1.1 产品目标

建设一个面向高校专业课程的 Web 学习平台，使学生能够完成：

- 登录并查看自己的课程和学习任务。
- 从课程首页进入章节、课件和知识点。
- 在线阅读 PDF、网页课件和课程资料。
- 记录阅读进度、完成任务和查看截止时间。
- 完成客观题、主观题、作业和考试。
- 查看成绩、教师反馈和学情状态。
- 参与课程讨论、收藏、笔记和资源搜索。
- 在同一课程页面使用 Agent 进行问答、学习诊断、学习路径和情景演练。

使教师能够完成：

- 创建和编辑课程目录。
- 上传、归档和发布课件。
- 创建题目、题库、作业和考试。
- 设置开放时间、截止时间、尝试次数、分值和评分规则。
- 查看学生完成率、正确率、知识点掌握情况和提交状态。
- 批改主观题、复核 Agent 初评、发布反馈。
- 发布通知、组织讨论和查看课堂互动数据。

使管理员能够完成：

- 管理课程、班级、用户和角色。
- 查看服务状态、Agent/知识库版本和审计记录。
- 执行内容发布、回滚、备份和恢复检查。
- 处理非法上传、违规内容、权限异常和系统故障。

### 1.2 复刻范围

以“主要工作流相似”作为验收目标，而不是像素级复制。

| 范围 | 目标 | 说明 |
|---|---|---|
| 课程工作台 | 高度相似 | 顶部导航、课程列表、任务提醒、学习进度和最近访问 |
| 课程空间 | 高度相似 | 课程头部、章节树、任务点、资料、讨论和成绩入口 |
| 章节学习 | 高度相似 | 章节列表、资源播放器、PDF 阅读、进度状态和上下文导航 |
| 作业 | 高度相似 | 待完成/已完成/已过期、答题、提交、批改和反馈 |
| 考试 | 核心相似 | 试卷、倒计时、自动保存、提交和结果；防作弊只做合规提示 |
| 讨论 | 核心相似 | 主题、回复、置顶、搜索、教师标识和审核 |
| 教师端 | 核心相似 | 课程编辑、资源、作业、题库、成绩和学情分析 |
| 课堂互动 | 第一版简化 | 签到、投票、抢答、问卷、分组任务可先做事件模型和结果页 |
| Agent | 差异化增强 | 课程问答、引用、学习路径、教师助手和情景演绎 |
| 离线能力 | 后续 | 第一版不做完整离线同步，只保留断点和草稿自动保存 |

### 1.3 不做的事情

- 不复制学习通的品牌标识、商业素材、私有接口或页面源代码。
- 不通过爬虫长期抓取学习通内容；browser-harness 只用于研究公开或用户有权限查看的交互。
- 不在前端直接保存讯飞 API Key、API Secret、Moodle 管理员凭据或数据库凭据。
- 不让模型直接写入成绩、课程资源、知识图谱或权限数据。
- 不在第一阶段实现真实的考试监控、摄像头监控或绕过平台安全限制。
- 不把 Agent 生成的来源、页码、成绩和推荐资源未经校验直接展示为事实。

## 2. 已确认的学习通工作流

### 2.1 公开资料确认的课程结构

学习通官方介绍将其描述为课程学习、知识传播、管理分享和资源整合平台。公开教师指南列出的课程工作流包含：创建课程、搜索和收藏资源、编辑课程目录、添加课程资料、创建班级、添加学生/助教、签到、投票、选人、抢答、主题讨论、评分、测验、问卷、分组任务、直播、通知、作业、考试和课程统计。

学生公开使用手册描述的课程内导航包括：任务模块中的讨论、作业、考试、课堂活动和通知；章节模块中的课程学习；更多模块中的资料、学习记录、考核比例和当前得分。

作业公开说明确认：教师可以编辑或从作业库选择作业发布；客观题自动批阅；主观题需要教师手动批阅、打分或打回重做。

这些信息足以支撑第一版信息架构。登录后真实页面中的颜色、具体导航名称、卡片密度、弹窗方式和响应式细节，需要用户完成登录后通过 browser-harness 截图与操作记录补齐。

### 2.2 browser-harness 实测结果

2026-07-25 通过用户已授权的 Chrome browser-harness 连接完成以下只读观察：

| 地址 | 实测结果 | 对产品计划的影响 |
|---|---|---|
| `https://www.xuexitong.com/` | 公开入口显示学习通品牌、蓝色渐变背景、客户端下载卡片、二维码和多端下载入口；不是课程学习工作台 | 我们的产品首页应优先进入课程工作台，不应照搬软件下载落地页 |
| `https://i.chaoxing.com` | 跳转到 `passport2.chaoxing.com/login` 登录页 | 课程工作台和课程内页面需要登录态，browser-harness 后续必须使用用户主动完成登录的浏览器会话 |
| 登录页可见区域 | “用户登录、忘记密码、验证码登录、其他登录方式、扫码登录、隐私政策、用户协议”等入口 | 登录页需要覆盖验证码、扫码和协议勾选等状态，但不在本项目中代管学习通账号 |

本次 browser-harness 观察没有读取 Cookie、Local Storage、密码或页面外的个人数据，也没有代填账号。登录墙后的课程列表、课程详情、章节、作业、考试、讨论和教师管理页面仍待用户登录后复核；在此之前，相关布局只采用公开指南和课程平台通用模式，验收标记为“待真实页面确认”。

### 2.3 第一版前端信息架构

```text
平台首页
├── 我的课程
├── 待办任务
├── 消息通知
├── 资料库/收藏
├── 学习记录
└── 个人中心

课程空间
├── 课程概览
├── 章节学习
│   ├── 章节目录
│   ├── 课件/PDF
│   ├── 视频/音频
│   ├── 知识点
│   └── 任务点
├── 作业
├── 考试/测验
├── 讨论
├── 资料
├── 学习进度
├── 成绩与反馈
└── 课程 Agent

教师空间
├── 课程编辑
├── 资源管理
├── 题库
├── 作业/考试发布
├── 批改中心
├── 成绩册
├── 学情分析
├── 课堂互动
└── 课程 Agent 助手

管理空间
├── 用户和角色
├── 课程与班级
├── Agent/Workflow 状态
├── 知识库版本
├── 内容审核
├── 审计日志
└── 备份恢复
```

## 3. 建议技术栈

### 3.1 前端主栈

| 层 | 技术 | 选择理由 |
|---|---|---|
| UI 框架 | React + TypeScript | 适合复杂课程状态、教师表格和学生交互；团队已有前端基础时迁移成本低 |
| 构建 | Vite | 适合当前静态 Agent UI 迁移为 SPA；构建产物可以继续由 Nginx/Caddy 提供 |
| 路由 | React Router | 课程、章节、作业、考试、讨论和教师页面需要明确 URL 与浏览器前进后退 |
| UI 组件 | Ant Design | 表格、表单、分页、上传、抽屉、弹窗、Tabs、树和评分等后台/教学组件齐全 |
| 样式 | CSS Modules + CSS 变量 | 保留自己的视觉系统，避免大量全局样式和组件库样式互相覆盖 |
| 服务端状态 | TanStack Query | 处理课程、章节、作业、成绩、消息等缓存、加载、错误和重新验证 |
| 客户端状态 | Zustand | 管理当前用户、当前课程、侧栏、阅读器、Agent 会话和草稿状态 |
| 表单 | React Hook Form + Zod | 统一校验题目、作业、考试、资源和教师配置表单 |
| 富文本 | Tiptap | 用于讨论、通知、作业说明和教师编辑；输出需做 HTML 白名单清洗 |
| PDF 阅读 | PDF.js/react-pdf | 支持页码、缩放、搜索、来源跳转和 Agent 引用定位 |
| 图谱 | `@xyflow/react` | 支持知识点节点、关系、先修路径、状态颜色和点击联动 |
| 图表 | Apache ECharts | 支持完成率、正确率、知识点掌握和班级对比 |
| 图标 | Lucide React | 统一线性图标，按钮同时保留文字或 tooltip，避免手写 SVG |
| 测试 | Vitest + Testing Library + Playwright | 分别覆盖纯逻辑、组件交互和真实浏览器工作流 |
| 可访问性 | axe-core + 手工键盘验收 | 课程学习和考试页面必须支持键盘、焦点和屏幕阅读器基本操作 |

### 3.2 后端和基础设施

| 层 | 建议技术 | 当前项目对应 |
|---|---|---|
| BFF/API | FastAPI + Pydantic | 延续当前 `agent-adapter`，统一权限、契约和讯飞转换 |
| LMS | Moodle | 继续作为课程、身份、基础资源和成绩的主系统 |
| 数据库 | MariaDB | 延续现有 Moodle 数据库；业务扩展数据需要明确归属 |
| Agent | 讯飞星辰 Workflow | 通过 Adapter 调用，前端不直连 |
| 文件存储 | Moodle file API/受控对象存储 | 不允许前端拼接任意本地路径 |
| 反向代理 | Caddy | 延续同源 `/`, `/agent/`, `/api/` 和 HTTPS |
| 实时/流式 | Fetch ReadableStream + SSE | 适合 Agent token、进度和状态事件；不先引入 WebSocket |
| 契约 | OpenAPI + 生成 TypeScript 类型 | 前后端字段变更可被 CI 阻断 |
| 监控 | 结构化日志 + health endpoint | 不记录密钥、完整隐私问题和完整模型原始输出 |

### 3.3 为什么不直接继续扩展当前单文件 HTML

当前 `agent-ui/index.html` 已验证课程 Agent、图谱、教材、作业、学情和情景的最小链路，但所有页面、样式和交互集中在一个文件中。继续堆叠会造成：

- 路由和浏览器前进后退不可维护。
- 学生、教师和管理员权限分支混在同一份 DOM 中。
- 课程列表、章节、作业和阅读器无法独立缓存和测试。
- 大量表格、表单和弹窗会让原生 DOM 事件难以复用。
- 后续接入 Moodle 真实数据时，接口错误和加载状态会扩散到所有函数。

建议保留当前页面作为回退 Demo，同时新建 `frontend/` React 应用，按页面逐步替换；每完成一类页面再切换 Caddy 路由，避免一次性重写导致竞赛 Demo 不可用。

## 4. 页面和交互设计

### 4.1 全局壳层

桌面端：

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Logo/课程平台 │ 搜索课程/资料          │ 消息 │ 帮助 │ 头像/角色菜单 │
├───────────────┼─────────────────────────────────────────────────────┤
│ 我的课程       │                                                     │
│ 待办任务       │                  当前页面内容                       │
│ 资料收藏       │                                                     │
│ 学习记录       │                                                     │
│ 课程管理*      │                                                     │
└───────────────┴─────────────────────────────────────────────────────┘
```

移动端：

```text
┌─────────────────────────────┐
│ 返回 │ 页面标题       ⋯     │
├─────────────────────────────┤
│                             │
│         页面内容             │
│                             │
├─────────────────────────────┤
│ 首页 │ 课程 │ 任务 │ 消息 │ 我 │
└─────────────────────────────┘
```

规则：

- 课程学习页面保持清晰的左侧目录，移动端改成抽屉或顶部章节选择器。
- 页面区块使用平面分组和细边框，不使用多层卡片嵌套。
- 主按钮只保留一个主要动作，危险动作使用二次确认。
- 所有图标按钮提供 tooltip、aria-label 和可见焦点。
- Agent 内容必须同时显示 AI 标识、生成状态、来源状态和重试入口。
- 加载不能用空白页面；使用骨架屏或局部 loading。

### 4.2 首页/工作台

核心组件：

- `TopNav`：平台标识、全局搜索、消息、用户菜单。
- `SidebarNav`：我的课程、任务、资料、记录和教师入口。
- `ContinueLearning`：最近课程和上次学习位置。
- `TaskSummary`：作业、考试、讨论、通知的数量和截止时间。
- `CourseGrid`：课程封面、课程名、教师、进度、最后访问时间。
- `MessageList`：系统通知、教师通知、Agent 任务提醒。
- `EmptyState`、`ErrorState`、`RetryButton`：统一空态和故障体验。

学生首页必须能在 10 秒内回答三件事：

1. 我正在学哪些课？
2. 我现在最需要完成什么？
3. 点击后能回到上次学习位置吗？

### 4.3 课程空间

课程空间采用“课程头部 + 课程导航 + 内容区”的结构：

- 课程头部：课程名、教师、班级、完成度、当前成绩和 Agent 入口。
- 导航 Tabs：概览、章节、作业、考试、讨论、资料、成绩、Agent。
- 章节树：章节、知识点、资源、任务点和完成状态。
- 右侧上下文栏：截止任务、最近通知、当前章节来源和学习建议。

章节树状态：

| 状态 | UI | 规则 |
|---|---|---|
| 未开始 | 灰色圆点 | 没有有效学习记录 |
| 学习中 | 蓝色进度 | 阅读/观看有记录但未完成 |
| 已完成 | 绿色勾 | 达到资源或任务完成条件 |
| 薄弱 | 橙红提示 | 学情规则或测验结果标记 |
| 锁定 | 锁图标 | 先修条件或开放时间未满足 |

### 4.4 章节和资源阅读器

桌面结构：

```text
章节目录 │ 资源阅读器/PDF │ 讨论、笔记、Agent 来源
```

功能：

- 章节目录折叠、当前资源高亮、完成按钮。
- PDF 页码、缩放、搜索、目录和来源定位。
- 课件页码与 Agent 来源卡片联动：点击来源进入对应页。
- 阅读进度节流保存，避免每次滚动都写数据库。
- 支持收藏、笔记、划线；第一版可只做页码级笔记。
- 资源加载失败显示明确错误和下载/重试入口。
- 来源数据来自 manifest，不接受模型自由生成的页码。

### 4.5 作业和考试

作业列表：

- 待完成、进行中、已提交、已批改、已过期五个筛选状态。
- 显示开放时间、截止时间、剩余尝试次数、分值和完成度。
- 一道作业进入一个稳定 URL，刷新后恢复答案草稿。
- 自动保存答案，提交按钮明确区分“保存草稿”和“最终提交”。
- 提交成功显示服务端提交编号和时间，防止重复提交误判。

答题页：

- 左侧题号导航；移动端变为顶部题号抽屉。
- 题目内容、选项、附件、作答区、评分规则和来源提示。
- 客观题本地即时校验格式，最终成绩以服务端为准。
- 主观题可进入 Agent 初评，但必须标记“等待教师复核”。
- 断网时保留本地草稿，恢复后提示用户同步，不自动冒险提交。

考试页：

- 倒计时由服务端开始时间和客户端显示共同计算。
- 自动保存使用版本号，避免多个标签页互相覆盖。
- 离开页面前提示未保存状态，但不承诺绕过系统安全策略。
- 到期后的提交由后端判断，不能仅依赖前端倒计时。

### 4.6 讨论和互动

第一版实现：

- 主题列表、搜索、排序、置顶、教师标识。
- 发帖、回复、@用户、附件白名单。
- 主题状态：开放、已解决、已关闭、待审核。
- 教师/管理员删除和审核有审计日志。
- Agent 可以把“课程问答”建议转成讨论草稿，但不能自动代替学生发帖。

后续实现：

- 投票、问卷、签到、抢答、分组任务和课堂直播入口。
- 课堂互动统一成 `activity` 模型，避免为每种活动单独重做课程页面。

### 4.7 Agent 页面

Agent 不单独做成脱离课程的聊天网站，而是嵌入课程语境：

- 从课程首页进入：默认携带课程 ID、章节 ID和当前知识点。
- 从教材页进入：默认携带资源 ID、页码和来源上下文。
- 从图谱进入：默认携带知识点和先修路径。
- 从作业进入：只允许使用与当前作业相关的辅导模式，不直接给出未授权答案。
- 教师端进入：提供备课、出题草稿、作业分析和批改初评。

回答区分四种状态：

1. 生成中：显示流式文本和取消按钮。
2. 已完成：显示答案、来源、引用页码、AI 标识和反馈按钮。
3. 资料不足：明确告诉用户课程资料不足，给出查阅建议。
4. 服务异常：显示错误编号、重试和返回教材入口，不伪造答案。

## 5. 路由规划

### 5.1 学生路由

```text
/                       工作台
/courses                我的课程
/courses/:courseId      课程概览
/courses/:courseId/chapters
/courses/:courseId/chapters/:chapterId
/courses/:courseId/resources/:resourceId
/courses/:courseId/assignments
/courses/:courseId/assignments/:assignmentId
/courses/:courseId/exams
/courses/:courseId/exams/:examId
/courses/:courseId/discussions
/courses/:courseId/discussions/:topicId
/courses/:courseId/materials
/courses/:courseId/progress
/courses/:courseId/grades
/courses/:courseId/agent
/tasks                    全局任务
/messages                 消息
/favorites                收藏和笔记
/profile                  个人中心
```

### 5.2 教师和管理员路由

```text
/teacher/courses
/teacher/courses/:courseId/overview
/teacher/courses/:courseId/editor
/teacher/courses/:courseId/resources
/teacher/courses/:courseId/question-bank
/teacher/courses/:courseId/assignments
/teacher/courses/:courseId/exams
/teacher/courses/:courseId/grading
/teacher/courses/:courseId/gradebook
/teacher/courses/:courseId/analytics
/teacher/courses/:courseId/activities
/teacher/courses/:courseId/agent

/admin/users
/admin/courses
/admin/agent-status
/admin/knowledge-bases
/admin/audit-log
/admin/backup
```

### 5.3 路由权限

路由守卫只负责体验层拦截；真正权限必须在 Adapter/API 重新校验。

| 角色 | 学生路由 | 教师路由 | 管理路由 |
|---|---:|---:|---:|
| student | 允许 | 拒绝 | 拒绝 |
| teacher | 允许 | 允许授权课程 | 拒绝 |
| admin | 按配置 | 允许维护 | 允许 |

## 6. API 和数据模型

### 6.1 前端 API 分组

```text
GET  /api/session
POST /api/session/open

GET  /api/courses
GET  /api/courses/:course_id
GET  /api/courses/:course_id/chapters
GET  /api/courses/:course_id/progress

GET  /api/resources/:resource_id
GET  /api/resources/:resource_id/content
POST /api/resources/:resource_id/progress
POST /api/resources/:resource_id/notes

GET  /api/tasks
GET  /api/assignments/:assignment_id
PUT  /api/assignments/:assignment_id/draft
POST /api/assignments/:assignment_id/submit
GET  /api/assignments/:assignment_id/result

GET  /api/exams/:exam_id
PUT  /api/exams/:exam_id/answer
POST /api/exams/:exam_id/submit

GET  /api/discussions
POST /api/discussions
POST /api/discussions/:topic_id/replies

GET  /api/knowledge-graph
GET  /api/knowledge-graph/nodes/:node_id
GET  /api/textbook/resources

POST /api/course-agent/chat
POST /api/course-agent/stream
POST /api/course-agent/feedback

GET  /api/teacher/courses/:course_id/analytics
POST /api/teacher/assignments
POST /api/teacher/exams
POST /api/teacher/grading/:submission_id
```

当前已有接口应通过 `/api` BFF 逐步归一，不要求前端直接访问 Moodle Web Service 或讯飞 URL。

### 6.2 统一返回结构

```json
{
  "status": "ok",
  "data": {},
  "meta": {
    "request_id": "req-...",
    "course_id": "storage-course",
    "version": "v1"
  }
}
```

错误：

```json
{
  "status": "error",
  "error": {
    "code": "ASSIGNMENT_ALREADY_SUBMITTED",
    "message": "该作业已经提交，请刷新查看结果",
    "retryable": false
  },
  "meta": {"request_id": "req-..."}
}
```

### 6.3 核心数据模型

```text
User
  id, display_name, role, avatar_url, last_seen_at

Course
  id, title, subtitle, teacher_ids, class_ids, cover, status

Chapter
  id, course_id, parent_id, title, order, prerequisite_ids

Resource
  id, chapter_id, type, title, file_id, page_count, duration, manifest_hash

LearningProgress
  user_id, resource_id, percent, last_page, completed_at, updated_at

KnowledgePoint
  id, chapter_id, name, status, prerequisite_ids, resource_ids

Activity
  id, course_id, type, title, open_at, due_at, visibility, status

Assignment
  id, activity_id, question_ids, max_attempts, total_score, rubric_version

Submission
  id, assignment_id, user_id, attempt, status, submitted_at, score, review_state

DiscussionTopic
  id, course_id, author_id, title, body, status, pinned, created_at

AgentSession
  id, user_id, course_id, mode, context_hash, workflow_id, created_at

AgentMessage
  id, session_id, role, content, sources, ai_generated, created_at
```

### 6.4 业务归属原则

- Moodle 负责登录、课程基础信息、用户角色、基础资源和最终成绩同步。
- Agent Adapter 负责讯飞鉴权、Agent 会话、来源校验、限流、幂等和安全边界。
- 课程扩展数据可以先由 Adapter 的结构化存储承载，但必须在文档中记录最终归属和备份方式。
- 前端只消费 API，不读取 MariaDB，不解析 `.env`，不调用讯飞平台。
- 成绩写入必须包含 `submission_id`、评分人/评分来源、评分规则版本和审计记录。

## 7. 推荐代码结构

第一版迁移建议：

```text
frontend/
├── src/
│   ├── app/
│   │   ├── router.tsx
│   │   ├── providers.tsx
│   │   └── permissions.ts
│   ├── components/
│   │   ├── layout/
│   │   ├── course/
│   │   ├── resource-viewer/
│   │   ├── assignment/
│   │   ├── discussion/
│   │   ├── agent/
│   │   └── feedback/
│   ├── pages/
│   │   ├── dashboard/
│   │   ├── course/
│   │   ├── teacher/
│   │   └── admin/
│   ├── features/
│   │   ├── session/
│   │   ├── courses/
│   │   ├── tasks/
│   │   ├── resources/
│   │   ├── assessments/
│   │   ├── discussions/
│   │   ├── knowledge-graph/
│   │   └── course-agent/
│   ├── api/
│   │   ├── client.ts
│   │   ├── types.ts
│   │   └── generated.ts
│   ├── stores/
│   ├── styles/
│   └── test/
├── public/
├── package.json
├── vite.config.ts
└── Dockerfile
```

迁移原则：

1. 先抽取当前单文件中的 API 调用和业务逻辑测试。
2. 用 `CourseShell`、`AgentPanel`、`ResourceList` 等组件替换原生拼 DOM。
3. 先迁移课程概览和章节页面，再迁移作业、教师端和管理员端。
4. 每个阶段都保留 `/legacy-agent/` 作为回退页面，直到新页面通过验收。
5. 不把所有页面都做成巨型组件；页面负责组装，feature 负责数据和业务行为。

## 8. 分阶段实施计划

### 阶段 0：browser-harness 真实观察与基线（0.5～1 天）

前置：Chrome 允许远程调试；如果页面进入登录墙，由用户自行完成登录，然后通知继续；不代填密码、不读取 Cookie 或本地存储。

操作记录：

1. 访问学习通公开入口，记录登录前首页、可见导航、窗口宽度和基础视觉。
2. 在用户已登录且有权限的情况下，依次记录首页、课程列表、课程详情、章节、资料、作业、考试、讨论、成绩和教师管理页。
3. 每个页面先截图，再进行一次点击/返回/刷新，记录 URL、入口、加载状态和错误状态。
4. 记录桌面视口 1440、1280、1024 和移动视口 390/412 的布局变化。
5. 只记录功能结构和交互，不导出 Cookie、Local Storage、密码、个人隐私和课程原文。

输出：

```text
research/xuexitong/
├── page-map.md
├── interaction-inventory.md
├── responsive-notes.md
├── screenshots/
└── acceptance-observations.md
```

如果无法获得登录态，允许用公开官方资料补足功能清单，但视觉验收标记为“待复核”。

### 阶段 1：前端工程化和设计系统（1～2 天）

- 初始化 React + TypeScript + Vite。
- 接入 React Router、TanStack Query、Zustand、Ant Design、Zod。
- 建立颜色、间距、字体、边框、状态色和响应式断点。
- 实现 `AppShell`、顶部导航、侧边栏、移动底部导航、权限守卫和错误边界。
- 接入现有 `/api/course/session/open`，显示真实角色和 AI 标识。
- 建立 MSW/API fixture，使未接入真实 Workflow 时页面仍可演示。

完成标准：

- 学生、教师、管理员能看到不同菜单。
- 无权限路由返回明确页面，不出现白屏。
- 页面在 390px、768px、1280px 和 1440px 无横向溢出。
- `npm run build`、单元测试和静态 UI 契约通过。

### 阶段 2：学生工作台和课程空间（2～3 天）

- 实现首页课程卡片、最近学习、待办任务和消息。
- 实现课程概览、章节树、课程 Tab、进度摘要和 Agent 入口。
- 把现有知识图谱、教材和作业入口放入课程空间，而不是堆在同一页。
- 统一加载、空数据、错误、无权限和重试状态。

完成标准：

- 学生从首页 3 次点击内进入任意章节。
- 刷新课程页后保留课程和章节 URL。
- 课程目录与现有 6 章、20 个资源、20 个知识点一致。
- 课程数据不来自前端硬编码，使用 API fixture 或真实 API。

### 阶段 3：章节、教材和资料阅读器（2～4 天）

- 实现章节树和资源列表。
- 接入 PDF.js/react-pdf。
- 实现页码、搜索、缩放、目录、进度和收藏。
- 实现来源点击回教材页。
- 实现知识点状态、先修路径和图谱/教材联动。

完成标准：

- 20 份课件均能打开或给出清晰的资源错误。
- 来源卡片的文件、章节和页码与 manifest 一致。
- 阅读进度刷新后保留。
- 移动端可以在抽屉中切换章节，不发生页面重叠。

### 阶段 4：作业、测验、考试和成绩（3～5 天）

- 实现任务中心和课程内作业列表。
- 实现客观题、简答题、文件上传题的答题组件。
- 实现草稿自动保存、幂等提交、截止时间和尝试次数。
- 实现客观题自动评分、主观题教师复核和反馈展示。
- 实现考试倒计时、自动保存、提交确认和成绩页。
- 复用 `Activity` 模型承载作业、考试、测验、问卷等活动。

完成标准：

- 刷新、重复点击和网络重试不会生成重复提交。
- 服务端而非前端决定最终分数和截止状态。
- 学生不能访问教师批改和题库管理。
- 教师能看到待批改数量、提交状态和成绩分布。

### 阶段 5：讨论、通知和课堂互动（2～4 天）

- 实现讨论主题、回复、搜索、置顶和教师标识。
- 实现课程通知和全局消息中心。
- 建立 `Activity` 活动抽象，先实现通知、投票、问卷的结果页。
- 签到、抢答、选人和分组任务以可配置活动卡片实现。

完成标准：

- 学生可以查看和参与课程讨论。
- 教师可以发布通知并查看互动结果。
- 审核、删除和置顶行为有权限校验和审计记录。

### 阶段 6：教师工作台和管理员页面（3～5 天）

- 课程目录拖拽/排序、资源上传和发布状态。
- 题库、题目编辑、作业/考试发布设置。
- 批改中心、评分规则、Agent 初评和教师复核。
- 成绩册、完成率、正确率、知识点掌握和风险学生列表。
- 知识库版本、Workflow 状态、服务状态、审计和备份入口。

完成标准：

- 教师只能管理授权课程。
- 管理员状态信息脱敏，不显示密钥。
- 未发布课件或知识库版本不能被普通学生检索。
- 教师可以修改 Agent 生成的内容后再发布。

### 阶段 7：课程 Agent 深度嵌入（2～4 天）

- 统一 `AgentPanel`，支持非流式和 SSE 流式回答。
- 根据页面上下文自动带入课程、章节、知识点、资源页码和活动 ID。
- 支持问答、学习诊断、学习路径、教师备课、出题草稿、批改初评和情景演绎。
- 来源卡片支持打开教材页；来源未知则显示待核验。
- 加载、取消、超时、重试、限流、Workflow 不可用和资料不足均有独立状态。

完成标准：

- 前端没有讯飞密钥。
- Agent 请求经过 Adapter 并带有会话和权限。
- 多轮会话不会跨用户或跨课程串线。
- Agent 无法把自由文本直接写入成绩或课程资源。
- 真实 Workflow 未配置时，页面明确显示演示/Mock 状态。

### 阶段 8：性能、移动端和竞赛交付（2～3 天）

- 路由级代码分割和资源懒加载。
- PDF 和图谱按需加载。
- 图片压缩、缓存头、静态资源 hash。
- 移动端触摸、键盘和屏幕阅读器验收。
- Playwright 三角色流程录制。
- 生成截图、视频、案例记录、验收报告和部署说明。

完成标准：

- 首屏静态内容在竞赛服务器上可接受。
- 课程页面没有明显横向溢出或组件重叠。
- 3 个竞赛案例可以从真实输入到结果完整演示。
- 录屏不展示密钥、个人隐私和后台管理接口。

## 9. 关键实现思路

### 9.1 Moodle 与自建前端的关系

推荐保留 Moodle 作为身份、课程和基础教学数据的权威来源，但不强迫用户长期停留在 Moodle 原生页面：

```text
浏览器
  -> Caddy 同源入口
      -> React 前端
          -> Agent Adapter/BFF
              -> Moodle Web Service 或受控 bridge
              -> 讯飞 Workflow
              -> 课程扩展存储
```

第一阶段可以继续通过 Moodle 课程页嵌入新 Agent 前端；第二阶段用 Caddy 将 `/app/` 或 `/agent/` 指向 React SPA。身份通过 Moodle 会话桥接，不在前端重复实现一套账号体系。

### 9.2 课程目录和任务点

不要把章节、资源、作业、考试分别写成互不相干的页面。使用：

```text
Course
  -> Chapter
      -> Resource
      -> KnowledgePoint
      -> Activity
          -> Assignment / Exam / Quiz / Survey / Discussion
```

这样可实现：

- 章节页统一显示资源和任务点。
- 课程进度统一计算资源完成和活动完成。
- Agent 可根据章节、知识点和活动上下文工作。
- 教师可以从同一个目录发布课件、作业和测验。

### 9.3 服务器状态和前端状态

TanStack Query 负责服务器数据：课程、章节、任务、成绩、讨论、知识库和服务状态。

Zustand 只负责界面状态：

- 当前用户和角色的轻量缓存。
- 当前课程和章节选择。
- 侧栏展开、阅读器布局和移动端抽屉。
- Agent 当前会话 ID、流式文本和取消控制器。
- 未提交草稿和临时筛选条件。

不要把完整课程、成绩和消息复制到多个全局 store；这会造成刷新失效、跨标签页冲突和脏数据。

### 9.4 幂等与自动保存

所有写操作携带：

```text
Idempotency-Key
X-Moodle-Sesskey
X-Request-ID
```

自动保存使用业务签名：

```text
draft:{user_id}:{activity_id}:{attempt}:{question_id}
```

最终提交使用服务端生成的提交 token。重复请求返回原提交结果，不重复创建成绩或提交记录。

### 9.5 Agent 来源和安全

Agent 返回：

```json
{
  "answer": "...",
  "sources": [
    {
      "resource_id": "resource-3-4",
      "source_file": "3.4-储能变流器拓扑及并网控制.pdf",
      "chapter": "第3章",
      "page": 12,
      "manifest_hash": "...",
      "knowledge_base_version": "..."
    }
  ],
  "ai_generated": true,
  "needs_review": false
}
```

Adapter 先核对来源，再发送到前端。前端只能渲染通过校验的来源；不允许直接渲染模型返回的 HTML，使用 Markdown 解析器时必须做安全过滤。

## 10. 测试与验收计划

### 10.1 自动化测试

| 类别 | 必测内容 |
|---|---|
| 单元测试 | 进度计算、状态转换、权限判断、倒计时、提交幂等、来源校验 |
| 组件测试 | 章节树、资源阅读器、答题组件、Agent 状态、表格、移动抽屉 |
| API 契约 | OpenAPI 路由、错误结构、分页、权限、字段版本 |
| Playwright | 三角色登录、课程导航、资源、作业、考试、讨论、Agent、教师批改 |
| 安全 | XSS、CSRF、越权、文件上传、敏感日志、来源伪造、Prompt Injection |
| 性能 | 首屏、课程列表、PDF 首页、图谱、3 个并发 Agent 请求 |
| 可访问性 | 键盘焦点、按钮名称、表单标签、颜色对比、错误提示 |
| 恢复 | 刷新、断网、服务重启、Workflow 超时、Qdrant/知识库不可用 |

### 10.2 关键人工验收场景

学生：

1. 从首页进入课程，打开第 3 章课件第 12 页。
2. 从页码来源打开 Agent，询问储能变流器并核验来源。
3. 完成一道作业，刷新页面，确认草稿保留。
4. 重复点击提交，确认只有一条提交记录。
5. 查看成绩、教师反馈和学习路径。
6. 在手机尺寸下完成一次章节切换和一次 Agent 提问。

教师：

1. 新建或编辑一个章节资源。
2. 生成题目草稿，修改后发布作业。
3. 查看学生提交，复核 Agent 初评并修改分数。
4. 查看知识点完成率和错误率。
5. 发布通知和讨论主题。

管理员：

1. 查看脱敏服务状态。
2. 创建知识库版本并上传合法/损坏文件。
3. 确认未发布版本不会被学生检索。
4. 重启 Adapter/Workflow 相关服务并验证错误恢复。
5. 执行备份和隔离恢复。

### 10.3 视觉和交互验收门槛

- 1440px、1280px、1024px、768px、412px、390px 六个视口截图无明显重叠。
- 页面主体不能依赖横向滚动才能完成课程学习。
- 所有按钮文字都适合容器宽度，长中文不会溢出。
- 表格在移动端改成卡片或横向滚动容器，不挤压文字。
- 章节树、PDF、Agent 来源三者切换后 URL、标题和高亮状态一致。
- 加载、空数据、错误、权限拒绝、超时和成功状态都可被人工识别。
- AI 输出始终有明显 AI 标识；来源缺失时不能伪造“已引用”。

## 11. 性能目标

以 2 vCPU、8 GB RAM 服务器作为第一阶段目标：

| 指标 | 目标 |
|---|---:|
| 静态首页可交互 | P95 ≤ 3 秒，受网络影响单独记录 |
| 课程数据首屏 | P95 ≤ 4 秒 |
| PDF 首页可见 | P95 ≤ 5 秒 |
| 图谱首屏 | P95 ≤ 4 秒 |
| 普通 API 错误率 | 0%（测试环境） |
| Agent 首 token | 目标 ≤ 8 秒，按上游单独记录 |
| Agent 完整回答 | 目标 ≤ 30 秒 |
| 3 个并发 Agent 请求 | 无 OOM、无上下文串线 |
| 自动保存 | 用户感知延迟 ≤ 1 秒，服务端异步持久化 |

不要把讯飞上游延迟归因于前端；报告需要分开记录浏览器、Caddy、Adapter、Workflow 和知识库耗时。

## 12. 交付物

```text
frontend/
├── 源码和构建配置
├── .env.example
├── Dockerfile
└── README.md

acceptance/frontend/
├── route-matrix.md
├── visual-acceptance-report.md
├── playwright-report/
├── screenshots/
└── performance-report.md

research/xuexitong/
├── page-map.md
├── interaction-inventory.md
├── responsive-notes.md
└── acceptance-observations.md
```

代码提交禁止包含：

- `deploy/.env`。
- API Key、API Secret、Cookie、Session、个人账号和真实学生数据。
- 原始课程 PDF、DOCX、XLSX、ZIP，除非提交规则明确要求且已确认授权。
- 真实学生作业、成绩和联系方式。

## 13. 第一版建议优先级

### P0：必须做

- 学生工作台。
- 课程空间和六章目录。
- 课件/PDF 阅读和页码来源。
- 任务中心、作业、提交、评分结果。
- 课程讨论基础能力。
- Agent 嵌入、流式、来源、错误和 AI 标识。
- Moodle 会话、角色、CSRF、幂等和权限隔离。
- 移动端无重叠、无横向溢出。

### P1：比赛 Demo 前应做

- 教师课程编辑。
- 题库、作业发布、批改和成绩册。
- 学情图表和知识图谱联动。
- 通知、收藏、笔记。
- 知识库版本和 Workflow 状态页。
- Playwright 三角色回归和真实用户验收。

### P2：后续增强

- 签到、投票、抢答、问卷和分组任务完整闭环。
- 直播。
- PWA 离线阅读和跨设备同步。
- 更复杂的推荐模型和学习行为分析。
- 与学校教务系统、统一身份认证和一卡通对接。

## 14. 立即执行清单

1. 在 Chrome 完成 browser-harness 远程调试授权。
2. 采集学习通真实页面状态、视口截图和交互记录，补充 `research/xuexitong/`。
3. 依据观察结果确定导航文案、颜色、卡片密度和移动端断点。
4. 在仓库新增 `frontend/` React + TypeScript + Vite 工程。
5. 先迁移 `agent-ui/index.html` 的 API 调用和现有验收夹具，不改变 Adapter 契约。
6. 实现 AppShell、课程首页、课程空间和章节阅读器。
7. 接入现有 6 章、20 资源、20 知识点和作业夹具。
8. 完成学生三角色 Playwright 流程后再开发教师端。
9. 配置真实讯飞 Workflow 和知识库后，将 Agent Mock 夹具切换为真实冒烟。
10. 完成视觉、功能、安全、性能、恢复和竞赛材料审核。

## 15. 当前结论

当前项目最适合采用“保留 Moodle 作为 LMS 和身份底座，使用 React 前端重做学习通式课程壳层，继续复用 Agent Adapter 和现有课程数据”的路线。

这条路线能复用已经通过测试的权限、CSRF、幂等、来源校验、图谱、教材、作业和 Agent 边界，又能解决当前单文件 Agent UI 不适合扩展完整课程平台的问题。

第一版不需要实现学习通的全部后台和课堂生态。只要优先完成学生学习闭环、教师教学闭环、Agent 来源闭环和管理员安全闭环，就能形成可演示、可验收、可继续扩展的课程平台。

正式实施前必须完成 browser-harness 真实页面复核，特别是登录后的课程导航、任务卡片、章节详情、作业答题、教师编辑和移动端布局；如果真实页面与公开资料不一致，以用户有权限看到的实际页面和赛方要求为准。

## 16. 参考资料

- [学习通官方介绍](https://www.xuexitong.com/)
- [超星学习通教师版公开课程指南](https://mooc1.chaoxing.com/mooc-ans/nodedetailcontroller/visitnodedetail?courseId=218003938&knowledgeId=429967193)
- [超星学习通学生学习使用手册](https://yjsy.hrbeu.edu.cn/_upload/article/files/ef/21/e708a4ea4358a9e3f4f7f7358446/305ca52a-5b39-4d3b-9524-a946e86fb705.pdf)
- [当前项目实施与验收计划](IMPLEMENTATION_PLAN.md)
- [当前项目完成状态](PROJECT_STATUS.md)
