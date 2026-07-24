#!/usr/bin/env bash
set -Eeuo pipefail

# This is a release gate, not a best-effort smoke test. It deliberately exits
# non-zero while external credentials, domain or human evidence are missing.
# macOS may add `._*` sidecar files during archive/copy operations; they are
# metadata, not source files, so the syntax audit deliberately excludes them.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER="${SERVER:-root@168.144.36.82}"
blockers=0

# The same script runs locally and on the deployed host.  The remote mode
# prevents a second SSH hop, which would require a separate known_hosts entry.
run_server() {
  if [[ "${PRE_SUBMISSION_REMOTE:-0}" == "1" ]]; then
    bash -c "$1"
  else
    ssh "$SERVER" "$1"
  fi
}

blocker() {
  printf 'BLOCKER: %s\n' "$*" >&2
  blockers=$((blockers + 1))
}

printf '%s\n' '[AUDIT] local syntax, data and UI contract'
if ! (cd "$ROOT_DIR" && bash -n scripts/*.sh && find agent-adapter scripts -type f -name '*.py' ! -name '._*' -print0 | xargs -0 -r -n1 python3 -m py_compile && python3 scripts/verify_course_data.py course-data/normalized && python3 scripts/test_ui_contract.py && docker compose --env-file deploy/.env -f deploy/docker-compose.yml config >/dev/null); then
  blocker 'local static/data/Compose audit failed'
fi

printf '%s\n' '[AUDIT] deployed Xingchen configuration presence'
if ! run_server 'cd /opt/jbgs-course-agent && bash scripts/check_xingchen_config.sh deploy/.env' >/tmp/jbgs-xingchen-audit.$$ 2>/tmp/jbgs-xingchen-audit.err; then
  cat /tmp/jbgs-xingchen-audit.$$ 2>/dev/null || true
  blocker 'Xingchen Workflow URL, flow_id or credentials are incomplete'
fi
rm -f /tmp/jbgs-xingchen-audit.$$ /tmp/jbgs-xingchen-audit.err

site_host="$(run_server 'grep -E "^SITE_HOST=" /opt/jbgs-course-agent/deploy/.env | tail -1 | cut -d= -f2-' || true)"
case "$site_host" in
  ''|*[!A-Za-z0-9.-]*|[0-9]*.[0-9]*.[0-9]*.[0-9]*) blocker 'formal demo domain/HTTPS is not configured' ;;
  *)
    # A domain name alone is not enough: Moodle URLs, the HTTPS Compose
    # overlay, and the live TLS listener must all agree before release.
    moodle_wwwroot="$(run_server 'grep -E "^MOODLE_WWWROOT=" /opt/jbgs-course-agent/deploy/.env | tail -1 | cut -d= -f2-' || true)"
    if [[ "$moodle_wwwroot" != "https://$site_host" && "$moodle_wwwroot" != "https://$site_host/" ]]; then
      blocker 'MOODLE_WWWROOT is not the configured HTTPS domain'
    fi
    if ! run_server 'cd /opt/jbgs-course-agent/deploy && docker compose --env-file .env -f docker-compose.yml -f docker-compose.https.yml config >/dev/null'; then
      blocker 'HTTPS Compose configuration is invalid'
    fi
    if ! run_server "curl -kfsS --max-time 10 --resolve '$site_host:443:127.0.0.1' 'https://$site_host/' -o /dev/null"; then
      blocker 'HTTPS listener did not return a successful response'
    fi
    ;;
esac

printf '%s\n' '[AUDIT] deployed server smoke'
if ! run_server 'cd /opt/jbgs-course-agent && BASE_URL=http://127.0.0.1 BASE_HOST=$(grep -E "^SITE_HOST=" deploy/.env | tail -1 | cut -d= -f2-) bash scripts/smoke_acceptance.sh >/dev/null'; then
  blocker 'deployed server smoke failed'
fi

if [[ "$blockers" -eq 0 ]]; then
  printf '%s\n' 'PRE_SUBMISSION_READY'
else
  printf 'PRE_SUBMISSION_BLOCKED blockers=%s\n' "$blockers" >&2
  exit 1
fi
