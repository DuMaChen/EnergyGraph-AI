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
4. 每个阶段都保留 `/agent/` 作为 legacy 回退页面，直到新页面通过验收。
5. 不把所有页面都做成巨型组件；页面负责组装，feature 负责数据和业务行为。

## 8. 分阶段实施计划

### 阶段 0：browser-harness 真实观察与基线

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

### 阶段 1：前端工程化和设计系统

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

### 阶段 2：学生工作台和课程空间

- 实现首页课程卡片、最近学习、待办任务和消息。
- 实现课程概览、章节树、课程 Tab、进度摘要和 Agent 入口。
- 把现有知识图谱、教材和作业入口放入课程空间，而不是堆在同一页。
- 统一加载、空数据、错误、无权限和重试状态。

完成标准：

- 学生从首页 3 次点击内进入任意章节。
- 刷新课程页后保留课程和章节 URL。
- 课程目录与现有 6 章、20 个资源、20 个知识点一致。
- 课程数据不来自前端硬编码，使用 API fixture 或真实 API。

### 阶段 3：章节、教材和资料阅读器

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

### 阶段 4：作业、测验、考试和成绩

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

### 阶段 5：讨论、通知和课堂互动

- 实现讨论主题、回复、搜索、置顶和教师标识。
- 实现课程通知和全局消息中心。
- 建立 `Activity` 活动抽象，先实现通知、投票、问卷的结果页。
- 签到、抢答、选人和分组任务以可配置活动卡片实现。

完成标准：

- 学生可以查看和参与课程讨论。
- 教师可以发布通知并查看互动结果。
- 审核、删除和置顶行为有权限校验和审计记录。

### 阶段 6：教师工作台和管理员页面

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

### 阶段 7：课程 Agent 深度嵌入

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

### 阶段 8：性能、移动端和竞赛交付

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

## 17. 构建批次、审查和验收总则

本节将前面的产品和技术计划转化为可执行的交付门禁。后续任何功能都必须以“一个构建批次”为单位交付；未通过本批次的审查和验收，不得进入下一批次，也不得把预览数据或 Mock 结果写入正式验收报告。

### 17.1 构建批次定义

每个批次必须有唯一编号、明确范围和可回退版本：

```text
BUILD-000-baseline
BUILD-010-frontend-foundation
BUILD-020-session-and-shell
BUILD-030-student-workbench
BUILD-040-course-and-resource
BUILD-050-assessment
BUILD-060-discussion-and-message
BUILD-070-teacher-workbench
BUILD-080-admin-and-audit
BUILD-090-agent-context
BUILD-100-release-hardening
```

批次编号不代表 Git commit 数量；一个批次可以包含多个小提交，但必须在合并前形成一个可部署、可测试、可回退的版本。

每个批次开始前必须记录：

| 项目 | 要求 |
|---|---|
| 基线提交 | 记录 `git rev-parse HEAD`，基线必须通过上一批次验收 |
| 目标范围 | 列出本批次新增、修改和明确不做的功能 |
| 影响面 | 标记前端、Adapter、Moodle bridge、SQLite/MariaDB、文件存储、Caddy、测试和部署文件 |
| 数据迁移 | 说明新增字段、索引、状态值、默认值、回滚方式和备份要求 |
| 权限矩阵 | 明确 student、teacher、admin、未登录用户的读写权限 |
| API 变更 | 列出新增/修改/废弃路由、请求字段、响应字段和错误码 |
| 验收夹具 | 指定学生、教师、管理员和异常数据夹具，不允许只用前端硬编码数据 |
| 回退点 | 指定上一通过版本、数据库回退策略和前端路由回退策略 |

### 17.2 每个批次的固定流程

每个批次必须严格执行以下顺序：

```text
需求冻结
  -> 数据/API/权限设计审查
  -> 实现与局部测试
  -> 代码审查
  -> 静态检查和单元测试
  -> API/数据库集成测试
  -> 浏览器和三角色验收
  -> 安全、性能和恢复检查
  -> 证据归档
  -> 通过门禁或回退
```

任何一步失败都必须记录失败原因和修复提交。不得通过修改测试夹具、关闭权限校验、打开 Mock 或手工修改数据库来获得绿色结果。

### 17.3 统一通过条件

一个批次只有同时满足以下条件才算通过：

- 代码审查没有未关闭的 P0/P1 问题；P2 问题必须记录负责人和计划完成批次。
- `bash -n scripts/*.sh` 和 `python3 -m compileall -q agent-adapter scripts` 通过。
- 相关单元测试、API 契约测试和集成测试全部通过；禁止以“暂时跳过”代替失败。
- 三类角色的权限测试全部通过，未登录请求不能访问受保护数据。
- 失败、空数据、无权限、超时、重复提交和服务不可用状态均有可识别界面。
- 数据写操作可以幂等重试，不产生重复提交、重复成绩、重复通知或重复审计记录。
- 未经 Adapter 来源校验的 Agent 文件名、页码、成绩和资源 ID不能进入用户可核验结果。
- 390px、412px、768px、1024px、1280px、1440px 截图无明显重叠、截断和不可操作的横向溢出。
- 证据目录包含测试命令、完整输出摘要、截图/视频、浏览器视口、提交号和环境信息。
- 通过后才能打标签，例如 `acceptance/BUILD-030-student-workbench`；失败版本不得标记为 release。

### 17.4 统一审查清单

每个批次的审查人必须逐项确认：

| 审查项 | 必查内容 |
|---|---|
| 需求边界 | 实现内容与批次目标一致，没有顺手引入未审查的大功能 |
| 数据归属 | Moodle、Adapter store、文件存储和前端缓存的权威来源明确 |
| 权限 | API 重新校验课程、对象、角色和所有者，不能只依赖路由隐藏 |
| 输入校验 | 类型、长度、枚举、时间、分页、文件大小和文件类型均由服务端校验 |
| 写操作 | `X-Moodle-Sesskey`、`Idempotency-Key`、请求 ID、重复请求和并发行为明确 |
| 输出安全 | 前端使用 `textContent` 或安全 Markdown 渲染，不使用任意 `innerHTML`/`eval` |
| 状态机 | 草稿、开放、提交、批改、发布、撤回、过期和回滚状态有合法迁移表 |
| 错误处理 | 上游错误不泄露堆栈、密钥、Cookie、内部 URL 或完整隐私输入 |
| 可观测性 | 日志包含脱敏 request ID、业务对象 ID、耗时和结果，不包含 Secret |
| 回退 | 代码、数据库迁移、静态资源和 API 兼容策略可以恢复到上一版本 |

### 17.5 统一测试命令和证据格式

在项目根目录执行：

```bash
RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh
python3 scripts/test_api_contract.py
python3 scripts/test_ui_contract.py
```

前端工程建立后必须提供以下脚本，命令名不得随意变化；以下前端命令均在 `frontend/` 目录执行：

```bash
cd frontend
npm ci
npm run test:all
npm run lint
npm run typecheck
npm run test:unit -- --run
npm run test:component -- --run
npm run test:hardening -- --run
npm run test:e2e:mock -- --workers=1
npm run build
npm run test:e2e -- --workers=1
npm run test:a11y -- --workers=1
npm run test:axe -- --workers=1
```

其中 `test:unit`、`test:component` 和 `test:hardening` 是按测试名称筛选的定向门禁；`test:all` 才是 Vitest 全量门禁，任何被筛选命令跳过的测试都必须由 `test:all` 覆盖，不能把 skipped 误记为全量通过。

每个批次在 `acceptance/frontend/BUILD-xxx/` 保存：

```text
metadata.json       # commit、时间、环境、浏览器和配置模式
scope.md            # 本批次范围和不做项
review.md           # 审查清单、问题和处理结果
test-output.txt     # 自动化命令摘要和退出码
api-contract.json   # 本批次 API 契约快照或 diff
screenshots/        # 六个视口的关键页面和错误状态
videos/             # 仅保存必要的验收流程视频
manual-acceptance.md
rollback.md
```

证据不得包含 API Key、API Secret、Cookie、Session、真实学生姓名、真实联系方式、真实成绩或未经授权的课程原文件。

## 18. 分批次构建与验收门禁

### BUILD-000：现状基线和回退点

**构建范围**

- 锁定当前 `agent-ui/index.html` 作为 legacy 回退页面。
- 固定当前 API 路由清单、数据库结构、课程 manifest、图谱基线和 Mock 夹具。
- 记录当前浏览器页面和服务器部署状态，不把现有预览数据标记为真实平台数据。

**构建后代码审查**

- 核对仓库没有新增密钥、`.env`、Cookie、真实用户数据和大体积原始课程文件。
- 核对 `course-data/normalized/manifest.json`、`graph-baseline.json` 和测试夹具可被新环境读取。
- 核对所有现有写 API 都有角色、CSRF 和幂等要求。
- 核对 legacy 页面在没有 Moodle 登录态时显示预览/未登录状态，而不是伪造真实成功。

**自动化测试**

```bash
git status --short --branch
bash -n scripts/*.sh
python3 -m compileall -q agent-adapter scripts
RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh
```

**人工验收**

- 未登录访问课程 API 返回明确的 `401` 或受控错误 JSON。
- Mock 学生、教师、管理员各完成一次登录、读取和受限操作。
- 预览模式明确显示“预览/Mock”，不能被截图当作真实 Workflow 证据。
- 使用重复 `Idempotency-Key` 不产生第二条业务记录。

**通过门禁**

- 基线测试全部通过。
- 记录基线 commit、API 路由数量、课程数据摘要和当前已知缺口。
- 失败时只允许修复基线问题，不得开始 React 迁移。

### BUILD-010：前端工程化和设计系统

本批次可以在 `BUILD-000` 的外部数据输入阻断期间准备数据无关的工程骨架，但这属于“实现中”而不是门禁通过：不得切换生产路由、不得把预览课程当作真实数据、不得跳过 `BUILD-000` 的课程数据校验。只有前置门禁关闭后，才能执行本批次最终验收和发布切换。

**构建范围**

- 新建 `frontend/` React + TypeScript + Vite 工程。
- 接入 React Router、TanStack Query、Zustand、Zod、组件库和现有设计变量。
- 建立 `AppShell`、权限守卫、错误边界、加载/空态/错误态和移动端导航。
- 保留 `/agent/` 作为可回退页面；暂不改变现有 Adapter API。

**构建后代码审查**

- 页面组件不直接访问数据库、`.env`、讯飞 URL 或 Moodle 管理接口。
- API 请求集中在 `frontend/src/api/`，类型集中管理，不能在页面中散落 `fetch` 字段猜测。
- Query 数据和界面状态分离；完整课程、成绩和消息不能复制到多个全局 store。
- 路由守卫只负责体验，所有权限仍由 Adapter/API 校验。
- 当前只允许客户端 `BrowserRouter`；不得启用 SSR、RSC、Server Actions 或服务端路由数据反序列化。若未来引入这些能力，必须先重新完成 React Router 安全审计。
- 键盘焦点、按钮名称、表单标签和响应式断点有测试或验收记录。

**自动化测试**

```bash
npm ci
npm run lint
npm run typecheck
npm run test:unit -- --run
npm run test:component -- --run
npm run build
```

**人工验收**

- student、teacher、admin、未登录四种状态进入首页时菜单不同且无白屏。
- 390px 和 1440px 下侧栏、顶部栏、底部导航、错误提示均可操作。
- API 断开时显示错误横幅和重试入口，不渲染假数据为真实数据。
- 刷新和浏览器前进/后退不会丢失当前合法 URL。

**通过门禁**

- 构建产物可由 Nginx 提供，健康检查通过。
- 新前端与 legacy 页面可以同时部署。
- 任一前端构建失败时 Caddy 可以切回 `/agent/`，不影响现有 Agent Demo。

### BUILD-020：会话、全局壳层和权限矩阵

**构建范围**

- 接入 `/api/course/session/open`，展示真实角色、课程 ID、CSRF 状态和 AI 标识。
- 实现平台导航、课程导航、用户菜单、通知入口和移动端抽屉。
- 固定学生、教师、管理员和未登录的路由权限表。

**构建后代码审查**

- 前端不接收或持久化 API Key、API Secret、Moodle 管理员凭据。
- CSRF token 只从同源会话响应获取，所有写请求统一注入。
- 角色和课程权限来自服务器响应，不能由 URL、localStorage 或浏览器字段提升。
- 会话过期后清理敏感内存状态，显示重新登录提示，不自动重试写请求。

**自动化测试**

- 未登录访问所有受保护路由均得到 `401` 或登录引导。
- student 访问教师和管理员 API 均得到 `403`。
- teacher 只能访问授权课程；admin 状态接口返回脱敏信息。
- Origin、sesskey、请求体大小和错误包络测试全部通过。
- Playwright 覆盖登录、刷新、退出、会话过期和返回上一页。
- 本地 Mock Adapter 浏览器验收必须覆盖 student/teacher 菜单、空 API 数据和开发代理 Origin 重写；这只能证明 Adapter 契约，不能替代真实 Moodle 账号。

**人工验收**

- 三种角色分别登录，菜单、课程范围和按钮权限与矩阵一致。
- 修改 URL 中的 course ID、assignment ID、submission ID 不得越权看到其他对象。
- 退出后按浏览器后退不能重新显示受保护数据。

**通过门禁**

- 权限测试零失败。
- 浏览器开发者工具中看不到任何讯飞凭据。
- 所有受保护写操作都能在日志中用 request ID 追踪，但日志不含隐私正文。

### BUILD-030：学生工作台和课程空间

**构建范围**

- 实现课程列表、最近学习、任务摘要、消息摘要、学习进度和继续学习入口。
- 实现课程概览、课程 Tab、章节树、课程 Agent 入口。
- 课程卡片、章节和任务从 API/fixture 获取，删除前端硬编码的课程主数据。

**构建后代码审查**

- 课程、章节、资源和活动使用稳定 ID，排序由服务器字段决定。
- 空课程、无任务、加载中、请求失败和无权限状态均独立处理。
- 课程切换时清理上一课程的资源、Agent 上下文和未提交草稿，防止串课。
- 进度百分比由服务端规则或明确的纯函数计算，不能由页面显示值反推成绩。

**自动化测试**

- API 契约覆盖课程、章节、任务和进度分页、字段类型、空集合和错误结构。
- 组件测试覆盖课程卡片、章节树、任务筛选、加载/错误/空态。
- Playwright 覆盖：登录 → 课程列表 → 课程空间 → 第 3 章 → 刷新 → 返回课程列表。
- 断网后恢复请求不会重复创建任何数据。

**人工验收**

- 学生从首页 3 次点击内进入任意章节。
- 页面刷新后 URL、课程、章节和当前 Tab 保持一致。
- 6 章、20 个资源和 20 个知识点与 manifest/图谱基线一致。
- 截止任务排序、已完成状态和学习进度与 API 返回一致。

**通过门禁**

- 不再依赖预览硬编码数据才能展示真实课程页面。
- 学生不能看到教师工具、管理员状态或未授权课程。
- 三个桌面视口和两个移动视口无重叠、截断和不可点击元素。

### BUILD-040：章节、PDF 阅读器和学习进度

**构建范围**

- 接入 PDF.js/react-pdf 或同等阅读器。
- 实现章节目录、资源打开、页码、缩放、搜索、来源跳转和页码级进度。
- 实现收藏、页码笔记和“标记完成”的最小闭环。
- 接入 manifest 来源校验，不接受模型自由生成的资源路径。

**构建后代码审查**

- 资源访问通过 Moodle file API/受控 bridge，前端不能拼任意本地文件路径。
- `resource_id`、`page`、`manifest_hash` 服务端重新核验；越界页码返回受控错误。
- 阅读进度使用节流写入、版本号和幂等键；多个标签页不会覆盖更新的进度。
- 笔记和收藏按 user/course/resource 隔离，并有删除和恢复策略。

**自动化测试**

- 合法资源、未知资源、越界页码、非法 source 和无权限资源测试通过。
- 进度节流、刷新恢复、重复保存、并发更新和断网草稿测试通过。
- Playwright 覆盖打开第 3 章课件第 12 页、搜索、缩放、刷新和来源回跳。
- PDF 首屏、图谱和来源卡片性能测量纳入报告。

当前实现必须绑定以下可执行检查：

```bash
python3 -m unittest -q scripts.test_course_store
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_resource_progress_api.py
npm run test:unit -- --run
npm run test:component -- --run
npm run test:e2e:mock
```

其中资源进度接口固定为 `GET/PUT /api/student/resources/{resource_id}/progress`，写请求必须携带 `Idempotency-Key`；正式 PDF 未挂载时，API 返回 `mount_status=pending_mount`，浏览器只能验收明确的“文件待挂载”状态，不能使用占位 PDF 代替阅读器验收。

**人工验收**

- 20 份资源均能打开，不能打开时显示文件名、错误编号和重试/返回入口。
- 点击 Agent 来源能准确打开对应资源和页码。
- 页面缩放、目录抽屉和移动端返回操作不覆盖正文或底部导航。
- 阅读 50% 后刷新，进度仍保留且不会重复写入记录。

**通过门禁**

- 来源文件、章节和页码与 manifest 完全匹配。
- 未授权用户不能通过修改 URL 读取其他课程或资源。
- 页面不执行模型返回的 HTML/脚本。

### BUILD-050：作业、测验、考试和成绩

**构建范围**

- 统一 `Activity` 模型，覆盖作业、测验、考试和问卷的公共字段。
- 实现客观题、简答题、文件上传题、草稿、自动保存、提交和结果页。
- 实现开放时间、截止时间、尝试次数、服务端计分、教师复核和成绩回写。
- 第一版考试只实现合规的服务端时间和提交校验，不实现摄像头监控。

**构建后代码审查**

- 最终分数、截止状态、尝试次数和提交时间全部由服务端决定。
- 答案草稿和最终提交分开存储；最终提交后不可由学生覆盖。
- 重复提交、重复点击、网络重试和多标签页提交使用服务端幂等。
- 主观题 Agent 只能生成待复核建议，不能直接写最终成绩。
- 成绩写入包含 submission ID、评分人/来源、rubric 版本、时间和审计记录。
- 文件题执行扩展名、MIME、大小、内容和病毒扫描策略，拒绝可执行文件。

**自动化测试**

- 客观题计分、部分分、空答案、非法答案和未知题目 ID 测试通过。
- 截止前、截止时、截止后、重复提交、超出尝试次数测试通过。
- 草稿自动保存、版本冲突、断网恢复和多标签页覆盖测试通过。
- teacher 批改、复核、改分、发布成绩和 Moodle bridge 回写测试通过。
- Playwright 覆盖学生答题/刷新/提交/查看结果和教师批改全流程。

**人工验收**

- 学生完成一次客观题和主观题，刷新后答案不丢失。
- 重复点击提交只生成一个 submission ID。
- 截止时间到达后前端提示不能代替服务端判断。
- 教师可查看提交、复核 Agent 初评、修改分数并留下审计记录。
- 学生不能访问题库、他人提交、批改接口和教师成绩册。

**通过门禁**

- 不允许使用前端分数作为最终成绩。
- 成绩回写失败必须显示失败状态，不能显示“同步成功”。
- 任何考试异常都可以通过 request ID、submission ID 和审计记录定位。

### BUILD-060：讨论、通知和课堂互动

**构建范围**

- 实现讨论主题、回复、搜索、排序、置顶、教师标识、关闭和审核。
- 实现课程通知、全局消息、已读状态和任务提醒。
- 以 `Activity` 抽象先实现通知、投票、问卷结果页；签到/抢答/分组任务先做事件模型。

**构建后代码审查**

- 富文本输出使用白名单清洗，禁止脚本、事件属性、任意 iframe 和危险 URL。
- @用户、附件、删除、置顶、审核和关闭均由服务端校验权限。
- 消息已读和讨论写操作幂等；重复点击不会创建重复主题或重复回复。
- Agent 只能生成讨论草稿，不能自动替学生发帖或替教师发布通知。

**自动化测试**

- XSS、越权读写、附件类型/大小、重复发帖、审核状态机测试通过。
- 学生、教师、管理员分别测试主题可见范围和删除/审核权限。
- Playwright 覆盖发帖、回复、搜索、置顶、通知已读和错误重试。

**人工验收**

- 学生能发起主题、回复和查看教师标识。
- 教师能发布通知、置顶主题、审核内容并查看操作记录。
- 被关闭或待审核内容在学生端状态正确，不出现空白或未解释的消失。
- 移动端输入框、回复列表和附件错误状态可用。

**通过门禁**

- 讨论内容没有存储型 XSS。
- 审核、删除、置顶和通知发布均有审计记录。
- 通知未读数与服务端状态一致，刷新不会重复计数。

### BUILD-070：教师工作台、题库、发布和成绩册

**构建范围**

- 实现教师课程概览、章节编辑、资源上传/归档/发布。
- 实现题库、题目编辑、作业/考试配置和发布撤回。
- 实现批改中心、成绩册、完成率、正确率、知识点掌握和风险学生列表。
- 支持 Agent 草稿生成，但所有发布内容必须教师确认。

**构建后代码审查**

- 教师管理范围以服务器授权课程为准，不能通过 course ID 越权。
- 发布操作区分草稿、审核、已发布、撤回和归档，合法状态迁移写入审计。
- 拖拽排序使用服务端版本号或排序令牌，冲突时提示重新加载。
- 资源替换不删除仍被历史成绩和来源引用的版本。
- Agent 生成题目、评分规则和反馈必须经过结构化 schema、ID 存在性和教师确认。

**自动化测试**

- 教师授权课程/非授权课程、学生越权、管理员例外权限测试通过。
- 题目 schema、选项、答案、分值、rubric、知识点 ID 和章节 ID 测试通过。
- 发布、撤回、归档、重复发布、并发编辑和资源版本测试通过。
- 成绩册汇总与逐题成绩、学情统计和 Moodle 回写结果一致。
- Playwright 覆盖教师创建题目 → 发布作业 → 查看提交 → 批改 → 发布成绩。

**人工验收**

- 教师可完成一次资源发布、题目编辑、作业发布和批改。
- 未确认的 Agent 草稿不会出现在学生端。
- 教师修改分数后学生端、成绩册和 Moodle bridge 的状态一致；失败有明确提示。
- 教师看不到其他课程教师的题目、学生提交和成绩。

**通过门禁**

- 教师端没有可直接写成绩的前端绕过路径。
- 发布前内容、评分规则和知识点引用均可追溯到操作者和版本。
- 课程编辑异常时不破坏已发布课程和历史成绩。

### BUILD-080：管理员、知识库、审计和恢复

**构建范围**

- 实现用户/角色、课程/班级、服务状态、Workflow、知识库版本、审计和备份页面。
- 实现知识库 draft → processing → tested → published → rollback 生命周期。
- 实现合法/损坏文件上传、manifest 校验、命中测试和发布门槛。
- 实现管理员脱敏状态、操作确认和恢复检查入口。

**构建后代码审查**

- 管理员页面不显示 API Key、API Secret、数据库密码、Cookie 和原始 Authorization。
- 知识库未发布版本不能被学生 Agent 使用；回滚必须绑定版本和 Workflow。
- 上传文件执行大小、类型、路径、内容、来源 manifest 和重复文件检查。
- 审计日志包含操作者、角色、动作、对象、结果、request ID 和时间，正文脱敏。
- 删除、回滚、恢复、批量改分和用户禁用必须二次确认并支持幂等。

**自动化测试**

- 知识库生命周期、manifest 指纹、黄金问题、来源页码和回滚测试通过。
- 非法文件、超大请求、路径穿越、重复上传和未发布访问测试通过。
- 管理员状态脱敏、审计字段、备份校验和隔离恢复测试通过。
- Playwright 覆盖管理员创建版本 → 上传 → 测试 → 发布 → 回滚。

**人工验收**

- 管理员可看到配置状态但看不到任何 Secret 原文。
- 学生在知识库未发布时得到明确“尚未发布”状态，不能检索未发布内容。
- 上传合法、损坏和超大文件时页面状态准确，失败不会留下假成功记录。
- 执行隔离恢复后课程、用户、资源、Adapter 数据和 Caddy 状态可检查。

**通过门禁**

- 备份归档内部不含 `.env`、私钥、Secret、Cookie 和不应提交的生产数据。
- 至少完成一次当前代码和当前数据库的隔离恢复，并保存恢复日志。
- 知识库发布必须有真实 manifest、黄金测试和操作者记录。

### BUILD-090：Agent 上下文、流式体验和教学场景

**构建范围**

- 建立统一 `AgentPanel`，支持问答、学习诊断、学习路径、教师助手、出题草稿、批改初评和情景演绎。
- 从课程、章节、知识点、教材页、作业和教师页面带入受服务端过滤的上下文。
- 支持 SSE token/source/done/error、取消、超时、重试、限流、资料不足和 Workflow 不可用状态。
- 来源卡片点击回教材；未知来源显示“待核验”，不渲染为可信引用。

**构建后代码审查**

- Agent mode、course ID、resource ID、student profile、rubric 和 graph context 都由 Adapter 重新确定或查询。
- 多轮会话绑定 user、course、session 和上下文 hash，不能跨用户、跨课程串线。
- 模型不能直接写成绩、题目发布、课程资源、知识图谱或权限；所有写入经过结构化 schema 和人工/规则门禁。
- 流式连接关闭、半帧、坏 JSON、重复 done、上游 401/429/5xx 和客户端取消均有明确处理。
- 完整隐私问题、完整模型原始响应和密钥不得写日志。

**自动化测试**

- SSE 帧解析、非流式/流式协议、断流、超时、错误映射和取消测试通过。
- 来源文件、章节、页码、manifest hash、资源 ID 和知识库版本严格匹配测试通过。
- 学生/教师模式权限、Prompt Injection、安全边界和课程外问题测试通过。
- Playwright 覆盖从教材页提问、来源回跳、学习诊断、情景开始/轮次/结束和重试。
- Mock 和真实 Workflow 测试分开记录；没有真实凭据时只能标记协议通过。

**人工验收**

- 生成中、已完成、资料不足、服务异常四种状态均可识别且可恢复。
- 课程外问题不会被伪装成课程知识答案；资料不足时不生成伪造页码。
- 学生从作业进入 Agent 时不能获得未授权答案；教师进入时可以使用备课/批改模式。
- 来源点击能打开准确资源页；来源不合法时显示待核验并不生成可点击证据。
- 同一浏览器同时打开两个课程的 Agent，不发生上下文混用。

**通过门禁**

- 前端无讯飞凭据。
- 真实 Workflow 未配置时所有页面明确显示 Mock/演示，不能作为真实主链路验收。
- 真实 Workflow 和真实知识库分别完成非流式、流式、黄金问题、来源核验和性能记录后，才能标记 P0 Agent 通过。

### BUILD-100：发布前硬化和最终验收

**构建范围**

- 路由级代码分割、静态资源缓存、PDF/图谱懒加载和错误监控。
- 完成移动端、可访问性、性能、备份恢复、三角色 Playwright 和竞赛材料。
- 使用正式域名和 HTTPS；关闭生产 Mock 鉴权和 Mock Workflow。

**构建后代码审查**

- 生产 Compose、Caddy、环境模板和前端构建产物只暴露必要端口。
- 生产配置不包含示例密码、默认 salt、Mock 开关和调试接口。
- 所有 P0/P1 路由均有 API 契约和浏览器流程；废弃接口已标记并有兼容期。
- 备份、恢复、日志、证书、资源权限和数据库迁移说明可由新成员复现。

**自动化测试**

```bash
RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh
bash scripts/pre_submission_audit.sh
bash scripts/check_submission_materials.sh
bash scripts/full_restore_rehearsal.sh
cd frontend
npm run lint
npm run typecheck
npm run test:all
npm run test:unit -- --run
npm run test:component -- --run
npm run test:hardening -- --run
npm run test:e2e:mock -- --workers=1
npm run test:e2e -- --workers=1
npm run test:a11y -- --workers=1
npm run test:axe -- --workers=1
npm run build
```

当前仓库状态说明：`frontend/package.json` 已提供 `test:all`、`test:a11y` 和 `test:axe` 脚本。本地自定义 Playwright 检查覆盖控件命名、键盘焦点、基础对比度、移动端溢出和错误/空状态；axe 当前扫描渲染后的 `<main>` 默认规则集并已包含 `color-contrast`，但仍不能替代正式真实角色覆盖、六视口人工验收或 T0-T6 证据。

真实环境另行执行：

```bash
bash scripts/real_workflow_preflight.sh deploy/.env
bash scripts/xingchen_smoke.sh
bash scripts/smoke_acceptance.sh
```

**人工验收**

- 学生完整流程：登录 → 课程 → 第 3 章课件 → 来源问答 → 作业草稿 → 提交 → 成绩/反馈 → 学习建议。
- 教师完整流程：登录 → 课程编辑 → 资源发布 → 出题 → 作业发布 → 批改 → 成绩册 → 学情分析。
- 管理员完整流程：服务状态 → 知识库创建/测试/发布/回滚 → 审计 → 备份 → 隔离恢复。
- 390px、412px、768px、1024px、1280px、1440px 六个视口完成关键流程截图。
- 断网、刷新、会话过期、Workflow 超时、知识库未发布和成绩回写失败分别验收。

**最终通过条件**

最终版本必须同时满足：

- 所有 P0 功能通过真实三角色验收。
- 列入本期范围的 P1 功能通过自动化和人工验收。
- 真实讯飞 Workflow 已发布并完成五次流式冒烟。
- 真实知识库版本、文件清单、manifest hash、黄金命中和来源页码均有证据。
- 正式 Demo 使用 HTTPS 域名，不使用 IP + HTTP 作为最终地址。
- 备份和隔离恢复使用当前代码、当前数据库和当前配置复测通过。
- 没有开放的 P0/P1 缺陷、越权、XSS、来源伪造、重复提交或成绩一致性问题。
- `PRE_SUBMISSION_READY` 和 `SUBMISSION_MATERIALS_READY` 均成功输出。

**失败和回退条件**

出现以下任一情况，发布必须阻断并回退到最近通过版本：

- 真实用户无法登录、课程无法进入或核心 API 返回 HTML/未包络错误。
- 学生可以访问教师/管理员数据，或教师可以跨课程操作。
- 重复点击生成重复提交、重复成绩、重复发布或重复通知。
- Agent 返回未知来源被展示为已核验来源。
- 生产环境仍启用 Mock 鉴权/Workflow，或页面泄露凭据。
- 数据库迁移不可回退、备份无法恢复或当前版本无法启动。
- 任一关键移动端视口存在遮挡、横向溢出或无法完成主流程。

## 19. 批次验收记录模板

每次构建完成后复制以下模板到 `acceptance/frontend/BUILD-xxx/manual-acceptance.md`：

```markdown
# BUILD-XXX 验收记录

## 1. 基本信息

- 构建编号：
- Git commit：
- 执行记录时间（仅用于审计证据，不作为完成条件）：
- 验收人：
- 环境：local / staging / production
- Mock 鉴权：true / false
- Mock Workflow：true / false
- 浏览器和版本：

## 2. 本批次范围

- 新增：
- 修改：
- 不做：
- 影响 API：
- 影响数据表/迁移：

## 3. 代码审查

| 项目 | 结果 | 证据/问题 |
|---|---|---|
| 权限和对象归属 | PASS/FAIL | |
| CSRF 和幂等 | PASS/FAIL | |
| 输入和输出安全 | PASS/FAIL | |
| 数据迁移和回退 | PASS/FAIL | |
| 日志和敏感信息 | PASS/FAIL | |
| 移动端和可访问性 | PASS/FAIL | |

## 4. 自动化测试

| 命令 | 退出码 | 结果 |
|---|---:|---|
| `npm run lint` |  | PASS/FAIL |
| `npm run typecheck` |  | PASS/FAIL |
| `npm run test:all` |  | PASS/FAIL |
| `npm run test:unit -- --run` |  | PASS/FAIL |
| `npm run test:component -- --run` |  | PASS/FAIL |
| `npm run test:hardening -- --run` |  | PASS/FAIL |
| `npm run test:e2e:mock -- --workers=1` |  | PASS/FAIL/NOT_IMPLEMENTED |
| `npm run test:e2e` |  | PASS/FAIL |
| `npm run test:a11y` |  | PASS/FAIL/NOT_IMPLEMENTED |
| `npm run test:axe -- --workers=1` |  | PASS/FAIL/NOT_IMPLEMENTED |
| 相关后端/验收脚本 |  | PASS/FAIL |

## 5. 人工验收

| 编号 | 角色 | 场景 | 结果 | 截图/视频 |
|---|---|---|---|---|
| 1 | student |  | PASS/FAIL | |
| 2 | teacher |  | PASS/FAIL | |
| 3 | admin |  | PASS/FAIL | |
| 4 | 未登录/异常 |  | PASS/FAIL | |

## 6. 缺陷和处理

| ID | 严重度 | 描述 | 是否阻断 | 修复 commit |
|---|---|---|---|---|

## 7. 结论

- [ ] PASS：允许进入下一构建批次
- [ ] CONDITIONAL：只允许修复指定 P2，不允许扩大范围
- [ ] FAIL：阻断并回退

回退版本：
回退原因：
验收人签名/确认：
```

## 20. 计划执行后的变更控制

- 每个批次开始后不得临时加入未审查的跨模块功能；新增需求进入下一批次。
- API 字段、状态值、权限规则和数据表变更必须先更新本计划、OpenAPI 和验收夹具，再写实现。
- 任何“为了让测试通过”而修改生产逻辑、降低权限、放宽来源校验或打开 Mock 的改动必须阻止合并。
- 真实 Workflow、真实知识库、真实角色和正式 HTTPS 证据必须单独标记，不能与本地夹具混在同一张通过表中。
- 每完成一个批次，更新 `PROJECT_STATUS.md`、`docs/README.md` 和对应验收报告中的状态、commit、证据路径和剩余风险。
- 当实际系统与本计划不一致时，以已部署代码、OpenAPI、数据库迁移和最新验收记录为事实来源，并在下一批次修订计划。

经过以上门禁后，本计划的“完成”不再表示页面看起来像学习通，而是表示每个学习闭环都有可复现构建、可审查实现、自动化测试、三角色人工验收、失败处理、证据归档和可回退版本。

## 21. API 驱动验收和测试接口接入规范

本节是对前面所有构建批次的强制补充。前端页面是否“看起来完成”不能作为功能完成依据；每项功能必须绑定一个或多个可执行 API 测试。用户后续提供的测试 API、OpenAPI 文件、测试账号和测试数据是接口验收的输入，但不能替代服务端权限、数据一致性和浏览器流程验收。

### 21.1 不使用任务时间作为完成条件

- 本计划不设置开发天数、截止日期、每日目标或按时间排序的完成要求。
- 所有阶段都必须完成；阶段顺序由依赖关系和上一阶段验收结果决定。
- 一个阶段可以反复构建、修复和重新验收，直到达到本计划规定的通过条件。
- “已经开发一段时间”“页面已能打开”“Mock 已通过”都不能视为阶段完成。
- 验收记录中的执行时间只用于证据追溯，不用于管理任务进度，也不构成通过条件。
- 阶段唯一的完成依据是：范围内的 API 测试、数据验证、权限测试、浏览器测试、安全测试和证据归档全部通过。

### 21.2 用户提供测试 API 的最小输入

在开始真实 API 验收前，用户或 API 提供方必须提供以下信息。缺失项不得通过猜测补齐，必须在 `api-test-manifest.yaml` 中标记为 `BLOCKED_INPUT`：

| 输入 | 必须内容 | 禁止内容 |
|---|---|---|
| API 地址 | 测试环境 HTTPS 基础地址、允许的路径前缀和证书要求 | 生产密钥、内网密码、未授权第三方地址 |
| API 文档 | OpenAPI JSON/YAML，或每个接口的 method、path、参数、响应示例 | 只给截图而没有可执行请求定义 |
| 鉴权方式 | Cookie、Moodle session、Bearer、API key、签名或组合鉴权 | 把真实 Secret 直接写入 Markdown |
| 测试角色 | 未登录、student、teacher、admin 的账号引用和可用课程范围 | 真实学生账号、真实成绩和个人联系方式 |
| 测试数据 | 固定课程、章节、资源、题目、作业、提交和知识库版本 ID | 不可恢复的生产对象 ID |
| 重置能力 | 数据重置、夹具重新导入、测试租户或一次性 namespace | 直接清空生产数据库 |
| 流式协议 | SSE/WebSocket 的地址、事件格式、结束标志、超时和取消行为 | 只提供一段无法重复的手工演示 |
| 文件接口 | 允许的扩展名、MIME、大小、上传结果和清理方式 | 未经授权的真实课程原文件 |
| 限制策略 | 速率、并发、请求体、分页、超时和测试窗口 | 要求绕过限流或安全策略 |
| 期望版本 | API 版本、数据库 schema 版本、前端 commit 和环境名称 | 未声明版本的混合接口 |

推荐提供以下脱敏文件：

```text
api-test-manifest.yaml       # API 测试定义和断言
openapi.test.json            # 测试环境接口契约
fixtures/                    # 不含个人隐私的固定测试数据
accounts.test.example.json   # 仅保存账号标识引用，不保存密码或 Token
README.md                    # 测试环境、重置方法和允许的操作
```

### 21.3 凭据安全硬门禁

参考截图中出现了 API Secret 和 API Key 字段。该类信息已经属于凭据暴露，不得继续用于测试或提交材料。处理规则如下：

1. 立即在对应服务平台撤销或轮换截图中暴露的凭据。
2. 新凭据只写入本机未跟踪的 `.env.test.local`、CI Secret 或密码管理器。
3. 计划、源代码、截图、视频、Issue、验收报告和聊天记录只能出现环境变量名，例如 `TEST_API_TOKEN`。
   对 Spark Assistant 必须使用并保持一致的变量名为 `TEST_API_BASE_URL`、`TEST_APP_ID`、`TEST_API_KEY` 和 `TEST_API_SECRET`；`TEST_API_TOKEN` 只适用于采用单 Token 鉴权的其他 HTTP API。
4. 测试输出必须过滤 `Authorization`、`Cookie`、`Set-Cookie`、`API-Key`、`Secret` 和 Token 值。
5. 测试日志只允许记录请求 method、脱敏 path、状态码、request ID、耗时和断言结果。
6. 测试账号必须是专用账号，权限只覆盖测试课程和测试租户。
7. 任何凭据进入 Git、构建日志、浏览器截图或公开附件，立即判定当前构建批次 FAIL，并执行凭据轮换。

本地示例只允许使用变量名：

```bash
export TEST_API_BASE_URL="https://test.example.invalid"
export TEST_API_TOKEN="<loaded-from-secret-manager>"
export TEST_STUDENT_SESSION="<loaded-from-secret-manager>"
```

### 21.4 测试 API 的配置文件规范

`api-test-manifest.yaml` 必须至少包含以下字段。实际路径可以由用户提供的 API 文档替换，但测试 ID 和断言语义必须保持稳定：

```yaml
manifest_version: "1"
environment: test
base_url_env: TEST_API_BASE_URL
api_version: v1
tls:
  verify: true
  allowed_hosts:
    - test.example.invalid
auth:
  mode: bearer
  token_env: TEST_API_TOKEN
  redaction_headers:
    - authorization
    - cookie
actors:
  anonymous:
    auth: none
  student:
    credential_ref: TEST_STUDENT_SESSION
    role: student
    course_ids: [course-test-001]
  teacher:
    credential_ref: TEST_TEACHER_SESSION
    role: teacher
    course_ids: [course-test-001]
  admin:
    credential_ref: TEST_ADMIN_SESSION
    role: admin
    course_ids: [course-test-001]
fixtures:
  reset_command: "provided-out-of-band"
  course_id: course-test-001
  chapter_id: chapter-test-003
  resource_id: resource-test-034
  assignment_id: assignment-test-001
  submission_id: submission-test-001
assertion_policy:
  require_json_envelope: true
  require_request_id: true
  reject_html_for_api_errors: true
  allow_extra_response_fields: true
endpoints: []
```

每个 `endpoints` 项必须包含：

```yaml
- id: session.open
  actor: student
  method: POST
  path: /api/course/session/open
  headers:
    content-type: application/json
  body: {}
  expect:
    status: 200
    content_type: application/json
    json_paths:
      - path: $.status
        equals: ok
      - path: $.data.role
        equals: student
      - path: $.data.csrf_token
        type: string
        non_empty: true
      - path: $.meta.request_id
        type: string
        non_empty: true
  side_effects:
    - session_is_authenticated
  negative_cases:
    - id: anonymous
      actor: anonymous
      expect_status: 401
```

### 21.5 单接口的强制测试顺序

每个接口都必须按以下顺序测试，不允许只测试成功请求：

| 编号 | 测试 | 方法 | 必须断言 |
|---:|---|---|---|
| 1 | 连通性 | HTTPS/TLS、DNS、健康检查 | 地址、证书、Host 和 API 前缀正确 |
| 2 | 未登录 | 去掉 Cookie/Token | 返回规定的 `401`，不能返回数据或登录 HTML |
| 3 | 无效鉴权 | 错误 Token、过期 Session、错误签名 | 返回 `401`，响应不泄露内部鉴权细节 |
| 4 | 合法成功 | 使用对应角色和固定夹具 | 状态码、Content-Type、包络、字段类型和业务值正确 |
| 5 | 参数边界 | 空值、最短值、最大值、超长值、Unicode、非法枚举 | 返回规定的 `400/422`，不产生副作用 |
| 6 | 对象权限 | 修改课程、资源、作业、提交 ID | 未授权返回 `403` 或 `404`，不能泄露对象存在性 |
| 7 | 重复请求 | 相同 Idempotency-Key 重放 | 返回同一业务结果，不创建第二条记录 |
| 8 | 并发请求 | 同一业务操作并发发送 | 至多一个业务写入，其余返回复用/冲突结果 |
| 9 | 状态迁移 | 草稿、发布、提交、批改、回滚等状态 | 只有定义的状态迁移成功，非法迁移被拒绝 |
| 10 | 持久化 | 成功后重新 GET、刷新、重新登录 | 数据存在、归属正确、版本和状态一致 |
| 11 | 错误恢复 | 上游超时、服务重启、断流、数据库错误 | 返回稳定错误码，重试规则明确，无假成功 |
| 12 | 审计 | 所有管理和成绩写操作 | 操作者、角色、对象、动作、request ID、结果和时间可追溯 |
| 13 | 清理 | 测试数据回收或重置 | 只清理测试 namespace，不影响其他测试和生产数据 |

一个接口只有在该接口的正向和适用负向测试全部通过后，才可以在对应批次标记 `API_PASS`。

通用 HTTP 接口使用上面的 13 步顺序；Spark Assistant WebSocket 不把“去掉 Cookie/Token”或 HTTP JSON 包络当作适用前提，而是使用 21.10 的握手、业务帧、流式响应、异常帧和关闭握手顺序。两类结果必须分开记录，不能用 HTTP fixture 的 PASS 覆盖 WebSocket 的 BLOCKED 或 FAIL。

### 21.6 统一响应断言

普通 JSON API 的最低响应要求：

```json
{
  "status": "ok",
  "data": {},
  "error": null,
  "meta": {
    "request_id": "non-empty-string",
    "version": "v1"
  }
}
```

错误响应最低要求：

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "STABLE_MACHINE_CODE",
    "message": "可向用户展示的消息",
    "retryable": false
  },
  "meta": {
    "request_id": "non-empty-string",
    "version": "v1"
  }
}
```

统一断言：

- API 成功响应不能返回 HTML、登录页、堆栈、调试对象或空响应。
- 错误 `code` 必须是稳定机器码，前端不得通过中文 `message` 判断业务分支。
- `request_id` 必须存在且在客户端、Adapter 日志和审计记录中一致。
- 时间字段必须是带时区的 ISO 8601，或在 API 契约中明确统一为 UTC。
- 分页响应必须明确 `items`、`page`、`page_size`、`total`；不得由前端猜测总数。
- 成绩、进度、页码、尝试次数和金额类字段必须是规定的数值类型并检查范围。
- 未知字段可以保留，但核心字段缺失、类型错误或 null 语义不明必须 FAIL。

### 21.7 API 测试执行方式

测试实现采用三层，不允许只依赖其中一层：

**第一层：契约测试**

- 读取 `openapi.test.json` 和 `api-test-manifest.yaml`。
- 验证 method、path、参数、状态码、Content-Type、包络和 JSON Schema。
- 发现接口实现与契约不一致时，先修订契约并经审查确认，不能静默放宽断言。

**第二层：Python API 集成测试**

推荐使用 `pytest + httpx`，每个测试使用独立的 request ID 和测试 namespace：

```python
def assert_error(response, status_code, code):
    assert response.status_code == status_code
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"]["code"] == code
    assert payload["meta"]["request_id"]
```

每个测试必须保存请求摘要和响应摘要，但经过脱敏；失败时保存 JSON diff，不保存鉴权头和完整隐私输入。

**第三层：Playwright 浏览器测试**

- 浏览器只通过同源前端操作，不绕过页面直接改数据库。
- API 响应可以监听用于断言，但最终仍要断言页面可见结果、URL、按钮状态和错误提示。
- 需要验证页面刷新、浏览器前进/后退、重复点击、断网恢复和移动视口。
- Agent SSE 测试必须同时断言 token、source、done、error 的页面状态。

### 21.8 API 类型测试标准

所有字符串字段至少测试：空字符串、首尾空白、中文、Emoji、超长文本、HTML、脚本片段和 Unicode 控制字符。

所有数值字段至少测试：缺失、null、0、负数、最大允许值、超过最大值、浮点、字符串数字和 NaN/Infinity 表示。

所有枚举字段至少测试：每个合法值、大小写变体、未知值、空值和跨角色不允许值。

所有 ID 字段至少测试：合法 ID、其他课程 ID、已删除 ID、格式错误 ID、空 ID、重复 ID 和批量超过上限。

所有时间字段至少测试：开放前、开放时、开放后、截止前、截止时、截止后、跨时区和夏令时差异（如适用）。

所有列表接口至少测试：默认分页、最小分页、最大分页、超过最大分页、空结果、过滤、排序和重复数据。

所有文件接口至少测试：允许类型、错误扩展名、伪造 MIME、空文件、超过大小、路径穿越文件名、重复文件和损坏内容。

### 21.9 API 失败判定和证据要求

以下任意情况直接判定所属构建批次 FAIL：

- 成功接口返回 HTML、未包络 JSON、缺少 request ID 或状态码与契约不一致。
- 未登录或低权限角色获得受保护数据，哪怕页面没有显示该数据也算失败。
- 重复请求创建第二个作业提交、成绩、主题、通知、知识库版本或审计事件。
- API 返回模型生成的未知来源，前端将其显示为已核验来源。
- 失败响应暴露堆栈、内部地址、Cookie、Token、数据库错误或完整隐私内容。
- 数据写入成功但重新读取、刷新或 Moodle 同步失败且界面显示成功。
- 测试通过依赖手工预先修改数据库、关闭权限、开启生产 Mock 或跳过清理。

每个接口的证据至少包括：

```text
request-summary.json       # method、脱敏 path、角色、request_id、body hash
response-summary.json      # status、content-type、脱敏 JSON、响应 hash
assertions.json             # 每个 JSONPath、期望值、实际值、结果
side-effects.json           # 数据条数、状态、版本、审计和同步结果
negative-cases.json         # 未登录、越权、边界、重复和错误恢复
```

### 21.10 Spark Assistant WebSocket 专项规范

当用户提供的接口地址是 `ws://` 或 `wss://spark-openapi.../v1/assistants/{assistant_id}` 时，必须按 Spark Assistant 协议测试，不能把它当作当前项目的 HTTP Workflow API。两条链路必须在配置、客户端、测试脚本和验收报告中分开：

| 链路 | 协议 | 必需配置 | 当前项目状态 |
|---|---|---|---|
| Xingchen Workflow | HTTPS POST + JSON/SSE | `XINGCHEN_WORKFLOW_URL`、`XINGCHEN_FLOW_ID`、`XINGCHEN_API_KEY`、`XINGCHEN_API_SECRET` | 现有 Adapter 已按此实现 |
| Spark Assistant | WSS + 签名握手 + JSON 流式帧 | `TEST_API_BASE_URL`、`TEST_APP_ID`、`TEST_API_KEY`、`TEST_API_SECRET` | 需要专用客户端或 Adapter 分支 |

Spark Assistant 本地测试配置只允许使用以下变量名，不写入真实值：

```text
TEST_API_BASE_URL=wss://spark-openapi.example.invalid/v1/assistants/assistant-id
TEST_APP_ID=<app-id>
TEST_API_KEY=<loaded-from-secret-manager>
TEST_API_SECRET=<loaded-from-secret-manager>
```

根据官方协议，专项测试必须覆盖：

1. URL 使用真实 `wss://` 或 `ws://`，不能把文档中的 `ws(s)://` 原样作为 URL。
2. WebSocket 握手使用签名机制，签名输入包含请求 `host`、`date` 和 `GET ... HTTP/1.1`，HMAC-SHA256 使用 API Secret，签名参数通过 URL 查询传递；API Key 和 Secret 不进入普通业务 JSON。
3. 首帧 JSON 包含 `header.app_id`，可选 `header.uid`；`app_id` 必须与已授权 Assistant 和 API 凭据匹配。
4. 请求业务帧包含 `parameter.chat` 和 `payload.message.text`；每条消息必须有合法 `role` 和 `content`，单轮请求至少包含一个 `user` 消息。
5. `temperature`、`top_k`、`max_tokens` 按官方范围测试；超范围必须返回稳定错误且不产生业务副作用。
6. 响应必须校验 `header.code`、`header.sid`、`header.status`、`payload.choices.status`、`seq` 和 `text`，不能只拼接收到的字符串。
7. 结束条件必须同时记录最后帧和连接关闭；最后结果应有结束状态和可追踪 `sid`，半帧、乱序、重复序号和无结束帧必须失败。
8. 一次交互结束后再开始下一次交互；并发连接、同一用户重复连接和未等待结束就发送下一问必须分别验证官方错误码和前端提示。
9. 内容审核错误 `10013`、`10014`、`10019` 必须进入安全分支；不能把审核拒绝内容伪装成正常课程回答。
10. 授权、日流控、秒级流控、并发流控和服务繁忙错误必须映射为稳定的 Adapter 错误，不得重试造成流量放大。

Spark Assistant 的最低验收 ID：

| 测试 ID | 测试方法 | 通过条件 |
|---|---|---|
| SPARK-AUTH-001 | 缺少 `TEST_APP_ID` 建立签名连接 | 连接被拒绝或返回明确授权错误，不泄露 Secret |
| SPARK-AUTH-002 | 错误 API Key/Secret | 非零错误码，不能返回正常回答 |
| SPARK-AUTH-003 | 修改签名中的 host/date/path | 握手失败，不能降级为未鉴权连接 |
| SPARK-AUTH-004 | 合法 AppID + 凭据 + assistant URL | 建立 WSS，收到可解析 JSON 响应 |
| SPARK-REQ-001 | 合法单轮 user 消息 | `header.code=0`，收到非空 assistant 内容和结束状态 |
| SPARK-REQ-002 | 缺 header.app_id | 稳定参数错误，不产生回答记录 |
| SPARK-REQ-003 | 缺 payload.message.text | 稳定 schema 错误，不产生回答记录 |
| SPARK-REQ-004 | 非法 role/content | 稳定参数错误，不执行模型请求 |
| SPARK-REQ-005 | chat 参数越界 | 返回参数错误，不建立假成功状态 |
| SPARK-RESP-001 | 多帧正常响应 | seq 可排序，文本完整，最后帧 status=2 |
| SPARK-RESP-002 | header.code 非零 | 转换为 Adapter error，不显示为正常答案 |
| SPARK-RESP-003 | 连接中断 | 状态为 failed/pending，可重试，不保存 done |
| SPARK-RESP-004 | 重复/乱序 seq | 标记协议错误，不把重复内容写入最终答案 |
| SPARK-LIMIT-001 | 同一用户并发连接 | 映射 10006/10007 或实际文档错误码，不能无限重试 |
| SPARK-LIMIT-002 | 触发授权流控 | 显示限流状态和 retryable 属性，保留 request/sid 证据 |
| SPARK-SAFE-001 | 敏感问题审核拒绝 | 映射 10013，不显示被拒绝结果 |
| SPARK-SAFE-002 | 敏感回复审核拒绝 | 映射 10014/10019，按协议停止后续交互 |

这些测试需要 `websockets`、`websocket-client` 或等价的经过审查的实现。没有第三方依赖时，可以使用只依赖 Python 标准库、经过代码审查的 RFC 6455 客户端；只有在没有可执行客户端、缺少凭据/assistant URL 或网络策略阻断时，`SPARK-*` 才能标记 `BLOCKED_INPUT` 或 `BLOCKED_DEPENDENCY`，不能把未执行标记为 PASS。

### 21.11 Spark Assistant 可复现测试方案

在 `BUILD-090` 进入真实 Agent 验收前，新增并审查 `scripts/test_spark_assistant_ws.py` 或等价测试实现。测试实现必须从 `.env.test.local`、CI Secret 或密码管理器读取凭据，禁止从命令行参数、源码常量和普通 JSON 业务帧读取 API Key/Secret。最小执行顺序如下：

1. **配置预检**：确认四个变量均存在；`TEST_API_BASE_URL` 是真实 `ws://`/`wss://`，路径符合 `/v1/assistants/{assistant_id}`，不是 `ws(s)://` 示例或 `.invalid` 占位地址；本地文件权限为 `600` 或使用等价的 Secret 管理权限。
2. **签名预检**：按官方规则解析 host/path，生成 UTC `date`，使用 API Secret 对 `host`、`date`、`GET {path} HTTP/1.1` 做 HMAC-SHA256，并将签名参数加入连接 URL；日志只能记录脱敏 host/path 和签名断言结果，不能记录签名 URL。
3. **握手断言**：建立 TLS（`wss`）并断言 WebSocket `101`；非 `101` 只记录状态码和脱敏错误类别，不保存响应正文。
4. **最小请求**：发送一条带 `header.app_id`、唯一测试 `uid`、`parameter.chat` 和 `payload.message.text` 的单轮 `user` 消息。测试问题固定、短小、无个人信息；请求正文摘要只保存 hash。
5. **逐帧解析**：逐帧解析 JSON，断言 `header.code`、非空 `header.sid`、`header.status`、`payload.choices.status`、整数 `seq` 和数组型 `payload.choices.text`。数组元素必须包含合法 `role` 与字符串 `content`；只将 `role=assistant` 的非空 content 计入回答，不打印回答原文。
6. **结束断言**：要求序号严格递增、没有重复/乱序/坏 JSON，且最后结果 `status=2`；没有结束帧、半帧或连接中断不得保存 `done`。
7. **关闭断言**：客户端发送 WebSocket close，等待对端关闭帧并记录关闭码；正常关闭码为 `1000` 或 `1001`。关闭码缺失必须标记协议风险，不得伪装为完整通过。
8. **脱敏证据**：只保留 `handshake_status`、`header_code`、`sid_present`、`frame_count`、`seq_valid`、`assistant_content_present`、`final_status`、`close_code`、退出码和环境标签；过滤 API Key、API Secret、Authorization、Cookie、完整 signed URL、完整问题和回答。

推荐的测试摘要格式如下，字段值只能是脱敏状态或数量：

```text
handshake=PASS
header_code=0
sid_present=yes
frames=3
seq_valid=yes
assistant_content_present=yes
final_status=yes
close_code=1000
close_normal=yes
```

本摘要只证明一次合法单轮链路，不等于整套 Spark 验收完成。完整通过还必须执行 `SPARK-AUTH-001` 至 `SPARK-SAFE-002` 中适用的负向、异常、限流和内容安全用例，并保存对应脱敏证据。

### 21.12 Spark Assistant 本轮实测记录与计划审查结论

2026-07-25 使用本机 `.env.test.local` 中的测试凭据，按讯飞官方 Spark Assistant WebSocket 协议完成一次严格的最小真实请求复测。随后将客户端固化为 `scripts/test_spark_assistant_ws.py` 并再次执行。两次测试均使用 Python 标准库 WebSocket 实现，未修改项目生产代码，未输出密钥、签名 URL、完整请求或回答正文。

| 验收项 | 本轮结果 | 结论边界 |
|---|---|---|
| `SPARK-AUTH-004` 合法 AppID、凭据和 assistant URL | `OBSERVED_PASS`：握手成功，`header.code=0`，`sid` 存在 | 仅证明当前凭据和地址的一次合法连接 |
| `SPARK-REQ-001` 合法单轮 user 消息 | `OBSERVED_PASS`：收到非空 `role=assistant` 内容和结束状态 | 仅证明最小请求结构可用 |
| `SPARK-RESP-001` 多帧正常响应 | `OBSERVED_PASS`：严格复测 17 帧；版本化脚本复测 3 帧；`text` 数组、`header.status`、`choices.status` 和序号均有效 | 需由后续套件继续覆盖坏帧、重复帧和断流 |
| WebSocket 关闭握手 | `OBSERVED_PASS`：关闭码 `1000` | 仅证明本次连接正常关闭 |
| 正向测试脚本 | `OBSERVED_PASS`：`scripts/test_spark_assistant_ws.py` 静态检查和真实执行均通过，当前工作树待提交 | 只覆盖合法单轮正向链路 |
| 缺凭据、错误签名、缺字段、非法参数、并发、流控和审核拒绝 | `NOT_RUN` | 不得标记 `API_PASS` 或最终 P0 通过 |

本次实测将 `SPARK-AUTH-004`、`SPARK-REQ-001` 和 `SPARK-RESP-001` 标记为 `OBSERVED_PASS`，不是完整 `API_PASS`。正向测试实现已经生成于仓库路径，但当前工作树尚未提交；在进入 `BUILD-090` 和 `BUILD-100` 的真实 Agent 通过门禁前，必须纳入版本控制，继续执行并归档负向用例、命令、commit、环境和脱敏摘要。若凭据失效、assistant 未发布、网络受限或接口版本变化，状态应降为 `BLOCKED_INPUT`、`BLOCKED_DEPENDENCY` 或 `FAIL`，不得沿用本次历史结果。

本次对计划的进一步审查结论：

- **协议边界通过**：Xingchen Workflow 的 HTTPS/SSE 与 Spark Assistant 的 WSS/JSON 流已分开，前端仍不直连凭据型上游。
- **凭据边界通过**：Spark 使用四个专用环境变量，计划、日志和证据不保存真实值；`.env.test.local` 必须继续保持未跟踪和严格权限。
- **验收边界修正**：真实单轮成功只证明正向链路，不能替代权限、异常、限流、安全和浏览器流程验收。
- **可复现性要求补强**：正向脚本已生成但尚未提交；提交前必须纳入版本控制，并补齐负向脚本和脱敏证据目录。
- **剩余阻断项**：Spark 负向/异常/限流/审核用例、Adapter 到前端 SSE 的转换、课程来源校验、三角色浏览器验收和最终恢复演练仍未因本次请求而完成。

## 22. 各功能域 API 验收矩阵

下面的测试 ID 是所有实现必须支持的验收语义。用户提供具体 API 后，将 method、path 和字段绑定到这些测试 ID；如果提供的 API 不能支持某项能力，必须把该能力列为未完成，不能删除验收项。

### 22.1 会话和角色

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| AUTH-001 | 未登录打开会话 | `401` | 不返回角色、课程数据或 HTML 登录页 |
| AUTH-002 | student 合法打开会话 | `200` | role、course scope、CSRF token、features、request ID 正确 |
| AUTH-003 | teacher 合法打开会话 | `200` | 只能返回授权课程和教师功能 |
| AUTH-004 | admin 合法打开会话 | `200` | 管理功能出现，密钥状态只能是布尔/枚举，不返回 Secret |
| AUTH-005 | 错误/过期凭据 | `401` | 不泄露鉴权实现和内部原因 |
| AUTH-006 | 写请求缺 sesskey | `403` | 数据不改变 |
| AUTH-007 | 跨 Origin 写请求 | `403` | 数据不改变 |
| AUTH-008 | 会话过期后刷新 | 受控登录状态 | 清理前端敏感状态，不重放写请求 |

### 22.2 工作台、课程和章节

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| COURSE-001 | student 获取课程列表 | `200` | 只返回本人课程，字段可渲染课程卡片 |
| COURSE-002 | 获取课程详情 | `200` | course ID、名称、教师、班级和状态一致 |
| COURSE-003 | 获取章节列表 | `200` | 章节排序稳定，测试课程章节数量与夹具一致 |
| COURSE-004 | 获取章节资源 | `200` | resource ID、类型、标题、页数和发布状态正确 |
| COURSE-005 | 访问未授权课程 | `403/404` | 不泄露课程存在性和资源标题 |
| COURSE-006 | 空课程/空章节 | `200` | 返回空数组和可解释空态，不返回 null 结构 |
| COURSE-007 | 课程切换 | `200` | 上一课程 Agent context、进度和草稿不串入当前课程 |
| COURSE-008 | 修改排序参数 | `200/400` | 只允许契约规定的排序和分页，不能注入 SQL/表达式 |

### 22.3 资源、阅读和进度

本矩阵绑定当前实现的资源进度接口：`GET/PUT /api/student/resources/{resource_id}/progress`。服务端以 `user_uid + resource_id` 隔离数据，以 `base_version` 执行乐观并发控制；`409 resource_progress_conflict` 必须要求客户端重新读取后再继续。

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| RESOURCE-001 | 打开合法资源 | `200` | 返回受控 file URL 或内容，不返回任意本地路径 |
| RESOURCE-002 | 打开其他课程资源 | `403/404` | 无内容泄露 |
| RESOURCE-003 | 打开越界页码 | `400/404` | 不重定向到其他页面，不生成来源记录 |
| RESOURCE-004 | 写入阅读进度 | `200` | percent/page 范围合法，user/resource 归属正确 |
| RESOURCE-005 | 重放进度写入 | `200` | 不产生重复事件，最终值符合版本规则 |
| RESOURCE-006 | 并发进度更新 | `409/200` | 旧版本不能覆盖新版本，冲突可恢复 |
| RESOURCE-007 | 添加页码笔记 | `201/200` | 只能访问自己的笔记，内容经过安全处理 |
| RESOURCE-008 | 收藏/取消收藏 | `200` | 重复操作幂等，刷新状态一致 |
| RESOURCE-009 | 来源回跳 | `200` | 文件、章节、页码、manifest hash 全部匹配 |

### 22.4 任务、作业、测验、考试和成绩

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| ASSESS-001 | 获取任务列表 | `200` | 状态、截止时间、尝试次数和分值正确 |
| ASSESS-002 | 获取作业详情 | `200` | 学生只能看到已发布题目和允许的辅导信息 |
| ASSESS-003 | 保存草稿 | `200` | 版本号、更新时间和答案正确，重复保存不复制记录 |
| ASSESS-004 | 草稿版本冲突 | `409` | 返回当前版本，不能覆盖其他标签页更新 |
| ASSESS-005 | 合法提交 | `201/200` | 唯一 submission ID、服务端时间和 attempt 正确 |
| ASSESS-006 | 重复提交 | `200/409` | 不产生第二个 submission ID，返回原结果或稳定冲突码 |
| ASSESS-007 | 超过尝试次数 | `409/422` | 不写入新提交，前端显示剩余次数为 0 |
| ASSESS-008 | 截止后提交 | `409/422` | 服务端拒绝，不能由修改客户端时间绕过 |
| ASSESS-009 | 客观题评分 | `200` | 分数由服务端计算，边界和总分一致 |
| ASSESS-010 | 主观题初评 | `200` | 只能生成 needs_review，不能写最终成绩 |
| ASSESS-011 | 教师复核改分 | `200` | 评分人、规则版本、原因和审计记录存在 |
| ASSESS-012 | 成绩查询 | `200` | 学生只能看到自己成绩，教师只能看到授权课程 |
| ASSESS-013 | Moodle 回写失败 | `502/503` | UI 不显示同步成功，成绩状态可重试和追踪 |
| ASSESS-014 | 考试倒计时 | `200` | 开始/结束时间由服务端决定，刷新不重置时间 |
| ASSESS-015 | 考试自动保存 | `200/409` | 多标签版本冲突可识别，不覆盖新答案 |

### 22.5 讨论、通知和互动

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| SOCIAL-001 | 获取主题列表 | `200` | 只返回课程和可见范围内主题，分页稳定 |
| SOCIAL-002 | 发布主题 | `201` | 作者为当前会话用户，不能由 body 伪造 |
| SOCIAL-003 | 回复主题 | `201` | 主题归属、作者、父主题和审核状态正确 |
| SOCIAL-004 | 恶意富文本 | `400/422` 或安全保存 | 脚本、事件属性和危险 URL 不执行 |
| SOCIAL-005 | 置顶/关闭/审核 | `200` | 只有教师/管理员可操作，产生审计记录 |
| SOCIAL-006 | 重复发帖 | `200/409` | 幂等键重放不复制主题/回复 |
| SOCIAL-007 | 通知发布 | `201` | 只发给课程范围内对象，操作者可追踪 |
| SOCIAL-008 | 通知已读 | `200` | 重复标记幂等，未读数准确 |
| SOCIAL-009 | 投票/问卷结果 | `200` | 一人/一尝试规则由服务端控制，结果不能被学生修改 |

### 22.6 教师和管理员

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| STAFF-001 | 教师题库/作业工作台列表 | `200` | 只返回授权课程范围内的题目和作业，分页/筛选稳定 |
| STAFF-002 | 创建题目和 schema 校验 | `201/422` | 题型、选项、答案、分值、章节和知识点 ID 由服务端校验 |
| STAFF-003 | 编辑草稿和版本冲突 | `200/409` | `base_version` 过期不能覆盖其他页面的修改 |
| STAFF-004 | 题目发布/撤回/归档 | `200/409` | 只允许合法状态迁移，历史引用不被删除，操作有审计 |
| STAFF-005 | 作业组卷和状态迁移 | `201/200/409` | 只能引用已发布题目，发布、撤回和归档状态可追踪 |
| STAFF-006 | 批改和成绩册 | `200/202` | 汇总值可由逐项成绩复算，学生答案和最终成绩权限隔离 |
| STAFF-007 | 知识点掌握和风险学生 | `200` | 只返回授权课程的脱敏统计，指标可由成绩数据复算 |
| STAFF-008 | 学生答案隔离 | `200` | 学生题目详情不返回答案、rubric 或教师内部字段 |
| STAFF-009 | 教师题库 → 作业 → 成绩册浏览器流程 | 页面可见且副作用正确 | Mock 与真实角色分别记录，刷新后状态不丢失 |
| STAFF-010 | 资源上传/替换/归档 | `201/200` | 文件类型、版本、发布状态、来源引用和审计正确；本地隔离实现通过时记 `OBSERVED_PASS`，正式 Moodle/pluginfile 未验收时保留环境限定 |
| ADMIN-001 | 服务状态 | `200` | 只返回 status、版本、配置布尔值和脱敏错误 |
| ADMIN-002 | 创建知识库版本 | `201` | version、workflow binding、manifest hash 正确 |
| ADMIN-003 | 上传文件 | `201/200` | 类型、大小、内容、来源和重复校验正确 |
| ADMIN-004 | 知识库命中测试 | `200` | 固定问题、答案、来源和版本可追溯 |
| ADMIN-005 | 发布/回滚知识库 | `200` | 未发布版本不可被学生使用，回滚可复验 |
| ADMIN-006 | 查看审计 | `200` | 只允许管理员，字段脱敏、不可篡改 |
| ADMIN-007 | 备份/恢复检查 | `200/202` | 任务状态、日志、校验和和结果可追踪 |

### 22.7 Agent 和流式 API

| 测试 ID | 请求 | 预期 | 关键断言 |
|---|---|---|---|
| AGENT-001 | 课程问答 | SSE/`200` | token、source、done 顺序正确，答案非空 |
| AGENT-002 | 资料不足问题 | SSE/`200` | 明确资料不足，不伪造文件、页码或文献 |
| AGENT-003 | Prompt Injection | `422/200` | 不绕过课程边界、不泄露系统提示和凭据 |
| AGENT-004 | 学习诊断 | SSE/`200` | profile 由服务端加载，推荐 ID 真实存在 |
| AGENT-005 | 教师出题 | SSE/`200` | 结构化题目需教师确认，学生不能调用 |
| AGENT-006 | 主观题初评 | `200` | 返回 needs_review，不能直接变更最终成绩 |
| AGENT-007 | 情景开始/轮次/结束 | `201/200` | session、turn、幂等、来源和摘要状态一致 |
| AGENT-008 | 上游超时/断流 | `502/504` 或 error event | 不保存假完成结果，pending 状态可重试 |
| AGENT-009 | 非法来源标记 | `200` | source 被丢弃或标记 unverified，不能成为可核验证据 |
| AGENT-010 | 跨课程会话 | `403/404` | 不允许读取或写入其他课程上下文 |

## 23. API 验收与构建批次的绑定关系

每个构建批次必须执行对应 API 集合；没有对应 API 的功能必须标记 `NOT_IMPLEMENTED`，不得用静态页面通过代替：

| 构建批次 | 必测 API 集合 | 批次完成条件 |
|---|---|---|
| BUILD-000 | AUTH、现有健康检查、现有写接口重复请求 | 当前基线行为有证据，已知缺口登记 |
| BUILD-010 | 静态资源、前端健康、API 错误包络 | 新前端可构建、可部署、可回退 |
| BUILD-020 | AUTH-001～008 | 四种身份和会话失效全部通过 |
| BUILD-030 | COURSE-001～008、工作台查询 | 课程数据来自 API，权限和刷新一致 |
| BUILD-040 | RESOURCE-001～009 | 资源、页码、来源、进度和笔记闭环通过 |
| BUILD-050 | ASSESS-001～015 | 草稿、提交、评分、考试和成绩一致性通过 |
| BUILD-060 | SOCIAL-001～009 | 讨论、通知和互动权限/XSS/幂等通过 |
| BUILD-070 | STAFF-001～008 + T4 的 STAFF-009 + STAFF-010 资源编辑 | 教师题库、作业发布、批改、成绩册和资源编辑的适用测试全部完成并明确环境状态，正式角色和 pluginfile 门禁仍必须通过 |
| BUILD-080 | ADMIN-001～007 | 知识库、审计、备份和恢复门禁通过 |
| BUILD-090 | AGENT-001～010 | Mock 与真实 Workflow 分离，来源和上下文通过 |
| BUILD-100 | 全部 API 集合 + 真实环境冒烟 | P0/P1、真实角色、HTTPS、恢复和材料全部通过 |

每个批次的 `manual-acceptance.md` 必须列出本批次所有测试 ID，并为每个 ID 填写统一状态：`PASS`、`OBSERVED_PASS`、`CONDITIONAL`、`REVIEW_REQUIRED`、`BLOCKED_INPUT`、`BLOCKED_DEPENDENCY`、`BLOCKED_EXTERNAL`、`NOT_RUN`、`NOT_IMPLEMENTED` 或 `FAIL`。只有全部为 `PASS` 才能进入下一批次；其余状态都必须保留阻断原因和后续动作。

## 24. API 测试执行记录模板

把用户提供的测试 API 绑定到本模板，不把真实凭据写入文件：

```markdown
# API 验收记录

## 1. 环境

- API manifest 版本：
- OpenAPI 版本：
- 测试环境名称：
- BASE_URL 环境变量名：TEST_API_BASE_URL
- Git commit：
- 数据库 schema 版本：
- 测试 namespace：
- Mock 鉴权：true/false
- Mock Workflow：true/false

## 2. 凭据检查

- [ ] 凭据已轮换且未出现在截图/日志/仓库
- [ ] 使用专用测试角色
- [ ] Token/Cookie 通过 Secret Manager 或未跟踪环境变量注入
- [ ] 输出脱敏检查通过

## 3. 单接口记录

- 测试 ID：
- 角色：anonymous/student/teacher/admin
- Method：
- Path 模板：
- Request ID：
- Idempotency-Key：
- 前置夹具：
- 请求 body hash：
- 预期状态码：
- 实际状态码：
- 预期 Content-Type：
- 实际 Content-Type：
- JSONPath 断言：
- 数据副作用断言：
- 审计断言：
- 清理结果：
- 结果：PASS/FAIL/BLOCKED/NOT_IMPLEMENTED

## 4. 负向和安全记录

| 场景 | 预期状态码 | 实际状态码 | 数据是否改变 | 结果 |
|---|---:|---:|---|---|
| 未登录 | | | 否 | |
| 错误凭据 | | | 否 | |
| 越权课程 | | | 否 | |
| 越权对象 | | | 否 | |
| 超长/非法参数 | | | 否 | |
| 重复请求 | | | 不重复 | |
| 并发请求 | | | 至多一次 | |
| 上游失败 | | | 无假成功 | |
```

## 25. 本次审核结论和修订要求

对当前 V2 的重新审核结论：

1. 原计划的产品范围、路由规划、数据模型、分阶段建设和安全边界保留。
2. 所有阶段时间估算已删除，阶段完成改为质量门禁完成。
3. 新增用户测试 API 接入规范，明确 API 文档、角色、夹具、重置和流式协议要求。
4. 新增凭据安全硬门禁，截图中暴露的 API Secret/API Key 不得继续使用，必须轮换。
5. 新增逐接口测试顺序、成功/失败响应断言、字段类型测试、权限测试、幂等测试、并发测试、状态机测试、持久化测试和审计测试。
6. 新增学生、教师、管理员、资源、作业、讨论、知识库和 Agent 的 API 验收矩阵。
7. 新增 API 测试 ID 与 `BUILD-000`～`BUILD-100` 的绑定规则。
8. 新增 API 验收记录模板，要求每个接口保留脱敏请求摘要、响应摘要、断言结果、副作用和清理结果。
9. “页面能打开”“Mock 返回内容”“手工点击成功”不再单独构成功能通过证据。
10. 用户提供具体测试 API 后，必须先填写 `api-test-manifest.yaml`，再执行实际接口测试；未绑定接口不得标记 PASS。

本计划现在以以下关系作为最终验收原则：

```text
产品功能
  -> API 契约
      -> 正向/负向/权限/幂等/并发/状态/持久化测试
          -> 浏览器三角色流程
              -> 安全、性能、恢复和证据审查
                  -> 构建批次通过
```

## 26. 2026-07-25 执行一致性审查（历史快照）

本次审查同时对照本计划、`PROJECT_PROGRESS.yaml`、当前前端 `package.json`、Caddy 路由、验收脚本和工作区文件状态。审查目标是确认“计划中的测试可以执行、执行结果不会被误读、门禁与实际实现一致”。

### 26.1 测试结果状态定义

后续计划和进度文件统一使用以下语义：

| 状态 | 含义 | 是否可以关闭构建批次 |
|---|---|---|
| `PASS` | 范围内测试已执行，断言和证据完整，且没有未处理阻断项 | 可以，前提是本批次其他项目也为 `PASS` |
| `OBSERVED_PASS` | 单次正向观察或局部测试通过，尚未覆盖该测试 ID 的适用负向/权限/恢复场景 | 不可以 |
| `PASS_WITH_ENV_BLOCKER` | 只证明配置/静态结构可解析，运行环境仍不完整 | 不可以 |
| `CONDITIONAL` | 实现或局部测试成立，但存在限定范围的 P2 或明确环境前置条件 | 不可以 |
| `REVIEW_REQUIRED` | 结果存在安全、依赖或设计风险，尚未完成审查闭环 | 不可以 |
| `BLOCKED_INPUT` | 缺少课程文件、测试账号、API 文档、固定夹具或外部配置 | 不可以 |
| `BLOCKED_DEPENDENCY` | 缺少可执行依赖、基础镜像、服务或网络能力 | 不可以 |
| `BLOCKED_EXTERNAL` | 真实 Workflow、正式域名、外部服务或授权环境尚未具备 | 不可以 |
| `NOT_RUN` / `NOT_IMPLEMENTED` | 尚未执行或尚未实现 | 不可以 |
| `FAIL` | 断言失败、权限错误、数据不一致或出现安全问题 | 不可以，必须修复并重验收 |

只有本批次范围内所有必测项为 `PASS`，且代码审查、人工验收、证据归档和回退检查全部完成，才允许把批次标记为 `PASS`。历史结果、Mock 结果和单次真实冒烟只能作为证据，不能自动升级为批次通过。

### 26.2 本轮发现和处理

| ID | 严重度 | 发现 | 处理结论 |
|---|---|---|---|
| `PLAN-ROUTE-001` | P1 | 计划部分位置写成 `/legacy-agent/`，实际 Caddy、README 和进度文件使用 `/agent/` | 已统一为 `/agent/`；关闭 |
| `PLAN-TEST-001` | P1 | 统一命令清单要求 `npm run test:a11y`，此前 `frontend/package.json` 没有该脚本 | 历史快照曾记录 2/2，随后 stale server 复测为 1/3；第 51 节已通过隔离端口复测 3/3，正式 axe 等价审查、真实角色和六视口证据仍是开放门禁 |
| `PLAN-STATE-001` | P0 | `OBSERVED_PASS`、`PASS_WITH_ENV_BLOCKER` 和正式 `PASS` 的边界此前未集中定义，可能造成误报 | 已加入状态定义；只有完整 `PASS` 才能关闭批次 |
| `PLAN-EVIDENCE-001` | P1 | `acceptance/frontend/BUILD-040/` 已建立并包含隔离测试证据，但根目录 `api-test-manifest.yaml` 和 `openapi.test.json` 尚未提供 | BUILD-040 的局部证据可保留；真实 API/浏览器批次启动前必须补齐 API 清单和契约，缺失期间标记 `BLOCKED_INPUT`，不创建伪造证据 |
| `PLAN-TEST-002` | P1 | 原有章节分别描述测试类型和批次门禁，但没有统一规定每次构建后的执行顺序、重测范围和证据闭环 | 已在第 27 节加入固定测试协议；后续批次必须按该协议执行，关闭 |
| `DATA-INPUT-001` | P0 | manifest 要求的 20 个 PDF 当前缺失，BUILD-000 课程数据校验 fail-fast | 保持 `BLOCKED_INPUT`；不得生成占位 PDF、篡改 manifest 或 hash |
| `FRONTEND-AUDIT-001` | P1 | 历史快照中的 `react-router-dom` 审计有 2 个 RSC/SSR 相关 high advisory | 已在后续依赖迁移中移除 `react-router-dom`，完成 Router 8/ESLint 10 回归和在线审计 0；当前状态以第 50 节为准 |

### 26.3 审查后的执行门禁

1. BUILD-000 仍是当前唯一正式前置门禁；课程 PDF、课程 manifest 校验和完整 local acceptance 未恢复前，BUILD-010/020/030 只能保留数据无关的实现和 Mock 证据，不能切换生产路由。
2. BUILD-010 在正式 axe 等价审查、容器构建和依赖审计结论完成前，状态只能是 `IMPLEMENTED_PENDING_GATE`，不能写成 `PASS`；本地自定义 `test:a11y` 只能记为 `OBSERVED_PASS`。
3. Spark Assistant 当前已有合法单轮正向和四类参数负向 `OBSERVED_PASS`；错误签名、异常、限流、并发和审核测试完成前，不得写成 `API_PASS` 或 BUILD-090 通过。
4. 每次测试必须记录命令、退出码、commit、环境模式、测试 ID、脱敏摘要和证据路径；没有证据路径的结果只能记为 `NOT_RUN`。
5. 任何计划与实现不一致时，先更新计划和进度状态，再决定是否修改代码；不得通过放宽断言或打开 Mock 消除阻断。

本轮审查结论：计划的测试覆盖和构建门禁已形成闭环，当前项目仍处于 `BUILD-000 = BLOCKED_INPUT`、`BUILD-010 = IMPLEMENTED_PENDING_GATE`，最终发布继续保持阻断状态。

## 27. 2026-07-25 测试方案落地与构建后复审协议

本节是每次构建之后必须执行的操作规程。第 10 节描述测试范围，第 18 节描述各批次功能门禁；本节规定实际执行顺序、结果判定、重测规则和证据格式。没有本节要求的证据，测试即使在本地执行成功，也只能记为 `OBSERVED_PASS`，不能关闭构建批次。

### 27.1 测试分层和适用范围

每个 BUILD 批次必须为下表每一层填写结果。某层确实不适用时必须在 `review.md` 说明原因和替代证据；把测试删掉、跳过或只运行 Mock 不得记为 `PASS`。

| 层级 | 测试内容 | 最低输出 | 批次门禁要求 |
|---|---|---|---|
| T0 | 需求、范围、数据归属、权限、迁移和回退审查 | `scope.md`、`review.md` | 没有未处理 P0/P1 |
| T1 | Shell/Python/TypeScript 语法、lint、typecheck、构建和差异检查 | 命令、退出码、摘要 | 所有适用命令退出码为 0 |
| T2 | 单元和组件测试 | 测试数量、失败数、覆盖的测试 ID | 业务规则、状态机和错误态不能缺测 |
| T3 | API 契约、集成、数据库和文件存储测试 | 脱敏请求/响应摘要、JSON 断言、副作用检查 | 正向、负向、权限、幂等、并发、持久化和审计全部适用通过 |
| T4 | Playwright 浏览器流程 | URL、可见状态、角色、视口、截图/视频 | Mock 与真实环境分开；三角色适用流程不能混记 |
| T5 | 安全、可访问性、性能和恢复测试 | 风险结论、指标、恢复日志 | P0/P1 风险清零；未实现项为阻断 |
| T6 | 证据、回退和最终门禁复审 | `manual-acceptance.md`、`rollback.md`、状态更新 | 只有所有必测 ID 为 `PASS` 才能关闭 |

### 27.2 每次构建后的固定执行顺序

构建完成后按以下顺序执行；修复缺陷后必须从受影响的步骤重新开始，并补跑本批次全量回归：

1. **冻结版本和范围**：记录 `git status --short --branch`、`git rev-parse HEAD`、构建编号、环境、Mock 开关、数据库 schema 和 API 契约版本；确认改动仍在 `scope.md` 范围内。
2. **审查代码差异**：检查数据权威来源、对象归属、角色权限、CSRF、幂等、输入校验、输出清洗、日志脱敏、迁移和回退；发现未审查的跨模块功能时暂停批次。
3. **执行静态门禁**：运行 `git diff --check`、`bash -n scripts/*.sh`、`python3 -m compileall -q agent-adapter scripts`、前端 lint、typecheck、依赖审计和生产构建；命令不存在或脚本未实现必须记为 `NOT_IMPLEMENTED`，不能记为成功。
4. **执行局部自动化测试**：先运行变更模块的单元/组件测试，再运行共享 API、Store、数据库、Adapter 和文件夹具测试；记录测试 ID、数量、失败信息和退出码。
5. **执行 API 测试**：先验证 `openapi.test.json` 与 `api-test-manifest.yaml`，再按第 21.5 节执行连通性、未登录、错误鉴权、成功、边界、越权、重复、并发、状态迁移、持久化、错误恢复、审计和清理。缺少 API 文档、角色或重置夹具时，整批真实 API 验收为 `BLOCKED_INPUT`。
6. **执行浏览器测试**：先执行本地/Mock 流程，再执行真实环境流程；覆盖刷新、前进/后退、重复点击、断网恢复、会话过期和移动视口。Mock 通过不能覆盖真实角色结果。
7. **执行质量测试**：执行适用的 axe 等价/键盘可访问性、六视口视觉检查、性能基线、上游超时/断流、数据库/服务重启和备份恢复检查。只有本地自定义 `test:a11y` 时，结果最多记为 `OBSERVED_PASS`；正式 axe 等价审查、真实角色和六视口证据缺失时必须保留阻断。
8. **归档和复审**：把命令、退出码、测试 ID、脱敏摘要、截图/视频、浏览器视口、commit 和剩余风险写入 `acceptance/frontend/BUILD-xxx/`；复核人根据 27.5 判定 `PASS`、`CONDITIONAL`、`BLOCKED_INPUT`、`REVIEW_REQUIRED` 或 `FAIL`，同步 `PROJECT_PROGRESS.yaml` 和 `PROJECT_STATUS.md`。

账本校验器的 Python 单元回归从仓库根目录统一使用模块入口：`python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract`。直接执行 `python3 scripts/test_validate_project_progress.py` 或 `python3 scripts/test_refresh_progress_snapshot.py` 不是权威命令，因为测试文件导入 `scripts.*` 包；若误用直接入口，必须记录为 `PLAN_COMMAND_FAILURE`，改用模块入口后重新执行并归档退出码。

禁止事项：不得通过修改测试数据让失败消失、关闭权限校验、把真实请求改为 Mock、手工改库后截图、删除失败日志、打印凭据或把历史结果当作当前构建结果。

### 27.3 每个 API/业务写操作的强制测试集合

每个新增或修改的接口至少绑定一个稳定测试 ID，并按适用性执行以下集合。适用性判断必须由 `api-test-manifest.yaml` 记录，不能由测试脚本静默跳过。

| 测试组 | 最低场景 | 通过条件 |
|---|---|---|
| 正向 | 合法角色、合法对象、最小和典型 payload | 状态码、Content-Type、包络、字段类型和业务结果正确 |
| 鉴权 | 未登录、错误/过期凭据、CSRF 缺失或错误 | 返回约定的 `401/403/419`，不泄露数据，不产生副作用 |
| 对象权限 | 跨用户、跨课程、跨角色、篡改 URL/ID | 返回 `403/404`，不泄露对象存在性或内部路径 |
| 输入边界 | 缺失、null、空串、超长、非法枚举、Unicode、越界数字和非法文件 | 返回稳定 `400/422`，不落库、不发送上游请求 |
| 幂等和并发 | 相同 `Idempotency-Key` 重放、并发写入、多标签页版本冲突 | 业务记录至多创建一次，冲突可识别，最新数据不被覆盖 |
| 状态和持久化 | 草稿/发布/提交/批改/回滚等合法和非法迁移，成功后重新 GET/刷新/重新登录 | 状态只按定义迁移，归属、版本、时间和结果一致 |
| 上游和恢复 | 超时、断流、`401/429/5xx`、服务重启、数据库错误 | UI 不显示假成功，错误可重试，未完成操作不伪造 `done` |
| 审计和清理 | 管理、成绩、发布、删除、回滚和恢复操作 | request ID、操作者、对象、结果可追溯；只清理测试 namespace |

### 27.4 浏览器和人工验收的最低记录

每个适用角色至少记录一条完整主流程和一条失败/恢复流程。记录必须包含：

- 角色、测试账号引用、课程/对象夹具 ID（不得记录密码、Token 或真实个人信息）。
- 起始 URL、关键 URL、浏览器和视口、执行环境及 Mock 开关。
- 页面可见结果、按钮状态、错误码/request ID 和实际副作用。
- 关键步骤截图；涉及流式、上传、恢复或移动端布局时才保存必要视频。
- 真实数据、Mock 数据、真实 Workflow 和测试 Workflow 分开归档，文件名带环境标签。

最低人工场景：学生完成资源阅读/进度保存或作业提交；教师执行发布/批改；管理员执行状态查看/知识库或恢复操作；未登录用户执行受保护访问；每类场景都要覆盖刷新或失败恢复。尚未实现的功能必须写 `NOT_IMPLEMENTED`，不能用静态页面截图替代。

### 27.5 门禁状态和复审判定

统一状态含义如下：

| 状态 | 判定 | 是否关闭批次 |
|---|---|---|
| `PASS` | 所有适用测试 ID、代码审查、人工验收、证据和回退检查均通过 | 是 |
| `CONDITIONAL` | 实现和局部测试成立，但有明确输入/环境阻断或允许跟踪的 P2 | 否 |
| `OBSERVED_PASS` | 单次正向观察、Mock 结果或局部测试通过 | 否 |
| `PASS_WITH_ENV_BLOCKER` | 静态配置或结构检查通过，但运行环境未完整建立 | 否 |
| `REVIEW_REQUIRED` | 存在安全、依赖、契约或证据风险，尚未完成复核 | 否 |
| `BLOCKED_INPUT` / `BLOCKED_DEPENDENCY` | 缺少课程文件、账号、API 契约、夹具、服务或基础镜像 | 否 |
| `BLOCKED_EXTERNAL` | 真实 Workflow、正式域名或外部授权环境尚未具备 | 否 |
| `NOT_RUN` / `NOT_IMPLEMENTED` | 尚未执行或能力尚未实现 | 否 |
| `FAIL` | 断言失败、越权、数据不一致、泄密或不可恢复错误 | 否，修复后重测 |

`CONDITIONAL` 只表示“保留当前实现并等待明确输入”，不表示可以进入下一批次；只有 `PASS` 可以关闭批次。P0/P1 缺陷、权限失败、凭据泄露、重复写入、来源伪造、成绩不一致或备份恢复失败不得记为 `CONDITIONAL`。

### 27.6 本轮计划审查后的实际状态

截至 2026-07-25，本计划和工作区对应关系如下：

- `BUILD-040` 已有 `acceptance/frontend/BUILD-040/`，Store、资源进度 API、Mock 浏览器和响应式测试有隔离证据；真实 PDF 首屏、Moodle 文件权限和真实学生进度仍为 `BLOCKED_INPUT`。
- `BUILD-000` 因 manifest 要求的 20 个 PDF 缺失保持 `BLOCKED_INPUT`；不得生成占位 PDF、修改 manifest 或伪造 hash/page_count。
- `BUILD-010` 的 lint、typecheck、单元、组件、构建和 Mock 浏览器结果不能关闭批次；当前本地自定义 `test:a11y` 仅为 `OBSERVED_PASS`，正式可访问性证据仍需补齐，容器构建受基础镜像影响、依赖审计仍需复核。
- `BUILD-050` 已完成本地作业/草稿/提交/批改实现，Store 7/7、草稿 API、评测 API、前端 7 个单元测试、2 个组件测试、5 条 Mock 浏览器流程和标准响应式流程通过；截止边界独立用例、真实 Moodle 回写、真实角色和多标签浏览器验收仍未关闭。
- 真实 API 验收所需的 `api-test-manifest.yaml` 和 `openapi.test.json` 尚未提供；在这两个文件和测试角色/夹具就绪前，真实 API 批次不得启动。
- Spark Assistant 已有合法单轮正向和四类参数负向 `OBSERVED_PASS`；错误签名、异常、限流、并发和内容审核用例未完成前，不得标记 `API_PASS` 或 BUILD-090 通过。

本轮审查结论（BUILD-070 实现前快照）：测试方案已写入计划并形成“构建后审查 → 分层测试 → 浏览器验收 → 安全/恢复 → 证据归档 → 门禁判定”的闭环；当时正式状态为 `BUILD-000 = BLOCKED_INPUT`、`BUILD-040 = IMPLEMENTED_PENDING_GATE`、`BUILD-050 = IMPLEMENTED_PENDING_GATE`、`BUILD-060 = IMPLEMENTED_PENDING_GATE`，最终发布 `blocked`。BUILD-070 的最新状态以第 31、32 节为准。

## 28. 2026-07-25 BUILD-060 执行复审与状态校正

本节是对 BUILD-060 实现后的第二轮审查，优先核对计划、代码、测试命令、证据目录和 `PROJECT_PROGRESS.yaml` 是否相互一致。它不替代第 27 节的通用流程；后续 BUILD 批次必须复制同样的核对方式。

### 28.1 已完成并有证据的范围

| 范围 | 当前结果 | 证据 |
|---|---|---|
| 讨论主题列表、搜索、详情和纯文本回复 | 已实现 | `frontend/src/App.tsx`、`scripts/test_social_api.py`、Mock 浏览器 |
| 讨论置顶、解决、关闭和教师权限 | 已实现 | `agent-adapter/app/main.py`、审计断言、Mock 浏览器 |
| 讨论/回复重复提交幂等 | 已实现 | `SOCIAL-002/003/006` API 断言、客户端请求头单元测试 |
| XSS/危险内容拒绝 | 已实现 | `SOCIAL-004` 脚本和事件属性拒绝断言 |
| 课程通知发布 | 已实现 | 教师工作台通知表单、`SOCIAL-007` API 和浏览器流程 |
| 学生消息列表和已读持久化 | 已实现 | `SOCIAL-008` API、刷新后的浏览器断言 |
| 客户端 DTO、安全请求头 | 已实现 | 9 个客户端/领域单元测试 |

### 28.2 本轮复审结果

| ID | 严重度 | 发现 | 状态和处理 |
|---|---|---|---|
| `BUILD060-STATE-001` | P1 | BUILD-060 在进度文件中仍是 `NOT_STARTED`，与已实现代码和测试不一致 | 已校正为 `IMPLEMENTED_PENDING_GATE`，保留真实环境和未实现活动阻断 |
| `BUILD060-TEST-001` | P1 | 本地总验收脚本没有绑定社会互动 API 测试 | 已加入 `scripts/test_social_api.py`；完整脚本仍受缺失课程 PDF fail-fast 阻断 |
| `BUILD060-UI-001` | P1 | 计划要求教师发布通知，但教师页原先只有占位工具卡 | 已增加教师通知发布表单，并通过 7 条 Mock 浏览器流程 |
| `BUILD060-SCOPE-001` | P1 | `SOCIAL-009` 投票/问卷结果页尚未实现，不能把 BUILD-060 写成完整通过 | 保持 `NOT_IMPLEMENTED`；纳入下一互动批次或明确缩小本批次范围后再审查 |
| `BUILD060-REAL-001` | P0 | 真实 Moodle 角色、正式 API 契约、正式课程数据和审计环境未具备 | 保持 `BLOCKED_INPUT`，Mock 结果不得升级为真实 PASS |
| `BUILD060-A11Y-001` | P1 | 该历史快照中的 `npm run test:a11y` 尚未实现 | 历史记录；当前自定义检查已在后续复审中达到 `OBSERVED_PASS_2_TESTS`，正式可访问性门禁仍阻断 |

### 28.3 本批次实际测试记录

执行过的确定性检查：

```bash
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_social_api.py
python3 scripts/test_api_contract.py
npm run lint
npm run typecheck
npm run test:unit -- --run
npm run test:component -- --run
npm run build
npm run test:e2e:mock -- --workers=1
npm run test:e2e -- --workers=1
```

结果为：`SOCIAL_API_OK`、`API_CONTRACT_OK routes=57`、客户端/领域单元测试 9/9、组件测试 2/2、Mock 浏览器 7/7、标准响应式浏览器 1/1、lint/typecheck/build 全部退出码 0。浏览器测试使用 Mock Adapter 和本地 Vite，不能证明真实 Moodle 或真实 Workflow。

### 28.4 BUILD-060 门禁判定

当前判定为 `IMPLEMENTED_PENDING_GATE`，不是 `PASS`。原因如下：

- `SOCIAL-009` 投票/问卷结果页为 `NOT_IMPLEMENTED`。
- `api-test-manifest.yaml`、`openapi.test.json` 和真实角色夹具仍缺失。
- `BUILD-000` 因 manifest 要求的 20 个 PDF 缺失而保持 `BLOCKED_INPUT`。
- 真实 Moodle 会话、通知审计、正式 HTTPS、六视口截图和可访问性自动化尚未完成。

只有补齐 SOCIAL-009 或经审查将其移出本批次范围，并完成 T0-T6、真实角色和证据复审后，BUILD-060 才能关闭。当前不得创建“全部功能已完成”或“真实学习通功能已验收”的结论。

## 29. 2026-07-25 BUILD-060 SOCIAL-009 完成复审

在第 28 节复审后，已实现投票/问卷活动闭环并重新执行受影响的测试层。第 28 节中的“尚未实现”结论属于变更前历史记录；本节是当前状态的权威复审结果。

### 29.1 实现范围

- SQLite 新增 `activities` 和 `activity_responses` 表，使用 additive migration。
- 提供 `GET /api/activities`、`GET /api/activities/{activity_id}`、`GET /api/activities/{activity_id}/results`。
- 提供 `POST /api/activities/{activity_id}/responses`，服务端校验活动状态、选项、答案数量、尝试次数和重复作答。
- 提供 `POST /api/teacher/activities`，教师/管理员可以创建草稿或已发布的投票/问卷，写入审计记录。
- 前端新增 `/activities` 和 `/activities/:activityId`，支持投票、问卷、提交成功、结果汇总、刷新恢复、加载和错误状态。

### 29.2 当前测试结果

```text
ACTIVITY_API_OK
API_CONTRACT_OK routes=62
frontend unit: 11 passed
frontend component: 2 passed
frontend Mock Playwright: 8 passed
frontend responsive Playwright: 1 passed at 1440px and 390px
lint/typecheck/build: PASS
```

活动 API 断言覆盖：未授权角色、教师创建权限、投票单选、问卷多选、非法选项、重复选项、重复提交、幂等重放、结果计数、结果比例和审计记录。浏览器断言覆盖学生提交投票、查看结果和刷新后保持“已提交”。

### 29.3 当前门禁结论

`SOCIAL-009` 当前为 `PASS`，但 `BUILD-060` 仍为 `IMPLEMENTED_PENDING_GATE`，因为完整构建门禁还需要真实 Moodle 角色、正式 API 测试清单、课程 PDF、真实审计环境、可访问性自动化和 T0-T6 证据复审。不得把 SOCIAL-009 的隔离测试结果升级为整个 BUILD-060 或最终发布通过。

## 30. 2026-07-25 测试方案再次审查与当前复测校正

本节是第 27 节测试协议和第 29 节 SOCIAL-009 复审之后的最新执行记录。第 29 节保留已归档的 8/8 Mock 浏览器结果；本节负责说明本轮重新执行的结果、环境限制和当前门禁，不覆盖历史证据。

### 30.1 本轮已复测项目

以下命令在当前工作区执行并退出码为 0：

```text
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_activity_api.py
python3 scripts/test_api_contract.py
python3 scripts/test_ui_contract.py
npm run lint
npm run typecheck
npm run test:unit -- --run
npm run test:component -- --run
npm run build
git diff --check
bash -n scripts/*.sh
python3 -m compileall -q agent-adapter scripts
```

结果摘要：`ACTIVITY_API_OK`、`API_CONTRACT_OK routes=62`、`UI_CONTRACT_OK`、单元测试 11/11、组件测试 2/2、lint、typecheck、build、Shell 语法、Python 编译和差异检查均通过。该结果只覆盖可在当前环境运行的隔离层，不能替代真实角色、真实课程资料或真实 HTTPS 验收。

### 30.2 当前未通过或未完成的复测

| 项目 | 当前结果 | 判定和后续动作 |
|---|---|---|
| `npm run test:a11y` | 历史快照曾为 `NOT_IMPLEMENTED`；当前为自定义检查 `OBSERVED_PASS_2_TESTS` | BUILD-010/100 的正式可访问性门禁保持阻断；补齐 axe 等价、真实角色和六视口证据后重测 |
| `npm run test:e2e:mock -- --workers=1` | `BLOCKED_ENVIRONMENT` | Playwright 的 webServer 检查 `127.0.0.1:8082` 返回 `connect EPERM`；需在允许本地回环端口的环境重跑，不能将本轮记为 PASS |
| `npm run test:e2e -- --workers=1` | `NOT_RUN` | Mock webServer 环境阻断未解除前，不宣称标准浏览器流程通过 |
| `RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh` | `BLOCKED_INPUT` | 课程 manifest 要求的 20 个 PDF 缺失，脚本按设计 fail-fast；不得生成占位 PDF 或修改 hash/page_count |
| 真实 API/三角色浏览器 | `BLOCKED_INPUT` | `api-test-manifest.yaml`、`openapi.test.json`、角色和可重置夹具仍未提供 |

历史 `frontend Mock Playwright: 8/8` 和 `responsive: 1/1` 仍可作为 `OBSERVED_PASS` 的隔离证据，但在本轮回环端口阻断解除并重新归档前，不得升级为当前 `PASS`。

### 30.3 复审后的计划门禁

- 测试方案已经覆盖 T0-T6、固定执行顺序、强制 API 测试集合、浏览器记录、重测规则、证据格式和状态定义，计划层面评估为 `DOCUMENTED_AND_REVIEWED`。
- 当前 `BUILD-060` 仍为 `IMPLEMENTED_PENDING_GATE`；`SOCIAL-009` 仅为隔离 API/Mock 范围 `PASS`。
- 该历史复测快照中的可访问性自动化为 `NOT_IMPLEMENTED`；当前已由自定义检查 `OBSERVED_PASS_2_TESTS` 取代，但真实角色验收、正式可访问性和本轮 Mock 浏览器复测阻断仍保持，最终发布继续 `blocked`。
- 任何修复或环境变化后，必须从受影响测试层重新执行，并补跑本批次全量回归；不得用第 29 节历史结果替代本轮证据。

### 30.4 下一次构建前置条件

1. 在允许本地回环端口和浏览器 webServer 检查的环境重跑 Mock 与标准 Playwright，并保存退出码、视口和截图证据。
2. 保留 `npm run test:a11y` 的本地回归，补齐正式 axe 等价审查、真实角色、六视口和错误恢复证据。
3. 提供脱敏的 `api-test-manifest.yaml`、`openapi.test.json`、student/teacher/admin 测试角色和可重置 namespace。
4. 恢复与 manifest 的 hash/page_count 一致的 20 个 PDF，执行 `verify_course_data.py` 后再重跑完整本地验收。
5. 完成 T0-T6 证据复审并同步 `PROJECT_PROGRESS.yaml`、`PROJECT_STATUS.md` 和对应 BUILD 目录；在此之前不得关闭 BUILD-060 或进入正式发布。

## 31. 2026-07-25 BUILD-070 教师工作台实现与复审

本节记录 BUILD-070 的当前实现和本地验收结果，并沿用第 27 节的 T0-T6 门禁。它不把教师端 Mock 流程或隔离 API 结果升级为真实 Moodle 通过。

### 31.1 实现范围

- 新增教师题库列表和状态筛选，支持题目创建、草稿编辑、`base_version` 乐观冲突和教师确认后发布。
- 服务端校验单选、多选、判断、简答和论述题的选项、答案、rubric、分值、章节 ID 和知识点 ID。
- 新增题目和作业的发布、撤回、归档状态迁移；状态迁移、创建、批改和教师复核均写入审计。
- 新增教师作业列表和组卷发布页面，发布前只能引用已发布题目。
- 新增成绩册聚合 API 和页面，展示提交/批改数量、平均成绩、知识点掌握和风险学生。
- 前端新增 `/teacher/questions`、`/teacher/assignments` 和 `/teacher/gradebook`，教师工作台入口不再使用创建内容和管理全部占位弹窗。

### 31.2 当前测试结果

```text
TEACHER_WORKBENCH_API_OK
ASSESSMENT_API_OK
API_CONTRACT_OK routes=68
frontend lint: PASS
frontend typecheck: PASS
frontend unit: 14 passed
frontend component: 2 passed
frontend build: PASS
frontend Mock Playwright: 9 passed
frontend responsive Playwright: 1 passed at 1440px and 390px
```

API 测试覆盖：教师/管理员权限、学生越权、题目幂等创建、草稿版本冲突、答案和评分标准隔离、题目/作业发布撤回归档、批改、成绩册汇总、知识点统计和风险学生。浏览器测试覆盖教师创建题目 → 发布题目 → 创建作业 → 发布作业 → 打开成绩册。

### 31.3 复审发现和处理

| ID | 严重度 | 发现 | 处理 |
|---|---|---|---|
| `BUILD070-API-001` | P1 | 原有题目和作业 API 已存在，但没有教师题库/作业列表和成绩册聚合入口 | 已新增教师列表、成绩册和状态迁移 API，并绑定 STAFF 测试 |
| `BUILD070-STATE-001` | P1 | 原有发布方法可把已归档题目重新发布，状态机不完整 | 已改为显式 draft/published/withdrawn/archived 合法迁移，已归档发布返回冲突 |
| `BUILD070-AUDIT-001` | P1 | 题目/作业创建和部分评分操作缺少统一审计证据 | 已为创建、发布、撤回、归档、批改和复核写入 `audit_log` |
| `BUILD070-UI-001` | P1 | 教师页“创建内容”和“管理全部”是占位交互 | 已替换为题库、作业发布和成绩册真实路由 |
| `BUILD070-REAL-001` | P0 | 真实 Moodle 三角色、Moodle pluginfile 资源权限、正式 grade bridge 和 API 清单未提供 | 保持 `BLOCKED_INPUT`，本地 STAFF-010 结果不得升级为正式 PASS |
| `BUILD070-A11Y-001` | P1 | 该历史快照中的 `npm run test:a11y` 尚未实现 | 历史记录；当前自定义检查已达到 `OBSERVED_PASS_3_TESTS`，正式可访问性仍继续阻断完整批次门禁 |
| `BUILD070-PLAN-001` | P1 | 原计划将 STAFF-002 定义为资源编辑，但当前 BUILD-070 实际证据的 STAFF-002～009 对应题库、发布、批改、隔离和浏览器流程 | 已在第 22、23 节按实际测试 ID 重排；资源上传/替换单列为 STAFF-010，并在第 40 节绑定本地隔离实现和正式环境阻断 |
| `BUILD070-EVIDENCE-001` | P1 | BUILD-070 验收文件使用“PASS（隔离）/PASS（Mock）”等非统一状态，可能被误读为正式 PASS | 统一改用 `OBSERVED_PASS`，并保留 `local-isolated-api`、`mock-browser` 环境限定 |
| `BUILD070-T4-001` | P1 | `acceptance/frontend/BUILD-070/` 当前没有按第 27.4 节要求归档截图/视口文件 | 保持开放；补齐截图或在 `review.md` 记录受控环境阻断前，不得把 T4 证据升级为正式 PASS |

### 31.4 当前门禁结论

`BUILD-070 = IMPLEMENTED_PENDING_GATE`。本地隔离实现、静态检查、API 测试、STAFF-010 资源编辑和 Mock 浏览器主流程是 `OBSERVED_PASS`；真实 Moodle 角色、课程 PDF、正式 API 测试清单、Moodle pluginfile 权限、grade bridge、正式可访问性、T4 截图和 T0-T6 真实证据仍未具备。下一批次只能在这些门禁明确处理或经审查保留阻断状态后继续，不得宣称教师教学闭环已经完成正式验收。

## 32. 2026-07-25 测试方案写入后的进一步审查

本节是 STAFF-010 实现前的历史复审快照；第 40 节优先级更高。审查对象包括第 17、21～27 节测试规则、BUILD-070 实现范围、`acceptance/frontend/BUILD-070/` 证据和 `PROJECT_PROGRESS.yaml`。本次只修正计划、状态和证据语义，不把隔离测试升级为真实环境通过。

### 32.1 审查项目

| 审查项目 | 结果 | 结论 |
|---|---|---|
| BUILD 编号与测试 ID 绑定 | `PASS` | BUILD-070 的 STAFF-001～008 为 API/业务测试，STAFF-009 为 T4 浏览器伴随测试，STAFF-010 已绑定资源编辑隔离 API 与前端入口，正式环境仍单独记录 |
| 测试状态词汇 | `PASS` | 证据文件使用统一状态；`PASS` 只表示完整门禁通过，局部隔离结果使用 `OBSERVED_PASS` |
| 测试命令可执行性 | `REVIEW_REQUIRED` | lint、typecheck、unit、component、build、Playwright 和自定义 `test:a11y` 已有命令；正式 axe 等价审查和真实角色执行条件仍不足 |
| API 可复现输入 | `BLOCKED_INPUT` | `api-test-manifest.yaml`、`openapi.test.json`、真实角色和可重置 namespace 仍未提供 |
| 浏览器证据完整性 | `BLOCKED_INPUT` | 当前 BUILD-070 目录无六视口截图和真实角色流程证据；Mock 14/14 只能作为 `OBSERVED_PASS` |
| 课程数据前置条件 | `BLOCKED_INPUT` | manifest 声明的 20 个 PDF 缺失，完整 local acceptance 仍在 BUILD-000 fail-fast |
| 凭据和日志边界 | `PASS` | 当前证据没有 API Key、API Secret、Cookie、签名 URL、真实学生信息或完整问答正文 |

### 32.2 开放问题和关闭条件

1. **STAFF-010 资源编辑范围**：本地隔离上传、替换、版本、来源引用和归档测试已在第 40 节完成；后续必须在真实 Moodle/pluginfile 和三角色环境复验，不能把本地 `OBSERVED_PASS` 升级为正式 PASS。
2. **T4 浏览器证据**：在允许回环端口的环境执行 Mock 和真实角色流程，保存视口、截图、命令、退出码和环境标签；受限环境失败不得用历史截图替代当前结果。
3. **T5 可访问性**：本地 `npm run test:a11y` 已覆盖可命名控件、键盘焦点、基础对比度、错误/空状态和移动视口，并在第 40 节复测为 3/3；该结果仅为 `OBSERVED_PASS`。仍需完成正式 axe 等价审查、真实角色覆盖、六视口人工证据和 T0-T6 复审。
4. **真实 API**：补齐 API manifest、OpenAPI 契约、student/teacher/admin 角色引用、数据重置和脱敏断言后，重新执行 STAFF-001～008；现有 `api-contract.json` 仅是 BUILD-070 局部快照，不能替代根级真实 API 输入。
5. **数据与外部环境**：恢复与 manifest 的 hash/page_count 匹配的 PDF，完成真实 Moodle grade bridge、课程来源校验和完整 T0-T6 复审；所有外部条件完成前，BUILD-070 保持 `IMPLEMENTED_PENDING_GATE`。

### 32.3 最新门禁判定

- 测试方案状态：`DOCUMENTED_AND_REVIEWED_WITH_OPEN_FINDINGS`。
- 当前构建：`BUILD-070`。
- BUILD-070：`IMPLEMENTED_PENDING_GATE`；本地 API、单元、组件和 Mock 浏览器结果只记 `OBSERVED_PASS`。
- BUILD-000：`BLOCKED_INPUT`；20 个课程 PDF 缺失，禁止生成占位文件或修改 manifest/hash/page_count。
- `test:a11y`：本地自定义检查在第 40 节为 `OBSERVED_PASS_3_TESTS`；正式 axe 等价审查、真实角色和六视口证据未完成；前端依赖审计的 high advisory 仍为 `REVIEW_REQUIRED`。
- 最终发布：`blocked`。

只有 STAFF-001～010 的适用项、T0-T6、真实三角色、课程数据、可访问性、截图证据、回退检查和正式 API 输入全部满足第 27.5 节的 `PASS` 条件，才可以关闭教师工作台批次；任何 `OBSERVED_PASS`、`CONDITIONAL`、`BLOCKED_*` 或 `NOT_IMPLEMENTED` 都不能关闭批次。

## 33. 2026-07-25 BUILD-080 管理员工作台实现与复审

本节是当前最新构建记录，覆盖管理员服务状态、知识库版本生命周期、审计查询和备份恢复状态入口。它遵循第 27 节 T0-T6 协议；隔离 API、Mock Workflow 和 Mock 浏览器结果只能记为 `OBSERVED_PASS`。

### 33.1 实现范围

- 新增 `/admin` 及 `/admin/agent-status`、`/admin/knowledge-bases`、`/admin/audit-log`、`/admin/backup` 管理员路由和导航。
- 新增管理员脱敏服务状态、分页审计日志和服务器托管备份状态 API；浏览器不直接启动宿主机备份或恢复命令。
- 知识库管理页面支持版本创建、服务端 manifest hash 展示、PDF/Markdown 上传、黄金问题测试、`draft → processing → tested → published` 状态迁移和带原因回滚。
- `audit_log`、`kb_audit` 采用 additive migration 增加 `request_id`；知识库创建、上传、命中测试、状态迁移和回滚均写入请求 ID。
- 前端新增知识库文件、命中测试、审计和备份状态 DTO 规范化；未开放的用户/课程写管理接口显示明确未实现状态，不渲染伪造数据。

### 33.2 当前测试结果

```text
ADMIN_WORKBENCH_API_OK
API_CONTRACT_OK routes=70
python3 -m compileall -q agent-adapter scripts: PASS
frontend lint: PASS
frontend typecheck: PASS
frontend unit: 16 passed
frontend component: 2 passed
frontend build: PASS
frontend Mock Playwright: 10 passed
frontend custom accessibility Playwright: 2 passed (OBSERVED_PASS)
```

隔离 API 覆盖：学生越权、管理员状态脱敏、备份状态权限、知识库 manifest 指纹、路径穿越、文件幂等、三条黄金问题、发布门槛、审计请求 ID和审计字段脱敏。Mock 浏览器覆盖管理员创建版本 → 上传文件 → 执行三条黄金问题 → 测试门槛 → 发布版本。

### 33.3 复审发现和处理

| ID | 严重度 | 发现 | 处理 |
|---|---|---|---|
| `BUILD080-API-001` | P1 | 原有知识库生命周期接口缺少管理员审计列表和请求 ID统一记录 | 已新增 `/api/admin/audit-log`，并为知识库写操作补充 request ID 和 `kb_audit` 记录 |
| `BUILD080-API-002` | P1 | 管理员只能看到状态摘要，无法检查备份/恢复边界 | 已新增只读 `/api/admin/backup/status`；不允许浏览器直接执行宿主机命令 |
| `BUILD080-UI-001` | P1 | 前端没有管理员路由和知识库生命周期操作页 | 已新增管理员路由、版本列表、文件、黄金问题和发布/回滚视图 |
| `BUILD080-SEC-001` | P0 | 管理页面可能误显示凭据或原始鉴权信息 | 状态和审计响应只返回布尔/枚举、伪名、对象和请求 ID；隔离测试断言不包含 API Key/Secret/Authorization |
| `BUILD080-REAL-001` | P0 | 真实管理员账号、正式知识库、服务器备份归档和恢复演练未提供 | 保持 `BLOCKED_INPUT`；Mock 结果不得升级为正式 PASS |
| `BUILD080-A11Y-001` | P1 | 本地自定义 `npm run test:a11y` 已通过 2/2，但覆盖范围不足以完成正式可访问性门禁 | 记为 `OBSERVED_PASS`；补齐正式 axe 等价审查、真实角色、六视口截图和 T0-T6 证据后再关闭 |
| `BUILD080-T4-001` | P1 | 当前 BUILD-080 只有受控 Mock 浏览器结果，尚未归档真实角色截图/六视口证据 | 保持 `BLOCKED_INPUT`，补齐截图和真实角色流程后重验收 |

### 33.4 当前门禁结论

`BUILD-080 = IMPLEMENTED_PENDING_GATE`。本地管理员 API、前端单元/组件、生产构建、Mock 浏览器和自定义可访问性检查为 `OBSERVED_PASS`；真实管理员角色、正式 API manifest/OpenAPI、真实知识库 Workflow、服务器备份校验、隔离恢复日志、正式 axe 等价审查、真实角色/六视口截图和课程 PDF 前置条件仍未完成。`test_kb_lifecycle.py` 在当前工作区仍因 manifest 声明的课程 PDF 缺失而 fail-fast；本批次测试使用受控 Markdown 来源夹具，不生成占位 PDF。

只有 `ADMIN-001`～`ADMIN-007` 的真实适用测试、T0-T6 证据、正式知识库发布、服务器备份/恢复演练和回退检查全部为 `PASS`，才允许关闭 BUILD-080。当前最终发布状态继续为 `blocked`。

## 34. 2026-07-25 BUILD-080 测试方案复审与验收条件校正

本节是第 33 节之后的当前复审记录，专门核对“测试方案是否已写入计划、命令是否可执行、结果是否进入证据目录、局部通过是否被误写为正式通过”。它不覆盖密钥内容，也不把隔离环境结果升级为正式环境结果。

### 34.1 分层审查结论

| 层级 | 当前结果 | 证据 | 复审结论 |
|---|---|---|---|
| T0 范围、权限、迁移和回退 | `REVIEW_REQUIRED` | `scope.md`、`review.md`、`rollback.md` | 实现范围和 additive migration 已审查；真实管理员角色、服务器恢复和正式契约仍开放 |
| T1 静态、编译、构建和差异 | `PASS` | BUILD-080 `test-output.txt` | Python compile、lint、typecheck、build 和差异检查必须全部退出码 0 |
| T2 单元和组件 | `OBSERVED_PASS` | 16 个单元、2 个组件测试 | 业务和客户端断言通过，但不替代真实角色流程 |
| T3 API、权限、幂等、持久化和审计 | `OBSERVED_PASS` | `ADMIN_WORKBENCH_API_OK`、`api-contract.json` | 隔离 API 覆盖 ADMIN-001～007；正式 `api-test-manifest.yaml` 和 `openapi.test.json` 缺失时不得升级为 `PASS` |
| T4 浏览器和视口 | `OBSERVED_PASS` / `BLOCKED_INPUT` | Mock Playwright 10/10 | Mock 主流程通过；真实管理员角色、六视口截图和允许回环端口的复测仍待完成 |
| T5 安全、可访问性和恢复 | `OBSERVED_PASS` / `BLOCKED_INPUT` | `test:a11y` 2/2、服务器证据缺失 | 本地自定义可访问性检查通过；正式 axe 等价审查、真实角色覆盖、备份校验和恢复演练仍未完成 |
| T6 证据、回退和最终门禁 | `CONDITIONAL` | BUILD-080 证据目录 | 证据结构已建立，但存在外部输入和正式环境阻断，不能关闭 BUILD-080 |

### 34.2 本轮固定命令和记录要求

BUILD-080 复审必须从仓库根目录执行以下命令，并把退出码、测试数量和脱敏摘要写入 `acceptance/frontend/BUILD-080/test-output.txt`：

```bash
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_admin_workbench_api.py
python3 scripts/test_api_contract.py
python3 -m compileall -q agent-adapter scripts
bash -n scripts/*.sh
git diff --check
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run test:unit -- --run
cd frontend && npm run test:component -- --run
cd frontend && npm run build
cd frontend && npm run test:e2e:mock -- --workers=1
cd frontend && npm run test:a11y -- --workers=1
```

每次命令失败都必须保留失败类别和修复后重测记录；不得删除失败输出、改写课程 manifest/hash/page_count、生成占位 PDF 或将 Mock 请求伪装成真实请求。任何涉及凭据的测试只能记录状态、退出码、响应类别和脱敏摘要。

### 34.3 本轮发现与处理

| ID | 严重度 | 发现 | 处理结论 |
|---|---|---|---|
| `BUILD080-TEST-001` | P1 | 早期 BUILD-080 证据遗漏 `test:a11y` 结果 | 已将本地 2/2 结果写入计划、进度文件和 BUILD-080 证据；状态为 `OBSERVED_PASS` |
| `BUILD080-A11Y-001` | P1 | 自定义检查只覆盖本地应用壳层，不等于正式 axe、真实角色或六视口验收 | 保持开放；补齐正式 T5 和 T4 证据后复审 |
| `BUILD080-UI-002` | P1 | Mock 复测发现教师成功提示被 reload 清空，管理员连续黄金问题点击受 busy 防重入影响 | 已修复提示设置顺序，并让测试逐项等待状态完成；最终 Mock Playwright 10/10 通过 |
| `BUILD080-EVIDENCE-001` | P1 | 真实 API manifest/OpenAPI、截图、服务器恢复日志尚未归档 | 保持 `BLOCKED_INPUT`；不创建伪造证据 |
| `BUILD080-DATA-001` | P0 | 全量脚本仍在课程数据基线阶段缺少 manifest 要求的 PDF | 保持 `BLOCKED_INPUT`；不得生成占位 PDF或修改 manifest/hash/page_count |

### 34.4 BUILD-080 关闭条件

只有以下条件全部为 `PASS`，才可以把 BUILD-080 从 `IMPLEMENTED_PENDING_GATE` 改为 `PASS`：

1. `ADMIN-001`～`ADMIN-007` 在正式管理员、学生越权和可重置夹具上完成正向、负向、权限、幂等、持久化和审计断言。
2. 正式 API manifest/OpenAPI、真实知识库 Workflow、版本发布/回滚和来源结果完成核验。
3. 真实管理员浏览器主流程、失败恢复、六视口截图、键盘焦点和错误状态证据完整归档。
4. `verify_backup.sh`、`restore_rehearsal.sh` 及适用的 `full_restore_rehearsal.sh` 在服务器执行成功，并完成 SHA256、Secret 排除、恢复后可读性和回退检查。
5. 课程 PDF 与 manifest 的 hash/page_count 完全匹配，`RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh` 不再因课程数据 fail-fast。
6. T0-T6 所有适用项目、代码审查、证据和回退检查均为 `PASS`，且不存在 `OBSERVED_PASS`、`CONDITIONAL`、`BLOCKED_*`、`REVIEW_REQUIRED` 或 `NOT_IMPLEMENTED`。

当前复审结论：测试方案已写入计划并覆盖每次构建后的审查、测试、归档和验收条件；本地实现和隔离测试保持 `OBSERVED_PASS`，BUILD-080 及最终发布继续阻断。

## 35. 2026-07-25 BUILD-090 实现后测试方案落地与进一步复审

本节是当前计划的最新 BUILD-090 复审记录。审查对象包括 Agent Adapter 上下文边界、前端 SSE 客户端、资源来源回跳、情景会话、BUILD-090 Mock 浏览器测试、隔离 API 测试和 `acceptance/frontend/BUILD-090/` 证据。测试结果严格区分 `OBSERVED_PASS`、`NOT_RUN` 和真实外部阻断，不把局部夹具结果升级为完整 Agent 或真实 Workflow 通过。

### 35.1 构建后代码审查

| 审查项 | 当前结果 | 结论 |
|---|---|---|
| 服务端上下文归属 | `OBSERVED_PASS` | `COURSE_ID`、资源归属、页码范围、Agent mode 和上下文 hash 由 Adapter 重新确定；浏览器只提交资源引用，不提交可信正文 |
| 角色模式边界 | `OBSERVED_PASS` | 学生调用 `teacher_assistant` 被拒绝；教师模式仍需正式角色和真实 Workflow 复核 |
| SSE 协议处理 | `OBSERVED_PASS` | token/source/done/error 类型化解析、坏 JSON、尾部未闭合缓冲区和重复 done 有客户端断言；上游断流和超时恢复尚未形成完整 API 门禁 |
| 来源核验与回跳 | `OBSERVED_PASS` | 只有带合法 resource ID、页码和已核验状态的来源可打开教材；非法来源显示待核验的正式 API 测试尚未补齐 |
| 情景会话 | `OBSERVED_PASS` | start、Agent turn、end 使用会话归属和幂等键；重复轮次、跨用户会话和上游失败恢复仍需独立测试 |
| 日志和密钥 | `OBSERVED_PASS` | 本次代码和证据不记录 API Key、API Secret、签名 URL、Cookie、Authorization、完整问题或完整回答 |
| BUILD-090 全范围覆盖 | `REVIEW_REQUIRED` | 学习诊断、教师助手、出题草稿、主观题初评、Prompt Injection、资料不足、跨课程隔离和负向流式已有本地边界证据；真实 Workflow 性能和正式环境证据仍未完成 |

### 35.2 本轮固定命令和结果

所有命令从仓库根目录或 `frontend/` 执行；真实凭据测试只由脚本读取 `.env.test.local`，本节和证据文件只记录脱敏结果。

| 层级 | 命令/结果 | 状态 |
|---|---|---|
| Adapter 上下文 API | `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_agent_context_api.py` → `AGENT_CONTEXT_API_OK` | `OBSERVED_PASS` |
| API 路由契约 | `python3 scripts/test_api_contract.py` → `API_CONTRACT_OK routes=70` | `PASS` |
| Python/Shell/YAML/差异 | `compileall`、`bash -n scripts/*.sh`、YAML parse、`git diff --check` | `PASS` |
| 前端 lint/typecheck | `npm run lint`、`npm run typecheck` | `PASS` |
| 前端单元 | `npm run test:unit` → 18 passed、2 skipped | `OBSERVED_PASS` |
| 前端组件 | `npm run test:component` → 2 passed、18 skipped | `OBSERVED_PASS` |
| 前端生产构建 | `npm run build` → Vite 1646 modules transformed | `PASS` |
| Mock 浏览器（第35节变更前快照） | `npm run test:e2e:mock -- --workers=1` → 12/12 | `OBSERVED_PASS`；第36节之后当前结果为 13/13 |
| 自定义可访问性 | `npm run test:a11y -- --workers=1` → 2/2 | `OBSERVED_PASS` |
| Spark Assistant 正向协议 | 已有脱敏正向单轮记录；只覆盖合法握手、响应结构和正常关闭 | `OBSERVED_PASS` |

定向复测中曾发现两类夹具问题：资源测试错误假定 `res-34`，情景测试的按钮在动画布局中未稳定。测试已改为读取服务端资源列表获取真实 ID，并对受控流程按钮使用稳定的强制交互；修复后定向测试为 `2 passed`，全量 Mock 测试为 `12 passed`。该修复不改变生产权限和业务逻辑。

### 35.3 AGENT 测试 ID 复审

| 测试 ID | 当前状态 | 当前证据 | 尚缺条件 |
|---|---|---|---|
| `AGENT-001` | `OBSERVED_PASS` | SSE 客户端测试、上下文 API、课程问答 Mock 浏览器 | 真实 Workflow 的 token/source/done 和专业答案复核 |
| `AGENT-002` | `NOT_RUN` | 无独立资料不足验收证据 | 真实资料不足问题、无伪造来源/页码断言 |
| `AGENT-003` | `NOT_RUN` | 无独立 Prompt Injection 验收证据 | 学生/教师边界、系统提示和凭据泄露负向测试 |
| `AGENT-004` | `NOT_RUN` | 本轮未执行学习诊断专用 API/浏览器批次 | 服务端 profile、推荐资源存在性和刷新一致性 |
| `AGENT-005` | `NOT_RUN` | 本轮未执行教师出题专用 Workflow 批次 | 结构化 schema、教师确认和学生越权断言 |
| `AGENT-006` | `NOT_RUN` | 本轮未执行主观题 Agent 初评批次 | `needs_review`、教师复核和最终成绩不可直写 |
| `AGENT-007` | `OBSERVED_PASS` | 第35节 12/12 Mock 浏览器包含情景 start/turn/end；第36节之后当前全量为 13/13 | 正式角色、真实 Workflow、重复轮次和跨用户会话复核 |
| `AGENT-008` | `NOT_RUN` | 仅有客户端格式错误断言，不能替代上游断流/超时门禁 | 502/504、pending 恢复、取消、重试和持久化一致性 |
| `AGENT-009` | `NOT_RUN` | 本轮未执行非法来源专用 API 夹具 | 未知文件、页码、版本和状态必须丢弃或标记待核验 |
| `AGENT-010` | `NOT_RUN` | 本轮未执行跨课程会话夹具 | 两课程、两用户和刷新后的上下文隔离 |

### 35.4 分层门禁结论

| 层级 | 当前结果 | 复审结论 |
|---|---|---|
| T0 范围、权限、回退 | `REVIEW_REQUIRED` | 局部代码边界已审查；完整 Agent 模式和真实角色范围仍未关闭 |
| T1 静态、编译、构建、差异 | `PASS` | 本轮所有固定静态门禁退出码为 0 |
| T2 单元和组件 | `OBSERVED_PASS` | 18 个单元、2 个组件通过；不能替代端到端和真实 Workflow |
| T3 API、权限、幂等、上下文 | `OBSERVED_PASS` | 上下文 API 和 70 路由静态契约通过；正式 API manifest/OpenAPI、完整 AGENT-001～010 尚缺 |
| T4 浏览器和视口 | `OBSERVED_PASS` / `BLOCKED_INPUT` | Mock 13/13 通过；真实角色、六视口人工截图和正式 PDF 仍阻断 |
| T5 安全、可访问性、恢复 | `OBSERVED_PASS` / `BLOCKED_INPUT` | 本地自定义可访问性 2/2；正式 axe 等价审查、真实负向 Agent、服务器恢复未完成 |
| T6 证据、回退、最终门禁 | `CONDITIONAL` | BUILD-090 证据已建立，但未满足全部测试 ID 和真实外部条件 |

### 35.5 BUILD-090 关闭条件

只有以下条件全部为 `PASS`，才可以将 BUILD-090 从 `IMPLEMENTED_PENDING_GATE` 改为 `PASS`：

1. `AGENT-001`～`AGENT-010` 在隔离 API、学生/教师/管理员适用角色和可重置命名空间中完成正向、负向、越权、幂等、持久化、恢复和审计断言；不允许用 `NOT_RUN` 或 `OBSERVED_PASS` 代替。
2. 提供正式 `api-test-manifest.yaml`、`openapi.test.json`、角色引用、固定课程资源和重置方法，并完成真实 Workflow 非流式、流式、黄金问题、来源核验和响应错误测试。
3. 资料不足、Prompt Injection、非法来源、上游 401/429/5xx、超时、断流、取消、重试、重复 done 和跨课程会话均有脱敏证据。
4. 真实知识库版本绑定 manifest，课程 PDF 的 hash/page_count 与 manifest 一致；性能记录覆盖首 token、完整回答和至少 3 个并发请求。
5. 完成真实角色浏览器流程、六视口截图、键盘/屏幕阅读器等价审查和错误恢复；服务器备份/恢复与回退证据同步归档。
6. T0-T6 不存在 `OBSERVED_PASS`、`CONDITIONAL`、`BLOCKED_*`、`REVIEW_REQUIRED`、`NOT_RUN` 或 `NOT_IMPLEMENTED`，并由复核人更新 `PROJECT_PROGRESS.yaml`、`PROJECT_STATUS.md` 和本目录证据。

当前结论：`BUILD-090 = IMPLEMENTED_PENDING_GATE`。本地实现、Mock 浏览器和隔离 API 已具备继续联调条件，但不能声称“真实讯飞 Agent 主链路”或“完整学习通式 Agent 功能已验收”。

## 36. 2026-07-25 BUILD-090 Agent 边界测试补齐与测试基础设施复审

本节覆盖第 35 节之后的新增实现和重测结果。新增内容包括 Adapter 的配置化 `COURSE_ID` 会话边界、独立 `scripts/test_agent_boundary_api.py`、同步夹具迁移到 `httpx.AsyncClient + ASGITransport`，以及课程 PDF 缺失时的显式待挂载断言。第 35 节的 `NOT_RUN` 是变更前快照；本节是当前 BUILD-090 本地证据的权威结果。

### 36.1 新增实现和审查

| 项目 | 结果 | 处理 |
|---|---|---|
| 单课程会话边界 | `OBSERVED_PASS` | 新增 `COURSE_ID` 配置；身份课程与 Adapter 挂载课程不一致时，session/API 在数据访问前返回 `course_forbidden` |
| 资料不足 | `OBSERVED_PASS` | 无来源的流式回答只显示正文和 done，不生成 source、文件名或页码 |
| 策略与角色边界 | `OBSERVED_PASS` | Prompt Injection 返回 `policy_blocked`；学生调用 `question_draft` 返回 `invalid_mode` |
| 学习诊断 | `OBSERVED_PASS` | profile、规则版本和推荐资源由服务端加载，推荐资源 ID 必须存在 |
| 教师出题/主观题初评 | `OBSERVED_PASS` | 教师可调用出题草稿模式；主观题初评和教师复核由 `ASSESSMENT_API_OK` 覆盖，初评不直写最终成绩 |
| 断流恢复 | `OBSERVED_PASS` | 情景流收到上游 error 后清理 pending turn；新幂等键可重试同一轮并完成 |
| 来源污染 | `OBSERVED_PASS` | 未知文件、错误章节和越界页码均不会进入核验来源 |
| 测试基础设施 | `PASS` | Starlette TestClient 在当前组合中会挂起；历史同步夹具改用当前线程短生命周期 ASGI 客户端后恢复可执行 |
| 课程 PDF 生命周期 | `BLOCKED_INPUT` | `test_kb_lifecycle.py` 仍因 manifest 指定的 PDF 文件缺失而阻断；没有生成占位 PDF |
| 教师 Agent 草稿入口 | `OBSERVED_PASS` | 教师可从统一 AgentPanel 生成草稿并带入题库编辑；页面不会自动创建或发布题目 |

### 36.2 新增固定命令和结果

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_agent_boundary_api.py` | `AGENT_BOUNDARY_API_OK` |
| `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_agent_context_api.py` | `AGENT_CONTEXT_API_OK` |
| `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_adapter_runtime.py` | `ADAPTER_RUNTIME_OK` |
| `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_acceptance_fixture.py` | `ACCEPTANCE_FIXTURE_OK` |
| `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_graph_scenario_fixture.py` | `CASE006_GRAPH_TEXTBOOK_SCENARIO_OK` |
| `PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_assessment_api.py` | `ASSESSMENT_API_OK` |
| `python3 -m unittest -q scripts.test_course_store` | `7 tests OK` |
| `python3 -m unittest -v agent-adapter/tests/test_main.py` | `10 tests OK` |
| `python3 -m compileall -q agent-adapter scripts` + `bash -n scripts/*.sh` | `PASS` |

测试基础设施修复前的四个同步夹具和 Adapter 单元测试曾出现 `TestClient` 初始化挂起（超时，无断言结果），该结果保留为 `BLOCKED_TEST_INFRA`，不能记作 PASS。迁移后四个夹具分别通过；知识库生命周期的失败类别为 `BLOCKED_INPUT`，原因是课程 PDF 缺失而非 API 断言失败。

### 36.3 AGENT 测试 ID 当前状态

| 测试 ID | 当前状态 | 当前证据 |
|---|---|---|
| `AGENT-001` | `OBSERVED_PASS` | 上下文 API、SSE 客户端、Mock 浏览器 |
| `AGENT-002` | `OBSERVED_PASS` | `test_agent_boundary_api.py` 无来源/无伪造引用断言 |
| `AGENT-003` | `OBSERVED_PASS` | `test_agent_boundary_api.py` + Adapter runtime 策略拒绝 |
| `AGENT-004` | `OBSERVED_PASS` | 服务端 profile/推荐资源和学习诊断响应断言 |
| `AGENT-005` | `OBSERVED_PASS` | 教师 `question_draft` 模式允许、学生越权拒绝 |
| `AGENT-006` | `OBSERVED_PASS` | `ASSESSMENT_API_OK` 的 Agent 初评、教师复核和最终成绩边界 |
| `AGENT-007` | `OBSERVED_PASS` | Mock 浏览器、Graph/Scenario fixture、Agent context |
| `AGENT-008` | `OBSERVED_PASS` | 情景上游 error、pending 清理和新幂等键重试 |
| `AGENT-009` | `OBSERVED_PASS` | manifest 文件、章节、页码严格匹配测试 |
| `AGENT-010` | `OBSERVED_PASS` | `COURSE_ID` 配置和其他课程 `course_forbidden` 测试 |

这些状态只表示本地隔离边界已通过，不能升级为真实 `API_PASS`。真实 Workflow、真实知识库、正式 API manifest/OpenAPI、真实 Moodle 角色、真实课程 PDF、性能、正式可访问性和服务器恢复仍按第 35.5 节作为关闭条件。

## 37. 2026-07-25 BUILD-090 性能基线重测与计划一致性复审

本节补录 BUILD-090 构建后性能烟囱测试，并校正前文“性能尚未执行”的表述。该测试使用本地 Mock Workflow、隔离 ASGI Adapter 和临时数据库，只证明当前 Adapter 在受控输入下的并发/限流路径可运行；它不代表真实讯飞 Workflow 的首 token、完整回答、来源质量或生产容量。

### 37.1 固定命令和结果

```bash
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/performance_smoke.py
```

结果：`PERFORMANCE_MOCK_OK samples=30 p50_ms=34.81 p95_ms=44.19`。

本次包含 3 个隔离用户、30 个请求，使用当前 `AGENT_USER_CONCURRENCY=1` 和 Mock Workflow。命令退出码为 0，响应均为 HTTP 200 且包含 `event: done`。结果状态为 `OBSERVED_PASS`，不得写成正式性能 `PASS`。

### 37.2 性能审查结论

| 审查项 | 当前结果 | 结论 |
|---|---|---|
| 本地 Adapter 30 请求烟囱 | `OBSERVED_PASS` | p50 34.81ms、p95 44.19ms，证明受控 Mock 路径可运行 |
| 真实 Workflow 首 token | `BLOCKED_INPUT` | 尚无真实 Workflow URL、版本绑定和脱敏时延记录 |
| 真实 Workflow 完整回答 | `BLOCKED_INPUT` | 尚无真实来源核验、专业答案复核和完整回答时延 |
| 真实并发容量 | `BLOCKED_INPUT` | 尚无至少 3 个并发请求、限流、429/超时和恢复证据 |
| 证据安全 | `PASS` | 仅归档样本数、状态码、事件存在性和时延，不归档凭据或完整问答 |

### 37.3 计划一致性修正

- BUILD-090 的本地性能检查已加入构建后固定证据，但真实性能门禁仍保持开放。
- `PROJECT_PROGRESS.yaml`、`PROJECT_STATUS.md` 和 `acceptance/frontend/BUILD-090/` 必须使用相同的 `OBSERVED_PASS`/`BLOCKED_INPUT` 语义。
- 后续真实性能批次必须记录首 token、完整回答、至少 3 个并发请求、429/超时/断流恢复和成功率；缺任何一项都不能关闭 BUILD-090。
- 课程 PDF、正式 API manifest/OpenAPI、真实角色、正式可访问性和服务器恢复阻断不因本地性能结果而改变。

### 37.4 最新门禁判定

测试方案状态：`DOCUMENTED_AND_REVIEWED_WITH_OPEN_FINDINGS`。第37节复审对象为 BUILD-090；本地 Agent-001～010 边界、Mock 浏览器和 Mock 性能为 `OBSERVED_PASS`，真实 Workflow、课程数据、正式角色、正式可访问性、正式性能和恢复证据仍未完成。因此 `BUILD-090 = IMPLEMENTED_PENDING_GATE`。第38节已将 BUILD-100 更新为 `IMPLEMENTED_PENDING_GATE`，但正式发布条件仍未满足，最终发布继续 `blocked`。

## 38. 2026-07-25 BUILD-100 发布前硬化实现与复审

本节记录在真实 Workflow、课程 PDF 和正式服务器条件尚未提供时，当前工作区可独立完成的发布前硬化。该批次只推进本地代码质量和隔离浏览器证据，不把本地结果升级为正式发布通过。

### 38.1 已实现范围

- 增加全局 `ErrorBoundary`。渲染异常显示重新加载入口，并把错误分类、当前路由、时间和脱敏编号写入受限的本地诊断记录；不保存异常正文、请求体、Cookie、Authorization、模型回答或凭据。
- 管理员工作台改为 `lazy(() => import('./AdminPage'))`，路由使用 `Suspense` 加载状态；生产构建生成独立 `AdminPage-*.js` chunk。
- PDF 阅读器 iframe 增加 `loading="lazy"` 和 `referrerPolicy="no-referrer"`；文件未挂载时继续显示明确待挂载状态，不创建伪造 PDF。
- `frontend/nginx.conf` 对 `/index.html` 和 `/api/` 设置 `Cache-Control: no-store`；对带指纹的 JS/CSS/图片/字体设置 `public, max-age=31536000, immutable`。
- 新增 `npm run test:hardening`，专门执行错误边界和脱敏诊断测试，防止被原有 `test:unit`/`test:component` 名称过滤遗漏。

### 38.2 构建后固定命令和结果

| 命令 | 结果 | 证据 |
|---|---|---|
| `python3 scripts/test_frontend_hardening.py` | `PASS`：`FRONTEND_HARDENING_OK` | BUILD-100 `test-output.txt` |
| `npm run lint` | `PASS` | BUILD-100 `test-output.txt` |
| `npm run typecheck` | `PASS` | BUILD-100 `test-output.txt` |
| `npm run test:unit -- --run` | `OBSERVED_PASS`：19 passed、3 skipped | BUILD-100 `test-output.txt` |
| `npm run test:component -- --run` | `OBSERVED_PASS`：2 passed | BUILD-100 `test-output.txt` |
| `npm run test:hardening -- --run` | `OBSERVED_PASS`：2 passed | BUILD-100 `test-output.txt` |
| `npm run build` | `PASS`：1649 modules，生成 AdminPage 独立 chunk | BUILD-100 `test-output.txt` |
| `npm run test:e2e:mock -- --workers=1` | `OBSERVED_PASS`：13 passed | BUILD-100 `test-output.txt` |
| `npm run test:a11y -- --workers=1` | `OBSERVED_PASS`：2 passed | BUILD-100 `test-output.txt` |
| `npm run test:e2e -- --workers=1` | `OBSERVED_PASS`：1 passed | BUILD-100 `test-output.txt` |

受限沙箱中的首次浏览器尝试在监听阶段返回 `listen EPERM`，未进入页面断言；在允许本地回环监听的环境串行重测后，Mock、可访问性和标准 smoke 均通过。该启动失败保留为 `BLOCKED_TEST_INFRA`，不能伪装成业务失败或通过。

### 38.3 构建后代码审查

| 审查项 | 当前结果 | 结论 |
|---|---|---|
| 错误恢复 | `OBSERVED_PASS` | 页面崩溃不再只留下空白屏；用户有重新加载入口和脱敏错误编号 |
| 诊断隐私 | `OBSERVED_PASS` | 诊断记录只有固定枚举、路由、时间和随机编号，数量上限为 20 |
| 路由级分包 | `OBSERVED_PASS` | 管理员工作台产生独立 chunk；其余大页面仍需后续分包批次继续审查 |
| 资源加载 | `OBSERVED_PASS` | PDF iframe 使用懒加载和 no-referrer；未挂载 PDF 不开放阅读器 |
| 缓存策略 | `OBSERVED_PASS` | 入口/API 不缓存，指纹静态资源长期缓存；容器内 Nginx 运行验证待补 |
| 正式发布配置 | `BLOCKED_INPUT` | Docker 基础镜像、HTTPS 域名、真实三角色和服务器验证尚未提供 |

### 38.4 BUILD-100 当前门禁

- 本地 BUILD-100 硬化：`IMPLEMENTED_PENDING_GATE`。
- 本地硬化测试、构建和隔离浏览器：`OBSERVED_PASS` 或局部 `PASS`。
- Docker 镜像、正式 HTTPS、真实三角色、六视口人工截图、正式 axe 等价审查、备份恢复、真实 Workflow 和课程数据：`BLOCKED_INPUT` 或 `BLOCKED_DEPENDENCY`。
- 只有容器运行验证、正式域名/HTTPS、三角色 Playwright、当前数据库恢复演练和 T0-T6 证据全部为 `PASS`，才能关闭 BUILD-100。
- 当前最终发布继续 `blocked`。

## 39. 2026-07-25 BUILD-030 学习图谱增量实现与复审

本节记录学生工作台中原有“打开学习图谱”占位入口的补齐。后端已经提供知识点搜索、节点详情、邻接关系和有限路径 API；本轮把这些服务端能力接入 React 页面，并保持预览模式、真实模式和正式课程数据边界清晰。

### 39.1 已实现范围

- 新增 `/knowledge-graph` 路由和主导航入口。
- 支持知识点名称搜索、章节筛选、节点选择、节点详情和相邻知识点继续选择。
- 节点详情显示服务端关系类型和学情掌握度；可从节点进入 Agent，使用编码后的 `node_id` 作为上下文引用。
- 学习记录页的知识点入口改为真实图谱路由；预览模式只显示已知学习点摘要，不伪造邻接关系。
- 客户端新增图谱 DTO 归一化测试，Mock 浏览器新增学生节点详情流程。

### 39.2 构建后固定命令和结果

| 命令 | 结果 | 证据 |
|---|---|---|
| `npm run lint` | `PASS` | BUILD-030 `graph-test-output.txt` |
| `npm run typecheck` | `PASS` | BUILD-030 `graph-test-output.txt` |
| `npm run test:unit -- --run` | `OBSERVED_PASS`：当前选择 20 passed、3 skipped | BUILD-030 `graph-test-output.txt` |
| `npm run test:e2e:mock -- --workers=1` | `OBSERVED_PASS`：14 passed | BUILD-030 `graph-test-output.txt` |
| `npm run test:a11y -- --workers=1` | `OBSERVED_PASS`：3 passed，包含图谱控件 | BUILD-030 `graph-test-output.txt` |
| `npm run test:e2e -- --workers=1` | `OBSERVED_PASS`：1 passed | BUILD-030 `graph-test-output.txt` |

### 39.3 复审结论

| 审查项 | 当前结果 | 结论 |
|---|---|---|
| 数据来源 | `OBSERVED_PASS` | 真实模式节点和邻接详情来自 Adapter，前端不提交可信节点正文 |
| 权限边界 | `REVIEW_REQUIRED` | 本地 Adapter 会话校验已存在；真实学生/教师角色和跨课程图谱证据仍缺失 |
| 来源联动 | `OBSERVED_PASS` | 节点详情可进入 Agent；正式教材来源和页码仍需真实 PDF 验证 |
| 可访问性/移动端 | `OBSERVED_PASS` | 现有自定义检查 3/3（含图谱控件）、响应式 smoke 1/1 通过；六视口人工证据未归档 |
| 图谱交互深度 | `REVIEW_REQUIRED` | 当前是可验收节点网格，不是最终拖拽布局、路径高亮和图表化视图 |

当前增量状态：`BUILD-030 = PARTIAL_IMPLEMENTATION_PENDING_GATE`。节点搜索、详情、邻接和 Agent 联动已具备本地证据；正式图谱版本、真实课程 PDF、真实角色、六视口截图和高级路径可视化仍未完成，不能关闭 BUILD-030 或最终发布。

## 40. 2026-07-25 BUILD-070 STAFF-010 资源编辑实现、构筑后审查与验收

本节是 BUILD-070 资源上传/替换/版本/归档的当前权威记录，覆盖本地隔离 API、React 教师页面和构筑后复审。它将原先的 `NOT_IMPLEMENTED` 缺口改为已实现的 `OBSERVED_PASS`，但不把本地存储实现升级为 Moodle `pluginfile` 或真实角色的正式通过。

### 40.1 实现范围与数据边界

- `resources` 表采用增量迁移，增加 `title`、`source_reference`、`status`、`revision` 和内部 `storage_path`；旧 manifest 资源默认为 `published`，不改写 manifest、hash 或 page_count。
- 新增 `resource_revisions` 表，每次上传/替换保留修订号、文件名、SHA-256、字节数、上传者、状态和时间；内部路径永不进入 API DTO。
- 新增教师 API：
  - `GET /api/teacher/resources`
  - `POST /api/teacher/resources`
  - `PUT /api/teacher/resources/{resource_id}/file`
  - `POST /api/teacher/resources/{resource_id}/publish`
  - `POST /api/teacher/resources/{resource_id}/archive`
- 上传只接受安全文件名、`.pdf` 或 `.md`，上限 20 MiB；PDF 需要 `%PDF-` 和尾部 `%%EOF`，Markdown 必须是非空 UTF-8 且不含 NUL。
- 每个写操作继续执行教师/管理员角色、CSRF、`Idempotency-Key`、request ID 和审计；相同资源的重复 SHA-256 不增加修订号。
- 学生查询、阅读详情和阅读进度只允许 `published`；替换已发布资源后自动回到 `draft`，归档后学生端返回 404/不再列出。
- React `/teacher/resources` 页面提供元数据草稿、文件上传/替换、修订展示、发布和归档入口。

### 40.2 STAFF-010 测试映射

| 测试 ID | 验收内容 | 必须满足的条件 | 当前证据 |
|---|---|---|---|
| STAFF-010-A | 角色与元数据 | student 访问教师资源 API 为 403；teacher 创建 draft，重复 metadata 幂等返回同一 ID | `scripts/test_teacher_resource_api.py` |
| STAFF-010-B | 文件安全 | 路径穿越、非法后缀、伪造 PDF、空文件、超 20 MiB 均拒绝；磁盘路径不出现在响应 | 同上 |
| STAFF-010-C | 上传与去重 | 合法 Markdown/PDF 生成 v1；相同 SHA 使用新幂等键不生成 v2 | 同上 |
| STAFF-010-D | 替换与版本 | 替换生成 v2，v1 为 `superseded`、v2 为 `active`，资源重新进入 draft | 同上 |
| STAFF-010-E | 发布与学生可见性 | draft 有文件才可 publish；published 可被学生列出和打开；替换 draft 后隐藏 | 同上 |
| STAFF-010-F | 归档与撤销访问 | archive 后学生列表不含资源、详情和进度接口为 404；归档资源不可再次替换 | 同上 |
| STAFF-010-G | 审计与回退 | create/upload/replace/publish/archive 均有审计；只删除本地临时测试目录，不删课程数据 | 同上、`store.audit_logs` |

### 40.3 每次构筑后的固定审查顺序

1. T0 范围审查：确认本批次只新增教师资源编辑，不把真实 Moodle 文件权限、PDF 页数或 manifest 数据伪装为已验收；检查回退说明和 `api-contract.json` 是否包含 STAFF-010 五条路由。
2. T1 静态审查：执行 `python3 -m compileall -q agent-adapter scripts`、`bash -n scripts/*.sh`、`git diff --check`；检查 SQLite migration 在旧数据库和空数据库都为 additive。
3. T2 单元/存储审查：执行 `python3 scripts/test_course_store.py`、`pytest -q agent-adapter/tests/test_main.py`，确认原有资源进度、图谱和教师题库不回归。
4. T3 API/安全审查：执行 `python3 scripts/test_teacher_resource_api.py`，逐条核对 STAFF-010-A～G；额外确认响应 JSON 不含 `storage_path`，文件只落在配置化 `RESOURCE_STORAGE_DIR/{resource_id}/`。
5. T4 前端审查：执行 `npm run lint`、`npm run typecheck`、`npm run test:unit -- --run`、`npm run test:component -- --run`、`npm run build`；用 Mock Playwright 验证教师会话仍能进入工作台，新增页面至少通过可访问性控件检查和 390px/1440px smoke。
6. T5 安全/恢复审查：复核控制字符、路径分隔符、后缀、魔数、大小、CSRF、幂等冲突、角色越权和归档后访问；检查本地测试目录退出后清理，不能把测试文件写入 `course-data/normalized/` 或 `COURSE_MANIFEST`。
7. T6 证据与门禁：将命令、退出码、测试数、环境、commit 状态和未完成条件写入 `acceptance/frontend/BUILD-070/`，再同步 `PROJECT_PROGRESS.yaml` 与 `PROJECT_STATUS.md`；任何正式 Moodle/真实角色缺失都保持 `IMPLEMENTED_PENDING_GATE`。

### 40.4 本次构筑结果

| 命令 | 结果 | 复审结论 |
|---|---|---|
| `python3 scripts/test_teacher_resource_api.py` | `TEACHER_RESOURCE_API_OK` | `OBSERVED_PASS`，STAFF-010-A～G local-isolated-api |
| `python3 scripts/test_resource_progress_api.py` | `RESOURCE_PROGRESS_API_OK` | `OBSERVED_PASS`，确认 published 可读、归档后不可读 |
| `python3 scripts/test_teacher_workbench_api.py` | `TEACHER_WORKBENCH_API_OK` | `OBSERVED_PASS`，既有题库/作业/成绩册回归 |
| `python3 scripts/test_api_contract.py` | `API_CONTRACT_OK routes=74` | `PASS`，STAFF-010 五条路由已纳入契约检查 |
| `python3 scripts/test_course_store.py` | 7 tests OK | `PASS` |
| `pytest -q agent-adapter/tests/test_main.py` | 10 passed | `PASS` |
| `npm run lint` | exit 0 | `PASS` |
| `npm run typecheck` | exit 0 | `PASS` |
| `npm run test:unit -- --run` | 21 passed，3 skipped | `OBSERVED_PASS` |
| `npm run test:component -- --run` | 2 passed | `OBSERVED_PASS` |
| `npm run test:hardening -- --run` | 2 passed | `OBSERVED_PASS` |
| `npm run build` | 1649 modules | `PASS` |
| `npm run test:e2e:mock -- --workers=1` | 15 passed | `OBSERVED_PASS`，包含 STAFF-010 教师资源上传/替换/发布/归档流程；允许本地监听环境 |
| `npm run test:a11y -- --workers=1` | 3 passed | `OBSERVED_PASS`，正式 axe 等价审查仍未完成 |
| `git diff --check`、`compileall` | exit 0 | `PASS` |

### 40.5 构筑后进一步审查结论

| 审查项 | 结果 | 未关闭原因 |
|---|---|---|
| 本地资源编辑业务闭环 | `OBSERVED_PASS` | 隔离 SQLite/ASGI 环境，不是生产数据证明 |
| 文件安全、幂等、版本和审计 | `OBSERVED_PASS` | 覆盖固定负向用例；仍需真实部署配置审查 |
| 学生可见性 | `OBSERVED_PASS` | 仅验证 Adapter published 状态，未验证 Moodle capability/pluginfile |
| 教师 React 页面 | `OBSERVED_PASS` | lint/typecheck/build 通过；Mock 浏览器已覆盖完整上传/替换/发布/归档交互，本地 CDP 六视口截图已归档，正式角色人工截图仍未完成 |
| 真实角色与 Moodle pluginfile | `BLOCKED_INPUT` | 真实课程、角色、API manifest、pluginfile 权限和可重置 namespace 未提供 |
| 课程 PDF 页数/hash | `BLOCKED_INPUT` | manifest 要求的 20 个 PDF 仍缺失；本批次禁止伪造 |

当前判定：`STAFF-010 = OBSERVED_PASS(local-isolated-api + mock-browser)`；`BUILD-070 = IMPLEMENTED_PENDING_GATE`。下一次 BUILD-070 复审必须优先补齐真实 student/teacher/admin 角色、Moodle 文件权限、正式 API 契约和 T4 截图，不能把本地资源存储结果升级为正式 PASS。

## 41. 2026-07-25 STAFF-010 测试复测后的计划进一步审查

本次复审以第 27 节的 T0-T6 协议为准，核对计划文字、实现、测试命令和 `acceptance/frontend/BUILD-070/` 证据是否一致。复测使用本地隔离 SQLite、Mock Auth、Mock Workflow、临时资源目录和允许本地回环监听的 Playwright 环境；没有读取、写入或记录任何凭据值。

### 41.1 复审发现与修正

| 复审项 | 发现 | 修正/结论 |
|---|---|---|
| 测试数量一致性 | 第 40 节和 BUILD-070 证据仍记录 14/14 | 已统一为 15/15，并明确新增 STAFF-010 浏览器流程 |
| 资源编辑浏览器覆盖 | 代码已有创建、上传、替换、发布和归档测试，但计划文字仍称未覆盖 | 已改为 Mock 浏览器完整覆盖；本地 CDP 六视口截图已归档，正式角色人工截图仍为 `BLOCKED_INPUT` |
| 可访问性门禁 | 最新执行为 3 个自定义 Playwright 检查 | 保持 `OBSERVED_PASS`；不替代正式 axe 等价审查 |
| 计划门禁语义 | 局部隔离测试容易被误读为正式通过 | 明确 STAFF-010 仅为 `OBSERVED_PASS(local-isolated-api + mock-browser)`，BUILD-070 继续 `IMPLEMENTED_PENDING_GATE` |
| 真实环境缺口 | Moodle 角色、pluginfile、课程 PDF、正式 API 契约和正式角色截图仍缺失 | 保留 `BLOCKED_INPUT`，不以本地资源存储或 Mock 截图关闭这些门禁 |

### 41.2 复测后的硬性验收条件

- STAFF-010 本地闭环必须同时满足 API `STAFF-010-A～G`、Mock 浏览器 15/15、可访问性 3/3、构建和静态检查；任一失败即回到 `REVIEW_REQUIRED`。
- 正式关闭 BUILD-070 还必须有可重置 Moodle 测试课程、student/teacher/admin 三角色、正式 API manifest/OpenAPI、pluginfile capability、成绩回写证据和 T4 六视口截图；本地 Mock 不可替代这些条件。
- 每次复测证据必须记录命令、退出码、测试数、运行边界、未完成输入和清理结果；不得记录 API key、API secret、Cookie、Authorization、签名 URL 或学生数据。

### 41.3 当前门禁结论

复测结果为：Mock 浏览器 `15/15`，自定义可访问性 `3/3`，STAFF-010 隔离 API 仍为 `TEACHER_RESOURCE_API_OK`。计划、实现和证据目录已重新对齐；测试方案状态为 `DOCUMENTED_AND_REVIEWED_WITH_OPEN_FINDINGS`。开放输入未满足前，`STAFF-010 = OBSERVED_PASS(local-isolated-api + mock-browser)`，`BUILD-070 = IMPLEMENTED_PENDING_GATE`，不得标记正式 `PASS`。

## 42. 2026-07-25 BUILD-090 Spark Assistant 负向测试实现与构筑后审查

本节记录 Spark Assistant WebSocket 的当前增量结果。测试仍与 Xingchen Workflow HTTPS/SSE 链路分开，所有真实接口测试只读取 `.env.test.local`，证据不保存凭据或完整对话。第一次直接运行负向 runner 时发现本地脚本导入路径错误；该次在建立连接前失败，修复后重新执行，不计为接口失败或通过。

### 42.1 新增测试实现

- `scripts/test_spark_assistant_contract.py`：离线测试配置缺失、占位/非法地址、预置鉴权参数、签名 URL 脱敏和 WebSocket 掩码/非掩码帧解码，6/6 通过。
- `scripts/test_spark_assistant_negative.py`：从 `.env.test.local` 加载配置，使用无个人数据的协议错误请求，禁止打印响应正文、签名 URL、API key/secret、Cookie 或 Authorization。
- 远端负向覆盖：缺少 `header.app_id`、缺少 `payload.message.text`、非法 `role`、越界 `temperature`；四个用例均完成 `101` 握手后返回脱敏错误码 `10003` 或 `10004`，并以 `close_code=1000` 关闭。

### 42.2 构筑后测试结果

| 命令 | 结果 | 状态/边界 |
|---|---|---|
| `python3 -m unittest -q scripts.test_spark_assistant_contract` | 6 tests OK | `OBSERVED_PASS`，离线协议契约 |
| `python3 scripts/test_spark_assistant_ws.py --timeout 30` | handshake 101、`header_code=0`、3 帧、正常关闭 1000 | `OBSERVED_PASS`，合法单轮正向 |
| `python3 scripts/test_spark_assistant_negative.py --timeout 15` | 4/4 返回 `error_code=10003/10004`、`close_code=1000` | `OBSERVED_PASS`，参数/字段负向 |
| `python3 -m compileall -q scripts`、`git diff --check` | exit 0 | `PASS` |

### 42.3 复审结论和剩余条件

| 审查项 | 当前结果 | 未关闭原因 |
|---|---|---|
| 本地配置和签名生成 | `OBSERVED_PASS` | 离线契约和合法正向握手通过；不代表远端会拒绝篡改鉴权 |
| 远端鉴权负向 | `FAIL` | 错误 API key、错误 Secret、篡改 date 均完成最终 `header.code=0`；必须先解释接口/环境行为并重验收 |
| 参数/字段负向 | `OBSERVED_PASS` | 4/4 远端返回 10003/10004；不能代表所有官方错误码或业务拒绝分支 |
| 限流和并发 | `NOT_RUN` | 需要受控测试窗口和明确日/秒/并发配额，避免无意放大请求量 |
| 断流/超时/恢复 | `NOT_RUN` | 需要 Adapter 到前端 SSE 的状态持久化、取消、重试和恢复证据 |
| 内容审核 | `NOT_RUN` | 需要按接口实际返回验证 10013、10014、10019 的安全分支，不保存敏感正文 |
| 生产 Agent 主链路 | `BLOCKED_INPUT` | Spark Assistant 结果不等于 Xingchen Workflow、知识库来源、正式角色和课程数据验收 |

当前判定：Spark 正向、离线契约和四类参数负向为 `OBSERVED_PASS`，但远端鉴权负向为 `FAIL`；`BUILD-090 = IMPLEMENTED_PENDING_GATE`。在解释并修复错误凭据仍返回最终 `header.code=0` 前，不得标记 Spark `API_PASS`。限流、并发、异常恢复、内容审核、Adapter SSE 集成、正式 Workflow 性能、课程 PDF、真实角色和正式 API 证据仍未完成。

## 43. 2026-07-25 本地 API 契约和测试配置归档审查

为推进第 21.2 节要求的可复现测试输入，本轮新增根目录 `api-test-manifest.yaml` 和 `openapi.test.json`。两份文件明确标记为 `local-isolated-adapter`，不声称是 Moodle 正式 API，也不包含账号、Token、Cookie 或真实课程数据。

### 43.1 生成与校验

- `scripts/generate_local_openapi.py` 从当前 Adapter 应用生成 OpenAPI 文档；本次生成 `73` 个路径。
- `scripts/test_api_contract.py` 现在同时校验 Python 路由集合、Caddy `/api/*` 代理、`deploy/.env.example` 和本地 OpenAPI 的环境标记/必需路径。
- `api-test-manifest.yaml` 固化 Mock Auth、Mock Workflow、临时 SQLite、临时资源目录、课程 PDF 缺失状态、证据脱敏规则和本地测试命令。

### 43.2 当前结果

| 检查 | 结果 | 边界 |
|---|---|---|
| `python3 scripts/test_api_contract.py` | `API_CONTRACT_OK routes=74` | `PASS`，本地代码/部署契约 |
| `python3 scripts/generate_local_openapi.py` | `LOCAL_OPENAPI_EXPORTED paths=73` | `PASS`，生成物来自当前代码 |
| YAML/JSON 解析 | 17 个配置/证据文件通过 | `PASS` |
| 正式 Moodle OpenAPI、角色和重置夹具 | 未提供 | `BLOCKED_INPUT`，不能用本地契约替代 |

### 43.3 审查结论

本地 API 验收现在具备可复现 manifest 和生成式 OpenAPI 入口；`PLAN-EVIDENCE-001` 的本地证据缺口已处理，但正式外部 API 契约仍保持开放。任何真实 API 批次必须以外部提供的版本化 OpenAPI、角色引用、固定夹具和重置方法覆盖本地文件，并重新执行第 27 节 T0-T6 流程。

## 44. 2026-07-25 Spark 鉴权负向失败复审与发布阻断

本节记录第 42 节之后的鉴权负向复测。测试只读取 `.env.test.local`，对三个变体各发送一次固定、无个人数据的最小业务帧：错误 API Key、错误 API Secret、篡改签名 date。响应正文从未输出或归档。

### 44.1 观察结果

| 用例 | 预期 | 实际 | 判定 |
|---|---|---|---|
| 错误 API Key | 非零鉴权错误 | WebSocket 101；8 帧；最终 `header.code=0` | `FAIL` |
| 错误 API Secret | 非零鉴权错误 | WebSocket 101；8 帧；最终 `header.code=0` | `FAIL` |
| 篡改签名 date | 非零签名错误 | WebSocket 101；8 帧；最终 `header.code=0` | `FAIL` |

### 44.2 安全处置

- 该结果不能被解释为本地 Adapter 的鉴权通过，也不能被忽略为“握手成功即可”；它表示当前测试端点对三类鉴权变体未返回计划规定的错误。
- 在供应方确认端点、Assistant、签名版本和测试凭据绑定关系前，不继续增加错误凭据请求，不把 Spark 直连纳入生产主链路，也不把结果写成 `OBSERVED_PASS`。
- 需要用供应方确认的测试端点和版本化协议重新执行 `SPARK-AUTH-002`、`SPARK-AUTH-003`；若仍返回最终 `header.code=0`，必须按安全缺陷处理并停止发布。

当前结论：Spark 参数/字段负向为 `OBSERVED_PASS`，远端鉴权负向为 `FAIL`；`SPARK-AUTH-002/003` 和 `BUILD-090` 保持未关闭，最终发布继续阻断。

## 45. 2026-07-25 BUILD-070 六视口截图夹具复审

为处理第 27.4 节和 `BUILD070-T4-001`，新增 `frontend/playwright.screenshots.config.ts` 与 `frontend/tests/screenshots.spec.ts`。夹具使用 Mock Auth、隔离 SQLite 和临时资源目录，覆盖 student dashboard、teacher resources、admin knowledge base 三个页面，以及 390、412、768、1024、1280、1440 六个 CSS 视口。

### 45.1 执行结果

| 检查 | 结果 | 判定 |
|---|---|---|
| 页面角色/标题断言 | 三类页面均进入并通过可见性断言 | `OBSERVED_PASS` |
| 横向溢出断言 | 三类页面六视口均通过到截图步骤 | `OBSERVED_PASS` |
| Chrome `page.screenshot` | 字体加载完成后超时；重试 viewport-only、禁用动画后仍超时 | `BLOCKED_TEST_INFRA` |
| 图片证据归档 | 0 个文件生成 | `BLOCKED_TEST_INFRA` |

### 45.2 复审结论

该夹具证明页面流程可以进入目标状态，但没有生成图片，不能满足 T4 截图证据条件。当前 `BUILD-070-T4-001 = BLOCKED_TEST_INFRA`，不是 `PASS` 或 `OBSERVED_PASS`。必须在 Chromium screenshot compositor 可用的环境重新执行并检查六组截图后，才能把本地 T4 证据升级；真实角色截图和人工验收仍另行阻断。

## 46. 2026-07-25 BUILD-070 T4 截图 CDP 复测通过

第 45 节的 Playwright `page.screenshot` 封装在当前 Chrome 环境超时。为获得可审查的浏览器证据，保留相同页面、角色、视口和断言，改用 Chrome DevTools Protocol 的 `Page.captureScreenshot` 直接保存 PNG；这不是静态 HTML 截图，也没有改变业务数据或 Mock 边界。

### 46.1 当前结果

| 项目 | 结果 |
|---|---|
| 命令 | `cd frontend && npm run test:screenshots -- --workers=1` |
| Playwright 测试 | `1 passed`，48.2s |
| 页面 | `student-dashboard`、`teacher-resources`、`admin-knowledge-bases` |
| 视口 | 390、412、768、1024、1280、1440 |
| 文件 | 18 个 PNG，均已写入 `acceptance/frontend/BUILD-070/screenshots/` |
| 尺寸 | 390x844、412x915、768x1024、1024x900、1280x900、1440x900 |
| 视觉抽查 | 学生移动端、教师桌面端、管理员平板端非空且无明显重叠 |

### 46.2 门禁边界

当前 `BUILD070-T4-001 = OBSERVED_PASS(local-mock-cdp)`，不等于正式 `PASS`。正式关闭 BUILD-070 仍需要真实 student/teacher/admin 会话、真实课程资料、正式 API、人工键盘/可访问性检查和真实角色截图；第 45 节的截图 API 超时作为历史基础设施记录保留。

## 47. 2026-07-25 BUILD-100 axe 可访问性扫描与依赖审计复审（历史快照）

本轮为前端加入 `@axe-core/playwright@4.12.1` 和 `npm run test:axe`。扫描覆盖最小引擎探针、student dashboard、teacher resources 和 admin knowledge base 的渲染 `<main>` 内容。

### 47.1 axe 结果

| 检查 | 结果 | 边界 |
|---|---|---|
| axe 引擎最小探针 | 1 passed | 证明依赖可执行；探针包含 `title` 和 `lang` |
| 学生/教师/管理员主内容 | 3 passed | 扫描规则集无违规 |
| `color-contrast` | 未纳入本次 axe 规则集 | 完整规则在 Chrome 147 + axe 4.12.1 中超时；现有自定义对比度检查 3/3 继续执行 |
| 真实角色和人工辅助技术 | `BLOCKED_INPUT` | 仍缺 Moodle 角色、屏幕阅读器和人工键盘证据 |

当前判定：该节记录的是依赖迁移前的历史快照。`npm run test:axe` 当时为 `OBSERVED_PASS_AXE_SUBSET`，不能写成完整 axe `PASS`；当前结果以第 50 节为准。

### 47.2 依赖安全审计

该节记录的是依赖迁移前的 `npm audit --json` 快照：`7 high / 0 critical`。后续已移除 `react-router-dom` 并完成 ESLint 10 迁移；当前安全审计和回归结果以第 50 节为准。

## 48. 2026-07-25 测试方案写入后的二次审查与当前复测（历史快照）

本节记录依赖迁移前的计划复审快照；后续端口隔离、夹具隔离和当前状态以第 51 节和进度账本中的最新 `test_runs` 为准。

### 48.1 测试方案一致性审查

| 审查项 | 当前结果 | 判定 |
|---|---|---|
| 每次构建后的固定顺序 | 第 27.2 节已明确冻结范围、代码审查、静态门禁、局部测试、API、浏览器、质量测试和证据归档 | `PASS` |
| T0-T6 覆盖 | 第 27.1 节为每个批次定义最低输出和关闭条件 | `PASS` |
| API 强制测试集合 | 第 27.3 节覆盖正向、鉴权、对象权限、输入边界、幂等并发、状态持久化、上游恢复、审计清理 | `PASS` |
| 浏览器证据边界 | 第 27.4 节强制记录角色、视口、环境、截图和失败/恢复流程，并明确 Mock 不能替代真实角色 | `PASS` |
| 状态语义 | 第 27.5 节明确 `PASS`、`OBSERVED_PASS`、`REVIEW_REQUIRED`、`BLOCKED_*` 和 `FAIL` 的关闭规则 | `PASS` |
| 计划、实现、证据数量 | 当前 API 契约 74 路由、单元 21 通过/3 跳过、组件 2 通过、Mock 浏览器 16/16、axe 4/4；自定义可访问性当前 1/3 | `REVIEW_REQUIRED` |
| 正式输入和外部环境 | 课程 PDF、Moodle 三角色、正式 API 契约、真实 Workflow、Docker 基础镜像和正式 HTTPS 仍缺失 | `BLOCKED_INPUT` / `BLOCKED_EXTERNAL` |

结论：测试方案已写入计划并通过结构一致性复审；其“可执行”不等于“所有批次已通过”。所有局部结果仍必须使用环境限定，不能升级为正式 `PASS`。

### 48.2 当前工作区复测

以下命令中，静态和隔离回归命令在当前复测退出码为 0；标准 smoke 和自定义可访问性分别记录失败，不把失败结果写成通过。真实凭据未被命令输出或证据归档：

```text
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run test:unit -- --run
cd frontend && npm run test:component -- --run
cd frontend && npm run test:hardening -- --run
cd frontend && npm run build
cd frontend && npm run test:axe -- --workers=1
python3 scripts/test_api_contract.py
python3 scripts/test_ui_contract.py
python3 -m compileall -q agent-adapter scripts
bash -n scripts/*.sh
git diff --check
python3 -c 'import yaml, json; yaml.safe_load(open("PROJECT_PROGRESS.yaml")); json.load(open("openapi.test.json")); print("FINAL_YAML_JSON_PARSE_OK")'
cd frontend && npm audit --json
```

结果摘要：lint、typecheck、硬化测试 `2/2`、单元 `21 passed / 3 skipped`、组件 `2/2`、生产构建 `1694 modules`、Mock 浏览器 `16/16`、API 契约 `routes=74`、UI 契约、Python 编译、Shell 语法和差异检查通过；axe 在允许本地端口的环境中 `4/4` 通过。自定义 `test:a11y` 为 `1 passed / 2 failed`，两个失败场景进入 ErrorBoundary；标准 `test:e2e` 未找到学生标题并失败。两者都不能升级为 `PASS`，也不能用 Mock 结果替代真实角色和人工验收。

依赖迁移后的在线 `npm audit --json` 已记录为 `0 vulnerabilities`；本轮受执行环境网络策略限制未重复发送审计请求，不能把离线 advisory 不完整时的 `0` 当作在线证据。依赖门禁以迁移后的在线结果、lockfile 和完整回归为准。

### 48.3 二次审查开放项

1. `DATA-INPUT-001`：恢复与 manifest 的 hash/page_count 匹配的 20 个 PDF，禁止生成占位文件。
2. `PLAN-EVIDENCE-001`：用正式版本化 Moodle API/OpenAPI、角色引用、固定夹具和可重置 namespace 替换当前 local-isolated-adapter 输入。
3. `SPARK-AUTH-FAIL-001`：由供应方确认端点、Assistant、签名版本和凭据绑定后，重新执行错误凭据鉴权；当前三类错误凭据仍返回最终 `header.code=0`，发布继续阻断。
4. `FRONTEND-AUDIT-001`：依赖迁移、在线审计和回归已完成；后续依赖变更必须重新打开该门禁，不得使用 `--force` 绕过 major 版本风险。
5. `FRONTEND-A11Y-001`：在兼容环境完成完整 `color-contrast`/axe 规则、真实三角色、键盘和屏幕阅读器证据；当前 axe 结果仍为子集观察性通过。
6. `FRONTEND-CONTAINER-001` 及发布门禁：取得 Docker 基础镜像后完成容器健康检查、正式 HTTPS、服务器恢复、六视口人工截图和 T0-T6 复审。

### 48.4 当前门禁判定

- `BUILD-000 = BLOCKED_INPUT`。
- `BUILD-070 = IMPLEMENTED_PENDING_GATE`；STAFF-010 仍为 `OBSERVED_PASS(local-isolated-api + mock-browser)`。
- `BUILD-090 = IMPLEMENTED_PENDING_GATE`；Spark 鉴权负向失败不能升级为通过。
- `BUILD-100 = IMPLEMENTED_PENDING_GATE`；本地硬化和 axe 子集通过不等于正式发布门禁通过。
- 最终发布继续为 `blocked`。

只有第 27.5 节规定的全部适用测试 ID、真实角色、真实课程数据、正式 API、可访问性、部署、恢复和证据条件均为 `PASS`，才允许关闭批次或宣称学习通平台正式验收完成。

## 49. 2026-07-25 BUILD-050 ASSESS-015 多标签草稿浏览器验收

本节补齐 BUILD-050 原先缺失的浏览器级多标签场景。测试使用隔离 Mock API，不改变生产代码中的服务端版本保护；真实 Moodle 多标签流程仍需正式角色和真实时间环境复验。

### 49.1 场景和验收条件

- 两个 student 浏览器标签同时打开同一作业，服务端均返回草稿 `version=0`。
- 标签 A 选择“服务端版本保护”，自动保存成功并生成 `version=1`。
- 标签 B 使用旧 `base_version=0` 选择“直接覆盖”，服务端返回 `409 assignment_draft_conflict`，页面显示“版本冲突”。
- 服务端最终答案保持标签 A 的内容；测试记录两个请求的 `base_version` 均为 `0`，不产生第二个服务端版本。

### 49.2 构筑后测试

```text
cd frontend && npm run test:e2e:mock -- --workers=1 --grep "two student tabs"
cd frontend && npm run test:e2e:mock -- --workers=1
```

首次运行在进入自定义作业页面前失败，原因是测试夹具使用过宽的 URL 通配模式，未拦截详情请求；该失败不计为业务通过。将作业详情和草稿接口拆为两个明确路由后，在允许本地监听的环境重测：`1 passed`。

随后执行批次全量 Mock 浏览器回归：`16 passed`，包含学生、教师、管理员、资源阅读状态、作业提交、讨论、通知、课堂活动、教师工作台、知识库、Agent 上下文/情景、学习图谱和 ASSESS-015 多标签冲突流程。

### 49.3 证据和门禁

- 证据：`frontend/tests/mock-api.spec.ts`、`acceptance/frontend/BUILD-050/test-output.txt`、`manual-acceptance.md` 和 `review.md`。
- `ASSESS-015 = OBSERVED_PASS(local-mock-browser)`；该结果证明前端能展示版本冲突，不能替代正式 Moodle 多标签验收。
- `BUILD-050` 继续为 `IMPLEMENTED_PENDING_GATE`，剩余阻断为真实 Moodle 成绩回写、正式截止时间/时钟环境、三角色浏览器和正式 API/课程数据。

## 50. 2026-07-25 依赖硬化复审、标准 smoke 复测与测试方案再审查（首次失败快照）

本节记录依赖迁移后的首次复测结果，其中保留了 stale server 和固定测试数据库造成的失败。后续修复和当前权威结果见第 51 节；本节不把本地 Mock、预览态或错误边界结果升级为真实角色验收。

### 50.1 依赖迁移结果

| 项目 | 当前结果 | 关闭条件/边界 |
|---|---|---|
| Router | `react-router@8.3.0`；已移除 `react-router-dom` | 仅使用客户端 `BrowserRouter`；不得启用 SSR、RSC 或 Server Actions |
| ESLint | `eslint@10.8.0`、`@eslint/js@10.0.1`、`eslint-plugin-react-hooks@7.1.1` | `npm run lint` 必须零 warning、零 error |
| 类型和构建 | lint、typecheck、生产构建通过；`1694 modules transformed` | 构建产物、`/learn/` base path 和 Admin 独立 chunk 均需复核 |
| 在线依赖审计 | `0 vulnerabilities` | 该结果来自依赖迁移后的在线审计记录；网络不可用时不得用离线 `0` 替代 |

### 50.2 每次构筑后的固定复审协议

每个 BUILD 批次完成实现后，必须按 T0 到 T6 顺序执行；同一批次修复失败项后不得只重跑单个命令就宣称通过。

| 层级 | 构筑后动作 | 必须通过的验收条件 | 失败后的重测范围 |
|---|---|---|---|
| T0 输入与范围 | 对照 scope、API diff、权限矩阵、迁移和回退点；检查 manifest、夹具和 secret 脱敏 | 范围冻结，输入可复现，无占位课程文件，无凭据进入证据 | 输入、API、权限或迁移变化时重跑 T0-T6 |
| T1 静态质量 | `lint`、`typecheck`、Python 编译、Shell 语法、契约/格式检查、`git diff --check` | 零错误；接口字段和错误包络与契约一致 | 生产代码或配置变化时重跑 T1-T6 |
| T2 局部行为 | 单元、组件、硬化测试；覆盖状态机、错误态、幂等、版本冲突和敏感信息 | 相关测试全部通过；跳过项必须有明确外部输入记录 | 业务逻辑变化时重跑 T2-T6 |
| T3 API/数据 | API 契约、角色权限、输入边界、并发、持久化、回写、审计和清理 | 正向及适用负向全部通过；无跨课程、跨用户或重复写入 | API、store、权限或数据变化时重跑 T3-T6 |
| T4 浏览器 | Mock 角色矩阵、标准 smoke、六视口、错误/空态、刷新/断网/会话过期 | student/teacher/admin 流程均有环境标识；页面无错误边界、重叠和不可操作溢出 | 路由、UI、API mock 或浏览器配置变化时重跑 T4-T6 |
| T5 质量与恢复 | axe、手工键盘、对比度、性能、上游超时/断流、容器、备份恢复 | 本地观察结果和正式结果分开；正式门禁不得用 Mock 替代 | 安全、部署、缓存、性能或错误处理变化时重跑 T5-T6 |
| T6 证据和签核 | 更新 `metadata.json`、`scope.md`、`review.md`、`test-output.txt`、截图和回退说明 | 命令、退出码、版本、视口、环境、缺陷和阻断项可追溯 | 任何测试结果或状态变更都需重签该批次 |

重测规则：修复只影响文档时重跑 T6，并重新解析 YAML/JSON；修复依赖、路由、API、权限、构建配置或测试夹具时，至少重跑受影响层及其下游层，默认按 T1-T6 全量复测。任何 `FAIL`、`REVIEW_REQUIRED` 或 `BLOCKED_*` 都阻止批次升级为正式 `PASS`。

### 50.3 当前复测结果

| 命令/场景 | 结果 | 证据边界 |
|---|---|---|
| `npm run lint` | `PASS` | ESLint 10 迁移后通过 |
| `npm run typecheck` | `PASS` | TypeScript 项目检查通过 |
| `npm run test:unit -- --run` | `21 passed / 3 skipped` | 跳过项仍按外部依赖记录，不作为失败替代 |
| `npm run test:component -- --run` | `2 passed` | 组件交互通过 |
| `npm run test:hardening -- --run` | `2 passed` | ErrorBoundary 和客户端诊断边界通过 |
| `npm run build` | `PASS; 1694 modules` | `/learn/` 生产构建通过 |
| `npm run test:e2e:mock -- --workers=1` | `16 passed` | 隔离 Mock API；不等于真实 Moodle |
| `npm run test:axe -- --workers=1` | `4 passed` | axe 主内容子集；`color-contrast` 仍未纳入 |
| `npm run test:a11y -- --workers=1` | `1 passed / 2 failed` | 两个用例进入 ErrorBoundary；正式可访问性门禁保持开放 |
| `npm run test:e2e -- --workers=1` | `FAIL` | 标准 smoke 未找到 `早上好，林同学`；当前配置没有可用认证/Adapter 前置，不能记为布局 PASS |

### 50.4 进一步审查发现

1. 依赖风险已从旧的 `7 high` 快照修复为 `0 vulnerabilities`；旧数字只能保留在历史章节，不能继续出现在当前门禁摘要。
2. Mock 浏览器已从 `13/13` 复测为 `16/16`，包含 ASSESS-015 多标签版本冲突；真实角色和 Moodle 回写仍未验收。
3. `test:a11y` 当前两个失败场景显示 ErrorBoundary，而不是预期的预览态/学习图谱页面。必须先确定是测试配置缺少 API 前置还是页面真实回归，再重新执行 `3/3`；在此之前不得写成 `OBSERVED_PASS`。
4. 标准 smoke 的认证前置没有显式写入配置。应补充专用认证夹具，或把该脚本改成明确断言未认证错误态；不能要求无认证环境出现学生登录后的标题。
5. 完整 axe `color-contrast`、真实三角色、六视口人工检查、真实课程 PDF、正式 API、Docker/HTTPS、备份恢复和真实 Workflow 仍是外部门禁。

### 50.5 当前门禁结论和关闭条件

- `FRONTEND-AUDIT-001 = CLOSED`：Router 8、ESLint 10、在线审计 0 和回归证据已形成闭环。
- `FRONTEND-A11Y-001 = OPEN`：完整 axe、对比度、真实角色、键盘和屏幕阅读器证据仍缺失。
- 新增 `FRONTEND-A11Y-002 = OPEN`：当前 `test:a11y` 为 `1/3`，需修复测试前置或页面回归并重测 `3/3`。
- 新增 `FRONTEND-SMOKE-001 = OPEN`：标准 smoke 必须拥有可复现认证夹具并通过，或改为明确的未认证错误态测试。
- `BUILD-100` 继续为 `IMPLEMENTED_PENDING_GATE`；本地硬化、Mock 和依赖审计通过不等于正式发布通过。

只有 T0-T6 全部满足、上述两个新增前端门禁关闭，并完成真实角色、课程数据、正式 API、部署和恢复验收，才允许把 BUILD-100 或最终发布标记为 `PASS`。

## 51. 2026-07-25 前端测试隔离修复后的构筑复审

本节覆盖第 50 节开放问题的修复和重测，是当前本地前端门禁的权威状态。

### 51.1 修复内容

- `playwright.config.ts` 和 `playwright.a11y.config.ts` 使用独立的 `4193/4194` 端口，并设置 `reuseExistingServer: false`，不再复用旧 Vite 进程。
- `playwright.mock.config.ts` 和 `playwright.axe.config.ts` 使用独立的固定专用端口；每次配置进程生成唯一 `COURSE_DB` 和 `RESOURCE_STORAGE_DIR`，避免跨运行残留课程资源和版本记录。
- 保留学生预览态、错误态、学习图谱和真实 Mock 角色的原有断言，不通过放宽断言来获得绿色结果。

### 51.2 根因审查

| 问题 | 根因 | 修复验证 |
|---|---|---|
| `test:a11y` 为 1/3 | `reuseExistingServer` 复用了旧端口上的 Vite 实例，页面进入 ErrorBoundary | 新隔离端口重测 `3/3` |
| 标准 smoke 失败 | 同一 stale server 问题，未访问当前代码实例 | 新隔离端口重测 `1/1` |
| Mock STAFF-010 偶发命中旧版本 | Mock API 使用固定 SQLite 和资源目录，跨运行保留旧资源 | 独立数据库/目录重测全量 `16/16` |
| worker 地址不一致 | 用 `process.pid` 同时生成 webServer 端口和 worker `baseURL`，两者进程号不同 | 改为固定专用端口，重测通过 |

### 51.3 当前 T1-T6 结果

| 层级 | 当前结果 | 证据 |
|---|---|---|
| T1 静态质量 | `PASS` | lint、typecheck、API `74` 路由、UI 契约、Python 编译、Shell 语法、`git diff --check` |
| T2 局部行为 | `PASS` | Vitest 全量 `24/24`；定向单元 `21 passed / 3 skipped`、组件 `2 passed`、硬化 `2 passed` |
| T3 API/数据 | `PASS`（隔离环境） | Mock Adapter 独立数据库、既有 API/权限/幂等夹具 |
| T4 浏览器 | `OBSERVED_PASS` | Mock `16/16`、a11y `3/3`、标准 smoke `1/1`；真实 Moodle 角色仍未验收 |
| T5 质量 | `OBSERVED_PASS` / `BLOCKED_INPUT` | axe 默认规则集主内容扫描 `4/4`，包含 `color-contrast`；人工辅助技术、容器、恢复和真实 Workflow 仍开放 |
| T6 证据 | `PASS` | 本节、进度 YAML、BUILD-100 `test-output.txt`、`review.md` 和 `metadata.json` 已更新 |

### 51.4 当前门禁结论

- `FRONTEND-AUDIT-001 = CLOSED`。
- `FRONTEND-A11Y-002 = CLOSED`：当前自定义 `test:a11y` 为 `3/3`。
- `FRONTEND-SMOKE-001 = CLOSED`：标准 smoke 为 `1/1`，使用隔离专用端口。
- `BUILD-100` 仍为 `IMPLEMENTED_PENDING_GATE`，原因是真实三角色、课程 PDF、正式 API、Docker/HTTPS、服务器恢复、六视口人工证据和真实 Workflow 仍未完成；本地 axe 主内容默认规则集（含 `color-contrast`）已通过 `4/4`。
- `BUILD-000` 继续因 manifest 要求的 20 个课程 PDF 缺失而 `BLOCKED_INPUT`；最终发布仍为 `blocked`。

只有真实外部门禁和正式证据全部满足，才允许把本地观察性通过升级为正式发布 `PASS`。

## 52. 2026-07-25 对比度修正后的最终本地复测与计划再审查

本节覆盖第 51 节之后的最后一轮本地复测，作为当前前端 T1-T5 结果的最新记录；第 47、48、50 节中的超时、端口复用和筛选测试失败均保留为历史快照，不得覆盖本节结果。

### 52.1 本轮修正和审查发现

- 将 `frontend/src/styles.css` 的 `--muted` 从 `#7b898e` 调整为 `#5c686c`，将 `--warm` 从 `#b8602e` 调整为 `#8f451f`，修复真实 axe 对比度检查暴露的低对比度风险。
- 在 `frontend/package.json` 增加 `test:all`，执行全部 Vitest 文件；`test:unit`、`test:component`、`test:hardening` 继续保留为定向门禁，但其 skipped 数量不得被解释为全量覆盖。
- `playwright.axe.config.ts` 的 axe 运行使用 legacy frame 模式，但没有禁用 `color-contrast`；当前结论限定为每个 student/teacher/admin 页面渲染 `<main>` 的默认 axe 规则集扫描，不宣称整站、跨域 iframe 或真实角色人工验收完成。

### 52.2 当前固定命令和结果

以下命令均在允许回环监听的隔离测试环境执行；命令没有输出或归档凭据值、Cookie、签名 URL、完整问题和回答：

| 层级 | 命令/结果 | 退出码 |
|---|---|---:|
| T1 | `git diff --check`、`bash -n scripts/*.sh`、`python3 -m compileall -q agent-adapter scripts`、`python3 scripts/test_api_contract.py`（`routes=74`）、`python3 scripts/test_ui_contract.py`、`python3 scripts/test_frontend_hardening.py` | 0 |
| T1 | `cd frontend && npm run lint`、`npm run typecheck`、`npm run build`（`1694 modules transformed`） | 0 |
| T2 | `cd frontend && npm run test:all`（`5 files / 25 tests passed`） | 0 |
| T2 | 定向门禁：`test:unit` `21 passed / 3 skipped`；`test:component` `2 passed / 22 skipped`；`test:hardening` `2 passed / 22 skipped` | 0 |
| T4 | `cd frontend && npm run test:e2e:mock -- --workers=1`（`16/16`）、`npm run test:a11y -- --workers=1`（`3/3`）、`npm run test:e2e -- --workers=1`（`1/1`） | 0 |
| T5 | `cd frontend && npm run test:axe -- --workers=1`：探针、student、teacher、admin 共 `4/4`；扫描 `<main>`，默认规则集包含 `color-contrast`，无 violation | 0 |

### 52.3 再审查后的门禁判定

- 本地 T1、全量 T2、隔离 API/T3、Mock/预览 T4 和 axe 主内容扫描均达到本轮命令的退出码 0；`test:all` 关闭了此前定向测试 skipped 造成的全量覆盖歧义。
- `FRONTEND-A11Y-001` 的本地 axe 规则执行部分已完成；真实 Moodle 三角色、人工键盘/屏幕阅读器、六视口人工截图和正式环境辅助技术验收仍保持开放，不能关闭整个正式可访问性门禁。
- `BUILD-100` 继续为 `IMPLEMENTED_PENDING_GATE`，而不是正式 `PASS`。当前仍阻断的条件包括课程 PDF、正式 Moodle API/角色、真实 Workflow、Docker/NginX 运行证据、正式 HTTPS、服务器备份恢复和正式人工 T4/T5 证据。
- `BUILD-000` 继续因 manifest 要求的 20 个课程 PDF 缺失而 `BLOCKED_INPUT`；不得用占位文件、Mock 结果或本地截图替代。

### 52.4 后续构筑的强制复测条件

任何修改 React 页面、样式、路由、依赖、Playwright 配置或 Adapter 契约后，必须重新执行 `test:all`、定向 T2、Mock `16/16`、a11y `3/3`、标准 smoke `2/2` 和 axe `4/4`；若改动资源、权限、API 或部署，则按第 27 节从受影响的 T1/T3/T4/T5 层重新执行，并更新对应 BUILD 证据目录。只有真实输入和外部环境阻断项全部解除后，才能把 `OBSERVED_PASS` 升级为正式 `PASS`。

## 53. 2026-07-25 BUILD-100 全局壳层功能实现与构筑后审查

本次增量补齐全局壳层中原先无效的搜索、帮助和设置入口，范围限定为前端导航与本机偏好，不改变 Moodle、成绩、资源文件或 Agent 服务端契约。

### 53.1 实现范围

- 全局搜索框提交到 `/search?q=...`，可检索当前课程的章节、资料、任务、学习知识点和服务端知识图谱结果；结果保留课程上下文并可跳转到对应页面。
- 新增 `/help` 帮助中心，提供课程、资料、任务和 Agent 的可操作入口；移除原先 `window.alert` 占位行为。
- 新增 `/settings` 学习设置，支持通知提醒、阅读进度自动保存和增强文字对比度；偏好只写入本机 `localStorage`，不保存 API Key、API Secret、Cookie、Session 或成绩。
- 新增用户菜单，支持进入学习记录、学习设置和退出课程；真实模式跳转 Moodle 登出端点，预览模式只清理前端会话并返回预览首页。
- 课程搜索结果可以通过 `chapter_id` 进入对应章节；高对比度设置使用 `data-contrast` 作用于当前文档根节点。

### 53.2 构筑后代码审查

| 审查项 | 结果 | 结论 |
|---|---|---|
| 搜索权限边界 | `PASS` | 页面只使用已加载的课程数据；实时知识点搜索仍通过 Adapter API，未新增前端直连外部服务 |
| 导航可恢复性 | `PASS` | 搜索、帮助和设置均为可复制 URL，刷新后可重新进入 |
| 本机偏好边界 | `PASS` | 只保存三个布尔偏好；显式禁止凭据和成绩写入设置页面 |
| 会话退出边界 | `PASS` | 清理前端 Zustand 会话；真实模式使用服务端 Moodle 登出 URL，未把退出状态伪装为本地成功 |
| 预览/真实数据边界 | `PASS` | 预览使用本地示例数据，真实模式的知识点搜索失败时显示有限本地结果，不伪造成功 |
| 移动端和键盘 | `PASS` | 表单有标签和按钮名称，搜索结果、帮助入口和复选框可键盘操作 |

### 53.3 当前构筑测试结果

| 层级 | 结果 | 证据 |
|---|---|---|
| T1 | `PASS` | `npm run lint`、`npm run typecheck`、生产构建 `1694 modules` |
| T2 | `PASS` | Vitest 全量 `25/25`；新增搜索/帮助/设置组件验收 |
| T4 | `OBSERVED_PASS` | 标准 smoke `2/2`；Mock 浏览器 `16/16` |
| T5 | `OBSERVED_PASS` | 自定义 a11y `3/3`、axe 主内容默认规则集 `4/4`（含 `color-contrast`） |
| T6 | `PASS` | 本节、BUILD-100 `test-output.txt`、`review.md`、`metadata.json` 和 `PROJECT_PROGRESS.yaml` 已同步 |

### 53.4 门禁结论

本地壳层增量达到 `OBSERVED_PASS`，但 `BUILD-100` 仍为 `IMPLEMENTED_PENDING_GATE`。真实 Moodle 三角色、课程 PDF、正式 API、Docker/Nginx、HTTPS、服务器恢复、人工辅助技术和真实讯飞 Workflow 仍是正式关闭条件；本次本地功能不得升级为正式发布 `PASS`。

## 54. 2026-07-25 BUILD-100 退出课程路径复测与计划终审

本节记录第 53 节之后对用户菜单“退出课程”流程的构筑后复测。复测发现测试断言把预览态行为错误地当成真实会话行为，已修正测试而未放宽产品边界。

### 54.1 发现、修复和审查结论

| 项目 | 首次结果 | 修复/终审结论 |
|---|---|---|
| 预览会话退出 | 失败快照未覆盖 | `clearSession()` 后回到 `/`，必须看到“早上好，林同学” |
| 真实会话退出 | 实现跳转 `/login/logout.php?sesskey=...`，旧断言错误期待首页 | 测试校验 Moodle 登出端点和非空 `sesskey`，不把本地页面显示当成登出成功 |
| 标准 smoke | 首次 `1/2`，失败为断言目标错误 | 修复分支断言后 `2/2`，覆盖两种合法运行环境 |
| 计划一致性 | 计划已要求预览/真实边界，但未写明 smoke 的双路径期望 | 已将环境前置、期望结果、失败后重测和证据归档写入本节及 BUILD-100 证据 |

### 54.2 退出课程验收方案

构筑后标准 smoke 必须先等待首页工作台稳定，再打开用户菜单并点击“退出课程”。验收根据会话环境选择唯一合法结果：

- 预览或 Adapter 不可用：前端会话被清理，URL 回到 `/learn/`，首页标题可见，预览提示仍可解释当前数据来源。
- 真实或 Mock Adapter 会话：浏览器 URL 必须匹配 `/learn/login/logout.php?sesskey=<非空值>`；测试不得把 Vite 的回退 HTML 当作已登录首页，也不得记录 token、Cookie 或完整 URL 参数值。

该流程的代码审查条件为：退出前端状态清理、真实模式调用服务端登出、预览模式不伪造服务端登出、两条路径均无凭据写入证据。若路由、会话初始化、测试配置或登出行为变更，必须重跑 T1-T6；仅修改断言时至少重跑 T4-T6，并重新解析 YAML/JSON 和执行 `git diff --check`。

### 54.3 当前终审结果

| 层级 | 结果 | 验收边界 |
|---|---|---|
| T1 | `PASS` | lint、typecheck、构建、契约、硬化和 diff 检查保持通过 |
| T2 | `PASS` | Vitest 全量 `25/25` |
| T3 | `PASS`（隔离 Mock） | 既有 API、权限、CSRF、幂等和数据边界不变 |
| T4 | `OBSERVED_PASS` | 标准 smoke `2/2`；预览首页和真实/MOCK 登出 URL 分支均覆盖，Mock 浏览器 `16/16`、自定义 a11y `3/3` |
| T5 | `OBSERVED_PASS` / `BLOCKED_INPUT` | axe `4/4` 和本地对比度通过；正式角色、人工辅助技术、容器、HTTPS、恢复仍未验收 |
| T6 | `PASS` | 计划、进度账本和 BUILD-100 证据已同步，未记录任何密钥或会话值 |

计划终审结论：测试方案已具备逐构筑的 T0-T6 执行顺序、环境前置、双路径退出验收、失败后的重测范围和证据归档要求；`BUILD-100` 仍为 `IMPLEMENTED_PENDING_GATE`，`BUILD-000` 仍为 `BLOCKED_INPUT`，正式发布继续 `blocked`。

## 55. 2026-07-25 BUILD-060 历史证据清理与当前门禁复测

本节将 BUILD-060 验收目录中落后的 `NOT_IMPLEMENTED`、早期 `8/8` 快照和受限环境 `EPERM` 与当前结果分层，避免历史失败覆盖现行状态。历史记录保留用于追溯，当前结果以本节、`PROJECT_PROGRESS.yaml` 和 BUILD-060 目录末尾的最新记录为准。

### 55.1 本轮复测命令和结果

| 层级 | 命令/场景 | 当前结果 |
|---|---|---|
| T2/T3 | `scripts/test_social_api.py` | `PASS / SOCIAL_API_OK` |
| T2/T3 | `scripts/test_activity_api.py` | `PASS / ACTIVITY_API_OK` |
| T1 | `test_api_contract.py`、`test_ui_contract.py`、`test_frontend_hardening.py` | `PASS / routes=74 / UI_CONTRACT_OK / FRONTEND_HARDENING_OK` |
| T2 | `cd frontend && npm run test:all` | `PASS / 5 files / 25 tests` |
| T4 | `npm run test:e2e:mock -- --workers=1` | `OBSERVED_PASS / 16/16`，隔离 Mock API |
| T4/T5 | `npm run test:a11y -- --workers=1` | `OBSERVED_PASS / 3/3`，隔离专用端口 |
| T4 | `npm run test:e2e -- --workers=1` | `OBSERVED_PASS / 2/2`，响应式和全局壳层流程 |

### 55.2 证据修正和审查结论

- BUILD-060 的 `accessibility_automation` 已从历史 `NOT_IMPLEMENTED` 修正为当前共享门禁 `OBSERVED_PASS_3_TESTS`；这不等于正式 axe 或屏幕阅读器验收。
- BUILD-060 的当前 Mock/浏览器证据更新为共享隔离结果 `16/16` 和 `2/2`；早期 `8/8` 与 `EPERM` 仍保留在 test-output 历史段落中，不再作为当前状态。
- 社交与活动 API 的对象归属、角色权限、纯文本输入、CSRF、幂等、审计、一次性提交和结果聚合保持通过；本轮没有修改业务数据或权限逻辑。
- 当前结果不关闭真实 Moodle 三角色、正式 API/OpenAPI、课程 PDF、正式审计、正式可访问性和完整 local acceptance 门禁。

### 55.3 当前验收状态

| 项目 | 状态 | 关闭条件 |
|---|---|---|
| BUILD-060 本地实现和隔离测试 | `OBSERVED_PASS` | 已具备 API、前端和浏览器证据 |
| BUILD-060 正式构建门禁 | `IMPLEMENTED_PENDING_GATE` | 真实角色、正式契约、课程资料、正式审计和人工证据全部通过 |
| BUILD-000 课程数据 | `BLOCKED_INPUT` | 恢复 manifest 匹配的 20 个 PDF 并重跑完整 local acceptance |
| 最终发布 | `blocked` | 所有 P0/P1、T0-T6、部署、恢复和真实 Workflow 条件满足 |

本节复审完成后，后续修改 BUILD-060 相关 API、权限、活动、通知或前端路由时，必须按第 27 节重跑受影响的 T1-T6，并在 BUILD-060 证据目录追加结果；仅文档修正则至少重新解析 YAML/JSON、执行 `git diff --check` 并更新本节关联状态。

## 56. 2026-07-25 BUILD-080 备份安全回归与恢复门禁边界

本节补充当前环境可以独立执行的备份安全测试。测试不依赖 Docker、MariaDB、生产卷或服务器账号，因此不会把本地安全检查误记为完整恢复演练。

### 56.1 新增测试

新增 `scripts/test_backup_security.sh`，使用临时目录构造三类脱敏夹具：

1. 合法归档目录包含 manifest 和 `SHA256SUMS`，`verify_backup.sh` 必须通过。
2. 备份目录直接包含 `.env`，`verify_backup.sh` 必须拒绝。
3. tar 包内部包含 `*.secret` 成员，目录级检查通过后，归档成员检查必须拒绝。

测试不会输出夹具内容、密钥值、签名 URL 或部署路径中的凭据，也不会修改仓库、Compose 卷或服务器数据。

### 56.2 构筑后结果

| 检查 | 结果 | 边界 |
|---|---|---|
| `bash -n scripts/test_backup_security.sh` | `PASS` | 测试脚本语法正确 |
| `bash scripts/test_backup_security.sh` | `PASS / BACKUP_SECURITY_OK cases=3` | 合法归档、目录明文密钥和 tar 内部密钥均覆盖 |
| `bash -n scripts/verify_backup.sh scripts/backup.sh scripts/restore_rehearsal.sh scripts/full_restore_rehearsal.sh` | `PASS` | 备份/恢复脚本静态语法通过 |
| 服务器备份 SHA256、隔离恢复、完整 Compose 恢复 | `BLOCKED_INPUT / BLOCKED_DEPENDENCY` | 真实备份目录、`deploy/.env`、Docker 基础镜像和服务器演练仍未提供 |

### 56.3 审查结论和关闭条件

- `verify_backup.sh` 当前同时检查备份目录文件、`SHA256SUMS` 和 tar 归档成员；本地回归覆盖正常路径和两类敏感文件拒绝路径。
- 本地测试结果只能记为 `OBSERVED_PASS`，不能关闭 `real_backup_restore` 或 BUILD-080。
- 关闭 BUILD-080 仍必须在服务器执行 `verify_backup.sh`、`restore_rehearsal.sh` 和适用的 `full_restore_rehearsal.sh`，验证恢复后的数据库、Adapter、Moodle 文件树、Caddy 状态、课程 manifest 和代码来源，并归档脱敏日志。
- 如果修改备份归档规则、密钥排除规则、Compose 卷、恢复脚本或部署配置，必须重跑 T1-T6；若仅修改本地安全夹具，至少重跑 T1、T2、T5、T6。

当前状态：`BUILD-080 = IMPLEMENTED_PENDING_GATE`，本地备份安全回归为 `OBSERVED_PASS`，真实备份/恢复和正式管理员角色继续保持阻断。

## 57. 2026-07-25 Spark Assistant 鉴权负向复测与签名构造复审

本节复核用户提供的讯飞 Spark Assistant 参考文档、当前 HMAC-SHA256 签名实现和远端鉴权负向结果。官方通用 URL 鉴权要求 `host`、RFC1123 `date`、`GET path HTTP/1.1` 参与签名，并将 `authorization`、`date`、`host` 放入最终 WebSocket URL；当前客户端实现与该规则一致。

### 57.1 本地构造审查

新增离线契约断言，覆盖 `wrong-api-key`、`wrong-secret` 和 `tampered-date` 三种变异，确认每个负向目标都改变鉴权材料，且没有把 API Key/Secret 写入普通业务帧或测试输出。

| 检查 | 结果 |
|---|---|
| `python3 -m unittest -q scripts.test_spark_assistant_contract` | `PASS / 7 tests` |
| `python3 -m compileall -q scripts/test_spark_assistant_contract.py scripts/test_spark_assistant_auth_negative.py` | `PASS` |
| 签名输入 | `PASS`，与官方 `host/date/request-line + HMAC-SHA256` 规则一致 |

### 57.2 远端负向结果

```text
python3 scripts/test_spark_assistant_auth_negative.py --timeout 10
case=wrong-api-key result=NOT_PASS handshake=101 ... error_code=0 final_seen=yes
case=wrong-secret result=NOT_PASS handshake=101 ... error_code=0 final_seen=yes
case=tampered-date result=NOT_PASS handshake=101 ... error_code=0 final_seen=yes
```

上面的省略号表示脱敏字段，完整证据只保留状态、帧数和错误类别，不保存密钥、签名 URL、Cookie、问题或回答。三类错误鉴权均建立 WebSocket `101` 并收到正常结束帧，未出现非零鉴权错误。

### 57.3 当前判定和后续关闭条件

- 本地签名构造与负向夹具：`OBSERVED_PASS`。
- 真实远端 `SPARK-AUTH-002`、`SPARK-AUTH-003`：`FAIL`，不能改写为 `PASS`。
- 当前失败更符合端点/Assistant 权限绑定、供应方鉴权策略或测试账号配置问题；在供应方确认具体 endpoint、Assistant 权限和协议版本前，不继续扩大请求量或执行限流/并发压力测试。
- 关闭条件：供应方确认测试端点和授权绑定后，重新执行错误 Key、错误 Secret、篡改 date/host/path、缺 AppID、错误权限和异常关闭用例，并得到非零错误或官方明确的等价拒绝语义；所有结果需脱敏归档。

当前状态：`BUILD-090 = IMPLEMENTED_PENDING_GATE`，Spark 正向和参数负向保持观察性通过，鉴权负向保持 `FAIL`，最终发布继续阻断。

## 58. 2026-07-25 课程资料输入审计与 BUILD-000 阻断确认

本节记录本轮对课程资料输入的只读审计。审计范围包括当前仓库 `course-data/`、Git 当前提交及远程跟踪分支、`/home/registrar/下载` 和桌面候选目录；未发现可用于恢复 manifest 的原始课件包或 PDF。

### 58.1 审计结果

| 检查 | 结果 | 证据 |
|---|---|---|
| `course-data/` 文件树 | `BLOCKED_INPUT` | 只有 `.gitkeep`、`manifest.json` 和 `graph-baseline.json` |
| Git 当前提交和 `origin/main` | `BLOCKED_INPUT` | `git ls-tree` 未发现 manifest 声明的 PDF |
| `/home/registrar/下载` 候选文件 | `BLOCKED_INPUT` | 仅发现与课程无关的 ZIP/TAR 文件，无课件 PDF/课件包 |
| 桌面候选文件 | `BLOCKED_INPUT` | 只有伦理声明 PDF，不属于课程 manifest |
| `python3 scripts/verify_course_data.py course-data/normalized` | `FAIL_FAST / BLOCKED_INPUT` | 首个缺失文件为 `chapter-1-1.1-.pdf` |

### 58.2 处理边界

- 不修改 `manifest.json`、hash、page_count 或 normalized 文件名。
- 不把伦理声明、设计文件或无关压缩包复制到课程目录。
- 不生成空 PDF、占位 PDF 或伪造文本覆盖率。
- 课程资料恢复后必须重新执行完整 manifest 校验、文本提取、知识库生命周期和 BUILD-000 全量 local acceptance；在此之前，后续本地隔离测试可以继续，但不能升级为正式课程数据通过。

当前结论：`DATA-INPUT-001 = BLOCKED_INPUT`，`BUILD-000 = BLOCKED_INPUT`。本轮审计没有引入文件变更，阻断原因需要用户提供原始课件包或与 manifest 完全匹配的 20 个 PDF 后才能解除。

## 59. 2026-07-25 测试方案落地后的进度账本一致性审查

本节记录将测试方案持续执行结果写入状态账本后的二次审查。目标是确保计划、当前门禁、验收证据目录、元数据和敏感信息边界可以由自动化检查重复验证。

### 59.1 新增一致性门禁

新增 `scripts/validate_project_progress.py`，使用 PyYAML 解析 `PROJECT_PROGRESS.yaml`，并检查：

- 计划文件存在，当前门禁存在且状态与账本一致；
- 当前门禁的 `acceptance/frontend/<BUILD-ID>/` 证据目录存在；
- `known_blockers` 为非空列表，且每个阻断项包含 `id`、`severity`、`status`、`description`、`required_action`；
- 存在 `.env.test.local` 时权限必须为 `600`；
- 所有前端 BUILD `metadata.json` 均可解析，且 `sensitive_values_recorded`、`secrets_recorded` 不得为 `true`。

校验器只输出门禁 ID、数量和状态，不读取或打印 API Key、API Secret、Cookie、Authorization、签名 URL、完整问题或完整回答。BUILD-000 证据目录新增 `review.md`，只记录课程资料阻断，不生成占位 PDF。

### 59.2 构筑后审查结果

| 检查 | 结果 |
|---|---|
| `python3 scripts/validate_project_progress.py` | `PASS / PROJECT_PROGRESS_VALIDATION_OK gate=BUILD-000 metadata=7 blockers=17` |
| BUILD-080 当前元数据 | 已校正为 API `74` 路由、Vitest `25`、Mock `16`、自定义 a11y `3/3` |
| BUILD-100 当前元数据 | 已校正 Vitest 全量为 `25` 测试 |
| `.env.test.local` | 存在时权限为 `600`，状态账本标记不记录值 |
| 当前正式门禁 | 仍为 `BUILD-000 = BLOCKED_INPUT`，未因本地校验通过而误升级为 `PASS` |

### 59.3 复审结论与后续条件

本轮确认测试方案已经同时具备人工执行协议和机器可验证的状态一致性门禁。历史 `test-output.txt` 中的早期数字保留用于追溯；当前权威数字以本节、`PROJECT_PROGRESS.yaml` 和对应 BUILD `metadata.json` 为准。后续任何构筑完成后，必须先运行账本校验，再按第 27 节执行受影响的 T0-T6 测试并追加脱敏证据。课程 PDF、正式 Moodle 契约与角色、服务器恢复、Docker/HTTPS、真实 Workflow 和人工可访问性仍是独立阻断项。

## 60. 2026-07-25 BUILD-020 会话过期恢复实现与构筑后审查

本节推进 BUILD-020 中此前标记为 `NOT_RUN` 的会话过期恢复项。范围只涉及前端会话状态和本地 Mock Adapter，不把真实 Moodle 会话时钟、登录重定向或角色能力误记为完成。

### 60.1 实现和代码审查

- API 客户端收到 HTTP `401`、`session_expired` 或 `not_authenticated` 时发出本地会话失效事件。
- Zustand 清理 session、课程数据和 preview 标记；应用上下文改用空数据，避免过期后的旧课程内容继续显示。
- 启动阶段的并行请求不会吞掉会话失效错误并回退到示例数据；普通非鉴权错误仍可进入明确的有限空状态。
- 会话失效后不自动重试任何请求，尤其不重放写操作；页面显示重新登录入口 `/login/index.php`。
- CSRF token 仍只来自会话响应，不写入 `localStorage`、测试输出或验收元数据。

### 60.2 构筑后测试和验收

| 层级 | 命令/结果 | 判定 |
|---|---|---|
| T1 | lint、typecheck、API `74` 路由契约、UI 契约、前端硬化、Python 编译、Shell 语法、`git diff --check` | `PASS` |
| T2 | Vitest 全量 `5 files / 26 tests`；会话失效事件单测通过 | `PASS` |
| T3 | `test_agent_boundary_api.py` 输出 `AGENT_BOUNDARY_API_OK`，跨课程会话拒绝保持通过 | `PASS` |
| T4 | Mock 浏览器 `18/18`，会话过期启动和启动后路径 `2/2`；标准 smoke `2/2` | `OBSERVED_PASS` |
| T5 | 自定义 a11y `3/3`；axe 主内容默认规则集 `4/4`，含 `color-contrast` | `OBSERVED_PASS` |
| T6 | BUILD-020 证据目录、进度账本和本节已同步 | `PASS` |

首次受限环境执行在 Vite 监听阶段返回 `listen EPERM`，没有进入断言；在允许回环监听的隔离环境串行重测后所有浏览器层通过。该基础设施结果保留在证据中，不作为业务失败或通过。

### 60.3 门禁结论

BUILD-020 的本地会话过期实现达到 `OBSERVED_PASS`，但批次保持 `IMPLEMENTED_PENDING_GATE`。关闭条件仍包括真实 Moodle student/teacher/admin 登录、真实会话过期和刷新/后退行为、正式 API 契约以及人工角色权限验收。当前项目整体的 `BUILD-000 = BLOCKED_INPUT`、课程 PDF、真实 Workflow、正式 HTTPS、服务器恢复和正式辅助技术门禁不变。

## 61. 2026-07-25 BUILD-090 Spark Assistant 当前协议复测与鉴权阻断复审

本节记录使用本地 `600` 权限测试环境对 Spark Assistant 参考协议的当前复测。测试脚本只输出脱敏状态，不保存凭据、签名 URL、Cookie、Authorization 值、问题或回答。

### 61.1 当前结果

| 用例 | 结果 | 说明 |
|---|---|---|
| 离线签名/帧契约 | `PASS` | `scripts.test_spark_assistant_contract` 7/7；签名材料和敏感值边界通过 |
| 合法正向 WebSocket | `OBSERVED_PASS` | handshake `101`、header code `0`、3 帧、assistant 内容、序列、结束状态和 close `1000` 均有效 |
| 参数协议负向 | `OBSERVED_PASS` | 缺 AppID、缺 message、非法 role、非法 temperature 共 `4/4`，错误类别为脱敏 `10003/10004` |
| 错误鉴权负向 | `FAIL` | wrong key、wrong secret、tampered date 共 `3/3` 仍完成正常业务帧并返回最终 `error_code=0` |

### 61.2 审查结论

- 正向结果只证明当前 Spark Assistant 测试端点的一轮协议连通性，不等于真实 Xingchen Workflow、知识库版本、来源命中或专业答案验收。
- 参数负向可以证明当前测试脚本和端点会拒绝部分非法业务帧；鉴权负向不通过，不能写成 `PASS`。
- 错误鉴权行为需要供应方确认 endpoint、Assistant 权限绑定、签名版本和测试账号配置；确认前不扩大并发、限流或重复请求范围。
- BUILD-090 继续为 `IMPLEMENTED_PENDING_GATE`，`SPARK-AUTH-FAIL-001` 继续为 `FAIL`，最终发布继续阻断。

### 61.3 关闭条件

供应方确认配置后，重新执行错误 API Key、错误 Secret、篡改 date/host/path、缺 AppID、错误权限和异常关闭用例，并得到非零错误或官方明确等价的拒绝语义；同时补齐真实 Workflow、知识库来源、并发/恢复和正式角色证据，才可重新评估 BUILD-090。

## 62. 2026-07-25 BUILD-090 Agent 流式客户端边界测试补齐与构筑后审查

本节补齐前端 Agent 客户端此前只有间接覆盖的流式边界。实现没有放宽服务端来源、权限或会话约束；新增测试只验证客户端在异常流上保持可解释状态。

### 62.1 新增契约覆盖

- 上游只发送 `token` 后结束：客户端抛出 `stream_incomplete`，保留已收到事件，不生成假 `done`。
- 上游发送 `error` 事件：客户端转成带上游错误码的 `ApiError`，不把错误当作成功回答。
- 上游重复发送 `done`：客户端只分发第一条 `done`，不会重复结束或追加后续事件。
- 原有坏 JSON、CSRF、可信上下文、取消和重试 UI 边界继续保留；写请求不由客户端自动重放。

### 62.2 构筑后结果

| 层级 | 结果 | 证据 |
|---|---|---|
| T1 | `PASS` | lint、typecheck、API `74` 路由、UI 契约、前端硬化、Python 编译、Shell 语法、差异检查 |
| T2 | `PASS` | Vitest `5 files / 30 tests`；新增流式边界 4 项通过 |
| T3 | `PASS` | Agent context/boundary API 均通过，跨课程和来源边界不变 |
| T4 | `OBSERVED_PASS` | Mock 浏览器 `18/18`、标准 smoke `2/2` |
| T5 | `OBSERVED_PASS` | 自定义 a11y `3/3`、axe 主内容默认规则集 `4/4` |
| T6 | `PASS` | BUILD-090 `test-output.txt`、`metadata.json`、账本和本节同步 |

### 62.3 门禁结论

本地 Agent 流式客户端边界达到 `OBSERVED_PASS`，但这不等于真实 Workflow 的断流、限流、并发、恢复、知识库来源或专业答案验收。BUILD-090 仍为 `IMPLEMENTED_PENDING_GATE`；Spark 鉴权负向 `FAIL`、课程 PDF、正式角色和真实 Workflow 继续阻断正式发布。

## 63. 2026-07-25 BUILD-090 Agent 重试/取消生成复测与计划二次审查

本节是第 27 节测试协议落地后的最新增量复审。新增浏览器用例只验证 Agent UI 对上游错误和用户取消的状态处理；不改变 Adapter、权限、来源核验或 Spark 鉴权结论。旧的 `18/18` 浏览器结果保留在历史构筑记录中，本节记录当前 `20/20` 的权威增量结果。

### 63.1 变更范围和审查结论

| 审查项 | 结果 | 结论 |
|---|---|---|
| 需求范围 | `PASS` | 仅新增 Agent 重试和取消生成的浏览器验收；没有扩展角色、数据模型或上游协议范围 |
| 失败状态 | `PASS` | 上游 `error` 先显示可重试错误，不渲染成功回答；重试是用户明确触发的第二次请求 |
| 取消状态 | `PASS` | 用户取消后显示取消状态；迟到的 token/done 不得追加到当前回答 |
| 请求副作用 | `PASS` | 重试用例断言请求次数为 `2`；没有自动重试写请求或重复提交业务数据 |
| 凭据和隐私 | `PASS` | 证据只记录状态、计数和脱敏错误类别，不记录密钥、Cookie、Authorization、完整问题或回答 |
| 外部边界 | `REVIEW_REQUIRED` | 真实 Workflow 的断流、超时、并发、恢复和真实三角色仍没有执行；Spark 鉴权负向仍为 `FAIL` |

### 63.2 本轮测试结果

本轮在允许回环监听的环境中串行执行，Mock API 使用本次运行专用数据库和资源目录：

```text
cd frontend && npm run test:e2e:mock -- --workers=1
OBSERVED_PASS: 20 passed (14.0s)

cd frontend && npm run test:a11y -- --workers=1
OBSERVED_PASS: 3 passed (2.0s)

cd frontend && npm run test:e2e -- --workers=1
OBSERVED_PASS: 2 passed (2.4s)

cd frontend && npm run test:axe -- --workers=1
OBSERVED_PASS: 4 passed (5.0s)
```

新增用例的强制断言：

- `Agent error state can retry once and then render the recovered answer`：第一次上游 error 可见；点击“重试”后回答恢复；请求计数严格为 `2`。
- `Agent generation can be cancelled without rendering a late answer`：点击“取消生成”后状态可见；等待延迟上游响应后，迟到回答出现次数为 `0`。

### 63.3 T0-T6 复审记录

| 层级 | 本轮结果 | 验收边界 |
|---|---|---|
| T0 | `PASS` | 范围审查确认只涉及 Agent UI 错误/取消状态；证据目录、计划和账本路径已指定 |
| T1 | `PASS_WITH_PRIOR_EVIDENCE` | 同一工作区最近构筑已通过 lint、typecheck、API/UI/硬化契约、Python/Shell 语法、构建和差异检查；本轮仅新增浏览器测试，不重复宣称静态命令已在本次命令序列执行 |
| T2 | `PASS_WITH_PRIOR_EVIDENCE` | 最近全量 Vitest 为 `5 files / 30 tests`；本轮新增的是 Playwright 流程，不改变生产代码逻辑 |
| T3 | `PASS_WITH_PRIOR_EVIDENCE` | Agent boundary/context API 最近复测通过；本轮没有新增 API 或持久化写操作 |
| T4 | `OBSERVED_PASS` | 当前 Mock Playwright `20/20`、标准 smoke `2/2`；只代表本地 Mock/预览环境，不替代真实角色流程 |
| T5 | `OBSERVED_PASS_WITH_EXTERNAL_BLOCKERS` | 自定义 a11y `3/3`、axe 主内容默认规则集 `4/4`；正式 axe 等价审查、人工键盘/屏幕阅读器、六视口和真实 Workflow 恢复仍开放 |
| T6 | `PASS_WITH_EXTERNAL_BLOCKERS` | 新增脱敏证据已归档并同步 metadata、账本和项目状态；由于正式外部门禁未闭合，BUILD-090 不能关闭 |

### 63.4 计划二次审查结果

本次对计划本身再次检查以下一致性：

1. 第 27 节的固定顺序仍适用：版本/范围、代码审查、静态门禁、局部测试、API 测试、浏览器测试、质量测试、证据归档和门禁判定没有被新增用例绕过。
2. 第 27.5 节的状态边界仍有效：`OBSERVED_PASS` 只能表示 Mock 或局部观察，`PASS` 仍要求所有适用测试、真实角色、人工验收、证据和回退检查全部通过。
3. 第 27.3 节的上游恢复要求得到 UI 级补充：错误不得伪装成 `done`，取消不得接收迟到结果，重试必须由用户触发并可计数。
4. 旧记录中的 `18/18` 没有被删除或改写；当前权威增量记录为 `20/20`，证据文件为 `acceptance/frontend/BUILD-090/agent-ui-retry-cancel-revalidation-20260725.txt`。
5. 本次复审没有关闭课程 PDF、正式 Moodle API/角色、真实 Workflow、Spark 鉴权负向、Docker/HTTPS、服务器恢复或正式可访问性门禁。

### 63.5 当前门禁结论

本轮 Agent UI 重试/取消生成功能达到 `OBSERVED_PASS`。`BUILD-090` 仍为 `IMPLEMENTED_PENDING_GATE`，原因是正式 Workflow 的错误/断流/限流/并发/恢复证据、真实知识库来源、三角色浏览器验收、Spark 鉴权负向修复和 T0-T6 正式证据尚未完成。最终发布继续保持阻断。

## 64. 2026-07-25 BUILD-100 Docker 构建依赖复测与门禁更新

本节记录在继续推进发布前硬化时对 Docker 运行条件的实际复测。此前的“缺少基础镜像”记录只说明本地镜像状态；本轮进一步访问 Docker 守护进程并执行真实构建，确认当前阻断原因是 Docker Hub manifest 请求超时，而不是前端 Dockerfile 静态语法错误。

### 64.1 复测结果

| 检查 | 结果 | 结论 |
|---|---|---|
| Docker daemon | `PASS` | Docker Server `29.1.3` 可访问 |
| 基础镜像 | `BLOCKED_DEPENDENCY` | 本地没有可用的 `node:22-alpine` / `nginx:1.27.5-alpine` 缓存 |
| 前端镜像构建 | `BLOCKED_DEPENDENCY` | 在 `FROM node:22-alpine` 解析阶段访问 Docker Hub manifest 超时；未生成可验收镜像 |
| Compose 静态配置 | `PASS_WITH_ENV_BLOCKER` | `docker compose ... config --no-interpolate --no-consistency` 成功；完整运行仍需要 `deploy/.env` 和镜像 |
| 容器健康检查 | `NOT_RUN` | 没有构建成功的镜像，不能伪造健康检查结果 |

复测命令：

```bash
docker version --format '{{.Server.Version}}'
docker build --file frontend/Dockerfile --build-arg VITE_BASE_PATH=/learn/ --tag energygraph-learning-frontend:test .
docker compose --project-directory deploy --env-file deploy/.env.example config --no-interpolate --no-consistency
```

### 64.2 构建后审查结论

- Dockerfile 和 Compose 的前端服务定义仍保留 `VITE_BASE_PATH=/learn/`、健康检查和 Caddy 依赖关系；本次没有为了绕过网络失败而替换基础镜像、关闭健康检查或降低运行约束。
- `docker build` 的失败发生在外部镜像 manifest 获取阶段，不能被记录为代码构建失败，也不能升级为容器 PASS。
- 由于没有生成镜像，本次不执行容器内 Nginx `Cache-Control`、`X-Content-Type-Options`、`/learn/` 路由、API no-store 和 legacy `/agent/` 回退检查；这些仍是下一次容器构建后的必测项。
- 本地前端 lint、typecheck、Vitest、生产构建、Mock 浏览器、a11y 和 axe 结果不替代容器运行证据。

### 64.3 T1/T5/T6 状态

| 层级 | 结果 | 验收边界 |
|---|---|---|
| T1 | `PASS_WITH_ENV_BLOCKER` | Docker Server 可访问，Compose 静态配置通过；镜像构建被外部 registry 超时阻断 |
| T5 | `BLOCKED_DEPENDENCY` | 容器健康检查、Nginx header、同源路由和正式 HTTPS 尚未执行 |
| T6 | `PASS_WITH_EXTERNAL_BLOCKERS` | 失败输出已脱敏归档并写入账本；BUILD-100 不能关闭 |

### 64.4 下一次关闭条件

在具备可信内部 registry、预加载镜像或稳定 Docker Hub 网络后，必须重新执行：

1. 前端镜像构建并记录镜像 digest。
2. 启动隔离 Compose，等待 frontend、Adapter、Moodle 和 Caddy 健康检查全部通过。
3. 使用容器内请求检查 `/learn/`、静态资源缓存、API `no-store`、安全 header 和 `/agent/` 回退。
4. 重新执行 BUILD-100 的全量 T1-T6，并将运行日志、健康状态和回退证据归档。

当前 `BUILD-100` 继续为 `IMPLEMENTED_PENDING_GATE`，`FRONTEND-CONTAINER-001` 继续为 `BLOCKED_DEPENDENCY`；最终发布状态不变。

## 65. 2026-07-25 Spark Assistant APPID 权限与签名鉴权分层复测

本节根据讯飞官方 Spark Assistant 文档和当前测试端点的实际结果，进一步拆分 BUILD-090 的鉴权门禁。此前“鉴权负向失败”只按三类签名材料变异统计；本轮加入“合法签名 + 无权限 APPID”用例，以验证端点是否执行 APPID/Assistant 权限绑定。

### 65.1 当前协议事实

- 官方文档规定 Assistant URL 为 `ws(s)://spark-openapi.cn-huabei-1.xf-yun.com/v1/assistants/{assistant_id}`，每次交互重新建立 WebSocket；生成中止可以发送 close 消息。
- 官方文档将 `header.code=0` 定义为成功，将非零码定义为错误，并列出 `11200` 为 APPID 未授权或业务量超限。
- 当前 `.env.test.local` 的测试端点路径符合官方 Assistant URL 形状；本节和证据文件只记录端点的脱敏 host/path 形状，不记录凭据值。

### 65.2 复测结果

| 用例 | 结果 | 观察 |
|---|---|---|
| 离线签名/帧契约 | `PASS` | `7/7`；新增用例确认无权限 APPID 不需要改变 URL 签名材料 |
| 合法正向 WebSocket | `PASS` | handshake `101`、`header.code=0`、19 帧、序列/最终状态有效、close `1000` |
| 合法签名 + 无权限 APPID | `OBSERVED_PASS` | handshake `101`，1 帧，`header.code=11200`，没有正常最终回答 |
| 错误 API Key | `FAIL` | handshake `101`，8 帧，最终 `header.code=0` |
| 错误 API Secret | `FAIL` | handshake `101`，8 帧，最终 `header.code=0` |
| 篡改 date | `FAIL` | handshake `101`，8 帧，最终 `header.code=0` |

执行命令：

```bash
python3 -m unittest -q scripts.test_spark_assistant_contract
python3 scripts/test_spark_assistant_auth_negative.py --timeout 15
python3 -m py_compile scripts/test_spark_assistant_auth_negative.py scripts/test_spark_assistant_contract.py
git diff --check
```

### 65.3 审查结论

1. 测试脚本的 APPID 负向构造是正确的：它保持合法 URL 签名，只将业务帧中的 `header.app_id` 改为无权限值；远端返回 `11200`，符合官方错误码语义。
2. 当前端点能够识别无权限 APPID，因此不能把所有鉴权问题解释为“端点完全不校验权限”。错误 key、错误 secret 和篡改 date 仍返回正常业务帧，仍是未解释的供应方协议/绑定问题。
3. 三类签名失败继续保持 `FAIL`，不得因正向握手成功、APPID 权限负向通过或错误响应包含业务帧而升级为 `PASS`。
4. 在供应方确认签名版本、API Key/Secret 绑定方式、Assistant 发布状态和端点路由前，不执行更高风险的并发/限流压力测试；先保持单轮脱敏验证。

### 65.4 门禁和下一步

当前 `SPARK-AUTH-FAIL-001` 仍为 P0 `FAIL`，但阻断范围已精确为“签名材料负向校验未得到拒绝语义”；`wrong-app-id` 作为 `OBSERVED_PASS` 单独记录。关闭条件是供应方确认并修正或解释三类签名行为后，重新得到非零鉴权错误或官方明确等价拒绝语义，再执行异常关闭、限流、并发、内容审核和真实 Workflow 复测。

## 66. 2026-07-25 进度账本校验器强化与证据路径复审

本节补强“本地维护一份详细配置文件”的机器保障。原校验器只检查 YAML/JSON 可解析、当前 gate 对齐、阻断项字段和 metadata 中的布尔标志；它不能证明证据文件真的存在，也不能证明 `.env.test.local` 中的测试密钥没有被复制进报告。本轮新增两类校验，并保留不打印敏感值的边界。

### 66.1 新增校验规则

| 规则 | 失败条件 | 当前结果 |
|---|---|---|
| 敏感值扫描 | `TEST_API_KEY` 或 `TEST_API_SECRET` 的实际值出现在文本代码、计划、账本或验收证据中 | `PASS`；变量名和路径之外不输出值 |
| 证据路径扫描 | `test_runs[].evidence` 中识别出的 `acceptance/frontend/`、计划、状态或账本路径不存在 | `PASS`；当前检查 `66` 个引用 |
| 权限扫描 | `.env.test.local` 存在且权限不是 `600` | `PASS` |
| metadata 状态扫描 | 任一 BUILD metadata 设置 `sensitive_values_recorded=true` 或 `secrets_recorded=true` | `PASS` |

### 66.2 实现和测试

新增实现位置：`scripts/validate_project_progress.py`。新增回归测试：`scripts/test_validate_project_progress.py`，覆盖：

- 将 fixture API key 写入临时验收文本时，校验器报告变量名和相对路径，但不把 fixture 值放进错误消息。
- `test_runs[].evidence` 指向临时缺失文件时，校验器返回明确的缺失路径错误。

本轮执行：

```text
python3 -m unittest -q scripts.test_validate_project_progress
PASS: 2 tests

python3 scripts/validate_project_progress.py
PROJECT_PROGRESS_VALIDATION_OK gate=BUILD-000 metadata=8 blockers=19 evidence_refs=66 redaction_scan=PASS

python3 -m compileall -q scripts agent-adapter
PASS

bash -n scripts/*.sh
PASS

git diff --check
PASS
```

### 66.3 审查边界和验收条件

1. 该校验器只扫描本地文本工件和 `.env.test.local` 中的测试密钥值，不输出、不归档、不上传密钥；它不证明真实外部服务已经安全。
2. 证据引用检查只验证文件或目录存在，不能把文件存在升级为测试通过；测试结果仍必须由对应 `test-output.txt`、`review.md`、metadata 和命令输出共同证明。
3. 任何新增 `test_runs`、BUILD 证据或密钥配置变更后，必须先运行校验器，再按第 27 节重跑受影响测试。
4. 当前账本仍准确记录 `BUILD-000 = BLOCKED_INPUT`、`BUILD-090` 签名鉴权负向 `FAIL` 和 `BUILD-100` Docker `BLOCKED_DEPENDENCY`；本轮校验器通过不改变任何正式产品门禁。

### 66.4 当前结论

账本维护能力达到本地 `PASS`：状态字段可解析、当前 gate 对齐、66 个证据引用存在、测试密钥实际值未出现在文本工件中。项目整体仍为 `in_progress`，最终发布继续阻断，下一次构建后必须沿用该校验器和第 27 节 T0-T6 流程。

## 67. 2026-07-25 BUILD-100 提交代码归档与材料审计

本节记录发布前代码归档和提交材料审计。目标是生成可复现、可校验且不包含密钥/课程原始文件/依赖缓存的源代码附件，同时准确记录哪些材料仍需要真实外部输入。

### 67.1 代码归档修正

`scripts/package_submission_code.sh` 已修正：

- `course-data/xingchen-sources` 只有在真实目录存在时才归档；缺失时输出通知，不把未提供的知识库来源伪造成存在。
- 排除根目录和子目录中的 `.env`、`.env.*`、`*.key`、`*.secret`。
- 排除 `node_modules`、`test-results`、`playwright-report`、Python 缓存、PDF、ZIP、XLSX 和 DOCX，避免把依赖缓存或课程原文件放入提交附件。
- 仍使用显式源目录清单，新增工作区文件不会自动进入归档。
- 使用 `/tmp/energygraph-ai-submission-materials.lock` 和临时归档文件；写入完成并通过成员检查后才原子替换正式归档，检查脚本使用同一把锁。

### 67.2 当前结果

```text
bash scripts/package_submission_code.sh
PASS: SUBMISSION_CODE_ARCHIVE_READY

sha256sum -c 05-作品代码/作品代码-源文件.sha256
PASS

archive inspection
PASS: approximately 1.8 MB; no .env/key/secret/node_modules/test-results/playwright-report member

concurrent package/check revalidation
PASS: shared flock serialized access; no EOF or SHA race; serial checksum passed

bash scripts/check_submission_materials.sh
BLOCKED_INPUT: missing=3
```

当前缺失材料为：

1. `03-作品Demo/demo-url.txt`：正式 HTTPS 域名地址。
2. `03-作品Demo/demo-video.mp4`：真实演示录屏。
3. `06-效果验证报告/真实人工验收汇总.md`：真实三角色、六视口和辅助技术验收汇总。

### 67.3 代码审查与验收边界

| 门禁 | 当前结果 | 说明 |
|---|---|---|
| 源代码归档 | `PASS` | 归档已生成，SHA-256 已验证 |
| 归档敏感文件检查 | `PASS` | 未发现环境文件、密钥类文件或私有配置成员 |
| 归档依赖/缓存检查 | `PASS` | 未发现 `node_modules`、Playwright 报告或测试结果缓存 |
| 正式提交材料 | `BLOCKED_INPUT` | 3 项真实外部材料缺失，不能用 README、Mock 输出或空文件替代 |

代码归档通过不等于最终提交通过。正式 Demo URL、真实视频和人工验收汇总到位后，必须重新执行 `check_submission_materials.sh`，并按第 27 节重做受影响的 T4-T6 证据复审。

### 67.4 当前门禁结论

`BUILD-100` 的代码归档子项达到本地 `PASS`；`SUBMISSION-MATERIALS-001` 保持 `BLOCKED_INPUT`，最终发布仍因正式域名、真实角色/Workflow、课程资料、容器运行和人工验收等条件未闭合而阻断。

## 68. 2026-07-25 测试方案结构化终审与下一次构筑规则

本节是对第 27 节测试方案和第 67 节最新证据审计的计划级终审。它只审查“规则是否足够明确、结果是否可追溯、证据是否能支撑门禁”，不把本地校验器通过升级为产品批次通过。

### 68.1 本轮审查范围和事实结果

| 审查项 | 当前结果 | 结论 |
|---|---|---|
| 进度账本、证据引用和脱敏扫描 | `PASS` | `PROJECT_PROGRESS_VALIDATION_OK`；当前门禁 `BUILD-000`，元数据 `8` 份，阻断项 `19` 个，证据引用 `68` 个，`redaction_scan=PASS` |
| 校验器回归 | `PASS` | `scripts.test_validate_project_progress` 为 `2/2`；覆盖敏感值泄露和缺失证据路径 |
| 计划章节连续性 | `PASS` | 第 27 节为执行协议，第 68 节为本轮结构化终审；第 67 节仍是最新提交材料审计 |
| 当前正式门禁 | `BLOCKED_INPUT` | manifest 要求的 20 个课程 PDF 仍缺失；不得生成占位文件或修改 hash/page_count |
| 真实发布状态 | `blocked` | 真实角色、正式 API/Workflow、Spark 签名鉴权负向、Docker 运行、HTTPS、恢复和人工验收仍未闭合 |

### 68.2 计划规则补强

1. **适用性必须显式记录。** 每个构建的 `review.md` 必须为 T0-T6 各写一行且只能使用 `PASS`、`OBSERVED_PASS`、`BLOCKED_INPUT`、`BLOCKED_DEPENDENCY`、`NOT_RUN`、`NOT_IMPLEMENTED` 或 `NOT_APPLICABLE`。使用 `NOT_APPLICABLE` 时必须同时写明不适用理由、替代证据和不影响范围；空目录、空截图或没有命令退出码不能作为证据。任何适用层缺少状态时，T6 只能为 `REVIEW_REQUIRED`。
2. **每次构筑尝试必须可区分。** `metadata.json` 必须记录 `run_id`、`attempt`、`authoritative_result`、`supersedes` 和 `environment`；`test-output.txt` 必须用明确标题标出本次权威结果。历史结果只能标记为 `HISTORICAL` 或 `SUPERSEDED`，不能在当前批次摘要中重复计数。
3. **前置门禁阻断时禁止越级关闭。** 前置 BUILD 未达到 `PASS` 时，后续 BUILD 可以进行数据无关的实现和局部测试，但状态只能是 `IMPLEMENTED_PENDING_GATE` 或相应阻断状态；不得切换生产路由、生成正式发布标签、把 Mock/隔离结果记作真实验收，或以后续 BUILD 的通过覆盖前置阻断。
4. **证据存在不等于证据成立。** 路径校验器只能证明文件或目录存在；`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `metadata.json` 还必须相互引用相同的 `run_id`、commit、环境模式、测试 ID、退出码和脱敏边界。任一项不一致时，本次结果为 `REVIEW_REQUIRED`，不得记为 `PASS`。
5. **失败后的重测范围固定。** 代码、配置、夹具或依赖发生修改后，从受影响的最早步骤重新执行，并补跑该 BUILD 的 T1-T6；仅重跑一个绿色子测试不能关闭批次。外部输入阻断解除后，必须从 T0 重新执行对应前置 BUILD，再重跑受影响的后续 BUILD。

### 68.3 下一次构筑的强制验收格式

下一次 BUILD 进入测试前，必须先在对应证据目录写入以下内容；缺项时不得开始正式门禁判定：

```text
scope.md                 # build_id、run_id、attempt、前置门禁、范围和 T0-T6 适用矩阵
review.md                # 每层状态、代码审查问题、适用性理由和复审人
metadata.json            # commit、环境、Mock 开关、浏览器、run_id 和权威结果标记
test-output.txt          # 当前权威命令、退出码、测试 ID、摘要和历史结果边界
manual-acceptance.md     # 角色、失败/恢复流程、视口、实际副作用和证据链接
rollback.md              # 代码、数据库、静态资源和路由回退验证
```

截图和视频只在该 BUILD 的 T4/T5 适用时保存；不适用时在 `review.md` 写 `NOT_APPLICABLE` 和理由，不创建空的“通过”目录。当前结果必须只由本次 `run_id` 的权威块汇总，历史快照保留但不得覆盖当前结果。

### 68.4 本轮发现、处理和开放项

| ID | 严重度 | 状态 | 结果 |
|---|---|---|---|
| `PLAN-TEST-006` | P1 | `CLOSED` | 已将 T0-T6 适用性、`NOT_APPLICABLE` 规则、空证据禁止和失败后重测范围写入本节 |
| `PLAN-TEST-007` | P1 | `CLOSED` | 校验器已检查 8 个现有 BUILD 的 metadata 运行身份、review.md T0-T6 状态矩阵、test-output/manual-acceptance 的共享 run_id 和测试输出退出码摘要；状态不一致时会退出非零 |
| `PLAN-TEST-008` | P1 | `CLOSED` | 已为 8 份现有 BUILD metadata 补齐唯一 `run_id`、`attempt`、`authoritative_result`、`supersedes` 和 `environment`，校验器已检查字段、目录匹配和 run_id 唯一性 |
| `PLAN-EVIDENCE-001` | P1 | `OPEN` | `api-test-manifest.yaml` 和 `openapi.test.json` 目前是 local-isolated-adapter 契约，不是正式 Moodle 契约；真实角色、可重置夹具和正式 API 仍缺失 |
| `DATA-INPUT-001` | P0 | `OPEN` | manifest 对应的 20 个课程 PDF 缺失，BUILD-000 继续 `BLOCKED_INPUT` |

### 68.5 终审结论

测试方案状态保持 `DOCUMENTED_AND_REVIEWED_WITH_OPEN_FINDINGS`。本轮修订使每次构筑的适用性、运行身份、历史结果边界、依赖门禁和失败重测条件可直接审查；但没有关闭任何真实外部输入。当前仍为 `BUILD-000 = BLOCKED_INPUT`，后续 BUILD 只能记录实现/隔离证据，最终发布继续 `blocked`。

## 69. 2026-07-25 构建证据运行身份校验实现与复审

本节记录对 `PLAN-TEST-007` 的本地可闭环部分进行实现：进度校验器现在会验证每份 `acceptance/frontend/BUILD-*/metadata.json` 的运行身份，而不是只验证 JSON 能否解析和证据路径是否存在。

### 69.1 新增机器校验规则

每份 BUILD metadata 必须同时满足：

- `build` 与父目录名一致。
- `run_id` 是非空字符串，且在所有 BUILD metadata 中唯一。
- `attempt` 是大于等于 1 的整数。
- `authoritative_result` 是布尔值。
- `supersedes` 是列表，即使本次没有覆盖历史结果也必须写空列表。
- `environment` 是非空字符串。

缺少字段、重复 `run_id`、目录错配或类型错误都会使 `validate_project_progress.py` 退出非零。该校验只验证证据身份，不把 `authoritative_result=true` 等同于构建门禁 PASS。

### 69.2 本轮变更和测试结果

| 项目 | 结果 | 证据 |
|---|---|---|
| 8 份 BUILD metadata | `PASS` | BUILD-020、040、050、060、070、080、090、100 均补齐运行身份字段 |
| 校验器单元回归 | `PASS` | `scripts.test_validate_project_progress` `4/4`，覆盖重复 run_id 和缺失字段 |
| 进度账本校验 | `PASS` | `PROJECT_PROGRESS_VALIDATION_OK gate=BUILD-000 metadata=8 blockers=19 evidence_refs=70 redaction_scan=PASS` |
| Python 编译和差异检查 | `PASS` | `py_compile`、`git diff --check` 均通过 |
| 当前正式门禁 | `BLOCKED_INPUT` | 20 个 manifest PDF 仍缺失；真实 T0-T6 证据和外部环境未改变 |

### 69.3 复审结论

`PLAN-TEST-007` 和 `PLAN-TEST-008` 均已关闭：校验器现在对 8 个现有 BUILD 执行 metadata、T0-T6 review matrix、共享 run_id 和退出码摘要的交叉校验。该机器门禁只证明证据结构可信，不把 `OBSERVED_PASS`、`BLOCKED_INPUT` 或 `BLOCKED_DEPENDENCY` 升级为正式 PASS。项目仍为 `in_progress`，`BUILD-000` 和最终发布状态不变。

## 70. 2026-07-25 课程资料输入重新审查与 BUILD-000 阻断复核

本节记录继续推进 BUILD-000 前置条件时对下载目录、归一化课程目录和 manifest 的重新检查。检查没有发现新的课程 PDF 或原始课件包，因此不生成占位文件、不修改 manifest、不修改 hash/page_count。

### 70.1 输入检查结果

| 检查 | 结果 | 说明 |
|---|---|---|
| `/home/registrar/下载` 候选文件 | `BLOCKED_INPUT` | 当前目录只有安装包、主题源码、图片和其他工程文件，没有 manifest 对应课程 PDF 或课件压缩包 |
| `course-data/normalized/manifest.json` | `PASS` | manifest 仍声明 20 个文件、439 页，内容未被修改 |
| `course-data/normalized` 实际 PDF | `BLOCKED_INPUT` | 目录只有 `manifest.json` 和 `graph-baseline.json`，实际 PDF 数量为 0 |
| `python3 scripts/verify_course_data.py course-data/normalized` | `BLOCKED_INPUT` | 在首个缺失文件 `chapter-1-1.1-.pdf` 处 fail-fast |
| 占位资料/manifest 改写 | `NOT_RUN` | 明确禁止，不作为解除阻断的手段 |

### 70.2 构筑后审查结论

课程资料输入阻断已由本轮只读检查再次确认，`DATA-INPUT-001` 和 `BUILD-000` 状态不变。资料恢复后必须从 T0 重新执行 manifest/hash/page_count 校验、文本覆盖率、知识库生命周期和完整 `RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh`，不能只重跑前端 Mock 测试。当前项目仍为 `in_progress`，最终发布继续 `blocked`。

### 70.3 账本一致性复核

本轮课程输入记录写入后再次执行：

```text
python3 -m unittest -q scripts.test_validate_project_progress
PASS: 5 tests
python3 scripts/validate_project_progress.py
PROJECT_PROGRESS_VALIDATION_OK gate=BUILD-000 metadata=8 blockers=19 evidence_refs=72 redaction_scan=PASS
python3 -m py_compile scripts/validate_project_progress.py scripts/test_validate_project_progress.py
PASS
git diff --check
PASS
```

校验通过只证明本地状态账本和证据引用一致，不改变课程资料输入阻断。

## 71. 2026-07-25 BUILD-000/010/030 标准证据目录补齐与复审

本节把计划第 19 节要求的标准证据结构应用到此前缺少完整目录的三个批次。整理只使用已有命令输出、图谱增量证据和本轮课程输入审计；没有把历史结果伪装成新鲜测试，也没有扩大产品功能范围。

### 71.1 标准化结果

| 批次 | 标准化内容 | 权威边界 | 当前状态 |
|---|---|---|---|
| BUILD-000 | metadata、scope、test-output、manual-acceptance、rollback；review 与本轮课程输入 run_id 对齐 | 本轮只读课程输入审计为权威；完整基线仍因 PDF 缺失阻断 | `BLOCKED_INPUT` |
| BUILD-010 | 新增标准 evidence 目录并引用既有前端工程化记录 | `authoritative_result=false`，明确不是本次新鲜重测 | `IMPLEMENTED_PENDING_GATE` |
| BUILD-030 | 将 graph-* 专用证据映射到标准 metadata、review、test-output、manual、scope、rollback | 图谱增量本地结果为权威；正式图谱版本/角色/视口仍阻断 | `PARTIAL_IMPLEMENTATION_PENDING_GATE` |

### 71.2 构筑后复审结果

```text
python3 -m unittest -q scripts.test_validate_project_progress
PASS: 5 tests
python3 scripts/validate_project_progress.py
PROJECT_PROGRESS_VALIDATION_OK gate=BUILD-000 metadata=11 blockers=19 evidence_refs=74 redaction_scan=PASS
python3 -m py_compile scripts/validate_project_progress.py scripts/test_validate_project_progress.py
PASS
git diff --check
PASS
```

校验器现在覆盖 11 份标准 metadata，并检查每份对应的 `review.md`、`test-output.txt`、`manual-acceptance.md`；BUILD-010 的历史证据标志保持为 `false`。证据结构通过不关闭 BUILD-000、BUILD-010 或 BUILD-030 的正式门禁。

## 72. 2026-07-25 BUILD-010 本地权威回归与浏览器复测

本节记录 BUILD-010 attempt 2 的实际本地回归。前一次并行浏览器启动受到沙箱回环端口权限影响，未计入产品结果；随后在允许回环监听的受控环境中串行重跑并取得有效结果。

### 72.1 本次运行结果

| 层级/命令 | 结果 | 边界 |
|---|---|---|
| `npm run lint` | `PASS` | 退出码 0 |
| `npm run typecheck` | `PASS` | 退出码 0 |
| `npm run test:all -- --run` | `PASS` | 5 files / 30 tests |
| `npm run test:hardening -- --run` | `PASS` | 2 tests；名称筛选产生的 skipped 不替代全量回归 |
| `npm run build` | `PASS` | 1694 modules transformed |
| API/UI/前端硬化契约 | `PASS` | API 74 routes、UI_CONTRACT_OK、FRONTEND_HARDENING_OK |
| `npm run test:e2e:mock -- --workers=1` | `OBSERVED_PASS` | 20/20，独立 Mock API/资源目录 |
| `npm run test:a11y -- --workers=1` | `OBSERVED_PASS` | 3/3，本地自定义检查 |
| `npm run test:axe -- --workers=1` | `OBSERVED_PASS` | 4/4，main 默认规则集含 color-contrast |
| `npm run test:e2e -- --workers=1` | `OBSERVED_PASS` | 2/2，1440x900 与 390x844 |
| Docker 构建 | `BLOCKED_DEPENDENCY` | 基础镜像/registry 条件未满足，本次不伪造容器结果 |
| 真实 Moodle/API/人工验收 | `BLOCKED_INPUT` | 账号、正式契约、课程 PDF 和人工环境未提供 |

### 72.2 构筑后审查结论

BUILD-010 的本地实现和隔离自动化达到本次 `OBSERVED_PASS`/局部 `PASS`，metadata 已更新为 `run_id=BUILD-010-20260725-02`、`attempt=2`、`authoritative_result=true`。该结果不能关闭 BUILD-010，因为前置 BUILD-000、真实三角色、正式 axe/人工辅助技术、Docker/HTTPS 和回退运行证据仍未完成。

`npm audit --json` 没有在本次 attempt 2 中重复执行，既有依赖审计结果保留为独立证据，不在本次输出中冒充新鲜审计。

## 73. 2026-07-25 BUILD-030 学习图谱 attempt 2 本地回归

本节记录学习图谱增量的本次本地权威回归。执行范围只覆盖图谱客户端、Adapter 场景、API 契约、图谱 Mock 浏览器和图谱控件可访问性；正式图谱版本、课程 PDF 来源、真实角色和六视口人工验收仍独立阻断。

### 73.1 本次结果

| 测试 | 结果 | 证据边界 |
|---|---|---|
| `python3 scripts/test_graph_scenario_fixture.py` | `PASS` | `CASE006_GRAPH_TEXTBOOK_SCENARIO_OK` |
| `python3 scripts/test_api_contract.py` | `PASS` | API 74 routes |
| 图谱客户端归一化 | `PASS` | 1 个 `knowledge graph` Vitest 测试 |
| 图谱 Mock 浏览器 | `OBSERVED_PASS` | 1/1，搜索、节点详情和邻接流程 |
| 图谱 a11y | `OBSERVED_PASS` | 1/1，键盘可操作控件 |
| 正式图谱/PDF/角色/六视口人工验收 | `BLOCKED_INPUT` | 外部数据和正式环境未提供 |

### 73.2 构筑后审查结论

BUILD-030 metadata 已更新为 `run_id=BUILD-030-20260725-02`、`attempt=2`、`authoritative_result=true`，并 supersede attempt 1。当前本地增量证据可信，但 `BUILD-030` 继续保持 `PARTIAL_IMPLEMENTATION_PENDING_GATE`，不能将本地节点网格当作正式图谱发布通过。

## 74. 2026-07-25 BUILD-040 资源阅读与进度 attempt 2 本地回归

本节记录资源阅读器和用户级进度闭环的本次本地回归。课程 PDF 当前仍未挂载，因此测试重点是服务端挂载状态、进度幂等/版本/CSRF 边界和前端不伪造阅读内容。

### 74.1 本次结果

| 测试 | 结果 | 证据边界 |
|---|---|---|
| `scripts.test_course_store` | `PASS` | Store 7/7，用户隔离和乐观版本冲突 |
| `scripts/test_resource_progress_api.py` | `PASS` | `RESOURCE_PROGRESS_API_OK`，CSRF、幂等、403/404/409 边界 |
| API 契约 | `PASS` | 74 routes |
| 资源阅读器前端选择测试 | `PASS` | 6 tests |
| 资源阅读器 Mock 浏览器 | `OBSERVED_PASS` | 1/1，`pending_mount` 且没有伪造 PDF iframe |
| 真实 PDF 首屏/pluginfile | `BLOCKED_INPUT` | 20 个课程 PDF 和正式 Moodle 文件权限缺失 |

### 74.2 构筑后审查结论

BUILD-040 metadata 已更新为 `run_id=BUILD-040-20260725-02`、`attempt=2`、`authoritative_result=true`，并 supersede attempt 1。本地资源进度实现达到观察性通过，但 `BUILD-040` 继续 `IMPLEMENTED_PENDING_GATE`，不能将 pending_mount 或 Mock 资源状态当作真实教材验收。

## 75. 2026-07-25 BUILD-050 作业、评分与多标签 attempt 2 本地回归

本节记录作业草稿、最终提交、截止时间、客观评分、主观题 Agent 初评、教师复核和多标签版本冲突的本次本地回归。所有写操作使用隔离数据库和幂等键；真实 Moodle 成绩回写、正式时间环境和三角色浏览器仍未执行。

### 75.1 本次结果

| 测试 | 结果 | 证据边界 |
|---|---|---|
| `scripts.test_course_store` | `PASS` | Store 7/7，草稿/评分/用户隔离规则 |
| `test_assignment_draft_api.py` | `PASS` | 草稿保存、重复幂等、版本冲突、学生答案隔离 |
| `test_assessment_api.py` | `PASS` | 截止拒绝、尝试次数、提交幂等、评分和教师复核 |
| API 契约 | `PASS` | 74 routes |
| 作业相关前端测试 | `PASS` | 5 tests |
| 学生草稿/教师评分/双标签浏览器 | `OBSERVED_PASS` | 3/3 Mock 流程，旧版本写入返回 409 |
| Moodle 成绩回写/正式截止环境/真实角色 | `BLOCKED_INPUT` | 外部 bridge、账号和环境未提供 |

### 75.2 构筑后审查结论

BUILD-050 metadata 已更新为 `run_id=BUILD-050-20260725-02`、`attempt=2`、`authoritative_result=true`，并 supersede attempt 1。本地作业闭环达到观察性通过，但 `BUILD-050` 继续 `IMPLEMENTED_PENDING_GATE`，不能将 Mock 成绩或本地教师复核当作 Moodle 正式成绩回写。

## 76. 2026-07-25 BUILD-060 attempt 2 测试方案落地与构筑后审查

本节把“每次构筑之后的审查、测试和验收”协议实际应用到 BUILD-060 attempt 2。此次只重测社交/活动代码和证据变更影响的范围；不把共享前端门禁或历史 attempt 1 输出重复计入本批次。

### 76.1 构筑前锁定条件

构筑开始前必须在 `acceptance/frontend/BUILD-060/` 固定以下身份和范围：

| 项目 | 本次值 | 缺失时处理 |
|---|---|---|
| `run_id` | `BUILD-060-20260725-02` | 不允许开始计分 |
| `attempt` | `2`，覆盖 `BUILD-060-20260725-01` | 旧结果只能标记 `HISTORICAL/SUPERSEDED` |
| 前置门禁 | `BUILD-000 = BLOCKED_INPUT` | 允许做数据无关的局部测试，但不得关闭正式 BUILD-060 |
| 环境 | `local-mock-and-isolated-api`，独立数据库、资源目录和端口 | 不能证明真实 Moodle 或正式 API |
| 敏感信息 | `secrets_recorded=false` | 发现实际密钥、Cookie、签名 URL 或学生数据即停止归档 |

### 76.2 T0-T6 可执行测试矩阵

每一层必须记录命令、退出码、测试 ID、运行号、环境和证据路径。任何适用层缺少退出码或证据，T6 自动为 `REVIEW_REQUIRED`。

| 层级 | 本批次测试 | 验收条件 | 本次结果 |
|---|---|---|---|
| T0 输入/前置 | 检查前置门禁、隔离数据库/资源目录、Mock 开关、密钥脱敏状态 | 前置和环境边界可复现；真实输入缺失必须显式阻断 | `PASS`，前置仍为 `BLOCKED_INPUT` |
| T1 静态/契约 | `python3 scripts/test_api_contract.py` | 退出码 0，路由和本地 manifest 一致 | `PASS`，74 routes |
| T2 服务/API | `test_social_api.py`、`test_activity_api.py` | 权限、对象归属、XSS、CSRF、幂等、审计、一次性提交、聚合结果均通过 | `PASS` |
| T3 前端单元/组件 | `cd frontend && npm run test:all -- --run` | 5 files、30 tests 全部退出码 0；不得以定向 skipped 替代全量回归 | `PASS` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1 --grep "student can create and reply to a discussion\|teacher can publish a notification\|student can submit a poll"` | 学生发帖/回复、教师通知/学生已读、投票提交/刷新聚合 3/3 通过 | `OBSERVED_PASS`，3/3 |
| T5 安全/可访问性/真实边界 | 检查 Mock 与真实模式分界、无假成功、无敏感值；正式角色、正式 axe、六视口人工和审计环境 | 隔离结果只能为 `OBSERVED_PASS`；未提供的真实条件必须阻断 | `OBSERVED_PASS`，真实项 `BLOCKED_INPUT` |
| T6 审查/回退/归档 | 审查代码、迁移和回退说明；交叉核对 metadata、review、输出和人工记录 | 所有文件共享 run_id；回退边界明确；真实门禁齐全才可 `PASS` | `REVIEW_REQUIRED` |

### 76.3 本次权威命令和结果

以下结果只属于 `BUILD-060-20260725-02`，并已写入 `acceptance/frontend/BUILD-060/test-output.txt`：

```text
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_social_api.py -> PASS (exit 0)
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_activity_api.py -> PASS (exit 0)
python3 scripts/test_api_contract.py -> PASS (API_CONTRACT_OK routes=74; exit 0)
cd frontend && npm run test:all -- --run -> PASS (5 files, 30 tests; exit 0)
cd frontend && npm run test:e2e:mock -- --workers=1 --grep "student can create and reply to a discussion|teacher can publish a notification|student can submit a poll" -> OBSERVED_PASS (3/3; exit 0)
```

### 76.4 构筑后代码和产品审查

| 审查项 | 结论 | 关闭条件 |
|---|---|---|
| 讨论/通知/活动对象归属 | 隔离 API `PASS` | 真实 Moodle capability 和跨课程数据验收仍需通过 |
| 角色权限、CSRF、幂等和 XSS | 隔离 API/Mock `PASS` | 真实 sesskey、正式网关和审计日志复核 |
| 学生活动一次性提交与刷新恢复 | 隔离 API + 3/3 Mock `OBSERVED_PASS` | 真实学生/教师账号和正式持久化环境 |
| 历史结果边界 | 已修正 | attempt 1 只保留 `HISTORICAL/SUPERSEDED`，当前批次只统计 attempt 2 |
| 回退和迁移 | 代码范围可回退，正式演练未完成 | 隔离备份恢复和正式部署回退均需有退出码 |
| 发布门禁 | 不允许关闭 | `BUILD-000`、课程 PDF、正式 API、真实角色和人工验收仍缺失 |

### 76.5 本次验收结论

`BUILD-060-20260725-02` 的隔离 API、前端全量测试和三条目标 Mock 流程满足本次局部验收，状态为 `OBSERVED_PASS_WITH_EXTERNAL_BLOCKERS`。T6 保持 `REVIEW_REQUIRED`，BUILD-060 保持 `IMPLEMENTED_PENDING_GATE`，最终发布保持 `blocked`。不能将 3/3 Mock 浏览器流程表述为真实 Moodle 三角色通过。

## 77. 2026-07-25 测试方案进一步审查

### 77.1 已确认的计划强制规则

本次复审检查了第 27、68、76 节，以及 BUILD-060 的六类标准证据文件。结果确认：

1. 每次构筑都有唯一 `run_id`、`attempt`、`authoritative_result` 和 `supersedes`；
2. T0-T6 有明确状态，`OBSERVED_PASS`、`BLOCKED_INPUT` 和 `REVIEW_REQUIRED` 不会被升级为正式 `PASS`；
3. 当前权威命令、退出码和历史结果边界可在单一输出文件中区分；
4. API、浏览器、权限、安全、可访问性、真实环境和回退证据分别记录，不能用一类证据覆盖另一类门禁；
5. 代码、配置、夹具或依赖变化后，必须从最早受影响层开始并补跑 T1-T6；课程资料恢复后必须从 BUILD-000/T0 重新执行；
6. 证据路径存在性、敏感值扫描和跨文件 run_id 一致性由 `scripts/validate_project_progress.py` 机器检查。

### 77.2 复审发现

| ID | 严重度 | 状态 | 结论 |
|---|---|---|---|
| `PLAN-TEST-009` | P1 | `CLOSED` | BUILD-060 attempt 2 已把三条目标 Mock 浏览器流程作为独立命令执行并记录为 `OBSERVED_PASS 3/3`，不是共享全量结果的重复引用 |
| `PLAN-RECORD-002` | P1 | `CLOSED` | attempt 1 的 62 routes、8/8 和受限环境失败已显式标记 `HISTORICAL/SUPERSEDED`，当前权威块只含 74 routes、30 tests 和 3/3 |
| `PLAN-ACCEPT-001` | P1 | `CLOSED` | BUILD-060 的局部验收条件已写到 T0-T6 表格，包含命令、退出码、通过阈值、阻断处理和证据位置 |
| `PLAN-EVIDENCE-001` | P1 | `OPEN` | `api-test-manifest.yaml`、`openapi.test.json` 仍是 local-isolated-adapter 契约，不是正式 Moodle 契约 |
| `DATA-INPUT-001` | P0 | `OPEN` | manifest 要求的 20 个课程 PDF 仍缺失，BUILD-000 仍在 `BLOCKED_INPUT` |
| `BUILD060-REAL-001` | P0 | `OPEN` | 真实 Moodle 三角色、正式审计、正式可访问性和六视口人工验收仍未执行 |

### 77.3 审查后的下一步

资料输入恢复后，必须依次执行：课程 manifest/hash/page_count 校验、知识库生命周期、真实 Moodle 三角色和 BUILD-000 全量验收；然后按受影响范围重跑 BUILD-010、030、040、050、060、070、080、090、100 的 T0-T6。未取得正式 API/OpenAPI、账号、Workflow/知识库版本、HTTPS 和恢复演练证据前，计划只能报告局部完成，不能报告最终发布通过。

## 78. 2026-07-25 本地进度配置与标准证据身份校验强化

本节继续落实“在本地维护一份详细配置文件”的要求。此前校验器已检查 metadata、T0-T6、退出码、证据路径和敏感值；本轮进一步要求每个 BUILD 的五类标准证据文件都必须引用 metadata 中同一个 `run_id`。

### 78.1 校验范围

对 `acceptance/frontend/BUILD-*` 的 11 个批次逐一检查：

```text
scope.md
review.md
test-output.txt
manual-acceptance.md
rollback.md
```

共 55 份文件。缺失文件、文件不可读或运行号不一致都会使 `scripts/validate_project_progress.py` 退出非零。该检查只验证配置与证据身份，不把局部测试结果升级为产品门禁通过。

### 78.2 本次结果

| 检查 | 结果 | 证据 |
|---|---|---|
| BUILD-020/070/080/090/100 运行号补齐 | `PASS` | 各批次 scope/rollback 已与 metadata 对齐 |
| 校验器回归 | `PASS` | `scripts.test_validate_project_progress`：6/6 |
| 标准证据交叉检查 | `PASS` | `STANDARD_EVIDENCE_RUN_ID_OK builds=11 artifacts=55` |
| 账本解析、证据路径和脱敏 | `PASS` | `PROJECT_PROGRESS_VALIDATION_OK metadata=11 blockers=19 evidence_refs=88 redaction_scan=PASS` |
| 差异检查 | `PASS` | `git diff --check` |

### 78.3 构筑后审查结论

本地配置文件和标准证据的身份一致性门禁已加强，`PLAN-EVIDENCE-002` 关闭。课程 PDF、正式 Moodle/API 契约、真实角色、真实 Workflow、Spark 鉴权负向、Docker/HTTPS、备份恢复和人工可访问性仍是独立阻断项。当前正式门禁仍为 `BUILD-000 = BLOCKED_INPUT`，最终发布仍为 `blocked`；资料或正式环境恢复后必须按第 27、68、77 节从受影响的最早层重新执行。

## 79. 2026-07-25 本地隔离全量回归与知识库输入阻断改进

### 79.1 回归范围

本轮执行了不依赖课程 PDF 的隔离矩阵：API/契约、Store、资源进度、作业草稿、评测、教师工作台、教师资源、讨论通知、课堂活动、管理员工作台、Agent 边界/上下文、Adapter 运行时、固定验收夹具、图谱夹具、讯飞本地 HTTP 夹具、前端硬化、Mock 性能，以及前端 lint、typecheck、Vitest 全量和生产构建。

### 79.2 结果和验收条件

| 范围 | 结果 | 验收边界 |
|---|---|---|
| API/Adapter/业务矩阵 | `PASS` | 所有命令退出码 0；只使用临时数据库和隔离资源目录 |
| 前端工程化 | `PASS` | lint、typecheck、Vitest 30/30、构建 1694 modules |
| 讯飞本地协议夹具 | `PASS` | `XINGCHEN_SMOKE_SCRIPT_FIXTURE_OK`，只验证本地请求/响应解析 |
| Mock 性能 | `PASS` | 30 samples，p50 38.74ms，p95 49.69ms；不代表真实 Workflow 性能 |
| 知识库生命周期 | `BLOCKED_INPUT` | 缺少首个 manifest PDF，退出码 2，输出 `KB_LIFECYCLE_BLOCKED_INPUT` |
| 完整正式验收 | `BLOCKED_INPUT` | 课程 manifest/hash/page_count、真实 Moodle、正式 API、知识库和角色环境仍缺失 |

### 79.3 代码审查与构筑后结论

`test_kb_lifecycle.py` 的受控阻断改进关闭了“缺失课程输入导致裸异常、无法归档”的 P1 质量问题；它没有改变正式门禁判断，也没有弱化缺失 PDF 的失败语义。BUILD-000 继续 `BLOCKED_INPUT`，后续资料恢复时仍必须从 manifest/hash/page_count 和 T0 重新执行，不能只重跑知识库测试或前端 Mock 流程。

## 80. 2026-07-25 课程数据校验器受控门禁与完整验收停止条件

### 80.1 变更

`scripts/verify_course_data.py` 现在对课程数据缺失和课程数据内容错误使用不同的机器可识别结果：

| 条件 | 输出 | 退出码 | 处理 |
|---|---|---:|---|
| manifest/graph/PDF 等必需输入缺失 | `COURSE_DATA_BLOCKED_INPUT` | 2 | 保持 BUILD-000 阻断，等待外部输入 |
| hash、page_count、图谱结构或来源标记不一致 | `COURSE_DATA_VERIFY_FAIL` | 1 | 资料校验失败，禁止继续发布 |
| 全部基线通过 | JSON 摘要 | 0 | 才能继续后续知识库和完整 local acceptance |

### 80.2 本次测试和结果

```text
python3 -m unittest -q scripts.test_verify_course_data -> PASS (2 tests)
python3 scripts/verify_course_data.py course-data/normalized -> BLOCKED_INPUT (exit 2)
bash scripts/run_local_acceptance.sh -> BLOCKED_INPUT (exit 2 at course data baseline)
PYTHONPATH=/tmp/jbgs-agent-deps:$PWD/agent-adapter python3 scripts/test_kb_lifecycle.py -> BLOCKED_INPUT (exit 2)
```

当前受控结果为：`COURSE_DATA_BLOCKED_INPUT missing PDF: chapter-1-1.1-.pdf`。该结果证明停止条件可复现，不证明课程数据通过；不得生成占位 PDF，不得修改 manifest、hash 或 page_count。

### 80.3 构筑后审查结论

`PLAN-TEST-011` 关闭。课程资料恢复后必须先重新运行课程数据校验器并取得退出码 0，再运行知识库生命周期、完整 local acceptance 和受影响 BUILD 的 T0-T6；任何退出码 1/2 都禁止进入正式发布判定。当前 `BUILD-000 = BLOCKED_INPUT`，最终发布继续 `blocked`。

## 81. 2026-07-25 本地配置工作树快照新鲜度校验

### 81.1 校验规则

`PROJECT_PROGRESS.yaml` 记录 `snapshot.working_tree.observed_git_status`，包括 `tracked_modified_count`、`untracked_count` 和 `total_count`。`scripts/validate_project_progress.py` 每次运行都执行 `git status --short`，若计数与配置不一致则退出非零，要求先更新配置再归档新的测试结果。路径列表作为人工索引保留，计数是机器门禁的权威值。

### 81.2 本次结果

| 检查 | 结果 |
|---|---|
| 账本校验器回归 | `PASS 7/7` |
| 进度账本验证 | `PROJECT_PROGRESS_VALIDATION_OK metadata=11 blockers=19 evidence_refs=90 redaction_scan=PASS` |
| 工作树快照 | `PASS tracked_modified=22 untracked=27 total=49` |
| Python 编译 | `PASS` |

### 81.3 审查结论

`PLAN-LEDGER-003` 关闭。以后代码、文档、证据或测试文件发生变化时，必须重新记录快照计数并通过账本校验；该机制只提高本地配置可信度，不把任何 Mock、隔离或局部回归升级为正式产品通过。课程 PDF、正式 API/Workflow、真实角色、Docker/HTTPS、恢复和人工验收仍未闭合。

## 82. 2026-07-25 前端浏览器与发布安全夹具复测

### 82.1 本次结果

| 门禁 | 结果 | 范围 |
|---|---|---|
| Mock 浏览器 | `OBSERVED_PASS` | 20/20，学生、教师、管理员、Agent、图谱、作业和多标签流程 |
| 自定义可访问性 | `OBSERVED_PASS` | 3/3，控件命名、键盘焦点、对比度和移动布局 |
| axe | `OBSERVED_PASS` | 4/4，main 默认规则集 |
| 标准 smoke | `OBSERVED_PASS` | 2/2，1440x900 与 390x844 |
| HTTP Workflow 夹具 | `PASS` | 本地回环请求、Authorization、SSE token/source/done、来源页码 |
| 备份安全夹具 | `PASS` | 3/3，正常归档通过、明文 Secret 和归档 Secret 拒绝 |

### 82.2 日志边界审查

`playwright.a11y.config.ts` 和标准 smoke 配置故意不启动 Adapter，以验证预览/服务不可用/错误态仍然诚实显示；因此 Vite 日志中的 `127.0.0.1:8081 ECONNREFUSED` 是预期环境边界。由于断言明确验证预览或错误状态，本次记为 `OBSERVED_PASS`，不是 API 集成通过，也不能替代 `test:e2e:mock`、真实 Moodle 或正式人工辅助技术验收。

### 82.3 构筑后审查结论

`PLAN-TEST-012` 关闭。本地浏览器、HTTP 夹具和备份安全证据已更新；正式 Moodle 三角色、正式 axe/屏幕阅读器、HTTPS、真实 Workflow、课程资料和恢复演练仍阻断 BUILD-000/最终发布。

## 83. 2026-07-25 Spark Assistant 正向与鉴权负向最新复测

### 83.1 结果

| 用例 | 结果 | 机器证据 |
|---|---|---|
| 合法签名正向 WebSocket | `PASS` | handshake 101、header code 0、15 帧、结束帧有效、close 1000 |
| 无权限 APPID | `PASS` | error code 11200、无最终正常回答 |
| 错误 API Key | `FAIL` | handshake 101、最终 code 0、仍出现最终回答 |
| 错误 API Secret | `FAIL` | handshake 101、最终 code 0、仍出现最终回答 |
| 篡改签名时间 | `FAIL` | handshake 101、最终 code 0、仍出现最终回答 |

### 83.2 构筑后审查

本轮确认正向协议可用，但不能把协议连通当作凭据鉴权通过。`SPARK-AUTH-FAIL-001` 继续为 P0 `FAIL`，发布决策为 `STOP_RELEASE`。在供应方确认 endpoint、Assistant 权限绑定、签名版本和错误语义前，不再扩大真实内容、并发或性能发布结论；本地离线签名构造测试也不能覆盖远端拒绝语义。

## 84. 2026-07-25 前端容器构建 context 修正与依赖复测

### 84.1 发现和修正

前端 Dockerfile 使用 `COPY package*.json ./`，因此正确构建 context 是 `frontend/`，而不是仓库根目录。此前根 context 构建会发送约 193.9MB，并在网络恢复后继续触发 package 文件路径风险。本轮完成：

- 前端构建命令改为 `docker build --file frontend/Dockerfile --build-arg VITE_BASE_PATH=/learn/ frontend/`；
- 新增 `frontend/.dockerignore`，排除 `node_modules`、`dist`、测试产物和 TypeScript 构建缓存；
- 根 `.dockerignore` 增加同类前端产物排除，保护其他根 context 构建。

修正后 context 约 587.8kB，Dockerfile 的 context/COPY 边界已正确；这项修正不替代基础镜像拉取。

### 84.2 本次结果

| 检查 | 结果 | 说明 |
|---|---|---|
| Docker Server | `PASS` | 29.1.3 |
| Compose 静态配置 | `PASS` | `docker compose ... config --no-interpolate --no-consistency` |
| 修正后的前端镜像构建 | `BLOCKED_DEPENDENCY` | `node:22-alpine` manifest 请求 Docker Hub 超时 |
| 容器健康/Nginx/header/路由 | `NOT_RUN` | 没有生成镜像，禁止伪造运行结果 |

### 84.3 构筑后审查结论

`BUILD100-CONTAINER-002` 关闭：本地 Dockerfile context 和忽略规则问题已修正。`FRONTEND-CONTAINER-001` 继续 `BLOCKED_DEPENDENCY`，待镜像缓存、可信 registry 或稳定网络后，从修正后的命令重新构建，并继续执行容器健康、Nginx header、`/learn/` 回退和 API no-store 验收。

## 85. 2026-07-25 前端容器静态契约门禁

### 85.1 测试内容

新增 `scripts/test_frontend_container_contract.py`，不依赖 Docker daemon 或外部镜像，检查：

- Dockerfile 的 Node 构建阶段、`npm ci`、`VITE_BASE_PATH`、生产构建和 Nginx 第二阶段；
- `frontend/` 正确构建 context 与 node_modules/dist/测试产物排除；
- Nginx `/api/` 代理、API `no-store`、静态资源 immutable 缓存和 SPA 回退；
- Compose frontend context、healthcheck、`agent-adapter` healthy 依赖和 Caddy 依赖。

### 85.2 结果与边界

```text
python3 scripts/test_frontend_container_contract.py -> PASS (4 tests; FRONTEND_CONTAINER_CONTRACT_OK)
bash scripts/run_local_acceptance.sh -> BLOCKED_INPUT (exit 2 after static contract, at missing chapter-1-1.1-.pdf)
```

静态契约 `PASS` 只证明配置和源码边界一致，不证明镜像已构建或运行。Docker Hub 基础镜像超时仍由 `FRONTEND-CONTAINER-001` 管理，健康检查、Nginx header、`/learn/` 回退、API no-store 和 HTTPS 必须在镜像生成后执行。

### 85.3 构筑后审查结论

`BUILD100-CONTAINER-003` 关闭。完整 local acceptance 的执行顺序现在先验证容器契约，再验证课程数据；任何课程资料或镜像依赖阻断都不会被静态绿色结果覆盖。

## 86. 2026-07-25 提交代码归档纳入学习通式前端与材料复审

### 86.1 发现和修正

提交归档脚本的显式 allow-list 原先包含 legacy `agent-ui`，但遗漏当前学习通式 React `frontend/`。本轮将 `frontend/` 纳入归档，并排除 `dist`、`.vite`、coverage、TypeScript 增量缓存等本地生成物，防止代码包缺失主前端或携带无关产物。

### 86.2 结果

| 检查 | 结果 |
|---|---|
| 代码归档生成 | `PASS`，`SUBMISSION_CODE_ARCHIVE_READY` |
| 前端主代码进入归档 | `PASS`，57 个 frontend 成员 |
| SHA-256 | `PASS` |
| Secret-like 成员扫描 | `PASS` |
| dist/.vite/tsbuildinfo 排除 | `PASS` |
| 正式提交材料 | `BLOCKED_INPUT`，缺少 3 项真实材料 |

缺失项为正式 HTTPS Demo URL、真实 `demo-video.mp4` 和真实人工验收汇总。禁止用 README、Mock 输出、空文件或占位文本关闭材料门禁。

### 86.3 构筑后审查结论

`BUILD100-SUBMISSION-ARCHIVE-002` 关闭：代码包完整性问题已修正。代码归档通过不等于最终提交通过；真实材料和所有 P0/P1 外部门禁完成后仍需重新运行提交材料检查和第 27 节 T0-T6 审查。

## 87. 2026-07-25 本地进度快照刷新工具与配置维护审查

### 87.1 工具边界

新增 `scripts/refresh_progress_snapshot.py`，从 `git status --short` 计算 tracked 修改数、untracked 数和总数，并只更新 `PROJECT_PROGRESS.yaml` 的：

```text
snapshot.working_tree.observed_git_status.tracked_modified_count
snapshot.working_tree.observed_git_status.untracked_count
snapshot.working_tree.observed_git_status.total_count
```

工具拒绝缺失或重复字段，保留 YAML 其他内容；刷新后仍必须运行账本校验器，不能用刷新动作掩盖测试或产品状态变化。

### 87.2 本次结果

```text
python3 scripts/refresh_progress_snapshot.py -> PASS (tracked_modified=23 untracked=30 total=53)
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data -> PASS (11 tests)
python3 scripts/validate_project_progress.py -> PASS (metadata=11 blockers=19 evidence_refs=102 redaction_scan=PASS)
```

### 87.3 构筑后审查结论

`PLAN-LEDGER-004` 关闭。配置文件维护现在具备“刷新、回归、校验”闭环；它只提高本地进度记录的可维护性，不关闭课程 PDF、正式 API/Workflow、真实角色、容器、HTTPS、恢复或提交材料阻断。

## 88. 2026-07-25 Spark 鉴权负向构造审查

### 88.1 审查结论

本轮检查 `test_spark_assistant_ws.py`、`test_spark_assistant_auth_negative.py` 和离线契约测试，确认：

- 正向签名使用 `host`、RFC1123 `date`、`GET path HTTP/1.1` 和 HMAC-SHA256；
- 错误 API Key/Secret 会在变异后重新生成对应签名；
- 篡改 date 保留原授权签名，只修改 URL date 参数，能够检验签名材料不一致；
- 无权限 APPID 只修改业务帧 `header.app_id`，保持合法 URL 签名，独立检验权限绑定。

### 88.2 结果

```text
python3 -m unittest -q scripts.test_spark_assistant_contract -> PASS (7 tests)
python3 -m compileall -q scripts/test_spark_assistant_ws.py scripts/test_spark_assistant_auth_negative.py scripts/test_spark_assistant_contract.py -> PASS
```

因此本地负向构造不是当前 P0 失败的原因；真实端点对错误 key/secret/date 仍返回最终 `code=0`，该结果继续作为供应方协议/凭据绑定问题记录。`SPARK-AUTH-FAIL-001` 保持 `FAIL`，发布决策保持 `STOP_RELEASE`。

## 89. 2026-07-25 提交归档串行新鲜度复测

### 89.1 本次顺序

提交归档会改变工作树的归档/校验文件状态，因此本轮固定顺序为：

```text
refresh_progress_snapshot.py
package_submission_code.sh
tar member/exclusion check
sha256sum -c
check_submission_materials.sh
validate_project_progress.py
```

不允许并行读取快照和生成归档；并行结果只作为 `NOT_AUTHORITATIVE`，不能写入正式账本摘要。

### 89.2 结果

| 检查 | 结果 |
|---|---|
| 工作树快照 | `PASS 24/30/54` |
| 代码归档 | `PASS`，包含 frontend 和新增测试/配置脚本 |
| 构建产物排除 | `PASS` |
| SHA-256/Secret 扫描 | `PASS` |
| 正式提交材料 | `BLOCKED_INPUT`，缺少 3 项真实材料 |

### 89.3 构筑后审查结论

`BUILD100-SUBMISSION-ARCHIVE-003` 关闭。归档和快照维护具有明确的串行边界；代码包通过不等于正式提交通过，真实材料和其他 P0/P1 外部门禁仍必须完成。

## 90. 2026-07-26 外部门禁日检与配置日期更新

### 90.1 复核项目

本次重新检查课程 PDF 输入、下载目录候选课件、Docker Server/基础镜像条件、正式提交材料和 `PROJECT_PROGRESS.yaml` 账本。复核为只读操作，不修改课程 manifest、hash、page_count、密钥或提交材料。

### 90.2 结果

| 门禁 | 结果 |
|---|---|
| 课程 PDF | `BLOCKED_INPUT`，归一化目录 0 个，首个缺失 `chapter-1-1.1-.pdf` |
| Docker | `BLOCKED_DEPENDENCY`，Server 29.1.3 可访问，基础镜像/registry 仍未就绪 |
| 正式提交材料 | `BLOCKED_INPUT`，缺 URL、视频、人工汇总 3 项 |
| 本地进度账本 | `PASS`，metadata 11、blockers 19、evidence_refs 108、脱敏通过 |

### 90.3 审查结论

`DAILY-GATE-20260726-001` 关闭。配置快照日期更新为 2026-07-26，但产品门禁不因日期变化而升级；外部输入恢复后仍必须从 BUILD-000/T0 重新执行。

## 91. 2026-07-26 README 本地进度维护入口

### 91.1 交接要求

README 现在明确本地配置和测试记录的权威入口：

```bash
python3 scripts/refresh_progress_snapshot.py
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data
python3 scripts/validate_project_progress.py
```

证据目录为 `acceptance/frontend/BUILD-*/`；课程资料缺失时完整验收必须保留 `COURSE_DATA_BLOCKED_INPUT`/退出码 2，不得用占位 PDF、Mock 结果或空提交材料覆盖前置门禁。

### 91.2 本次验证

| 检查 | 结果 |
|---|---|
| 快照刷新 | `PASS 24/30/54` |
| 配置维护回归 | `PASS 11 tests` |
| 账本校验 | `PASS metadata=11 blockers=19 evidence_refs=110 redaction_scan=PASS` |
| README 命令路径 | `PASS` |

### 91.3 审查结论

`DOCS-MAINT-20260726-001` 关闭。README、计划、账本和证据目录的本地维护入口已对齐；这不改变任何正式产品门禁状态。

## 92. 2026-07-26 测试方案落地后的计划与账本唯一性审查

### 92.1 审查目的和范围

本轮把“每次构筑之后的审查、测试、验收和证据归档”进一步落到配置质量门禁。审查范围包括：

- `plan_review.scope` 中的路径是否唯一；
- `plan_review.findings`、`test_runs` 和 `known_blockers` 的 ID 是否唯一；
- 当前构筑、最新前端复测和计划审查版本是否指向同一批次；
- 测试运行号、证据路径、T0-T6 规则和当前 `BUILD-000` 门禁是否一致；
- 脱敏扫描、工作树快照、静态容器契约和语法检查是否在构筑后重新执行。

唯一性是配置可信度条件，不是产品功能通过条件。任何重复路径或 ID 都必须使账本校验失败，不能依靠人工阅读猜测“最新”记录。

### 92.2 构筑后测试方案和验收条件

本批次固定按以下顺序执行；每次新增代码、计划、证据或测试文件后都要刷新快照，再重新执行本表：

| 层级 | 命令/检查 | 通过条件 | 本次结果 |
|---|---|---|---|
| T0 变更和范围审查 | 审查计划、账本、证据目录和外部阻断边界 | 变更范围明确；无秘密值；正式门禁不被本地结果升级 | `PASS` |
| T1 语法和配置 | `python3 -m compileall -q scripts agent-adapter`；`bash -n scripts/*.sh`；`git diff --check` | 三项退出码均为 0 | `PASS` |
| T2 账本回归 | `python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract` | 19/19；重复路径、finding/run/blocker ID 夹具均能被拒绝 | `PASS` |
| T3 进度和证据校验 | `python3 scripts/validate_project_progress.py` | `PROJECT_PROGRESS_VALIDATION_OK`；metadata=11；证据路径存在；脱敏通过；无重复标识 | `PASS` |
| T4 前端发布契约 | `python3 scripts/test_frontend_container_contract.py` | 4/4；context、Dockerfile、Nginx、Compose 依赖规则一致 | `PASS` |
| T5 外部/人工验收 | 真实 PDF、Moodle 三角色、正式 API/Workflow、Docker runtime、HTTPS、辅助技术和恢复演练 | 必须有真实环境命令、退出码和人工记录；当前输入不足 | `BLOCKED_INPUT` |
| T6 复审和归档 | 交叉核对 run_id、证据路径、快照、当前 gate 和回退边界 | 账本一致且外部门禁真实完成才可正式 PASS | `REVIEW_REQUIRED` |

### 92.3 本次权威运行和证据

```text
run_id: config-identifier-audit-20260726-03
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract -> PASS (19 tests)
python3 scripts/validate_project_progress.py -> PROJECT_PROGRESS_VALIDATION_OK metadata=11 blockers=19 evidence_refs=114 redaction_scan=PASS
python3 scripts/test_frontend_container_contract.py -> FRONTEND_CONTAINER_CONTRACT_OK (4 tests)
python3 -m compileall -q scripts agent-adapter -> PASS
bash -n scripts/*.sh -> PASS
git diff --check -> PASS
```

机器证据见 `acceptance/frontend/BUILD-000/config-identifier-audit-20260726-03.txt`。证据只记录状态、退出码、计数、运行号和错误类别，不记录 API Key、API Secret、Cookie、Authorization、签名 URL、完整题目/答案或真实学生数据。

### 92.4 构筑后审查结论

`PLAN-LEDGER-005` 关闭。计划和进度账本现在明确拒绝重复 scope 路径和重复 ledger ID，并将这一规则纳入每次构筑后的 T2/T3/T6 验收。`BUILD-000` 仍为 `BLOCKED_INPUT`，最终发布仍为 `blocked`；课程 PDF、真实角色、正式 API/OpenAPI、Spark 错误凭据拒绝语义、Docker 运行时、HTTPS、恢复演练和人工验收仍不能以本地配置绿色结果替代。

新增或修改计划、账本、测试或证据后，下一次操作顺序仍为：

```bash
python3 scripts/refresh_progress_snapshot.py
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract
python3 scripts/validate_project_progress.py
```

## 93. 2026-07-26 当前工作树前端与本地验收复测

### 93.1 本次构筑范围

本轮针对当前工作树执行前端工程、已实现教学 API、Agent 边界、Mock 浏览器、可访问性、发布硬化、容器静态契约和完整本地验收复测。浏览器测试在允许本地回环监听的环境执行；没有把沙箱中的 `listen EPERM` 或并发 webServer 启动冲突记录为产品失败。

### 93.2 T0-T6 结果和验收条件

| 层级 | 验收条件 | 本次结果 |
|---|---|---|
| T0 范围和代码审查 | 当前工作树、测试配置、Mock/正式边界和敏感信息规则明确 | `PASS` |
| T1 工程构筑 | lint、typecheck、生产构建成功，构建产物 1694 modules | `PASS` |
| T2 API 和领域规则 | API 74 routes，Agent boundary/context、教师和管理员工作台测试通过 | `PASS` |
| T3 前端自动化 | Vitest 30/30，前端 hardening 和 container contract 4/4 | `PASS` |
| T4 浏览器和可访问性 | Mock 20/20、a11y 3/3、axe 4/4、smoke 2/2 | `OBSERVED_PASS` |
| T5 完整验收和材料 | 课程数据必须有 manifest 匹配 PDF；正式材料必须齐全 | `BLOCKED_INPUT` |
| T6 复审和发布 | 所有外部 P0/P1 门禁、真实角色和正式材料完成后才可正式 PASS | `REVIEW_REQUIRED` |

### 93.3 构筑后审查

本轮确认前端和本地隔离实现没有新的断言失败。a11y 与标准 smoke 配置按设计不启动 Adapter，因此日志中的 `127.0.0.1:8081 ECONNREFUSED` 是测试预期的错误态输入；测试断言验证了错误/预览状态，不能表述为 API 集成通过。Mock 浏览器使用独立端口、数据库和资源目录，20 个流程覆盖学生、教师、管理员、作业、讨论、活动、资源修订、知识库、Agent 重试/取消和多标签冲突。

完整 `RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh` 在课程基线以 `COURSE_DATA_BLOCKED_INPUT`、退出码 2 停止，首个缺失文件为 `chapter-1-1.1-.pdf`；没有生成占位 PDF，也没有修改 manifest、hash 或 page_count。提交材料检查仍缺正式 HTTPS Demo URL、真实视频和人工验收汇总 3 项。

### 93.4 权威运行和结论

```text
run_id: frontend-local-revalidation-20260726-04
frontend: lint PASS; typecheck PASS; Vitest 30/30; build 1694 modules
backend/local: API 74 routes; Agent boundary/context/teacher/admin PASS
browser: Mock 20/20; a11y 3/3; axe 4/4; smoke 2/2
hardening/container: PASS; container contract 4/4
full local acceptance: BLOCKED_INPUT exit 2
submission materials: BLOCKED_INPUT missing 3
current gate: BUILD-000 BLOCKED_INPUT
final release: blocked
```

证据见 `acceptance/frontend/BUILD-090/frontend-local-revalidation-20260726-04.txt`。本轮关闭 `PLAN-TEST-015` 的本地复测项，但不关闭课程输入、正式 Moodle/API/Workflow、Spark 鉴权负向、Docker/HTTPS、恢复、人工可访问性或提交材料门禁。

## 94. 2026-07-26 BUILD-040 资料收藏与页码笔记构筑后审查

### 94.1 构筑范围和审查结论

本轮将 BUILD-040 原计划中的“收藏、页码笔记最小闭环”从 UI 入口补齐为服务端用户级能力，范围限定为：

- `resource_favorites` 和 `resource_notes` SQLite 表，按 `user_uid + resource_id` 隔离，笔记再按页码隔离；
- `GET /api/student/resources/{resource_id}/annotations` 读取当前用户收藏和笔记；
- `PUT /api/student/resources/{resource_id}/favorite` 收藏/取消收藏；
- `PUT/DELETE /api/student/resources/{resource_id}/notes/{page_number}` 保存/删除页码笔记；
- 所有写请求沿用统一的角色、课程、资源发布状态、CSRF、幂等和审计边界；笔记使用 `base_version` 和删除墓碑防止旧标签页复写；
- React 阅读器增加收藏图标、当前页笔记编辑/保存/删除、冲突和失败状态；预览模式只提供交互演示，不声称服务端持久化。

本轮代码审查结论：本地隔离实现已覆盖 `RESOURCE-007` 和 `RESOURCE-008` 的服务端语义；真实 Moodle 资源文件、正式权限、真实角色和人工验收仍是开放门禁。不能因为本地 API 和预览 UI 通过而关闭 BUILD-000、BUILD-040 或最终发布。

### 94.2 T0-T6 测试方案、命令和通过条件

| 层级 | 固定命令/检查 | 通过条件 | 本轮结果 |
|---|---|---|---|
| T0 变更审查 | 审查 Store、Adapter routes、client DTO、Reader UI、manifest/OpenAPI、证据和敏感值扫描 | 只改资源标注边界；无密钥/真实用户数据；正式门禁不升级 | `PASS` |
| T1 语法和配置 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check` | 三项退出码均为 0 | `PASS` |
| T2 Store/API/契约 | `python3 -m unittest -q scripts.test_course_store`；`PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_resource_progress_api.py`；`PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_resource_annotations_api.py`；`python3 scripts/test_api_contract.py` | Store 8/8；进度和标注 API 输出固定成功标记；契约 `routes=77`；覆盖用户隔离、幂等、版本冲突、删除墓碑、角色和真实模式 CSRF | `PASS` |
| T3 前端构筑 | `cd frontend && npm run lint`；`npm run typecheck`；`npm run test:all -- --run`；`npm run build` | lint/typecheck 退出码 0；Vitest 31/31；生产构建 1694 modules | `PASS` |
| T4 浏览器和可访问性 | `npm run test:e2e:mock -- --workers=1`；`npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1` | Mock 20/20；a11y 3/3；axe 4/4；smoke 2/2；移动端无水平溢出；控件有可访问名称 | `OBSERVED_PASS` |
| T5 外部和人工 | 20 个 manifest PDF、Moodle 三角色、正式 API/OpenAPI、正式 HTTPS、人工键盘/屏幕阅读器和真实资料打开 | 必须提供真实环境命令、退出码、角色引用和人工记录；当前资料不足 | `BLOCKED_INPUT` |
| T6 构筑后复审 | 交叉检查 `run_id`、证据、API 契约、资源归属、审计、版本冲突、删除恢复、当前 gate 和回退边界 | 本地证据完整且外部门禁仍原样保留；真实门禁完成后才能正式 PASS | `REVIEW_REQUIRED` |

### 94.3 逐项验收条件

- 未登录或非学生不能读取或写入个人收藏和页码笔记；教师请求返回受控 `403`；未知/未发布资源返回受控 `404`。
- 收藏重复写入返回稳定结果，不新增重复关系；取消收藏后刷新状态为 false。
- 笔记文本不能为空且不超过 2000 字；页码必须落在资源有效范围；笔记不能跨用户读取。
- 同一页旧 `base_version` 保存或删除必须返回 `409 resource_note_conflict`，不能覆盖新内容；删除后保留版本墓碑，旧客户端不能以旧版本恢复覆盖。
- 真实模式写请求必须同时通过集中式 `X-Moodle-Sesskey` 检查和 `Idempotency-Key` 检查；成功收藏、保存和删除均写入脱敏审计记录。
- 前端保存失败、冲突和离线状态必须可见；预览模式不写入服务端，不能把演示状态标为真实保存。
- `openapi.test.json` 和 `api-test-manifest.yaml` 只代表 `local-isolated-adapter`，不能当作正式 Moodle 外部契约。

### 94.4 权威运行和证据

```text
run_id: resource-annotations-revalidation-20260726-05
Store: 8/8
resource progress API: RESOURCE_PROGRESS_API_OK
resource annotations API: RESOURCE_ANNOTATIONS_API_OK
API contract: API_CONTRACT_OK routes=77
frontend: lint PASS; typecheck PASS; Vitest 31/31; build 1694 modules
browser: Mock 20/20; a11y 3/3; axe 4/4; smoke 2/2
hardening/container contract: PASS; 4/4
T5: BLOCKED_INPUT, 20 course PDFs and formal role/material evidence absent
T6: REVIEW_REQUIRED
current gate: BUILD-000 BLOCKED_INPUT
final release: blocked
```

证据见 `acceptance/frontend/BUILD-040/resource-annotations-revalidation-20260726-05.txt`。本轮新增代码、测试、契约和证据后，下一次改动必须从 T0 重新审查；若课程资料或正式角色输入恢复，必须从受影响最早步骤重新执行 T1-T6，不能只补跑浏览器测试。

### 94.5 本轮审查发现和后续边界

`BUILD040-ANNOTATIONS-001` 关闭：本地收藏和页码笔记闭环已实现并有隔离证据。`BUILD-040` 仍保持 `IMPLEMENTED_PENDING_GATE`，原因是 manifest PDF、真实 Moodle pluginfile 权限、真实学生进度/标注回写和正式人工验收未提供。考试能力单独按 BUILD-050 批次审查，不因资源标注结果自动视为通过。

## 95. 2026-07-26 BUILD-050 独立考试与服务端倒计时构筑后审查

### 95.1 构筑范围和边界

本轮修正前一轮审查指出的功能缺口：考试不再复用作业模型，新增独立的考试生命周期和答题状态：

- `exams` 保存题目集合、开放时间、结束时间、考试时长、允许次数和发布状态；
- `exam_attempts` 在服务端记录真实开始时间和固定 `deadline_at`，刷新页面不会重新计时；
- `exam_drafts` 独立保存考试答案并提供 `base_version` 乐观并发保护；
- `exam_submissions` 独立保存提交、服务端提交时间、客观题分数和主观题待复核标记；
- 教师 API 支持创建和发布考试，学生 API 支持列表、详情、开始、草稿和提交；
- React 前端新增考试中心和限时答题页，倒计时只负责显示，截止拒绝、尝试次数、提交时间和分数全部由 Adapter 决定。

第一版不实现摄像头监控或不合规防作弊，仅实现计划要求的服务端时间窗、自动保存、提交幂等和结果显示。真实 Moodle 成绩回写、主观题教师复核和正式人工验收仍未关闭。

### 95.2 T0-T6 测试方案、命令和通过条件

| 层级 | 固定命令/检查 | 通过条件 | 本轮结果 |
|---|---|---|---|
| T0 变更审查 | 审查考试 Store、routes、DTO、页面、OpenAPI、证据和敏感值 | 考试与作业数据边界独立；服务器时间为唯一裁决；无秘密值 | `PASS` |
| T1 语法和配置 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check` | 三项退出码均为 0 | `PASS` |
| T2 Store/API/契约 | `python3 -m unittest -q scripts.test_course_store`；`PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_exam_api.py`；`python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py` | Store 9/9；考试夹具 `EXAM_API_OK`；OpenAPI 为本地隔离契约；API route set 和必需考试路径一致 | `PASS` |
| T3 前端构筑 | `cd frontend && npm run lint`；`npm run typecheck`；`npm run test:all -- --run`；`npm run build` | lint/typecheck 退出码 0；Vitest 33/33；生产构建 1694 modules | `PASS` |
| T4 浏览器和可访问性 | `npm run test:e2e:mock -- --workers=1`；`npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1` | Mock 20/20；a11y 3/3；axe 4/4；smoke 2/2；新增导航不破坏移动端布局和既有角色流程 | `OBSERVED_PASS` |
| T5 外部和人工 | 真实 Moodle 考试、三角色、正式时间环境、成绩桥接、课程 PDF、HTTPS 和辅助技术 | 必须有真实账号引用、退出码、提交/回写结果和人工记录；当前输入不足 | `BLOCKED_INPUT` |
| T6 构筑后复审 | 核对 run_id、证据、服务端时间裁决、草稿版本、提交幂等、成绩范围、当前 gate 和回退边界 | 本地证据完整但外部门禁不变；正式环境完成后才可 PASS | `REVIEW_REQUIRED` |

### 95.3 逐项验收条件

- 未发布、未开放、已结束考试分别返回受控状态；学生不能读取教师考试配置或答案字段。
- 开始考试只在服务端开放窗口内成功；重复相同幂等键返回同一尝试和同一 `deadline_at`。
- `deadline_at = min(started_at + duration_seconds, close_at)`，刷新详情只能读取已存在尝试，不能延长时间。
- 截止前草稿保存成功，旧 `base_version` 返回 `409 exam_draft_conflict`，不能覆盖新标签页答案。
- 截止后草稿和提交均由服务端拒绝；客户端倒计时归零不能伪造成功提交。
- 同一尝试重复提交不产生第二个 submission ID；新幂等键返回稳定冲突。
- 客观题分数由服务端依据题目答案计算；主观题只产生 `needs_review`，不能伪造教师最终复核。
- 页面显示倒计时、自动保存状态、冲突、截止和提交结果；预览模式明确不写入课程平台。
- `openapi.test.json` 和 `api-test-manifest.yaml` 只作为 `local-isolated-adapter` 证据，不能替代正式 Moodle 外部契约。

### 95.4 权威运行和证据

```text
run_id: exam-revalidation-20260726-06
Store: 9/9
exam API: EXAM_API_OK
API contract: API_CONTRACT_OK routes=90
local OpenAPI export: 89 paths
frontend: lint PASS; typecheck PASS; Vitest 33/33; build 1694 modules
browser: Mock 20/20; a11y 3/3; axe 4/4; smoke 2/2
T5: BLOCKED_INPUT, real Moodle exam/roles/grade bridge/PDF/manual evidence absent
T6: REVIEW_REQUIRED
current gate: BUILD-000 BLOCKED_INPUT
final release: blocked
```

证据见 `acceptance/frontend/BUILD-050/exam-revalidation-20260726-06.txt`。本轮生成 OpenAPI 和验证账本必须串行执行；若课程资料、正式考试接口或 Moodle 角色恢复，必须从受影响最早步骤重跑 T1-T6，不能只依赖当前本地倒计时截图。

### 95.5 本轮审查结论

`BUILD050-EXAM-001` 关闭：独立考试模型、服务端时间窗、草稿版本、提交幂等、客观题计分和前端倒计时已完成本地隔离验收。`BUILD-050` 继续保持 `IMPLEMENTED_PENDING_GATE`，开放阻断包括真实 Moodle 三角色、正式成绩回写、主观题复核、正式 API/OpenAPI、课程 PDF、HTTPS、辅助技术和人工验收。

## 96. 2026-07-26 BUILD-050 终审和计划一致性复核

### 96.1 复核范围

本次终审覆盖 BUILD-050 独立考试实现、T0-T6 测试方案、最终串行命令、考试证据、`PROJECT_PROGRESS.yaml`、`PROJECT_STATUS.md`、OpenAPI 生成结果和证据路径。复核重点是确认：计划中的测试方案能被实际执行；证据中的结果与命令一致；本地观察性通过不会升级正式外部门禁；scope 路径、finding ID、test run ID 和 known blocker ID 没有重复。

### 96.2 最终串行结果

| 层级 | 实际结果 | 审查判定 |
|---|---|---|
| T0 范围和敏感信息 | 考试与作业模型分离；服务器时间裁决；证据未写入密钥、Cookie、Authorization 或真实学生数据 | `PASS` |
| T1 语法和差异 | Python compile、Shell syntax、`git diff --check` 全部退出码 0 | `PASS` |
| T2 Store/API/契约 | Store 9/9；`EXAM_API_OK`；OpenAPI 89 paths；API 90 routes | `PASS` |
| T3 前端工程 | lint、typecheck、Vitest 33/33、生产构建 1694 modules | `PASS` |
| T4 浏览器和可访问性 | Mock 20/20；a11y 3/3；axe 4/4；smoke 2/2；硬化和容器静态契约 4/4 | `OBSERVED_PASS` |
| T5 外部和人工 | 课程 PDF、真实 Moodle 考试、三角色、成绩回写、主观题复核、正式 HTTPS 和辅助技术证据缺失 | `BLOCKED_INPUT` |
| T6 复审和归档 | 本地证据、运行号、当前 gate 和回退边界一致；正式发布条件仍未满足 | `REVIEW_REQUIRED` |

### 96.3 账本一致性结果

最终串行复核命令及通过条件如下：

```text
python3 scripts/refresh_progress_snapshot.py -> PROGRESS_SNAPSHOT_REFRESHED tracked_modified=24 untracked=32 total=56
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract -> 19/19 PASS
python3 scripts/validate_project_progress.py -> PROJECT_PROGRESS_VALIDATION_OK metadata=11 blockers=21 evidence_refs=120 redaction_scan=PASS
```

路径和标识唯一性审查通过：`plan_review.scope` 无重复路径，findings、test_runs 和 known_blockers 无重复 ID；`exam-revalidation-20260726-06` 是 BUILD-050 当前权威批次。课程数据完整验收仍在 `chapter-1-1.1-.pdf` 缺失处以退出码 2 fail-fast，没有生成占位 PDF，也没有修改 manifest、hash 或 page_count。

### 96.4 终审结论和后续触发条件

`BUILD050-PLAN-AUDIT-001` 关闭：BUILD-050 的测试方案已经写入计划并经过一次实际构筑后的 T0-T6 终审，命令、阈值、证据、状态边界和重测规则可复现。该结论只关闭计划质量审查，不关闭 BUILD-050 的正式功能门禁或最终发布。

在真实课程资料或正式 Moodle 输入恢复后，必须从受影响的最早层级重跑 T1-T6：先验证课程资料、正式考试 API/OpenAPI 和三角色权限，再验证开放/截止、刷新恢复、草稿冲突、重复提交、成绩回写和主观题教师复核，最后完成正式 HTTPS、辅助技术和人工验收。当前 `BUILD-000 = BLOCKED_INPUT`、`BUILD-050 = IMPLEMENTED_PENDING_GATE`、最终发布 `blocked` 均保持不变。

## 97. 2026-07-26 外部门禁日常复核

### 97.1 复核范围

本轮只读复核课程资料输入、提交材料、Docker 可用性和测试密钥文件边界。复核不会读取密钥值、不会生成课程占位 PDF、不会修改 manifest/hash/page_count，也不会把无关下载目录压缩包误判为课程课件。

### 97.2 结果和验收判定

| 检查项 | 实际结果 | 判定 |
|---|---|---|
| `/home/registrar/下载` 课程输入 | 未发现与 manifest 匹配的 PDF 或课程课件包 | `BLOCKED_INPUT` |
| `python3 scripts/verify_course_data.py course-data/normalized` | `COURSE_DATA_BLOCKED_INPUT`，退出码 2，首个缺失 `chapter-1-1.1-.pdf` | `BLOCKED_INPUT` |
| `bash scripts/check_submission_materials.sh` | 缺少 Demo URL、真实视频和真实人工验收汇总 3 项，退出码 1 | `BLOCKED_INPUT` |
| Docker | client `29.3.0` 可见；访问 `/var/run/docker.sock` 被拒绝，server 不可用 | `BLOCKED_DEPENDENCY` |
| `.env.test.local` | 权限 `600`，Git ignored；没有读取或记录值 | `PASS` |

### 97.3 复核结论

证据见 `acceptance/frontend/BUILD-000/daily-gate-revalidation-20260726-07.txt`。本轮确认课程输入和正式提交材料状态未恢复，Docker 阻断由“镜像拉取超时”更新为当前可观测的 Docker socket 权限阻断；这不改变课程前置门禁的等级。`BUILD-000` 继续为 `BLOCKED_INPUT`，`BUILD-050` 继续为 `IMPLEMENTED_PENDING_GATE`，最终发布继续 `blocked`。外部输入恢复后必须从受影响的最早层级重跑 T1-T6。

## 98. 2026-07-26 BUILD-050 考试浏览器闭环复测

### 98.1 变更和审查范围

本轮补齐了计划中“考试页面应完成真实交互闭环”的本地证据。新增 Mock Playwright 场景覆盖：考试中心列表、进入考试、服务端开始尝试、题目作答、自动保存、服务端返回固定截止时间、提交和成绩显示。测试通过路由夹具验证 HTTP 合约，不把夹具数据当作正式 Moodle 数据。

### 98.2 构筑后测试与验收结果

| 层级 | 命令/条件 | 本轮结果 |
|---|---|---|
| T0 | 检查考试 UI、客户端 DTO、Mock 路由和敏感值边界 | `PASS` |
| T1 | lint、typecheck、Vitest、生产构建 | `PASS`；Vitest `33/33`；构建 `1694 modules` |
| T2 | list/detail/start/draft/submit 请求和服务端成绩响应 | `PASS` |
| T3 | `npm run test:e2e:mock -- --workers=1 --grep "timed exam"` | `OBSERVED_PASS`；`1/1` |
| T4 | `npm run test:e2e:mock -- --workers=1` | `OBSERVED_PASS`；`21/21` |
| T5 | 真实 Moodle 考试、正式时间环境、成绩回写、主观题复核和人工验收 | `BLOCKED_INPUT` |
| T6 | 运行号、证据路径、当前 gate 和正式边界复核 | `REVIEW_REQUIRED` |

### 98.3 验收条件

- 考试列表中的“进入考试”按钮必须进入对应考试详情，不能把标题文本误当作操作控件。
- 选择答案后，前端必须通过考试草稿接口发送答案并显示“答案已保存”；不能只更新浏览器内存。
- 提交前必须先完成待保存草稿，提交接口必须携带当前答案；成功后页面显示服务端返回的成绩和提交状态。
- 浏览器倒计时仍只负责显示，截止、尝试次数、保存版本和成绩以服务端响应为准。
- 该 Mock 场景只证明本地前端和 Adapter 合约连接，不替代真实 Moodle 时间边界、成绩桥接、主观题复核或人工验收。

### 98.4 复测结论

`BUILD050-EXAM-UI-001` 关闭：考试浏览器闭环已从仅有预览/API 证据补齐为 `1/1` 定向流程和 `21/21` 完整 Mock 回归。`BUILD-050` 仍为 `IMPLEMENTED_PENDING_GATE`，因为真实 Moodle、正式课程资料、正式 API/OpenAPI、成绩回写、主观题复核、HTTPS 和人工验收仍未完成。证据见 `acceptance/frontend/BUILD-050/exam-ui-revalidation-20260726-08.txt`。

## 99. 2026-07-26 测试方案增补与计划二次审查

### 99.1 审查范围和结论边界

本轮只审查测试计划、当前实现边界、测试命令可执行性、账本唯一性和证据归档规则，不实现新的前端页面或 API，不切换生产路由，也不读取或记录任何测试密钥。第 27 节仍是所有构筑的总协议；本节把当前发现的下一项功能缺口写成可直接执行的构筑前置方案。

审查确认当前后端已有 `POST /api/teacher/exams` 和 `POST /api/teacher/exams/{exam_id}/publish`，但尚未形成教师端完整闭环：没有教师考试列表 `GET /api/teacher/exams`，前端没有 `TeacherExam` DTO、教师考试 API 客户端、`/teacher/exams` 页面或教师工作台入口。因此，已有学生考试浏览器通过不能被解释为“教师创建并发布考试已完成”。

### 99.2 计划审查发现

| ID | 严重度 | 状态 | 审查结果 |
|---|---|---|---|
| `PLAN-TEST-016` | P1 | `CLOSED` | 第 17 节、第 27 节和第 98 节中的命令已与当前仓库核对；`scripts/test_ui_contract.py`、`scripts/test_api_contract.py`、`scripts/test_frontend_hardening.py` 和 `frontend/package.json` 中的前端脚本均存在。没有发现把不存在命令记为通过的计划错误。 |
| `BUILD050-TEACHER-EXAM-UI-001` | P1 | `OPEN` | 教师考试创建、列表、发布和状态回读尚未有前端闭环；现有后端创建/发布 API 只能作为局部能力，不能关闭教师考试功能门禁。 |
| `PLAN-TEST-017` | P1 | `CLOSED` | 下一次教师考试构筑已补齐 T0-T6 的命令、测试 ID、通过阈值、证据文件、失败重测范围和真实环境阻断边界。 |

### 99.3 下一次教师考试构筑的 T0-T6 测试方案

本方案是下一次实现教师考试管理页面和列表 API 时的强制门禁。当前尚未实现的测试必须记录为 `NOT_IMPLEMENTED`，不能以学生考试 Mock 流程、静态页面或已存在的 POST API 替代。

| 层级 | 测试命令/检查 | 必须满足的验收条件 | 当前状态 |
|---|---|---|---|
| T0 范围、权限和数据审查 | 审查 `scope.md`、权限矩阵、状态迁移表、API diff、迁移和 `rollback.md` | teacher/admin 可管理本课程考试；student/未登录返回受控 `403/401`；考试只能引用已发布题目；学生响应不含答案、评分标准或教师配置；草稿、发布、撤回、归档迁移明确 | `NOT_IMPLEMENTED` |
| T1 静态和构建 | `git diff --check`；`bash -n scripts/*.sh`；`python3 -m compileall -q agent-adapter scripts`；`cd frontend && npm run lint`；`cd frontend && npm run typecheck`；`cd frontend && npm run build` | 所有适用命令退出码为 0；TypeScript DTO、路由和响应字段无未使用或隐式 any；构建产物可重复生成 | `NOT_RUN` |
| T2 单元、Store 和客户端 | `python3 -m unittest -q scripts.test_course_store`；新增 `scripts/test_teacher_exam_api.py` 的 Store/DTO/权限定向用例；`cd frontend && npm run test:all -- --run` | 覆盖列表过滤、创建、发布、重复发布、非法题目、时间窗、尝试次数、幂等重放和错误包络；新增测试与全量 Vitest 均通过 | `NOT_IMPLEMENTED` |
| T3 API、契约和持久化 | `python3 scripts/test_api_contract.py`；串行生成本地 OpenAPI 后再运行契约校验；新增 `scripts/test_teacher_exam_api.py` | `GET /api/teacher/exams`、`POST /api/teacher/exams`、`POST /api/teacher/exams/{exam_id}/publish` 的状态码、分页、角色隔离、幂等、状态回读和审计副作用正确；OpenAPI 和 manifest 与实际路由一致 | `NOT_IMPLEMENTED` |
| T4 浏览器流程 | `cd frontend && npm run test:e2e:mock -- --workers=1 --grep "teacher.*exam"`；随后运行完整 `npm run test:e2e:mock -- --workers=1` | 教师选择已发布题目、填写标题/开放时间/结束时间/时长/次数、保存草稿、发布并刷新后显示已发布；学生只能看到已发布考试；错误、空数据、无权限和重复点击均有明确状态 | `NOT_IMPLEMENTED` |
| T5 质量、可访问性和真实环境 | `cd frontend && npm run test:a11y -- --workers=1`；`cd frontend && npm run test:axe -- --workers=1`；六视口人工截图；真实 Moodle 三角色考试流程 | 表单控件可命名、键盘可操作、无明显重叠/截断；真实 Moodle 的教师发布、学生可见性、时间边界、成绩回写和主观题复核均有证据；本地 Mock 只能记 `OBSERVED_PASS` | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 更新 `metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`api-contract.json`、`manual-acceptance.md`、`rollback.md`，再运行账本校验 | 每层都有状态和退出码；所有文件共享唯一 `run_id`；代码、数据库迁移、路由和 API 均有回退点；无 P0/P1 未关闭问题；正式输入未齐时批次只能保持 `IMPLEMENTED_PENDING_GATE` | `REVIEW_REQUIRED` |

### 99.4 逐项验收条件和失败重测

- 创建考试必须拒绝空标题、空题目、未发布题目、非法时间窗、超出时长范围和非法尝试次数，并且拒绝时不产生考试记录。
- 同一 `Idempotency-Key` 重放创建或发布请求只能返回同一个考试结果；同一幂等键改写 payload 必须返回稳定冲突，不能重复写入或改变状态。
- 教师列表只能显示当前课程且有权限的考试；学生列表只能显示已发布考试，不能通过详情接口读取草稿状态、答案、rubric 或教师审计字段。
- 发布前后刷新页面必须从服务端重新读取状态；前端按钮禁用只能改善交互，不能承担权限、状态迁移或幂等裁决。
- 测试、API、权限、路由、迁移、Mock 夹具或构建配置任一发生变化，都必须从受影响的最早层级重新执行并补跑 T1-T6；只重跑一个绿色浏览器用例不能关闭批次。
- 真实课程资料、正式 Moodle API/OpenAPI、三角色账号、正式考试时间环境、成绩回写、主观题复核、HTTPS、人工辅助技术和恢复证据恢复后，必须从 T0 重新执行 BUILD-000 及受影响的后续批次。

### 99.5 本轮计划审查的机器验收

本轮计划审查必须串行执行以下命令；前端完整回归沿用第 98 节的权威结果，因为本轮没有修改前端代码：

```text
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract
python3 scripts/test_api_contract.py
python3 scripts/test_ui_contract.py
python3 scripts/test_frontend_hardening.py
python3 -m compileall -q agent-adapter scripts
bash -n scripts/*.sh
git diff --check
python3 scripts/validate_project_progress.py
```

通过条件是：计划和 YAML 可解析；scope、finding、test run、known blocker 标识无重复；所有证据路径存在；脱敏扫描通过；API/UI/硬化命令退出码为 0；课程资料校验若仍缺文件，必须保留 `COURSE_DATA_BLOCKED_INPUT` 和退出码 2。计划审查绿色只证明规则可执行，不关闭 `BUILD-000`、`BUILD-050` 或最终发布门禁。

### 99.6 计划二次审查结论

`PLAN-TEST-016` 和 `PLAN-TEST-017` 关闭，`BUILD050-TEACHER-EXAM-UI-001` 保持开放。测试方案状态为 `DOCUMENTED_AND_REVIEWED_WITH_OPEN_FINDINGS`；第 27 节的 T0-T6 顺序、状态边界、证据要求和重测规则继续有效，教师考试构筑在实现前不得报告为通过。

本轮不改变现有状态：`BUILD-000 = BLOCKED_INPUT`、`BUILD-050 = IMPLEMENTED_PENDING_GATE`、最终发布 `blocked`。当前前端考试闭环的最新本地证据仍是 `exam-ui-revalidation-20260726-08`；正式 Moodle 角色、课程 PDF、正式 API/OpenAPI、成绩回写、主观题复核、Docker/HTTPS、恢复、六视口和人工验收仍未完成。机器审查证据见 `acceptance/frontend/BUILD-000/plan-test-revalidation-20260726-09.txt`。

## 100. 2026-07-26 BUILD-050 教师考试管理构筑后审查

### 100.1 构筑范围和实现结果

本批次按第 99 节方案补齐教师考试管理闭环，变更范围为：

- Adapter 新增 `GET /api/teacher/exams` 分页列表，以及考试撤回和归档接口；接口只允许 teacher/admin，学生和默认未登录 Mock 身份不能访问教师管理数据。
- 前端新增 `TeacherExam` 类型、列表/创建/发布/撤回/归档客户端方法和写操作的 `X-Moodle-Sesskey`、`Idempotency-Key`、`X-Request-ID` header。
- 新增 `/teacher/exams` 页面，并从教师工作台提供“管理考试”入口；页面使用已发布题目组卷，服务端回读考试状态，支持草稿、发布、撤回、归档和刷新恢复。
- 新增 `scripts/test_teacher_exam_api.py`、客户端 DTO/header 测试和 Mock Playwright 教师流程；本地 OpenAPI 已在路由变更后串行重新生成。

本批次没有实现摄像头监控、非合规防作弊、真实 Moodle 成绩回写或主观题自动定分；这些边界仍按第 95、96 节保留。

### 100.2 构筑后 T0-T6 测试结果

| 层级 | 命令/检查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查后端路由、Store 状态迁移、DTO、页面权限、敏感信息和回退边界 | 教师管理只读/写入边界明确；学生响应不返回答案或 rubric；本地 Mock 语义与正式 401/角色门禁分开记录 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；前端 lint/typecheck/build | 全部退出码 0；生产构建 `1694 modules` | `PASS` |
| T2 Store/API/客户端 | `python3 scripts/test_course_store.py`；`scripts/test_exam_api.py`；`scripts/test_teacher_exam_api.py`；`scripts/test_teacher_workbench_api.py`；Vitest | Store `9/9`；独立考试 API、教师考试 API、教师工作台 API 通过；Vitest `35/35` | `PASS` |
| T3 契约和持久化 | `python3 scripts/generate_local_openapi.py` 后串行执行 `python3 scripts/test_api_contract.py` | OpenAPI `91 paths`；静态 API 契约 `92 routes`；创建幂等、非法未发布题目、分页、角色隔离、状态迁移和审计均通过 | `PASS` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1 --grep "teacher can create, publish, withdraw and archive a timed exam"`；完整 Mock 回归 | 定向 `1/1`；完整 `22/22`；覆盖创建草稿、发布、刷新、撤回和归档 | `OBSERVED_PASS` |
| T5 质量和辅助技术 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1` | a11y `3/3`、axe `4/4`、标准 smoke `2/2`；预览模式的 Adapter `8081 ECONNREFUSED` 是预期边界 | `OBSERVED_PASS` |
| T6 证据和发布门禁 | 交叉核对本节、运行号、证据、账本、状态和外部阻断 | 本地证据可追溯；正式 Moodle、课程资料、人工和部署门禁未完成 | `REVIEW_REQUIRED` |

### 100.3 逐项验收条件

- 教师考试列表包含草稿、已发布、已撤回和已归档状态；分页参数越界返回受控 `422`，学生访问返回 `403`。
- 创建考试只能引用已发布题目；空标题、非法时间窗、非法时长、非法尝试次数和未发布题目均被拒绝且不产生有效考试记录。
- 相同幂等键重复创建或发布不会产生第二条记录；相同幂等键改写 payload 返回稳定冲突。
- 前端创建成功后清空表单并从服务端刷新列表；发布、撤回和归档后页面显示服务端状态，刷新不会恢复旧状态。
- 学生考试列表只显示已发布考试；教师列表字段不包含题目答案或评分标准。
- 表单控件有可访问名称，移动布局没有新增明显重叠或不可操作溢出；本地 axe 结果不等于正式三角色辅助技术验收。

### 100.4 代码审查发现和重测规则

本轮第一次 API 夹具尝试把 Mock 模式下无 header 的默认学生身份断言为 `401`，复审后修正为本地 `403`，并在测试中注明正式 Moodle 未登录 `401` 由外部门禁验证。第二次教师考试定向和完整浏览器回归均通过。该修正不放宽生产鉴权，也不改变真实环境验收要求。

本批次以后若修改考试路由、Store、前端页面、客户端 header、测试夹具或 OpenAPI，必须从受影响最早的 T1 层重新执行并补跑 T1-T6；若正式课程资料、Moodle 账号、API 契约或成绩桥接恢复，必须从 BUILD-000 的 T0 重新执行受影响后续批次。

### 100.5 本轮审查结论

`BUILD050-TEACHER-EXAM-UI-001` 已关闭：教师创建、列表、发布、刷新回读、撤回和归档的本地隔离闭环已实现，并有 API、客户端、组件、Mock 浏览器和质量测试证据。`BUILD-050` 仍为 `IMPLEMENTED_PENDING_GATE`，本轮 T4/T5 只能记 `OBSERVED_PASS`，因为真实 Moodle 三角色、正式考试时间、成绩回写、主观题复核、课程 PDF、正式 HTTPS、正式辅助技术和人工验收仍缺失。

本轮权威证据为 `teacher-exam-ui-revalidation-20260726-10`，见 `acceptance/frontend/BUILD-050/teacher-exam-ui-revalidation-20260726-10.txt`。当前 `BUILD-000 = BLOCKED_INPUT`，最终发布继续 `blocked`。

## 101. 2026-07-26 测试方案写入后的进一步审查

### 101.1 审查目标和边界

本轮将第 27 节的通用 T0-T6 协议和第 100 节的教师考试构筑结果作为当前执行基线，检查测试方案是否能直接执行、命令是否存在、状态是否被正确解释、最新运行号是否可追溯，以及证据文件是否足以支撑 BUILD 门禁。本轮只修改计划和审查记录，不实现功能、不切换生产路由、不读取或记录任何 API Key、API Secret、Cookie、Authorization 或真实学生数据。

### 101.2 当前构筑必须执行的测试方案

每次构筑完成后必须按 T0 到 T6 顺序执行；同一层失败或输入变化时，必须从最早受影响层重新执行并补跑后续层。下表是当前批次的最小可执行门禁，不能用单个绿色浏览器用例替代完整批次。

| 层级 | 必须执行 | 通过/阻断条件 | 证据要求 |
|---|---|---|---|
| T0 范围与代码审查 | scope、权限矩阵、API diff、状态迁移、敏感值和 rollback 审查 | 没有未处理 P0/P1；Mock、正式环境和未实现范围明确分开 | `scope.md`、`review.md` |
| T1 静态与构建 | `git diff --check`、`bash -n scripts/*.sh`、`python3 -m compileall -q agent-adapter scripts`、lint、typecheck、生产构建 | 适用命令全部退出码为 0；命令不存在记为 `NOT_IMPLEMENTED` | 命令、退出码、构建摘要 |
| T2 单元与业务规则 | 变更 Store/API/客户端定向测试，再执行前端 `npm run test:all -- --run` | 状态迁移、权限、错误包络、幂等和版本冲突均有断言 | 测试 ID、通过数量、失败摘要 |
| T3 API 与契约 | 先串行生成本地 OpenAPI，再运行 API manifest/契约测试和持久化审查 | 正向、负向、越权、分页、幂等、状态回读和审计全部适用通过；缺正式输入则 `BLOCKED_INPUT` | `api-contract.json`、脱敏请求/响应摘要 |
| T4 浏览器流程 | 定向 Mock Playwright、完整 Mock 回归，再执行适用真实三角色流程 | Mock 结果最多 `OBSERVED_PASS`；刷新、重复点击、失败恢复和移动视口均覆盖 | `test-output.txt`、截图/视频、角色和视口 |
| T5 质量与外部验收 | `test:a11y`、`test:axe`、标准 smoke、正式 axe 等价、六视口、性能/恢复和真实环境验收 | 本地自定义质量测试不能替代正式角色、辅助技术、HTTPS、恢复和成绩回写 | `manual-acceptance.md`、质量输出 |
| T6 证据与门禁复审 | 交叉核对唯一 `run_id`、退出码、T0-T6 状态、回退点和开放阻断 | 只有全部适用项为 `PASS` 才能关闭 BUILD；否则保留 `REVIEW_REQUIRED` 或阻断状态 | `metadata.json`、`review.md`、`rollback.md`、账本校验 |

### 101.3 机器审查结果

本轮串行审查使用以下命令集合：

```text
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract
python3 scripts/test_api_contract.py
python3 scripts/test_ui_contract.py
python3 scripts/test_frontend_hardening.py
python3 -m compileall -q agent-adapter scripts
bash -n scripts/*.sh
git diff --check
python3 scripts/validate_project_progress.py
```

结果为：账本回归 `19/19`；API 契约 `92 routes`；UI 契约通过；前端硬化通过；Python 编译、Shell 语法和差异检查通过；进度校验 `metadata=11`、`blockers=21`、`evidence_refs=130`、`redaction_scan=PASS`。计划中的命令均能在当前仓库解析或执行，未发现不存在的命令被记录为成功。

### 101.4 证据身份审查发现

`teacher-exam-ui-revalidation-20260726-10` 已有脱敏的专用结果文件，并与第 100 节、`PROJECT_PROGRESS.yaml` 的本地结果一致。但 `acceptance/frontend/BUILD-050/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md` 仍属于旧的 `BUILD-050-20260725-02` 标准批次；校验器因此正确地把这两类证据分开，没有把专用结果自动升级为新的标准 BUILD 证据。

该问题记为 `PLAN-EVIDENCE-003`（P1，开放）：下一次教师考试标准批次签核前，必须使用唯一新 `run_id` 补齐六类标准文件，令五类证据和 `review.md` 的 T0-T6 状态与 `metadata.json` 完全一致，再重新执行账本校验。当前专用结果可以支撑本地观察性复审，但不能单独关闭 `BUILD-050`。

### 101.5 本轮审查结论和重测触发

测试方案已写入并通过可执行性审查；第 27 节的 T0-T6 顺序、状态边界、证据要求和失败重测规则有效。`PLAN-TEST-018` 关闭，`PLAN-EVIDENCE-003` 保持开放。当前状态不变：`BUILD-000 = BLOCKED_INPUT`、`BUILD-050 = IMPLEMENTED_PENDING_GATE`、最终发布 `blocked`。

以下任一条件发生时，必须从 T0 重新审查并重跑受影响的 T1-T6：教师考试路由、Store、客户端 header、前端表单/状态迁移、API manifest/OpenAPI、测试夹具、标准证据身份或正式 Moodle/课程资料输入发生变化。课程 PDF、真实 Moodle 三角色、正式 API/OpenAPI、成绩回写、主观题复核、HTTPS、正式可访问性、六视口人工证据和恢复证据仍未完成前，不得将任何 `OBSERVED_PASS` 升级为正式 `PASS`。

## 102. 2026-07-26 BUILD-050 完整标准批次复测

### 102.1 复测范围

本批次为关闭 `PLAN-EVIDENCE-003` 而执行的完整 BUILD-050 本地复测，覆盖学生作业/草稿/评分、独立考试服务端裁决、教师考试管理、教师工作台 API、前端全量构建和共享质量门禁。运行号为 `BUILD-050-20260726-03`，attempt `3`，已 supersede `BUILD-050-20260725-02`；运行环境为本地隔离 Adapter、预览浏览器和受控 Mock 数据。

本批次不宣称真实 Moodle 成绩回写、正式考试时间、正式 API/OpenAPI、课程 PDF、真实三角色、正式 HTTPS、正式辅助技术或服务器恢复通过。第一次 Mock 浏览器启动在受限回环环境超时，随后在允许本机回环监听的环境以单 worker 重跑并通过；两次结果均保留在批次审查边界内，受限环境启动超时不计作产品断言失败。

### 102.2 T0-T6 构筑后结果

| 层级 | 命令/检查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 作业、独立考试、教师考试路由/Store/客户端、权限、敏感值和回退审查 | 三类教学流程范围清楚；学生不接收答案/rubric；教师写操作保留 sesskey、幂等和 request ID 边界 | `PASS` |
| T1 静态和构建 | Store/API 脚本、OpenAPI 生成、Python 编译、Shell 语法、lint、typecheck、生产构建 | Store `9/9`；编译/Shell/lint/typecheck 退出码 0；构建 `1694 modules` | `PASS` |
| T2 单元和业务规则 | 草稿、评测、独立考试、教师考试、教师工作台 API；Vitest | 作业/考试/教师 API 均通过；Vitest `35/35` | `PASS` |
| T3 契约和持久化 | 生成 OpenAPI 后串行执行 API 契约；角色、分页、幂等、状态和审计断言 | 本地 OpenAPI `91 paths`、API 契约 `92 routes`；正式 Moodle 契约仍未提供 | `OBSERVED_PASS` |
| T4 浏览器流程 | 定向教师考试流程、完整 Mock Playwright、刷新/状态回读 | 定向教师考试 `1/1`；完整 Mock `22/22`，覆盖作业、考试和教师考试管理 | `OBSERVED_PASS` |
| T5 质量和外部验收 | a11y、axe、smoke、真实角色/成绩回写/正式时间/人工辅助技术 | a11y `3/3`、axe `4/4`、smoke `2/2`；正式外部和人工项缺失 | `BLOCKED_INPUT` |
| T6 标准证据和账本 | 六类标准文件、共享 run_id、退出码摘要、账本/脱敏/唯一性校验 | `BUILD-050-20260726-03` 在标准文件中一致；`metadata=11`、`evidence_refs=133`、redaction PASS | `REVIEW_REQUIRED` |

### 102.3 逐项验收结论

- 作业草稿、版本冲突、截止/尝试边界、重复提交、客观题评分和主观题待教师复核均通过本地 API 断言。
- 独立考试的服务端 deadline、草稿版本、提交幂等、客观题评分和未知/非法状态边界均通过本地 API 断言。
- 教师考试列表、题目发布状态约束、创建/发布幂等、分页/角色隔离、发布/撤回/归档和刷新回读均有 API 或 Mock 浏览器证据。
- 学生列表不能通过本地管理接口读取教师考试字段；正式 Moodle 未登录 `401`、真实角色和正式 API 语义仍需外部验收。
- T3/T4 的本地结果只属于 `OBSERVED_PASS`；T5/T6 的正式环境、人工、部署和恢复条件未满足前，不得关闭 BUILD-050。

### 102.4 证据和计划审查结论

`metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md` 现在共享唯一运行号 `BUILD-050-20260726-03`；`api-contract.json` 同步加入教师考试接口和测试 ID。`python3 scripts/validate_project_progress.py` 重新验证通过，`PLAN-EVIDENCE-003` 关闭。

本次复测只关闭“标准证据身份缺口”，不关闭 BUILD-050 的正式功能门禁。当前状态保持：`BUILD-000 = BLOCKED_INPUT`、`BUILD-050 = IMPLEMENTED_PENDING_GATE`、最终发布 `blocked`。证据见 `acceptance/frontend/BUILD-050/test-output.txt` 和 `acceptance/frontend/BUILD-050/metadata.json`。

## 103. 2026-07-26 BUILD-090 Spark 鉴权负向远端复测

### 103.1 复测范围和安全边界

本轮只复测 Spark Assistant WebSocket 的鉴权负向，不修改生产 Adapter、不把凭据写入代码或证据、不记录签名 URL、Authorization、Cookie、问题正文或回答正文。脚本从权限为 `600` 的本地测试环境读取配置，并仅输出 case 状态和脱敏错误码。

### 103.2 实际结果

执行命令：

```text
python3 scripts/test_spark_assistant_auth_negative.py --timeout 15
```

| Case | 预期 | 实际 | 判定 |
|---|---|---|---|
| `wrong-app-id` | 非零鉴权错误且不进入正常回答 | handshake `101`，错误码 `11200`，无最终业务帧 | `PASS` |
| `wrong-api-key` | 非零鉴权错误且不进入正常回答 | handshake `101`，最终 `header.code=0`，正常完成 | `FAIL` |
| `wrong-secret` | 非零鉴权错误且不进入正常回答 | handshake `101`，最终 `header.code=0`，正常完成 | `FAIL` |
| `tampered-date` | 非零鉴权错误且不进入正常回答 | handshake `101`，最终 `header.code=0`，正常完成 | `FAIL` |

进程退出码为 `6`。离线签名构造测试已经证明错误 key/secret/date 会改变对应签名材料；无权限 APPID 能得到 `11200`，因此当前问题不是本地测试变异没有生效，而是远端 endpoint、Assistant 绑定、签名版本或供应方错误语义仍未解释。

### 103.3 门禁结论

`SPARK-AUTH-FAIL-001` 继续保持 P0 `FAIL`，`BUILD-090` 继续 `IMPLEMENTED_PENDING_GATE`，最终发布继续 `blocked`。在供应方确认 endpoint、Assistant、签名版本、凭据绑定和错误拒绝语义前，不再把错误 Key/Secret/date 负向标记为 `PASS`，也不增加真实内容、并发或性能发布结论。后续只有在外部协议输入恢复后，才按第 27 节从 T0 重新执行鉴权、异常恢复、限流、并发、内容审核和真实 Workflow 验收。

脱敏证据：`acceptance/frontend/BUILD-090/spark-auth-negative-revalidation-20260726-13.txt`。

## 104. 2026-07-26 BUILD-080 管理员工作台完整本地复测

### 104.1 复测范围

本批次按 BUILD-080 的 ADMIN-001～007 范围复测管理员服务状态、知识库版本生命周期、文件安全、黄金问题、发布状态、审计分页、备份状态和浏览器恢复边界；同时复核当前共享 API/前端质量门禁。运行号为 `BUILD-080-20260726-02`，attempt `2`，已 supersede `BUILD-080-20260725-01`。

真实管理员 Moodle 账号、正式知识库 Workflow、服务器备份归档、数据库/文件恢复、正式 API 契约、正式 axe 等价审查和六视口人工证据仍不在本地输入范围内；本批次不把隔离 Mock 结果升级为正式通过。

### 104.2 T0-T6 构筑后结果

| 层级 | 命令/检查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围与权限审查 | 管理员路由、学生越权、状态脱敏、文件路径、备份命令边界和回退审查 | ADMIN-001～007 范围明确；浏览器只读托管备份状态，不执行宿主机命令 | `PASS` |
| T1 静态与构建 | 管理员 API、备份脚本语法、OpenAPI、API 契约、lint、typecheck、Vitest、build | 管理员 API通过；备份安全脚本 `3/3`；OpenAPI `91 paths`、API `92 routes`、Vitest `35/35`、构建 `1694 modules` | `PASS` |
| T2 业务规则 | `test_admin_workbench_api.py` 和前端管理员组件/全量测试 | 权限、manifest hash、路径穿越、重复上传、黄金问题、发布门槛、审计和敏感字段断言通过 | `PASS` |
| T3 API 与持久化 | 隔离 ASGI API、OpenAPI/manifest、本地审计和备份安全夹具 | 本地契约和副作用通过；正式 Moodle API/知识库契约未提供 | `OBSERVED_PASS` |
| T4 浏览器流程 | 管理员定向 Mock、完整 Mock、刷新/空态/错误态 | 管理员定向 `1/1`；完整 Mock `22/22` | `OBSERVED_PASS` |
| T5 质量与真实验收 | a11y、axe、smoke、正式管理员、服务器恢复和六视口 | a11y `3/3`、axe `4/4`、smoke `2/2`；真实管理员、恢复和人工证据缺失 | `BLOCKED_INPUT` |
| T6 标准证据与账本 | BUILD-080 六类文件、唯一 run_id、退出码、回退和账本校验 | `BUILD-080-20260726-02` 共享身份一致；账本 `metadata=11`、`evidence_refs=138`、redaction PASS | `REVIEW_REQUIRED` |

### 104.3 验收结论

- `ADMIN-001`～`ADMIN-007` 的本地隔离 API 已通过：管理员权限、状态脱敏、manifest hash、文件路径和重复幂等、三条黄金问题、发布门槛、审计 request ID、备份 Secret 排除均有断言。
- 本地备份安全脚本通过合法校验和、目录 `.env` 拒绝和 tar 内部 `*.secret` 拒绝三类夹具；这不等于服务器备份和恢复成功。
- 管理员浏览器页面在 Mock API 中完成创建、上传、黄金测试和发布；完整共享 Mock、a11y、axe 和 smoke 通过或观察性通过。
- `BUILD-080` 仍为 `IMPLEMENTED_PENDING_GATE`；真实管理员、正式知识库、服务器恢复、正式辅助技术、截图和课程资料前置门禁仍开放。

### 104.4 证据和计划审查结论

`BUILD-080` 标准六类文件已统一为 `BUILD-080-20260726-02`，metadata 的 T0/T1/T2 为 `PASS`，T3/T4 为 `OBSERVED_PASS`，T5 为 `BLOCKED_INPUT`，T6 为 `REVIEW_REQUIRED`。本次只关闭 BUILD-080 标准证据陈旧问题，不关闭正式 BUILD 门禁；当前 `BUILD-000 = BLOCKED_INPUT`，最终发布继续 `blocked`。证据见 `acceptance/frontend/BUILD-080/test-output.txt` 和 `acceptance/frontend/BUILD-080/metadata.json`。

## 105. 2026-07-26 BUILD-090 Agent 与 Spark 本地完整复测

### 105.1 复测范围

本批次为 BUILD-090 attempt 2，运行号 `BUILD-090-20260726-02`。范围覆盖 Agent 上下文和边界 API、Adapter runtime、图谱/情景/评测夹具、Xingchen HTTP/SSE 本地夹具、Agent 单元、Mock 性能、Spark Assistant 协议、前端全量质量门禁和标准证据身份。

真实 Xingchen Workflow、正式知识库版本、课程 PDF、Moodle 三角色、正式 API/OpenAPI、正式辅助技术、六视口人工证据和服务器恢复仍不在本地输入范围内。本地 Spark Assistant 测试端点只作为协议观察证据，不能代表正式 Workflow。

### 105.2 T0-T6 结果

| 层级 | 命令/检查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和安全审查 | Agent-001～010、Spark 协议/鉴权、来源、隐私、回退和外部边界 | 范围和敏感值边界明确；Spark 错误鉴权仍独立阻断 | `PASS` |
| T1 静态和构建 | Agent/Adapter 测试、编译、Shell、diff、前端 lint/typecheck/build | 全部适用静态检查通过；生产构建 `1694 modules` | `PASS` |
| T2 业务和协议规则 | 上下文/边界/评测/图谱/情景/Adapter 单元、离线 Spark 契约、性能夹具 | Agent API/夹具通过；Adapter 单元 `10/10`；离线 Spark `7/7`；性能 `30 samples` | `PASS` |
| T3 API 与上游集成 | HTTP Workflow 夹具、API 契约、Spark 正向和协议负向 | HTTP 夹具通过，API `92 routes`；Spark 正向观察性通过，参数负向 `4/4`；错误凭据负向 FAIL | `OBSERVED_PASS` |
| T4 浏览器流程 | 完整 Mock、Agent retry/cancel、教师/管理员流程、a11y/smoke | Mock `22/22`、a11y `3/3`、smoke `2/2`；真实角色未验收 | `OBSERVED_PASS` |
| T5 安全、性能与真实环境 | Spark 鉴权、正式 Workflow 性能、课程知识库、正式辅助技术和恢复 | 错误 key/secret/date 仍最终 code=0；正式环境未提供 | `BLOCKED_INPUT` / `FAIL` |
| T6 标准证据和账本 | BUILD-090 六类文件、唯一 run_id、Spark 脱敏证据和进度校验 | `BUILD-090-20260726-02` 标准身份一致；P0 `SPARK-AUTH-FAIL-001` 保持开放 | `REVIEW_REQUIRED` |

### 105.3 关键验收结果

- `AGENT-001`～`AGENT-010` 的本地上下文、权限、资料不足、策略、诊断、教师草稿、主观题初评、情景、断流恢复、非法来源和跨课程边界均有当前隔离证据。
- Xingchen HTTP/SSE 夹具验证服务端 Authorization 注入、SSE 事件、来源核验和错误映射；它不代表真实 Workflow。
- Spark 正向 handshake `101`、`header.code=0`、3 帧和正常关闭通过；4/4 参数负向返回脱敏错误码 `10003/10004`。
- `wrong-app-id` 返回 `11200`，但 `wrong-api-key`、`wrong-secret` 和 `tampered-date` 均进入正常 `header.code=0` 完成，远端鉴权脚本退出码 `6`；该 P0 失败不能改写为通过。
- Mock 性能仅为观察性结果：30 samples，p50 `40.01ms`，p95 `51.02ms`，不能替代真实 Workflow 首 token、完整回答和并发容量验收。

### 105.4 复测结论

BUILD-090 标准证据已更新为 `BUILD-090-20260726-02`，但正式 BUILD 仍为 `IMPLEMENTED_PENDING_GATE`。`SPARK-AUTH-FAIL-001` 保持 P0 `FAIL`，真实 Workflow、知识库、课程 PDF、角色、正式辅助技术、恢复和性能门禁仍开放；`BUILD-000 = BLOCKED_INPUT`，最终发布继续 `blocked`。证据见 `acceptance/frontend/BUILD-090/test-output.txt`、`acceptance/frontend/BUILD-090/metadata.json` 和 `acceptance/frontend/BUILD-090/spark-auth-negative-revalidation-20260726-13.txt`。

## 106. 2026-07-26 BUILD-100 测试方案复测与计划进一步审查

### 106.1 审查目标和运行身份

本轮把前面写入的通用 T0-T6 方案实际应用到 BUILD-100，检查测试命令、阈值、浏览器环境、标准证据身份、账本状态和正式阻断边界是否一致。当前权威运行号为 `BUILD-100-20260726-02`，attempt `2`，supersede `BUILD-100-20260725-01`。本轮只验证发布前硬化、前端质量门禁和证据链，不读取或归档 API Key、API Secret、Cookie、Authorization、签名 URL、完整问答或真实学生数据。

### 106.2 T0-T6 实际执行矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 错误边界、脱敏诊断、懒加载、PDF iframe、Nginx 缓存、全局搜索/帮助/设置、回退和敏感值边界审查 | 范围、回退和禁止记录项清楚；未发现新的未处理 P0/P1 | `PASS` |
| T1 静态和构建 | `python3 scripts/test_frontend_hardening.py`、`python3 -m compileall -q agent-adapter scripts`、`bash -n scripts/*.sh`、`git diff --check`、`cd frontend && npm run lint`、`npm run typecheck`、`npm run build` | 硬化 `FRONTEND_HARDENING_OK`；编译、Shell、diff、lint、typecheck 退出码为 0；构建 `1694 modules` 且生成 Admin 独立 chunk | `PASS` |
| T2 单元和组件规则 | `cd frontend && npm run test:all -- --run` | 5 个文件、`35/35`；错误边界、客户端诊断和前端业务规则均在全量结果中 | `PASS` |
| T3 API/UI 契约 | `python3 scripts/test_api_contract.py`、`python3 scripts/test_ui_contract.py` | API `92 routes`、UI 契约通过；本批次不改写正式 Moodle 契约，正式 API/OpenAPI 仍是外部门禁 | `OBSERVED_PASS` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1`、覆盖预览/Mock 退出分支的 `npm run test:e2e -- --workers=1` | Mock `22/22`；标准 smoke `2/2`，覆盖 `1440x900` 和 `390x844`、搜索/帮助/设置/用户菜单及退出双路径 | `OBSERVED_PASS` |
| T5 质量和正式验收 | `npm run test:a11y -- --workers=1`、`npm run test:axe -- --workers=1`，并审查 Docker/HTTPS/真实角色/恢复/人工辅助技术 | 自定义 a11y `3/3`、axe `4/4`（默认规则含 color-contrast）；Docker 容器运行、正式 HTTPS、三角色、六视口人工和恢复未提供 | `BLOCKED_DEPENDENCY` |
| T6 证据和门禁复审 | 六类 BUILD-100 标准文件、唯一 run_id、T0-T6 矩阵、进度账本、脱敏和差异校验 | 六类文件统一为 `BUILD-100-20260726-02`；账本校验通过；正式门禁仍开放 | `REVIEW_REQUIRED` |

### 106.3 逐项验收条件

- BUILD-100 的本地硬化、错误恢复、脱敏诊断、懒加载、缓存策略和全局壳层必须有代码审查和自动化结果；任一敏感值扫描命中都直接阻断证据归档。
- T1 必须全部退出码为 0，生产构建必须成功并保留构建模块数和独立 Admin chunk；构建失败时不得使用上一轮产物冒充本轮结果。
- T2 必须执行 `test:all` 全量套件；`test:unit`、`test:component` 或测试名称筛选的结果只能作为补充，不能代替 `35/35` 全量结果。
- T3 本地 API/UI 契约必须通过并明确 `local-isolated-adapter` 边界；不能把本地 `92 routes` 解释为正式 Moodle API/OpenAPI 已验收。
- T4 Mock 浏览器只能标记 `OBSERVED_PASS`；必须覆盖刷新、错误态、恢复、重复操作、移动视口和真实/预览退出分支。第一次在受限沙箱因 `listen EPERM` 超时的结果标记为测试基础设施阻断，不计为产品断言失败；在允许回环监听环境重跑后以 `22/22` 为权威结果。
- T5 的本地 a11y/axe 结果不能替代正式角色、正式域名 HTTPS、六视口截图、键盘/屏幕阅读器、容器内 Nginx header、健康检查和服务器恢复演练。
- T6 只有六类标准证据共享同一运行号、metadata 与 review 的 T0-T6 状态一致、证据路径存在、脱敏和账本校验通过，才允许签核；本轮因正式 T5 条件缺失保持 `REVIEW_REQUIRED`。

### 106.4 进一步审查结论

1. 计划第 27 节的通用协议和本轮 BUILD-100 专用矩阵均可执行；命令在当前仓库存在，API `92 routes`、UI 契约、硬化、编译、Shell 和 diff 检查均通过。
2. BUILD-100 六类标准证据已从旧运行号切换到唯一的 `BUILD-100-20260726-02`；旧运行保留为 superseded 历史，不能覆盖新结果。
3. 当前本地前端质量门禁为：硬化 PASS、lint/typecheck PASS、Vitest `35/35` PASS、构建 `1694 modules` PASS、Mock `22/22` OBSERVED_PASS、a11y `3/3` OBSERVED_PASS、axe `4/4` OBSERVED_PASS、标准 smoke `2/2` OBSERVED_PASS。
4. 浏览器输出中的 `8081 ECONNREFUSED` 是未启动 Adapter 时预览错误态的已知边界，断言仍通过；它不被记录为产品故障，也不被升级为真实 Adapter 验收。
5. 本轮不关闭任何正式 BUILD：`BUILD-000 = BLOCKED_INPUT`、`BUILD-100 = IMPLEMENTED_PENDING_GATE`，课程 PDF、真实 Moodle 三角色、正式 API/OpenAPI、Docker/Nginx 运行、HTTPS、恢复、正式辅助技术、真实 Workflow 和三项提交材料仍阻断最终发布。

### 106.5 后续重测规则

修改错误边界、诊断、路由懒加载、PDF 资源策略、Nginx、全局壳层、前端依赖、测试配置或证据生成脚本时，从受影响最早的 T1 开始重跑 T1-T6；若影响 API/client 契约，先重跑 T3；若影响浏览器配置，必须在允许回环监听的隔离环境重跑 T4/T5。Docker、HTTPS、真实角色、课程 PDF、恢复或正式 API 输入恢复后，从 BUILD-000 T0 重新执行受影响后续批次。任何失败必须保留退出码、失败分类、修复提交范围和唯一新运行号，禁止覆盖旧证据。

本轮权威证据见 `acceptance/frontend/BUILD-100/metadata.json`、`acceptance/frontend/BUILD-100/test-output.txt`、`acceptance/frontend/BUILD-100/review.md` 和 `acceptance/frontend/BUILD-000/plan-test-audit-20260726-16.txt`。

## 107. 2026-07-26 首页真实数据边界复测与计划终审

### 107.1 本轮范围和审查目标

本轮针对首页真实会话仍显示预览指标的问题完成一次小范围构筑后复审，并复核第 27 节 T0-T6 测试协议是否覆盖本次变更。修改范围为 `frontend/src/types.ts`、`frontend/src/data/preview.ts`、`frontend/src/App.tsx`、`frontend/src/App.test.tsx`，以及与浏览器门禁稳定性相关的 `frontend/tests/axe.spec.ts`、`frontend/tests/smoke.spec.ts`。本轮没有修改 Adapter 路由、OpenAPI、数据库迁移、权限协议或生产路由。

验收必须证明两条边界同时成立：预览模式仍显示明确的示例数据；已认证但服务端返回空列表时，章节、资料、建议、通知、评分和学习时长不能回退到预览值，也不能显示伪造的课程动态。

### 107.2 构筑后 T0-T6 测试方案和结果

| 层级 | 必须执行/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围与代码审查 | 对比真实会话、预览会话和会话过期三条数据路径；审查 PlatformData 新字段、空态、敏感值和回退边界 | 真实空响应与预览数据路径分离；无新增 API、权限或敏感信息范围 | `PASS` |
| T1 静态与构建 | `npm run lint`、`npm run typecheck`、`npm run build` | lint/typecheck 退出码 0；生产构建 `1694 modules` | `PASS` |
| T2 单元与组件 | `npm run test:all -- --run`，重点检查 authenticated empty data 回归用例 | 5 个测试文件、`36/36`；新增空真实会话回归通过 | `PASS` |
| T3 API 与契约 | 判断是否改动 Adapter/API；若改动则重新生成 OpenAPI 并执行契约测试 | 本轮无 API schema/route 变更，记 `NOT_APPLICABLE`；沿用最近 `92 routes/91 paths` 证据 | `NOT_APPLICABLE` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1`、`npm run test:e2e -- --workers=1`；覆盖刷新、预览空态、用户菜单和退出分支 | Mock `22/22`；标准 smoke `2/2`，覆盖 `1440x900`、`390x844` 和双退出分支 | `OBSERVED_PASS` |
| T5 质量与辅助技术 | `npm run test:a11y -- --workers=1`、`npm run test:axe -- --workers=1`，并区分本地结果与正式辅助技术 | 自定义 a11y `3/3`；axe 默认规则 `4/4`；正式角色、屏幕阅读器、HTTPS 和六视口人工证据仍缺失 | `OBSERVED_PASS` |
| T6 证据和门禁复审 | 核对唯一 run_id、命令退出码、失败重测原因、账本和脱敏扫描 | 新证据身份唯一且可追溯；正式外部输入仍阻断，不能关闭 BUILD | `REVIEW_REQUIRED` |

### 107.3 失败重测和测试基础设施审查

第一次复测暴露两个测试层问题：axe 使用 `setLegacyMode(true)` 时连最小探针也超时；标准 smoke 在首页 React 壳层完成挂载前点击用户菜单，导致元素稳定性等待超时。两者都不能被记录为产品缺陷或通过。修复后 axe 使用当前插件默认分析路径，smoke 先等待“早上好，林同学”标题和用户菜单可见，再执行点击；在允许本机回环监听的环境重跑后分别得到 axe `4/4` 和 smoke `2/2`。

沙箱内 `listen EPERM` 属于浏览器测试基础设施限制；预览模式的 `8081 ECONNREFUSED` 是未启动 Adapter 时的预期错误态，页面断言仍通过。证据中保留这些分类，不能把它们转写成正式角色或真实 Adapter 通过。

### 107.4 逐项验收条件

- 预览模式的样例通知和学习时长仍可见，并带有预览提示。
- 已认证空数据只显示明确空态或“待同步”，不出现预览通知、预览建议、预览章节数、预览资料数和预览评分。
- 真实会话下首页指标由 `PlatformData` 驱动；以后新增首页指标必须同时提供服务端字段、空态和回归断言。
- T4/T5 的本地 Mock、预览、axe 和自定义 a11y 结果只能标记 `OBSERVED_PASS`，不能替代正式 Moodle 三角色、正式辅助技术、HTTPS 和人工验收。
- 任何后续 API 字段、首页状态、路由壳层、浏览器测试配置或权限变化，都必须从最早受影响的 T0/T1 层重新执行并生成新的 run_id。

### 107.5 计划终审结论

本轮关闭“首页真实会话显示预览数据”的本地回归缺口；测试方案、失败分类、重测规则和证据路径已对齐。权威本地证据为 `acceptance/frontend/BUILD-100/frontend-data-driven-revalidation-20260726-17.txt`。

本轮不关闭正式门禁：`BUILD-000 = BLOCKED_INPUT`、`BUILD-100 = IMPLEMENTED_PENDING_GATE`、最终发布仍为 `blocked`。课程 manifest 要求的 20 个 PDF、真实 Moodle 三角色、正式 API/OpenAPI、Docker/Nginx 运行、HTTPS、服务器恢复、正式辅助技术、真实 Xingchen Workflow、Spark 错误鉴权语义和提交材料仍需外部输入或正式环境验收。

### 107.6 配置和证据链终审

终审命令及结果：

```text
python3 scripts/validate_project_progress.py                         PASS metadata=11 blockers=21 evidence_refs=150 redaction_scan=PASS
python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data  PASS 12 tests
python3 -m compileall -q agent-adapter scripts                                  PASS
bash -n scripts/*.sh                                                            PASS
git diff --check                                                                PASS
strict YAML duplicate-key audit                                                  PASS
```

审查确认：新运行号在 `test_runs`、证据文件和计划引用中唯一；`PROJECT_PROGRESS.yaml` 的 snapshot 由刷新脚本更新为当前工作树；敏感值扫描没有输出或记录任何测试凭据；T3 的 `NOT_APPLICABLE` 有明确原因；本地 `OBSERVED_PASS` 没有被升级为正式 `PASS`。因此计划文档、测试方案、证据索引和门禁状态已经一致，但项目交付状态仍受外部输入阻断。
## 108. 2026-07-26 资料收藏列表闭环构筑后 T0-T6 复审

### 108.1 构筑范围和输入边界

本轮完成计划中 /favorites“收藏和笔记”功能的最小真实闭环，运行号为 BUILD-040-FAVORITES-20260726-01，attempt 1。变更覆盖 CourseStore.favorite_resources、GET /api/student/resources/favorites、本地 OpenAPI/API manifest、前端 FavoriteResource DTO、学生“资料收藏”页面、导航入口、取消收藏和对应 Store/API/Vitest/Mock Playwright 测试。

本轮只使用本地隔离 SQLite、Mock Auth、Mock Workflow 和课程 manifest 元数据。接口只返回当前用户收藏的已发布且属于课程 1 的资源，并投影收藏时间和未删除笔记数量；不读取或记录 API Key、API Secret、Cookie、Authorization、签名 URL、完整问答或真实学生数据。课程 manifest 要求的 20 个 PDF 仍然缺失，因此阅读器继续显示“文件待挂载”，不能用占位 PDF 关闭资料门禁。

### 108.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围与代码审查 | Store 查询、课程和用户隔离、已发布可见性、student 权限、预览空态、取消收藏回退、敏感值和 rollback 审查 | 查询不暴露 storage path；非学生 403；预览不伪造收藏；现有收藏写接口的 CSRF/幂等边界未削弱 | PASS |
| T1 静态与构建 | test_frontend_hardening.py、UI/API 契约、Python 编译、Shell 语法、git diff --check、lint、typecheck、生产构建 | 硬化/UI/API 全部通过；API 93 routes；lint/typecheck 通过；生产构建 1694 modules | PASS |
| T2 单元与业务规则 | Store、收藏 API、前端 client DTO 和全量 Vitest | Store 10/10；收藏 API RESOURCE_FAVORITES_API_OK；Vitest 37/37；覆盖空列表、分页、403、422、用户隔离、笔记数量、取消收藏和幂等写入 | PASS |
| T3 API 与契约 | 先生成本地 OpenAPI，再执行 API contract 和隔离 ASGI API；核对输出字段和错误包络 | 本地 OpenAPI 92 paths；API contract 93 routes；API 隔离测试通过；正式 Moodle API/OpenAPI 和真实角色 namespace 未提供 | OBSERVED_PASS |
| T4 浏览器流程 | 定向收藏列表流程、完整 Mock Playwright、刷新、空态、打开资料、取消收藏 | 完整 Mock Playwright 23/23；覆盖收藏空态、列表笔记数量、资料入口和取消收藏；使用隔离 Mock，不替代正式三角色 | OBSERVED_PASS |
| T5 质量与外部验收 | a11y、axe、标准 smoke、正式角色、HTTPS、六视口人工、课程 PDF、容器/恢复和真实 Workflow | 自定义 a11y 3/3、axe 4/4、标准 smoke 2/2；正式角色、PDF、HTTPS、恢复、人工辅助技术和真实 Workflow 仍缺失 | BLOCKED_INPUT |
| T6 证据与门禁复审 | 唯一 run_id、证据脱敏、计划/账本同步、标准证据身份和正式门禁审查 | 专项证据与本节共享 BUILD-040-FAVORITES-20260726-01；脱敏要求满足；BUILD-040 标准六类证据尚未重签，不能关闭正式 BUILD | REVIEW_REQUIRED |

### 108.3 逐项验收条件

- 收藏列表只返回当前学生自己的收藏；其他学生和教师不能读取该列表。
- 已取消收藏的资源不再出现在列表中；重复写入不产生重复行，现有 Idempotency-Key 语义保持有效。
- 列表资源必须经过课程和 published 条件过滤，响应不得包含 storage_path 等部署私有字段。
- note_count 只统计当前用户未删除的页码笔记；没有笔记时显示“已收藏”，不能显示其他用户笔记数量。
- 前端真实会话加载服务端列表；预览模式和真实空列表分别显示明确空态，不能注入示例收藏。
- 资源未挂载时只能进入状态页，不能伪造 PDF、iframe 或可读页码。
- Mock、a11y、axe 和 smoke 结果只能记为 OBSERVED_PASS，不能替代正式 Moodle 三角色、正式 API、人工辅助技术、HTTPS、恢复和真实 Workflow。

### 108.4 失败分类和重测规则

第一次 Mock 浏览器尝试中，收藏流程使用不存在的伪造资源 ID，取消收藏 API 返回 404；这是测试夹具违反资源前置条件，分类为 TEST_FIXTURE_FAILURE，不计为产品失败。修正为 manifest 派生的真实隔离资源 ID 后，从该 T4 用例及完整 Mock 批次重跑，结果为 23/23。

沙箱内第一次完整 Mock 启动因本机回环监听超时，分类为 BLOCKED_TEST_INFRA；在允许回环监听的隔离环境完成权威重跑。a11y 和标准 smoke 日志中的 8081 ECONNREFUSED 属于未启动 Adapter 时的预览错误态，页面断言仍通过，不升级为产品故障或真实 API 通过。

后续若修改收藏查询、资源发布状态、用户/课程条件、客户端 DTO、/favorites 路由、取消收藏 header、OpenAPI、Mock fixture 或分页逻辑，必须从 T0 重新审查，并至少重跑 T1-T6；若只恢复正式 PDF、Moodle 三角色、正式 API、HTTPS、容器、恢复或真实 Workflow，则从 BUILD-000 T0 重新执行受影响后续门禁。任何失败需保留唯一新 run_id、退出码、失败分类和修复后的重测证据。

### 108.5 计划进一步审查结论

本轮确认计划第 27 节 T0-T6 通用测试方案能够约束一个跨 Store、API、契约、前端、浏览器和质量门禁的完整构筑；第 108 节补充了本功能的精确命令、阈值、验收条件、测试夹具失败分类、基础设施失败分类、证据身份和重测起点。专项证据为 acceptance/frontend/BUILD-040/favorites-list-revalidation-20260726-18.txt。

本轮本地功能达到实现完成和观察性验收，但不关闭正式门禁：BUILD-000 = BLOCKED_INPUT、BUILD-040 = IMPLEMENTED_PENDING_GATE、BUILD-100 = IMPLEMENTED_PENDING_GATE、最终发布继续 blocked。开放阻断仍包括 20 个课程 PDF、真实 Moodle 三角色、正式 API/OpenAPI、真实 Workflow/知识库、Docker/Nginx 运行、HTTPS、服务器恢复、正式辅助技术、六视口人工证据和提交材料。不得把本轮任何 OBSERVED_PASS 改写为正式 PASS。

## 109. 2026-07-26 BUILD-090 Agent 流式异常闭环构筑后 T0-T6 复审

### 109.1 构筑范围、运行身份和变更审查

本轮运行号为 `BUILD-090-AGENT-STREAM-20260726-19`，attempt `1`。范围是 Agent 流式异常闭环：讯飞上游超时、网络异常、截断流、错误帧、非 2xx 错误包络、用户取消、组件卸载、重试次数和取消后的迟到 token/done。变更文件为 `agent-adapter/tests/test_main.py`、`frontend/src/api/client.ts`、`frontend/src/api/client.test.ts`、`frontend/src/App.tsx`，不修改课程数据 manifest、PDF hash/page_count、Spark 凭据或生产密钥。

审查确认：服务端原有 `workflow_timeout`、`workflow_network_error`、`upstream_disconnected` 映射有效，但原单元测试没有分别锁定超时、网络异常和截断流；客户端原有 AbortSignal 透传和重复 `done` 保护有效，但读取器在取消后收到迟到数据时没有二次中止检查，非 2xx Agent 响应也没有保留服务端 `error.code` 和 `request_id`。本轮补齐这些边界，并为 Assistant 页面增加卸载时取消。

### 109.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 对照 `xingchen_stream`、`streamAgent`、`AssistantPage` 审查 timeout、断流、错误帧、取消、重试、组件卸载、迟到帧、reader 释放、敏感值和 rollback | 范围仅涉及流式错误处理和前端生命周期；凭据、Cookie、Authorization、签名 URL、完整问答不进入证据；未改变正式 Spark 鉴权结论 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；`python3 scripts/test_frontend_hardening.py`；`python3 scripts/test_ui_contract.py`；`cd frontend && npm run lint`；`npm run typecheck`；`npm run build` | 编译、Shell、diff、硬化、UI 契约、lint 和 typecheck 均通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和协议规则 | `python3 -m unittest -q agent-adapter/tests/test_main.py`；`cd frontend && npm run test:all -- --run` | Adapter `12/12`；Vitest `39/39`；覆盖 timeout、network failure、truncated stream、provider error frame、non-2xx envelope、AbortSignal 和 late frame | `PASS` |
| T3 API 和上游夹具 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_xingchen_http_fixture.py`；`python3 scripts/test_agent_context_api.py`；`python3 scripts/test_agent_boundary_api.py` | 本地 OpenAPI `92 paths`；API 契约 `93 routes`；HTTP/SSE、上下文和边界夹具通过；只证明本地协议，不证明真实 Workflow | `OBSERVED_PASS` |
| T4 浏览器流程 | `cd frontend && npm run test:e2e:mock -- --workers=1`，并核对 retry/cancel 用例的请求数、状态清理和迟到回答 | Mock Playwright `23/23`；重试严格为 `2` 次请求；取消后延迟回答不渲染；真实 Moodle 三角色和真实 Workflow 未执行 | `OBSERVED_PASS` |
| T5 质量和外部验收 | `cd frontend && npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；审查正式 Workflow、三角色、HTTPS、PDF、恢复、人工辅助技术 | 自定义 a11y `3/3`、axe `4/4`、标准 smoke `2/2`；正式外部和人工门禁仍缺失；标准 smoke/a11y 中的 `8081 ECONNREFUSED` 属预览未启动 Adapter 的预期错误态 | `OBSERVED_PASS` / `BLOCKED_INPUT` |
| T6 证据、账本和门禁 | 核对唯一 run_id、退出码、脱敏扫描、计划引用、失败分类、标准证据身份和 rollback | 专项脱敏证据已归档；第一次回环夹具监听被沙箱拒绝，分类为 `BLOCKED_TEST_INFRA`，授权隔离环境重跑通过；本地观察结果不能升级正式 BUILD | `REVIEW_REQUIRED` |

专项证据为 `acceptance/frontend/BUILD-090/agent-stream-failure-revalidation-20260726-19.txt`。

### 109.3 逐项验收条件

- 服务端上游超时必须输出 `event:error` 且 code 为 `workflow_timeout`，不得输出成功 `done`。
- 服务端上游网络异常必须输出 `workflow_network_error`；上游发送 token 后无结束帧必须输出 `upstream_disconnected`，不得自行补造 `done`。
- 服务端 provider 错误帧必须保留错误类别和可审计 request ID，不得把失败流标记为成功。
- 客户端收到非 2xx JSON 错误时必须保留服务端错误 `code`、message 和 request ID；没有 JSON 错误包络时才使用通用客户端错误。
- 客户端在每次 reader read 和每个 SSE block dispatch 前检查 AbortSignal；取消后必须 cancel/release reader，迟到 token/source/done 不得进入当前回答。
- Assistant 页面卸载必须取消未完成请求；用户重试只能由明确按钮触发，重试请求数必须可断言且不能自动递归重试。
- 上游 error 后只显示可重试失败状态；取消后只显示取消状态；未收到 done、错误帧、超时和断流均不得显示为成功回答。
- Mock、HTTP 夹具、a11y、axe 和 smoke 结果只能记为 `OBSERVED_PASS`，不能替代真实 Xingchen Workflow、知识库来源、Moodle 三角色、正式辅助技术、HTTPS、课程 PDF、恢复演练或真实性能。

### 109.4 失败分类、重测和回滚规则

本轮首次运行 `python3 scripts/test_xingchen_http_fixture.py` 在受限沙箱中因禁止绑定 `127.0.0.1` 返回 `PermissionError`，没有进入业务断言，分类为 `BLOCKED_TEST_INFRA`，不得记为产品失败。随后在允许回环监听的隔离环境重跑，得到 `XINGCHEN_HTTP_FIXTURE_OK`。这次重跑只解除测试基础设施限制，不改变真实外部门禁状态。

若后续修改 `xingchen_stream` 的错误码、HTTP client timeout、SSE 解析、`streamAgent`、AbortSignal、Assistant 状态机、重试按钮、路由卸载、Mock SSE fixture 或错误包络，必须从 T0 重新审查，并至少重跑 T1-T6；任何一次失败都要保留新 run_id、退出码、失败分类和修复后的权威重测结果。若只发生真实 Workflow、知识库、Moodle 角色、HTTPS、PDF、容器或恢复环境变化，则从 BUILD-000 T0 重跑受影响正式门禁，不得用本地回归替代。

回滚以本轮变更文件为边界：保留原有服务端错误码和状态协议，回退新增客户端错误包络解析、reader 取消/释放和页面卸载清理前，必须先恢复对应测试夹具；回滚后不得保留“测试通过但实现路径不存在”的证据。禁止通过修改 manifest、hash、page_count、生成占位 PDF 或屏蔽断言来关闭门禁。

### 109.5 计划进一步审查结论

本轮发现并修复了一个 P1 级本地异常闭环缺口：取消后迟到流数据可能在测试替身或非标准浏览器实现中继续进入 UI；同时补齐了非 2xx 错误信息丢失和 Adapter 超时/网络/截断流独立回归。修复后 T0/T1/T2 通过，T3/T4/T5 为本地观察性通过，T6 需要保留外部门禁审查。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`BUILD-090` 继续 `IMPLEMENTED_PENDING_GATE`，`BUILD-000` 继续 `BLOCKED_INPUT`，最终发布继续 `blocked`。`SPARK-AUTH-FAIL-001` 的 P0 `FAIL` 不因本轮本地 Agent 流式测试而改变。真实 Workflow 超时/断流/并发/恢复、正式知识库来源、Moodle 三角色、正式 API/OpenAPI、课程 PDF、Docker/HTTPS、服务器恢复、正式辅助技术和人工验收仍是关闭条件。

## 110. 2026-07-26 BUILD-030 学习图谱先修路径构筑后 T0-T6 复审

### 110.1 构筑范围、运行身份和代码审查

本轮运行号为 `BUILD-030-GRAPH-PATH-20260726-20`，attempt `1`。范围是学生学习图谱的先修路径：新增 `KnowledgeGraphPath` DTO 和 `/api/knowledge-graph/paths` 客户端调用，增加起点/目标选择、路径摘要、可点击路径步骤、图谱节点路径高亮，以及对应 CSS 和 Mock 浏览器验收。变更未修改课程 manifest、graph-baseline.json、PDF hash/page_count、Spark 凭据或生产密钥。

代码审查确认：

- 路径请求固定传递 `from`、`to` 和 `max_depth`，响应只接受服务端返回的节点 ID 顺序和深度。
- 预览模式禁用服务端路径操作，不生成伪造的先修路径；真实模式的路径步骤点击复用已加载节点详情。
- 路径高亮只根据返回 ID 命中当前图谱节点，起点和终点有独立状态，移动端路径面板会折叠为单列。
- 查询、起点或目标变化时会清理旧路径并使未完成请求失效，迟到响应不能覆盖当前图谱状态。
- 本地测试不记录凭据、Cookie、Authorization、签名 URL、完整问答或真实学生数据；回滚边界限于本轮图谱路径客户端/UI/样式/测试文件。

### 110.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查路径 DTO、query 编码、预览边界、起点/目标选择、节点高亮、步骤回跳、移动端 CSS、敏感值和回滚 | 范围闭合；不修改课程基线和凭据 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；`python3 scripts/test_frontend_hardening.py`；`python3 scripts/test_ui_contract.py`；`cd frontend && npm run lint`；`npm run typecheck`；`npm run build` | 编译、Shell、diff、硬化、UI 契约、lint、typecheck 通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和领域规则 | `python3 -m unittest -q agent-adapter/tests/test_main.py`；`cd frontend && npm run test:all -- --run` | Adapter `12/12`；Vitest `39/39`；路径 query 和 DTO 归一化包含在回归中 | `PASS` |
| T3 API 和夹具 | `python3 scripts/test_graph_scenario_fixture.py`；`python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_agent_context_api.py`；`python3 scripts/test_agent_boundary_api.py`；`python3 scripts/test_xingchen_http_fixture.py` | 图谱情景通过；OpenAPI `92 paths`；API `93 routes`；Agent 上下文/边界和 Xingchen HTTP 夹具通过；只证明本地隔离协议 | `OBSERVED_PASS` |
| T4 浏览器流程 | `cd frontend && npm run test:e2e:mock -- --workers=1`；选择 `kp-3-1` 到 `kp-3-4`，核对路径步骤、深度、节点高亮和中间节点详情 | Mock Playwright `24/24`；路径专项 `1/1`；显示 3 个节点、深度 2、高亮 3 个节点 | `OBSERVED_PASS` |
| T5 质量和外部验收 | `cd frontend && npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；审查真实图谱、Moodle 角色、六视口人工辅助技术 | 自定义 a11y `3/3`、axe `4/4`、标准 smoke `2/2`；正式角色、图谱版本和人工验收仍缺失 | `OBSERVED_PASS` / `BLOCKED_INPUT` |
| T6 证据、账本和门禁 | 核对唯一 run_id、退出码、证据存在、脱敏扫描、计划引用、状态边界和回滚说明 | 专项脱敏证据已归档；本节、进度账本和状态文档同步；正式外部门禁继续开放 | `REVIEW_REQUIRED` |

专项证据为 `acceptance/frontend/BUILD-030/graph-path-revalidation-20260726-20.txt`。

### 110.3 逐项验收条件

- 起点和目标选择器必须只展示当前服务端图谱节点；起点等于目标、加载中、预览模式和空节点列表时，路径按钮必须不可用或明确显示不可用原因。
- `GET /api/knowledge-graph/paths?from=kp-3-1&to=kp-3-4&max_depth=8` 必须返回有限路径；页面显示服务端路径长度和深度，不能用前端猜测替代响应。
- Mock 基线中 `kp-3-1 → kp-3-2 → kp-3-4` 必须显示 3 个步骤、深度 `2`，并在图谱板上高亮 3 个节点；点击中间步骤必须打开 `kp-3-2` 详情。
- 路径接口失败时只显示可重试错误，不保留上一条路径为成功结果；请求期间按钮禁用，路径结果不会跨查询错误地残留。
- 预览模式不调用路径接口、不伪造路径节点；正式模式节点正文和邻接关系仍来自服务端 API。
- 本地 Mock、a11y、axe、smoke 和 OpenAPI 结果只能记为 `OBSERVED_PASS`，不能替代正式图谱版本、课程 PDF 来源、真实 Moodle 三角色、六视口人工验收或最终发布门禁。

### 110.4 失败分类、重测和回滚规则

本轮第一次图谱路径浏览器断言使用了不在 `graph-baseline.json` 中的知识点名称，分类为 `TEST_FIXTURE_FAILURE`，不计为产品失败；修正为基线权威名称后，路径专项测试 `1/1`，完整 Mock 批次 `24/24`。

第一次并行浏览器批次出现 axe 最小探针超时和标准 smoke 用户菜单稳定性超时。它们没有形成业务断言失败：axe 串行重跑 `4/4`，smoke 串行重跑 `2/2`；固定顶栏按钮的测试使用强制点击，保留菜单事件和后续菜单项验收。受限沙箱中的 Xingchen 回环监听 `PermissionError` 分类为 `BLOCKED_TEST_INFRA`，授权隔离环境重跑为 `XINGCHEN_HTTP_FIXTURE_OK`。

若修改路径 API、DTO、query 编码、`KnowledgeGraphPage`、路径 CSS、Mock 图谱夹具或相关浏览器断言，必须从 T0 重新审查，并至少重跑 T1-T6。任何失败都要保留唯一新 run_id、退出码、失败分类和修复后的重测证据。若只恢复正式图谱版本、课程 PDF、Moodle 角色、正式 API、HTTPS、容器、恢复环境或人工辅助技术，则从 BUILD-000 T0 重跑受影响的正式门禁，不得以本地路径回归替代。

回滚只能恢复本轮新增路径客户端/UI/样式/测试文件；不得删除或改写 graph-baseline.json、manifest、PDF hash/page_count，也不得屏蔽路径断言或生成占位教材来关闭门禁。回滚后必须同步回退本节专项证据的状态，不能保留“测试通过但实现路径已不存在”的记录。

### 110.5 计划进一步审查结论

本轮确认计划第 27 节的 T0-T6 协议可以约束图谱路径从 API DTO、前端状态、节点高亮、浏览器交互到质量门禁的完整复审；本节补充了精确命令、阈值、权威图谱名称、夹具失败分类、基础设施失败分类、证据身份和重测起点。`BUILD030-GRAPH-PATH-001` 关闭，表示本地路径功能和测试方案已对齐；`BUILD030-REAL-001` 及课程资料/真实角色/六视口人工证据仍保持开放。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`BUILD-030` 继续 `PARTIAL_IMPLEMENTATION_PENDING_GATE`，`BUILD-000` 继续 `BLOCKED_INPUT`，最终发布继续 `blocked`。本轮本地观察性结果不改变 `SPARK-AUTH-FAIL-001` 的 P0 `FAIL`，也不关闭真实 Workflow、正式知识库、课程 PDF、Moodle 三角色、正式 API/OpenAPI、Docker/HTTPS、服务器恢复或正式辅助技术门禁。


## 111. 2026-07-26 BUILD-060 教师课堂活动管理构筑后 T0-T6 复审

### 111.1 构筑范围、运行身份和审查边界

本轮运行号为 BUILD-060-ACTIVITY-20260726-21，attempt 3。本轮完成并复审教师课堂活动管理页面：投票/问卷创建、选项维护、草稿保存、直接发布、允许次数和活动列表；复用已有活动 API 的教师权限、学生已发布过滤、CSRF、幂等、选项校验和审计。代码审查范围为 frontend/src/App.tsx、frontend/src/styles.css、frontend/tests/mock-api.spec.ts 及既有活动 API/Store。未修改课程 manifest、PDF hash/page_count、Spark 凭据、正式 Moodle/API 契约或生产部署。

本轮只使用 local-mock-and-isolated-api、隔离 SQLite/资源目录和允许回环监听的 Chrome/Playwright 环境。证据中不记录 API Key、API Secret、Token、Cookie、Authorization、签名 URL、完整问答或真实学生数据。

### 111.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围与代码审查 | 审查教师入口、活动 DTO、草稿/发布状态、学生可见性、选项和次数校验、权限/CSRF/幂等、审计、敏感值和回滚边界 | 范围闭合；服务端继续作为权限和业务规则裁决点；不改变课程基线和凭据 | PASS |
| T1 静态与构建 | npm run lint、npm run typecheck、npm run build、git diff --check | lint/typecheck/diff 退出码 0；生产构建 1694 modules | PASS |
| T2 单元与业务规则 | npm run test:all -- --run、scripts/test_activity_api.py；覆盖草稿、发布、学生过滤、选项/次数校验和幂等 | Vitest 5 files / 39 tests；ACTIVITY_API_OK | PASS |
| T3 API 与契约 | 复核活动路由、角色权限、CSRF、幂等和审计；确认是否改动正式 API/OpenAPI | local-isolated-adapter 活动契约通过；本轮未提供正式 Moodle API/OpenAPI | OBSERVED_PASS |
| T4 浏览器流程 | npm run test:e2e:mock -- --workers=1；教师活动专项流程；覆盖保存草稿、发布、学生过滤、刷新和既有核心流程 | Mock 25/25，活动专项 1/1 | OBSERVED_PASS |
| T5 质量与辅助技术 | npm run test:a11y -- --workers=1、npm run test:axe -- --workers=1、npm run test:e2e -- --workers=1；审查正式角色、键盘/屏幕阅读器和六视口 | 自定义 a11y 3/3、smoke 2/2；axe 四个用例均在 AxeBuilder.analyze() 超时，正式辅助技术和人工证据仍缺失 | OBSERVED_PASS / INFRA_TIMEOUT / BLOCKED_INPUT |
| T6 证据与门禁复审 | 核对唯一 run_id、退出码、失败分类、证据路径、脱敏扫描、账本、计划和状态边界 | 专项证据已归档；BUILD-060 仍 IMPLEMENTED_PENDING_GATE，T6 REVIEW_REQUIRED | REVIEW_REQUIRED |

专项证据为 acceptance/frontend/BUILD-060/activity-management-revalidation-20260726-21.txt。

### 111.3 逐项验收条件

- 教师能够创建投票/问卷草稿，填写合法选项和允许次数，并在保存后从教师列表恢复状态。
- 教师直接发布后，活动进入已发布状态；学生只看到已发布且属于当前课程的活动，不能看到草稿。
- 空标题、非法选项、重复选项、超出允许次数和越权写入必须由服务端拒绝；客户端不得只依靠隐藏按钮实现权限控制。
- 活动写请求必须携带 CSRF 保护和幂等语义；重复请求不得生成重复活动或重复响应；创建、发布和提交动作必须保留审计边界。
- 刷新后教师草稿/已发布状态和学生已发布列表必须与服务端一致；加载失败显示错误，不得显示假成功或预览活动。
- Mock、a11y 和 smoke 只能记为 OBSERVED_PASS；axe 本轮因引擎分析超时只能记为 INFRA_TIMEOUT，不能引用旧批次 4/4 冒充本轮通过。
- 正式 Moodle 三角色、正式 API/OpenAPI、20 个课程 PDF、正式审计、正式 axe/人工辅助技术、Docker/Nginx、HTTPS、恢复和真实 Workflow 未具备前，BUILD-060 和最终发布不得关闭。

### 111.4 失败分类、重测和证据规则

本轮标准 smoke 在第一次修正复选框后，于退出课程菜单项的稳定性等待超时；这是 React 壳层/Playwright 交互时序问题。补充 click({ force: true }) 后串行重跑为 2/2，分类为 TEST_HARNESS_STABILITY_TIMEOUT，不计为产品断言失败。axe 先在受限环境发生 WebServer 启动超时；在允许回环监听环境启动成功后，最小 HTML 探针和三个页面仍全部在 AxeBuilder.analyze() 内超时，统一分类为 TEST_HARNESS_INFRA_TIMEOUT，保留失败输出，不改写为通过。

Vite 日志中的 8081 ECONNREFUSED 仅表示标准 smoke/a11y 未启动真实 Adapter 时的预览错误态；页面断言通过，不能升级为真实 API 或真实 Moodle 角色证据。

若修改活动 API/DTO、教师活动页面、学生活动过滤、权限/CSRF/幂等、测试配置或 Mock 夹具，必须从 T0 重新审查并重跑 T1-T6，使用新的唯一 run_id。若只恢复课程 PDF、真实 Moodle 账号、正式 API、Docker/HTTPS、服务器恢复、正式辅助技术或真实 Workflow，则从 BUILD-000 T0 重跑受影响的正式门禁。回滚只能覆盖本轮活动 UI、测试和证据边界；不得删除既有课程/成绩数据、生成占位活动或 PDF、屏蔽断言或输出敏感值。

### 111.5 计划进一步审查结论

本轮确认第 27 节 T0-T6 协议能约束教师活动管理从表单状态、服务端权限、学生可见性、幂等审计、浏览器流程到质量门禁的完整复审，并补充了明确的测试阈值、失败分类、axe 超时边界、重测起点、证据路径和回滚规则。BUILD060-ACTIVITY-001 关闭，表示本地活动管理实现与测试方案已对齐；BUILD060-REAL-001、正式辅助技术和正式课程/API 输入继续开放。

计划审查结论为 DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN。BUILD-060 继续 IMPLEMENTED_PENDING_GATE，BUILD-000 继续 BLOCKED_INPUT，最终发布继续 blocked。本轮不改变 SPARK-AUTH-FAIL-001 的 P0 FAIL，也不关闭真实 Workflow、正式知识库、课程 PDF、Moodle 三角色、正式 API/OpenAPI、Docker/HTTPS 或服务器恢复门禁。


## 112. 2026-07-26 Chrome 147 axe 对比度兼容性与前端可访问性复审

### 112.1 构筑范围、运行身份和根因审查

本轮运行号为 FRONTEND-A11Y-20260726-22，attempt 1。变更仅覆盖 frontend/tests/axe.spec.ts 和 frontend/tests/a11y.spec.ts：保留 axe 默认规则集，显式排除在当前 Chrome 147 中会无限等待的 color-contrast 与 color-contrast-enhanced；同时增强自定义对比度检查，覆盖主内容叶文本、透明背景合成、有效前景色和 WCAG 大字号阈值。未修改业务组件、Adapter、API、课程 manifest、PDF hash/page_count、Spark 凭据或生产部署。

诊断顺序为：完整默认 axe 最小探针复现挂起；逐规则探针确认 color-contrast 触发；临时安装 axe 4.11.0 在同一 Chrome 147 中复现；使用单规则非对比度探针验证 axe 其余规则可以完成。结论是当前浏览器/axe 对比度规则兼容性阻断，不是页面断言或业务代码失败。提高测试超时、吞掉 incomplete 或引用旧批次 4/4 均不允许作为修复。

### 112.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围与根因审查 | 审查 axe 规则边界、最小探针、逐规则探针、Chrome/axe 版本、独立对比度校验、敏感值和回滚边界 | color-contrast 两条规则在 Chrome 147 复现挂起；排除是显式、可审计的临时兼容边界 | PASS / BLOCKED_DEPENDENCY |
| T1 静态与构建 | npm run lint、npm run typecheck、npm run build、git diff --check | lint/typecheck/diff 退出码 0；生产构建 1694 modules | PASS |
| T2 单元与前端回归 | npm run test:all -- --run | Vitest 5 files / 39 tests | PASS |
| T3 API 与契约 | 判断是否改动 API、权限、Store、OpenAPI 或数据库 | 本轮无业务/API 变更 | NOT_APPLICABLE |
| T4 浏览器流程 | npm run test:e2e:mock -- --workers=1、npm run test:e2e -- --workers=1 | Mock 25/25；标准 smoke 2/2 | OBSERVED_PASS |
| T5 质量与辅助技术 | npm run test:a11y -- --workers=1、npm run test:axe -- --workers=1；审查完整内置对比度规则和正式人工辅助技术 | 自定义 a11y 3/3；axe 其余默认规则 4/4；内置两条对比度规则仍 BLOCKED_DEPENDENCY；正式角色/人工证据缺失 | OBSERVED_PASS_WITH_OPEN_RULE_BLOCKER / BLOCKED_INPUT |
| T6 证据与门禁复审 | 核对唯一 run_id、显式排除项、退出码、证据路径、脱敏扫描、账本和重测规则 | 专项证据已归档；正式发布门禁不变 | REVIEW_REQUIRED |

专项证据为 acceptance/frontend/BUILD-100/a11y-contrast-revalidation-20260726-22.txt。

### 112.3 逐项验收条件

- a11y 自定义检查必须覆盖所有可见主内容叶文本；透明背景必须按祖先背景合成，普通文本阈值为 4.5:1，大字号阈值为 3:1。
- axe 测试必须明确记录排除的规则 ID、原因、浏览器版本和恢复条件；排除不能隐藏其他 axe violation。
- 探针、student、teacher、admin 四个 axe 用例的其余默认规则必须全部退出码 0、无 violation，当前结果为 4/4。
- Chrome/axe 兼容性恢复后，必须移除两条排除规则，在同一四页矩阵重新运行；完整 color-contrast 通过后才可关闭该本地阻断。
- Mock、a11y、smoke 和当前受限 axe 结果只能记为 OBSERVED_PASS 或带明确阻断的观察性结果，不能替代真实 Moodle 角色、屏幕阅读器、键盘人工验收、六视口截图、HTTPS 或正式辅助技术。

### 112.4 失败分类、重测和回滚规则

完整默认 axe 和 color-contrast 单规则在 Chrome 147 中无限等待，分类为 BLOCKED_DEPENDENCY，不是产品 PASS/FAIL；axe 4.11.0 临时隔离验证同样复现。受限沙箱直接启动 Chrome 时出现 SIGTRAP，分类为 BLOCKED_TEST_INFRA；授权环境中的非对比度 axe 4/4 和自定义 a11y 3/3 已完成。

修改页面、CSS、浏览器配置、axe 依赖或 a11y 断言时，从 T0 重新审查并重跑 T1-T5；修改 API 或业务代码时按第 27 节从最早受影响层重跑 T1-T6。若恢复可用 Chrome/axe 组合，先删除显式排除列表，再运行完整 axe 四页矩阵。回滚只能恢复本轮测试文件和证据边界，不得删除对比度断言、关闭所有规则或保留不再匹配实现的通过证据。

### 112.5 计划进一步审查结论

本轮修复了“自定义对比度检查覆盖不足”和“axe 超时没有明确规则边界”两个本地质量问题；增强检查通过 3/3，axe 非对比度默认规则通过 4/4，并将内置 color-contrast 兼容性阻断显式写入代码、测试输出、证据和账本。FRONTEND-A11Y-CHROME147-001 关闭，表示当前测试方案对根因和重测规则已对齐；FRONTEND-A11Y-001 继续开放，直到兼容环境完成完整 color-contrast axe 扫描及正式人工辅助技术验收。

计划审查结论为 DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN。BUILD-100 继续 IMPLEMENTED_PENDING_GATE，BUILD-000 继续 BLOCKED_INPUT，最终发布继续 blocked。

随后进行文档一致性复核时发现 `PROJECT_PROGRESS.yaml` 的 `plan_review.scope` 曾重复列出 `frontend/tests/axe.spec.ts`；已删除重复项，未改变测试范围或业务代码。刷新快照并重跑 `scripts/validate_project_progress.py`、`scripts/test_validate_project_progress.py`、`scripts/test_refresh_progress_snapshot.py` 和 `git diff --check` 后，结果为 `metadata=11`、`blockers=21`、`evidence_refs=160`、`redaction_scan=PASS`、校验器 `8/8` 与 `2/2` 通过。该复核不改变完整内置对比度规则、真实角色、正式辅助技术和最终发布门禁的开放状态。

## 113. 2026-07-26 规范课程路由与成绩入口构筑后 T0-T6 复审

### 113.1 构筑范围、运行身份和边界

初始构筑运行号为 `BUILD-010-ROUTE-20260726-23`，attempt 1；修复成绩页课程参数占位后，以 `BUILD-010-ROUTE-20260726-24`、attempt 2 完成权威重测。依据第 5 节路由规划，补齐了学生规范课程路由 `/courses/:courseId/...` 和教师规范课程路由 `/teacher/courses/:courseId/...` 到现有页面能力的受权限保护映射，保留既有 `/course`、`/teacher/*` 兼容路径；新增学生课程成绩页 `/courses/:courseId/grades`，成绩只使用服务端返回的任务状态和分数。章节路由支持从 URL 读取 `chapterId`，刷新后保持指定章节。

本轮只修改 `frontend/src/App.tsx` 和 `frontend/tests/mock-api.spec.ts`，未修改 API 路由、Store、数据库、课程 manifest、PDF hash/page_count、Spark 凭据、Workflow 或部署配置。路由映射不伪造多课程数据；`courseId` 仅作为 URL 上下文，当前课程内容和权限仍由会话/API 决定。学生访问教师规范路由必须被重定向到工作台，非学生访问教师路由仍需由服务端再次校验。

### 113.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围与路由审查 | 对照第 5 节学生/教师路由表，核对参数、兼容路径、成绩入口、越权边界和数据真实性 | 规范路径映射到已有页面；成绩页不生成服务端不存在的成绩；API/数据边界未扩张 | PASS |
| T1 静态与构建 | `npm run lint`、`npm run typecheck`、`npm run build`、`git diff --check` | lint/typecheck/diff 退出码 0；生产构建 1694 modules | PASS |
| T2 单元与组件回归 | `npm run test:all -- --run` | Vitest 5 files / 39 tests | PASS |
| T3 API 与契约 | 判断是否改动 API、权限、Store、OpenAPI 或数据库 | 无 API/Store 变更；使用既有 Mock Adapter 仅支撑浏览器页面加载 | NOT_APPLICABLE |
| T4 浏览器路由与角色 | 规范学生路由、规范教师路由、学生访问教师路由；完整 `npm run test:e2e:mock -- --workers=1` | 路由专项 3/3；完整 Mock 28/28；学生越权重定向通过 | OBSERVED_PASS |
| T5 质量与辅助技术 | `npm run test:a11y -- --workers=1`、`npm run test:axe -- --workers=1`、`npm run test:e2e -- --workers=1` | 自定义 a11y 3/3；axe 非对比度默认规则 4/4；标准 smoke 2/2；内置对比度规则仍受 Chrome 147 兼容性阻断 | OBSERVED_PASS / BLOCKED_DEPENDENCY |
| T6 证据与门禁复审 | 核对唯一 run_id、测试输出、权限边界、脱敏、外部前置检查和状态更新 | 专项证据已归档；BUILD-010 仍需真实角色/API/部署门禁，不升级正式 PASS | REVIEW_REQUIRED |

初始证据为 `acceptance/frontend/BUILD-010/route-contract-revalidation-20260726-23.txt`；因修复成绩页课程参数后，权威证据为 `acceptance/frontend/BUILD-010/route-contract-revalidation-20260726-24.txt`。

### 113.3 逐项验收条件

- `/courses`、`/courses/:courseId`、章节、资料、材料、任务、考试、讨论、进度、成绩和 Agent 规范路径必须渲染对应页面，不得因未知路径回退到错误的根页面。
- `/teacher/courses/:courseId/overview`、`editor`、`question-bank`、`assignments`、`exams`、`resources`、`activities`、`grading`、`gradebook`、`analytics` 和 `agent` 必须进入教师页面；带作业 ID 的批改路径必须保持参数。
- 学生访问任一教师规范路径必须重定向到 `/learn/` 工作台，且不渲染教师操作、教师成绩或教师内部字段。
- 成绩页只能显示任务对象已有的 `score` 和状态；空分数必须显示待反馈边界，不能将完成状态推断成成绩通过。
- 兼容路径继续可用；本轮不删除现有导航和 API 端点。
- Mock 路由通过只证明前端映射与当前隔离夹具一致，不能替代真实 Moodle 多课程、真实角色、正式 API 或 T4/T5 人工验收。

### 113.4 失败分类、重测和回滚规则

第一次定向 Playwright 执行因 shell 将 `|` 解释为管道，没有产生测试结果，不计入证据；随后拆分为无管道命令，在允许回环监听的隔离环境中以唯一 run_id 重跑并通过。初始结果后发现成绩页使用固定 `current` 作为跳转上下文，按修复后重测规则删除该占位值，并以 attempt 2 从 T0 重跑至 T5；受限沙箱直接启动 Vite 时 `listen EPERM`，分类为 `BLOCKED_TEST_INFRA`；授权环境的路由专项和完整 Mock 结果才是本轮浏览器权威结果。标准 a11y/smoke 中连接未启动的 8081 只记录为预览错误态边界。

若修改路由、权限守卫、`CoursePage`、`GradesPage`、页面参数解析或路由测试夹具，必须从 T0 重新审查并重跑 T1-T6；若修改 API/会话/Store，则按第 27 节从最早受影响层重跑。若只恢复真实课程资料、Moodle 角色、正式 API、Docker/HTTPS、恢复环境或 Workflow，则从 BUILD-000 T0 重跑受影响的正式门禁。回滚只能移除本轮规范路由和成绩入口改动及其测试，不得删除旧兼容路径、课程数据、成绩记录或降低越权断言。

### 113.5 计划进一步审查结论

本轮关闭本地 finding `BUILD010-ROUTE-001`：计划第 5 节的学生/教师规范路由已与现有前端页面和角色守卫对齐，并新增真实可观察的成绩入口；保留的 `courseId` 数据边界明确写入代码和证据。T0-T5 的本地结果达到计划要求，但 T3 为 `NOT_APPLICABLE`、T4/T5 为观察性结果，不能关闭 BUILD-010 的正式门禁。

外部前置检查仍显示：课程数据缺少 manifest 要求的 20 个 PDF，`deploy/.env` 不存在因而无法进行真实 Xingchen Workflow 预检，正式提交材料仍缺 3 项；这些条件继续记录为阻断，不创建占位文件。BUILD-000 继续 `BLOCKED_INPUT`，BUILD-010 继续 `IMPLEMENTED_PENDING_GATE`，BUILD-100 继续 `IMPLEMENTED_PENDING_GATE`，最终发布继续 `blocked`。

## 114. 2026-07-26 测试方案可执行性终审与 BUILD-030 课程列表缺口登记

### 114.1 审查范围和运行身份

本轮运行号为 `TEST-PLAN-AUDIT-20260726-25`，目标是独立复核第 27 节 T0-T6 协议、当前命令库存、证据引用、账本状态以及 BUILD-030 的 COURSE-001～008 实现边界。审查范围包括第 5、18、22、23、27 节，`frontend/src/App.tsx`、`frontend/src/api/client.ts`、`frontend/src/types.ts`、`agent-adapter/app/main.py`、`PROJECT_PROGRESS.yaml`、`PROJECT_STATUS.md` 和现有 `acceptance/frontend/` 证据目录。

本轮不读取或输出 `.env.test.local` 的任何值，不修改课程 manifest、PDF hash/page_count、生产凭据、真实 Workflow 或部署路由。所有本地命令只检查代码、测试、计划和脱敏账本。

### 114.2 机器复核结果

| 层级 | 执行内容 | 实际结果 | 判定 |
|---|---|---|---|
| T0 | 对照第 27 节复核状态边界、证据身份、重测起点和 BUILD-030 COURSE-001～008 | T0-T6 协议完整；发现 `/courses` 仍映射单课程详情页，课程列表契约未实现 | `PASS_WITH_OPEN_FINDING` |
| T1 | `python3 scripts/test_api_contract.py`、`python3 scripts/test_ui_contract.py`、`python3 scripts/test_frontend_hardening.py`、`python3 -m compileall -q agent-adapter scripts`、`bash -n scripts/*.sh`、`git diff --check`；`cd frontend && npm run lint`、`npm run typecheck`、`npm run test:all -- --run`、`npm run build` | API `93 routes`、UI 契约、硬化、Python、Shell、diff、前端 lint/typecheck、Vitest `39/39` 和生产构建 `1694 modules` 全部通过 | `PASS` |
| T2 | `python3 -m unittest -q scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress scripts.test_verify_course_data scripts.test_spark_assistant_contract` | `19/19` 通过 | `PASS` |
| T3 | `python3 scripts/validate_project_progress.py`，交叉检查标准证据、唯一 ID、工作树计数和脱敏 | `metadata=11`、`blockers=22`、`evidence_refs=166`、`redaction_scan=PASS`；最新路由证据统一为 `...-24` | `PASS` |
| T4 | 检查 BUILD-030 计划要求与前端路由/API实现的对应关系 | 当前仅有课程详情/单课程预览映射；课程列表、`GET /api/courses`、多课程切换和 COURSE-001～008 自动化闭环未执行 | `NOT_IMPLEMENTED` |
| T5 | 检查真实课程资料、真实 Moodle 三角色、正式 API、六视口和人工辅助技术前置条件 | 20 个 PDF、正式角色/API、正式 axe、六视口人工证据仍缺失 | `BLOCKED_INPUT` |
| T6 | 核对计划、账本、状态文档和证据路径的一致性 | 计划测试协议有效；已修正陈旧的 `...-23` 路由证据引用；课程列表缺口登记为开放 P1 | `REVIEW_REQUIRED` |

一次直接执行 `python3 scripts/test_validate_project_progress.py` 的命令因 `scripts` 包导入路径失败，分类为 `PLAN_COMMAND_FAILURE`，没有计入回归失败；改用第 27.2 节规定的模块入口后 `8/8` 和 `2/2` 两组校验器回归均通过。该分类和规范入口已写入本计划，后续权威命令不再使用直接脚本入口。

### 114.3 计划缺口和验收条件

在本次第 114 节历史审查时，`BUILD030-COURSE-LIST-001` 保持开放：当时 `/courses` 仍进入 `CoursePage`，前端 `PlatformData` 没有课程摘要集合，客户端没有 `loadCourses()`，Adapter 没有 `GET /api/courses`。该历史缺口已由第 115 节的 `BUILD-030-COURSE-LIST-20260726-26` 构筑后复审重新验证；当前只关闭本地实现缺口，不关闭正式多课程门禁。

关闭该 finding 前必须完成并复审以下条件：

- 新增 `CourseSummary` 和 `PlatformData.courses`，DTO 归一化不得接受未声明字段或伪造课程。
- Adapter 提供受会话、角色和课程范围控制的 `GET /api/courses`；当前只有单课程夹具时必须明确返回单课程限制，不能伪造第二门课程。
- `/courses` 改为课程列表页；课程卡片显示 API 返回的稳定 ID、名称、教师、班级/状态和进度，并能进入 `/courses/:courseId`。
- COURSE-001～008 覆盖未登录、空列表、稳定排序、未授权课程、分页/排序边界、课程切换隔离和刷新恢复；API、组件和 Mock Playwright 证据必须共享唯一新 `run_id`。
- 课程列表实现完成后从 T0 重新执行 T1-T6；真实 Moodle 多课程、正式 API、课程 PDF、角色和人工证据仍只能按 `OBSERVED_PASS`/`BLOCKED_INPUT` 边界记录，不能由本地单课程夹具关闭正式 BUILD-030。

### 114.4 终审结论和重测规则

本轮历史审查确认测试方案已具备可执行的 T0-T6 顺序、状态语义、命令入口、证据身份和失败分类；`PLAN-CMD-001` 关闭。账本和证据引用一致性通过；当时的 `BUILD030-COURSE-LIST-001` 已由第 115 节复审更新为本地实现待正式门禁，课程 PDF、正式 Moodle 三角色/API、Spark 错误鉴权、正式 Workflow、Docker/HTTPS、恢复、正式辅助技术和提交材料继续开放。

任何修改第 27 节命令、进度校验器、标准证据结构、课程列表路由/API/DTO/Mock 夹具，或恢复课程资料/正式角色输入，都必须从最早受影响的 T0 开始，重跑后续 T1-T6，并用新唯一 `run_id` 替换旧权威结果。当前状态保持：`BUILD-000 = BLOCKED_INPUT`、`BUILD-030 = PARTIAL_IMPLEMENTATION_PENDING_GATE`、`BUILD-010 = IMPLEMENTED_PENDING_GATE`、最终发布 `blocked`。

## 115. 2026-07-26 BUILD-030 课程列表构筑后 T0-T6 复审

### 115.1 构筑范围、运行身份和代码审查

本轮运行号为 `BUILD-030-COURSE-LIST-20260726-26`，attempt `1`，并替代 BUILD-030 之前的课程/图谱本地标准证据。构筑范围是“我的课程”列表闭环：新增 `GET /api/courses` 和 `GET /api/courses/{course_id}`，增加 `CourseSummary`/`CourseList` DTO、`PlatformData.courses`、`loadCourses()`、`/courses` 列表页、课程卡片、加载/空/错误状态、进入课程按钮以及课程详情越权保护；同时保留已有学习图谱和先修路径能力。

代码审查确认：

- 课程列表和详情接口均经过会话、角色和课程范围控制；未登录返回 `401`，未授权/未知课程不泄露其他课程内容。
- `page`、`page_size` 和 `sort` 使用显式白名单和边界校验，客户端只发送归一化后的合法参数。
- 当前本地数据边界只有一门已配置课程；实现和证据明确标注该限制，不伪造第二门课程或虚构多课程成绩/进度。
- `/courses` 的空态、错误态和重试路径不显示成功数据；课程详情路由在课程 ID 不属于当前会话时回到列表页。
- 本轮未修改课程 manifest、graph-baseline.json、PDF hash/page_count、Spark 凭据、生产部署或 `.env.test.local` 内容；证据不记录 API Key、API Secret、Token、Cookie、Authorization、签名 URL、完整问答或真实学生数据。

### 115.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查课程列表 API、DTO、会话/课程范围、分页排序、加载/空/错误态、课程进入、越权隔离、单课程数据边界、敏感值和回滚 | 范围闭合；单一已配置课程边界显式记录；不生成第二门课程 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；`python3 scripts/test_frontend_hardening.py`；`python3 scripts/test_ui_contract.py`；`cd frontend && npm run lint`；`npm run typecheck`；`npm run build` | Python、Shell、diff、硬化、UI 契约、lint、typecheck 通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和领域规则 | `python3 scripts/test_course_list_api.py`；`cd frontend && npm run test:all -- --run` | `COURSE_LIST_API_OK cases=8`；Vitest `40/40`；覆盖未登录、空列表、排序/分页边界、未授权课程和单课程边界 | `PASS` |
| T3 API 和契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py` | 本地 OpenAPI `94 paths`；API 契约 `95 routes`；仅证明本地隔离 Adapter，不替代正式 Moodle API | `OBSERVED_PASS` |
| T4 浏览器流程 | `cd frontend && npm run test:e2e:mock -- --workers=1`；核对课程列表正常/空/错误、进入授权课程和未知课程回退 | Mock Playwright `32/32`；课程列表专项正常、空、错误和越权路径通过 | `OBSERVED_PASS` |
| T5 质量和外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；审查真实多课程 Moodle、20 个 PDF、正式图谱来源、六视口和人工辅助技术 | 自定义 a11y `3/3`、axe `4/4`（Chrome 147 对比度挂起规则排除）、标准 smoke `2/2`；完整脚本在课程资料基线以退出码 `2` fail-fast；正式数据、角色和人工门禁缺失 | `OBSERVED_PASS` / `BLOCKED_INPUT` |
| T6 证据、账本和门禁 | 核对唯一 run_id、六类标准证据共享身份、退出码摘要、脱敏、计划引用、finding 状态和回滚边界 | `BUILD-030-COURSE-LIST-20260726-26` 已写入六类标准证据和专项证据；本地 finding 关闭，正式门禁保持开放 | `REVIEW_REQUIRED` |

专项证据为 `acceptance/frontend/BUILD-030/course-list-revalidation-20260726-26.txt`。

### 115.3 逐项验收条件

- 未登录访问课程列表必须返回 `401`；当前会话只能看到已授权课程，未知或未授权详情不得返回课程内容。
- `GET /api/courses` 必须返回稳定的 `items/page/page_size/total` 包络，并对 `sort`、`page` 和 `page_size` 做白名单和范围校验；错误参数返回 `422`。
- `/courses` 必须展示 API 返回的课程名称、教师、班级/状态、最后访问时间和进度；加载、空列表和失败状态必须清晰可见，并提供可控重试。
- 当前单课程夹具必须明确标注“单一已配置课程边界”，不得通过前端预览数据、静态数组或测试替身伪造第二门课程。
- 进入课程必须使用 API 返回的稳定课程 ID；详情页刷新、未知课程和跨课程访问不得沿用上一门课程的章节、任务、成绩、图谱或 Agent 上下文。
- 本地 Mock、a11y、axe、smoke、OpenAPI 和 `COURSE_LIST_API_OK` 只能记为本地观察性/隔离通过；不能替代真实 Moodle 多课程、真实三角色、课程 PDF、正式图谱来源、正式 API、正式辅助技术或人工六视口验收。

### 115.4 失败分类、重测和回滚规则

本轮第一次完整 Mock 命令在受限沙箱中因禁止回环监听，在测试开始前等待 webServer 超时；该结果分类为 `BLOCKED_TEST_INFRA`，没有进入产品断言。随后在允许本地回环监听的隔离环境按同一 run_id 重跑，Mock `32/32` 通过。标准 a11y 的 `8081 ECONNREFUSED` 仅表示预览配置未启动 Adapter 的错误态边界；axe 扫描继续按既有规则记录 Chrome 147 的 `color-contrast`/`color-contrast-enhanced` 挂起限制，不把排除后的 `4/4` 升格为完整对比度通过。

若修改课程列表 API、课程范围校验、DTO 归一化、`PlatformData`、`loadCourses()`、`CoursesPage`、课程详情隔离、相关 CSS、Mock 夹具或课程列表断言，必须从 T0 重新审查，并至少重跑 T1-T6；失败必须保留新唯一 run_id、退出码、失败分类和修复后的权威结果。若只恢复真实 Moodle 多课程、课程 PDF、正式图谱、正式 API、HTTPS、容器、恢复环境或人工辅助技术，则从 BUILD-000 T0 重跑受影响正式门禁，不得以本地单课程结果替代。

回滚只能恢复本轮课程列表 API/DTO/页面/隔离保护/测试和样式文件；不得删除课程范围校验、修改 manifest 或 graph-baseline.json、生成占位 PDF、屏蔽 COURSE-001～008 断言或保留“通过但实现不存在”的证据。回滚后必须同步更新 BUILD-030 六类标准证据的 run_id、T0-T6 状态和 finding 状态。

### 115.5 计划进一步审查结论

本轮确认第 27 节 T0-T6 协议可以约束课程列表从 API 合同、会话范围、DTO、前端状态、课程进入、错误态到浏览器质量门禁的完整复审。`BUILD030-COURSE-LIST-001` 的“功能未实现” finding 已关闭，含义仅是本地课程列表代码和单一已配置课程边界已经有实现与测试证据；真实多课程数据、Moodle 三角色、课程 PDF、正式图谱来源、六视口人工辅助技术和最终发布门禁仍开放。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`BUILD-030` 继续 `PARTIAL_IMPLEMENTATION_PENDING_GATE`，`BUILD-000` 继续 `BLOCKED_INPUT`，最终发布继续 `blocked`；本轮不改变 `SPARK-AUTH-FAIL-001` 的 P0 `FAIL`，也不把本地 API/Mock/axe/smoke 结果升级为正式 PASS。

## 116. 2026-07-26 BUILD-030 课程中心排序与分页构筑后 T0-T6 复审

### 116.1 构筑范围、运行身份和代码审查

本轮运行号为 `BUILD-030-COURSE-NAV-20260726-27`，attempt `1`，supersede `BUILD-030-COURSE-LIST-20260726-26` 的课程中心标准证据。本轮继续围绕“我的课程”推进：新增类型化 `CourseSort`，为 `/courses` 增加服务端驱动排序选择、`page/page_size` 请求参数、分页页码显示、上一页/下一页控件和跨页结果清理；保留课程列表 API、课程详情越权保护、空态、错误态和重试。

代码审查确认：

- 排序只能使用 `last_accessed`、`progress`、`name` 和 `id` 白名单；选择排序会将页码重置为第 1 页，并重新请求 Adapter。
- 页面分页使用服务端返回的 `total`、`page` 和固定 `page_size=6` 计算页数，不在浏览器端拼接或猜测正式课程数据。
- 翻页后课程卡片完全由当前响应替换，不能把上一页课程混入当前页；按钮有可访问名称、禁用边界和移动端布局约束。
- 为验证分页 UI，Mock 浏览器使用 7 条显式合成课程摘要响应；该夹具仅证明页面契约，不进入课程 manifest、数据库或正式证据，不代表本地已有第二门真实课程。
- 本轮没有读取或修改 `.env.test.local`，没有修改课程 PDF、manifest、graph-baseline、Spark 凭据、生产部署或真实 Moodle 数据。

### 116.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查 `CourseSort`、排序白名单、服务端 query、页码状态、跨页替换、按钮可访问性、合成夹具隔离和回滚范围 | 范围闭合；正式 API 数据仍只有一门已配置课程，未将合成第二页当作正式多课程 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；硬化/UI 契约；`npm run lint`；`npm run typecheck`；`npm run build` | 全部通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和领域规则 | `python3 scripts/test_course_list_api.py`；`cd frontend && npm run test:all -- --run` | `COURSE_LIST_API_OK cases=8`；Vitest `40/40`；客户端排序 query、课程 DTO 和既有课程边界回归通过 | `PASS` |
| T3 API 和契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py` | 本地 OpenAPI `94 paths`；API `95 routes`；排序/分页使用既有本地契约，不能替代正式 Moodle API | `OBSERVED_PASS` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1 --grep "course list uses server pagination"`；完整 `npm run test:e2e:mock -- --workers=1` | 分页专项 `1/1`；完整 Mock `33/33`；排序请求、跨页隔离、空态、错误态、课程进入和越权流程通过 | `OBSERVED_PASS` |
| T5 质量和外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；审查真实多课程和人工辅助技术 | a11y `3/3`、axe `4/4`（Chrome 147 对比度挂起规则排除）、smoke `2/2`；完整脚本在缺失 PDF 基线以退出码 `2` fail-fast；真实输入缺失 | `OBSERVED_PASS` / `BLOCKED_INPUT` |
| T6 证据、账本和门禁 | 核对唯一 run_id、六类标准证据、专项证据、合成夹具边界、退出码、脱敏和回滚 | `BUILD-030-COURSE-NAV-20260726-27` 已同步标准证据和专项证据；正式 BUILD 仍开放 | `REVIEW_REQUIRED` |

专项证据为 `acceptance/frontend/BUILD-030/course-navigation-revalidation-20260726-27.txt`。

### 116.3 逐项验收条件

- 选择“最近访问、学习进度、课程名称、课程编号”时，客户端必须只发送对应白名单值，并将页码恢复为 1；不得用前端排序替代真实模式的服务端列表排序。
- 服务端返回 `total=7,page=1,page_size=6` 时，页面必须显示 6 张课程卡片和“第 1 / 2 页”；进入第 2 页后只能显示剩余 1 张，上一页卡片不得残留。
- 首页按钮在第 1 页禁用，末页按钮在第 2 页禁用；按钮必须有可访问名称，390px 视口不得造成横向溢出。
- 排序或翻页请求失败时必须保留错误状态和可重试入口，不得显示上一页作为当前成功结果；返回空列表时显示明确空态。
- 合成分页夹具只能用于 UI 分页契约，不能写入 `course-data`、SQLite 正式课程目录、manifest、PROJECT_PROGRESS 的真实课程计数，也不能关闭真实多课程门禁。
- 本地 API、Mock、a11y、axe、smoke 和合成分页结果只能记为观察性/隔离通过；真实 Moodle 多课程、三角色、20 个 PDF、正式 API/图谱来源、六视口人工验收仍需独立门禁。

### 116.4 失败分类、重测和回滚规则

本轮课程分页专项和完整 Mock 均在允许回环监听的隔离环境退出码 0；此前受限沙箱的回环监听超时继续作为 `BLOCKED_TEST_INFRA` 历史分类，不计入产品失败。a11y/标准 smoke 的 `8081 ECONNREFUSED` 是未启动 Adapter 的预览错误态边界；axe 仍显式排除 Chrome 147 会挂起的两条对比度规则，不把 `4/4` 记作完整正式对比度通过。完整 `run_local_acceptance.sh` 因缺失 `chapter-1-1.1-.pdf` 以退出码 `2` fail-closed，归类为 `BLOCKED_INPUT`。

若修改课程列表 API、`CourseSort`、排序 query、分页状态、课程卡片、CSS、Mock 路由或浏览器断言，必须从 T0 重新审查并重跑 T1-T6；若只恢复真实多课程、课程 PDF、Moodle、正式 API、HTTPS、恢复环境或人工辅助技术，则从 BUILD-000 T0 重跑受影响正式门禁。任何失败都必须保留新 run_id、退出码、失败分类和权威重测证据。

回滚仅限本轮排序/分页控件、`CourseSort` 类型、页面状态、测试和合成夹具；不得删除课程列表会话/课程范围校验、修改 manifest/hash/page_count、生成占位 PDF、把合成课程写入正式目录或保留“通过但实现已删除”的证据。

### 116.5 计划进一步审查结论

本轮确认第 27 节 T0-T6 协议能够覆盖课程中心从排序白名单、服务端分页、状态替换、可访问控件到证据隔离的完整复审。课程中心本地交互增量达到观察性通过，`BUILD-030` 仍为 `PARTIAL_IMPLEMENTATION_PENDING_GATE`；`BUILD-000` 仍为 `BLOCKED_INPUT`，最终发布仍为 `blocked`。

本轮没有把合成分页夹具当作真实第二门课程，也没有改变 `BUILD030-COURSE-LIST-001` 的正式多课程门禁、`DATA-INPUT-001`、`FRONTEND-A11Y-001`、`SPARK-AUTH-FAIL-001` 或其他外部阻断项。

## 117. 2026-07-26 BUILD-030 canonical 课程路由范围守卫构筑后 T0-T6 复审

### 117.1 构筑范围、运行身份和代码审查

本轮运行号为 `BUILD-030-ROUTE-SCOPE-20260726-28`，attempt `1`，supersede `BUILD-030-COURSE-NAV-20260726-27`。本轮修复 canonical 课程子路由的范围保护：将学生 `/courses/:courseId/*` 和教师 `/teacher/courses/:courseId/*` 子路由归并到统一 `CourseScope` 守卫，验证当前 session/course list 授权后才渲染子页面；未知或未授权课程在页面数据加载前重定向，学生访问教师课程路由仍回到工作台。

代码审查确认：

- `CourseScope` 同时检查 route `courseId` 与当前 session 的 `courseId`；预览无 session 时只接受已知课程列表 ID。
- 教师 canonical 路由使用 `staffOnly` 保护，不能因 URL 变化绕过角色边界；旧的非 canonical 工作台入口继续保留既有角色守卫。
- 嵌套路由保留章节、任务、考试、资料、讨论、学习记录、成绩、Agent、教师题库/作业/考试/活动/资料/成绩册等既有路径，不改 API 契约或课程数据。
- 路由专项只验证隔离和重定向，不伪造第二门真实课程；无凭据、Cookie、Authorization、签名 URL 或真实学生数据进入证据。

### 117.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查 `CourseScope`、嵌套路由映射、学生/教师角色、未知 course ID、预览边界和回滚 | 所有 canonical 课程子路由统一先过范围守卫；学生/教师越权不渲染受保护页面 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；UI/硬化；`npm run lint`；`npm run typecheck`；`npm run build` | 全部通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和领域规则 | `npm run test:all -- --run`；`python3 scripts/test_course_list_api.py` | Vitest `40/40`；课程 API `8/8`；既有客户端、课程列表和状态机回归通过 | `PASS` |
| T3 API 和契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py` | OpenAPI `94 paths`；API `95 routes`；本轮无 API schema 变化，仍不替代正式 Moodle API | `OBSERVED_PASS` |
| T4 浏览器流程 | 课程范围专项 `--grep`；完整 `npm run test:e2e:mock -- --workers=1` | 范围专项 `4/4`；完整 Mock `35/35`；学生 7 类子路由和教师成绩册越权回退通过 | `OBSERVED_PASS` |
| T5 质量和外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；审查真实 Moodle 三角色/多课程 | a11y `3/3`、axe `4/4`（Chrome 147 对比度规则排除）、smoke `2/2`；正式角色和多课程输入缺失 | `OBSERVED_PASS` / `BLOCKED_INPUT` |
| T6 证据、账本和门禁 | 核对唯一 run_id、六类标准证据、专项证据、脱敏和当前 gate | `BUILD-030-ROUTE-SCOPE-20260726-28` 已归档；BUILD-030 继续待正式门禁 | `REVIEW_REQUIRED` |

专项证据为 `acceptance/frontend/BUILD-030/course-route-scope-revalidation-20260726-28.txt`。

### 117.3 逐项验收条件

- 学生访问 `/courses/999/assignments`、`/exams`、`/resources`、`/discussions`、`/progress`、`/grades` 和 `/agent` 时，必须在子页面数据渲染前回到 `/courses`，不得显示当前课程内容。
- 教师访问 `/teacher/courses/999/gradebook` 等 canonical 子路由时，必须回到课程列表，不能只依赖页面内部的空态或隐藏按钮来实现授权。
- 有效的当前课程 ID 必须保留所有 canonical 页面入口；教师访问学生路径、学生访问教师路径和未知 role 均需符合既有角色守卫。
- 课程 ID、session、课程列表或加载状态变化时，迟到的子页面响应不得覆盖新的 route scope；任何真实课程 API 仍需由 Adapter 依据会话裁决。
- 本地 Mock 路由通过不能替代真实 Moodle course capability、三角色、正式 API/OpenAPI、课程 PDF、多课程切换、人工键盘/屏幕阅读器和六视口验收。

### 117.4 失败分类、重测和回滚规则

本轮课程范围专项 `4/4` 和完整 Mock `35/35` 在允许回环监听的隔离环境通过。若嵌套路由匹配、`CourseScope`、角色守卫、课程列表 DTO、Mock 路由或 route 断言发生变化，必须从 T0 重新审查并至少重跑 T1-T6；仅重跑一个页面不能关闭批次。受限沙箱回环监听失败、a11y/smoke 的 `8081 ECONNREFUSED` 和 Chrome 147 axe 对比度挂起继续按既有基础设施/依赖分类记录。

回滚只恢复 `CourseScope`、canonical 嵌套路由和本轮隔离测试；不得删除课程 ID/角色守卫、把无授权路由重新指向数据页面、修改 manifest/hash/page_count 或保留与实现不一致的绿色证据。真实 Moodle 输入恢复后必须从 BUILD-000 T0 重跑正式门禁。

### 117.5 计划进一步审查结论

本轮确认第 27 节 T0-T6 协议已覆盖课程路由从 URL 参数、session/course scope、角色边界、子页面渲染顺序到浏览器回归的完整审查。`BUILD-030` 的本地路由隔离增量为观察性通过，但正式多课程和真实 Moodle 门禁仍开放；`BUILD-000 = BLOCKED_INPUT`，最终发布继续 `blocked`。

## 118. 2026-07-26 测试方案写入计划后的当前终审

### 118.1 审查目标和当前基线

本轮把测试方案、构筑后审查、验收条件和失败重测规则统一核对为当前执行基线。审查范围包括第 10 节测试范围、第 17 节构建总则、第 18 节批次门禁、第 27 节 T0-T6 协议、第 101 节历史计划审查，以及最新的 BUILD-030 课程列表、排序分页和 canonical 路由范围守卫证据。

当前权威产品构筑为 `BUILD-030-ROUTE-SCOPE-20260726-28`。本轮计划审查运行号为 `PLAN-TEST-AUDIT-20260726-29`，机器证据为 `acceptance/frontend/BUILD-000/plan-test-audit-20260726-29.txt`。本轮只审查文档、账本、测试入口和既有证据，不读取或记录密钥，不实现新功能，不改变生产路由。

### 118.2 每次构筑后的执行版测试方案

每次构筑完成后必须按 T0 到 T6 顺序执行。某层失败、输入发生变化或代码/测试/证据范围扩大时，必须从最早受影响的层重新执行，并补跑后续层；单个局部测试通过不能关闭整个构筑批次。

| 层级 | 必须执行和审查 | 通过条件 | 当前终审结果 |
|---|---|---|---|
| T0 范围与代码审查 | 冻结 `git status`、HEAD、构筑范围、数据权威来源、权限矩阵、API diff、状态迁移、敏感值和回滚边界；区分 Mock、local-isolated Adapter 与正式 Moodle/Workflow | 无未处理 P0/P1；不把预览数据、合成课程或历史结果写成正式数据 | `PASS` |
| T1 静态与生产构筑 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；`python3 scripts/test_ui_contract.py`；`python3 scripts/test_frontend_hardening.py`；`python3 scripts/test_frontend_container_contract.py`；前端 `lint`、`typecheck`、`build` | 所有适用命令退出码为 0；生产构建可复现；命令缺失记为 `NOT_IMPLEMENTED` | `PASS` |
| T2 单元、领域和组件 | 先运行变更模块定向测试，再运行 `cd frontend && npm run test:all -- --run`；覆盖权限、状态机、错误态、幂等、版本冲突和路由边界 | 所有适用断言通过；禁止用 skipped、注释断言或假数据替代失败 | `PASS` |
| T3 API、OpenAPI 和持久化 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；按第 21.5 节执行未登录、错误鉴权、越权、边界、幂等、状态回读、审计和清理 | 本地契约完整只能记 `OBSERVED_PASS`；缺正式 Moodle API、角色夹具或真实数据时记 `BLOCKED_INPUT` | `OBSERVED_PASS` |
| T4 浏览器流程 | 定向 Mock Playwright、完整 Mock 回归，再执行真实 student/teacher/admin 流程；覆盖刷新、重复点击、失败恢复、会话过期和六视口 | Mock 与真实结果分开；真实适用流程缺失不得关闭批次 | `OBSERVED_PASS` |
| T5 质量、安全、性能和恢复 | `test:a11y`、`test:axe`、标准 smoke、键盘/屏幕阅读器、六视口、性能、上游超时/断流、服务重启、备份恢复和完整本地验收 | 本地自定义结果不能替代正式辅助技术、完整 axe、HTTPS、恢复或真实 Workflow；输入缺失即阻断 | `OBSERVED_PASS / BLOCKED_INPUT` |
| T6 证据和门禁复审 | 核对唯一 `run_id`、`attempt`、权威结果标记、T0-T6、退出码、证据路径、脱敏、账本、回滚和开放 finding | 所有必测项为正式 `PASS` 才能关闭 BUILD；否则保持 `REVIEW_REQUIRED` 或阻断状态 | `REVIEW_REQUIRED` |

### 118.3 当前机器复测结果

本轮复测结果如下，均已写入上述脱敏证据：

- 账本/配置回归：`19/19`；`PROJECT_PROGRESS_VALIDATION_OK metadata=11 blockers=22 evidence_refs=172 redaction_scan=PASS`。
- API/UI/安全/容器静态契约：API `95 routes`、UI 契约通过、前端硬化通过、容器契约 `4/4`。
- 工程门禁：Python 编译、Shell 语法、`git diff --check`、前端 lint、typecheck 均通过。
- 前端回归：Vitest `40/40`，生产构建 `1694 modules transformed`。
- 最新 BUILD-030 浏览器证据：课程范围专项 `4/4`，Mock Playwright `35/35`；该结果为 `OBSERVED_PASS`。
- 最新本地质量证据：自定义 a11y `3/3`、axe 非对比度规则 `4/4`、标准 smoke `2/2`；Chrome 147 的 `color-contrast` 和 `color-contrast-enhanced` 仍是显式 `BLOCKED_DEPENDENCY`，不能写成完整 axe 通过。
- 完整本地验收：`bash scripts/run_local_acceptance.sh` 以退出码 `2` 返回 `COURSE_DATA_BLOCKED_INPUT`，首个缺失文件为 `chapter-1-1.1-.pdf`。该脚本 fail-fast，未继续虚构知识库、来源或 Workflow 结果。

### 118.4 进一步审查发现和修正

1. 第 27 节的 T0-T6 顺序、适用性、退出码、证据格式和失败后重测规则可以直接执行；本轮实际命令均存在并能获得可分类结果。
2. 最新 BUILD-030 证据与课程路由范围实现一致：课程列表排序/分页的合成数据只用于 UI 契约，canonical 路由守卫只证明本地隔离，不代表正式多课程。
3. 项目状态顶部摘要已更新为当前 `40/40`、`35/35`、`3/3`、非对比度 axe `4/4` 和最新构筑号；历史章节中的旧计数保留为历史记录，不得作为当前结果引用。
4. 账本校验通过只说明运行身份、证据路径、工作树快照和脱敏边界一致，不会自动关闭课程资料、真实 Moodle、正式 API、Spark 鉴权、完整可访问性、Docker/HTTPS、恢复或人工验收门禁。

### 118.5 验收条件、失败分类和重测触发

- 只有 T0-T6 所有适用项为正式 `PASS`，且真实课程资料、真实三角色、正式 API/OpenAPI、真实 Workflow/知识库、完整辅助技术、HTTPS、容器运行、恢复演练和提交材料均有证据，才能把 BUILD 或最终发布标记为 `PASS`。
- Mock、合成分页、local-isolated Adapter、本地 OpenAPI、a11y、受限 axe 和标准 smoke 的绿色结果最多为 `OBSERVED_PASS`；Chrome 147 对比度规则挂起为 `BLOCKED_DEPENDENCY`；缺失课程 PDF 为 `BLOCKED_INPUT`；安全鉴权异常继续按 P0 `FAIL` 保留。
- 修改计划命令、测试配置、进度校验器、标准证据、课程列表/路由/权限/API/DTO、课程数据或正式环境输入时，必须生成新的唯一 `run_id`，从最早受影响的 T0 重跑并更新六类证据和账本。
- 修复后不得覆盖原始失败输出，不得删除旧证据，不得生成占位 PDF、第二门正式课程、伪造 manifest hash/page_count 或以历史运行号冒充当前权威结果。
- 当前结论：计划测试方案已写入并通过机器可执行性审查；`BUILD-000 = BLOCKED_INPUT`，`BUILD-030 = PARTIAL_IMPLEMENTATION_PENDING_GATE`，最终发布继续 `blocked`。

本轮计划终审结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。

## 119. 2026-07-26 进度账本最新审查身份同步

本轮只维护本地配置和证据索引，不修改产品代码。发现计划第 118 节的计划终审运行号与 `PROJECT_PROGRESS.yaml` 中 `test_plan.current_review_run_id` 的语义混用：账本原先仍把权威产品构筑 `BUILD-030-ROUTE-SCOPE-20260726-28` 作为当前计划审查运行号。

已修正为：

- 计划审查运行号：`PLAN-TEST-AUDIT-20260726-29`。
- 权威产品构筑运行号：`BUILD-030-ROUTE-SCOPE-20260726-28`。
- `PROJECT_PROGRESS.yaml` 新增同一运行号的 `test_runs` 条目和 `latest_plan_audit` 摘要。
- 证据引用增加至 `174`，脱敏扫描和重复 ID 校验继续通过。

### 119.1 账本修订验收条件

- `current_review_run_id`、`authoritative_review_run_id` 和 `authoritative_product_build_run_id` 必须表达不同层级且可追溯到证据。
- `test_runs[].id` 必须唯一，命令、结果、开放门禁和证据文件必须使用同一 `PLAN-TEST-AUDIT-20260726-29`。
- 账本绿色只表示配置、证据身份和脱敏边界一致，不能关闭 `BUILD-000`、真实课程资料、正式 Moodle、Workflow、完整 axe、Docker/HTTPS、恢复或人工验收门禁。

### 119.2 本轮结果

`python3 scripts/validate_project_progress.py` 返回 `PROJECT_PROGRESS_VALIDATION_OK gate=BUILD-000 metadata=11 blockers=22 evidence_refs=174 redaction_scan=PASS`；账本回归 `19/19`，`git diff --check` 通过。该修订结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`，最终发布状态保持 `blocked`。

## 120. 2026-07-26 BUILD-030 只读课程数据范围构筑后 T0-T6 复审

### 120.1 构筑范围、运行身份和代码审查

本轮运行号为 `BUILD-030-COURSE-SCOPE-20260726-30`，attempt `1`，supersede `BUILD-030-ROUTE-SCOPE-20260726-28`。本轮针对未来多课程场景补齐只读课程数据边界：`CourseStore` 的章节、课程摘要、知识点、搜索、先修路径、章节资源、资源详情和教师资源查询均接收 `course_id` 并增加课程范围过滤；Adapter 将 `identity.course_id` 传播到 session、课程详情、图谱、路径、资源、教师资源、Agent/resource context 和学习推荐读取链路。

本轮不把写入链路一并宣称完成。作业、成绩、活动等写入仍需单独构筑和多课程审查；第二课程只存在于明确隔离的 SQLite 测试夹具，不进入 manifest、正式数据库或正式课程验收数据。

代码审查确认：

- 所有本批次只读 SQL 查询均有显式 `course_id` 范围，课程 1/2 的章节、节点、路径、资源和课程摘要不会互相泄漏。
- session、Agent graph/resource context 和推荐读取使用当前身份的课程范围，不能因 node/resource/chapter ID 跨课程读取。
- 课程列表、canonical 路由范围、排序分页、空态、错误态和重试回归保持覆盖；本轮不修改课程 manifest、graph-baseline、PDF hash/page_count、Spark 凭据、生产部署或 `.env.test.local`。
- 证据不记录 API Key、API Secret、Token、Cookie、Authorization、签名 URL、完整问答或真实学生数据。

专项证据为 `acceptance/frontend/BUILD-030/course-scope-revalidation-20260726-30.txt`；六类标准证据共享同一运行号：`acceptance/frontend/BUILD-030/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md`、`rollback.md`。

### 120.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查 `CourseStore` 全部只读查询、`identity.course_id` 传播、SQL 课程过滤、Agent/resource context、隔离夹具、写入链路边界、敏感值和回滚 | 只读范围闭合；第二课程仅在 SQLite 夹具；写入链路未被误报为完成 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；UI/硬化/容器契约；`npm run lint`；`npm run typecheck`；`npm run build` | 全部通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和领域规则 | `python3 scripts/test_course_store.py`；`python3 scripts/test_course_list_api.py`；`python3 scripts/test_adapter_runtime.py`；`cd frontend && npm run test:all -- --run` | CourseStore `11/11`；课程 API `8/8`；Adapter `12/12`；Vitest `40/40` | `PASS` |
| T3 API 和契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py` | OpenAPI `94 paths`；API 契约 `95 routes`；仅证明本地 Adapter，不替代正式 Moodle API | `OBSERVED_PASS` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1 --grep "course list uses server pagination"`；完整 `npm run test:e2e:mock -- --workers=1`；核对课程范围、分页替换、空态、错误态和 canonical 路由 | 分页专项 `1/1`；完整 Mock `35/35`；课程范围和跨页结果无串课 | `OBSERVED_PASS` |
| T5 质量和外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；审查真实 Moodle 多课程、正式角色、PDF、人工辅助技术 | a11y `3/3`、受限 axe `4/4`、smoke `2/2`；完整验收退出码 `2`，缺失 `chapter-1-1.1-.pdf`；正式外部输入缺失 | `OBSERVED_PASS / BLOCKED_INPUT` |
| T6 证据、账本和门禁复审 | 核对新唯一 `run_id`、attempt、权威结果、T0-T6、六类证据、专项证据、退出码、脱敏、工作树快照、开放 finding 和回滚边界 | 课程范围证据已归档；最终发布和 BUILD-030 正式门禁保持开放 | `REVIEW_REQUIRED` |

### 120.3 逐项验收条件

- 以课程 2 隔离夹具调用课程 1 的章节、节点、路径、资源和摘要查询时，必须返回课程 1 范围内结果，不得返回课程 2 记录；反向调用同理。
- 同一 node/resource/chapter ID 在不同课程范围下必须由 Adapter 重新裁决；Agent graph/resource context 不能沿用上一课程的上下文。
- 课程列表、canonical 路由、排序分页和本地单课程边界的既有验收必须保持通过；当前正式目录仍只能声明一门已配置课程。
- 本批次通过不等于作业、成绩、活动写入链路的多课程隔离通过；这些链路必须由后续批次建立独立的 T0-T6 证据。
- 本地 SQLite、Mock Playwright、local OpenAPI、a11y、受限 axe 和 smoke 只能记为观察性/隔离结果，不能替代真实 Moodle 多课程、三角色、正式 API、正式图谱来源、课程 PDF、人工六视口或恢复演练。

### 120.4 失败分类、重测和回滚规则

- 课程范围 SQL、`identity.course_id` 传播、Agent/resource context、课程列表/路由 DTO 或 Mock 课程夹具发生变化时，从 T0 重新审查并重跑 T1-T6；不得只重跑一个查询或一个页面。
- 若只修改分页测试按钮稳定性，必须保留原始失败输出，使用新的唯一 `run_id` 重跑分页专项和完整 Mock，并继续执行适用的 T5 质量门禁；本轮前一项 Playwright 点击超时已分类为 `TEST_HARNESS_STABILITY_TIMEOUT`，修复后 `1/1` 和 `35/35` 均通过。
- 受限沙箱无法回环监听分类为 `BLOCKED_TEST_INFRA`；Chrome 147 对比度规则挂起分类为 `BLOCKED_DEPENDENCY`；缺失课程 PDF、正式 Moodle/API/角色或人工输入分类为 `BLOCKED_INPUT`，不得改写成产品 PASS。
- 回滚只能恢复本轮只读 `course_id` 过滤、Adapter 范围传播、隔离夹具和证据；不得删除跨课程泄漏断言、生成占位 PDF、伪造第二门正式课程、修改 manifest/hash/page_count 或暴露密钥。

### 120.5 计划进一步审查结论

本轮确认第 27 节 T0-T6 协议不仅能覆盖前端课程列表和 canonical 路由，也能覆盖 Adapter/Store 的只读数据边界；测试入口、通过条件、失败分类、证据身份和回滚规则均可执行。课程范围本地实现和隔离测试为观察性通过，真实多课程、写入链路、课程资料、正式 Moodle/API、完整 axe、Docker/HTTPS、恢复和人工验收仍开放。

本轮计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`BUILD-000 = BLOCKED_INPUT`，`BUILD-030 = PARTIAL_IMPLEMENTATION_PENDING_GATE`，最终发布继续 `blocked`。

## 121. 2026-07-26 BUILD-030 知识库写入课程范围构筑后 T0-T6 复审

### 121.1 构筑范围、运行身份和代码审查

本轮运行号为 `BUILD-030-COURSE-WRITE-SCOPE-20260726-31`，attempt `1`，supersede `BUILD-030-COURSE-SCOPE-20260726-30`。本轮把前一轮明确未完成的知识库写入链路纳入课程范围审查：`kb_versions`、`kb_files`、`kb_hit_tests`、发布状态、回滚和管理员审计均按 `course_id` 过滤；知识库 API、`validate_sources()`、Mock/real Workflow 发布状态、管理员状态和审计路由均传播 `identity.course_id`。跨课程不存在的版本统一返回 `404`，避免通过状态差异暴露其他课程对象。

新增 `scripts/test_kb_course_scope_api.py`：在临时 SQLite 和临时知识库存储中完成课程 2 的版本创建、Markdown 来源文件上传、三条固定黄金问题、测试、发布和审计查询；随后切换到课程 1，验证版本、文件、命中测试、发布状态、来源 `kb_version_id`、管理员状态和审计记录不可见，跨课程状态/命中测试/回滚写入返回 `404`，切回课程 2 后原发布状态和 3 条命中记录仍完整。第二课程仅存在于隔离夹具，不写入正式 manifest、graph-baseline、产品数据库或正式验收资料。

代码审查同时确认：知识库查询没有保留 `WHERE course_id=1` 的生产硬编码；管理员审计 UNION 的普通审计和知识库审计均绑定同一课程参数；`save_kb_hit_test()` 在写入前验证版本归属；课程 1/2 的来源版本和审计记录不会串课。未读取、记录或提交 `.env.test.local` 中的密钥。

专项证据为 `acceptance/frontend/BUILD-030/kb-write-scope-revalidation-20260726-31.txt`；六类标准证据共享同一运行号：`acceptance/frontend/BUILD-030/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md`、`rollback.md`。

### 121.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围和代码审查 | 审查知识库版本/文件/命中测试/发布/回滚/审计 SQL、`identity.course_id` 传播、来源版本、跨课程 404、评测/社交/资源写入边界、敏感值和回滚 | 知识库读写范围闭合；课程 2 仅在临时隔离夹具；未发现 `WHERE course_id=1` 生产硬编码 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；UI/前端硬化/容器契约；`npm run lint`；`npm run typecheck`；`npm run build` | 全部通过；生产构建 `1694 modules` | `PASS` |
| T2 单元和领域规则 | `python3 scripts/test_course_store.py`；`python3 scripts/test_kb_course_scope_api.py`；评测/社交/资源课程范围 API；Adapter 边界/上下文；`cd frontend && npm run test:all -- --run` | CourseStore `12/12`；KB 课程范围通过；评测/社交/资源课程范围通过；Adapter/边界通过；Vitest `40/40` | `PASS` |
| T3 API 和契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；UI/安全契约；`admin_status`/`admin_audit_log` 课程范围复核 | OpenAPI `94 paths`；API 契约 `95 routes`；本地契约通过；仅证明 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器流程 | `npm run test:e2e:mock -- --workers=1`；课程列表/分页/空态/错误态/规范路由/知识库管理流程；授权回环环境复跑 | Mock Playwright `35/35`；知识库管理流程通过；受限沙箱初次回环超时分类为 `BLOCKED_TEST_INFRA`，授权隔离环境权威结果通过 | `OBSERVED_PASS` |
| T5 质量、安全、性能和恢复 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；Spark 负向；真实 Moodle/课程资料/人工辅助/恢复审查 | a11y `3/3`、受限 axe `4/4`、smoke `2/2`；完整验收退出码 `2` 缺失 `chapter-1-1.1-.pdf`；Spark 负向退出码 `6` 为上游 DNS/网络；正式输入与人工门禁缺失 | `OBSERVED_PASS / BLOCKED_INPUT / BLOCKED_DEPENDENCY` |
| T6 证据、账本和门禁复审 | 核对唯一 `run_id`、attempt、权威结果、T0-T6、六类证据、专项证据、退出码、脱敏、工作树快照、开放 finding 和回滚边界 | BUILD-030 六类证据已统一为 `...-31`；账本校验 `metadata=11`、`blockers=22`、`evidence_refs=178`、脱敏 PASS；正式门禁保持开放 | `REVIEW_REQUIRED` |

### 121.3 逐项验收条件

- 课程 2 的知识库版本、文件、3 条命中测试、发布状态和审计可见；切换课程 1 后不得返回课程 2 的任何内容，且跨课程状态、命中测试和回滚写入必须为 `404`。
- `validate_sources(text, course_id)` 的 `kb_version_id` 必须绑定当前课程已发布版本；无当前课程发布版本时只能使用 `local-manifest`，不能借用其他课程发布版本。
- 管理员状态与审计日志只能显示当前课程；普通审计和知识库审计的课程字段必须一致。
- CourseStore `12/12`、知识库课程范围 API、评测/社交/资源课程范围 API、Adapter、OpenAPI、前端 `40/40`、Mock `35/35`、a11y `3/3`、axe `4/4`、smoke `2/2` 和生产构建必须保持记录；任何一项回归失败都不能保留本轮权威 PASS。
- 本地隔离结果不能替代真实 Moodle 多课程、三角色、20 个 manifest-matched PDF、正式 API/OpenAPI、正式 Workflow、完整 axe 对比度、HTTPS、Docker、恢复演练或人工键盘/屏幕阅读器验收。

### 121.4 失败分类、重测和回滚规则

- 修改知识库 Store schema/query、知识库 API、`validate_sources()`、`xingchen_stream()`、管理员状态/审计、`identity.course_id` 传播、课程范围测试夹具或 API 契约时，必须从 T0 重新审查并重跑 T1-T6；不得只重跑知识库列表页或一个 SQL 查询。
- 只修改浏览器断言稳定性时，保留原始退出码和失败分类，使用新唯一 `run_id` 重跑受影响的 T4，并继续执行适用的 T5/T6；本轮受限回环启动失败归类 `BLOCKED_TEST_INFRA`，授权隔离环境结果才是浏览器权威结果。
- 缺失课程 PDF、正式 Moodle/API/角色、正式 Workflow 或人工资料归类 `BLOCKED_INPUT`；Spark 上游 DNS/网络不可用归类 `BLOCKED_DEPENDENCY`；不得改写成产品 PASS。
- 回滚仅限本轮知识库 `course_id` 过滤、Adapter 传播、跨课程 404、测试夹具和证据；不得删除跨课程泄漏断言、生成占位 PDF、伪造第二门正式课程、修改 manifest/hash/page_count 或输出密钥。

### 121.5 本轮构筑结论

本轮确认第 27 节 T0-T6 协议已覆盖知识库从版本创建、文件上传、黄金问题、发布状态、来源校验、管理员审计到跨课程拒绝的完整写入链路。知识库写入课程范围本地实现和隔离测试为观察性通过；真实课程资料、多课程 Moodle、正式 API/Workflow、完整辅助技术、HTTPS、Docker、恢复和人工验收仍开放。

本轮构筑结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`BUILD-030` 继续 `PARTIAL_IMPLEMENTATION_PENDING_GATE`，`BUILD-000` 继续 `BLOCKED_INPUT`，最终发布继续 `blocked`。

## 122. 2026-07-26 测试方案与构筑证据一致性进一步审查

本轮计划审查运行号为 `PLAN-TEST-AUDIT-20260726-32`，目标是验证第 118 节固化的测试方案能否实际约束第 121 节知识库写入课程范围构筑，并复核命令入口、证据身份、状态语义、失败分类和开放门禁。

### 122.1 审查结果

- T0-T6 顺序可执行：知识库代码审查先于静态构建、领域测试、契约、浏览器和外部门禁；课程范围改变时没有局部跳过规则。
- 命令入口已按规范复核：仓库根目录使用 `python3 -m scripts.test_verify_course_data`、`python3 -m scripts.test_refresh_progress_snapshot` 和 `python3 -m unittest -q scripts.test_validate_project_progress`；直接脚本路径的包导入失败不作为产品失败，计划继续要求模块入口。
- 证据身份可追溯：产品权威构筑为 `BUILD-030-COURSE-WRITE-SCOPE-20260726-31`，计划审查为 `PLAN-TEST-AUDIT-20260726-32`，二者不混用；六类 BUILD-030 标准证据和专项证据共享产品构筑运行号。
- 状态语义未被升级：本地 API/Mock/受限 axe/a11y/smoke 只记 `PASS` 或 `OBSERVED_PASS`；课程 PDF 缺失仍为 `BLOCKED_INPUT`；Spark 上游 DNS/网络仍为 `BLOCKED_DEPENDENCY`；T6 保持 `REVIEW_REQUIRED`。
- 回滚和敏感值边界可执行：证据不记录 `.env.test.local`、API Key、API Secret、Token、Cookie、Authorization、签名 URL、真实学生数据或完整 Workflow 问答；回滚不触碰 manifest、graph-baseline、正式数据库和占位 PDF。

### 122.2 进一步审查结论

第 27 节测试方案与第 121 节实际构筑证据一致，未发现新的未处理 P0/P1 计划缺口。`PLAN-TEST-001`、`PLAN-TEST-002`、`PLAN-CMD-001` 和 `PLAN-STATE-001` 的约束在本轮均可验证；正式 Moodle 多课程/三角色、20 个课程 PDF、正式 API/Workflow、Spark 错误鉴权、完整 axe 对比度、Docker/HTTPS、恢复和人工验收仍是开放门禁。

本轮计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`PROJECT_PROGRESS.yaml` 的 `current_review_run_id` 应为 `PLAN-TEST-AUDIT-20260726-32`，`authoritative_product_build_run_id` 应为 `BUILD-030-COURSE-WRITE-SCOPE-20260726-31`；最终发布状态不得改变为 `PASS`。

## 123. 2026-07-26 BUILD-080 管理员目录构筑后 T0-T6 复审

### 123.1 构筑范围、运行身份和代码审查

本轮产品构筑运行号为 `BUILD-080-ADMIN-DIRECTORY-20260726-33`，attempt `3`，supersede `BUILD-080-20260726-02`。本轮把 BUILD-080 原有管理员服务状态、知识库和审计工作台中明确缺失的“用户与角色”“课程与班级”只读闭环纳入实现和验收。

新增范围如下：

- Adapter 新增 `GET /api/admin/users` 和 `GET /api/admin/courses`，两者均要求 `admin` 角色。
- 用户目录、课程目录和 Moodle bridge 结果均按 `identity.course_id` 过滤；课程 1/2 只在临时隔离夹具验证，不写入正式 manifest、正式数据库或课程资料。
- `MOCK_ADMIN_DIRECTORY_JSON` 仅在 `MOCK_AUTH_MODE=true` 时生效；正式环境使用服务器端 `MOODLE_ADMIN_DIRECTORY_URL` bridge。浏览器不接触 bridge token、Cookie、Authorization、API Key 或 API Secret。
- 用户 DTO 只返回伪名标识、显示名、角色、课程、状态和最近访问时间；无目录配置时返回 `configured=false` 与空用户列表，不伪造管理员用户。
- 前端管理员页增加目录导航、脱敏来源标识、搜索、角色筛选、分页、课程卡片和空/错误状态，不提供改角色、禁用或删除操作。

代码审查确认：目录归一化在服务端丢弃其他课程和未知角色；查询参数由服务端分页；前端客户端只消费已归一化 DTO；课程摘要由当前 Adapter 绑定课程生成。没有读取或记录 `.env.test.local` 的密钥值。

标准证据与专项证据：`acceptance/frontend/BUILD-080/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md`、`rollback.md` 和 `admin-directory-revalidation-20260726-33.txt`，均共享 `BUILD-080-ADMIN-DIRECTORY-20260726-33`。

### 123.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围、权限和脱敏审查 | 审查两个管理员 GET 路由、`identity.course_id` 过滤、Mock/bridge 来源边界、敏感字段归一化、空态、前端权限导航和回滚边界 | 非管理员 403；课程 1/2 不串用户；邮箱、密码、secret、Cookie、Authorization 和 bridge token 不进入响应 | `PASS` |
| T1 静态和构建 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；容器/UI/API 契约；`npm run lint`；`npm run typecheck`；`npm run build` | 全部通过；本地 OpenAPI `96 paths`；API 契约 `97 routes`；生产构建 `1694 modules` | `PASS` / `OBSERVED_PASS` |
| T2 单元、Store、API 和 DTO | `scripts/test_admin_directory_api.py`；管理员工作台、CourseStore、知识库/课程范围、评测/社交/资源/Agent 回归；`npm run test:all -- --run` | 管理员目录通过；CourseStore `12/12`；全量 Vitest `41/41`；领域回归通过 | `PASS` |
| T3 API 和本地契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；前端容器/UI 契约 | `LOCAL_OPENAPI_EXPORTED paths=96`；`API_CONTRACT_OK routes=97`；仅证明 local-isolated Adapter，不替代正式 Moodle API | `OBSERVED_PASS` |
| T4 浏览器流程 | 授权环境定向 `npm run test:e2e:mock -- --grep "admin (user|course) directory"`；随后完整 `npm run test:e2e:mock -- --workers=1` | 目录定向 `2/2`；完整 Mock `37/37`；覆盖加载、搜索、角色筛选、分页、未配置空态和当前课程卡片 | `OBSERVED_PASS` |
| T5 质量、安全、性能和外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；真实 Moodle/HTTPS/Docker/恢复/人工审查 | a11y `3/3`、axe `4/4`、smoke `2/2`；本地验收退出码 `2`，缺失 `chapter-1-1.1-.pdf`；正式外部输入缺失 | `OBSERVED_PASS` / `BLOCKED_INPUT` |
| T6 证据、账本和门禁复审 | 核对唯一 run_id、attempt、六类证据、专项证据、命令退出码、脱敏、工作树快照、开放 finding 和回滚边界 | 新 BUILD-080 证据身份一致；正式 BUILD-000、真实 Moodle、课程资料、恢复和最终发布门禁继续开放 | `REVIEW_REQUIRED` |

### 123.3 逐项验收条件

- 非管理员访问 `/api/admin/users` 和 `/api/admin/courses` 必须返回 `403`；管理员响应必须只包含当前 `identity.course_id` 的目录记录。
- 用户角色只能是 `student`、`teacher` 或 `admin`；非法角色筛选返回 `422`；关键词和分页必须由服务端参数约束，不能在前端伪造总数或跨页数据。
- 无 `MOODLE_ADMIN_DIRECTORY_URL` 且无显式 Mock 夹具时，用户目录必须为空并明确 `configured=false`；课程目录只允许显示当前 Adapter 绑定课程摘要。
- API 响应和浏览器渲染均不得出现 `email`、`password`、`secret`、`cookie`、`authorization`、bridge token 或其他敏感凭据字段。
- 客户端必须归一化 snake_case/camelCase 字段；前端必须显示加载、空、错误、搜索、角色筛选和分页状态，且不出现删除/改角色写操作。
- 本地目录 API、前端 41 个 Vitest、Mock 37 个浏览器场景和质量门禁通过，只能证明隔离实现；不能替代真实 Moodle 多课程、三角色和正式 bridge。

### 123.4 失败分类、重测和回滚规则

- 修改目录路由、课程过滤、bridge 配置、用户/课程 DTO、前端目录状态、API 契约或 Mock 夹具时，必须从 T0 重新审查并重跑 T1-T6；不得只重跑一个列表请求或一个页面。
- 受限沙箱无法回环监听分类为 `BLOCKED_TEST_INFRA`；首次授权定向测试中的选择器/数据流断言缺陷在修正后以同一构筑的新 attempt 重跑；最终授权结果 `2/2` 才是浏览器权威结果。
- Chrome 147 对比度规则挂起分类为 `BLOCKED_DEPENDENCY`；axe `4/4` 不得解释为完整正式对比度通过；缺失课程 PDF、真实目录 bridge、三角色、HTTPS、Docker、恢复和人工输入分类为 `BLOCKED_INPUT`。
- 回滚只恢复本轮管理员目录服务端归一化、前端目录展示、契约、测试和证据；不得删除历史证据、生成占位 PDF、伪造第二门正式课程、修改 manifest/hash/page_count 或输出密钥。回滚后必须生成新 run_id 并从 T0 重跑。

### 123.5 构筑结论

本轮管理员目录在 local-isolated Adapter + authorized Mock browser 范围内达到观察性通过；正式管理员/教师/学生账号、Moodle 多课程目录、正式 bridge、课程 PDF、完整辅助技术、HTTPS、Docker、恢复演练和人工验收仍开放。`BUILD-080` 继续 `IMPLEMENTED_PENDING_GATE`，`BUILD-000` 继续 `BLOCKED_INPUT`，最终发布继续 `blocked`。

## 124. 2026-07-26 BUILD-080 构筑后计划进一步审查

本轮计划审查用于检查第 123 节是否把测试方案、每次构筑后的审查、验收条件、失败分类、证据身份和回滚规则真正落到可执行文件。计划审查不读取、不记录、不验证 `.env.test.local` 中的任何密钥值。

### 124.1 进一步审查结果

- **命令可执行性**：T0 到 T6 顺序可执行；新增管理员目录脚本、API 契约、OpenAPI 生成、Vitest、定向/完整 Mock、a11y、axe、smoke 和本地验收命令均存在。管理员目录定向入口固定为 `npm run test:e2e:mock -- --workers=1 --grep "admin (user|course) directory"`，其中 `|` 必须保留为正则分支符；错误的 `npm run test` 入口未被写入计划，正式入口为 `test:all`、`test:e2e:mock`、`test:a11y`、`test:axe` 和 `test:e2e`。
- **状态语义**：本地管理员 API 和 Mock 浏览器只能记 `PASS` 或 `OBSERVED_PASS`；本地完整验收因课程资料缺失记 `BLOCKED_INPUT`；T6 记 `REVIEW_REQUIRED`。没有把目录实现或本地 OpenAPI 升级为正式发布 PASS。
- **证据身份**：产品构筑 `BUILD-080-ADMIN-DIRECTORY-20260726-33` 与计划审查运行号分离；六类标准证据和管理员专项证据共享产品构筑运行号；旧 BUILD-080 `...-02` 保留为 superseded 历史身份。
- **验收闭环**：用户权限、课程范围、目录来源、脱敏、未配置空态、搜索/角色/分页、课程卡片和浏览器失败重测均有自动化断言；真实 Moodle、多课程、三角色、正式 bridge、Docker/HTTPS、恢复和人工辅助技术仍明确列为开放条件。
- **回滚完整性**：回滚范围包含服务端、前端、契约、测试和证据索引，但禁止删除历史证据、课程资料或修改 manifest/hash/page_count；修复后必须生成新 run_id 并从最早受影响层级重跑。

### 124.2 计划缺口和风险复核

本轮未发现新的未处理 P0/P1 计划缺口。仍开放的外部门禁为：20 个 manifest-matched 课程 PDF、真实 Moodle 多课程和三角色、正式目录 bridge/API/OpenAPI、真实 Workflow/Spark 鉴权与错误链路、完整 axe 对比度、键盘/屏幕阅读器、六视口人工证据、Docker/HTTPS、备份恢复和提交材料。`BUILD-080` 本轮本地目录闭环不能关闭这些风险。

本轮计划进一步审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。本节形成的 `PLAN-TEST-AUDIT-20260726-34` 基线已由 124.3 的 `PLAN-TEST-AUDIT-20260726-35` 命令复现性复审取代；当前 `authoritative_product_build_run_id` 仍为 `BUILD-080-ADMIN-DIRECTORY-20260726-33`，`BUILD-000` 和最终发布状态不得改变为 PASS。

### 124.3 定向命令复现性复审（PLAN-TEST-AUDIT-20260726-35）

本次复审发现第 123.2 节原定向命令曾写成 `admin (user\|course) directory`。在 Playwright 正则中，反斜杠会把 `|` 变成字面量字符，无法稳定匹配“用户目录”或“课程目录”用例；BUILD-080 的历史权威证据实际使用的是正确形式 `admin (user|course) directory`。该计划级 `P1` 缺陷记为 `PLAN-CMD-002`，现已修正并用新审查运行号复核。

- 修正后的命令必须选中两条管理员目录用例，结果阈值为 `2 passed`、退出码 `0`；无匹配、只匹配一条或退出码非零均为 `FAIL`。
- 本次只修改计划、账本和计划审查证据，没有修改产品代码或 BUILD-080 产品构筑；`BUILD-080-ADMIN-DIRECTORY-20260726-33` 仍是权威产品构筑。
- `PLAN-CMD-002` 已关闭；本地隔离结果继续记为 `OBSERVED_PASS`，课程资料、真实 Moodle 三角色/多课程、正式 bridge、完整 axe、人工辅助技术、Docker/HTTPS、恢复和最终发布门禁继续开放。

本次计划命令复现性复审结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`PROJECT_PROGRESS.yaml` 的 `current_review_run_id` 和 `authoritative_review_run_id` 更新为 `PLAN-TEST-AUDIT-20260726-35`；`authoritative_product_build_run_id` 保持 `BUILD-080-ADMIN-DIRECTORY-20260726-33`，`BUILD-000` 和最终发布状态不得改变为 PASS。

## 125. 2026-07-26 BUILD-080 内容审核构筑后 T0-T6 复审

### 125.1 构筑范围、运行身份和代码审查

本轮产品构筑运行号为 `BUILD-080-CONTENT-MODERATION-20260726-36`，attempt `1`，supersede `BUILD-080-ADMIN-DIRECTORY-20260726-33`。本轮在已有讨论功能上补齐本地内容审核闭环，范围严格限定为课程内主题/回复举报、管理员审核队列和审核决策。

本轮新增或复核的行为如下：

- `POST /api/discussions/{topic_id}/report` 接受主题或同一主题下的回复举报；举报后对象进入 `pending_review`，学生侧不可继续读取待审核主题。
- `GET /api/admin/moderation` 只允许管理员读取当前 `identity.course_id` 的待审核队列，支持关键词、内容类型和服务端分页。
- `PATCH /api/admin/moderation/{content_type}/{content_id}` 只允许管理员批准或拒绝当前课程对象；批准恢复可见，拒绝关闭审核对象。
- 举报和决策均有幂等键、冲突响应、request ID 和审计记录；重复相同请求返回原结果，不同语义复用幂等键返回 `409`。
- 主题与回复的课程范围、回复所属主题范围和管理员队列范围均在服务端校验；跨主题回复举报返回 `404`，不能借助对象 ID 越权。
- 管理员前端提供“内容审核”导航、搜索、类型筛选、原因输入、批准/拒绝、加载/空态/错误态；学生和课程成员获得讨论举报入口。浏览器不接触任何 API Key、API Secret、Token、Cookie、Authorization 或真实用户敏感字段。

代码审查确认：Store 的审核状态变更、举报冲突、管理员权限、课程过滤、回复归属校验、审计和 request ID 已形成闭环；临时 SQLite/Mock 仅用于隔离测试，不修改正式 manifest、课程 PDF、graph-baseline、正式数据库或 `.env.test.local`。证据不记录密钥、完整 Authorization、签名 URL、真实学生数据或完整问答内容。

本轮标准证据与专项证据共享产品构筑运行号：`acceptance/frontend/BUILD-080/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md`、`rollback.md` 和 `content-moderation-revalidation-20260726-36.txt`；旧的 `admin-directory-revalidation-20260726-33.txt` 保留为历史证据。

### 125.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围、权限、隔离和安全审查 | 审查举报/队列/决策三条路由、学生/教师/管理员权限、主题/回复课程范围、跨主题拒绝、状态机、幂等、request ID、审计、DTO 脱敏和回滚边界 | 非管理员不能读审核队列；主题/回复均绑定当前课程；跨主题回复举报 `404`；敏感字段不进入响应或证据 | `PASS` |
| T1 静态、编译、构建和契约硬化 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；`test_frontend_hardening.py`；`test_frontend_container_contract.py`；`npm run lint`；`npm run typecheck`；`npm run build` | 全部通过；生产构建 `1694 modules`；硬化、容器和 UI 契约通过 | `PASS` |
| T2 单元、Store、API、客户端和领域回归 | `python3 scripts/test_admin_moderation_api.py`；管理员工作台/目录、Social API、课程范围/资源/评测/活动/Agent 回归；`cd frontend && npm run test:all -- --run` | `ADMIN_MODERATION_API_OK`；Social、管理员工作台、目录和相关领域回归通过；Vitest `43/43` | `PASS` |
| T3 API 和本地契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；审查 API manifest、OpenAPI、请求/响应 DTO 和错误码 | Local OpenAPI `99 paths`；API 契约 `100 routes`；仅证明 local-isolated Adapter，不替代正式 Moodle API/OpenAPI | `OBSERVED_PASS` |
| T4 浏览器流程 | 授权环境定向 `npm run test:e2e:mock -- --workers=1 --grep "admin moderation queue"`；随后完整 `npm run test:e2e:mock -- --workers=1`；核对学生举报、管理员筛选/批准/拒绝、空态和错误态 | 内容审核定向 `1/1`；完整 Mock `38/38`；受限回环失败按 `BLOCKED_TEST_INFRA` 保留，授权结果为浏览器权威结果 | `OBSERVED_PASS` |
| T5 质量、安全和正式外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；审查真实 Moodle/三角色/HTTPS/Docker/恢复/人工辅助技术 | a11y `3/3`、受限 axe `4/4`、smoke `2/2`；完整验收退出码 `2`，首个缺失 PDF 为 `chapter-1-1.1-.pdf`；正式外部输入缺失 | `OBSERVED_PASS / BLOCKED_INPUT` |
| T6 证据、账本和门禁复审 | 核对唯一 run_id、attempt、supersede 链、六类证据、专项证据、命令退出码、敏感值扫描、工作树、开放 finding 和回滚边界 | 内容审核证据已归档；BUILD-080、BUILD-000 和最终发布的正式外部门禁仍开放 | `REVIEW_REQUIRED` |

### 125.3 逐项验收条件

- 权限：学生/课程成员可以举报自己课程内主题或回复；教师不能读取或修改管理员审核队列；非管理员访问队列和决策路由必须为 `403`；管理员只能处理当前 `identity.course_id` 的对象。
- 状态机：主题举报和回复举报均进入 `pending_review`；待审核内容不能在学生详情中继续作为可见内容返回；批准后的回复为 `visible`；拒绝后的主题为 `closed`，审核队列不再返回已决策对象。
- 课程和对象隔离：切换课程 2 后课程 1 的队列必须为空；跨主题提交其他主题的 `reply_id` 必须为 `404`；不存在、跨课程或错误类型的审核对象不得通过错误差异泄露其他课程对象。
- 幂等和并发：相同幂等键、相同请求体必须返回原结果且不得重复写入；相同幂等键改变请求语义必须为 `409`；已完成举报用新键重复提交必须为明确冲突；审核决策同理，不能重复追加状态转换。
- 审计和可追踪性：举报和决策各写入审计动作、当前课程、对象 ID、结果、原因和 request ID；前端和专项证据不得包含 API Key、API Secret、Token、Cookie、Authorization、bridge token、邮箱、密码或真实用户敏感值。
- 管理员 UI：必须覆盖内容审核导航、加载、空、错误、关键词、内容类型、原因输入、批准、拒绝和刷新后的队列状态；失败响应需显示可理解的错误，不得静默标记成功。
- 本地结果边界：API `ADMIN_MODERATION_API_OK`、Vitest `43/43`、Mock `38/38`、a11y `3/3`、axe `4/4`、smoke `2/2` 和生产构建只证明隔离实现；不能替代真实 Moodle 多课程、学生/教师/管理员三角色、正式 API/OpenAPI、课程 PDF、正式 Workflow/Spark、完整 axe、人工辅助技术、Docker/HTTPS 或恢复演练。

### 125.4 失败分类、重测和回滚规则

- 修改 Store 审核表/状态机、举报/队列/决策路由、权限依赖、课程过滤、回复归属、幂等/审计/request ID、API DTO、前端审核交互或 Mock 路由时，必须从 T0 重新审查并重跑 T1-T6；不得只重跑一条请求或一个页面。
- 只修改浏览器选择器、等待条件或数据流断言时，必须保留原始失败输出，生成新的唯一 run_id，重跑受影响的 T4 及适用的 T5/T6；定向命令必须选中恰好 `1 passed`，无匹配、多匹配或退出码非零均为 `FAIL`。
- 权限绕过、跨课程/跨主题泄漏、敏感值泄漏、无幂等导致重复变更、无审计或错误状态转换为 P0/P1 产品失败，不得降级为测试基础设施问题；修复后从最早受影响层级重跑。
- 受限环境无法回环监听或 webServer 健康检查超时分类为 `BLOCKED_TEST_INFRA`；Chrome 147 对比度规则挂起分类为 `BLOCKED_DEPENDENCY`；缺失 PDF、真实 Moodle/API/三角色、正式 Workflow、Docker/HTTPS、恢复和人工资料分类为 `BLOCKED_INPUT`，都不能改写成产品 PASS。
- 外部输入恢复时从最早受影响的 T0 重新执行；不得用新的成功结果覆盖旧失败输出。幂等写操作重测必须复用同一幂等键验证重放，不能通过换键掩盖重复写入。
- 回滚仅限本轮内容审核服务端状态/权限/课程过滤、前端审核页和举报入口、测试/契约及证据索引；不得删除历史证据、修改 manifest/hash/page_count、生成占位 PDF、伪造第二门正式课程、修改正式数据库或输出密钥。回滚后必须生成新 run_id 并从 T0 重测。

### 125.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260726-37）

本轮计划审查核对第 27 节通用 T0-T6 协议与第 125 节内容审核矩阵、命令入口、状态语义、证据身份、失败分类、重测规则和回滚边界：

- 命令入口可执行且无歧义：代码审查发现用例标题为 `admin moderation queue filters content and records an approval decision`，因此管理员内容审核定向入口固定为 `npm run test:e2e:mock -- --workers=1 --grep "admin moderation queue"`；计划同时保留 API、契约、前端、质量和本地总验收入口。定向结果阈值是恰好 `1 passed`，无匹配不能记为通过。
- 安全与权限审查覆盖举报者、课程成员、教师和管理员四类边界，覆盖主题/回复两种对象、跨主题拒绝、课程切换、敏感字段扫描、幂等冲突和审计 request ID；没有把“队列显示成功”当作权限通过。
- 证据身份分离：产品构筑为 `BUILD-080-CONTENT-MODERATION-20260726-36`，计划审查为 `PLAN-TEST-AUDIT-20260726-37`；标准六类证据和内容审核专项证据共享产品构筑号，旧管理员目录专项证据只作为历史记录。
- 状态语义正确：T0-T2 为本地实现通过，T3-T5 的本地/Mock/受限质量结果仍为观察性结果；缺失课程 PDF 和真实正式环境保持 `BLOCKED_INPUT`；T6 为 `REVIEW_REQUIRED`；BUILD-080 仍是 `IMPLEMENTED_PENDING_GATE`，最终发布仍为 `blocked`。
- `PLAN-CMD-003` 记录了原始 `content moderation` grep 与实际用例标题不匹配的问题；已修正为 `admin moderation queue`，并在授权浏览器环境重测为恰好 `1 passed`，现已关闭。除此之外没有新的未处理 P0/P1 缺口。内容审核 finding `BUILD080-MODERATION-001` 仅在本地隔离范围关闭；正式三角色、多课程、课程资料、Workflow/Spark、完整辅助技术、Docker/HTTPS、恢复和提交材料仍是开放门禁。

本轮计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`PROJECT_PROGRESS.yaml` 的 `current_review_run_id` 和 `authoritative_review_run_id` 更新为 `PLAN-TEST-AUDIT-20260726-37`；`authoritative_product_build_run_id` 更新为 `BUILD-080-CONTENT-MODERATION-20260726-36`。不得将 BUILD-080、BUILD-000 或最终发布状态改为 `PASS`。

## 126. 2026-07-26 BUILD-090 Spark Assistant 增量 provider revalidation

### 126.1 运行身份、范围和安全边界

本轮运行号为 `BUILD-090-SPARK-REVALIDATION-20260726-38`，attempt `1`，属于 BUILD-090 的增量 provider revalidation，supersede 关系指向全量本地构筑 `BUILD-090-20260726-02`，但不替代其完整 Agent/前端标准证据。本轮只验证本地 `.env.test.local` 指向的 Spark Assistant WebSocket 测试端点，不把它写成正式 Xingchen Workflow 或课程知识库验收。

测试使用固定、无个人数据的协议请求，脚本只输出握手状态、脱敏错误码、帧数和关闭状态；不输出或归档 API Key、API Secret、签名 URL、Authorization、Cookie、完整问题、完整回答或真实学生数据。环境变量名和文件权限通过离线契约检查，密钥值未被记录。

### 126.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 实际结果 | 判定 |
|---|---|---|---|
| T0 范围、配置和安全审查 | 审查 Spark endpoint 形状、签名材料构造、`.env.test.local` 权限、脱敏输出、固定测试内容、与 Xingchen Workflow 的边界 | 配置键齐全；离线契约覆盖凭据缺失、占位 endpoint、预置鉴权参数和签名变异；未记录敏感值 | `PASS` |
| T1 静态和命令入口 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；模块测试入口复核 | 静态、Shell 和 diff 通过；直接执行 `python3 scripts/test_spark_assistant_contract.py` 曾因包导入失败，分类为 `PLAN_COMMAND_FAILURE`；规范模块入口通过 | `PASS`，命令缺陷已记录 |
| T2 离线协议和帧规则 | `python3 -m unittest -q scripts.test_spark_assistant_contract` | `7/7` 通过；签名 URL 不暴露原始 key/secret，WebSocket 帧和错误变异断言通过 | `PASS` |
| T3 远端协议和参数负向 | `python3 scripts/test_spark_assistant_ws.py --timeout 30`；`python3 scripts/test_spark_assistant_negative.py --timeout 15`；`python3 scripts/test_spark_assistant_auth_negative.py --timeout 15` | 正向 handshake `101`、`header.code=0`、3 帧、正常关闭；参数负向 `4/4` 返回 `10003/10004`；无权限 APPID `11200`；错误 key/secret/date 仍正常完成 | `OBSERVED_PASS / FAIL` |
| T4 浏览器流程 | 本轮未修改前端或 Agent UI；复用 BUILD-090-20260726-02 的 Mock 浏览器、a11y 和 smoke 证据，不重复宣称浏览器重测 | 适用性原因：本轮仅为服务端 provider 网络重验证，无前端差异；既有 UI 结果保持历史观察性证据 | `NOT_APPLICABLE_WITH_REASON` |
| T5 安全、正式 Workflow 和外部验收 | 鉴权负向门禁、真实 Xingchen Workflow、正式知识库、课程 PDF、真实角色、性能/并发/恢复和正式辅助技术审查 | 3 个错误签名 case 退出为失败；真实 Workflow、知识库、课程资料、角色和正式环境仍缺失 | `FAIL / BLOCKED_INPUT` |
| T6 证据、账本和门禁复审 | 核对 provider 专项证据、运行号、退出码、失败分类、敏感值扫描、全量构筑证据不被窄范围结果覆盖 | 增量证据已归档；`SPARK-AUTH-FAIL-001` 继续开放；BUILD-090 和最终发布不能关闭 | `REVIEW_REQUIRED` |

### 126.3 逐项验收条件

- 正向协议必须完成 WebSocket `101` 握手，收到合法 header、assistant 内容、递增 seq、最终 choice 状态，并以 close code `1000` 正常关闭；本轮实际满足。
- 缺少 app ID、消息体、非法 role 和非法 temperature 的 4 个参数/字段负向必须返回非零业务错误且不得进入正常最终回答；本轮 `4/4` 满足，错误码为 `10003/10004`。
- 无权限 APPID 必须返回非零权限错误且不得产生正常最终回答；本轮 `11200` 满足。
- 错误 API Key、错误 Secret 和篡改签名 date 必须在握手后被业务端拒绝，不能出现最终 `header.code=0` 和完整正常回答；本轮三项均未满足，必须保留 P0 `SPARK-AUTH-FAIL-001`，不得以握手 `101` 或网络可达替代鉴权通过。
- Spark Assistant 测试端点结果不得写成正式 Xingchen Workflow、知识库来源、课程答案质量、并发容量或正式角色验收；这些必须使用版本化正式 endpoint、Workflow、课程资料和角色夹具重新执行。
- 所有网络测试的日志、终端输出和证据必须不含密钥值、签名 URL、Authorization、Cookie、完整问答或真实学生数据；异常只记录类别、错误码、退出码和连接阶段。

### 126.4 失败分类、重测和回滚规则

- `wrong-api-key`、`wrong-secret` 或 `tampered-date` 出现最终业务帧是 P0 鉴权失败，不得归类为“测试端点可用”或 `OBSERVED_PASS`；在供应方确认 endpoint、Assistant 绑定、签名版本和凭据绑定前，不继续增加错误凭据请求。
- 受限网络 DNS/连接失败归类为 `BLOCKED_DEPENDENCY`，不改写为 provider PASS；授权网络的权威输出必须保留受限环境失败作为历史边界。
- 若只修改离线测试入口、参数解析或脱敏断言，保留原始失败输出，使用新唯一 run_id 重跑 T0-T3 和适用的 T5/T6；本轮直接脚本导入失败记为 `PLAN_COMMAND_FAILURE`，模块入口 `7/7` 才是规范结果。
- 若修改签名算法、endpoint 构造、WebSocket 帧、Adapter provider 适配或错误映射，必须从 T0 重新执行 T1-T6，并同时复跑 Agent/Adapter/前端受影响回归；不得只重跑一个错误 case。
- 回滚仅限本轮测试入口、provider 测试代码、脱敏证据和配置键名说明；不得回滚或改写正式密钥、生成签名 URL、修改课程 manifest/PDF/hash、接入未验证 provider，或将 Spark 直连替换正式 Workflow 主链路。

### 126.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260726-39）

本轮审查确认：T0-T3 的命令、退出码、错误分类和敏感值边界已落到可执行脚本；T4 明确以“本轮无前端变更”为 `NOT_APPLICABLE_WITH_REASON`，没有把历史 Mock 浏览器结果冒充本轮重测；T5 明确区分协议观察性通过、鉴权 P0 失败和正式 Workflow `BLOCKED_INPUT`。

计划级 finding `PLAN-CMD-004` 记录了直接脚本入口与 `scripts.*` 包导入的差异，规范入口已固定为 `python3 -m unittest -q scripts.test_spark_assistant_contract` 并通过 `7/7`。`SPARK-AUTH-FAIL-001` 不关闭，且本轮授权网络重测再次复现三类错误签名最终 `header.code=0`。

本轮没有修改产品代码，也没有把增量 Spark 测试 run_id 替换 BUILD-090 全量本地标准证据。当前权威产品代码构筑仍为 `BUILD-080-CONTENT-MODERATION-20260726-36`；`BUILD-090-SPARK-REVALIDATION-20260726-38` 仅作为最新 provider 专项证据。BUILD-090 仍为 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。

本轮计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。计划审查运行号为 `PLAN-TEST-AUDIT-20260726-39`，不得将 Spark 鉴权、正式 Workflow、课程资料、真实角色、正式辅助技术、Docker/HTTPS、恢复或最终发布标记为 `PASS`。

## 127. 2026-07-28 BUILD-060 课堂活动生命周期构筑后 T0-T6 复审

### 127.1 运行身份、范围和安全边界

本轮产品构筑运行号为 `BUILD-060-ACTIVITY-LIFECYCLE-20260728-40`，attempt `4`，supersede `BUILD-060-ACTIVITY-20260726-21` 和标准证据运行 `BUILD-060-20260725-02`。计划审查运行号为 `PLAN-TEST-AUDIT-20260728-41`，两者不得互相替代。

本轮在既有投票/问卷和教师活动管理基础上补齐完整本地生命周期：

- 活动状态机固定为 `draft -> published -> closed -> published`。学生只可读取非草稿活动；关闭后禁止提交，重新开放后只在剩余次数内继续作答。
- 教师端提供发布、关闭和重新开放；状态迁移键由组件实例标识和递增序列组成，避免同毫秒和页面重新挂载后复用旧键。
- 活动创建、学生作答和状态迁移使用 `BEGIN IMMEDIATE` 活动专用事务，在同一提交中完成幂等判定、业务写入、审计和响应缓存；同键同语义重放返回原结果，同键不同语义返回 `409`。
- 学生尝试次数按 `MAX(attempt)` 推导，兼容旧数据库非连续记录；`attempts_used`、`can_respond` 和 `next_attempt` 与最大尝试号、学生角色、活动状态和次数上限一致。
- 聚合结果只统计每位学生最大 `attempt` 的最新答案，重答不重复增加参与人数；开放态未提交学生看不到聚合，提交后或活动关闭后可见。
- 活动详情、结果、响应和状态迁移均按 `identity.course_id` 过滤；跨课程返回 `404`。真实会话未知角色在认证边界拒绝，Store 也显式限定 `student|teacher|admin`。
- 创建、响应、发布、关闭和重开写入 request ID 审计。证据不读取或记录 API Key、API Secret、Token、Cookie、Authorization、签名 URL、完整问答或真实学生数据。

标准证据位于 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `activity-lifecycle-revalidation-20260728-40.txt`。旧 `activity-management-revalidation-20260726-21.txt` 保留为历史，不得覆盖、删除或计入本轮结果。

### 127.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 范围、状态、安全和代码审查 | 审查角色权限、课程隔离、状态机、结果可见性、顺序尝试、旧库兼容、原子幂等、request ID 审计、未知角色和回滚边界 | 初审发现跨挂载键复用、非原子幂等窗口、未知角色失败开放、创建/响应缺 request ID 和冲突状态码不一致；全部修复并补回归，未剩余 P0/P1 产品缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；`npm run lint`；`npm run typecheck`；`npm run build`；前端硬化和容器契约 | 全部退出码 `0`；生产构建 `1694 modules`；硬化、容器和 UI 契约通过 | `PASS` |
| T2 单元、组件、Store 和领域回归 | `PYTHONPATH=$PWD/agent-adapter python3 scripts/test_activity_api.py`；Adapter/Store；Social/Adapter runtime；`cd frontend && npm run test:all -- --run` | `ACTIVITY_API_OK` 含 lifecycle、legacy gap、latest results、course scope、atomic idempotency、multi-instance atomic idempotency、audit；两个独立 `CourseStore` 实例共享同一 SQLite 文件首次修复后定时运行 `0.62s`，最终修改后定时复跑 `0.61s`，并行独立复跑 `3/3`；Adapter `13/13`、Store `12/12`、Vitest `45/45` | `PASS` |
| T3 本地 API/OpenAPI 契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_ui_contract.py`；审查 `api-test-manifest.yaml` | Local OpenAPI `102 paths`、API 契约 `103 routes`、UI 契约通过；只代表 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器生命周期和完整 Mock | `npm run test:e2e:mock -- --workers=1 --grep "teacher can publish close and reopen an activity"`；随后完整 Mock | 两条命令均因 `/usr/bin/python3: No module named uvicorn` 退出 `1`；依赖安装审批服务返回 `503`，未绕过审批；没有本轮浏览器 PASS | `BLOCKED_TEST_INFRA` |
| T5 质量、安全和正式外部验收 | `npm run test:a11y -- --workers=1`；`npm run test:axe -- --workers=1`；`npm run test:e2e -- --workers=1`；`bash scripts/run_local_acceptance.sh`；真实角色/课程/API/辅助技术审查 | axe 缺 `uvicorn`；a11y/smoke 的 Vite 监听 `127.0.0.1` 返回 `EPERM`；完整验收退出码 `2`，首个缺失 PDF 为 `chapter-1-1.1-.pdf` | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对唯一 run ID、attempt、supersede 链、六类证据、专项证据、退出码、敏感值扫描、工作树、开放 finding 和计划命令 | 产品和计划运行身份分离；历史结果未复用；正式外部门禁继续开放 | `REVIEW_REQUIRED` |

T5 在 metadata/review 标准矩阵中使用唯一规范状态 `BLOCKED_INPUT`；缺 `uvicorn`、Vite `EPERM` 和审批 `503` 在 T4 及 T5 明细中记录为 `BLOCKED_TEST_INFRA`，不得合并成伪造的浏览器通过。

### 127.3 逐项验收条件

- 生命周期：草稿只对教师/管理员可见；草稿发布后学生可见；开放活动可以在次数范围内提交；关闭后 `can_respond=false` 且 `next_attempt=null`；重新开放后仅未耗尽次数的学生恢复提交。
- 顺序尝试：首次必须为 attempt `1`，后续必须等于历史 `MAX(attempt)+1`；超过 `max_attempts`、跳号、重复同一 attempt 或关闭态提交均失败。旧库只有 attempt `2` 时，下一次必须为 `3`，不能因 `COUNT(*)=1` 卡死。
- 最新结果：同一学生多次作答只计一个参与者，选项计数来自最大 attempt；开放态未提交学生得到 `results_available=false` 和空 options，关闭态所有课程内学生可读取结果。
- 权限和隔离：学生不能创建或迁移活动，教师/管理员不能代学生提交；不存在或跨课程详情、结果、响应和迁移统一为 `404`；异常真实会话角色不得读取草稿或聚合结果。
- 幂等和并发：同一用户、endpoint、key 和语义重放返回同一 ID；共享 Store API 并发以及两个独立 `CourseStore` 实例共享同一 SQLite 文件的同键并发，状态码都应为一个 `201` 和一个 `200`，数据库只产生一个活动和一条创建审计；同键改变答案或语义返回 `409`。业务写入、审计和幂等响应必须原子提交。多实例夹具必须使用显式 `ThreadPoolExecutor` 和有限超时，测试执行器挂起不得记为产品通过或失败。
- 审计：创建、学生响应、发布、关闭和重新开放必须记录当前课程、对象、动作和 request ID；同键重放不得重复追加审计。
- 前端：教师可以发布、关闭和重开；学生看到剩余次数、提交后结果和关闭提示；关闭按钮跨组件重新挂载产生不同幂等键。组件测试必须覆盖“活动已结束”禁用、“1 人参与”和跨挂载键唯一。
- 浏览器结果边界：本轮 Playwright、a11y、axe 和 smoke 没有通过结果。历史 Mock `25/25`、活动专项 `1/1`、a11y `3/3`、smoke `2/2` 和 axe 历史结果均不得计入运行 `...40`。
- 正式边界：本地 `103 routes`、`102 paths`、Vitest `45/45` 和隔离 API 不能替代真实 Moodle 三角色、多课程、正式 API/OpenAPI、课程 PDF、正式 Workflow/知识库、完整 axe、人工辅助技术、Docker/HTTPS、恢复或最终发布。

### 127.4 失败分类、重测和回滚规则

- 权限绕过、跨课程泄漏、未知角色读取草稿/结果、关闭态仍可提交、聚合重复计数、非原子幂等导致重复活动、审计缺失或前端假成功为 P0/P1 产品失败；修复后从 T0 重跑 T1-T6。
- 组件重新挂载复用幂等键会导致“关闭 -> 重开 -> 再关闭”重放旧结果，分类为产品 P1，不得归入测试基础设施。本轮已用组件实例标识和跨挂载 Vitest 关闭。
- 缺 Python `uvicorn`、Vite `listen EPERM`、webServer 无法健康检查或审批服务 `503` 分类为 `BLOCKED_TEST_INFRA`；不得复制历史浏览器结果。环境恢复后使用新的产品 run ID，从 T4 重跑定向、完整 Mock、a11y、axe、smoke 和 T6。
- 定向 Playwright 入口固定为 `--grep "teacher can publish close and reopen an activity"`，恢复环境后必须恰好命中 `1 passed`。无匹配、多匹配或退出码非零均不能记为通过。
- 缺失课程 PDF、真实 Moodle/API/三角色、正式 Workflow、人工辅助技术、Docker/HTTPS、恢复和提交材料分类为 `BLOCKED_INPUT` 或既有外部阻断；输入恢复后从最早受影响层级重跑，禁止生成占位 PDF 或修改 manifest/hash/page_count。
- 回滚仅限本轮活动状态机、活动专用原子事务、尝试次数/聚合/可见性、前端状态控制、测试和证据；不得删除历史活动/响应/审计/幂等记录，不得修改正式数据库、课程资料或密钥。回滚后生成新 run ID 并从 T0 重测。

### 127.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260728-41）

本轮计划审查对照第 27 节通用协议和第 127 节执行结果，复核范围、状态语义、命令入口、验收条件、证据身份、失败分类、重测和回滚边界：

- `BUILD-060-ACTIVITY-LIFECYCLE-20260728-40` 是产品构筑，`PLAN-TEST-AUDIT-20260728-41` 是计划审查；六类标准证据和活动专项证据只绑定产品运行号，计划专项证据不替代产品测试。
- 初始草案使用 `--grep "activity lifecycle"`，与实际用例标题不一致；计划 finding `PLAN-CMD-005` 已将规范入口固定为 `teacher can publish close and reopen an activity`。本轮因 webServer 缺依赖在测试选择前失败，因此只能证明命令配置被执行，不能声称 `1/1`。
- 产品审查发现的跨挂载键复用、非原子幂等、未知角色失败开放、request ID 缺失和冲突状态码不一致均已修复；活动 API、Adapter、Store、组件和契约回归通过。原子幂等同时由共享 Store API 并发和两个独立 `CourseStore` 实例共享 SQLite 的并发夹具覆盖；后者首次修复后定时运行 `0.62s`，最终修改后定时复跑 `0.61s` 且并行独立复跑 `3/3`。最初的 `asyncio.to_thread` 测试执行器挂起已替换为显式线程池和 5 秒超时，该历史只归类为测试夹具问题。原子事务只覆盖本轮活动写端点，没有借机改写其他业务模块。
- `scripts/validate_project_progress.py` 已显式允许 `BLOCKED_TEST_INFRA`，并新增 metadata 单元回归；T4 状态可由机器校验，不需要降级成语义较弱的 `NOT_RUN`。
- 旧 `activity-management-revalidation-20260726-21.txt` 和历史浏览器统计保留但不计数；缺依赖、回环 `EPERM`、审批 `503` 和 PDF 缺失均保留实际退出码和分类。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。`PROJECT_PROGRESS.yaml` 的 `current_review_run_id` 和 `authoritative_review_run_id` 更新为 `PLAN-TEST-AUDIT-20260728-41`，`authoritative_product_build_run_id` 更新为 `BUILD-060-ACTIVITY-LIFECYCLE-20260728-40`。BUILD-060 继续 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布不得改为 `PASS`。

## 128. 2026-07-28 BUILD-030 交互式先修关系图构筑后 T0-T6 复审

### 128.1 运行身份、范围和安全边界

本轮产品构筑运行号为 `BUILD-030-GRAPH-INTERACTIVE-20260728-42`，attempt `1`，supersede `BUILD-030-COURSE-WRITE-SCOPE-20260726-31` 的 BUILD-030 标准证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260728-43`，两者不得互相替代。

本轮关闭“本地节点网格不是最终关系图”的产品缺口，但不关闭正式图谱门禁：

- 新增 `GET /api/knowledge-graph/graph`，返回当前身份课程的结构化节点和方向边；查询必须同时过滤 source 和 target 两端课程，禁止跨课程边暴露对象 ID。
- 前端默认使用 React Flow 关系视图，支持缩放、平移、节点拖动、适配视图、Minimap、方向箭头和键盘可选择节点；保留列表视图作为紧凑和降级浏览方式。
- 图节点展示章节、类别和掌握状态；服务端先修路径同时高亮连续节点和方向边，章节/搜索筛选后只保留两端均可见的边。
- 全局搜索的 `?q=` 参数直接进入图谱筛选；失败重试必须发起新请求。图谱组件按需懒加载，不能把复杂图依赖加入首屏主 chunk。
- 只使用本地图谱基线、临时 SQLite、Mock Auth 和本地 OpenAPI；不修改 manifest、`graph-baseline.json`、PDF hash/page_count，不读取或记录密钥、Cookie、Authorization、完整问答或真实学生数据。

标准证据位于 `acceptance/frontend/BUILD-030/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`；专项证据为 `interactive-graph-revalidation-20260728-42.txt`。历史路径、课程列表、路由范围、课程数据范围和知识库写入范围专项证据继续保留。

### 128.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 范围、安全和代码审查 | 审查课程隔离、边两端过滤、悬空边、图布局、键盘语义、路径高亮、URL 筛选、失败重试、依赖和回退 | 初始同步引入导致主 chunk `650 kB` 警告，已改为懒加载；ARIA tab 语义和筛选关系统计已修正；无剩余 P0/P1 产品缺陷 | `PASS` |
| T1 静态、类型、依赖和构建 | lint、typecheck、Python/Shell、UI/硬化/容器契约、生产构建、安装审计 | 全部退出码 `0`；安装审计 `0 vulnerabilities`；构建 `1857 modules`，主 chunk `467.27 kB`、图谱 chunk `182.17 kB`，无 chunk 警告 | `PASS` |
| T2 单元、组件、Store 和领域回归 | 图谱夹具、客户端快照归一化、图投影、Adapter/Store/活动/社交/runtime、Vitest 全量 | 图快照 `20 nodes/17 edges`；三角色相同、未知角色拒绝、跨课程边不泄漏；Adapter `13/13`、Store `12/12`、Vitest `48/48` | `PASS` |
| T3 本地 API/OpenAPI 契约 | 生成本地 OpenAPI，执行 API/UI/图谱场景契约 | API `104 routes`、Local OpenAPI `103 paths`、图谱/教材/情景夹具通过；只代表 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器关系图流程 | 定向执行图谱浏览和先修路径两例，再执行完整 Mock；检查 20 节点、17 边、键盘选点、视图切换和 2 条路径边 | 定向和完整 Mock 均在用例选择前因缺 `uvicorn` 退出 `1`；审批服务 `503`，没有本轮浏览器 PASS | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | a11y、axe、smoke、完整本地验收、真实图谱/角色/PDF/辅助技术 | axe 缺 `uvicorn`；a11y/smoke 的 Vite 回环监听 `EPERM`；完整验收缺 `chapter-1-1.1-.pdf` 退出 `2` | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对 run ID、attempt、supersede、六类证据、专项证据、退出码、脱敏、工作树、依赖和开放 finding | 产品与计划运行身份分离，历史浏览器结果未复用，正式门禁保持开放 | `REVIEW_REQUIRED` |

### 128.3 逐项验收条件

- 图快照必须返回当前基线的 `20` 个节点和 `17` 条方向边；节点字段限定为 ID、名称、章节、类别和描述，边限定为 source、target 和 relation type。
- 学生、教师和管理员读取同一课程时快照一致；未知角色拒绝。临时第二课程的节点、内部边以及从课程 1 指向课程 2 的跨课程边都不得出现在课程 1 响应或错误正文中。
- 客户端必须拒绝 source 或 target 不在节点集合内的悬空边，不能把后端异常边渲染成可点击对象。
- 关系图必须具有稳定尺寸；节点按章节形成确定性布局，可缩放、平移、拖动和适配视图；每个节点具有真实按钮和掌握状态，列表视图保持可用。
- `kp-3-1 -> kp-3-2 -> kp-3-4` 的路径必须形成 3 个高亮节点和 2 条连续高亮方向边；非连续关系不能错误高亮。
- 搜索、章节筛选、关系数和可见边集合必须一致；`/knowledge-graph?q=...` 应直接应用查询，失败重试触发新请求。
- React Flow 必须位于懒加载 chunk；主入口不得因关系图库超过 Vite `500 kB` 警告线。依赖安装审计不得存在已知 vulnerability。
- 本地 API、jsdom、Mock、OpenAPI 和构建结果不能替代正式图谱版本、PDF 来源、Moodle 三角色、正式 API、六视口和人工辅助技术验收。

### 128.4 失败分类、重测和回滚规则

- 跨课程节点/边泄漏、未知角色可读、悬空边可点击、路径边错误高亮、筛选后边端点不可见、键盘无法选择或重试不发请求属于 P0/P1 产品失败；修复后从 T0 重跑 T1-T6。
- 首屏 chunk 超过警告线或关系图依赖没有按需加载属于性能 P1；必须拆包并重跑 build、hardening、Vitest 和适用浏览器层。
- 缺 `uvicorn`、Vite `listen EPERM`、webServer 启动失败和审批 `503` 分类为 `BLOCKED_TEST_INFRA`；不得复制历史图谱 Mock/a11y/axe/smoke 结果。
- 缺课程 PDF、正式图谱版本、真实 Moodle/API/三角色、人工辅助技术、Docker/HTTPS、恢复和提交材料按既有外部阻断处理；不得生成占位 PDF、第二门正式课程或修改 manifest/hash/page_count。
- 回滚仅限图快照 API/DTO、React Flow/懒加载/样式、图谱测试和本轮证据；不得删除两端课程过滤断言、历史专项证据、图谱基线或正式数据。回滚后生成新 run ID 并从 T0 重测。

### 128.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260728-43）

本轮计划审查确认产品构筑 `...42` 与计划审查 `...43` 身份分离；T0-T6 命令、20/17 图快照阈值、三角色/未知角色/跨课程边验收、图交互、路径边、懒加载、失败分类和回滚边界均可执行。浏览器和课程资料阻断未改写为产品 PASS，历史 BUILD-030 浏览器结果未计入本轮。

最终账本签核前的独立代码审查发现两个 P1：节点内容按钮的 `nodrag` 覆盖主体导致实际拖动入口缺失；路径边高亮只按端点匹配，未限定 `prerequisite`。另发现双向跨课程边、source 悬空边、URL 初始筛选和失败重试的回归证据不足。因此 `PLAN-TEST-AUDIT-20260728-43` 状态改为 `SUPERSEDED_BEFORE_FINAL_LEDGER_RUN`，不得作为最终计划审查；修复、重测和最终审查转入第 129 节。

## 129. 2026-07-28 BUILD-030 交互式关系图审查修复后 T0-T6 重测

### 129.1 运行身份和修复范围

修复后产品运行号为 `BUILD-030-GRAPH-INTERACTIVE-RETEST-20260728-44`，attempt `2`，supersede `BUILD-030-GRAPH-INTERACTIVE-20260728-42`。计划审查运行号为 `PLAN-TEST-AUDIT-20260728-45`，supersede 未完成最终账本签核的 `...43`。

- 节点内容按钮继续使用 `nodrag` 保证点击和键盘选择，新增独立 `graph-node-drag-handle`，并通过 React Flow node `dragHandle` 选择器绑定拖动入口。
- 路径边只有在 source/target 为连续路径节点且 `relation_type=prerequisite` 时高亮；同端点 `related` 边必须保持普通样式。
- 临时第二课程夹具同时加入课程 1 -> 课程 2 和课程 2 -> 课程 1 两个方向的边；客户端同时覆盖缺 source 和缺 target 的悬空边。
- 组件测试覆盖 `/knowledge-graph?q=...` 首次筛选和失败后点击重新加载发出第二次图快照请求；Playwright 增加拖动手柄、缩放、URL 筛选和重试断言。
- 不修改课程 manifest、图谱基线、PDF hash/page_count、正式数据或凭据；不把无法运行的浏览器断言记为通过。

### 129.2 修复后 T0-T6 测试矩阵

| 层级 | 修复后必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 独立审查与修复复核 | 检查拖动入口、按钮键盘语义、关系类型过滤、双向课程隔离、悬空边、URL/重试和证据身份 | 两个 P1 和两个 P2 证据缺口已修复；标准证据切换至 attempt 2，attempt 1 保留历史 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、Python/Shell、UI/硬化/容器契约、生产构建 | 全部退出码 `0`；`1857 modules`，主 chunk `467.27 kB`、图谱 chunk `182.89 kB`，无 chunk 警告 | `PASS` |
| T2 单元、组件、Store 和领域回归 | 图谱夹具、客户端、投影、URL/重试组件、Adapter/Store/活动/社交/runtime、Vitest 全量 | 图快照 `20/17`；Adapter `13/13`、Store `12/12`、Vitest `50/50`；双向跨课程边、双端悬空边、拖动手柄和异类型边负向通过 | `PASS` |
| T3 本地 API/OpenAPI 契约 | 生成本地 OpenAPI并执行 API/UI/图谱场景契约 | API `104 routes`、Local OpenAPI `103 paths`，全部本地契约退出 `0` | `OBSERVED_PASS` |
| T4 浏览器关系图流程 | 定向图谱/路径 grep 和完整 Mock | 两次均在用例选择前因缺 `uvicorn` 退出 `1`；拖动、缩放、URL/重试运行时断言未执行 | `BLOCKED_TEST_INFRA` |
| T5 可访问性和正式验收 | a11y、axe、smoke、完整本地验收、正式角色/图谱/PDF/辅助技术 | axe 缺 `uvicorn`；a11y/smoke webServer 退出 `1`；完整验收缺 `chapter-1-1.1-.pdf` 退出 `2` | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对 run ID、attempt、supersede、六类证据、专项证据、实际计数、脱敏和开放门禁 | 产品与计划运行身份分离；最终账本结果由 `...45` 记录 | `REVIEW_REQUIRED` |

### 129.3 验收和重测规则

- 拖动验收必须从专用手柄改变节点位置，同时节点内容按钮仍可聚焦并用 Enter 选择；仅存在 `nodesDraggable=true` 或库默认值不构成通过证据。
- 路径高亮必须同时匹配连续端点和 `prerequisite` 类型；同端点异类型边是强制负向用例。
- 服务端必须对 edge source 和 target 两端执行课程过滤；两个跨课程方向任一泄漏均为 P0。
- 客户端 source/target 任一不在节点集合时必须丢弃该边；URL query 和重试必须由组件或浏览器可观察请求证明。
- 浏览器基础设施恢复后生成新产品运行号，从 T4 重跑拖动、缩放、平移、fit view、键盘、URL、重试、路径、完整 Mock、a11y、axe 和 smoke；禁止复用历史 PASS。
- 正式图谱版本、PDF、Moodle 三角色、正式 API、六视口和人工辅助技术恢复后，从最早受影响层级重跑；不得生成占位输入。

### 129.4 本轮计划进一步审查（PLAN-TEST-AUDIT-20260728-45）

计划审查确认 attempt 1 的错误声明没有被静默覆盖；`...42/...43` 保留为历史，`...44/...45` 形成新的产品/计划身份链。BUILD-030 六类当前标准证据绑定 `...44`，修复专项证据为 `interactive-graph-revalidation-20260728-44.txt`。

计划审查结论保持 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。BUILD-030 继续 `PARTIAL_IMPLEMENTATION_PENDING_GATE`，BUILD-000 和最终发布继续阻断；`SPARK-AUTH-FAIL-001` 的 P0 `FAIL` 不因本轮本地图谱修复改变。最终工作树快照为 tracked `24`、untracked `41`、total `65`；账本回归 `11/11`；验证器为 `metadata=11`、`blockers=24`、`evidence_refs=206`、`redaction_scan=PASS`；`git diff --check` 退出 `0`。T6 文档收尾完成，但 T4/T5 外部门禁继续开放。

## 130. 2026-07-28 BUILD-060 消息中心完整工作流构筑后 T0-T6 复审

### 130.1 运行身份、实现范围和安全边界

本轮产品构筑运行号为 `BUILD-060-NOTIFICATION-CENTER-20260728-46`，attempt `5`，supersede `BUILD-060-ACTIVITY-LIFECYCLE-20260728-40`、`BUILD-060-ACTIVITY-20260726-21` 和 `BUILD-060-20260725-02` 的标准 BUILD-060 证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260728-47`，两者不得互相替代。

- `GET /api/notifications` 将分页下推到 SQLite `LIMIT/OFFSET`，页大小为 `1..100`、页码为 `1..1000000`；当前页、筛选总数和全局未读数使用同一读快照。
- 全局未读数独立于当前页和 `unread_only`；列表和写入按当前 `identity.course_id`、`course_all/course_students/course_teachers` 受众及用户 read marker 隔离，未知角色失败关闭。
- 通知发布、单条已读和全部已读使用 `BEGIN IMMEDIATE`，业务写入、审计和幂等响应缓存在同一事务内提交；相同键同语义重放原结果，不同课程、角色或请求语义复用键返回 `409`。
- 单条已读返回服务端权威 `unread_count`；全部已读返回 `marked_count/unread_count`。三类写入均记录 request ID；两个独立 `CourseStore` 共享 SQLite 的并发同键回归只能产生一次业务写入和一次审计。
- 前端启动数据和通知更新统一使用 Zustand 数据源；消息中心覆盖加载、空、错误、全部/未读筛选、分页、单条已读、全部已读、忙碌状态、顶栏未读提示和失败恢复。
- 前端请求序列忽略过期分页响应；预览切换筛选不得恢复旧未读记录；服务端写失败不得乐观清除行状态或顶栏未读数。
- 证据不得读取或记录 `.env.test.local` 的值，不得记录 API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据；本轮不修改 manifest、PDF hash/page_count、图谱基线或正式数据库。

标准证据位于 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `notification-center-revalidation-20260728-46.txt`。活动生命周期 `...40` 和此前 BUILD-060 专项证据继续保留为历史，不得删除或计入本轮浏览器结果。

### 130.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 范围、权限、安全和独立代码审查 | 审查课程/受众/用户隔离、未知角色、SQL 分页、全局未读数、CSRF、原子幂等、审计、前端状态源、过期响应、失败恢复、脱敏和回滚 | 双状态源、内存切页、非原子幂等和失败恢复证据缺口已修复；无剩余本地 P0/P1 产品缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；前端 hardening/container/UI；`npm run lint`；`npm run typecheck`；`npm run build` | 全部退出码 `0`；生产构建 `1857 modules`，无 chunk 警告 | `PASS` |
| T2 单元、组件、Store 和领域回归 | `PYTHONPATH=$PWD/agent-adapter python3 scripts/test_social_api.py`；Social 课程范围、Adapter `13/13`、Store `12/12`、活动/评测/资源/教师/管理员等 25 个脚本；`cd frontend && npm run test:all` | `SOCIAL_API_OK` 含 SQL 分页、独立未读数、原子及多实例幂等、审计；25 个脚本通过；Vitest `53/53` | `PASS` |
| T3 本地 API/OpenAPI 契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_ui_contract.py`；审查 `api-test-manifest.yaml` | Local OpenAPI `104 paths`、API 契约 `105 routes`、UI 契约通过；仅代表 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器消息工作流和完整 Mock | 先 `--list`；定向执行 `npm run test:e2e:mock -- --workers=1 --grep "teacher can publish notifications and student can paginate, persist and bulk-read them"`，再完整 Mock | 用例发现 Mock `40`；本地缓存恢复 uvicorn 后 API 启动成功，但健康检查连接回环返回 `EPERM`，审批服务 `503`；定向和完整流程均 `0` 条计数通过 | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | a11y/axe/smoke `--list` 与实际执行；`bash scripts/run_local_acceptance.sh`；真实 Moodle/三角色/API/审计/PDF/辅助技术/Docker/HTTPS/恢复 | 发现 a11y `3`、axe `4`、smoke `2`；实际 webServer/回环阻断；完整验收缺 `chapter-1-1.1-.pdf` 退出 `2` | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对唯一 run ID、attempt、supersede、六类证据、专项证据、命令退出码、工作树、敏感值扫描、finding 和回滚边界 | 当前标准证据绑定运行 `...46`；计划审查绑定 `...47`；外部和浏览器门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 130.3 逐项验收条件

- 列表合同：合法请求返回 `items/total/page/page_size/unread_count`；页面最多 `100` 条，极端页码和非法页大小必须为 `422`，不得触发全表序列化或 500。
- 一致性：`total` 反映当前筛选，`unread_count` 反映当前课程和受众全部可见通知；跨分页切换、单条已读和全部已读后两者必须保持语义一致。
- 权限和隔离：学生只看 `course_all/course_students`，教师和管理员只看 `course_all/course_teachers`；跨课程、隐藏受众和其他用户 read marker 不得泄漏，单条隐藏通知写入返回 `404`，未知角色失败关闭。
- CSRF 和幂等：三类写请求必须携带有效会话防重放令牌及 `Idempotency-Key`；缺键为 `422`，同键不同语义为 `409`。同键并发时业务、审计和响应缓存必须原子，不能通过线程内锁假装多实例安全。
- 审计：发布、单条已读和全部已读各记录动作、当前课程、对象、结果和 request ID；相同键重放不得追加第二条业务审计。
- 前端：消息页必须有加载、空、错误、刷新、筛选、分页、单条/全部已读和忙碌状态；顶栏未读提示同步更新，布局不因数量或状态切换位移。
- 恢复：过期分页响应不得覆盖新筛选；单条或全部已读失败必须显示服务端错误并保持未读状态、按钮可重试和顶栏计数，不得显示假成功。
- 浏览器阈值：定向命令必须恰好 `1 passed`，完整 Mock 必须全部通过；`0` 条命中、用例选择前阻断、仅 `--list` 成功或历史通过都不能记为 T4 PASS。
- 本地边界：ASGI、SQLite、jsdom、Mock、Local OpenAPI 和本地构建不能替代真实 Moodle 多课程/三角色、正式 API/OpenAPI/审计、课程 PDF、正式 Workflow、完整 axe、人工辅助技术、Docker/HTTPS 或恢复演练。

### 130.4 失败分类、重测和回滚规则

- 跨课程/受众/用户泄漏、未知角色可读、CSRF 绕过、同键重复发布/审计、未读数错误、写失败显示成功或敏感值泄漏属于 P0/P1 产品失败；修复后从 T0 重跑 T1-T6。
- 只修改分页 SQL、索引、read marker、通知幂等/审计、API DTO、前端全局状态或消息交互时，也必须重跑 Social API、多实例并发、Adapter/Store、Vitest、API/OpenAPI 和适用浏览器层，不能只跑一个组件测试。
- 直接执行 `scripts.test_*` 文件导致包导入失败分类为 `PLAN_COMMAND_FAILURE`；规范入口为 `python3 -m unittest -q scripts.test_verify_course_data scripts.test_refresh_progress_snapshot scripts.test_validate_project_progress`，直接入口失败不得冒充产品失败或通过。
- 缺 `uvicorn` 可在获得批准后安装锁定依赖；本轮本地缓存恢复不等于项目依赖验收。回环 `EPERM`、webServer 健康检查失败和审批 `503` 分类为 `BLOCKED_TEST_INFRA`，不得通过替代端口、绕过审批或复制历史结果关闭。
- 缺 PDF、正式 Moodle/API/三角色/审计、正式 Workflow、完整辅助技术、Docker/HTTPS、恢复和提交材料分类为 `BLOCKED_INPUT` 或既有外部 blocker；不得生成占位 PDF、伪造角色/课程或修改 manifest/hash/page_count。
- 回滚仅限本轮通知 SQL/索引、原子幂等入口、API DTO、消息中心状态和测试/证据；不得删除通知/read marker/audit/idempotency 历史数据或活动生命周期专项证据。回滚后生成新 run ID 并从 T0 重测。

### 130.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260728-47）

计划审查确认产品运行 `...46` 与计划运行 `...47` 身份分离；精确 Playwright 选择器与实际用例标题一致，定向阈值为恰好 `1 passed`，用例发现不能替代执行。T0-T6 已覆盖 SQL 分页快照、全局未读数、课程/受众/用户隔离、未知角色、CSRF、三类原子幂等、多实例并发、request ID 审计、全局前端状态、竞态和失败恢复。

本轮没有把本地缓存恢复依赖写成浏览器通过，也没有把审批 `503`、回环 `EPERM`、缺失 PDF、真实 Moodle/API/角色/审计、正式 Workflow、完整辅助技术、Docker/HTTPS 或恢复门禁降级。`BUILD060-NOTIFICATION-003` 在 local-isolated 范围关闭；`BUILD060-BROWSER-INFRA-001`、`DATA-INPUT-001`、`SPARK-AUTH-FAIL-001` 和正式外部门禁继续开放。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。BUILD-060 继续 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。最终工作树快照为 tracked `24`、untracked `41`、total `65`；账本回归 `13/13`；验证器为 `metadata=11`、`blockers=24`、`evidence_refs=211`、`redaction_scan=PASS`；API 契约 `105 routes` 和 `git diff --check` 退出 `0`。机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260728-47.txt`。

## 131. 2026-07-29 BUILD-060 课堂签到完整工作流构筑后 T0-T6 复审

### 131.1 运行身份、实现范围和安全边界

本轮产品构筑运行号为 `BUILD-060-CHECKIN-20260729-48`，attempt `6`，supersede `BUILD-060-NOTIFICATION-CENTER-20260728-46`、`BUILD-060-ACTIVITY-LIFECYCLE-20260728-40`、`BUILD-060-ACTIVITY-20260726-21` 和 `BUILD-060-20260725-02` 的标准 BUILD-060 证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260729-49`，两者不得互相替代。

- 活动类型扩展为 `poll/survey/checkin`；签到复用 `draft -> published -> closed -> published` 生命周期，由服务端固定为单次响应，不接受调用方自定义选项或多次尝试。
- 旧 SQLite 数据卷若仍有只允许 `poll/survey` 的 `activities.kind` CHECK 约束，则在单一事务内重建表、复制全部历史活动和响应、恢复索引，并在提交前执行 `PRAGMA foreign_key_check`。不得清空历史数据规避迁移。
- 学生签到使用 `BEGIN IMMEDIATE`；签到响应、request ID 审计和幂等响应缓存原子提交。同键同语义重放原结果，不同键重复签到或同键改变语义均拒绝。
- 两个独立 `CourseStore` 共享同一 SQLite 文件时，同一学生并发签到只能生成一条响应。线程内锁或单实例结果不能代替该验收。
- 学生结果不得包含参与者列表；教师/管理员只可读取伪匿名 `user_ref` 和签到时间，不返回真实姓名、联系方式或其他身份字段。
- 教师端支持创建和发布签到；学生端只显示一键签到，不暴露内部 `present` 哨兵选项，刷新后以服务端状态保持已签到；教师结果页显示人数和伪匿名记录。
- 本轮不实现抢答、随机选人和分组任务，不把签到通过解释为全部课堂事件完成。证据不得读取或记录 `.env.test.local` 的值、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

标准证据为 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `checkin-revalidation-20260729-48.txt`。此前通知中心、活动生命周期和活动管理专项证据只保留为历史，不计入本轮浏览器结果。

### 131.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 范围、迁移、权限、隐私和代码审查 | 审查旧库 CHECK 迁移、历史数据保留、生命周期、固定单次规则、课程/角色隔离、参与者隐私、原子幂等、request ID 审计、索引和回滚 | 迁移保留旧投票及响应，`foreign_key_check` 无违规；学生无参与者列表，教师仅见伪匿名记录；无剩余本地 P0/P1 签到缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；前端 hardening/container/UI；`npm run lint`；`npm run typecheck`；`npm run build` | 全部退出码 `0`；生产构建 `1857 modules`，无 chunk 警告；容器契约 `4/4` | `PASS` |
| T2 API、迁移、并发、单元和组件回归 | `PYTHONPATH=$PWD/agent-adapter python3 scripts/test_activity_api.py`；Store、Adapter、24 个非回环后端领域脚本；`cd frontend && npm run test:all -- --run` | Activity API 含签到、隐私、多实例竞争、生命周期、课程范围、幂等和审计；Store `13/13`、Adapter `13/13`、后端 `24/24`、Vitest `55/55` | `PASS` |
| T3 本地 API/OpenAPI 契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_ui_contract.py`；审查 `api-test-manifest.yaml` | Local OpenAPI `104 paths`、API 契约 `105 routes`、UI 契约通过；签到复用既有活动路由，路由数不变，仅证明 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器签到流程和完整 Mock | 先执行四类 `--list`；定向执行 `--grep "teacher can publish a check-in and inspect a persisted student attendance record"`，再执行完整 Mock | 发现 Mock `41`、a11y `3`、axe `4`、smoke `2`；定向和完整 Mock 在用例选择前失败，`.last-run.json` 为 `failed` 且 `failedTests=[]`；审批服务 `503` | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | 实际执行 a11y、axe、smoke、`bash scripts/run_local_acceptance.sh`；复核真实 Moodle 花名册/三角色/API/审计/PDF/辅助技术/Docker/HTTPS/恢复 | axe 同样在选择前失败，a11y/smoke webServer 退出 `1`；完整验收缺 `chapter-1-1.1-.pdf` 退出 `2`；正式输入未提供 | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对唯一 run ID、attempt、supersede、六类标准证据、专项证据、命令退出码、工作树、敏感值扫描、开放 finding、重测和回滚边界 | 标准证据绑定产品运行 `...48`，计划证据绑定审查运行 `...49`；浏览器和正式门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 131.3 逐项验收条件

- 迁移：旧表必须真实包含仅允许 `poll/survey` 的 CHECK 约束、至少一个历史活动和响应；迁移后原 ID、类型、状态、选项和响应保持一致，可创建/发布/提交 `checkin`，`PRAGMA foreign_key_check` 返回空集合，活动查询索引存在。
- 服务端规则：`checkin` 的选项和 `max_attempts` 由服务端固定；自定义选项、次数不为 `1`、教师代签、学生创建或迁移活动、草稿/关闭态签到、跨课程读取或写入必须拒绝。学生成功签到后 `can_respond=false`、`next_attempt=null`。
- 生命周期：草稿只对教师/管理员可见，发布后学生可见，关闭后禁止签到，重新开放不允许已签到学生再次提交；列表、详情、响应和结果均以当前 `identity.course_id` 为范围。
- 幂等和并发：同一用户、endpoint、key 和语义重放原响应且不追加第二条审计；同键改变语义返回 `409`。两个独立 Store 对同一学生并发签到后数据库必须恰好一条响应，不得出现重复参与人数。
- 隐私：学生签到结果不得出现 `participants` 或任何其他学生标识；教师/管理员记录字段限定为伪匿名 `user_ref` 和 `submitted_at`。测试正文、日志和证据不得使用真实花名册或真实学生数据。
- 前端：创建请求不得发送内部签到选项；学生只看到稳定尺寸的一键签到控件，提交中防重复，失败可重试，成功及刷新后保持完成态；教师显示人数、伪匿名记录和签到时间，长标识不得溢出或遮挡。
- 浏览器阈值：定向用例必须恰好 `1 passed`，完整 Mock 当前应为 `41/41`，a11y `3/3`、axe `4/4`、smoke `2/2`；`--list`、API 子进程启动、`failedTests=[]` 或历史结果都不能计为通过。
- 正式边界：本地 SQLite、ASGI、jsdom、Mock、Local OpenAPI 和构建结果不能替代真实 Moodle 花名册与三角色、正式 API/OpenAPI/审计、多课程、课程 PDF、正式 Workflow、人工键盘/屏幕阅读器、六视口、Docker/HTTPS、恢复演练或最终发布。

### 131.4 失败分类、重测和回滚规则

- 历史活动/响应丢失、外键违规、跨课程/角色越权、学生看到参与者标识、教师看到真实身份字段、关闭态可签到、重复响应/审计、前端假成功或敏感值泄漏属于 P0/P1 产品失败；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改活动 schema、迁移、签到规则、隐私 DTO、原子事务或索引时，必须重跑旧库迁移、Activity API、两个 Store 多实例竞争、Store/Adapter、后端领域回归、API/OpenAPI、Vitest 和适用浏览器层，不能只运行新增 happy path。
- 回环连接受限、webServer 退出、Playwright 在选择前结束或审批服务 `503` 分类为 `BLOCKED_TEST_INFRA`；环境恢复后使用新产品 run ID 重跑定向 `1/1`、完整 Mock `41/41`、a11y `3/3`、axe `4/4`、smoke `2/2` 和 T6，不得绕过审批或复制历史结果。
- 缺课程 PDF、正式 Moodle/API/角色/花名册/审计、正式 Workflow、完整辅助技术、Docker/HTTPS、恢复和提交材料归入 `BLOCKED_INPUT` 或既有外部 blocker；不得生成占位 PDF、伪造花名册/角色或修改 manifest/hash/page_count。
- 回滚只限 `checkin` 类型、约束迁移、签到响应/结果 DTO、前端签到流程和相关测试/证据。数据库已有签到行时不得直接恢复只允许 `poll/survey` 的旧约束；必须停止写入、生成可验证备份并保留签到档案。回滚后生成新 run ID，从 T0 重新验收。

### 131.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260729-49）

计划审查确认产品运行 `...48` 与计划运行 `...49` 身份分离；六类标准证据和签到专项证据均绑定 `BUILD-060-CHECKIN-20260729-48`。`api-test-manifest.yaml` 的活动条目已更新为当前签到、迁移、隐私和多实例竞争范围；签到复用既有活动端点，因此 API 契约仍为 `105 routes`、Local OpenAPI 仍为 `104 paths`，没有用路由数量不变否认 DTO 和数据库约束变更。

本轮浏览器只有用例发现，没有可计数通过结果；定向、完整 Mock 和 axe 均在选择前失败，a11y/smoke webServer 退出，审批服务返回 `503`。这些结果保持 `BLOCKED_TEST_INFRA`。完整本地验收缺课程 PDF 退出 `2`，保持 `BLOCKED_INPUT`。历史浏览器 PASS、本地 API 通过和 `.last-run.json` 的空失败列表均未被用来关闭 T4/T5。

首轮 `scripts/validate_project_progress.py` 发现 BUILD-060 `test-output.txt` 已记录逐命令 `exit=...` 和退出摘要，但缺少验证器要求的字面标签 `exit code`，因此退出 `1`。`PLAN-EVIDENCE-004` 已将末行规范为 `Exit code summary`；该修正只提高机器可读性，不改变任何命令结果，修正后必须重新运行完整账本回归和验证器，首轮失败不得删除或写成首次通过。

`BUILD060-CHECKIN-004` 在 local-isolated 范围关闭；`BUILD060-CLASSROOM-EVENTS-002` 新增为开放产品项，明确抢答、随机选人和分组任务尚未实现。`BUILD060-BROWSER-INFRA-001`、`DATA-INPUT-001`、`SPARK-AUTH-FAIL-001` 和正式外部门禁继续开放。BUILD-060 保持 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。最终工作树快照为 tracked `24`、untracked `41`、total `65`；账本回归 `13/13`；验证器为 `metadata=11`、`blockers=25`、`evidence_refs=216`、`redaction_scan=PASS`；API 契约 `105 routes`，YAML 结构、`git diff --check`、残留进程和端口检查通过。3 个只读子代理均在初始化阶段因 `429` 失败，已全部关闭且未产生文件修改。机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-49.txt`。

## 132. 2026-07-29 BUILD-060 课堂抢答完整工作流构筑后 T0-T6 复审

### 132.1 运行身份、实现范围和安全边界

本轮产品构筑运行号为 `BUILD-060-QUICK-RESPONSE-20260729-50`，attempt `7`，supersede `BUILD-060-CHECKIN-20260729-48` 及此前 BUILD-060 标准证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260729-51`，两者不得互相替代。

- 活动类型扩展为 `poll/survey/checkin/quick_response`；教师/管理员可保存抢答草稿或直接发布，抢答固定为一个内部 `claim` 响应和一次尝试，调用方不能自定义选项或次数。
- 第一名学生通过 SQLite `BEGIN IMMEDIATE` 获得写锁。胜出响应、活动自动关闭、`activity.respond`、`activity.quick_response.win` 和幂等响应缓存同一事务提交；任一步失败必须整体回滚。
- 后续学生返回 `409 quick_response_already_claimed`；胜出学生使用相同用户、endpoint、key 和语义重放时必须返回原响应，不增加响应或审计。同键改变语义必须返回幂等冲突。
- 已产生胜出者的抢答为终态，不允许重新开放；教师手动关闭但尚无响应的抢答可以重新开放。前端只能在服务端 `can_reopen=true` 时显示重开动作。
- 学生详情、结果和冲突响应不得包含胜出者身份；教师/管理员参与记录字段严格限定为 `user_ref` 和 `submitted_at`，不返回真实姓名、联系方式或其他身份属性。
- 旧 `poll/survey` 和已有 `checkin` 两类 SQLite CHECK 约束都必须升级；迁移保留历史 ID、状态、时间、响应、显式索引和触发器，并在提交前执行 `PRAGMA foreign_key_check`。发现孤儿引用时必须回滚到旧表。
- 前端明确区分 `won/lost/uncertain`。POST `201` 是权威胜出结果，后续 GET 失败不得撤销；请求网络结果不明时禁止直接重发，先使用“确认抢答结果”恢复 won/lost/open；双击只能产生一个 POST。
- 本轮不实现随机选人和分组任务。证据不得读取或记录 `.env.test.local` 的值、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

标准证据为 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `quick-response-revalidation-20260729-50.txt`。签到、通知中心和活动生命周期专项证据只作为历史保留，不计入本轮浏览器结果。

### 132.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 状态机、迁移、事务、权限和隐私审查 | 审查两类旧库迁移、首位锁语义、自动关闭、两条审计、幂等重放、终态、角色/课程范围、DTO 隐私、网络歧义和回滚 | 迁移保留历史及依赖对象并在外键违规时回滚；抢答事务与终态、隐私和前端不确定状态均有正负向断言；无剩余本地 P0/P1 抢答缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | Python compile、Shell、UI/硬化/容器契约、lint、typecheck、build、最终 `git diff --check` | 已执行项目静态与契约命令并退出 `0`；生产构建 `1857 modules`、无 chunk 警告；最终 diff 由计划审查签核 | `PASS` |
| T2 API、迁移、并发、故障回滚、单元和组件 | Activity API、Store、Adapter、24 个非回环领域脚本、抢答竞态重复、定向和全量 Vitest | Store `16/16`、Adapter `13/13`、后端 `24/24`、Activity API 稳定重复 `8/8`、定向 `61/61`、Vitest `67/67` | `PASS` |
| T3 本地 API/OpenAPI 契约 | 生成 Local OpenAPI，执行 API/UI 契约并审查 manifest | Local OpenAPI `104 paths`、API 契约 `105 routes`、UI 契约通过；抢答复用既有路由但修改 DTO 和 SQLite 约束，只证明 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器抢答流程和完整 Mock | 四类 `--list`；定向执行精确抢答标题；完整 Mock | 发现 Mock `42`、a11y `3`、axe `4`、smoke `2`；定向和完整 Mock 在选择前等待 webServer 超时，定向 `.last-run.json` 为 `failed/failedTests=[]`；审批服务 `503` | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | 实际执行 a11y、axe、smoke、完整本地验收；复核真实 Moodle/三角色/API/审计/PDF/辅助技术/Docker/HTTPS/恢复 | axe 选择前超时，a11y/smoke webServer 退出 `1`；完整验收缺 `chapter-1-1.1-.pdf` 退出 `2`；正式输入未提供 | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对 run ID、attempt、supersede、六类标准证据、专项证据、命令退出码、工作树、脱敏、开放 finding、子代理/进程清理和回滚边界 | 产品证据绑定 `...50`，计划证据绑定 `...51`；浏览器、随机选人/分组和正式门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 132.3 逐项验收条件

- 迁移：必须分别从只允许 `poll/survey` 和允许 `poll/survey/checkin` 的真实旧表启动；迁移后历史活动、响应和时间一致，显式索引/触发器仍存在，`quick_response` 可创建。带孤儿响应的旧库必须在提交前报 `activity_kind_migration_foreign_key_failure`，旧表和数据保持原状。
- 服务端配置：抢答创建请求不得接受自定义选项或 `max_attempts != 1`；草稿对学生不可见，只有学生可以抢答，教师/管理员不能代答，列表、详情、响应和结果必须以当前 `identity.course_id` 为范围。
- 并发：两个不同学生通过 API 和两个独立 Store 同时抢答时，数据库必须恰好一条响应和一名胜出者，活动必须为 `closed`；胜出请求为 `201`，失败请求为专用 `409`，不得依赖单进程 Python 锁证明。
- 原子回滚：在胜出审计处注入异常后，响应数、活动状态、响应审计、胜出审计和幂等缓存都必须保持未写入；解除异常后相同业务请求可成功提交。
- 幂等：胜出者同键同语义重放必须返回同一响应且状态码为重放语义，不追加第二条审计；同键改变答案或 attempt 必须冲突。失败者不得通过新 key 覆盖现有胜出。
- 终态：有胜出响应时 `can_reopen=false`，直接重开 API 拒绝，教师 DOM 无“重新开放”；无响应的手动关闭抢答可重开。
- 隐私：任何学生列表、详情、结果、409 正文和 DOM 都不得出现其他学生的 `user_ref`；教师/管理员参与记录必须恰好包含 `user_ref/submitted_at` 两个字段。测试和证据只使用合成标识。
- 前端：教师创建请求不发送 `claim`；学生提交固定 `["claim"]` 及 CSRF/幂等头。POST 成功后 GET 失败仍显示已胜出；409 立即进入失败终态；未知网络结果显示确认操作并禁止再次抢答；确认必须覆盖 won/lost/open；双击只能发送一个 POST。
- 浏览器阈值：定向用例必须恰好 `1 passed`，完整 Mock 为 `42/42`，a11y `3/3`、axe `4/4`、smoke `2/2`；`--list`、API 子进程启动、`failedTests=[]` 或历史结果都不能计为通过。
- 正式边界：本地 SQLite、ASGI、jsdom、Mock、Local OpenAPI 和构建结果不能替代真实 Moodle 花名册与三角色、正式 API/OpenAPI/审计、多课程、课程 PDF、正式 Workflow、人工键盘/屏幕阅读器、六视口、Docker/HTTPS、恢复演练或最终发布。

### 132.4 失败分类、重测和回滚规则

- 产生两个胜出响应、活动未原子关闭、失败后残留响应/审计/幂等记录、胜出后可重开、跨课程/角色越权、学生身份泄漏、POST 成功被 GET 失败撤销、网络歧义直接重发或双击多 POST 属于 P0/P1 产品失败；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改活动 schema、迁移、抢答事务、终态、隐私 DTO 或前端确认逻辑时，必须重跑两类迁移、外键故障、Activity API、两个 Store 竞争、故障注入、Store/Adapter、24 个领域脚本、API/OpenAPI、Vitest 和适用浏览器层，不能只运行 happy path。
- webServer 就绪超时、回环受限、Playwright 在选择前结束或审批服务 `503` 分类为 `BLOCKED_TEST_INFRA`；环境恢复后使用新 run ID 重跑定向 `1/1`、完整 Mock `42/42`、a11y `3/3`、axe `4/4`、smoke `2/2` 和 T6，不得绕过审批或复制历史结果。
- 缺课程 PDF、正式 Moodle/API/角色/花名册/审计、正式 Workflow、完整辅助技术、Docker/HTTPS、恢复和提交材料归入 `BLOCKED_INPUT` 或既有外部 blocker；不得生成占位 PDF、伪造花名册/角色或修改 manifest/hash/page_count。
- 回滚只限 `quick_response` 类型、约束迁移、响应/自动关闭/结果 DTO、前端抢答流程和相关测试/证据。数据库已有抢答行时不得直接恢复旧约束或删除胜出记录；必须停止写入、生成可验证备份并保留活动、响应和审计档案。回滚后生成新 run ID，从 T0 重新验收。

### 132.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260729-51）

计划审查确认产品运行 `...50` 与计划运行 `...51` 身份分离；六类标准证据和抢答专项证据均绑定 `BUILD-060-QUICK-RESPONSE-20260729-50`。活动复用既有端点，因此 API 契约仍为 `105 routes`、Local OpenAPI 仍为 `104 paths`；这不否认新增 kind、DTO、迁移和事务行为。

本轮只有浏览器用例发现，没有可计数通过结果；定向抢答、完整 Mock 和 axe 均在选择前失败，a11y/smoke webServer 退出，审批服务返回 `503`。这些结果保持 `BLOCKED_TEST_INFRA`。完整本地验收缺课程 PDF 退出 `2`，保持 `BLOCKED_INPUT`。历史浏览器 PASS、本地 API 通过和空 `failedTests` 均未被用来关闭 T4/T5。

`BUILD060-QUICK-RESPONSE-005` 在 local-isolated 范围关闭；`BUILD060-CLASSROOM-EVENTS-002` 继续开放，但范围缩小为随机选人和分组任务。浏览器、课程资料、Spark 鉴权、真实 Moodle/API/Workflow、辅助技术、Docker/HTTPS、恢复和提交材料门禁继续开放。BUILD-060 保持 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。

最终工作树快照为 tracked `24`、untracked `41`、total `65`；账本回归 `13/13`；验证器为 `metadata=11`、`blockers=25`、`evidence_refs=221`、`redaction_scan=PASS`；YAML 为 `test_runs=115`、`known_blockers=25`、`manifest tests=15`；API 契约 `105 routes` 和 `git diff --check` 退出 `0`。本轮两个成功子代理和一个 `429` 失败子代理均已关闭，三个 ID 均不可再找到；无 Uvicorn/Vite/Playwright 遗留进程或目标端口监听。机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-51.txt`。

## 133. 2026-07-29 BUILD-060 随机选人与分组任务完整工作流构筑后 T0-T6 复审

### 133.1 运行身份、实现范围和安全边界

本轮产品构筑运行号为 `BUILD-060-RANDOM-GROUP-20260729-52`，attempt `8`，supersede `BUILD-060-QUICK-RESPONSE-20260729-50` 及此前 BUILD-060 标准证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260729-53`，两者不得互相替代。

- 活动类型扩展为 `poll/survey/checkin/quick_response/random_selection/group_task`；SQLite 新增 `random_selection_results`、`group_task_revisions` 和 `group_task_members`，旧活动 kind 约束升级到六类且保留历史数据和依赖对象。
- 课堂花名册只读取 `_load_admin_directory()` 经 `_admin_user_rows()` 规范化后当前 `identity.course_id` 的 active student。原始 Moodle ID 必须先经 `stable_uid()` 转换，响应和证据不得出现原始 ID。
- 目录未配置时花名册返回 `configured=false`，抽取和分组返回 `503 classroom_roster_unavailable`；当前课程没有 active student 时返回 `409 classroom_roster_empty`。禁止生成演示学生、回退到其他课程或将教师/管理员加入花名册。
- 随机选人使用 `BEGIN IMMEDIATE`。同一 cycle 内当前有效花名册成员在全部被选中前不得重复；耗尽后开始新 cycle，全局 sequence 单调递增。结果持久化 cycle、sequence、伪匿名引用、展示名、操作者和时间。
- 随机结果、`activity.random_select` request ID 审计和幂等响应缓存必须同事务提交。同用户、endpoint、key 和语义重放原结果；两个独立 Store 并发写入也必须序列化，不能依赖线程内锁。
- 分组任务以活动 options 作为固定组 ID/名称，至少两组且 active student 数不得少于组数。每个 revision 中花名册成员必须恰好出现一次，任意两组人数差不超过一。
- 每次生成创建新的不可变 revision；revision、全部 member 行、`activity.groups.generate` 审计和幂等缓存同事务提交。教师/管理员可回读历史 revision，学生始终读取最新 revision 的本人小组。
- 关闭态随机选人和分组生成均拒绝；重新开放后延续原 cycle、sequence 和 revision，不能清空或重编号历史来制造新活动。
- 学生随机选人响应字段限定为最新展示名、时间和 `is_me`，不返回 `user_ref`、cycle 或历史；学生分组响应只含本人组和队友展示名/`is_me`，不返回其他组、revision 列表或任何伪匿名引用。教师/管理员只获得伪匿名引用，不获得 Moodle 原始 ID、联系方式或其他身份属性。
- 前端增加两类活动创建入口、花名册就绪/未配置状态、教师抽取与生成、历史/当前结果、学生隐私视图、加载/空/错误/关闭态、CSRF、幂等键和请求锁。学生 DOM 不得渲染内部引用或其他组。
- 证据只允许记录状态、命令、退出码、计数、时间和脱敏错误分类；不得读取或记录 `.env.test.local` 的值、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

标准证据为 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `random-group-revalidation-20260729-52.txt`。此前抢答、签到、通知中心和活动生命周期专项证据只保留为历史，不计入本轮浏览器结果。

### 133.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 schema、花名册、权限、隐私和代码审查 | 审查六类 kind 迁移、三张结果表/索引、当前课程 active student 过滤、稳定引用、未配置零写入、随机周期、分组不变量、事务/审计/幂等、生命周期、DTO 白名单和回滚 | 旧约束扩展、课程/状态过滤、零造数、周期/均衡/revision、学生字段白名单和两 Store 序列化均有正负回归；无剩余本地 P0/P1 课堂事件缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；`git diff --check`；UI/hardening/container；`npm run lint`；`npm run typecheck`；`npm run build` | 全部退出码 `0`；生产构建 `1857 modules`，主 chunk 未越过警告线；容器契约 `4/4` | `PASS` |
| T2 Store、API、并发、单元和组件回归 | `python3 -m unittest -q scripts.test_course_store`；`python3 scripts/test_classroom_events_api.py` 并行隔离 `8` 次；Activity API、Adapter 和 25 个非回环后端脚本；定向 client/App；Vitest 全量 | Classroom API 含花名册、周期、均衡、revision、原子幂等、审计、隐私和课程范围，稳定性 `8/8`；Store `20/20`、Adapter `13/13`、定向 `65/65`、Vitest `71/71` | `PASS` |
| T3 本地 API/OpenAPI 契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_ui_contract.py`；审查 `api-test-manifest.yaml` | Local OpenAPI `109 paths`、API 契约 `110 routes`、UI 契约通过；只代表 local-isolated Adapter，不代表正式 Moodle | `OBSERVED_PASS` |
| T4 浏览器课堂事件流程和完整 Mock | 四类 `--list`；定向执行 `--grep "random selection and group tasks preserve roster privacy across teacher and student views"`；再执行完整 Mock | 发现 Mock `43`、a11y `3`、axe `4`、smoke `2`；定向和完整 Mock 因系统 Python 缺 `uvicorn` 在选择前退出；锁定依赖安装受 DNS 和审批 `503` 阻断，计数通过为 `0` | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | 实际执行 a11y、axe、smoke、`bash scripts/run_local_acceptance.sh`；复核真实 Moodle 花名册/三角色/API/审计/PDF/辅助技术/Docker/HTTPS/恢复 | axe 同样在选择前失败，a11y/smoke webServer 退出 `1`；完整验收缺 `chapter-1-1.1-.pdf` 退出 `2`；正式输入未提供 | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对唯一 run ID、attempt、supersede、六类标准证据、专项证据、API 快照、退出码、工作树、脱敏、开放 finding、子代理/进程清理和回滚边界 | 产品证据绑定 `...52`，计划证据绑定 `...53`；本地产品 finding 关闭，浏览器和正式 Moodle/课程资料门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 133.3 逐项验收条件

- schema：旧 `poll/survey`、`poll/survey/checkin` 和抢答时代约束都必须升级到六类 kind；历史活动、响应、时间、显式索引和触发器保持一致，`PRAGMA foreign_key_check` 无违规。三张新表必须有活动/revision 外键和查询索引。
- 花名册：教师和管理员返回集合必须恰好等于当前课程 active student；停用、未知状态、教师、管理员和其他课程成员均排除。每项字段恰好为 `user_ref/display_name`，原始目录 ID 不得出现在序列化响应。学生读取花名册返回 `403`。
- 不可用边界：未配置目录时教师界面显示明确不可用状态，两个生成端点返回 `503`，三张结果表和幂等/审计不得新增业务记录；空 active roster 返回 `409`。网络/目录错误不得触发合成花名册。
- 活动配置：`random_selection` options 必须由服务端固定为空且 `max_attempts=1`；`group_task` 必须至少两个 ID 唯一、名称非空的选项且 `max_attempts=1`。学生不能通过通用 response 端点代替教师抽取或分组。
- 随机周期：N 名有效学生的前 N 次抽取必须形成 cycle 1、sequence 1..N 且 N 个引用互异；第 N+1 次进入 cycle 2。关闭后写入返回 `409 activity_not_open`，重开后 sequence 连续且 cycle 2 内不得立即重复已抽成员。
- 随机原子性：并发同键请求必须得到 `201/200` 且响应完全相同，数据库只有一条结果和一条 request ID 审计；同键不同语义冲突。两个 Store 不同键并发应得到唯一 sequence 1/2 和两个不同成员。注入审计失败后结果、审计和幂等均为零，解除故障后可成功重试。
- 分组不变量：N 名学生、G 组必须产生 N 条 member，所有 `user_ref` 唯一且集合等于花名册；组数等于配置，`max(size)-min(size) <= 1`。N 小于 G 返回 `409 classroom_roster_too_small` 且零写入。
- revision 和原子性：首次/再次生成 revision 为 1/2，`available_revisions` 按新到旧保留且 revision 1 可回读。两个 Store 并发生成只允许连续 revision 1/2，每版都有 N 个成员。注入审计失败后 revision/member/审计/幂等全部回滚。
- 权限和课程：只有 teacher/admin 可生成；学生写入为 `403`。其他课程活动、花名册、随机历史和分组 revision 必须返回 `404` 或不出现在响应，错误正文不得泄漏对象或成员。未知角色失败关闭。
- 隐私：学生随机响应不得含 `user_ref/history/cycle/sequence`，只以 `is_me` 表示本人；学生分组响应不得含 `groups/available_revisions/user_ref`，只能看到 `my_group`。教师/管理员可以看到伪匿名引用但不得看到 Moodle 原始 ID、邮箱、手机号或其他身份字段。
- 前端：花名册加载、未配置、空、错误和就绪状态必须明确；抽取/生成按钮仅在 staff 且活动开放时可用。写请求包含 CSRF 和唯一幂等键，双击只发送一个 POST；失败保留可重试状态且不显示假结果。学生不显示教师按钮、历史、其他组或内部引用。
- 浏览器阈值：定向用例必须恰好 `1 passed`，完整 Mock 为 `43/43`，a11y `3/3`、axe `4/4`、smoke `2/2`；`--list`、API 子进程启动、选择前失败、空 `failedTests` 或历史结果都不能计为通过。
- 正式边界：本地目录 JSON、SQLite、ASGI、jsdom、Mock、Local OpenAPI 和构建不能替代真实 Moodle 花名册 bridge、三角色、正式 API/OpenAPI/审计、多课程、课程 PDF、正式 Workflow、人工键盘/屏幕阅读器、六视口、Docker/HTTPS、恢复演练或最终发布。

### 133.4 失败分类、重测和回滚规则

- 伪造花名册、跨课程成员进入结果、停用成员可参与、同 cycle 重复、分组漏人/重复/不均衡、并发重复 sequence/revision、事务失败留残记录、学生看到内部引用/其他组、关闭态可写、CSRF/幂等绕过或前端假成功属于 P0/P1 产品失败；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改 activity schema、目录规范化、稳定引用、随机算法、分组算法、事务/索引、DTO 或前端状态时，必须重跑旧库迁移、课堂事件 API、`8/8` 稳定性、两个 Store 并发、故障注入、Activity/Adapter/Store、25 个领域脚本、API/OpenAPI、Vitest 和适用浏览器层，不能只运行 happy path。
- 花名册源恢复或正式目录字段变化后，必须先验证状态/课程/角色映射和原始 ID 脱敏，再从 T0 重跑；不得把本地目录 JSON 的通过复制为正式 Moodle 通过。
- 缺 `uvicorn`、依赖安装 DNS 失败、webServer 退出、Playwright 在选择前结束、回环限制或审批服务 `503` 分类为 `BLOCKED_TEST_INFRA`；环境恢复后使用新 run ID 重跑定向 `1/1`、完整 Mock `43/43`、a11y `3/3`、axe `4/4`、smoke `2/2` 和 T6，不得绕过审批或复制历史结果。
- 缺课程 PDF、正式 Moodle/API/角色/花名册/审计、正式 Workflow、完整辅助技术、Docker/HTTPS、恢复和提交材料归入 `BLOCKED_INPUT` 或既有外部 blocker；不得生成占位 PDF、伪造角色/课程或修改 manifest/hash/page_count。
- 回滚只限两类 activity kind、新结果表、花名册读取、API DTO、前端课堂事件流程和相关测试/证据。已有结果时不得恢复旧 CHECK 约束、删除抽取/分组/审计历史或重编号 cycle/revision；必须停止写入、生成可验证备份并导出档案。回滚后生成新 run ID，从 T0 重新验收。

### 133.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260729-53）

计划审查确认产品运行 `...52` 与计划运行 `...53` 身份分离；六类标准证据、OpenAPI 快照和随机/分组专项证据均绑定 `BUILD-060-RANDOM-GROUP-20260729-52`。`api-test-manifest.yaml` 已增加独立课堂事件条目；新增五条路由后 API 契约为 `110 routes`、Local OpenAPI 为 `109 paths`。

本轮 Store `20/20`、Adapter `13/13`、课堂事件 API、既有活动 API、25 个非回环后端脚本、并行稳定性 `8/8`、定向前端 `65/65`、Vitest `71/71`、lint/typecheck/build、UI/硬化/容器和契约均通过或观察性通过。随机选人和分组任务的产品 finding `BUILD060-CLASSROOM-EVENTS-002` 只在 local-isolated 范围关闭，真实花名册/三角色/API/审计继续由 `BUILD060-REAL-001` 和正式门禁管理。

本轮浏览器只有用例发现，没有可计数通过结果；定向课堂事件、完整 Mock 和 axe 因系统 Python 缺 `uvicorn` 在选择前失败，a11y/smoke webServer 退出。锁定依赖安装受沙箱 DNS 阻断，所需沙箱外重试因审批服务 `503` 被拒绝，未绕过审批。完整本地验收缺课程 PDF 退出 `2`。因此 `BUILD060-BROWSER-INFRA-001`、`DATA-INPUT-001`、`SPARK-AUTH-FAIL-001` 和正式外部门禁继续开放。

3 个初始子代理因 `429` 未能执行，2 个替代子代理完成 API/前端复核；所有成功、失败子代理均已关闭。证据没有读取或记录密钥、签名 URL、Authorization、Cookie、完整问答或真实学生数据，也没有生成占位 PDF 或修改 manifest hash/page_count。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。BUILD-060 保持 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。最终工作树快照为 tracked `24`、untracked `42`、total `66`；账本回归 `13/13`；验证器为 `metadata=11`、`blockers=25`、`evidence_refs=226`、`redaction_scan=PASS`；YAML 为 `test_runs=117`、`known_blockers=25`、`manifest tests=16`；API 契约 `110 routes` 和 `git diff --check` 退出 `0`。无 Uvicorn/Vite/Playwright 遗留进程，目标端口通过 `/proc` 核对；机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-53.txt`。

## 134. 2026-07-29 BUILD-060 统一学生任务中心完整工作流构筑后 T0-T6 复审

### 134.1 运行身份、实现范围和安全边界

本轮产品构筑运行号为 `BUILD-060-TASK-CENTER-20260729-54`，attempt `9`，supersede `BUILD-060-RANDOM-GROUP-20260729-52` 及此前 BUILD-060 标准证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260729-55`，计划审查不得替代产品测试或共用产品 run ID。

- 新增学生专用 `GET /api/student/tasks`，只从当前 `identity.course_id` 聚合作业、考试、讨论和学生受众可见通知；teacher/admin 调用必须返回 `403`。
- 作业状态优先级为已提交 `completed`、到期未提交 `expired`、存在本人草稿 `in_progress`、其余 `pending`。其他用户草稿/提交不得影响当前学生。
- 考试状态优先级为已提交 `completed`、关闭时间已到 `expired`、存在本人进行中尝试或草稿 `in_progress`、其余 `pending`。时间由服务端按 UTC 比较，客户端不得提交状态或当前时间。
- 讨论由本人创建主题或本人可见回复判为 `completed`；未参与且主题关闭判为 `expired`，其余可见主题为 `pending`。`pending_review` 等学生不可见状态不得进入任务中心。
- 通知沿用学生受众白名单；本人已读记录判为 `completed`，未读为 `pending`。其他用户的已读状态不得影响当前学生，教师受众和其他课程通知不得进入列表或计数。
- API 只接受空值或四种 `kind`、四种 `status`，页码为 `1..1000000`，页大小为 `1..100`；非法输入必须返回 `422`，不得静默回退。
- 四类/四状态计数在类型和状态筛选前、同一数据库读取事务快照内计算；筛选后再稳定排序和分页。`total` 表示当前筛选结果，不得与全局计数混用。
- DTO 字段白名单为 `id/source_id/kind/title/summary/status/due_at/updated_at/progress`。不得返回 `user_uid/author_uid/answers/score/audience/created_by` 或真实学生资料；摘要规范空白并限制长度。
- 前端增加严格 DTO normalization、四类/四状态服务端筛选、分页、真实刷新、加载/错误/空态、重试、四类详情导航和请求序号保护。慢请求不得覆盖更新后的筛选结果。
- 预览模式必须首帧提供四种任务且不短暂显示空态；侧栏不得用作业数冒充全部任务数。生产拆包应保持主 chunk 不触发 Vite 体积警告。
- 证据只允许状态、命令、退出码、计数、时间、构建大小和脱敏错误分类；不得读取或记录 `.env.test.local` 的值、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

标准证据为 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `task-center-revalidation-20260729-54.txt`。随机分组、抢答、签到、通知中心和活动生命周期专项证据继续保留为历史，不计入本轮浏览器结果。

### 134.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 数据源、状态、权限、隐私和代码审查 | 审查四类 SQL、状态优先级、UTC 截止边界、当前 UID/课程/受众过滤、快照、计数、排序、分页、DTO 白名单、前端请求竞争和回滚 | 四类状态与课程/用户隔离均有正负向断言；非法筛选/页码失败关闭；无剩余本地 P0/P1 任务中心缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | `python3 -m compileall -q agent-adapter scripts`；`bash -n scripts/*.sh`；UI/hardening/container；`npm run lint`；`npm run typecheck`；`npm run build`；最终 `git diff --check` | 静态、类型、硬化和构建命令退出 `0`；容器契约 `4/4`；构建 `1857 modules`，主应用 chunk `436.99 kB` 且无体积警告 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | `python3 scripts/test_task_center_api.py`；Store `20`；Adapter `13`；26 个数据输入无关非回环脚本；定向 client/App；Vitest 全量 | Task API 覆盖四类、用户状态、截止、筛选、分页、计数、排序、隐私、课程和角色；初次定向 `69/70` 暴露预览空态闪烁，修复后 `71/71`；全量 `77/77`；其余均退出 `0` | `PASS` |
| T3 本地 API/OpenAPI 契约 | `python3 scripts/generate_local_openapi.py`；`python3 scripts/test_api_contract.py`；`python3 scripts/test_ui_contract.py`；审查 `api-test-manifest.yaml` | Local OpenAPI `110 paths`、API 契约 `111 routes`、UI 契约通过；manifest 新增 `TASK-CENTER-LOCAL-001`，只代表 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器任务中心流程和完整 Mock | 四类 `--list`；定向执行 `--grep "unified task center filters four task kinds and performs a real refresh"`；再执行完整 Mock | 发现 Mock `44`、a11y `3`、axe `4`、smoke `2`；定向和完整 Mock 因系统 Python 缺 `uvicorn` 在选例前退出，当前浏览器计数通过为 `0` | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | 实际执行 a11y、axe、smoke、`bash scripts/run_local_acceptance.sh` 和数据相关 KB 生命周期；复核真实 Moodle/三角色/API/审计/PDF/辅助技术/Docker/HTTPS/恢复 | axe 在选择前失败，a11y/smoke webServer 退出 `1`；完整验收和 KB 生命周期均缺 `chapter-1-1.1-.pdf` 退出 `2`；正式输入未提供 | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对唯一 run ID、attempt、supersede、六类标准证据、专项证据、OpenAPI、退出码、初次失败与修复、工作树、脱敏、开放 finding、子代理/进程清理和回滚边界 | 产品证据绑定 `...54`，计划证据绑定 `...55`；初次 `69/70` 未删除，浏览器和正式 Moodle/课程资料门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 134.3 逐项验收条件

- 四类完整性：夹具中当前课程四类可见对象的集合、类型计数和总数必须精确匹配；隐藏讨论、教师通知和其他课程对象不得出现在 items、total 或 counts。
- 作业状态：当前学生已提交优先于截止；截止优先于草稿；仅当前学生草稿可进入 `in_progress`。已提交任务进度必须为 `100`，未完成任务不得伪造完成分数。
- 考试状态：当前学生提交优先于关闭；关闭优先于草稿/尝试；仅当前学生状态可影响结果。服务端必须拒绝无时区的内部测试时间，正式路径使用 UTC 当前时间。
- 讨论和通知：本人创建或可见回复完成讨论；关闭且未参与为过期。通知已读按 `(notification_id,user_uid)` 读取，学生受众集合必须失败关闭；未知角色不能通过受众函数扩大可见范围。
- 权限和课程：student 只能读取本人当前课程；teacher/admin 读取学生任务接口为 `403`；其他课程每一种对象均不得泄漏。错误正文不得暴露对象标题、正文或用户信息。
- 快照、排序和计数：四类读取必须在同一事务快照完成；计数在筛选前计算且恰好包含四类/四状态键。筛选后未完成项先于完成项，截止或更新时间和 ID 形成稳定顺序；同一请求分页不得重复或漏项。
- 输入边界：未知 kind/status、页码 `0`、超大页码、页大小 `0` 或 `>100` 必须返回 `422`；客户端只发送经过白名单和边界规范化的查询参数。
- DTO 隐私：每行必须恰好可映射到受控 `StudentTask` 字段；未知 kind/status、缺失计数、非整数分页、空必填字符串、非字符串时间或 `progress <0/>100` 必须由客户端拒绝，不能被强制转换成看似有效状态。
- 前端筛选：四种类型按钮和四种状态 tab 必须产生新的服务端请求并把页码重置为 1；刷新保留当前筛选且请求数增加 1；筛选结果、总数和分页文案与服务端响应一致。
- 前端状态：加载期间不显示旧数据为新结果；错误态有 `role=alert` 和重试，不能同时显示空态；空结果明确显示无任务；慢的旧筛选响应不能覆盖后返回的新筛选。
- 导航：assignment 到作业详情、exam 到考试详情、discussion 到讨论详情、notification 到消息中心定位参数；路径中的来源 ID 必须 URL 编码。过期/完成项只提供查看语义。
- 预览和响应式：预览首帧包含四种任务且无空态闪烁；最长标题/摘要、筛选控件、分页和操作按钮在移动/桌面布局不得溢出或相互遮挡。真实浏览器未执行前该项不能标记正式 PASS。
- 浏览器阈值：定向用例必须恰好 `1 passed`，完整 Mock 为 `44/44`，a11y `3/3`、axe `4/4`、smoke `2/2`；`--list`、webServer 启动、选择前失败、历史结果或空失败列表均不能计为通过。
- 正式边界：本地 SQLite、ASGI、jsdom、Mock、Local OpenAPI 和构建不能替代真实 Moodle 三角色、正式状态映射/API/OpenAPI/审计、多课程、课程 PDF、正式 Workflow、人工键盘/屏幕阅读器、六视口、Docker/HTTPS、恢复演练或最终发布。

### 134.4 失败分类、重测和回滚规则

- 跨课程对象、其他用户草稿/提交/已读影响本人、teacher/admin 越权、隐藏讨论或错误受众通知泄漏、服务端截止优先级错误、客户端可伪造状态、DTO 泄漏答卷/成绩/用户字段或前端把错误显示为空态，属于 P0/P1 产品失败；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改任务来源 SQL、状态优先级、时间解析、受众、快照/排序/分页、DTO、筛选、刷新、导航或请求竞争逻辑时，必须重跑任务中心 API、Store/Adapter、26 个数据输入无关后端脚本、API/OpenAPI、定向和全量 Vitest、lint/typecheck/build 及适用浏览器层，不能只运行新增 happy path。
- 测试第一次失败后必须记录原因、修复和权威重跑结果；不得删除 `69/70`、只记录最终 `71/71`，也不得把修复测试本身描述为产品功能通过。
- 缺 `uvicorn`、webServer 退出、Playwright 在选例前结束、回环限制、依赖网络或审批服务异常归为 `BLOCKED_TEST_INFRA`；环境恢复后用新 run ID 重跑定向 `1/1`、完整 Mock `44/44`、a11y `3/3`、axe `4/4`、smoke `2/2` 和 T6，不得绕过审批或复制历史结果。
- 缺课程 PDF、正式 Moodle/API/角色/审计、正式 Workflow、完整辅助技术、Docker/HTTPS、恢复和提交材料归入 `BLOCKED_INPUT` 或既有外部 blocker；不得生成占位 PDF、伪造状态/角色/课程或修改 manifest hash/page_count。
- 回滚只限只读任务中心 Store 投影、API 路由、DTO/client、页面筛选/分页/刷新、侧栏徽标、拆包配置和相关测试/证据。本轮无 schema 迁移，不得删除现有草稿、提交、尝试、讨论、通知已读或审计数据。
- 部署回滚应先恢复不依赖 `/api/student/tasks` 的前端，再下线路由；回滚页面必须明确只展示作业，不能保留“四类统一任务中心”文案。回滚后使用新 run ID，从 T0 重新验收并保留历史证据。

### 134.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260729-55）

计划审查确认产品运行 `...54` 与计划运行 `...55` 身份分离；六类标准证据、Local OpenAPI 和任务中心专项证据均绑定 `BUILD-060-TASK-CENTER-20260729-54`。`api-test-manifest.yaml` 新增独立任务中心条目；新增一个路由后 API 契约为 `111 routes`、Local OpenAPI 为 `110 paths`。

本轮 Task API、Store `20/20`、Adapter `13/13`、26 个数据输入无关后端脚本、修复后定向前端 `71/71`、Vitest `77/77`、lint/typecheck/build、UI/硬化/容器和契约均通过或观察性通过。初次 `69/70` 的预览空态闪烁已保留并归类为 `REPAIRED_TEST_FAILURE`。`BUILD060-TASK-CENTER-006` 只在 local-isolated 范围关闭。

浏览器只有用例发现，没有可计数通过结果；定向任务中心、完整 Mock 和 axe 因系统 Python 缺 `uvicorn` 在选例前失败，a11y/smoke webServer 退出。完整本地验收及单独 KB 生命周期均因课程 PDF 缺失退出 `2`。因此 `BUILD060-BROWSER-INFRA-001`、`DATA-INPUT-001`、`SPARK-AUTH-FAIL-001` 和真实 Moodle/API/审计等正式门禁继续开放。

本轮未启动新子代理；此前成功、失败或已完成的子代理均保持关闭。证据未读取或记录密钥、签名 URL、Authorization、Cookie、完整问答或真实学生数据，也未生成占位 PDF 或修改 manifest hash/page_count。

计划审查结论为 `DOCUMENTED_AND_REVIEWED_WITH_EXTERNAL_GATES_OPEN`。BUILD-060 保持 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。最终工作树快照为 tracked `24`、untracked `43`、total `67`；账本回归 `13/13`；验证器为 `metadata=11`、`blockers=26`、`evidence_refs=231`、`redaction_scan=PASS`；YAML 为 `test_runs=119`、`known_blockers=26`、`manifest tests=17`；API 契约 `111 routes` 和 `git diff --check` 退出 `0`。无 Uvicorn/Vite/Playwright 遗留进程，Mock/axe/a11y/smoke 目标端口通过 `/proc` 核对无监听；本轮未启动新子代理，当前子代理并发为零。机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-55.txt`。

## 135. 2026-07-29 BUILD-060 通知任务深链接定位构筑后 T0-T6 复审

### 135.1 运行身份、实现范围和安全边界

本轮产品构筑运行号为 `BUILD-060-NOTIFICATION-DEEP-LINK-20260729-56`，attempt `10`，supersede `BUILD-060-TASK-CENTER-20260729-54` 及此前 BUILD-060 标准证据。计划审查运行号为 `PLAN-TEST-AUDIT-20260729-57`，两者不得互相替代。

- 第 134 节任务中心已为通知任务生成 `/messages?notice=<source_id>`，但消息中心此前没有读取 `notice`，因此原“notification 到消息中心定位参数”验收只证明了 URL 生成，没有形成定位闭环。
- `GET /api/notifications` 增加可选 `focus_id`。服务端必须先应用当前 `identity.course_id`、当前角色受众白名单和当前筛选，再在同一读取事务中定位；禁止先按 ID 查全局对象再检查权限。
- 通知页权威顺序保持 `created_at DESC, id ASC`。目标可见时，服务端按该精确顺序计算前置行数并返回目标所在页；目标必须实际包含在返回 `items` 中。
- `focus_id` 为空时保持普通分页兼容；非空时限长 `200`，只允许 `[A-Za-z0-9._:-]`。非法字符或超长输入返回 `422`，不得静默忽略。
- 定位结果只允许 `focus_found` 和找到时的 `focused_id`。不存在、其他课程、当前角色不可见受众必须返回相同 `focus_found=false/focused_id=null`，不得返回对象标题、正文、受众、创建者或差异化错误原因。
- 前端消息中心读取 `notice` 后强制使用“全部”视图，将 ID 作为 `focus_id` 发送，并接受服务端返回页码；不得只在当前内存页查找或依赖客户端估算页码。
- 成功定位必须有明确状态、高亮和 `aria-current=true`；不可见或不存在显示统一“该通知不存在或当前账号不可查看”。筛选切换和手动翻页应清除定位参数，避免旧 URL 持续覆盖用户操作。
- 定位是只读操作，不得自动插入 `notification_reads`、发送单条已读 PUT 或改变全局未读数。已读状态仍由用户主动点击和既有幂等写接口控制。
- 组件测试必须在每例前重置会话、预览和数据 Store，避免用例数量或顺序改变通知已读结果。该隔离只属于测试基础设施，不得改写生产状态语义。
- 证据只允许状态、命令、退出码、计数、构建大小和脱敏错误分类；不得读取或记录 `.env.test.local` 的值、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

标准证据为 `acceptance/frontend/BUILD-060/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `notification-deep-link-revalidation-20260729-56.txt`。任务中心 `...54`、随机分组 `...52` 及更早专项证据继续保留为历史，不能替代本轮浏览器结果。

### 135.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 顺序、权限、隐私、只读和代码审查 | 审查可见范围先过滤、排序/页码一致性、同事务读取、ID 边界、未找到同形响应、不自动已读、URL/筛选生命周期和回滚 | 可见跨页、隐藏受众、跨课程、缺失对象、非法输入、成功/失败 UI 和 no-auto-read 均有正负向断言；无剩余本地 P0/P1 深链接缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | Python compile、Shell、UI/hardening/container、lint、typecheck、build、最终 `git diff --check` | 首次 typecheck 因启动回退 DTO 缺两个新增字段退出 `1`；修复后全部退出 `0`。构建 `1857 modules`、主 chunk `438.21 kB`，无体积警告 | `PASS` |
| T2 API、Store、单元、组件和领域回归 | Social API、Task API、Store `20`、Adapter `13`、26 个数据输入无关非回环脚本、定向 client/App、Vitest 全量及稳定性复跑 | 首次全量 `78/79` 暴露共享预览 Store 测试污染；进一步收紧不一致 focus DTO 和生效筛选边界后，定向 `74/74`、全量连续两次 `80/80`；后端 `26/26`、Store `20/20`、Adapter `13/13` | `PASS` |
| T3 本地 API/OpenAPI 契约 | 生成 Local OpenAPI，执行 API/UI 契约并审查 `api-test-manifest.yaml` | Local OpenAPI `110 paths`、API 契约 `111 routes`、UI 契约通过；新增一个查询参数和 manifest 专项条目，不新增路由 | `OBSERVED_PASS` |
| T4 浏览器深链接流程和完整 Mock | 四类 `--list`；定向 `--grep "task-center notification deep link locates the requested visible notice"`；完整 Mock | 发现 Mock `45`、a11y `3`、axe `4`、smoke `2`；定向与完整 Mock 因系统 Python 缺 `uvicorn` 在选例前退出，浏览器计数通过为 `0` | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | 实际执行 a11y、axe、smoke、完整本地验收和 KB 生命周期；复核真实 Moodle/三角色/API/审计/PDF/辅助技术/Docker/HTTPS/恢复 | axe 在选例前阻断，a11y/smoke webServer 退出 `1`；完整验收与 KB 生命周期缺 `chapter-1-1.1-.pdf` 退出 `2`；正式输入未提供 | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对 run ID、attempt、supersede、六类证据、专项证据、初次失败、OpenAPI、工作树、脱敏、finding、子代理/进程清理和回滚 | 产品证据绑定 `...56`，计划证据预留 `...57`；浏览器、课程资料和正式 Moodle 门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 135.3 逐项验收条件

- 可见目标定位：至少准备两页学生可见通知；以第一页为请求页、第二页对象为 `focus_id`，响应 `page` 必须切到第二页，`focus_found=true`、`focused_id` 精确匹配且 `items` 包含目标。
- 排序一致：同一时间通知必须按 ID 升序打破平局；页码计算和最终 SELECT 必须使用完全相同的排序。修改任一 ORDER BY 时必须补同时间边界回归。
- 课程与受众：学生可定位 `course_all/course_students`，教师/管理员可定位 `course_all/course_teachers`；其他课程、错误受众和未知角色都不得扩大范围。
- 不泄漏：用同一请求页分别查询教师通知、其他课程通知和不存在 ID，三类必须都返回 `focus_found=false/focused_id=null`，且 items/page/total/unread_count 的可见结果一致。
- 输入边界：空 focus 保持旧分页；空格、斜线、控制字符、超过 200 字符和无法满足 ID 格式的值必须返回 `422`。错误正文不得回显输入值。
- 事务与状态：定位、总数、页数据和未读数必须在一个读取事务中得到；定位前后 `notification_reads`、审计和幂等缓存行数不变，未读数不因定位下降。
- 客户端契约：非空 focus 必须 URL 编码并作为 `focus_id` 发送；snake/camel 两种结果字段规范为 boolean 和 nullable ID。只有严格 boolean `true`、合法非空 focused ID 且目标实际存在于返回页才算成功；缺失、不一致或字符串布尔值按未定位处理，不能把请求 ID 自行当成已找到。
- 页面初始化：带 `notice` 进入时必须选中“全部”，即使此前状态为未读筛选；采用服务端返回页码，慢的旧请求不得覆盖较新的 URL 或筛选。
- 成功 UI：目标行必须可由稳定 ID 找到，具有高亮与 `aria-current=true`；目标已读时仍可定位但不得重新启用已读写，目标未读时保持可点击且不会自动 PUT。
- 失败 UI：未找到只显示统一文案，不渲染对象存在性、课程、受众或权限原因；列表仍可展示普通当前页，用户可以继续筛选/分页。
- 导航退出：点击筛选或上一页/下一页时删除 `notice`，随后按用户选择加载；刷新按钮保留定位，用于重新确认目标。不得产生 URL/state 无限循环。
- 测试隔离：每个 App 组件用例必须从空 session/data/preview/sidebar 状态开始；新增或重排用例后全量结果仍需稳定，不能依赖单文件定向结果。
- 浏览器阈值：定向用例必须恰好 `1 passed`，完整 Mock `45/45`、a11y `3/3`、axe `4/4`、smoke `2/2`；`--list`、`failedTests=[]`、选例前退出或历史通过均不能计为 PASS。
- 正式边界：本地 SQLite、ASGI、jsdom、Mock 定义、Local OpenAPI 和构建结果不能替代真实 Moodle 课程/受众/三角色、正式 API/审计、课程 PDF、Workflow、人工辅助技术、六视口、Docker/HTTPS、恢复和最终发布。

### 135.4 失败分类、重测和回滚规则

- 跨课程或错误受众目标可定位、隐藏/缺失响应可区分、页码与排序不一致、定位自动标记已读、前端伪造 `focusFound`、旧请求覆盖新 URL 或出现无限加载，属于 P0/P1 产品失败；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改通知 ORDER BY、受众函数、课程过滤、focus ID 校验、页码 SQL、响应字段、客户端 normalization、URL 生命周期、高亮或已读交互时，必须重跑 Social API、Task API、Store/Adapter、26 个后端脚本、API/OpenAPI、定向和全量 Vitest、lint/typecheck/build 及适用浏览器层。
- 首次 typecheck `exit=1` 和首次全量 `78/79` 必须保留为 `REPAIRED_TYPE_CONTRACT_FAILURE`、`REPAIRED_TEST_ISOLATION_FAILURE`；只有修复并完成最终失败关闭审查后的 typecheck `0`、定向 `74/74` 和全量连续两次 `80/80` 可以作为权威本地结果。
- 缺 `uvicorn`、webServer 退出、选例前结束、回环限制、依赖网络或审批服务异常归为 `BLOCKED_TEST_INFRA`；环境恢复后用新 run ID 重跑深链接定向 `1/1`、完整 Mock `45/45`、a11y `3/3`、axe `4/4`、smoke `2/2` 和 T6。
- 缺课程 PDF、正式 Moodle/API/角色/审计、正式 Workflow、完整辅助技术、Docker/HTTPS、恢复和材料归入 `BLOCKED_INPUT` 或既有外部 blocker；不得生成占位 PDF、伪造通知/角色/课程或修改 manifest hash/page_count。
- 回滚只限通知 focus 查询参数、页码计算、定位 DTO、客户端/UI 定位状态、测试隔离和相关测试/证据；不得回滚统一任务中心、删除通知/已读/审计数据或覆盖历史专项证据。
- 部署回滚顺序为先将通知任务链接改回普通 `/messages`，再下线服务端 `focus_id`；回滚后生成新 run ID，从 T0 重验并保留本轮失败与修复历史。

### 135.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260729-57）

计划审查确认产品运行 `...56` 与计划运行 `...57` 身份分离；BUILD-060 六类标准证据、专项证据、Local OpenAPI 和 manifest 条目均绑定 `BUILD-060-NOTIFICATION-DEEP-LINK-20260729-56`。本轮只扩展既有通知路由查询参数，因此 API 契约仍为 `111 routes`、Local OpenAPI 仍为 `110 paths`。

服务端先应用课程、角色受众和可选未读筛选，再按与列表相同的 `created_at DESC, id ASC` 顺序计算页码。可见跨页定位、教师受众、其他课程、缺失 ID、非法输入和未读计数不变均有断言。客户端最终审查进一步要求 boolean `true`、返回页内 matching ID 才接受成功，避免字符串布尔或不一致 DTO 产生假高亮；消息中心采用生效筛选决定已读后的列表行为。

首次 typecheck 因启动回退 DTO 缺 `focusFound/focusedId` 退出 `1`，首次全量 Vitest `78/79` 暴露共享预览 Store 测试污染；两次失败均保留。修复并完成最终失败关闭审查后，定向 client/App `74/74`、全量 `80/80` 连续两次、26 个数据输入无关后端脚本、Store `20/20`、Adapter `13/13`、lint/typecheck/build、UI/硬化/容器和契约均通过或观察性通过。生产构建为 `1857 modules`，主 chunk `438.21 kB`，无体积警告。

浏览器只有 Mock `45`、a11y `3`、axe `4`、smoke `2` 的发现结果。深链接定向、完整 Mock 和 axe 因系统 Python 缺锁定环境的 `uvicorn` 在选例前失败，a11y/smoke webServer 退出；`.last-run.json` 的 `failedTests=[]` 不计为通过。诊断只找到版本不匹配且不稳定的第三方工具私有解释器，未接入项目、未安装依赖、未绕过审批。完整本地验收和 KB 生命周期均因缺 `chapter-1-1.1-.pdf` 退出 `2`。

两个诊断子代理均已停止并关闭，未修改文件或留下进程。证据未读取或记录密钥、签名 URL、Authorization、Cookie、完整问答或真实学生数据，也未生成占位 PDF 或修改 manifest hash/page_count。

`BUILD060-TASK-NOTICE-LINK-007` 只在 local-isolated 范围关闭；`BUILD060-BROWSER-INFRA-001`、`BUILD060-REAL-001`、`DATA-INPUT-001`、`SPARK-AUTH-FAIL-001` 和其他正式门禁继续开放。BUILD-060 保持 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。

最终工作树快照为 tracked `24`、untracked `43`、total `67`；账本回归 `13/13`；验证器为 `metadata=11`、`blockers=27`、`evidence_refs=236`、`redaction_scan=PASS`；YAML 为 `test_runs=121`、`known_blockers=27`、`manifest tests=18`；API 契约 `111 routes` 和 `git diff --check` 退出 `0`。YAML 计数首次命令因 f-string 转义产生 `SyntaxError`，已归类 `PLAN_COMMAND_FAILURE` 并改用参数化格式重跑通过，不计为产品失败。无 Uvicorn/Vite/Playwright 遗留进程或 Mock/axe/a11y/smoke 目标端口监听。机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-57.txt`。

## 136. 2026-07-29 BUILD-040 恢复最近学习位置构筑后 T0-T6 复审

### 136.1 运行身份、契约、隔离和安全边界

本轮产品构筑运行号为 `BUILD-040-RESUME-LEARNING-20260729-58`，attempt `3`，supersede `BUILD-040-20260725-02` 及 BUILD-040 收藏/页码笔记历史专项结果。计划审查运行号为 `PLAN-TEST-AUDIT-20260729-59`；产品运行和计划运行不得混用。

- 新增 `GET /api/student/learning-position`。接口只允许 `student`，使用已认证 `identity.uid` 和 `identity.course_id`，不接受客户端 user/course 查询参数；教师返回 `403`，未认证请求保持既有 `401` 边界。
- Store 必须先以 `user_uid` 和 `course_id` 限定范围，再联结章节和资源；只允许 `status=published`、`page_start>=1`、`page_end` 非空且保存页位于资源页界内的记录。其他用户、其他课程、`draft`、`archived` 和历史越界页不得成为候选。
- 最近位置的唯一权威顺序为 `updated_at DESC, resource_id ASC`；同一 `updated_at` 必须由资源 ID 升序稳定打破平局，查询必须 `LIMIT 1`。无候选项统一返回 `position=null`，不得返回 `404` 或合成默认资源。
- 响应资源必须经过 `public_resource()`，不得输出 `storage_path`、本地绝对路径、原始权限信息或其他内部字段。进度必须明确匹配同一 `resource_id`，并包含有效 `page`、`percent`、`completed`、`version`、`updated_at` 和 `has_saved_progress=true`。
- 前端仅在非预览、`role=student` 且 `session.courseId` 为正整数时调用私有接口。预览、教师、无课程或已失效会话不发请求，也不得用平台静态数据伪造“最近位置”。
- 客户端把服务端响应视为不可信输入：课程 ID、资源 ID、标题/文件名、chapter/page 范围、`published` 状态、`available` 与 `mount_status` 一致性、locator 安全性、进度资源 ID、百分比、版本、时间和已保存标志必须全部通过严格校验；任一不一致均失败关闭。
- 返回 `course_id` 必须等于当前 `session.courseId`。成功目标固定为 `/courses/:courseId/resources/:resourceId?page=N`，并分别编码课程和资源参数；不得导航到返回的 locator 或其他任意 URL。
- `ready` 资源显示“继续”，`pending_mount`/`unavailable` 显示“查看状态”；后两者仍进入受控阅读器状态页，但不得创建 iframe、伪造 PDF、合成页内容或绕过挂载状态。
- 加载中按钮禁用并声明 `aria-busy`，避免重复动作；错误显示可理解且可重试的状态，重试重新调用 API；`position=null` 回退当前课程；刷新或组件重新挂载必须重新读取服务端位置。
- 本轮证据只记录状态、命令、退出码、计数、构建大小和脱敏错误分类。不得读取或记录 `.env.test.local`、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

六类标准证据为 `acceptance/frontend/BUILD-040/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，API 补充证据为 `api-contract.json`，专项证据为 `resume-learning-revalidation-20260729-58.txt`。旧资源进度、收藏和页码笔记专项文件保留为历史，不得覆盖或冒充本轮浏览器结果。

### 136.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 范围、权限、排序、隐私和代码审查 | 审查 Store SQL、identity 范围、published/页界过滤、稳定排序、public_resource、严格客户端校验、会话条件、状态机、导航和回滚 | 跨用户/课程、草稿/归档、越界页、同时间排序、空态、教师 403、畸形 DTO、pending_mount 和无伪造 PDF 均有正负向断言；未发现剩余本地 P0/P1 恢复位置缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | Python compile、Shell、UI/hardening/container、lint、typecheck、build、git diff --check | 首次 lint 因控制字符正则触发 no-control-regex 退出 1；改为显式 ASCII 字符码检查后全部退出 0。构建 1857 modules、主 chunk 443.94 kB，无体积警告 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | Store、Adapter、26 个数据输入无关非回环脚本、资源进度/课程范围 API、定向 learning position/resume Vitest 和前端全量 | Store 20/20、Adapter 13/13、后端 26/26、RESOURCE_PROGRESS_API_OK、资源课程范围通过、定向 7/7、全量 88/88 | `PASS` |
| T3 本地 API/OpenAPI 契约 | 生成 Local OpenAPI，执行 API/UI 契约并审查 api-test-manifest.yaml 和 BUILD-040 api-contract.json | Local OpenAPI 111 paths、API 契约 112 routes、UI 契约通过、manifest 18 项；只证明 local-isolated Adapter | `OBSERVED_PASS` |
| T4 恢复学习浏览器和完整 Mock | 四类 --list；定向 grep dashboard restores the latest learning position；完整 Mock | 发现 Mock 46、a11y 3、axe 4、smoke 2；定向和完整 Mock 因系统 Python 缺 uvicorn 在选例前退出 1，本轮浏览器通过计数为 0 | `BLOCKED_TEST_INFRA` |
| T5 可访问性、安全和正式外部验收 | 实际运行 a11y、axe、smoke、KB 生命周期和完整本地验收；审查真实 Moodle/pluginfile/PDF/三角色/辅助技术/HTTPS/恢复 | axe 在选例前退出 1，a11y/smoke webServer 退出 1；KB 与完整验收缺 chapter-1-1.1-.pdf 退出 2；正式输入和人工证据未提供 | `BLOCKED_INPUT`，浏览器子项为 `BLOCKED_TEST_INFRA` |
| T6 证据、账本和门禁复审 | 核对 run ID、attempt、supersede、六类证据、专项证据、首次失败、OpenAPI、manifest、工作树、脱敏、finding、子代理/进程清理和回滚 | 产品证据绑定运行 58，计划证据绑定运行 59；浏览器、课程资料和正式 Moodle 门禁未改写为 PASS | `REVIEW_REQUIRED` |

### 136.3 精确验收条件

- 权限和身份：未认证为 `401`，教师/管理员为 `403`；学生请求不能指定或覆盖 `user_uid`/`course_id`。相同资源在其他用户下的更新不能影响当前用户选择。
- 课程隔离：当前课程只能返回该课程章节下的资源；切换隔离夹具到课程 2 时只返回课程 2 候选，切回课程 1 后不能沿用课程 2 位置。
- 资源可见性：`draft`、`archived`、缺 `page_end`、`page_start<1` 或保存页越界记录必须被跳过。合法 `pending_mount` 记录仍可作为最近位置，因为“文件未挂载”不等于“学习记录不存在”。
- 排序：较新 `updated_at` 必须胜出；时间相同时 `resource_id` 字典升序胜出。任何排序字段或 SQL 联结变化都必须补充同时间和跨课程回归。
- 空态和最小响应：无合法候选必须为 HTTP `200` 且 `position=null`。响应资源不得含 `storage_path`；公开 `mount_status`、`available` 和 locator 必须符合既有资源契约。
- 客户端信任：字符串数字/布尔、NaN/Infinity、零/负课程 ID、危险或控制字符 locator、非法资源 ID、非 published、available/mount_status 矛盾、不同 resource_id、越界页、`version<1`、无效时间或 `has_saved_progress` 非 true 均必须拒绝。
- 会话条件：预览和教师组件用例必须断言从未请求 `/api/student/learning-position`。有效学生会话初始化只能发起所需请求，慢的已卸载请求不得更新新组件。
- 页面状态：加载时必须有 `aria-live`/`aria-busy` 状态和防重复点击；API/校验错误不得伪装为空位置，必须显示错误并允许重新定位；只有 null 才显示“尚无已保存的学习位置”。
- 导航：ready 和 pending_mount 均使用当前课程、返回资源和保存页构建 canonical URL；ready 显示“继续”，pending_mount 显示“查看状态”。点击前不得提前改变服务端进度。
- 刷新恢复：保存进度后刷新工作台应重新请求并展示同一资源、页码和百分比；不得从 localStorage 或旧 React 状态冒充服务端恢复。
- 单元阈值：定向最近位置必须 `7/7`，完整 Vitest 必须 `88/88`；Store `20/20`、Adapter `13/13`、`26/26` 后端脚本、资源 API、lint/typecheck/build、UI/硬化/容器和契约均须退出 `0`。
- 浏览器恢复阈值：定向用例必须恰好 `1/1`，完整 Mock `46/46`、a11y `3/3`、axe `4/4`、smoke `2/2`；`--list`、`failedTests=[]`、选例前退出、历史结果或部分通过均不能记为本轮 PASS。
- 正式边界：只有真实 Moodle 学生/教师/管理员、正式 API/OpenAPI、manifest-matched PDF、pluginfile 权限、真实 PDF 页码恢复、完整辅助技术、六视口、Docker/HTTPS、备份恢复和提交材料均通过，才能关闭 BUILD-040 或最终发布。

### 136.4 失败分类、重测和回滚规则

- 跨用户/跨课程泄漏、教师可读、draft/archived/越界页被恢复、内部路径泄漏、客户端接受危险 locator、课程不匹配仍导航或伪造 PDF，属于 P0/P1 产品失败；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改 `resource_progress`/schema、`recent_learning_position` SQL、`identity.course_id` 传播、`public_resource`、学习位置 DTO、严格 normalization、会话条件、工作台状态、canonical URL 或阅读器页码解析时，必须重跑 Store/Adapter、26 个后端脚本、资源进度与课程范围 API、API/OpenAPI、定向和全量 Vitest、lint/typecheck/build 及适用浏览器层。
- 首次 lint exit 1 必须保留为 `REPAIRED_LINT_RULE_FAILURE`；只有改用显式字符码检查并完成最终 lint/typecheck/Vitest/build 后，才允许把 T1/T2 记为本地 PASS。不得删除失败记录或把 ESLint 规则关闭作为修复。
- 系统缺 uvicorn、webServer 退出、选例前结束、回环监听限制、依赖网络或审批异常归为 `BLOCKED_TEST_INFRA`。环境恢复后必须使用新 run ID 重跑定向 `1/1`、完整 Mock `46/46`、a11y `3/3`、axe `4/4`、smoke `2/2` 和 T6；不得复用历史浏览器证据。
- 缺课程 PDF、正式 Moodle/API/角色/pluginfile、Workflow、完整辅助技术、Docker/HTTPS、恢复或材料归为 `BLOCKED_INPUT`、`BLOCKED_DEPENDENCY` 或既有外部 blocker；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除工作台恢复 CTA/状态，再下线客户端 DTO/请求，最后下线只读学习位置 API/Store 查询；不得删除 resource_progress、收藏/笔记、审计或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 136.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260729-59）

计划审查确认运行 `58` 与运行 `59` 身份分离，BUILD-040 六类标准证据、API 补充证据、Local OpenAPI、manifest 条目和专项证据均可追溯到产品运行 `58`。接口新增一个 GET 路由，因此本地 API 契约从 `111` 增至 `112 routes`，Local OpenAPI 从 `110` 增至 `111 paths`；这些数字仍明确标记为 local-isolated。

服务端过滤顺序、稳定排序、空态、public_resource 和 current-user/current-course 隔离均有 API/Store 覆盖。客户端拒绝畸形或不一致响应，只在有效真实学生会话中加载，并将 pending_mount 作为状态页而非虚构 PDF。首次 no-control-regex lint 失败已保留，最终定向 `7/7`、全量 `88/88`、Store `20/20`、Adapter `13/13`、后端 `26/26`、lint/typecheck/build 和契约通过或观察性通过。

浏览器只有 Mock `46`、a11y `3`、axe `4`、smoke `2` 的发现结果；因系统 Python 缺 uvicorn 或 webServer 失败，可计数通过仍为 `0`。课程数据门禁仍因缺 `chapter-1-1.1-.pdf` 退出 `2`。两个已完成实现子代理均已关闭，复查返回 `not_found`；不得创建或保留无用子代理。

`BUILD040-RESUME-LEARNING-008` 只在 local-isolated Store/API/client/component 范围关闭；`BUILD040-BROWSER-INFRA-001`、`RESOURCE-PROGRESS-001`、`DATA-INPUT-001`、真实 Moodle/API/pluginfile、正式辅助技术、Docker/HTTPS、恢复和最终发布门禁继续开放。BUILD-040 保持 `IMPLEMENTED_PENDING_GATE`，BUILD-000 和最终发布继续阻断。

最终机器对账结果必须写入 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-59.txt` 和 `PROJECT_PROGRESS.yaml`；在账本回归、验证器、YAML 计数、API 契约、git diff、进程/端口和子代理清理全部复核前，T6 保持 `REVIEW_REQUIRED`。

最终对账已完成：账本回归 `13/13`；验证器为 `metadata=11`、`blockers=28`、`evidence_refs=241`、`redaction_scan=PASS`；YAML 为 `test_runs=123`、`known_blockers=28`、`manifest tests=18`；工作树 tracked `24`、untracked `43`、total `67`；API 契约 `112 routes`，`git diff --check` 退出 `0`。无 Uvicorn/Vite/Playwright 遗留进程，Mock/axe/a11y/smoke 端口 `4300/4301/4800/4801/4193/4194` 经 `/proc` 核对无监听；两个实现子代理复查均为 `not_found`。机器结果归档于 `acceptance/frontend/BUILD-000/plan-test-audit-20260729-59.txt`。T6 因浏览器、课程资料和正式外部门禁继续保持 `REVIEW_REQUIRED`。

## 137. 2026-08-06 BUILD-030 当前课程全局搜索正式编号与本地验证完成

### 137.1 运行身份、契约、隔离和安全边界

本轮产品构筑运行号为 `BUILD-030-GLOBAL-SEARCH-20260806-23`，attempt `23`，supersede 草稿 `global-search-unnumbered-draft-20260730-attempt-22.txt` 与既有权威图谱运行 `BUILD-030-GRAPH-INTERACTIVE-RETEST-20260728-44`。计划审查运行号为 `PLAN-TEST-AUDIT-20260806-60`；产品运行和计划运行不得混用。

- 搜索 API 保持当前身份、当前课程边界：`course/chapter/resource/assignment/exam/discussion/knowledge` 七类统一搜索，三角色显式可见性，归档课程七类结果全空，稳定排序、分页与筛选前分类计数，超大页码返回 422，客户端严格 DTO 与 stale-response 保护，canonical 路由。
- 交互式先修关系图继续保留在本构筑：20 节点 17 方向边、`prerequisite` 方向边高亮、双向课程范围过滤、URL 初始筛选与错误重试新请求。
- 2026-08-06 基线变更：本地 `course-data/normalized` 已挂载 20 份真实课程 PDF（439 页），`verify_course_data` PASS，`run_local_acceptance.sh` 完整通过。
- Mock 浏览器测试 2 个用例从“未挂载”断言更新为挂载后真实行为（工作台恢复位置“继续”、资源卡“打开资料”、阅读器“课程阅读器”+ `iframe.pdf-frame`）；无产品代码、API、DTO、排序、分页或路由语义变化。
- 真实工作流知识库发布（`REAL-KB-RELEASE-20260806-01`）与真实聊天 E2E（`REAL-CHAT-E2E-20260806`）保持 PARKED，不在本轮范围。
- 本轮证据只记录状态、命令、退出码、计数、构建大小和脱敏错误分类。不得读取或记录 `.env.test.local`、API Key、API Secret、签名 URL、Authorization、Cookie、完整问答或真实学生数据。

六类标准证据为 `acceptance/frontend/BUILD-030/metadata.json`、`scope.md`、`review.md`、`test-output.txt`、`manual-acceptance.md` 和 `rollback.md`，专项证据为 `global-search-20260806-attempt-23.txt`；attempt 1-22 专项文件保留为历史，不得覆盖或冒充本轮结果。

### 137.2 构筑后 T0-T6 测试矩阵

| 层级 | 必须执行的命令/审查 | 本轮实际结果 | 判定 |
|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 审查七类搜索范围、三角色可见性、归档隔离、分页/排序/计数、严格 DTO、stale-response、canonical 路由、图谱范围过滤与回滚 | 本地 20 份 PDF 基线挂载后完整复核，未发现剩余本地 P0/P1 搜索或图谱缺陷 | `PASS` |
| T1 静态、类型、构建和硬化 | compileall、Shell、UI/hardening/container、lint、typecheck、build | 全部退出 0；构建 1857 modules、index 450.94 kB、图谱懒加载 182.89 kB，无体积警告 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | Store、Adapter、KB release driver、资源进度/课程范围、全局搜索 API、前端全量 Vitest | Store 20/20、Adapter 15/15、KB driver 10/10、LOCAL_ACCEPTANCE_OK、Vitest 100/100 | `PASS` |
| T3 本地 API/OpenAPI 契约 | 生成 Local OpenAPI，执行 API/UI 契约并审查 api-test-manifest.yaml | Local OpenAPI 112 paths、API 契约 113 routes、GLOBAL_SEARCH_API_OK roles=3 kinds=7；只证明 local-isolated Adapter | `OBSERVED_PASS` |
| T4 浏览器流程与质量门禁 | Mock、a11y、axe、smoke、六视口截图（本机 chrome + /tmp/jbgs-agent-deps） | Mock 50/50、a11y 3/3、axe 4/4、smoke 2/2、screenshots 1/1（六视口） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 真实 Moodle 三角色/pluginfile、六视口人工辅助技术、真实工作流 KB、HTTPS/域名 | 外部输入未齐；KB 发布与聊天 E2E PARKED | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 专项证据统一 run_id；账本验证器、脱敏、git diff、进程/端口复核 | 验证器 `PROJECT_PROGRESS_VALIDATION_OK metadata=11 blockers=28 evidence_refs=241 redaction PASS`；正式门禁未齐 | `REVIEW_REQUIRED` |

### 137.3 逐项验收条件和失败重测

- 硬阈值：Vitest `100/100`、Store `20/20`、Adapter `15/15`、KB release driver `10/10`、API 契约 `113 routes`、Local OpenAPI `112 paths`、Mock `50/50`、a11y `3/3`、axe `4/4`、smoke `2/2`、六视口截图 `1/1`。
- 正式边界：真实 Moodle 学生/教师/管理员、正式 API/OpenAPI、pluginfile 权限、真实 PDF 页码、完整辅助技术、六视口人工、Docker/HTTPS、备份恢复、真实工作流知识库发布和提交材料全部通过后，才能关闭 BUILD-030 或最终发布。

### 137.4 失败分类、重测和回滚规则

- 角色/课程泄漏、归档结果可见、超范围分页、客户端接受畸形 DTO、canonical 路由错误或图谱跨课程边可见属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑 T1-T6。
- 修改搜索 Store/API/DTO、客户端归一化、SearchPage effect、canonical 路由或图谱范围过滤时，必须重跑 Store/Adapter、全局搜索 API、API/OpenAPI、定向和全量 Vitest、lint/typecheck/build 及适用浏览器层。
- 系统缺 uvicorn/httpx、webServer 退出、选例前结束、回环监听限制归为 `BLOCKED_TEST_INFRA`；环境恢复后必须使用新 run ID 重跑全套，不得复用历史浏览器证据。
- 缺正式 Moodle/API/角色/pluginfile、工作流引用标记、完整辅助技术、Docker/HTTPS、恢复或材料归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先恢复 mock-api.spec.ts 挂载前断言并重跑 50/50，再移除本轮六份标准证据与专项证据；不触碰产品代码、course-data、服务器 deploy/.env 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 137.5 本轮计划进一步审查（PLAN-TEST-AUDIT-20260806-60）

计划审查确认运行 `23` 与运行 `60` 身份分离，BUILD-030 六类标准证据、专项证据、Local OpenAPI、manifest 条目和账本均可追溯到产品运行 `23`。搜索 API 无新增路由（`113 routes` / `112 paths` 与部署容器一致），数字明确标记为 local-isolated 与服务器容器双路径一致。

本地 20 份 PDF 基线解除后，`run_local_acceptance.sh` 完整通过（KB release driver 10/10、performance p50=37.87ms），Mock 浏览器 2 个用例更新为挂载后行为并通过 50/50 全量回归。真实工作流知识库发布与真实聊天 E2E 保持 PARKED（需工作流配置引用标记）；`SPARK-AUTH-FAIL-001` 仍为开放 P0，不得由本地回归关闭。

BUILD-030 从 `PAUSED_UNNUMBERED_UNVERIFIED_DRAFT` 转为 `IMPLEMENTED_PENDING_GATE`；BUILD-000 保持 `BLOCKED_INPUT`（真实 Moodle 三角色/pluginfile、六视口人工辅助技术、HTTPS/域名、提交材料），最终发布继续 `blocked`。

最终机器对账结果写入 `acceptance/frontend/BUILD-000/plan-test-audit-20260806-60.txt` 和 `PROJECT_PROGRESS.yaml`；验证器 `metadata=11`、`blockers=28`、`evidence_refs=241`、`redaction_scan=PASS`。T6 因正式外部门禁继续保持 `REVIEW_REQUIRED`。

## 第 138 节 BUILD-110 PWA 离线阅读与跨设备同步（纯前端增量）

Run ID：`BUILD-110-PWA-OFFLINE-READING-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 138.1 范围

- Service Worker（`public/sw.js`）：`/api/` 请求永不缓存；导航 network-first + index.html 回退；静态资源 cache-first；PDF locator `/local/course_agent/` cache-first；`CACHE_PDF` 消息主动缓存。
- IndexedDB 离线存储（`src/offline/offlineStore.ts`）：progress/annotations/ops，内存回退 + 订阅通知。
- 离线同步队列（`src/offline/syncQueue.ts`）：progress/favorite/note-save/note-delete；同 key 合并、网络错误停止、冲突丢弃、逐操作幂等键。
- 在线状态 Hook（`useOnlineStatus.ts`）、PWA 辅助（`pwa.ts`，仅 PROD 非 preview/mock 注册）、离线横幅（`OfflineBanner.tsx`，恢复在线自动同步一次，手动重试）。
- `ResourceReaderPage` 离线回退与缓存按钮；`manifest.webmanifest`、`icon.svg`、`index.html` 注入。
- 测试：`offlineStore.test.ts` 5、`syncQueue.test.ts` 12、`OfflineBanner.test.tsx` 4、`pwa.test.ts` 6。

### 138.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 离线数据按资源隔离、API 永不缓存、SW 仅 PROD 注册、幂等与冲突语义 | 代码审查 + 单测 | 无新增跨资源/凭据泄露路径；`/api/` 不入缓存 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建 1862 modules，dist 含 sw.js/manifest/icon.svg | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 127/127（原 100 + 新增 27） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | Mock/a11y/axe/smoke/截图 | 本轮只读增量未重跑 | 下一轮本地全量回归执行 | `NOT_RUN` |
| T5 质量、可访问性和真实环境 | HTTPS 下真实 SW 注册、离线访问、跨设备同步、真实辅助技术 | 外部输入未齐 | 正式域名/人工验收未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-110/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 138.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 dist 含 `sw.js`/`manifest.webmanifest`/`icon.svg`、Vitest 全量 `127/127`、离线模块 `27/27`、`git diff --check` 通过。
- 正式边界（T5）：HTTPS/正式域名下的真实 SW 注册与离线访问、至少两台真实设备跨设备同步、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-110 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 138.4 失败分类、重测和回滚规则

- 离线数据跨资源泄漏、`/api/` 被缓存、SW 在 preview/mock 注册、同步乱序/重复上报、凭据落盘属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `offlineStore`/`syncQueue`/`OfflineBanner`/`sw.js`/`App.tsx` 离线路径时，必须重跑离线模块 27/27、全量 Vitest、lint/typecheck/build，并按需执行浏览器层。
- 缺 HTTPS 域名、真实设备、辅助技术、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先停用 SW 与离线入口并清除站点数据，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 138.5 本轮计划进一步审查

本增量确认“真实 API 未配置部分”已在文件中标记并移到下一项：所有真实 API 依赖项保持在 `PROJECT_PROGRESS.yaml` 的 `parked_items`/`open_release_gates`，本增量不伪造、不绕过；BUILD-110 只完成纯前端离线阅读与同步队列，并作为 P2 增强列表中唯一可继续开发项推进。

下一项开发候选：P2 其余纯前端项（如可访问性细节、性能优化、PWA 安装提示/更新提示），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 139 节 BUILD-111 PWA 安装提示与更新提示（纯前端增量）

Run ID：`BUILD-111-PWA-PROMPTS-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 139.1 范围

- 安装提示 Hook（`src/offline/usePwaInstallPrompt.ts`）：捕获 `beforeinstallprompt`（先 `preventDefault` 再保存）、`install()` 在用户手势中调用 `prompt()` 并等待 `userChoice`、`appinstalled` 后隐藏；导出 `BeforeInstallPromptEvent` 类型。
- 提示组件（`src/offline/pwaPrompts.tsx`）：`InstallPromptButton` 仅可安装时渲染“安装应用”按钮；`UpdatePromptBanner` 显示“发现新版本”横幅，按钮默认 `window.location.reload()`（可注入 `onRefresh`）。
- SW 更新监听（`src/offline/pwa.ts`）：`watchServiceWorkerUpdates` 监听 `updatefound` + worker `statechange`，仅当新 worker 达到 `installed` 且存在 `navigator.serviceWorker.controller` 时通知（首次安装不打扰）；`registerServiceWorker(onUpdateReady)` 支持回调。
- 状态接线：`useAppStore` 新增 `pwaUpdateReady`/`setPwaUpdateReady`（纯布尔，不存 SW 对象）；`main.tsx` 注册 SW 时写入；`App.tsx` 顶栏挂载安装按钮、内容区挂载更新横幅；`styles.css` 新增样式。
- 测试：`pwa.test.ts` 新增 3 个更新监听用例（update 检查、有 controller 才通知、首次安装不通知）；新增 `pwaPrompts.test.tsx` 7 个用例（hook 捕获/安装/隐藏、按钮渲染与点击、横幅渲染与刷新）。

### 139.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 安装/更新提示不越权、不落盘凭据、首次安装不打扰 | 代码审查 + 单测 | 无新增跨资源/凭据泄露路径；提示仅存布尔状态 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建 1864 modules，dist 含 sw.js/manifest/icon.svg | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 137/137（原 127 + 新增 10；offline 模块 37/37） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | Mock/a11y/axe/smoke/截图 | 本轮只读增量未重跑 | 下一轮本地全量回归执行 | `NOT_RUN` |
| T5 质量、可访问性和真实环境 | HTTPS 下真实安装弹窗、SW 更新推送、跨设备、真实辅助技术 | 外部输入未齐 | 正式域名/人工验收未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-111/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 139.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 dist 含 `sw.js`/`manifest.webmanifest`/`icon.svg`、Vitest 全量 `137/137`、offline 模块 `37/37`、`git diff --check` 通过。
- 正式边界（T5）：HTTPS/正式域名下的真实安装弹窗与 SW 更新推送、至少两台真实设备跨设备安装/更新、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-111 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 139.4 失败分类、重测和回滚规则

- 无用户手势自动弹安装框、首次安装误报更新、提示内出现会话/凭据内容、`sw.js` 缓存策略被改、更新提示循环触发属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `usePwaInstallPrompt`/`pwaPrompts`/`watchServiceWorkerUpdates`/`App.tsx` 提示挂载点时，必须重跑 `pwaPrompts` 7/7、`pwa` 9/9、全量 Vitest、lint/typecheck/build，并按需执行浏览器层。
- 缺 HTTPS 域名、真实设备、辅助技术、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除安装/更新提示挂载点并清除浏览器 SW 状态，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 139.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-111 完成 PWA 安装/更新提示（纯前端），并已部署到 `139.196.45.2` 的 `/learn/` 前端验证静态资源可达。

下一项开发候选：P2 其余纯前端项（如可访问性细节、性能优化），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 140 节 BUILD-112 键盘可达性与焦点管理硬化（纯前端增量）

Run ID：`BUILD-112-KEYBOARD-A11Y-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 140.1 范围

- 跳转链接（WCAG 2.4.1）：`App.tsx` AppShell 顶部 `.skip-link`（“跳到主内容”，`href="#main-content"`），默认移出视口、`:focus-visible` 时显示；`<main>` 增加 `id="main-content"` 与 `tabIndex={-1}`。
- 搜索快捷键 Hook `src/a11y/shortcuts.ts`（`useSearchShortcut`）：非表单控件、无修饰键时按 `/` 聚焦并全选全局搜索；搜索框聚焦时按 `Escape` 清空并失焦（搜索页回无参数 `/search`）；输入中不劫持按键。
- 用户菜单键盘闭环：`Escape` 关闭菜单并归还焦点到触发按钮；菜单项点击同样归还焦点。
- reduced-motion：`styles.css` 新增 `@media (prefers-reduced-motion: reduce)`，压缩动画/过渡时长、`scroll-behavior: auto` 并禁用 `.spin`。
- 浏览器层：`tests/a11y.spec.ts` 新增第 4 用例（跳转链接隐藏/聚焦/跳转、`/` 聚焦、`Escape` 清空、reduced-motion 规则存在）。
- 测试：`shortcuts.test.tsx` 7、`App.test.tsx` 新增 3（跳转链接、菜单 Esc/焦点返回、搜索快捷键）。

### 140.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 跳转链接、快捷键边界、焦点归还、无凭据落盘 | 代码审查 + 单测 | 无新增网络/凭据路径；快捷键只操作焦点与输入框 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建 1865 modules，dist 含 sw.js/manifest/icon.svg | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 147/147（原 137 + 新增 10） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y 套件 | `npm run test:a11y` | 4/4（真实 Chrome）；mock/axe/smoke/截图未重跑 | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-112/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 140.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 dist 含 `sw.js`/`manifest.webmanifest`/`icon.svg`、Vitest 全量 `147/147`、a11y 浏览器套件 `4/4`、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-112 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 140.4 失败分类、重测和回滚规则

- 快捷键劫持表单输入、Escape 影响其他控件、焦点丢失不归还、跳转链接遮挡内容、reduced-motion 规则破坏布局属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `shortcuts`/AppShell 键盘路径/`styles.css` reduced-motion 时，必须重跑 `shortcuts` 7/7、`App` 键盘 3 用例、全量 Vitest、lint/typecheck/build，并重跑 a11y 浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除跳转链接/快捷键/菜单键盘处理与 reduced-motion 样式，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 140.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-112 完成键盘可达性与焦点管理硬化（纯前端），并部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如性能优化、更多可访问性细节），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 141 节 BUILD-113 路由级代码分割与渲染优化（纯前端增量）

Run ID：`BUILD-113-CODE-SPLITTING-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 141.1 范围

- `App.tsx` 由 2739 行内联 40+ 页面组件与共享小组件，重构为 334 行壳层；页面组件抽取到 `src/pages/` 下 12 个页面模块（dashboard/courses/tasks/exams/assignments/community/search/misc/reader/assistant/teacher/knowledge），`App.tsx` 以 `lazy(() => import('./pages/...'))` 引用。
- 共享组件层拆分：`src/ui.tsx` 仅导出 React 组件（PageHead/Metric/SectionTitle/ChapterRow/TaskRow/Notice/QuestionBlock）；非组件工具（previewExams/previewStudentTasks/studentTaskKinds/studentTaskStatuses/previewStudentTaskCounts/activityKindLabel/isOptionlessActivityKind/isSingleConfigurationActivityKind/syncGlobalNotificationState）移入 `src/ui-helpers.ts`，规避 `react-refresh/only-export-components` 警告（`--max-warnings=0`）。
- 懒加载特例：`AdminPage` 与 `KnowledgeGraphCanvas` 保持独立 chunk；页面内部 `ResourceRow`/`SubmissionReview`/`Tool` 等局部组件不导出。
- 抽取工具：`frontend/scripts/extract-pages.mjs`（TypeScript AST，fixpoint 收敛被页面引用符号、相对路径 import 重写、`KnowledgeGraphCanvas` 特例）。
- 测试适配：`App.test.tsx` 两处同步断言（“继续学习”按钮、搜索结果按钮）改为 `findByRole` 等待懒加载路由就绪；断言目标与行为不变。

### 141.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 页面模块完整性、懒加载边界、行为等价、无凭据落盘 | 代码审查 + 单测 | 12 页面模块与 lazy 引用一一对应；ui 层拆分 0 警告；无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建 1879 modules，主包 292.26 kB（基线约 462 kB，-37%），12 个页面 chunk 独立 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 147/147（含 2 处懒加载 findBy 适配） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y 套件 + mock e2e | `npm run test:a11y`、`npm run test:e2e:mock` | a11y 4/4、mock e2e 50/50（真实 Chrome，覆盖全部懒加载路由）；axe/smoke/截图未重跑 | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-113/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 141.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且主包显著小于基线（292.26 kB vs 约 462 kB）、12 个页面 chunk 独立产出、Vitest 全量 `147/147`、a11y 浏览器套件 `4/4`、mock e2e 浏览器套件 `50/50`、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-113 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 141.4 失败分类、重测和回滚规则

- 页面模块漏导出/重复导出、懒加载后行为不一致、react-refresh 警告回归、主包不降反升、页面间跳转丢状态属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `App.tsx` 路由/lazy 引用、`src/pages/*`、`src/ui.tsx`/`src/ui-helpers.ts` 时，必须重跑全量 Vitest、lint/typecheck/build，并重跑 a11y 与 mock e2e 浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先恢复 `App.tsx` 内联结构（备份 `/tmp/App.tsx.bak` 可参考）并移除页面模块/ui 层，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 141.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-113 完成路由级代码分割（纯前端），主包 462→292 kB，并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多性能优化、可访问性细节），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 142 节 BUILD-114 懒加载 chunk 重试与浏览器全量回归（纯前端增量）

Run ID：`BUILD-114-LAZY-RETRY-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 142.1 范围

- 新增 `frontend/src/lazyRetry.ts`：`lazyRetry(factory, { retries, delaysMs })` 镜像 React `lazy()` 签名（`T extends ComponentType`，带针对性 eslint-disable 说明）；动态 import 失败后按 `delaysMs`（默认 600ms/1600ms）最多重试 `retries` 次（默认 2），重试耗尽才把错误交给全局 ErrorBoundary。
- 全量接线：`App.tsx` 32 处路由级 `lazy()`（AdminPage + 31 个页面模块）与 `src/pages/knowledge.tsx` 内部 `KnowledgeGraphCanvas` 全部切换为 `lazyRetry()`；瞬时网络故障不再让整个应用落入错误页，Suspense 内自动重试后恢复；chunk 结构不变。
- 测试：`src/lazyRetry.test.tsx` 4 用例（首次成功 1 次调用；瞬时失败 1 次后重试成功共 2 次调用；重试耗尽 3 次调用后进入 ErrorBoundary；`retries=0` 不重试）。
- 浏览器全量回归：a11y 4/4、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50——全部真实 Chrome 下通过，覆盖全部懒加载路由（含 BUILD-113 代码分割后跨页面跳转），补齐 BUILD-112/113 延期的 axe/smoke/screenshots 回归。

### 142.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 重试边界、错误语义、无凭据落盘 | 代码审查 + 单测 | lazyRetry 仅包装动态 import；重试耗尽才进 ErrorBoundary；无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建 1880 modules，主包 292.39 kB（gzip 87.22），12 个页面 chunk + ui/ui-helpers/AdminPage/KnowledgeGraphCanvas/vendor 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 151/151（原 147 + lazyRetry 4） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npm run test:smoke`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 4/4、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50（真实 Chrome） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实弱网 chunk 重试 | 外部输入未齐 | 正式环境人工/辅助技术未提供；真实 HTTPS 下弱网重试行为未验收 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-114/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 142.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功（1880 modules，主包 292.39 kB）、chunk 结构不变、Vitest 全量 `151/151`、a11y 4/4、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS 弱网下 chunk 重试行为、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-114 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 142.4 失败分类、重测和回滚规则

- 重试次数/延迟语义错误、重试耗尽未进 ErrorBoundary、`retries=0` 行为回归、react-refresh 警告回归、页面间跳转丢状态属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `frontend/src/lazyRetry.ts`、`App.tsx` 路由/lazy 引用、`src/pages/*` 时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先恢复 `lazyRetry` 引入前的 `App.tsx`/`pages/knowledge.tsx` 直接 `lazy()` 引用并移除 `lazyRetry.ts` 与其测试，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 142.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-114 完成懒加载 chunk 重试（纯前端）与五个浏览器套件全量回归，主包 292 kB 结构不变，并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多性能优化、可访问性细节），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 143 节 BUILD-115 路由级文档标题与导航焦点管理（纯前端增量）

Run ID：`BUILD-115-ROUTE-TITLES-FOCUS-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 143.1 范围

- 新增 `frontend/src/routeMeta.ts`：`SITE_TITLE`/`DEFAULT_ROUTE_TITLE`/`ROUTE_TITLES` 模式表/`resolveRouteTitle(pathname)`/`formatDocumentTitle(title)`，覆盖 App.tsx 全部路由（工作台、课程空间/我的课程、任务/作业详情、考试中心/详情、资料库/章节阅读、收藏、图谱、讨论/详情、活动/详情、消息、搜索、帮助、设置、Agent、学习记录、成绩册、教师工作台及各管理页、管理员工作台）；未知路径回退「课程平台」。
- `AppShell` 新增标题 effect：`location.pathname` 变化时 `document.title = formatDocumentTitle(resolveRouteTitle(location.pathname))`（「页面名 · 储能学习空间」），替代静态 `index.html` 标题。
- `AppShell` 新增焦点 effect：仅在路径变化（非首次加载、非同路径重复导航）时将焦点移回 `main#main-content`（`focus({ preventScroll: true })`，配合 BUILD-112 的 `tabIndex={-1}` 与跳转链接）；懒加载 Suspense 状态由 `role=status` 播报，标题变化由读屏软件播报。
- 测试：`src/routeMeta.test.ts` 5 用例；`src/App.test.tsx` 新增 4 用例（导航更新标题、未知路由重定向并设置标题、路由变化移焦主内容、同路径重复导航不夺焦）；`tests/a11y.spec.ts` 新增第 5 个浏览器用例（真实 Chrome 点击导航后标题更新且 `#main-content` 聚焦）。

### 143.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 标题映射完整性、焦点语义、无凭据落盘 | 代码审查 + 单测 | 模式表覆盖全部路由；仅路径变化移焦；无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 295.78 kB（+3.4 kB 标题映射），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 161/161（原 151 + routeMeta 5 + App 4） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 5/5、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50（真实 Chrome） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 读屏实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-115/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 143.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `161/161`、a11y 5/5、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下读屏软件实测标题与焦点管理、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-115 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 143.4 失败分类、重测和回滚规则

- 标题映射缺失/错配、焦点在首次加载或同路径导航被夺走、与跳转链接/`/` 快捷键冲突、react-refresh 警告回归属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `frontend/src/routeMeta.ts`、`App.tsx` 标题/焦点 effect 或路由表时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除 `AppShell` 标题/焦点 effect、`mainContentRef` 与 `routeMeta.ts`/其测试/a11y 第 5 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 143.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-115 完成路由级文档标题与导航焦点管理（纯前端，SPA 标准可访问性模式），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如通知未读状态实时播报、移动端抽屉焦点管理、更多性能优化），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 144 节 BUILD-116 移动端导航抽屉焦点管理（纯前端增量）

Run ID：`BUILD-116-MOBILE-DRAWER-FOCUS-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 144.1 范围

- 移动端导航抽屉（`sidebarOpen`）焦点管理，补全 BUILD-112 键盘可达性与 BUILD-115 路由焦点的标准抽屉模式：
  - 打开：点击「打开导航」后焦点移入「关闭导航」按钮（`focus({ preventScroll: true })`）。
  - 关闭：点击关闭按钮或遮罩后焦点归还「打开导航」触发按钮；点击导航链接关闭时，若 BUILD-115 路由焦点已移到 `main#main-content`，不抢焦。
  - Escape：抽屉打开期间 window keydown 监听 Escape，关闭抽屉并归还焦点；监听随关闭清理。
  - Tab 循环：`handleSidebarKeyDown` 在抽屉内首尾循环 Tab/Shift+Tab，焦点不落入遮罩与后台内容。
- 测试：`src/App.test.tsx` 新增 5 用例（打开移焦关闭按钮、Escape 关闭并归还焦点、关闭按钮归还焦点、遮罩归还焦点、Tab 首尾循环）；`tests/a11y.spec.ts` 新增第 6 个浏览器用例（390x844 移动视口：打开抽屉→关闭按钮聚焦，Escape→抽屉关闭且触发按钮聚焦）。

### 144.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 焦点语义、Escape 边界、无凭据落盘 | 代码审查 + 单测 | 打开/关闭/归还/Escape/Tab 循环语义正确；无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 296.59 kB（+0.8 kB），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 166/166（原 161 + 抽屉 5） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，113 routes/112 paths 不改变 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50（真实 Chrome） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 移动抽屉实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-116/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 144.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `166/166`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 50/50、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下移动抽屉焦点与读屏实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-116 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 144.4 失败分类、重测和回滚规则

- 打开不移焦、Escape 不关闭/不归还焦点、关闭后焦点丢失、Tab 循环破坏、与路由焦点/用户菜单 Escape 冲突属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `AppShell` 抽屉状态/焦点 effect、`handleSidebarKeyDown` 或侧边栏结构时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除抽屉焦点 effect/Escape effect/`handleSidebarKeyDown` 与三个 ref，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 144.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-116 完成移动端导航抽屉焦点管理（纯前端，标准抽屉模式），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如通知未读状态实时播报、资源列表性能优化、更多可访问性细节），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 145 节 BUILD-117 通知未读状态实时播报（纯前端增量）

Run ID：`BUILD-117-UNREAD-BROADCAST-20260806-01`  
状态：`IMPLEMENTED_PENDING_GATE`（本地实现与验证完成，真实环境门禁开放）

### 145.1 范围

- 通知未读状态实时播报，不依赖真实 API：
  - 新增 `src/useUnreadPolling.ts` 的 `useUnreadNotificationPolling(intervalMs = 60_000)` Hook：每 60 秒调用既有 `loadNotifications(false, 1, 1)` 轻量拉取未读数；仅非预览、非会话过期时轮询；`document.visibilityState` 隐藏时暂停、恢复可见时立即轮询并重置定时器；卸载清理定时器与监听。
  - 未读数通过既有 `syncGlobalNotificationState` 同步到全局 store，铃铛角标与 `aria-label` 实时更新；未读数上升时在 `AppShell` 的 `sr-only` + `aria-live="polite"` 播报区输出「您有 N 条新通知，当前共 M 条未读。」；下降/不变不播报；失败静默重试。
- 测试：`src/useUnreadPolling.test.tsx` 5 用例（定时轮询同步/播报、下降不播报、预览不轮询、会话过期不轮询、卸载清理）；`tests/mock-api.spec.ts` 新增第 51 浏览器用例（`page.clock` 快进 60s 验证铃铛 `aria-label` 与 `.notification-live-region` 文本）。

### 145.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 轮询语义、播报边界、无凭据落盘 | 代码审查 + 单测 | 60s 轮询只读、仅上升播报、失败静默、无新增凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 300.68 kB（+4.1 kB），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 171/171（原 166 + 轮询 5） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，复用 `/api/notifications` 既有契约 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 51/51（真实 Chrome，含 `page.clock` 轮询播报用例） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 轮询播报实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-117/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 145.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `171/171`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 51/51、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下轮询播报与读屏实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-117 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 145.4 失败分类、重测和回滚规则

- 轮询泄漏（未卸载定时器/监听）、预览或会话过期仍请求、下降或不变误播报、`notification-live-region` 缺失属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `useUnreadNotificationPolling`、`AppShell` 播报区或通知同步路径时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先删除 `src/useUnreadPolling.ts` 与 `src/useUnreadPolling.test.tsx`、移除 AppShell 的 Hook 调用与播报区、删除 mock e2e 第 51 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 145.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-117 完成通知未读状态实时播报（纯前端，60s 轮询 + aria-live 播报），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如资源列表性能优化、更多可访问性细节），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 146 节：BUILD-118 资源列表性能优化（纯前端增量）

### 146.1 本轮实现

- `frontend/src/pages/misc.tsx` 的 `ResourcesPage` 性能优化（纯前端，不依赖真实 API）：
  - 搜索过滤改用 `useMemo`（依赖 `data.resources` 与 `useDeferredValue(query)`），输入变化时列表不再每次重算；`useDeferredValue` 让搜索框输入保持高优先级响应，过滤结果以低优先级渲染，提升大列表输入流畅度。
  - 抽出 `ResourceCard` 卡片组件并包裹 `React.memo`，配合稳定的 `useCallback` 打开回调，搜索/计数变化时未变更卡片跳过重渲染。
  - 新增结果计数行 `.resource-summary`：「共 N 份资料，当前显示 M 份。」；「清除筛选」按钮在无关键词时 `disabled`。
  - 过滤语义与旧版一致：空关键词显示全部；非空按 `title + sourceFile` 小写包含匹配（额外 `trim`）。
- 测试：`src/App.test.tsx` 新增 1 个组件用例（预览 `/resources`：5 张卡片与计数、输入「规划」过滤到 1 张、无匹配空态与 0 份、清除筛选恢复全部并清空输入、按钮禁用/启用）；`tests/mock-api.spec.ts` 新增第 52 个浏览器用例（真实 Chrome：输入「变流器」过滤到 `储能变流器拓扑及并网控制` 1 张卡片、计数「当前显示 1 份」、清除筛选恢复全部）。

### 146.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 过滤语义、计数、无凭据落盘 | 代码审查 + 单测 | 过滤/计数/清除语义正确；纯本地行为，无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 300.68 kB（与 BUILD-117 同尺寸），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 172/172（原 171 + 资源过滤 1） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，过滤与计数完全本地完成 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 52/52（真实 Chrome，含资源搜索用例） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 资源搜索实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-118/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 146.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `172/172`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 52/52、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下资源列表搜索与读屏实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-118 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 146.4 失败分类、重测和回滚规则

- 过滤语义漂移（空关键词不全显示、大小写/空格处理异常）、计数不更新、`useDeferredValue` 与 `useMemo` 依赖缺失导致陈旧结果、`ResourceCard` memo 破坏卡片交互（打开/状态按钮失效）属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `ResourcesPage`、`ResourceCard`、`.resource-summary` 或资源过滤逻辑时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除 `ResourceCard`/`useMemo`/`useDeferredValue`/`useCallback` 与 `.resource-summary`、恢复 `ResourcesPage` 直接过滤渲染、删除组件用例与 mock e2e 第 52 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 146.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-118 完成资源列表性能优化（纯前端，`useMemo` + `useDeferredValue` + `React.memo` + 结果计数），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多可访问性细节、教师端/社区页面增量），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 147 节：BUILD-119 搜索结果键盘方向键导航（纯前端增量）

### 147.1 本轮实现

- `frontend/src/pages/search.tsx` 的 `SearchPage` 搜索结果列表增加 roving tabindex 键盘导航（纯前端，不依赖真实 API）：
  - 列表容器 `onKeyDown` 统一处理：`ArrowDown`/`ArrowUp` 在结果间移动焦点（到首/尾停止，不循环）、`Home`/`End` 跳到首/尾；焦点落在结果行时 `Enter`/`Space` 由原生按钮行为打开目标。
  - `rowRefs` 数组 + `activeIndex` 状态实现 roving tab stop：当前行 `tabIndex=0`、其余 `-1`；结果变化（查询/类型/分页）时锚点重置为 0，保证新结果列表始终有可聚焦入口。
  - 行 `onFocus` 同步 `activeIndex`：鼠标点击或 Tab 聚焦所在行即成为 roving 锚点。
  - 不改变结果列表既有语义（原生按钮 + `aria-live="polite"` 区域），不新增 ARIA 角色。
- 测试：`src/App.test.tsx` 新增 1 个组件用例（预览 `/search?q=储能`：首行 tabIndex=0、ArrowDown 移焦且 tabIndex 交换、ArrowUp 回移、End/Home 跳首尾、顶部 ArrowUp 保持、直接 focus 末行同步锚点）；`tests/mock-api.spec.ts` 新增第 53 个浏览器用例（真实 Chrome + mock `/api/search` 4 条结果：ArrowDown×2、End、Home、顶部 ArrowUp、Enter 激活跳转 `/courses/1/chapters/1`）。

### 147.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 键盘语义、roving 边界、无凭据落盘 | 代码审查 + 单测 | 方向键/Home/End 语义正确；纯本地处理，无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 300.68 kB（与 BUILD-118 同尺寸），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 173/173（原 172 + 搜索键盘 1） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，键盘处理完全本地完成 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 53/53（真实 Chrome，含搜索键盘用例） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 搜索键盘实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-119/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 147.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `173/173`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 53/53、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下搜索键盘导航与读屏实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-119 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 147.4 失败分类、重测和回滚规则

- 方向键越界/循环错误、焦点与 tabIndex 不一致、结果变化后无 Tab 停靠点、Enter/Space 被拦截或双重触发、与分页/类型切换焦点冲突属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `SearchPage` 键盘处理、`rowRefs`/`activeIndex` 或结果行结构时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除 `handleResultKeyDown`/`activeIndex`/`rowRefs`/行 `tabIndex`/`ref`/`onFocus`、恢复 `.search-result-list` 无键盘处理版本、删除组件用例与 mock e2e 第 53 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 147.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-119 完成搜索结果键盘方向键导航（纯前端，roving tabindex + Arrow/Home/End + Enter 激活），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多可访问性细节、教师端/社区页面增量），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 148 节：BUILD-120 学生/教师数据表格 ARIA 语义化（纯前端增量）

### 148.1 本轮实现

- 学生/教师数据表格 ARIA 语义化（纯前端，不依赖真实 API）：
  - 学生端 3 个 div 网格表格补充 `role="table"` + `aria-label`：`tasks.tsx` 任务中心「任务列表」、`exams.tsx` 考试列表「考试列表」、`misc.tsx` 成绩页「任务成绩」；表头行 `role="row"` + 4 个 `role="columnheader"`，数据行 `role="row"`，单元格 `role="cell"`；操作按钮包装为 `<span className="task-table-actions" role="cell">`，空态改为合法表格行（`empty-row` 行内单 `cell`）。
  - 教师端 6 个 div 网格表格同样语义化（`teacher.tsx`）：课堂活动「活动列表」、课程资料「资料版本」、题库「题库」、作业「作业列表」、考试「考试列表」、成绩册「作业成绩汇总」；`row-actions` 操作区补 `role="cell"`。
  - CSS：`.task-table-row > .task-table-actions { justify-self: end; }` 替代原 `.button` 移动端规则；新增 `.task-table-row > .empty-state { grid-column: 1 / -1; }` 与 `.task-table-actions { min-width: 0; }`，视觉布局与改造前一致。
  - 读屏收益：表格可被识别为「表格 N 列」，支持行/列导航与表头播报。
- 测试：`src/App.test.tsx` 新增 1 个组件用例（预览 `/tasks` 表头文本序列 + 行数、`/exams`、`/courses/1/grades` 表头 4 列、mock 教师会话 `/teacher/resources` 表头 4 列 + 2 行）；`tests/mock-api.spec.ts` 新增第 54 个浏览器用例（真实 Chrome：学生 `/tasks` 表格可见 + 4 columnheader + 行/单元格；教师 `/teacher/resources`「资料版本」表格可见 + 4 columnheader + 第 2 行可见）。

### 148.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 表格结构、ARIA 层级、无凭据落盘 | 代码审查 + 单测 | 9 表 `table→row→columnheader/cell` 结构完整；纯前端属性，无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 300.68 kB（与 BUILD-119 同尺寸），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 174/174（原 173 + 表格语义 1） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，表格语义完全本地完成 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 54/54（真实 Chrome，含表格语义用例） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 表格读屏实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-120/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 148.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `174/174`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 54/54、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下表格读屏导航实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-120 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 148.4 失败分类、重测和回滚规则

- 表格角色层级破坏（行内出现裸按钮/空态非行子节点）、表头/单元格错配、移动端操作列定位回归、空态跨列丢失属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改四个页面表格结构、`.task-table-actions`/`.empty-state` 规则或表格测试时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除四文件中的表格角色/`aria-label`/`task-table-actions` 包装与空态行、恢复 `.button` 移动端规则、删除组件用例与 mock e2e 第 54 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 148.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-120 完成学生/教师 9 个数据表格 ARIA 语义化（纯前端，`role=table/row/columnheader/cell` + 空态合法化 + 视觉无回归），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多可访问性细节、教师端/社区页面增量），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 149 节：BUILD-121 教师成绩册 CSV 导出（纯前端增量）

### 149.1 本轮实现

- 教师成绩册 CSV 导出（纯前端，不依赖真实 API）：
  - `frontend/src/pages/teacher.tsx` 的 `TeacherGradebookPage` 增加「导出 CSV」按钮（位于「作业成绩汇总」表头工具栏，紧邻筛选与刷新控件）。
  - 导出三区块 CSV：作业成绩汇总（作业、题数、状态、已提交、已批改、完成率、平均成绩、平均正确率）、学生汇总（学生、提交次数、已完成作业、平均正确率、需要关注）、知识点掌握（知识点、状态、掌握度）；数据全部来自已加载 `gradebook` 状态，无新网络请求。
  - CSV 兼容性：UTF-8 BOM 开头便于 Excel 识别中文；字段含逗号/引号/换行时按 RFC 4180 引号包裹转义；`\r\n` 行分隔；文件名 `成绩册-YYYY-MM-DD.csv`。
  - 下载实现：`Blob` + `URL.createObjectURL` + 临时 `<a download>` 点击 + `revokeObjectURL` 释放；无凭据、无服务端写入。
- 测试：`src/App.test.tsx` 新增 1 个组件用例（mock 教师会话 `/teacher/gradebook`：stub URL 子类 createObjectURL 与 anchor click，断言文件名、BOM、三区块表头与逐行数据；try/finally 清理全局）；`tests/mock-api.spec.ts` 新增第 55 个浏览器用例（真实 Chrome `page.waitForEvent('download')` 校验文件名与 CSV 内容）。

### 149.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 导出内容、CSV 转义、无凭据落盘 | 代码审查 + 单测 | 三区块数据完整、RFC 4180 转义正确；纯前端只读，无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 300.68 kB（与 BUILD-120 同尺寸），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 175/175（原 174 + CSV 导出 1） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，导出完全本地完成 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 55/55（真实 Chrome，含 CSV 下载用例） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 导出实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-121/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 149.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `175/175`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 55/55、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下成绩册导出实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-121 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 149.4 失败分类、重测和回滚规则

- CSV 转义错误（含逗号/引号/换行字段破坏列结构）、BOM/编码缺失导致 Excel 乱码、文件名/日期错误、下载对象 URL 泄漏（未 revoke）属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `exportGradebookCsv`/`downloadGradebookCsv`、导出按钮或成绩册工具栏时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先移除 `exportGradebookCsv`/`downloadGradebookCsv`/导出按钮与 `Download` 图标导入、删除组件用例与 mock e2e 第 55 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 149.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-121 完成教师成绩册 CSV 导出（纯前端，三区块导出 + BOM/RFC 4180 + 真实 Chrome 下载验收），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多可访问性细节、教师端/社区页面增量），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。

## 第 150 节：BUILD-122 讨论列表分页（纯前端增量）

### 150.1 本轮实现

- 讨论列表分页（纯前端，不依赖真实 API）：
  - `frontend/src/api/client.ts` 的 `loadDiscussions` 扩展为 `loadDiscussions(query, page = 1, pageSize = 8)`：请求携带 `query`/`page`/`page_size` 参数，复用服务端既有 `/api/discussions` 分页契约（`paginate` 返回 `total`），返回 `{ items, total }`。
  - `frontend/src/pages/community.tsx` 的 `DiscussionsPage` 接入分页：`page`/`total` 状态、每页 8 条、`totalPages` 计算；列表下方新增 `.course-pagination` 导航（上一页/下一页 + 「第 N / M 页，共 X 条」），首/末页按钮禁用；计数标签改为服务端 `total` 个主题。
  - 搜索输入变化时页码重置为 1；新增 `loadSequence` 竞态守卫，丢弃过期响应，避免旧页结果覆盖新查询。
- 测试：`src/api/client.test.ts` 更新 `loadDiscussions` 用例（URL `?query=…&page=1&page_size=8` + `{ items, total }` 形状）；`src/App.test.tsx` 新增 1 个组件用例（12 条 fixture：首页 8 条 + 分页文本 + 上一页禁用、下一页 4 条 + `page=2` 请求、返回上一页、搜索重置为单页）；`tests/mock-api.spec.ts` 新增第 56 个浏览器用例（真实 Chrome 完整分页流程）。

### 150.2 T0-T6 矩阵

| 层 | 检查 | 命令/范围 | 结果 | 状态 |
|---|---|---|---|---|
| T0 范围、权限、数据与代码审查 | 分页语义、竞态、无凭据落盘 | 代码审查 + 单测 | 分页/搜索重置/竞态守卫正确；复用既有契约，无新增网络/凭据路径 | `PASS` |
| T1 静态、类型、构建和硬化 | lint、typecheck、build | `npx eslint . --max-warnings=0`、`npx tsc -b --pretty false`、`npm run build` | 全部退出 0；构建成功，主包 300.78 kB（+0.1 kB 分页参数），chunk 结构不变 | `PASS` |
| T2 Store、API、单元、组件和领域回归 | 全量 Vitest | `npx vitest run --config vitest.config.ts` | 176/176（原 175 + 讨论分页 1 + client 用例更新） | `PASS` |
| T3 本地 API/OpenAPI 契约 | 无新增后端路由 | 不适用 | 本增量纯前端，复用 `/api/discussions` 既有分页契约 | `NOT_APPLICABLE` |
| T4 浏览器流程与质量门禁 | a11y + axe + smoke + screenshots + mock e2e | `npm run test:a11y`、`npm run test:axe`、`npx playwright test --config playwright.config.ts`、`npm run test:screenshots`、`npm run test:e2e:mock` | a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 56/56（真实 Chrome，含讨论分页用例） | `OBSERVED_PASS` |
| T5 质量、可访问性和真实环境 | 正式 axe 等价、真实辅助技术、六视口人工、真实角色、真实 HTTPS 讨论分页实测 | 外部输入未齐 | 正式环境人工/辅助技术未提供 | `BLOCKED_INPUT` |
| T6 证据、回退和签核 | 六类标准证据 + 账本 | `acceptance/frontend/BUILD-122/` 六件套 + 验证器 | 证据齐；正式门禁未齐 | `REVIEW_REQUIRED` |

### 150.3 逐项验收条件和失败重测

- 硬阈值：ESLint 0 错误 0 警告、tsc 退出 0、生产构建成功且 chunk 结构不变、Vitest 全量 `176/176`、a11y 6/6、axe 4/4、smoke 2/2、screenshots 1/1（六视口）、mock e2e 56/56、`git diff --check` 通过。
- 正式边界（T5）：正式 axe 等价审查、真实辅助技术与六视口人工验收、真实 Moodle/pluginfile 三角色、真实工作流知识库发布与聊天 E2E、真实 HTTPS/正式域名下讨论分页与读屏实测、Docker/HTTPS、备份恢复和提交材料全部通过后，才能关闭 BUILD-122 或最终发布。
- 真实 API 依赖项保持 PARKED：`REAL-KB-RELEASE-20260806-01`（需讯飞控制台配置引用标记）、`REAL-CHAT-E2E-20260806`（依赖 KB 发布）；`SPARK-AUTH-FAIL-001` 为独立开放 P0，不得由本增量关闭。

### 150.4 失败分类、重测和回滚规则

- 分页越界/按钮状态错误、搜索后停留在越界页、过期响应覆盖新结果（竞态）、单页误显分页、计数与分页文本不一致属于 P0/P1；修复后使用新产品 run ID 从 T0 重跑。
- 修改 `loadDiscussions`、`DiscussionsPage` 分页逻辑或讨论列表结构时，必须重跑全量 Vitest、lint/typecheck/build，并重跑五个浏览器套件。
- 缺正式 axe、辅助技术、真实角色、真实 Moodle/工作流归为 `BLOCKED_INPUT`/`BLOCKED_DEPENDENCY`；不得生成占位 PDF、伪造角色/课程或修改 manifest hash/page_count。
- 回滚顺序为先恢复 `loadDiscussions(query)` 旧签名与 `DiscussionsPage` 无分页版本（移除 `page`/`total`/`loadSequence`/导航/重置 effect）、恢复 client 旧断言、删除组件用例与 mock e2e 第 56 用例，再移除本轮六份标准证据；不触碰产品代码、course-data、服务器 `deploy/.env` 或历史证据。回滚后生成新 run ID 并从 T0 复验。

### 150.5 本轮计划进一步审查

本增量继续推进“真实 API 未配置部分保持标记并移到下一项”的路径：`REAL-KB-RELEASE-20260806-01` 与 `REAL-CHAT-E2E-20260806` 仍 PARKED，未伪造或绕过；BUILD-122 完成讨论列表分页（纯前端，复用 `/api/discussions` 契约 + 查询重置 + 竞态守卫），并计划部署到 `139.196.45.2` 的 `/learn/` 前端验证。

下一项开发候选：P2 其余纯前端项（如更多教师端/管理后台页面增量），或恢复真实 API 门禁（需用户完成讯飞控制台配置）。
