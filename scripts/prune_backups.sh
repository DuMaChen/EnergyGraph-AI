#!/usr/bin/env bash
set -Eeuo pipefail

# Remove only backups that fail the current archive-member security check.
# Preview is the default; deletion requires the explicit flag so an operator
# cannot erase recovery evidence by accidentally omitting a confirmation.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_ROOT="${1:-$ROOT_DIR/backups}"
DELETE_INVALID=0
if [[ "${2:-}" == "--delete-invalid" ]]; then
  DELETE_INVALID=1
elif [[ -n "${2:-}" ]]; then
  printf 'usage: %s [BACKUP_ROOT] [--delete-invalid]\n' "$0" >&2
  exit 2
fi

[[ -d "$BACKUP_ROOT" ]] || { printf 'backup root not found: %s\n' "$BACKUP_ROOT" >&2; exit 1; }
invalid=0
for backup in "$BACKUP_ROOT"/*; do
  [[ -d "$backup" ]] || continue
  if bash "$ROOT_DIR/scripts/verify_backup.sh" "$backup" >/dev/null 2>&1; then
    printf 'KEEP %s\n' "$backup"
    continue
  fi
  invalid=$((invalid + 1))
  if [[ "$DELETE_INVALID" == 1 ]]; then
    # The verification failed before this point, so only the backup directory
    # itself is removed; live Compose volumes are never touched by this script.
    rm -rf -- "$backup"
    printf 'REMOVED_INVALID %s\n' "$backup"
  else
    printf 'INVALID %s (rerun with --delete-invalid to remove)\n' "$backup"
  fi
done

if [[ "$DELETE_INVALID" == 0 && "$invalid" -gt 0 ]]; then
  printf 'INVALID_BACKUPS=%s\n' "$invalid" >&2
  exit 1
fi
printf 'BACKUP_PRUNE_OK invalid=%s deleted=%s\n' "$invalid" "$DELETE_INVALID"
