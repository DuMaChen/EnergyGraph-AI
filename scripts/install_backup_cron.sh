#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_ROOT="${1:-/var/backups/jbgs-course-agent}"
CRON_FILE="/etc/cron.d/jbgs-course-agent-backup"

[[ "$(id -u)" == 0 ]] || { printf '%s\n' 'run as root'; exit 1; }
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
# Keep the schedule explicit and do not put any secret in the cron file.
# The source archive may not preserve executable bits on every deployment
# path. Invoke Bash explicitly so the scheduled backup does not fail with
# Permission denied after a clean checkout or tar-based synchronization.
printf '17 3 * * * root /bin/bash %q %q >>/var/log/jbgs-course-agent-backup.log 2>&1\n' \
  "$ROOT_DIR/scripts/backup.sh" "$BACKUP_ROOT" > "$CRON_FILE"
chmod 600 "$CRON_FILE"
printf 'installed %s\n' "$CRON_FILE"
