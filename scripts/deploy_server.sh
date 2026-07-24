#!/usr/bin/env bash
set -Eeuo pipefail

# Stream the project to the server without ever copying deploy/.env. The
# server's existing .env contains its own generated secrets and must remain
# server-side state.
SERVER="${SERVER:-root@168.144.36.82}"
REMOTE_ROOT="${REMOTE_ROOT:-/opt/jbgs-course-agent}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v ssh >/dev/null || { printf '%s\n' 'ssh is required'; exit 1; }
command -v tar >/dev/null || { printf '%s\n' 'tar is required'; exit 1; }
[[ -f "$ROOT_DIR/deploy/.env.example" ]] || { printf '%s\n' 'deploy/.env.example is missing'; exit 1; }

ssh "$SERVER" "mkdir -p '$REMOTE_ROOT'"
# Final competition attachments are local release artifacts, not runtime
# inputs; keep videos, reports and code archives off the application host.
tar czf - \
  --exclude='./deploy/.env' --exclude='./.env' --exclude='./.git' \
  --exclude='./backups' \
  --exclude='*/__pycache__' --exclude='*/.pytest_cache' \
  --exclude='*/._*' --exclude='./._*' --exclude='*/.DS_Store' --exclude='./.DS_Store' \
  --exclude='./01-参赛信息' --exclude='./02-伦理与安全合规性声明' \
  --exclude='./03-作品Demo' --exclude='./04-作品方案' \
  --exclude='./05-作品代码' --exclude='./06-效果验证报告' \
  --exclude='./07-其他材料' \
  -C "$ROOT_DIR" . | ssh "$SERVER" "tar xzf - -C '$REMOTE_ROOT'"

ssh "$SERVER" "test -f '$REMOTE_ROOT/deploy/.env' || { echo 'remote deploy/.env is missing; configure it out of band' >&2; exit 1; }"
ssh "$SERVER" "for key in AGENT_BRIDGE_TOKEN AGENT_UID_SALT; do value=\$(grep -E \"^\${key}=\" '$REMOTE_ROOT/deploy/.env' | tail -1 | cut -d= -f2-); if [[ -z \"\$value\" || \"\$value\" == replace-with-* ]]; then echo \"remote \${key} is missing or still a placeholder\" >&2; exit 1; fi; done"
ssh "$SERVER" "docker compose --project-directory '$REMOTE_ROOT/deploy' --env-file '$REMOTE_ROOT/deploy/.env' config >/dev/null"
ssh "$SERVER" "docker compose --project-directory '$REMOTE_ROOT/deploy' --env-file '$REMOTE_ROOT/deploy/.env' up -d --build db moodle agent-adapter agent-ui caddy"
# Caddy mounts its configuration as a read-only file. Compose does not always
# recreate a container when only that bind-mounted file changes, so explicitly
# restart it before validating the newly synchronized same-origin routes.
ssh "$SERVER" "docker compose --project-directory '$REMOTE_ROOT/deploy' --env-file '$REMOTE_ROOT/deploy/.env' restart caddy"
ssh "$SERVER" "docker compose --project-directory '$REMOTE_ROOT/deploy' --env-file '$REMOTE_ROOT/deploy/.env' ps"
ssh "$SERVER" "cd '$REMOTE_ROOT' && BASE_URL=http://127.0.0.1 BASE_HOST=\$(grep -E '^SITE_HOST=' '$REMOTE_ROOT/deploy/.env' | tail -1 | cut -d= -f2-) bash scripts/smoke_acceptance.sh"
ssh "$SERVER" "cd '$REMOTE_ROOT' && BASE_URL=http://127.0.0.1 SITE_HOST=\$(grep -E '^SITE_HOST=' '$REMOTE_ROOT/deploy/.env' | tail -1 | cut -d= -f2-) bash scripts/moodle_login_smoke.sh '$REMOTE_ROOT/deploy/.env'"
