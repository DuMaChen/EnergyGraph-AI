#!/usr/bin/env bash
set -Eeuo pipefail
trap 'printf "MOODLE_LOGIN_SMOKE_ERROR line=%s\n" "$LINENO" >&2' ERR

# Exercise the real Moodle login and course page through Caddy. Credentials
# are read without sourcing the server .env and are never printed. The cookie
# jar and downloaded HTML are temporary and removed by the exit trap.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-$ROOT_DIR/deploy/.env}"
BASE_URL="${BASE_URL:-https://energygraph.icu}"
SITE_HOST="${SITE_HOST:-$(grep -E '^SITE_HOST=' "$ENV_FILE" | tail -1 | cut -d= -f2- || true)}"
[[ -f "$ENV_FILE" ]] || { printf 'deploy/.env is missing\n' >&2; exit 1; }
[[ -n "$SITE_HOST" ]] || { printf 'SITE_HOST is missing\n' >&2; exit 1; }
command -v curl >/dev/null || { printf 'curl is required\n' >&2; exit 1; }
command -v python3 >/dev/null || { printf 'python3 is required\n' >&2; exit 1; }

value_for() {
  # Missing values are handled by the explicit validation below.
  (grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-) || true
}

admin_user="$(value_for MOODLE_ADMIN_USER)"
admin_password="$(value_for MOODLE_ADMIN_PASSWORD)"
[[ -n "$admin_user" && -n "$admin_password" ]] || {
  printf 'Moodle administrator configuration is incomplete\n' >&2
  exit 1
}
db_name="$(value_for MARIADB_DATABASE)"
db_user="$(value_for MARIADB_USER)"
db_password="$(value_for MARIADB_PASSWORD)"
[[ -n "$db_name" && -n "$db_user" && -n "$db_password" ]] || {
  printf 'Moodle database configuration is incomplete\n' >&2
  exit 1
}
compose=(docker compose --project-directory "$ROOT_DIR/deploy" --env-file "$ENV_FILE")

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/moodle-smoke.XXXXXX")"
jar="$tmp_dir/cookies.txt"
login_page="$tmp_dir/login.html"
course_page="$tmp_dir/course.html"
trap 'rm -rf "$tmp_dir"' EXIT

curl_args=(-sS --max-time 20 -H "Host: $SITE_HOST" -c "$jar" -b "$jar")
curl "${curl_args[@]}" "$BASE_URL/login/index.php" -o "$login_page"
logintoken="$(python3 - "$login_page" <<'PY'
from html.parser import HTMLParser
import sys

class LoginTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = ""
    def handle_starttag(self, tag, attrs):
        if tag != "input":
            return
        values = dict(attrs)
        if values.get("name") == "logintoken":
            self.token = values.get("value", "")

parser = LoginTokenParser()
parser.feed(open(sys.argv[1], encoding="utf-8", errors="replace").read())
print(parser.token)
PY
)"

form=(--data-urlencode "username=$admin_user" --data-urlencode "password=$admin_password")
[[ -n "$logintoken" ]] && form+=(--data-urlencode "logintoken=$logintoken")
# Do not force POST across redirects. Curl will POST the login form first and
# then follow Moodle's normal redirect as GET, preserving the authenticated
# session instead of requesting the course page with an invalid method.
curl "${curl_args[@]}" -L "${form[@]}" "$BASE_URL/login/index.php" \
  -o "$tmp_dir/after-login.html" -w '%{http_code}\t%{url_effective}\n' > "$tmp_dir/login-meta.txt"

course_index="$tmp_dir/course-index.html"
curl "${curl_args[@]}" -L "$BASE_URL/course/index.php" -o "$course_index"
course_path="$(python3 - "$course_index" <<'PY'
from html.parser import HTMLParser
import sys

class CourseLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = ""
        self._candidate = ""
        self._text = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._candidate = dict(attrs).get("href", "")
            self._text = []
    def handle_data(self, data):
        if self._candidate:
            self._text.append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self._candidate:
            if "电力系统储能技术" in "".join(self._text):
                self.href = self._candidate
            self._candidate = ""

parser = CourseLinkParser()
parser.feed(open(sys.argv[1], encoding="utf-8", errors="replace").read())
print(parser.href)
PY
)"
if [[ -z "$course_path" ]]; then
  # Administrators may be redirected away from the course index. Query the
  # course ID by its stable shortname instead of assuming a numeric ID.
  course_id="$("${compose[@]}" exec -T db mariadb -N -u "$db_user" -p"$db_password" "$db_name" \
    -e "SELECT id FROM course WHERE shortname='storage-course' AND id <> 1 LIMIT 1;" 2>/dev/null | tr -d '[:space:]' || true)"
  [[ "$course_id" =~ ^[0-9]+$ ]] || { printf 'teaching course ID could not be resolved\n' >&2; exit 1; }
  course_path="/course/view.php?id=$course_id"
fi
case "$course_path" in
  http://*|https://*) course_url="$course_path" ;;
  *) course_url="$BASE_URL$course_path" ;;
esac
curl "${curl_args[@]}" -L "$course_url" -o "$course_page"
grep -q '电力系统储能技术' "$course_page" || { printf 'course title not found at %s\n' "$course_path" >&2; exit 1; }
grep -q '课程 Agent' "$course_page" || { printf 'Agent entry not found on course page\n' >&2; exit 1; }
grep -q 'src="/agent/"' "$course_page" || { printf 'Agent iframe not found on course page\n' >&2; exit 1; }

for chapter in \
  '第1章 概述' \
  '第2章 电力系统与储能技术的应用' \
  '第3章 电力储能系统的组成及工作原理' \
  '第4章 电力储能系统的规划配置' \
  '第5章 电力储能系统的接入与运行控制' \
  '第6章 电力储能系统的性能检测与评估'; do
  grep -q "$chapter" "$course_page" || { printf 'missing chapter: %s\n' "$chapter" >&2; exit 1; }
done

resource_count="$( (grep -o 'mod/resource/view.php' "$course_page" || true) | wc -l | tr -d ' ')"
[[ "$resource_count" -ge 20 ]] || { printf 'course resource count is %s, expected at least 20\n' "$resource_count" >&2; exit 1; }
printf 'MOODLE_LOGIN_SMOKE_OK path=%s chapters=6 resources=%s\n' "$course_path" "$resource_count"
