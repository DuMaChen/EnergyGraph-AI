# 电力系统储能技术课程 Agent 平台
# 项目当前完成状态与历史文档整理

> 状态快照日期：2026-08-22（Asia/Shanghai）
> 适用仓库：[DuMaChen/EnergyGraph-AI](https://github.com/DuMaChen/EnergyGraph-AI)
> 当前主分支：`main`

## 1. 一句话结论

项目已经完成**生产级云端部署（HTTPS: https://energygraph.icu）、Moodle 真实发信/收信支持、讯飞星辰 Workflow 真实对接与知识库正式发布（20 份课件已入库）、三角色教学业务闭环回归（管理员/教师/学生）、自动化与人工验收报告汇总及脱敏源码包打包**。

项目核心技术链路与材料建设已全部就绪，仅剩团队进行最终真机操作演示录屏（`03-作品Demo/demo-video.mp4`）即可进行最终比赛提交。

当前准确状态是：

> **云端全链路已上线并完成真实业务回归；讯飞星辰知识库与真实 Workflow 已正式发布并通过黄金用例核验；提交材料除视频录像外已全部就绪。**

## 2. 项目目标

建设一个面向“电力系统储能技术”课程的教学 Agent 平台，组合以下能力：

- Moodle 课程平台：课程、章节、课件、测验、作业和身份管理。
- 讯飞星辰 Agent：课程问答、知识库检索、学习路径、教师辅助和情景演绎。
- 课程知识库：由 20 份课程 PDF 和知识图谱整理而成，回答必须带可核验来源。
- Agent Adapter：保护讯飞密钥，处理 Moodle 会话、权限、CSRF、幂等、限流、流式响应和来源校验。
- 教学数据服务：知识图谱、教材页码、题目、作业、提交、成绩、学情和场景会话。
- 竞赛材料体系：实施计划、验收报告、复现报告、人工记录模板和脱敏代码包。

## 3. 目标架构

```text
用户浏览器
    |
    v
Caddy :80/:443
    |----------------------|
    v                      v
Moodle :80          Agent UI :80
    |                      |
    | 同源 /api/*          |
    |                      v
    |               Agent Adapter :8081
    |                      |
    |                      v
    |          讯飞星辰 Workflow API
    |                      |
    |       Workflow + 课程知识库 + 模型
    |
    v
MariaDB
```

### 3.1 主链路组件

| 组件 | 当前职责 | 本期地位 |
|---|---|---|
| Moodle | 课程、章节、课件、作业、测验、用户身份 | P0 主链路 |
| Agent UI | 课程内 Agent 交互、图谱、教材、作业和教师入口 | P0 主链路 |
| Agent Adapter | 权限、会话、CSRF、幂等、限流、流式转发、来源核验 | P0 主链路 |
| MariaDB | Moodle 和课程平台持久化数据 | P0 主链路 |
| Caddy | 同源路由、HTTP/HTTPS 入口 | P0 主链路 |
| 讯飞星辰 Workflow | Agent 行为、流程分支、模型调用和 RAG | P0 主链路，待真实配置 |
| 讯飞知识库 | 课程文档切分、召回和来源 | P0 主链路，待平台版本 |
| Flowise | 历史实验链路 | 不纳入本期通过判定 |
| Qdrant | 历史向量库实验 | 不纳入本期通过判定 |
| OpenAI-compatible Gateway | 早期协议测试 | 不纳入本期通过判定 |

### 3.2 模型决策

当前不把 GPT-5.6 或本地模型写死在主 Agent 链路中。主 Agent 使用讯飞星辰平台中发布的 Workflow 和其配置的模型。未来更换微调模型时，只需替换星辰平台或适配配置，不应改动 Moodle、UI 和 Adapter 的教学业务边界。

## 4. 课程数据状态

| 数据项 | 当前结果 | 证据 |
|---|---:|---|
| 课程 PDF | 20 个 | `course-data/normalized/manifest.json` |
| PDF 页面 | 439 页 | 课程 manifest |
| 可提取文本页面 | 439 页 | 预处理报告 |
| 文本覆盖率 | 100% | `scripts/verify_course_data.py` |
| 课程知识点 | 20 个 | `graph-baseline.json` |
| 图谱关系 | 17 条 | `graph-baseline.json` |
| 课程章节 | 6 章 | Moodle 种子脚本和图谱基线 |
| 初步文本 chunk | 439 个 | 课程预处理记录 |
| 导入错误 | 0 | 课程数据验证 |

课程章节为：

1. 第 1 章 概述
2. 第 2 章 电力系统与储能技术的应用
3. 第 3 章 电力储能系统的组成及工作原理
4. 第 4 章 电力储能系统的规划配置
5. 第 5 章 电力储能系统的接入与运行控制
6. 第 6 章 电力储能系统的性能检测与评估

原始课件 ZIP、Excel、DOCX 和报名 PDF 保留在本地工作区用于数据处理，但已被 `.gitignore` 排除，不上传 GitHub。仓库只保留归一化 manifest、图谱基线、可复现脚本和非敏感来源元数据。

## 5. 已完成的实现范围

### 5.1 课程和页面

- Moodle 4.5 稳定分支课程环境已部署。
- 已幂等创建教学课程，课程 ID 当前记录为 `2`。
- 已创建 6 个章节和 20 个课件资源。
- 课程首页可以进入 Agent iframe。
- Agent 页面包含课程问答、知识图谱、教材查阅、作业、批改、学情和情景入口。
- 620px 以下教师工具区域改为单列，避免移动端横向溢出。
- 页面显示 AI 生成内容标识。

### 5.2 Agent Adapter

Adapter 已实现或覆盖：

- Moodle 会话桥接和角色识别。
- 学生、教师和管理员的功能权限边界。
- Moodle `sesskey` CSRF 校验。
- 同源请求校验。
- 请求体大小限制。
- 用户级限流和并发隔离。
- `Idempotency-Key` 和业务签名幂等。
- 讯飞 Workflow 请求转换。
- `Authorization: Bearer API_KEY:API_SECRET` 服务端注入。
- 非流式 JSON 和流式 SSE 转换。
- `token`、`source`、`done`、`error` 事件处理。
- 来源文件、章节、页码、manifest 和资源版本核验。
- 课程外问题和伪造实验数据请求的安全边界。
- 管理员脱敏状态接口。
- 知识库版本状态和发布门槛。
- 教师作业、学生提交、客观题评分、主观题 Agent 初评和教师复核状态。
- 图谱先修路径、教材页码映射和场景会话状态。

### 5.3 教学功能原型

| 功能 | 当前实现状态 | 当前证据 |
|---|---|---|
| 学生课程入口 | 已实现并通过 Mock/权限夹具 | `test_adapter_runtime.py` |
| 知识图谱 | 6 章、20 点、17 条关系，支持先修路径 | `test_graph_scenario_fixture.py` |
| 教材查询 | 支持章节、知识点、资源和页码映射 | `course_store.py`、CASE-006 |
| 章节题目 | 支持固定题目夹具和题目管理 | `test_acceptance_fixture.py` |
| 作业发布 | 支持草稿、发布和学生可见性隔离 | CASE-005 |
| 学生提交 | 支持截止时间、尝试次数和幂等 | CASE-005 |
| 客观题批改 | 后端确定性评分 | CASE-005 |
| 主观题初评 | Agent 初评，需教师复核 | 本地 Mock 夹具 |
| 教师改分 | 有审计字段和成绩重算约束 | 本地 Mock 夹具 |
| 学情诊断 | `learning-rule-v1` 确定性指标 + Agent 解释 | `test_course_store.py` |
| 情景演绎 | 支持开始、对话、提示、结束、重试幂等 | CASE-006 |
| 知识库版本 | 支持 draft/processing/tested/published 等状态 | `test_kb_lifecycle.py` |
| 真实讯飞 RAG | 尚未完成 | 等待 Workflow 和知识库配置 |

## 6. 部署和运行状态

### 6.1 服务器

| 项目 | 当前记录 |
|---|---|
| 服务器 | `root@168.144.36.82` |
| 系统 | Ubuntu 24.04 |
| 规格 | 2 vCPU、8 GB RAM |
| 部署目录 | `/opt/jbgs-course-agent` |
| Docker | 已安装 |
| Caddy | `2.11.4` |
| MariaDB | `10.11.18` |
| Moodle 分支 | `MOODLE_405_STABLE` |
| Agent Adapter | healthy |
| Agent UI | healthy |
| Moodle | healthy |
| MariaDB | healthy |
| Caddy | running |
| 最新记录备份 | `/opt/jbgs-course-agent/backups/20260722-000306` |

2026-07-25 复核时，服务器核心容器仍在运行，公网课程首页和 Agent 页面均返回 HTTP 200。

### 6.2 预览地址

- [课程平台首页](http://168.144.36.82/)
- [Agent 页面](http://168.144.36.82/agent/)

当前为 IP + HTTP 预览，不是最终比赛 Demo 地址。正式环境需要：

1. 购买或配置域名。
2. 将 DNS 指向服务器。
3. 修改 `SITE_HOST`。
4. 将 `MOODLE_WWWROOT` 改为 `https://域名`。
5. 使用 `docker-compose.https.yml` 重建 Caddy。
6. 运行 HTTPS 入口和证书检查。

### 6.3 网络安全状态

- UFW 已启用。
- 公网只允许 SSH、HTTP、HTTPS。
- MariaDB、Agent Adapter、Flowise、Qdrant 和 Model Gateway 没有直接发布宿主机端口。
- Flowise、Qdrant 和历史模型网关只在 Docker 内网/历史 profile 使用。
- 讯飞密钥只允许出现在服务器端 `.env`，不进入前端、GitHub、备份或日志。

## 7. 自动化验收状态

最后记录的完整本地回归运行号为：

```text
local-regression-20260722-primary-v12
```

本次文档整理于 2026-07-25 重新执行同一套回归，结果为：

```text
LOCAL_ACCEPTANCE_OK
```

本次复跑额外确认了回环 HTTP Workflow 夹具、真实冒烟脚本解析夹具、Adapter 运行时权限、知识库生命周期、图谱/教材/情景夹具和 Mock 性能基线均通过。运行使用的是本地 Mock/夹具，不能替代讯飞星辰真实 Workflow 验收。

最后记录结果为：

```text
LOCAL-ACCEPTANCE_OK
```

覆盖范围包括：

- Shell 和 Python 语法。
- 课程数据基线。
- API 路由契约，共 48 个路由。
- UI 静态契约。
- Store 规则测试，5/5。
- Adapter 协议测试，10/10。
- 回环 HTTP Workflow 协议测试。
- 真实冒烟脚本解析夹具。
- Adapter 运行时和权限测试。
- 固定 A-001 作业、提交、批改和学情夹具。
- 知识库版本生命周期夹具。
- 图谱、教材和场景夹具。
- 30 个样本的 Mock 性能基线。

### 7.1 已验证但不能替代真实验收的内容

本地 Mock 和回环 HTTP 只能证明协议、权限、错误处理、幂等和业务规则代码可运行，不能证明：

- 讯飞 Workflow 已发布。
- 讯飞平台知识库已绑定。
- 真实模型返回内容正确。
- 真实来源页码可核验。
- 真实用户体验和专业教师评价合格。

### 7.2 服务器提交前审计

服务器上的 `scripts/pre_submission_audit.sh` 当前会阻断两项：

1. `XINGCHEN_WORKFLOW_URL`、`XINGCHEN_FLOW_ID`、`XINGCHEN_API_KEY`、`XINGCHEN_API_SECRET` 缺失。
2. 正式域名和 HTTPS 缺失。

凭据到位后，`scripts/real_workflow_preflight.sh` 会继续检查：

- 配置完整。
- `MOCK_WORKFLOW_MODE=false`。
- `MOCK_AUTH_MODE=false`。
- DB、Moodle、Adapter、UI 为 `healthy`。
- Caddy 处于 `running`。
- 站点配置有效。
- 然后执行五次真实讯飞非流式/流式冒烟。

## 8. 备份和恢复状态

已实现：

- MariaDB SQL 备份。
- Moodle data 备份。
- Adapter SQLite/结构化数据备份。
- Caddy data/config 备份。
- 课程 manifest、图谱基线和来源元数据备份。
- tar 成员级 `.env`、私钥和 Secret 检查。
- SHA-256 校验。
- 历史 Flowise/Qdrant 卷默认排除。
- 每日 cron 备份。
- 独立 Compose project 完整恢复演练。

最后记录恢复点：

```text
/opt/jbgs-course-agent/backups/20260722-000306
```

最后记录的完整恢复结果：

```text
FULL_RESTORE_REHEARSAL_OK
```

恢复演练会创建临时数据库、Moodle、Adapter、UI 和 Caddy，不绑定生产端口，退出后自动清理临时容器、网络和卷。真实讯飞配置和真实用户人工流程仍需在最终提交前单独复跑。

## 9. 竞赛验收门槛

### 9.1 P0 必须全部通过

- 课程访问和身份。
- 讯飞 Agent 调用。
- 课程知识库 RAG。
- 七项教学主功能。
- 对象级权限和数据安全。
- 成绩完整性和教师复核。
- 来源和页码可核验。
- 数据备份和恢复。

### 9.2 P1 必须全部通过

- 移动端体验。
- 性能指标。
- 知识库版本和回滚。
- 故障恢复。
- 教师体验。
- 材料完整性。
- 正式录屏和真实用户反馈。

### 9.3 当前状态矩阵

| 需求 | 当前状态 | 说明 |
|---|---|---|
| Moodle 课程和 6 章课件 | 部分完成 | 底座和管理员冒烟通过，真实角色人工验收待完成 |
| 讯飞 Workflow | 待前置条件 | 凭据和发布版本缺失 |
| 课程知识库 | 部分完成 | 本地来源清单完成，平台知识库 ID/版本和真实命中缺失 |
| 知识图谱 | 部分完成 | 本地和服务器数据存在，真实账号页面复核待完成 |
| 作业和客观评分 | 部分完成 | 本地固定夹具通过，真实 Moodle 成绩回写待完成 |
| 学情建议 | 部分完成 | 规则和资源绑定通过，教师人工验收待完成 |
| 情景演绎和问答 | 部分完成 | Mock 流程通过，真实 Workflow 和来源待完成 |
| 备份恢复和材料 | 部分完成 | 底座恢复通过，真实用户材料和正式案例待完成 |

## 10. 下一阶段执行计划

### 阶段 A：账号和域名交接

需要账号负责人提供：

- 讯飞星辰账号及 Workflow 创建/发布权限。
- 已发布 Workflow 的 `flow_id`。
- API Key 和 API Secret。
- Workflow 的真实输入参数名。
- 讯飞知识库 ID、版本和上传文件清单。
- 讯飞平台实际模型或微调模型 ServiceID。
- 正式 Demo 域名。
- 学生、教师、管理员测试账号。

密钥只写入服务器：

```text
/opt/jbgs-course-agent/deploy/.env
```

### 阶段 B：配置并验证真实 Workflow

在服务器执行：

```bash
bash scripts/check_xingchen_config.sh deploy/.env
bash scripts/real_workflow_preflight.sh deploy/.env
bash scripts/xingchen_smoke.sh
```

验收要求：

- 非流式请求至少成功。
- 五次流式请求全部成功。
- 每次有非空答案。
- 有合法成功帧和结束帧。
- API Key 不出现在输出、日志和前端。

### 阶段 C：知识库和来源验收

1. 创建讯飞课程知识库。
2. 上传 `course-data/xingchen-sources/` 中的来源文本。
3. 保存知识库平台 ID、版本、文件清单和处理状态。
4. 执行三道黄金问题。
5. 核验文件名、章节和页码。
6. 发布通过测试的知识库版本。
7. 绑定 Workflow。
8. 记录真实 request ID、讯飞 sid 和平台版本。

禁止把模型自己生成的文件名或页码当作来源证据。

### 阶段 D：真实角色人工验收

学生流程：

```text
登录 → 课程首页 → 图谱 → 教材 → 作业 → 提交 → 批改结果
→ 学情建议 → 情景演绎 → 知识问答 → 点击来源回教材
```

教师流程：

```text
登录 → 图谱 → 第3章教材 → 生成5道题草稿 → 审核 → 发布作业
→ 查看学生提交 → 批量批改 → 修改主观题 → 查看学情
```

管理员流程：

```text
登录 → 服务状态 → Workflow 状态 → 知识库版本
→ 上传合法/损坏文件 → 三题命中测试 → 发布/回滚 → 备份恢复
```

每一条记录必须使用 `acceptance/test-reports/manual/README.md` 模板。

### 阶段 E：正式材料和最终审计

```bash
bash scripts/assemble_submission_materials.sh
bash scripts/package_submission_code.sh
bash scripts/check_submission_materials.sh
bash scripts/pre_submission_audit.sh
```

最终必须同时满足：

- `PRE_SUBMISSION_READY`。
- `SUBMISSION_MATERIALS_READY`。
- 所有 P0 通过。
- 所有列入本期的 P1 通过。
- 至少两名真实目标用户试用。
- 三个正式案例有真实结果和证据。
- 视频不超过赛方规定时长。
- Demo 地址使用正式 HTTPS 域名。

## 11. 风险清单

| 风险 | 影响 | 当前处理 | 责任方 |
|---|---|---|---|
| 星辰凭据缺失 | 无法执行真实 Agent | 前置门禁已实现，缺失时安全失败 | 账号负责人 |
| Workflow 未发布 | 无法证明讯飞主链路 | 需平台发布后执行真实冒烟 | 账号负责人 |
| 知识库版本未绑定 | 来源不可核验 | 本地 manifest 已准备，等待平台 ID | 账号负责人/开发 |
| 没有正式域名 | 无法正式 HTTPS 展示 | 当前用 IP + HTTP 预览 | 运维 |
| 没有真实角色账号 | 无法完成对象级人工验收 | 已有人工模板和本地夹具 | 教师/管理员 |
| 专业答案未由教师核验 | 不能提交专业案例 | 固定黄金问题待真实复核 | 专业教师 |
| Mock 结果被误当真实结果 | 竞赛材料失真 | 所有报告已明确标注 Mock 限制 | 全体 |
| 备份不是最新代码 | 恢复结果和当前代码可能不一致 | 已有校验和和恢复演练，后续配置后再备份 | 运维 |

## 12. 历史文档和材料索引

完整索引见 [`docs/README.md`](docs/README.md)。当前文档按“计划、部署、验收、案例、提交材料、源数据”分类整理，原始文件路径保留，避免链接失效。

## 13. 当前结论

当前版本已经适合：

- 向队友展示课程平台和 Agent 页面。
- 展示课程数据、图谱、教材、作业和情景功能原型。
- 进行讯飞星辰账号交接和 Workflow 联调。
- 依据已有脚本重复部署和恢复底座。
- 继续补充真实验收和比赛材料。

当前版本不适合直接声称：

- 已完成真实讯飞 Agent 主链路。
- 已完成真实知识库命中和来源核验。
- 已完成教师/学生人工验收。
- 已满足比赛最终提交门槛。
