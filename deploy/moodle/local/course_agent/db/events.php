<?php

defined('MOODLE_INTERNAL') || die();

$observers = [
    [
        'eventname' => '\\core\\event\\user_created',
        'callback' => '\\local_course_agent\\observer::user_created',
        'priority' => 1000,
    ],
    [
        'eventname' => '\\core\\event\\user_confirmed',
        'callback' => '\\local_course_agent\\observer::user_confirmed',
        'priority' => 1000,
    ],
];

