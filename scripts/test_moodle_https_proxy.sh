#!/usr/bin/env bash
set -Eeuo pipefail

# Runtime regression test for Moodle behind the Caddy HTTPS reverse proxy.
# Run this on the deployment host after the Moodle container is healthy.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ROOT_DIR/deploy/.env")

output="$(${COMPOSE[@]} exec -T moodle php -r '
    define("CLI_SCRIPT", true);
    require "/var/www/html/config.php";
    echo "wwwroot=" . ($CFG->wwwroot ?? "") . PHP_EOL;
    echo "reverseproxy=" . (!empty($CFG->reverseproxy) ? "true" : "false") . PHP_EOL;
    echo "sslproxy=" . (!empty($CFG->sslproxy) ? "true" : "false") . PHP_EOL;
')"
printf '%s\n' "$output"

grep -Fxq 'wwwroot=https://energygraph.icu' <<<"$output"
grep -Fxq 'reverseproxy=false' <<<"$output"
grep -Fxq 'sslproxy=true' <<<"$output"
curl -fsS -L --max-time 20 -o /dev/null https://energygraph.icu/
printf '%s\n' 'MOODLE_HTTPS_PROXY_CONFIG_OK'
