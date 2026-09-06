<?php
// Controlled textbook locator. It resolves a normalized filename only inside
// the current Moodle course and never accepts a filesystem path from a user.
require_once('/var/www/html/config.php');
require_once($CFG->libdir . '/moodlelib.php');
require_once($CFG->dirroot . '/lib/modinfolib.php');

$course = $DB->get_record('course', ['shortname' => 'storage-course'], '*', MUST_EXIST);
require_login($course, false);
$source = required_param('source', PARAM_RAW_TRIMMED);
// Course filenames may contain Chinese characters. Validate the path shape
// explicitly instead of using PARAM_FILE, which can strip legitimate names on
// some Moodle/PHP locale combinations.
if ($source === '' || basename($source) !== $source || str_contains($source, chr(0)) || str_contains($source, '/') || str_contains($source, '\\')) {
    http_response_code(400);
    header('Content-Type: text/plain; charset=utf-8');
    echo '教材资源名称无效';
    exit;
}
$page = max(1, optional_param('page', 1, PARAM_INT));

// Agent citations use the human-readable manifest source_file while Moodle
// stores the upload under normalized_file. Resolve that mapping before
// searching the access-controlled resource files.
$manifestpath = '/opt/course-materials/manifest.json';
if (is_file($manifestpath)) {
    $manifest = json_decode(file_get_contents($manifestpath), true);
    foreach (($manifest['files'] ?? []) as $item) {
        if ((string)($item['source_file'] ?? '') === $source) {
            $source = basename((string)($item['normalized_file'] ?? ''));
            break;
        }
    }
}

$modinfo = get_fast_modinfo($course);
$storage = get_file_storage();
foreach ($modinfo->get_cms() as $cm) {
    if ($cm->modname !== 'resource' || !$cm->uservisible || !$cm->available) {
        continue;
    }
    $files = $storage->get_area_files($cm->context->id, 'mod_resource', 'content', 0, 'filename', false);
    foreach ($files as $file) {
        if ($file->is_directory() || $file->get_filename() !== $source) {
            continue;
        }
        // Moodle supplies the access-controlled pluginfile URL; the page
        // fragment is a best-effort hint supported by most PDF viewers.
        $url = moodle_url::make_pluginfile_url(
            $file->get_contextid(), $file->get_component(), $file->get_filearea(),
            $file->get_itemid(), $file->get_filepath(), $file->get_filename(), true
        );
        redirect($url . '#page=' . $page);
    }
}

http_response_code(404);
header('Content-Type: text/plain; charset=utf-8');
echo '教材资源不存在或无权访问';
