#!/usr/bin/env bash
set -Eeuo pipefail

# Assemble only reviewed, non-secret material into the competition folders.
# Runtime data, course PDFs, server backups and every .env file stay outside
# the submission tree; this prevents a convenient packaging command from
# accidentally turning credentials or student data into an attachment.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

copy_material() {
  local source="$1" destination="$2"
  mkdir -p "$(dirname "$ROOT_DIR/$destination")"
  cp "$ROOT_DIR/$source" "$ROOT_DIR/$destination"
}

copy_material 'acceptance/ethics-and-safety-statement.md' \
  '02-伦理与安全合规性声明/ethics-and-safety-statement.md'
copy_material 'acceptance/ethics-and-safety-statement.pdf' \
  '02-伦理与安全合规性声明/ethics-and-safety-statement.pdf'
copy_material 'IMPLEMENTATION_PLAN.md' '04-作品方案/IMPLEMENTATION_PLAN.md'
copy_material 'deploy/README.md' '05-作品代码/deployment-readme.md'
copy_material 'acceptance/requirements-matrix.md' \
  '06-效果验证报告/requirements-matrix.md'
copy_material 'acceptance/functional-acceptance-report.md' \
  '06-效果验证报告/functional-acceptance-report.md'
copy_material 'acceptance/security-and-compliance-report.md' \
  '06-效果验证报告/security-and-compliance-report.md'
copy_material 'acceptance/reproducibility-report.md' \
  '06-效果验证报告/reproducibility-report.md'
copy_material 'acceptance/local-verification-report.md' \
  '06-效果验证报告/local-verification-report.md'
copy_material 'acceptance/test-reports/manual/README.md' \
  '06-效果验证报告/manual-acceptance-template.md'

printf '%s\n' 'SUBMISSION_MATERIALS_ASSEMBLED'
printf '%s\n' 'Review the generated files, then run scripts/check_submission_materials.sh.'
