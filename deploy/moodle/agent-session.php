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
$context = context_course::instance($course->id);

if (!isloggedin() || isguestuser()) {
    http_response_code(401);
    echo json_encode(['error' => 'login_required', 'errorcode' => 'requireloginerror'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Ensure logged-in user is enrolled so they can access the course without roadblocks
if (!is_enrolled($context, $USER, '', true) && !is_siteadmin($USER)) {
    $enrol_plugin = enrol_get_plugin('manual');
    $instances = enrol_get_instances($course->id, true);
    $manual_instance = null;
    foreach ($instances as $instance) {
        if ($instance->enrol === 'manual') {
            $manual_instance = $instance;
            break;
        }
    }
    if ($manual_instance) {
        $student_role = $DB->get_record('role', ['shortname' => 'student']);
        $role_id = $student_role ? $student_role->id : 5;
        $enrol_plugin->enrol_user($manual_instance, $USER->id, $role_id);
    }
}

require_login($course, false);

if (is_siteadmin($USER)) {
    $role = 'admin';
} else if (has_capability('moodle/course:update', $context)) {
    $role = 'teacher';
} else {
    $role = 'student';
}

$deployment_course_id = getenv('COURSE_ID');
$bridge_course_id = ($deployment_course_id !== false && is_numeric($deployment_course_id))
    ? (int)$deployment_course_id
    : (int)$course->id;

$user_record = $DB->get_record('user', ['id' => $USER->id]);
$username = $user_record ? (string)$user_record->username : (string)($USER->username ?? '');
$user_fullname = $user_record ? fullname($user_record) : fullname($USER);
if (empty(trim($user_fullname)) || $user_fullname === ' ') {
    if ($user_record && (!empty($user_record->firstname) || !empty($user_record->lastname))) {
        $user_fullname = trim(($user_record->lastname ?? '') . ($user_record->firstname ?? ''));
    } else {
        $user_fullname = $username;
    }
}

echo json_encode([
    'user_id' => (int)$USER->id,
    'username' => $username,
    'fullname' => (string)$user_fullname,
    'course_id' => $bridge_course_id,
    'role' => $role,
    // Moodle's sesskey is returned only over the authenticated same-origin
    // bridge and is required by Adapter write operations as a CSRF proof.
    'sesskey' => sesskey(),
], JSON_UNESCAPED_UNICODE);

