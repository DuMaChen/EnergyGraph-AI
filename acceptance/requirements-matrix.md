# 需求合规矩阵

| 需求编号 | 需求/证据 | 状态 | 证据位置 | 负责人 | 复核日期 |
|---|---|---|---|---|---|
| R-001 | Moodle 课程、六章课件和登录态 | 部分完成 | `deploy/moodle/seed-course.php`；`acceptance/local-verification-report.md`；服务器课程种子和服务健康已通过，真实账号登录待人工验收 |  | 2026-07-22 |
| R-002 | 讯飞星辰 Workflow 主链路 | 待前置条件 | `agent-adapter/app/main.py`；待 `flow_id`、凭证和真实调用证据 | 讯飞账号负责人 | 2026-07-22 |
| R-003 | 课程知识库版本和来源清单 | 部分完成 | `agent-adapter/app/course_store.py`, `scripts/export_xingchen_sources.py`；本地来源清单已生成，待讯飞平台版本 ID 和真实命中证据回填 |  | 2026-07-22 |
| R-004 | 知识图谱六章、20 个知识点 | 部分完成 | `scripts/build_course_baseline.py`；本地 6 章/20 点/17 条关系通过，服务器 Adapter 挂载课程数据，待真实账号页面验收 |  | 2026-07-22 |
| R-005 | 题目、提交、确定性客观评分 | 部分完成 | `scripts/test_acceptance_fixture.py`, `agent-adapter/app/course_store.py`, `deploy/moodle/grade-sync.php`；本地契约通过，待真实 Moodle 账号回写复测 |  | 2026-07-22 |
| R-006 | 学情规则和建议 | 部分完成 | `scripts/test_course_store.py`, `learning-rule-v1`；待固定教师夹具人工验收 |  | 2026-07-22 |
| R-007 | 两个情景演绎和问答来源 | 部分完成 | `/api/scenarios/*`, `/api/course-agent/chat`；Mock 已通过，待真实 Workflow |  | 2026-07-22 |
| R-008 | 备份恢复和竞赛材料 | 部分完成 | `scripts/backup.sh`, `scripts/verify_backup.sh`, `scripts/full_restore_rehearsal.sh`, `acceptance/deployment-checklist.md`；独立 Compose 完整服务恢复已通过，真实用户材料和三个正式案例复跑待完成 |  | 2026-07-22 |

状态只能使用：`已完成`、`部分完成`、`待前置条件`、`未完成`、`不适用`。
真实讯飞链路不得用 Mock 结果替代证据。
