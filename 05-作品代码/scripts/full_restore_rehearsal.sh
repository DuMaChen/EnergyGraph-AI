#!/usr/bin/env bash
set -Eeuo pipefail

# Start the restored P0 stack in an isolated Compose project. This is more
# complete than restore_rehearsal.sh, but deliberately publishes no host
# ports and removes its temporary volumes on exit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${1:?usage: full_restore_rehearsal.sh BACKUP_DIR}"
ENV_FILE="$ROOT_DIR/deploy/.env"
[[ -d "$BACKUP_DIR" ]] || { printf 'backup directory not found: %s\n' "$BACKUP_DIR" >&2; exit 1; }
[[ -f "$ENV_FILE" ]] || { printf 'deploy/.env is missing\n' >&2; exit 1; }
BACKUP_DIR="$(cd "$BACKUP_DIR" && pwd)"

bash "$ROOT_DIR/scripts/verify_backup.sh" "$BACKUP_DIR" >/dev/null
for file in mariadb.sql agent-data.tar.gz moodledata.tar.gz; do
  [[ -f "$BACKUP_DIR/$file" ]] || { printf 'backup member missing: %s\n' "$file" >&2; exit 1; }
done

project="jbgs-restore-$$"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/jbgs-full-restore.XXXXXX")"
override="$tmp_dir/compose.override.yml"
cleanup() {
  # Compose owns the temporary network and named volumes for this project.
  "${compose[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

# Use explicit names so the tar extraction and Compose mounts are unambiguous.
cat >"$override" <<YAML
services:
  caddy:
    # Compose's normal list merge retains the base 80/443 mappings; !reset
    # explicitly removes them so the rehearsal cannot collide with production.
    ports: !reset []
volumes:
  moodledata:
    name: ${project}-moodledata
  agent_data:
    name: ${project}-agent-data
YAML

compose=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ENV_FILE" \
  --project-name "$project" -f "$ROOT_DIR/deploy/docker-compose.yml" -f "$override")

"${compose[@]}" config >/dev/null
"${compose[@]}" up -d db

db_name="$(grep -E '^MARIADB_DATABASE=' "$ENV_FILE" | tail -1 | cut -d= -f2-)"
db_root_password="$(grep -E '^MARIADB_ROOT_PASSWORD=' "$ENV_FILE" | tail -1 | cut -d= -f2-)"
db_version="$(grep -E '^MARIADB_VERSION=' "$ENV_FILE" | tail -1 | cut -d= -f2-)"
for value in db_name db_root_password db_version; do
  [[ -n "${!value}" ]] || { printf 'database setting is missing: %s\n' "$value" >&2; exit 1; }
done

ready=0
for attempt in $(seq 1 60); do
  if "${compose[@]}" exec -T db mariadb-admin ping -h 127.0.0.1 \
      -u root -p"$db_root_password" --silent >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
[[ "$ready" == 1 ]] || { printf 'isolated MariaDB did not become ready\n' >&2; exit 1; }

# Import before Moodle starts so its entrypoint sees the restored schema rather
# than creating a fresh database and hiding a failed restore.
"${compose[@]}" exec -T db mariadb -u root -p"$db_root_password" "$db_name" \
  < "$BACKUP_DIR/mariadb.sql"

for volume in "${project}-moodledata:moodledata" "${project}-agent-data:agent-data"; do
  name="${volume%%:*}"
  archive="${volume##*:}"
  docker volume create "$name" >/dev/null
  docker run --rm -v "$name:/restore" -v "$BACKUP_DIR/$archive.tar.gz:/backup.tar.gz:ro" \
    alpine:3.20 tar xzf /backup.tar.gz -C /restore
done

"${compose[@]}" up -d moodle agent-adapter agent-ui caddy

for service in db moodle agent-adapter agent-ui caddy; do
  id="$("${compose[@]}" ps -q "$service")"
  state="$(docker inspect --format '{{.State.Status}}' "$id")"
  [[ "$state" == running ]] || { printf '%s did not start: %s\n' "$service" "$state" >&2; exit 1; }
done
for service in db moodle agent-adapter agent-ui; do
  id="$("${compose[@]}" ps -q "$service")"
  health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$id")"
  [[ "$health" == healthy ]] || { printf '%s health is %s\n' "$service" "$health" >&2; exit 1; }
done

course_count="$("${compose[@]}" exec -T db mariadb -N -u root -p"$db_root_password" "$db_name" \
  -e "SELECT COUNT(*) FROM course WHERE shortname='storage-course';")"
[[ "$course_count" == 1 ]] || { printf 'restored course count is %s\n' "$course_count" >&2; exit 1; }
"${compose[@]}" exec -T agent-adapter python3 -c \
  'import urllib.request, json; r=urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=5); d=json.load(r); assert r.status == 200 and d["status"] == "ok"'
printf 'FULL_RESTORE_REHEARSAL_OK project=%s course=%s\n' "$project" "$course_count"
