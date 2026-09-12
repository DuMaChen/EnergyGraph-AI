#!/usr/bin/env bash
set -Eeuo pipefail

# Validate the external Workflow handoff without sourcing or printing the
# credential file. This makes the next deployment step deterministic while
# keeping API keys and secrets out of terminals, logs and CI artifacts.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/deploy/.env}"
[[ -f "$ENV_FILE" ]] || { printf 'CONFIG_FILE_MISSING %s\n' "$ENV_FILE" >&2; exit 1; }

value_for() {
  # A missing external key is a validation result, not a shell error.
  (grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-) || true
}

failed=0
for key in XINGCHEN_WORKFLOW_URL XINGCHEN_FLOW_ID XINGCHEN_API_KEY XINGCHEN_API_SECRET; do
  value="$(value_for "$key")"
  if [[ -z "$value" || "$value" == replace-with-* ]]; then
    printf '%s=missing\n' "$key"
    failed=1
  else
    printf '%s=present\n' "$key"
  fi
done

url="$(value_for XINGCHEN_WORKFLOW_URL)"
if [[ -n "$url" && "$url" != https://* ]]; then
  printf '%s\n' 'XINGCHEN_WORKFLOW_URL must use HTTPS' >&2
  failed=1
fi

input_name="$(value_for XINGCHEN_INPUT_NAME)"
input_name="${input_name:-AGENT_USER_INPUT}"
if [[ -z "$input_name" || ! "$input_name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  printf '%s\n' 'XINGCHEN_INPUT_NAME is missing or is not a valid parameter name' >&2
  failed=1
fi

if [[ "$failed" == 0 ]]; then
  printf '%s\n' 'XINGCHEN_CONFIG_READY'
else
  printf '%s\n' 'XINGCHEN_CONFIG_INCOMPLETE' >&2
  exit 1
fi
