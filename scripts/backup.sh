#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ROOT_DIR/deploy/.env")
BACKUP_ROOT="${1:-$ROOT_DIR/backups}"
# Docker bind mounts require an absolute host path. Normalize the user
# argument up front so `backup.sh backups` behaves the same as an absolute
# path and cannot accidentally create a named Docker volume.
mkdir -p "$BACKUP_ROOT"
BACKUP_ROOT="$(cd "$BACKUP_ROOT" && pwd)"
STAMP="$(date '+%Y%m%d-%H%M%S')"
DEST="$BACKUP_ROOT/$STAMP"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

mkdir -p "$DEST"
chmod 700 "$DEST"
[[ -f "$ROOT_DIR/deploy/.env" ]] || fail "deploy/.env is missing"

printf '%s\n' '[BACKUP] exporting MariaDB'
"${COMPOSE[@]}" exec -T db sh -c \
  'mariadb-dump --single-transaction --routines --events -u root -p"$MARIADB_ROOT_PASSWORD" "$MARIADB_DATABASE"' \
  > "$DEST/mariadb.sql"
chmod 600 "$DEST/mariadb.sql"

volume_for() {
  local service="$1" destination="$2" id
  id="$("${COMPOSE[@]}" ps -q "$service")"
  [[ -n "$id" ]] || fail "$service is not running"
  docker inspect --format "{{range .Mounts}}{{if eq .Destination \"$destination\"}}{{.Name}}{{end}}{{end}}" "$id"
}

archive_volume() {
  local name="$1" output="$2"
  [[ -n "$name" ]] || fail "could not resolve volume for $output"
  docker run --rm \
    -v "$name:/source:ro" \
    -v "$DEST:/backup" \
    alpine:3.20 tar czf "/backup/$output" -C /source .
  chmod 600 "$DEST/$output"
}

printf '%s\n' '[BACKUP] archiving persistent application data'
archive_volume "$(volume_for moodle /var/www/moodledata)" moodledata.tar.gz
archive_volume "$(volume_for agent-adapter /app/data)" agent-data.tar.gz
archive_volume "$(volume_for caddy /data)" caddy-data.tar.gz
archive_volume "$(volume_for caddy /config)" caddy-config.tar.gz

# Course source files and baselines are part of the restore contract. The
# server-side .env is intentionally excluded; credentials must be re-entered
# out of band during a restore.
printf '%s\n' '[BACKUP] archiving non-secret course manifests and source metadata'
tar czf "$DEST/course-data.tar.gz" \
  --exclude='deploy/.env' --exclude='*.key' --exclude='*.secret' \
  -C "$ROOT_DIR" course-data 2>/dev/null || fail "course-data archive failed"
chmod 600 "$DEST/course-data.tar.gz"

# Reproducibility also depends on the adapter, UI, deployment templates and
# acceptance scripts. Archive those non-secret inputs so a restore does not
# silently depend on an unrecorded developer checkout; the live .env remains
# deliberately excluded and must be re-entered out of band.
printf '%s\n' '[BACKUP] archiving non-secret source and acceptance material'
tar czf "$DEST/application-source.tar.gz" \
  --exclude='deploy/.env' --exclude='./backups' \
  --exclude='*/__pycache__' --exclude='*/.pytest_cache' \
  -C "$ROOT_DIR" \
  agent-adapter agent-ui deploy scripts acceptance IMPLEMENTATION_PLAN.md \
  model-gateway ingestion .gitignore 2>/dev/null || fail "application source archive failed"
chmod 600 "$DEST/application-source.tar.gz"

# Flowise and Qdrant are historical, non-P0 services in the current plan.
# Their volumes may contain provider tokens or generated signing keys, so the
# competition backup deliberately omits them instead of copying credentials
# from an excluded service into an otherwise restorable artifact.

sha256sum "$DEST"/* > "$DEST/SHA256SUMS"
chmod 600 "$DEST/SHA256SUMS"
printf 'BACKUP CREATED: %s\n' "$DEST"
