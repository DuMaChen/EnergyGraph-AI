<?php

namespace local_course_agent;

defined('MOODLE_INTERNAL') || die();

/**
 * Registration onboarding observers for the course Agent.
 */
final class observer {

    /**
     * Enrol a newly created user if already confirmed.
     */
    public static function user_created(\core\event\user_created $event): void {
        $user = $event->get_record_snapshot('user', $event->objectid);
        if ($user) {
            self::enrol_user_if_confirmed($user);
        }
    }

    /**
     * Enrol a self-registered user after they click the verification link in their email.
     */
    public static function user_confirmed(\core\event\user_confirmed $event): void {
        global $DB;
        $user = $DB->get_record('user', ['id' => $event->objectid]);
        if ($user) {
            self::enrol_user_if_confirmed($user);
        }
    }

    /**
     * Enrol a confirmed email user into the teaching course.
     */
    private static function enrol_user_if_confirmed(\stdClass $user): void {
        global $CFG, $DB;

        if (empty($user) || !empty($user->deleted) || ($user->auth ?? '') !== 'email') {
            return;
        }

        // Do not auto-enrol unconfirmed users to prevent unsolicited welcome emails
        if (empty($user->confirmed)) {
            return;
        }

        try {
            require_once($CFG->dirroot . '/lib/enrollib.php');

            $course = $DB->get_record('course', ['shortname' => 'storage-course']);
            if (!$course || (defined('SITEID') && (int)$course->id === SITEID)) {
                return;
            }

            // A pre-existing enrollment from any method is enough; do not
            // create a duplicate manual enrollment for an existing student.
            $alreadyenrolled = $DB->record_exists_sql(
                'SELECT 1
                   FROM {user_enrolments} ue
                   JOIN {enrol} e ON e.id = ue.enrolid
                  WHERE ue.userid = ? AND e.courseid = ?',
                [$user->id, $course->id]
            );
            if ($alreadyenrolled) {
                return;
            }

            $instance = $DB->get_record('enrol', [
                'courseid' => $course->id,
                'enrol' => 'manual',
                'status' => ENROL_INSTANCE_ENABLED,
            ], '*', IGNORE_MULTIPLE);
            $manual = enrol_get_plugin('manual');
            $studentrole = $DB->get_record('role', ['shortname' => 'student']);
            if (!$instance || !$manual || !$studentrole) {
                debugging('Course Agent onboarding could not find the manual enrollment instance or student role.', DEBUG_DEVELOPER);
                return;
            }

            $manual->enrol_user($instance, $user->id, $studentrole->id, time());
        } catch (\Throwable $exception) {
            // Registration and email confirmation must remain usable even if
            // course onboarding needs attention after a deployment.
            debugging(
                'Course Agent onboarding failed: ' . $exception->getMessage(),
                DEBUG_DEVELOPER
            );
        }
    }
}

