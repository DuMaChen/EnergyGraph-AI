<?php
// Internal session bridge for Agent Adapter. It is called only inside the
// Docker network, while Moodle remains the source of truth for login and role.
define('AJAX_SCRIPT', true);
require_once('/var/www/html/config.php');
require_once($CFG->libdir . '/moodlelib.php');

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'method_not_allowed'], JSON_UNESCAPED_UNICODE);
    exit;
}

$course = $DB->get_record('course', ['shortname' => 'storage-course'], '*', MUST_EXIST);
require_login($course, false);
$context = context_course::instance($course->id);

if (is_siteadmin($USER)) {
    $role = 'admin';
} else if (has_capability('moodle/course:update', $context)) {
    $role = 'teacher';
} else {
    $role = 'student';
}

echo json_encode([
    'user_id' => (int)$USER->id,
    'course_id' => (int)$course->id,
    'role' => $role,
    // Moodle's sesskey is returned only over the authenticated same-origin
    // bridge and is required by Adapter write operations as a CSRF proof.
    'sesskey' => sesskey(),
], JSON_UNESCAPED_UNICODE);
