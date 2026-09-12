#!/usr/bin/env bash
set -Eeuo pipefail

# Build the code attachment from an explicit allow-list. An allow-list is
# safer than archiving the repository root because the workspace also contains
# course originals, local caches, backups and a server-only deploy/.env.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$ROOT_DIR/05-作品代码"
ARCHIVE="$OUTPUT_DIR/作品代码-源文件.tar.gz"
mkdir -p "$OUTPUT_DIR"

tar_args=(
  --exclude='deploy/.env'
  --exclude='*.pdf'
  --exclude='*.zip'
  --exclude='*.xlsx'
  --exclude='*.docx'
  --exclude='*/__pycache__'
  --exclude='*/.pytest_cache'
  --exclude='*.pyc'
  --exclude='*.key'
  --exclude='*.secret'
  --exclude='._*'
  --exclude='*/._*'
  --exclude='.DS_Store'
  --exclude='*/.DS_Store'
)

# Keep the source list explicit so adding a new local artifact cannot silently
# add credentials or private teaching data to the competition attachment.
tar -czf "$ARCHIVE" "${tar_args[@]}" -C "$ROOT_DIR" \
  IMPLEMENTATION_PLAN.md \
  .dockerignore .gitignore \
  agent-adapter agent-ui deploy scripts acceptance \
  course-data/normalized/manifest.json \
  course-data/normalized/graph-baseline.json \
  course-data/xingchen-sources \
  ingestion model-gateway flowise

chmod 600 "$ARCHIVE"
if tar -tzf "$ARCHIVE" | grep -E '(^|/)(\.env|.*\.(key|secret))$' >/dev/null; then
  printf '%s\n' 'FAIL: submission archive contains a secret-like member' >&2
  exit 1
fi

sha256sum "$ARCHIVE" > "$OUTPUT_DIR/作品代码-源文件.sha256"
chmod 600 "$OUTPUT_DIR/作品代码-源文件.sha256"
printf 'SUBMISSION_CODE_ARCHIVE_READY %s\n' "$ARCHIVE"
