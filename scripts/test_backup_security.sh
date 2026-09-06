#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERIFY_SCRIPT="$ROOT_DIR/scripts/verify_backup.sh"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/energygraph-backup-security.XXXXXX")"
trap 'rm -rf -- "$TEST_ROOT"' EXIT

fail() {
  printf 'BACKUP_SECURITY_FAIL %s\n' "$1" >&2
  exit 1
}

make_checksums() {
  local backup_dir="$1"
  (cd "$backup_dir" && sha256sum -- * > SHA256SUMS)
}

normal="$TEST_ROOT/normal"
mkdir -p "$normal"
printf 'course metadata only\n' > "$normal/manifest.json"
make_checksums "$normal"
bash "$VERIFY_SCRIPT" "$normal" >/dev/null || fail 'valid backup was rejected'

plain_secret="$TEST_ROOT/plain-secret"
mkdir -p "$plain_secret"
printf 'course metadata only\n' > "$plain_secret/manifest.json"
printf 'never persisted\n' > "$plain_secret/.env"
make_checksums "$plain_secret"
if bash "$VERIFY_SCRIPT" "$plain_secret" >/dev/null 2>&1; then
  fail 'plain .env was accepted'
fi

archive_secret="$TEST_ROOT/archive-secret"
payload="$TEST_ROOT/payload"
mkdir -p "$archive_secret" "$payload/nested"
printf 'course metadata only\n' > "$archive_secret/manifest.json"
printf 'never persisted\n' > "$payload/nested/api.secret"
tar czf "$archive_secret/payload.tar.gz" -C "$payload" .
make_checksums "$archive_secret"
if bash "$VERIFY_SCRIPT" "$archive_secret" >/dev/null 2>&1; then
  fail 'secret archive member was accepted'
fi

printf 'BACKUP_SECURITY_OK cases=3\n'
