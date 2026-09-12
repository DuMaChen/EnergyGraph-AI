#!/usr/bin/env python3
"""Static contract checks for the Moodle registration -> course onboarding path."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "deploy" / "moodle" / "local" / "course_agent"


def test_plugin_is_copied_into_the_moodle_image() -> None:
    dockerfile = (ROOT / "deploy" / "moodle" / "Dockerfile").read_text()
    assert "COPY local/course_agent " in dockerfile


def test_user_created_observer_enrols_email_users() -> None:
    events = (PLUGIN / "db" / "events.php").read_text()
    observer = (PLUGIN / "classes" / "observer.php").read_text()

    assert r"\\core\\event\\user_created" in events
    assert "observer::user_created" in events
    assert "auth" in observer and "email" in observer
    assert "storage-course" in observer
    assert "enrol_get_plugin('manual')" in observer
    assert "shortname' => 'student'" in observer


def test_observer_is_idempotent_and_does_not_break_registration() -> None:
    observer = (PLUGIN / "classes" / "observer.php").read_text()

    assert "record_exists_sql" in observer
    assert "return;" in observer
    assert "try" in observer and "catch" in observer


def test_moodle_upgrade_runs_after_plugin_is_present() -> None:
    entrypoint = (ROOT / "deploy" / "moodle" / "docker-entrypoint.sh").read_text()
    assert "admin/cli/upgrade.php" in entrypoint
