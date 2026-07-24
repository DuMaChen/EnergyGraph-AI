# CASE-005 题目、批改和学情

- 固定夹具：`test-fixtures/assignment-A-001.json`
- 目标：草稿审核、作业发布、学生提交、批量评分、主观题待复核、改分审计、学情重算。
- 自动化结果：`PYTHONPATH=/tmp/jbgs-agent-deps python3 scripts/test_acceptance_fixture.py` 通过，输出 `ACCEPTANCE_FIXTURE_OK`。
- 已覆盖：5 题固定作业、草稿发布边界、学生答案隔离、截止时间/尝试次数、重复提交幂等、客观题批改、Agent 初评待教师复核、学生不可见教师字段和确定性学情建议资源。
- 限制：当前为本地 Mock Workflow 夹具；真实 Moodle 成绩回写、教师录屏和真实用户评分仍待外部账号与讯飞凭证。
- 结论：本地协议通过；竞赛正式案例暂记为“待真实环境复测”。
