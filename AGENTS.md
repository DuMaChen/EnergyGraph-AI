<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

# EnergyGraph-AI: Course Agent Platform Context

## Project Summary
- **Domain**: 电力系统储能技术 (Energy Storage Technology for Power Systems)
- **Architecture**: Moodle 4.5 LMS + FastAPI Adapter (`agent-adapter`) + Single-Page UI (`agent-ui`) + iFlytek Xingchen (讯飞星辰) Workflow + Caddy (Reverse Proxy & HTTPS: `energygraph.icu`).
- **Data Baseline**: 6 Chapters, 20 Courseware PDFs (439 pages), 20 Knowledge Graph Nodes, 17 Graph Relationship Edges.

## Key Paths
- **Backend Adapter**: [`agent-adapter/app/main.py`](file:///agent-adapter/app/main.py)
- **Frontend SPA**: [`agent-ui/index.html`](file:///agent-ui/index.html)
- **Course Data**: [`course-data/normalized/manifest.json`](file:///course-data/normalized/manifest.json) & [`graph-baseline.json`](file:///course-data/normalized/graph-baseline.json)
- **Deployment**: [`deploy/docker-compose.yml`](file:///deploy/docker-compose.yml), [`deploy/caddy/Caddyfile`](file:///deploy/caddy/Caddyfile)
- **Trellis Specs**: [`.trellis/spec/`](file:///.trellis/spec/)

## Validation Commands
```bash
# Run local deterministic acceptance suite
bash scripts/run_local_acceptance.sh

# Verify course data baseline
python3 scripts/verify_course_data.py course-data/normalized

# Test API route contracts
python3 scripts/test_api_contract.py
```
