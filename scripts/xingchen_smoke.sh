#!/usr/bin/env bash
set -Eeuo pipefail

# Real-provider smoke test. It writes only HTTP status and aggregate counts to
# stdout; the answer stream is kept in a mode-600 temporary file and deleted.
: "${XINGCHEN_WORKFLOW_URL:?set XINGCHEN_WORKFLOW_URL}"
: "${XINGCHEN_FLOW_ID:?set XINGCHEN_FLOW_ID}"
: "${XINGCHEN_API_KEY:?set XINGCHEN_API_KEY}"
: "${XINGCHEN_API_SECRET:?set XINGCHEN_API_SECRET}"
export XINGCHEN_INPUT_NAME="${XINGCHEN_INPUT_NAME:-AGENT_USER_INPUT}"
command -v curl >/dev/null || { printf '%s\n' 'curl is required'; exit 1; }
command -v python3 >/dev/null || { printf '%s\n' 'python3 is required'; exit 1; }

tmp="$(mktemp)"
chmod 600 "$tmp"
trap 'rm -f "$tmp"' EXIT
success=0
# Check the provider's ordinary JSON contract separately from the five-call
# streaming smoke. This catches a workflow that is published but misconfigured
# for one response mode before the UI is tested.
body="$(python3 -c 'import json,os; print(json.dumps({"flow_id":os.environ["XINGCHEN_FLOW_ID"],"uid":"acceptance-json-user","parameters":{os.environ["XINGCHEN_INPUT_NAME"]:"请回答：什么是储能变流器？","AGENT_MODE":"qa"},"stream":False},ensure_ascii=False))')"
status="$(curl -sS --max-time "${XINGCHEN_TIMEOUT_SECONDS:-90}" \
  -H "Authorization: Bearer ${XINGCHEN_API_KEY}:${XINGCHEN_API_SECRET}" \
  -H 'Content-Type: application/json' -d "$body" -o "$tmp" -w '%{http_code}' "$XINGCHEN_WORKFLOW_URL")" || status=000
if [[ "$status" != "200" ]] || ! python3 - "$tmp" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding='utf-8', errors='replace').read().strip()
try:
    payload = json.loads(raw)
except json.JSONDecodeError:
    raise SystemExit(1)
choices = payload.get('choices') if isinstance(payload, dict) else None
# Xingchen-compatible providers may put the answer in either the streaming
# delta shape or the ordinary message shape. A non-empty answer is required;
# a successful HTTP status with an empty choices array is not a pass.
content = ''
if isinstance(choices, list):
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        item = choice.get('message') or choice.get('delta') or {}
        if isinstance(item, dict):
            content += str(item.get('content') or '')
raise SystemExit(0 if isinstance(payload, dict) and payload.get('code', 0) == 0 and content.strip() else 1)
PY
then
  printf 'XFYUN_NON_STREAM_FAILED status=%s\n' "$status" >&2
  exit 1
fi
for attempt in 1 2 3 4 5; do
  body="$(python3 -c 'import json,os; print(json.dumps({"flow_id":os.environ["XINGCHEN_FLOW_ID"],"uid":"acceptance-smoke-user","parameters":{os.environ["XINGCHEN_INPUT_NAME"]:"请回答：什么是储能变流器？","AGENT_MODE":"qa"},"stream":True},ensure_ascii=False))')"
  status="$(curl -sS --no-buffer --max-time "${XINGCHEN_TIMEOUT_SECONDS:-90}" \
    -H "Authorization: Bearer ${XINGCHEN_API_KEY}:${XINGCHEN_API_SECRET}" \
    -H 'Content-Type: application/json' -d "$body" -o "$tmp" -w '%{http_code}' "$XINGCHEN_WORKFLOW_URL")" || status=000
  if [[ "$status" == 200 ]] && python3 - "$tmp" <<'PY'
import json, sys
has_success = False
has_end = False
has_content = False
has_malformed = False
for raw in open(sys.argv[1], encoding='utf-8', errors='replace'):
    line = raw.strip()
    if line.startswith('data:'):
        line = line[5:].strip()
    if line in {'[DONE]', '[done]'}:
        has_end = True
        continue
    if not line:
        continue
    try:
        frame = json.loads(line)
    except json.JSONDecodeError:
        has_malformed = True
        continue
    if isinstance(frame, dict) and frame.get('code') == 0:
        has_success = True
        choices = frame.get('choices') or []
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            item = choice.get('delta') or choice.get('message') or {}
            if isinstance(item, dict) and str(item.get('content') or '').strip():
                has_content = True
            if choice.get('finish_reason') == 'stop':
                has_end = True
    elif isinstance(frame, dict) and frame.get('code', 0) != 0:
        has_malformed = True
print('', end='')
raise SystemExit(0 if has_success and has_content and has_end and not has_malformed else 1)
PY
  then
    success=$((success + 1))
  fi
done
printf 'XFYUN_REAL_SMOKE success=%s/5\n' "$success"
[[ "$success" == 5 ]]
