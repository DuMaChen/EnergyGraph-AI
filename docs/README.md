# 项目文档索引

这里是项目已有计划、部署说明、验收报告、案例、提交材料和数据处理文档的统一入口。
文档保留在原有目录中，避免复制后出现多个不一致版本；本页只负责分类、说明用途和标记状态。

## 1. 当前状态

- [PROJECT_STATUS.md](../PROJECT_STATUS.md)：2026-07-25 当前完成状态、服务器复核、风险和下一步计划。
- [根目录 README](../README.md)：项目简介、快速开始、预览地址和主阻断项。

## 2. 计划和方案

- [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)：唯一主实施与验收计划，包含架构、功能范围、P0/P1 门槛、自动化测试、人工验收、恢复和竞赛材料要求。
- [学习通式前端实施计划](../XUEXITONG_STYLE_FRONTEND_PLAN.md)：基于公开资料和 browser-harness 公开入口实测整理的课程平台前端改造方案，包含技术栈、路由、组件、数据模型、阶段计划和验收标准。
- [提交方案目录说明](../04-作品方案/README.md)：正式提交方案目录说明。
- [提交版计划副本](../04-作品方案/IMPLEMENTATION_PLAN.md)：提交材料整理时的计划副本；修改计划时以根目录版本为准，再运行材料组装脚本。

## 3. 部署和运行

- [deploy/README.md](../deploy/README.md)：Docker Compose、Moodle、Caddy、讯飞配置、备份恢复和维护命令。
- [agent-adapter/README.md](../agent-adapter/README.md)：Adapter 的接口边界、Mock 运行和成绩回写说明。
- [flowise/README.md](../flowise/README.md)：历史 Flowise 实验说明，不属于本期 P0/P1 主链路。
- [当前预览](http://168.144.36.82/)：Moodle 课程入口。
- [Agent 预览](http://168.144.36.82/agent/)：Agent 页面入口。

## 4. 自动化验收报告

| 文档 | 用途 | 当前状态 |
|---|---|---|
| [local-verification-report.md](../acceptance/local-verification-report.md) | 本地代码、数据、协议、UI、备份和审计证据 | 本地回归通过，真实链路待配置 |
| [functional-acceptance-report.md](../acceptance/functional-acceptance-report.md) | 功能验收矩阵和运行号 | 基线记录为 `local-regression-20260722-primary-v12`；2026-07-25 复跑 `LOCAL_ACCEPTANCE_OK` |
| [security-and-compliance-report.md](../acceptance/security-and-compliance-report.md) | 权限、CSRF、上传、注入、日志和 AI 标识 | 本地通过，真实账号/Workflow 项目部分完成 |
| [reproducibility-report.md](../acceptance/reproducibility-report.md) | 干净环境部署和恢复复现记录 | 底座通过，真实讯飞恢复待完成 |
| [deployment-checklist.md](../acceptance/deployment-checklist.md) | 服务器、网络、备份和最终提交勾选项 | 外部前置条件未勾选 |
| [requirements-matrix.md](../acceptance/requirements-matrix.md) | 需求状态与证据位置 | 8 条需求逐项标记 |
| [security baseline](../acceptance/test-reports/automated/security-baseline-2026-07-22.md) | 自动化安全基线记录 | 底座通过，真实主链路阻断 |

## 5. 黄金案例和固定夹具

### 黄金案例

- [CASE-001 知识问答](../acceptance/golden-cases/case-001-qa.md)
- [CASE-002 学习诊断](../acceptance/golden-cases/case-002-learning.md)
- [CASE-003 教师备课](../acceptance/golden-cases/case-003-teacher.md)
- [CASE-004 安全边界](../acceptance/golden-cases/case-004-safety.md)
- [CASE-005 作业/批改/学情](../acceptance/golden-cases/case-005-assessment-and-grading.md)
- [CASE-006 图谱/教材/情景](../acceptance/golden-cases/case-006-graph-textbook-scenario.md)

### 固定夹具

- [作业 A-001](../acceptance/test-fixtures/assignment-A-001.json)
- [图谱基线](../acceptance/test-fixtures/graph-baseline.json)
- [学情基线](../acceptance/test-fixtures/learning-profile-baseline.json)
- [场景基线](../acceptance/test-fixtures/scenarios.json)
- [人工验收记录模板](../acceptance/test-reports/manual/README.md)

## 6. 提交材料

- [01 参赛信息](../01-参赛信息/README.md)
- [02 伦理与安全合规性声明](../02-伦理与安全合规性声明/README.md)
- [03 作品 Demo](../03-作品Demo/README.md)
- [04 作品方案](../04-作品方案/README.md)
- [05 作品代码](../05-作品代码/README.md)
- [06 效果验证报告](../06-效果验证报告/README.md)
- [07 其他材料](../07-其他材料/README.md)

提交材料脚本：

```bash
bash scripts/assemble_submission_materials.sh
bash scripts/package_submission_code.sh
bash scripts/check_submission_materials.sh
```

目前材料检查仍应阻断：正式 HTTPS Demo 地址、实际录屏、真实人工验收汇总。

## 7. 数据处理和源文件

- `course-data/normalized/manifest.json`：20 个 PDF 的 manifest、文件哈希、章节和页数。
- `course-data/normalized/graph-baseline.json`：6 章、20 个知识点和 17 条关系。
- `course-data/xingchen-sources/`：带来源标记的讯飞知识库上传文本和 manifest。
- `scripts/prepare_course_data.py`：处理课件 ZIP 文件名和文本。
- `scripts/build_course_baseline.py`：生成图谱基线。
- `scripts/export_xingchen_sources.py`：生成讯飞知识库来源文本。

原始 ZIP、Excel、DOCX、报名 PDF 和归一化 PDF 不属于 GitHub 源码提交内容，详见根目录 `.gitignore`。

## 8. 脚本分类

| 类型 | 脚本 |
|---|---|
| 部署 | `deploy_server.sh`、`smoke_acceptance.sh`、`moodle_login_smoke.sh` |
| 真实 Workflow | `check_xingchen_config.sh`、`real_workflow_preflight.sh`、`xingchen_smoke.sh` |
| 本地验收 | `run_local_acceptance.sh`、`test_*`、`performance_smoke.py` |
| 安全和提交 | `pre_submission_audit.sh`、`check_submission_materials.sh`、`assemble_submission_materials.sh`、`package_submission_code.sh` |
| 备份恢复 | `backup.sh`、`verify_backup.sh`、`restore_rehearsal.sh`、`full_restore_rehearsal.sh` |

## 9. 阅读顺序

新成员建议按以下顺序阅读：

1. `README.md`
2. `PROJECT_STATUS.md`
3. `IMPLEMENTATION_PLAN.md`
4. `deploy/README.md`
5. `acceptance/requirements-matrix.md`
6. `acceptance/local-verification-report.md`
7. 对应黄金案例和固定夹具
8. `acceptance/test-reports/manual/README.md`
