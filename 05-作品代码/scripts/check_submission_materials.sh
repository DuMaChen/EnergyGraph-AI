#!/usr/bin/env bash
set -Eeuo pipefail

# Check the release folder without treating placeholders as evidence. This is
# intentionally separate from pre_submission_audit.sh because missing videos,
# user records, and competition forms are material gaps rather than runtime
# service failures.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
missing=0

require_file() {
  local path="$1"
  if [[ ! -s "$ROOT_DIR/$path" ]]; then
    printf 'MISSING: %s\n' "$path" >&2
    missing=$((missing + 1))
  fi
}

for directory in \
  '01-参赛信息' \
  '02-伦理与安全合规性声明' \
  '03-作品Demo' \
  '04-作品方案' \
  '05-作品代码' \
  '06-效果验证报告' \
  '07-其他材料'; do
  require_file "$directory/README.md"
done

require_file 'IMPLEMENTATION_PLAN.md'
require_file 'acceptance/ethics-and-safety-statement.pdf'
require_file 'acceptance/requirements-matrix.md'
require_file 'acceptance/functional-acceptance-report.md'
require_file 'acceptance/security-and-compliance-report.md'
require_file 'acceptance/reproducibility-report.md'
require_file 'acceptance/test-reports/manual/README.md'
require_file '05-作品代码/作品代码-源文件.tar.gz'
require_file '05-作品代码/作品代码-源文件.sha256'

archive="$ROOT_DIR/05-作品代码/作品代码-源文件.tar.gz"
checksum="$ROOT_DIR/05-作品代码/作品代码-源文件.sha256"
if [[ -s "$archive" && -s "$checksum" ]]; then
  # Validate both integrity and archive contents at release time. The first
  # check catches accidental replacement; the second catches credentials that
  # may have entered the archive after the packaging script was changed.
  if ! (cd "$(dirname "$archive")" && sha256sum -c "$(basename "$checksum")" >/dev/null 2>&1); then
    printf 'MISSING: code archive SHA-256 does not match\n' >&2
    missing=$((missing + 1))
  fi
  if tar -tzf "$archive" | grep -E '(^|/)(\.env|.*\.(key|secret))$' >/dev/null; then
    printf 'MISSING: code archive contains a secret-like member\n' >&2
    missing=$((missing + 1))
  fi
fi

# These are deliberately required for final submission and are expected to
# remain missing until the domain, real Workflow and human evidence exist.
require_file '03-作品Demo/demo-url.txt'
require_file '03-作品Demo/demo-video.mp4'
require_file '06-效果验证报告/真实人工验收汇总.md'

demo_url_file="$ROOT_DIR/03-作品Demo/demo-url.txt"
demo_video="$ROOT_DIR/03-作品Demo/demo-video.mp4"
manual_summary="$ROOT_DIR/06-效果验证报告/真实人工验收汇总.md"

if [[ -s "$demo_url_file" ]]; then
  demo_url="$(tr -d '[:space:]' < "$demo_url_file")"
  # The release URL must be an HTTPS domain, not the development IP or a
  # documentation placeholder that would make the material appear complete.
  if [[ ! "$demo_url" =~ ^https://[A-Za-z0-9.-]+(/.*)?$ || "$demo_url" =~ https://([0-9]{1,3}\.){3}[0-9]{1,3}(/|$) || "$demo_url" == *example.com* ]]; then
    printf 'MISSING: demo-url.txt is not a formal HTTPS domain\n' >&2
    missing=$((missing + 1))
  fi
fi

if [[ -s "$demo_video" ]]; then
  if ! file "$demo_video" | grep -Eqi 'video|mp4|mpeg|quicktime'; then
    printf 'MISSING: demo-video.mp4 is not recognized as a video file\n' >&2
    missing=$((missing + 1))
  fi
fi

if [[ -s "$manual_summary" ]]; then
  # Require the fields that make a human result auditable. A template or a
  # report that still says "待人工" must not satisfy the final gate.
  for field in '验收编号' '验收人员' '实际结果' '验收结论'; do
    if ! grep -q "$field" "$manual_summary"; then
      printf 'MISSING: manual summary lacks field %s\n' "$field" >&2
      missing=$((missing + 1))
    fi
  done
  if grep -Eq '待(人工|真实|补充)|占位|TBD' "$manual_summary"; then
    printf '%s\n' 'MISSING: manual summary still contains placeholder wording' >&2
    missing=$((missing + 1))
  fi
fi

if [[ "$missing" -eq 0 ]]; then
  printf '%s\n' 'SUBMISSION_MATERIALS_READY'
else
  printf 'SUBMISSION_MATERIALS_INCOMPLETE missing=%s\n' "$missing" >&2
  exit 1
fi
