<?php
// This file is part of Moodle - http://moodle.org/
// Course Agent extension library

defined('MOODLE_INTERNAL') || die();

/**
 * Route course clicks directly to the modern learning space when applicable.
 * Note: Tab 'AI 智慧教学与学习空间' is removed as requested.
 *
 * @param navigation_node $navigation The course navigation node
 * @param stdClass $course The course object
 * @param context_course $context The course context
 */
function local_course_agent_extend_navigation_course(\navigation_node $navigation, \stdClass $course, \context_course $context) {
    if ((int)$course->id === (int)SITEID) {
        return;
    }
    
    global $PAGE;
    if ((int)$course->id === 2) {
        $is_raw = optional_param('moodle_raw', 0, PARAM_INT);
        $is_edit = optional_param('edit', '', PARAM_RAW);
        if (!$is_raw && empty($is_edit) && isset($PAGE->requires)) {
            $PAGE->requires->js_init_code("
                if (!window.location.search.includes('moodle_raw=1') && !window.location.search.includes('edit=')) {
                    window.location.replace('/agent/');
                }
            ");
        }
    }
}
