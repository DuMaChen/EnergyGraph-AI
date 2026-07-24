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

exec "$@"
