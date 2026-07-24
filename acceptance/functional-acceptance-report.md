# 功能验收报告

## 测试元数据

- TEST_RUN_ID：`local-regression-20260722-primary-v12`
- 代码版本：工作区当前版本（服务器已部署；无 Git 提交号）
- 图谱版本/哈希：`graph-baseline.json` / `62544d23ae56ea6df1b8f5bc81d2cd676d7acc847bf1983bcf54bca867c3b4f3`
- 课程 manifest 版本/哈希：`local-v1` / `2ae4acd137d30b673ee425a18c3ed27fb162c95b24ceb3e96c7b29cc11b99f90`
- Workflow 发布版本：Mock 协议夹具；真实讯飞版本待前置条件
- 验收人员：自动化夹具；专业教师和真实学生待人工验收
- 本轮回归：完整 `RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh` 通过；资源限制部署后重新验证。
- 本轮新增验证：UI 契约、业务签名幂等键、HTTP 非安全上下文随机键回退、提交前 HTTPS 配置审计和人工验收记录模板均通过静态/夹具检查。

## 结果

| 编号 | 角色 | 输入夹具 | 预期 | 实际 | request ID | 来源/截图 | 结论 |
|---|---|---|---|---|---|---|---|
| FEAT-001 | 学生 | `test_adapter_runtime.py` | 课程会话和角色功能可用 | Mock 学生会话、角色入口和权限通过 | 临时 request ID | `local-verification-report.md` | 有条件通过：待真实账号页面验收 |
| KG-001 | 教师 | `test_graph_scenario_fixture.py` | 6章/20点和先修路径 | 6章、20点、`kp-3-1 -> kp-3-4` 通过 | 临时 request ID | CASE-006 夹具输出 | 有条件通过 |
| QA-001 | 学生 | `case-001-qa.md` | 真实来源 | Mock SSE 返回 token/source/done，来源经 manifest 校验 | 临时 request ID | CASE-001 | 有条件通过：待真实讯飞 |
| ASSESS-004 | 教师 | `test_acceptance_fixture.py` | 重复评分一致 | 固定作业、重复提交/批改和学生字段隔离通过 | 临时 request ID | CASE-005 | 有条件通过 |
| SIM-002 | 学生 | `test_graph_scenario_fixture.py` | 轮次不重复 | 两个场景、来源保存、重复轮次幂等、结束后拒绝追加通过 | 临时 request ID | CASE-006 | 有条件通过 |

结论：本地自动化验收为“有条件通过”；真实讯飞主链路、真实账号和人工专业复核完成前，禁止作为最终竞赛通过结论。
