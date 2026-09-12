<?php
// Internal grade bridge. It is reachable only on the Docker network and is
// additionally protected by a server-side token shared with Agent Adapter.
define('AJAX_SCRIPT', true);
require_once('/var/www/html/config.php');
require_once($CFG->libdir . '/moodlelib.php');
require_once($CFG->libdir . '/gradelib.php');

header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'method_not_allowed'], JSON_UNESCAPED_UNICODE);
    exit;
}

$expected = getenv('AGENT_BRIDGE_TOKEN') ?: '';
$provided = $_SERVER['HTTP_X_AGENT_BRIDGE_TOKEN'] ?? '';
if ($expected === '' || $provided === '' || !hash_equals($expected, $provided)) {
    http_response_code(403);
    echo json_encode(['error' => 'bridge_forbidden'], JSON_UNESCAPED_UNICODE);
    exit;
}

$course = $DB->get_record('course', ['shortname' => 'storage-course'], '*', MUST_EXIST);
// Server-to-server bridge: the adapter has already authenticated the human
// actor (Moodle session + CSRF + teacher/admin role) and shares this token
// over the internal Docker network. require_login() would issue a redirect on
// the internal HTTP host name and is intentionally not used here; the bridge
// only validates that the graded account actually exists.

try {
    $payload = json_decode(file_get_contents('php://input'), true);
    $user_id = filter_var($payload['user_id'] ?? null, FILTER_VALIDATE_INT);
    $score = filter_var($payload['score'] ?? null, FILTER_VALIDATE_FLOAT);
    $max_score = filter_var($payload['max_score'] ?? null, FILTER_VALIDATE_FLOAT);
    $assignment_id = (string)($payload['assignment_id'] ?? '');
    if (!$user_id || $score === false || $max_score === false || $max_score <= 0 || $score < 0 || $score > $max_score || !preg_match('/^[A-Za-z0-9_-]{1,120}$/', $assignment_id)) {
        http_response_code(422);
        echo json_encode(['error' => 'invalid_grade'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    if (!$DB->record_exists('user', ['id' => $user_id, 'deleted' => 0])) {
        http_response_code(422);
        echo json_encode(['error' => 'unknown_user'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $itemname = '储能技术 Agent 作业 ' . $assignment_id;
    $idnumber = 'agent-assignment-' . $assignment_id;
    $grades = [$user_id => ['userid' => $user_id, 'rawgrade' => $score]];
    $details = [
        'gradetype' => GRADE_TYPE_VALUE,
        'grademin' => 0,
        'grademax' => $max_score,
        'itemname' => $itemname,
        'idnumber' => $idnumber,
    ];
    // Manual gradebook items cannot be written through grade_update (its raw-grade
// path only serves itemtype 'mod' activity items). Use the gradebook API the
// same way a teacher's gradebook edit does: fetch-or-create the manual item by
// idnumber, then update_final_grade for the student.
$itemname = '储能技术 Agent 作业 ' . $assignment_id;
$idnumber = 'agent-assignment-' . $assignment_id;
$grade_item = grade_item::fetch(['courseid' => (int)$course->id, 'idnumber' => $idnumber]);
if (!$grade_item) {
    $grade_item = new grade_item([
        'courseid' => (int)$course->id,
        'itemname' => $itemname,
        'idnumber' => $idnumber,
        'itemtype' => 'manual',
        'gradetype' => GRADE_TYPE_VALUE,
        'grademin' => 0,
        'grademax' => $max_score,
    ]);
    if (!$grade_item->insert()) {
        http_response_code(502);
        echo json_encode(['error' => 'grade_item_create_failed'], JSON_UNESCAPED_UNICODE);
        exit;
    }
}
$grade_item->grademax = $max_score;
$grade_item->update('local_course_agent');
if (!$grade_item->update_final_grade($user_id, $score, 'local_course_agent')) {
    http_response_code(502);
    echo json_encode(['error' => 'grade_update_failed'], JSON_UNESCAPED_UNICODE);
    exit;
}
if ($result != GRADE_UPDATE_OK) {
        http_response_code(502);
        echo json_encode(['error' => 'grade_update_failed', 'code' => $result], JSON_UNESCAPED_UNICODE);
        exit;
    }

    echo json_encode(['status' => 'synced', 'assignment_id' => $assignment_id], JSON_UNESCAPED_UNICODE);

} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode(['error' => 'grade_bridge_exception', 'message' => $e->getMessage()], JSON_UNESCAPED_UNICODE);
}
