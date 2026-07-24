# CASE-006 图谱、教材和情景

- 固定夹具：`test-fixtures/scenarios.json`
- 目标：图谱先修路径、教材页码回跳、两个情景会话、重复轮次和结束状态。
- 情景轮次还必须保存 Workflow 回答、来源证据和完成状态；同一轮重试不得再次调用上游。
- 自动化结果：`PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_graph_scenario_fixture.py` 通过，输出 `CASE006_GRAPH_TEXTBOOK_SCENARIO_OK`。
- 已覆盖：6 章/20 个节点、先修路径 `kp-3-1 -> kp-3-4`、教材资源页码定位、两个固定场景、来源证据保存、同一幂等键重试、其他学生越权和结束后禁止追加轮次。
- 限制：当前为本地 Mock Workflow 夹具；真实讯飞来源、浏览器录屏和教师/学生人工评价仍待外部条件。
- 结论：本地协议通过；竞赛正式案例暂记为“待真实环境复测”。
