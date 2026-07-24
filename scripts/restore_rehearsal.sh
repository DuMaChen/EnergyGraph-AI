#!/usr/bin/env bash
set -Eeuo pipefail

# Restore a backup into temporary storage without touching the live Compose
# volumes. This is intentionally a rehearsal: it validates the database dump,
# application SQLite state, Moodle file tree and Caddy archives, then removes
# every temporary container and directory on exit.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${1:?usage: restore_rehearsal.sh BACKUP_DIR}"
ENV_FILE="${ROOT_DIR}/deploy/.env"
[[ -d "$BACKUP_DIR" ]] || { printf 'backup directory not found: %s\n' "$BACKUP_DIR" >&2; exit 1; }
[[ -f "$ENV_FILE" ]] || { printf 'deploy/.env is missing\n' >&2; exit 1; }
for file in mariadb.sql agent-data.tar.gz moodledata.tar.gz caddy-data.tar.gz caddy-config.tar.gz course-data.tar.gz application-source.tar.gz; do
  [[ -f "$BACKUP_DIR/$file" ]] || { printf 'backup member missing: %s\n' "$file" >&2; exit 1; }
done

env_value() {
  # The deployment template uses simple KEY=value entries. Do not source the
  # file: sourcing would turn a server credential file into executable shell.
  grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-
}

db_name="$(env_value MARIADB_DATABASE)"
db_user="$(env_value MARIADB_USER)"
db_password="$(env_value MARIADB_PASSWORD)"
db_root_password="$(env_value MARIADB_ROOT_PASSWORD)"
db_version="$(env_value MARIADB_VERSION)"
for value in db_name db_user db_password db_root_password db_version; do
  [[ -n "${!value}" ]] || { printf 'required database setting is missing: %s\n' "$value" >&2; exit 1; }
done

# Reuse the exact image selected by the deployed Compose project. Using a
# floating `:latest` tag here would make a restore rehearsal depend on a
# mutable local tag instead of the version that is actually running.
compose=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ENV_FILE")
adapter_image="$("${compose[@]}" images -q agent-adapter | head -1)"
[[ -n "$adapter_image" ]] || {
  printf 'deployed agent-adapter image could not be resolved from Compose\n' >&2
  exit 1
}

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/jbgs-restore.XXXXXX")"
network="jbgs-restore-$$"
db_container="jbgs-restore-db-$$"
cleanup() {
  docker rm -f "$db_container" >/dev/null 2>&1 || true
  docker network rm "$network" >/dev/null 2>&1 || true
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

docker network create "$network" >/dev/null
docker run -d --name "$db_container" --network "$network" \
  -e MARIADB_DATABASE="$db_name" -e MARIADB_USER="$db_user" \
  -e MARIADB_PASSWORD="$db_password" -e MARIADB_ROOT_PASSWORD="$db_root_password" \
  "mariadb:${db_version}" >/dev/null

ready=0
for attempt in $(seq 1 60); do
  if docker exec "$db_container" mariadb-admin ping -h 127.0.0.1 \
      -u root -p"$db_root_password" --silent >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
[[ "$ready" == 1 ]] || { printf 'temporary MariaDB did not become ready\n' >&2; exit 1; }

docker exec -i "$db_container" mariadb -u root -p"$db_root_password" "$db_name" \
  < "$BACKUP_DIR/mariadb.sql"
course_count="$(docker exec "$db_container" mariadb -N -u root -p"$db_root_password" "$db_name" \
  -e "SELECT COUNT(*) FROM course WHERE shortname='storage-course';")"
user_count="$(docker exec "$db_container" mariadb -N -u root -p"$db_root_password" "$db_name" \
  -e 'SELECT COUNT(*) FROM user;')"
[[ "$course_count" == 1 ]] || { printf 'restored course count is %s, expected 1\n' "$course_count" >&2; exit 1; }
[[ "$user_count" -ge 2 ]] || { printf 'restored user count is %s, expected at least 2\n' "$user_count" >&2; exit 1; }

mkdir -p "$tmp_dir/agent" "$tmp_dir/moodledata" "$tmp_dir/caddy-data" "$tmp_dir/caddy-config" "$tmp_dir/course-data"
mkdir -p "$tmp_dir/source"
tar xzf "$BACKUP_DIR/agent-data.tar.gz" -C "$tmp_dir/agent"
tar xzf "$BACKUP_DIR/moodledata.tar.gz" -C "$tmp_dir/moodledata"
tar xzf "$BACKUP_DIR/caddy-data.tar.gz" -C "$tmp_dir/caddy-data"
tar xzf "$BACKUP_DIR/caddy-config.tar.gz" -C "$tmp_dir/caddy-config"
tar xzf "$BACKUP_DIR/course-data.tar.gz" -C "$tmp_dir/course-data"
tar xzf "$BACKUP_DIR/application-source.tar.gz" -C "$tmp_dir/source"

[[ -f "$tmp_dir/agent/course.db" ]] || { printf 'restored Adapter SQLite database is missing\n' >&2; exit 1; }
agent_rows="$(docker run --rm --entrypoint python \
  -v "$tmp_dir/agent:/restore:ro" "$adapter_image" \
  -c 'import sqlite3; db=sqlite3.connect("/restore/course.db"); print(db.execute("select count(*) from knowledge_nodes").fetchone()[0])')"
[[ "$agent_rows" -ge 20 ]] || { printf 'restored Adapter node count is %s, expected at least 20\n' "$agent_rows" >&2; exit 1; }

moodle_files="$(find "$tmp_dir/moodledata/filedir" -type f 2>/dev/null | wc -l | tr -d ' ')"
[[ "$moodle_files" -gt 0 ]] || { printf 'restored Moodle filedir is empty\n' >&2; exit 1; }
[[ -d "$tmp_dir/caddy-data" && -d "$tmp_dir/caddy-config" ]] || { printf 'restored Caddy state is missing\n' >&2; exit 1; }
[[ -f "$tmp_dir/course-data/course-data/normalized/manifest.json" ]] || {
  printf 'restored course manifest is missing\n' >&2
  exit 1
}
[[ -f "$tmp_dir/source/agent-adapter/app/main.py" ]] || { printf 'restored Adapter source is missing\n' >&2; exit 1; }
[[ -f "$tmp_dir/source/deploy/.env.example" ]] || { printf 'restored environment template is missing\n' >&2; exit 1; }
[[ -f "$tmp_dir/source/scripts/backup.sh" ]] || { printf 'restored backup script is missing\n' >&2; exit 1; }

printf 'RESTORE_REHEARSAL_OK course=%s users=%s agent_nodes=%s moodle_files=%s\n' \
  "$course_count" "$user_count" "$agent_rows" "$moodle_files"
