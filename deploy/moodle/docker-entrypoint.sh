#!/usr/bin/env bash
set -Eeuo pipefail

DATA_ROOT="${MOODLE_DATAROOT:-/var/www/moodledata}"
mkdir -p "$DATA_ROOT"
chown -R www-data:www-data "$DATA_ROOT"

# Recreate config.php when a new container is created. The database and moodledata
# volumes outlive the application image, so config.php must not be image-local state.
php -r '
$values = [
    "dbtype" => getenv("DB_TYPE") ?: "mariadb",
    "dbhost" => getenv("DB_HOST") ?: "db",
    "dbport" => getenv("DB_PORT") ?: "3306",
    "dbname" => getenv("MARIADB_DATABASE") ?: "moodle",
    "dbuser" => getenv("MARIADB_USER") ?: "moodle",
    "dbpass" => getenv("MARIADB_PASSWORD") ?: "",
    "wwwroot" => getenv("MOODLE_WWWROOT") ?: "http://localhost",
    "dataroot" => getenv("MOODLE_DATAROOT") ?: "/var/www/moodledata",
];
$config = "<?php\nunset(\$CFG);\n\$CFG = new stdClass();\nglobal \$CFG;\n";
foreach ($values as $key => $value) {
    $config .= "\$CFG->{$key} = " . var_export($value, true) . ";\n";
}
if (strpos($values["wwwroot"], "https://") === 0) {
    $config .= "\$CFG->sslproxy = true;\n";
}
$config .= "\$CFG->admin = " . var_export(getenv("MOODLE_ADMIN_USER") ?: "admin", true) . ";\n";
$config .= "\$CFG->directorypermissions = 02770;\n\nrequire_once(__DIR__ . \"/lib/setup.php\");\n";
file_put_contents("/var/www/html/config.php", $config, LOCK_EX);
chmod("/var/www/html/config.php", 0640);
'
chown www-data:www-data /var/www/html/config.php

php -r '
$host = getenv("DB_HOST") ?: "db";
$port = (int)(getenv("DB_PORT") ?: 3306);
$user = getenv("MARIADB_USER") ?: "moodle";
$pass = getenv("MARIADB_PASSWORD") ?: "";
$db = getenv("MARIADB_DATABASE") ?: "moodle";
$deadline = time() + 180;
do {
    $conn = @new mysqli($host, $user, $pass, $db, $port);
    if (!$conn->connect_errno) { exit(0); }
    usleep(2000000);
} while (time() < $deadline);
fwrite(STDERR, "Database did not become available\n");
exit(1);
'

if [[ ! -f "$DATA_ROOT/.moodle-installed" ]]; then
    php admin/cli/install_database.php \
        --agree-license \
        --lang=zh_cn \
        --adminuser="${MOODLE_ADMIN_USER}" \
        --adminpass="${MOODLE_ADMIN_PASSWORD}" \
        --adminemail="${MOODLE_ADMIN_EMAIL}" \
        --fullname="${MOODLE_FULLNAME}" \
        --shortname="${MOODLE_SHORTNAME}" \
        --summary="电力系统储能技术课程 Agent 平台"
    touch "$DATA_ROOT/.moodle-installed"
    chown www-data:www-data "$DATA_ROOT/.moodle-installed"
fi

# Install/upgrade bundled local plugins before the first web request. This is
# what registers the new-user onboarding observer on an existing volume.
if [[ "${MOODLE_RUN_UPGRADE:-true}" == "true" ]]; then
    php admin/cli/upgrade.php --non-interactive --lang=zh_cn
fi

if [[ "${MOODLE_SEED_COURSE:-true}" == "true" ]]; then
    # Some CLI-first Moodle installs leave MUC with empty stores/locks. The
    # official writer restores the default persistent file/session caches.
    php -r '
        define("CLI_SCRIPT", true);
        require "/var/www/html/config.php";
        $cache = \core_cache\config::instance();
        if (!$cache->get_locks()) {
            \core_cache\config_writer::create_default_configuration(true);
        }
    '
    php /usr/local/bin/moodle-seed-course.php
fi

# Configure SMTP and Email Registration idempotently from environment variables
php -r '
    define("CLI_SCRIPT", true);
    require "/var/www/html/config.php";
    require_once($CFG->libdir . "/clilib.php");

    $smtphost = getenv("MOODLE_SMTP_HOST");
    if (!empty($smtphost)) {
        set_config("smtphosts", $smtphost);
        set_config("smtpuser", getenv("MOODLE_SMTP_USER") ?: "");
        set_config("smtppass", getenv("MOODLE_SMTP_PASS") ?: "");
        set_config("smtpsecure", getenv("MOODLE_SMTP_SECURE") ?: "ssl");
        set_config("smtpauthtype", getenv("MOODLE_SMTP_AUTHTYPE") ?: "LOGIN");
        set_config("noreplyaddress", getenv("MOODLE_NOREPLY_ADDRESS") ?: (getenv("MOODLE_SMTP_USER") ?: "noreply@example.com"));
        set_config("emailonlyfromnoreplyaddress", 1);
        mtrace("Configured Moodle SMTP: host=" . $smtphost . ", user=" . (getenv("MOODLE_SMTP_USER") ?: "none"));
    }

    $supportemail = getenv("MOODLE_SUPPORT_EMAIL") ?: getenv("MOODLE_SMTP_USER");
    if (!empty($supportemail)) {
        set_config("supportemail", $supportemail);
        set_config("supportname", getenv("MOODLE_SUPPORT_NAME") ?: "电力系统储能技术教学团队");
    }

    if (getenv("MOODLE_EMAIL_ENABLE_REGISTRATION") === "true") {
        $auths = empty($CFG->auth) ? [] : explode(",", $CFG->auth);
        if (!in_array("email", $auths, true)) {
            $auths[] = "email";
            set_config("auth", implode(",", $auths));
        }
        set_config("registerauth", "email");
        mtrace("Configured Moodle email-based self-registration (auth_email enabled)");
    }
'

# The upgrade and seed CLIs intentionally run before Apache and therefore as
# root. Restore Moodle's data-root ownership so the first normal web request
# cannot fail while creating cache/session directories.
chown -R www-data:www-data "$DATA_ROOT"

exec "$@"
