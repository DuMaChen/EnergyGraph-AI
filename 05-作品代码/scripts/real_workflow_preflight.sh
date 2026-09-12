#!/usr/bin/env bash
set -Eeuo pipefail

# This gate is the first command to run after the account owner supplies
# Xingchen credentials. It intentionally stops before any provider request if
# the server is still in Mock mode or the required runtime services are down.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/deploy/.env}"
[[ -f "$ENV_FILE" ]] || { printf 'CONFIG_FILE_MISSING %s\n' "$ENV_FILE" >&2; exit 1; }

bash "$ROOT_DIR/scripts/check_xingchen_config.sh" "$ENV_FILE"

value_for() {
  (grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-) || true
}

mock_workflow="$(value_for MOCK_WORKFLOW_MODE)"
mock_auth="$(value_for MOCK_AUTH_MODE)"
if [[ "${mock_workflow,,}" != "false" || "${mock_auth,,}" != "false" ]]; then
  printf '%s\n' 'REAL_PREFLIGHT_BLOCKED mock mode is enabled' >&2
  exit 1
fi

# Inspect Docker's state directly instead of assuming a process is reachable;
# this catches a stale container that still has an old environment mounted.
compose=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ENV_FILE")
for service in db moodle agent-adapter agent-ui caddy; do
  container_id="$("${compose[@]}" ps -q "$service")"
  state="$(docker inspect --format '{{.State.Status}}' "$container_id" 2>/dev/null || true)"
  [[ "$state" == "running" ]] || {
    printf 'REAL_PREFLIGHT_BLOCKED service_not_running=%s\n' "$service" >&2
    exit 1
  }
  if [[ "$service" != "caddy" ]]; then
    health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id")"
    [[ "$health" == "healthy" ]] || {
      printf 'REAL_PREFLIGHT_BLOCKED service_not_healthy=%s\n' "$service" >&2
      exit 1
    }
  fi
done

base_url="$(value_for MOODLE_WWWROOT)"
site_host="$(value_for SITE_HOST)"
[[ -n "$base_url" && -n "$site_host" ]] || {
  printf '%s\n' 'REAL_PREFLIGHT_BLOCKED site configuration is incomplete' >&2
  exit 1
}

# The smoke script loads credentials only in this subshell, so the parent
# process and its normal terminal output never receive the secret values.
(
  set -a
  . "$ENV_FILE"
  set +a
  bash "$ROOT_DIR/scripts/xingchen_smoke.sh"
)

printf '%s\n' 'REAL_WORKFLOW_PREFLIGHT_OK'
