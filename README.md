# EnergyGraph-AI ·《电力系统储能技术》AI Agent 智能课程教学平台

> 线上系统：https://energygraph.icu/agent/ （student / teacher 公开教学账号见《03-作品Demo》内手册）
> 代码仓库按参赛提交目录结构组织，目录索引如下。

| 目录 | 内容 |
| :--- | :--- |
| `02-伦理与安全合规性声明/` | 伦理与安全合规性声明（PDF） |
| `03-作品Demo/` | 作品体验：`DEMO_GUIDE.md`（体验地址、账号、15 分钟体验路线）与学生/教师/平台三份使用手册 |
| `04-作品方案/` | （占位，待提交作品方案材料） |
| `05-作品代码/` | 全部源码与工程档案：`agent-adapter`（FastAPI 网关）、`agent-ui`（前端 SPA）、`deploy`（Docker Compose 生产部署）、`scripts`、`docs`、`course-data`、`archive`（过程档案）等；复现指南见 `05-作品代码/REPRODUCTION.md` |
| `06-效果验证报告/` | （占位，待提交效果验证报告） |
| `07-其他材料/` | （占位，待提交其他补充材料） |

## 快速链接

- 五分钟跑起来：`05-作品代码/REPRODUCTION.md`
- 项目现状与功能矩阵：`05-作品代码/PROJECT_STATUS.md`
- 运维手册（错误码对照/发布纪律/密钥 SOP）：`05-作品代码/docs/OPERATIONS.md`
- 全量开发留档：`05-作品代码/DEVELOPMENT_ARCHIVE.md`

## 工程红线

- 讯飞密钥仅存服务器端 `deploy/.env`，不入前端/日志/仓库（2026-09-09 安全专项后实测成立）；
- 零表情符号规范；上游失败一律如实提示，绝不编造题目、答案或引用。
