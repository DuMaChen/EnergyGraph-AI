#!/usr/bin/env bash
set -Eeuo pipefail

# Run the deterministic checks that do not require external Xingchen
# credentials. Keeping the order in one script makes a clean-machine rerun
# auditable and prevents a green result from omitting a required layer.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHONPATH_VALUE="${PYTHONPATH:-/tmp/jbgs-agent-deps}"

run_step() {
  printf '\n[LOCAL-ACCEPTANCE] %s\n' "$1"
  shift
  (cd "$ROOT_DIR" && "$@")
}

run_step 'shell and Python syntax' bash -c 'bash -n scripts/*.sh && python3 -m compileall -q agent-adapter scripts'
run_step 'course data baseline' python3 scripts/verify_course_data.py course-data/normalized
run_step 'API route and configuration contract' python3 scripts/test_api_contract.py
run_step 'static Agent UI contract' python3 scripts/test_ui_contract.py
run_step 'structured store rules' python3 -m unittest -q scripts.test_course_store
run_step 'Adapter protocol tests' env PYTHONPATH="$PYTHONPATH_VALUE:$ROOT_DIR/agent-adapter" python3 -m unittest -q agent-adapter/tests/test_main.py
# Binding a loopback port is intentionally opt-in: restricted CI sandboxes
# may forbid it, while the normal deterministic suite must remain runnable
# without network privileges. Run this separately with RUN_HTTP_FIXTURE=1.
if [[ "${RUN_HTTP_FIXTURE:-0}" == "1" ]]; then
run_step 'real HTTP Workflow fixture' env PYTHONPATH="$PYTHONPATH_VALUE" python3 scripts/test_xingchen_http_fixture.py
else
  printf '\n[LOCAL-ACCEPTANCE] real HTTP Workflow fixture (skipped; set RUN_HTTP_FIXTURE=1)\n'
fi
run_step 'real-provider smoke parser fixture' python3 scripts/test_xingchen_smoke_script.py
run_step 'Adapter runtime and permission tests' env PYTHONPATH="$PYTHONPATH_VALUE" python3 scripts/test_adapter_runtime.py
run_step 'fixed assignment and grading fixture' env PYTHONPATH="$PYTHONPATH_VALUE" python3 scripts/test_acceptance_fixture.py
run_step 'knowledge-base lifecycle fixture' env PYTHONPATH="$PYTHONPATH_VALUE" python3 scripts/test_kb_lifecycle.py
run_step 'graph, textbook, and scenario fixture' env PYTHONPATH="$PYTHONPATH_VALUE" python3 scripts/test_graph_scenario_fixture.py
run_step 'mock performance baseline' env PYTHONPATH="$PYTHONPATH_VALUE" python3 scripts/performance_smoke.py

printf '\nLOCAL_ACCEPTANCE_OK\n'
