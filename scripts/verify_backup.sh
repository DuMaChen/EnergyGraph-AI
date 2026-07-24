#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_DIR="${1:?usage: verify_backup.sh BACKUP_DIR}"
[[ -d "$BACKUP_DIR" ]] || { printf '%s\n' 'backup directory not found' >&2; exit 1; }
[[ -f "$BACKUP_DIR/SHA256SUMS" ]] || { printf '%s\n' 'SHA256SUMS is missing' >&2; exit 1; }
(cd "$BACKUP_DIR" && sha256sum -c SHA256SUMS)
if find "$BACKUP_DIR" -type f \( -name '.env' -o -name '*.key' -o -name '*.secret' \) -print -quit | grep -q .; then
  printf '%s\n' 'backup contains a forbidden secret file' >&2
  exit 1
fi
# Check archive members as well as the backup directory itself. A forbidden
# file hidden inside a tarball would otherwise pass the filesystem-only check
# until a restore extracted it.
for archive in "$BACKUP_DIR"/*.tar.gz; do
  [[ -f "$archive" ]] || continue
  if tar tzf "$archive" | grep -Eq '(^|/)(\.env|[^/]+\.(key|secret))$'; then
    printf 'backup archive contains a forbidden secret member: %s\n' "$archive" >&2
    exit 1
  fi
done
printf 'BACKUP_VERIFY_OK %s\n' "$BACKUP_DIR"
