# Testing & Acceptance Verification Guide

> Multi-tiered acceptance testing methodology and verification protocols for competition delivery.

---

## 1. Testing Pyramid & Gates

```text
[Tier 4: Live Demonstration & Video]   03-作品Demo (Manual video recording)
[Tier 3: Golden Scenario Evaluation]   scripts/real_quality_eval.py, golden-cases/
[Tier 2: Real Workflow Preflight]      scripts/real_workflow_preflight.sh (Requires Xingchen keys)
[Tier 1: Deterministic Local Suite]    scripts/run_local_acceptance.sh (Offline, Mock enabled)
```

---

## 2. Running Local Acceptance

The local acceptance suite verifies all static invariants, API schemas, course data integrity, and store logic without requiring network calls or cloud API keys:

```bash
# Run deterministic local acceptance
bash scripts/run_local_acceptance.sh

# Run with loopback HTTP fixture enabled
RUN_HTTP_FIXTURE=1 bash scripts/run_local_acceptance.sh
```

### Verified Acceptance Checkpoints
1. **Syntax & Compilation**: Python syntax check across `agent-adapter` and `scripts`.
2. **Course Data Baseline**: Verifies 20 PDFs (439 pages), 20 knowledge graph nodes, and 17 edges.
3. **API Contract**: Verifies all 53 FastAPI route signatures against client specs.
4. **Adapter Protocol**: Tests session validation, rate limiting, and CSRF token checks.
5. **Knowledge Base Lifecycle**: Simulates document indexing, chunk retrieval, and citation formatting.

---

## 3. Golden Test Cases

Golden test cases are located in `acceptance/golden-cases/`:
- `case-001-qa.md`: Course Q&A and concept explanation accuracy.
- `case-002-learning.md`: Knowledge path recommendation and weak-point diagnosis.
- `case-003-teacher.md`: Assignment generation, grading assistance, and grade synchronization.
- `case-004-safety.md`: Injection prompt rejection and off-topic filtering.
- `case-005-assessment-and-grading.md`: Objective quiz auto-scoring and subjective question grading.
- `case-006-graph-textbook-scenario.md`: Multi-modal linking between textbook PDF, graph node, and chat.
