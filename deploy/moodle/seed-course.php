<?php
// Idempotent course bootstrap for the competition demo.
define('CLI_SCRIPT', true);
require_once('/var/www/html/config.php');
require_once($CFG->libdir . '/clilib.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->libdir . '/filelib.php');

global $DB, $CFG, $USER;

// File draft APIs require a real user even when this script runs from CLI.
// Use Moodle's administrator account for the bootstrap-only draft area.
$bootstrapadmin = get_admin();
if ($bootstrapadmin) {
    $USER = $bootstrapadmin;
    // Moodle file APIs inspect the CLI session manager, not only the global
    // variable; without this call the administrator is treated as a guest.
    \core\session\manager::set_user($bootstrapadmin);
}

// Keep the production bootstrap output concise, but make one-off diagnosis
// possible without exposing details to normal web requests.
if (getenv('MOODLE_BOOTSTRAP_DEBUG') === 'true') {
    $DB->set_debug(DEBUG_DEVELOPER);
    set_exception_handler(function (Throwable $exception): void {
        fwrite(STDERR, get_class($exception) . ': ' . $exception->getMessage() . "\n");
        fwrite(STDERR, $exception->getTraceAsString() . "\n");
        exit(1);
    });
}

$courseconfig = [
    'fullname' => getenv('MOODLE_FULLNAME') ?: '电力系统储能技术',
    'shortname' => getenv('MOODLE_SHORTNAME') ?: 'storage-course',
    'summary' => '<p>电力系统储能技术课程 Agent 平台。课程内容、知识点、课件和 AI 生成内容均用于教学辅助，专业回答应以课程来源为准。</p>',
];

$chapters = [
    1 => '第1章 概述',
    2 => '第2章 电力系统与储能技术的应用',
    3 => '第3章 电力储能系统的组成及工作原理',
    4 => '第4章 电力储能系统的规划配置',
    5 => '第5章 电力储能系统的接入与运行控制',
    6 => '第6章 电力储能系统的性能检测与评估',
];

$course = $DB->get_record('course', ['shortname' => $courseconfig['shortname']]);
if ($course && $course->id == (defined('SITEID') ? SITEID : 1)) {
    // The site course is reserved by Moodle for the front page. Older
    // versions of this bootstrap reused ID 1, which made normal course URLs
    // redirect administrators to /admin/index.php. Preserve that site row and
    // create a dedicated teaching course for the Agent platform.
    mtrace('Reserved site course is using the teaching shortname; migrating it to site-home');
    $sitecourse = $course;
    $sitecourse->shortname = 'site-home';
    $sitecourse->fullname = 'Site home';
    $sitecourse->summary = '';
    $sitecourse->summaryformat = FORMAT_HTML;
    $DB->update_record('course', $sitecourse);
    $course = null;
}
if (!$course) {
    $data = (object) [
        'category' => 1,
        'fullname' => $courseconfig['fullname'],
        'shortname' => $courseconfig['shortname'],
        'summary' => $courseconfig['summary'],
        'summary_format' => FORMAT_HTML,
        'format' => 'topics',
        'numsections' => 6,
        'visible' => 1,
        'enablecompletion' => 1,
        'showcompletionconditions' => 1,
    ];
    $course = create_course($data);
    mtrace("Created course {$course->id}: {$course->fullname}");
} else {
    $course->fullname = $courseconfig['fullname'];
    $course->summary = $courseconfig['summary'];
    $course->summaryformat = FORMAT_HTML;
    $course->format = 'topics';
    $course->numsections = 6;
    $DB->update_record('course', $course);
    mtrace("Using existing course {$course->id}: {$course->fullname}");
}

foreach ($chapters as $number => $name) {
    $section = $DB->get_record('course_sections', [
        'course' => $course->id,
        'section' => $number,
    ]);
    // Moodle's normal section helper obtains a request-scoped lock. The
    // bootstrap runs before Apache has a request context, so create only
    // missing rows directly and let normal Moodle code manage later edits.
    if (!$section) {
        $section = (object) [
            'course' => $course->id,
            'section' => $number,
            'name' => $name,
            'summary' => '',
            'summaryformat' => FORMAT_HTML,
            'sequence' => '',
            'visible' => 1,
            'availability' => null,
            'component' => '',
            'itemid' => 0,
            'timemodified' => time(),
        ];
        $section->id = $DB->insert_record('course_sections', $section);
    }
    $section->name = $name;
    $section->summary = '<p>本章课件、知识点和 Agent 学习入口。</p>';
    $section->summaryformat = FORMAT_HTML;
    $section->visible = 1;
    $section->timemodified = time();
    $DB->update_record('course_sections', $section);
}

function add_label_once(stdClass $course, int $sectionnumber, string $idnumber, string $name, string $html): void {
    global $DB;
    $labelmodule = $DB->get_record('modules', ['name' => 'label'], '*', MUST_EXIST);
    $existing = $DB->get_record_sql(
        'SELECT l.id, l.intro, l.introformat FROM {course_modules} cm
          JOIN {label} l ON l.id = cm.instance
         WHERE cm.course = ? AND cm.module = ? AND l.name = ?',
        [$course->id, $labelmodule->id, $name]
    );
    if ($existing) {
        // Update the embedded Agent when the Adapter configuration changes;
        // this keeps the seed command idempotent without storing credentials.
        $existing->intro = $html;
        $existing->introformat = FORMAT_HTML;
        $DB->update_record('label', $existing);
        return;
    }
    if ($DB->record_exists('course_modules', ['course' => $course->id, 'idnumber' => $idnumber])) {
        return;
    }
    $info = (object) [
        'modulename' => 'label',
        'module' => $labelmodule->id,
        'course' => $course->id,
        'section' => $sectionnumber,
        'name' => $name,
        'intro' => $html,
        'introformat' => FORMAT_HTML,
        'cmidnumber' => $idnumber,
        'visible' => 1,
        'visibleoncoursepage' => 1,
        'groupmode' => 0,
        'groupingid' => 0,
    ];
    add_moduleinfo($info, $course);
}

add_label_once(
    $course,
    0,
    'storage-agent-entry',
    '课程 Agent',
    '<div class="alert alert-info"><strong>课程 Agent</strong><br>用于课程知识问答、学习路径和教师备课。生成内容带有 AI 标识，专业结论请核验引用来源。<br><iframe title="电力系统储能技术 Agent" src="/agent/" style="width:100%;min-height:680px;border:1px solid #d7e0e3;border-radius:6px;"></iframe></div>'
);

$manifestpath = '/opt/course-materials/manifest.json';
$manifest = file_exists($manifestpath) ? json_decode(file_get_contents($manifestpath), true) : null;
$materialroot = '/opt/course-materials';
if (is_array($manifest) && !empty($manifest['files'])) {
    foreach ($manifest['files'] as $item) {
        $filename = basename((string)($item['normalized_file'] ?? ''));
        $path = $materialroot . '/' . $filename;
        $chapter = (int)($item['chapter_id'] ?? 0);
        if ($chapter < 1 || $chapter > 6 || !is_file($path)) {
            continue;
        }
        $idnumber = 'storage-pdf-' . preg_replace('/[^A-Za-z0-9_-]/', '-', $filename);
        if ($DB->record_exists('course_modules', ['course' => $course->id, 'idnumber' => $idnumber])) {
            continue;
        }
        $module = $DB->get_record('modules', ['name' => 'resource'], '*', MUST_EXIST);
        $draftitemid = file_get_unused_draft_itemid();
        $usercontext = context_user::instance(get_admin()->id);
        $fs = get_file_storage();
        $fs->create_file_from_pathname([
            'contextid' => $usercontext->id,
            'component' => 'user',
            'filearea' => 'draft',
            'itemid' => $draftitemid,
            'filepath' => '/',
            'filename' => $filename,
        ], $path);
        $info = (object) [
            'modulename' => 'resource',
            'module' => $module->id,
            'course' => $course->id,
            'section' => $chapter,
            'name' => (string)($item['source_file'] ?? $filename),
            'intro' => '<p>课程课件。来源：' . s((string)($item['source_file'] ?? $filename)) . '</p>',
            'introformat' => FORMAT_HTML,
            'files' => $draftitemid,
            'display' => 5,
            'displayoptions' => 'a:1:{s:10:"printintro";i:0;}',
            'cmidnumber' => $idnumber,
            'visible' => 1,
            'visibleoncoursepage' => 1,
            'groupmode' => 0,
            'groupingid' => 0,
        ];
        add_moduleinfo($info, $course);
        mtrace("Added {$filename} to section {$chapter}");
    }
}

rebuild_course_cache($course->id, true);
mtrace("Course bootstrap complete: {$course->id}");
