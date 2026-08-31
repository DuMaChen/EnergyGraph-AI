#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ROOT_DIR/deploy/.env")
BASE_URL="${BASE_URL:-https://energygraph.icu}"
BASE_HOST="${BASE_HOST:-}"

# A request to 127.0.0.1 reaches Caddy with a different Host header than the
# configured site address. Resolve the configured host for loopback checks so
# the fallback Moodle site cannot produce a false green API result.
if [[ -z "$BASE_HOST" && "$BASE_URL" =~ ^https?://(127\.0\.0\.1|localhost)(:[0-9]+)?(/|$) ]]; then
  BASE_HOST="$(grep -E '^SITE_HOST=' "$ROOT_DIR/deploy/.env" | tail -1 | cut -d= -f2- || true)"
fi

curl_base() {
  if [[ -n "$BASE_HOST" ]]; then
    curl -H "Host: $BASE_HOST" "$@"
  else
    curl "$@"
  fi
}

fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
command -v docker >/dev/null || fail "docker is required"
command -v curl >/dev/null || fail "curl is required"
[[ -f "$ROOT_DIR/deploy/.env" ]] || fail "deploy/.env is missing"

# The remote host only needs POSIX shell tools. Prefer ripgrep locally, but
# keep the acceptance script runnable on minimal Ubuntu images as well.
if command -v rg >/dev/null; then
  search_source() { rg -n --hidden -g '!.env' -g '!deploy/.env' -g '!**/.git/**' -g '!**/__pycache__/**' -g '!**/.pytest_cache/**' "$1" "$ROOT_DIR"; }
  has_source() { rg -q --hidden -g '!.env' -g '!deploy/.env' -g '!**/.git/**' -g '!**/__pycache__/**' -g '!**/.pytest_cache/**' "$1" "$ROOT_DIR"; }
else
  search_source() { grep -REn --exclude='*.env' --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.pytest_cache "$1" "$ROOT_DIR"; }
  has_source() { grep -REq --exclude='*.env' --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.pytest_cache "$1" "$ROOT_DIR"; }
fi

printf '%s\n' '[INF-001] validating the new Moodle + Agent Adapter compose stack'
"${COMPOSE[@]}" config >/dev/null
grep -Eq 'path /api/\*' "$ROOT_DIR/deploy/caddy/Caddyfile" \
  || fail 'Caddy does not route the complete same-origin API prefix to the Adapter'

if [[ "${RUN_UP:-0}" == "1" ]]; then
  printf '%s\n' '[INF-002] building and starting required services'
  "${COMPOSE[@]}" up -d --build db moodle agent-adapter agent-ui caddy
fi

required_services=(db moodle agent-adapter agent-ui caddy)
healthy_services=(db moodle agent-adapter agent-ui)
container_id() { "${COMPOSE[@]}" ps -q "$1"; }

printf '%s\n' '[INF-002] checking required containers'
for service in "${required_services[@]}"; do
  id="$(container_id "$service")"
  [[ -n "$id" ]] || fail "$service has no container"
  state="$(docker inspect --format '{{.State.Status}}' "$id")"
  [[ "$state" == running ]] || fail "$service state is $state"
done
for service in "${healthy_services[@]}"; do
  id="$(container_id "$service")"
  health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$id")"
  [[ "$health" == healthy ]] || fail "$service health is $health"
done

printf '%s\n' '[INF-003] checking public Moodle and Agent routes'
for path in / /agent/; do
  code="$(curl_base -sS -o /dev/null -w '%{http_code}' --max-time 15 "$BASE_URL$path")"
  case "$code" in 200|301|302|303|307|308) ;; *) fail "$path returned HTTP $code" ;; esac
done
api_code="$(curl_base -sS -o /dev/null -w '%{http_code}' -X POST --max-time 15 "$BASE_URL/api/course/session/open")"
case "$api_code" in
  401|502|307|308) ;;
  *) fail "/api/course/session/open returned unexpected HTTP $api_code without a Moodle session" ;;
esac

printf '%s\n' '[FEAT-001] checking Adapter health inside the Docker network'
"${COMPOSE[@]}" exec -T agent-adapter python -c \
  'import urllib.request, json; r=urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=5); d=json.load(r); assert r.status == 200 and d["status"] == "ok"'

printf '%s\n' '[SEC-002] scanning source files for obvious secret material'
if search_source '(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----)'; then
  fail "possible secret material found in source tree"
fi

printf '%s\n' '[HISTORICAL] Flowise/Qdrant/model-gateway are excluded from new P0/P1 smoke acceptance'
printf '%s\n' 'SMOKE ACCEPTANCE PASSED'
