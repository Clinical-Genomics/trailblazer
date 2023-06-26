from typing import Dict

import pytest

import trailblazer
from tests.mocks.store_mock import MockStore
from trailblazer.cli.core import (
    base,
    cancel,
    delete,
    ls_cmd,
    scan,
    set_analysis_completed,
    user,
    get_users_from_db,
    archive_user,
    unarchive_user,
)


def test_base(cli_runner):
    # GIVEN the cli

    # WHEN asking for the version
    result = cli_runner.invoke(base, ["--version"])

    # THEN it should print the name and version of the tool only
    assert trailblazer.__title__ in result.output
    assert trailblazer.__version__ in result.output


def test_set_analysis_completed(cli_runner, trailblazer_context, caplog):
    # GIVEN an analysis with status FAILED
    failed_analysis = "crackpanda"
    analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(case_id=failed_analysis)

    # Make sure status is not "completed"
    assert analysis_obj.status != "completed"

    # WHEN running command
    result = cli_runner.invoke(
        set_analysis_completed, [str(analysis_obj.id)], obj=trailblazer_context
    )

    # THEN command runs successfully
    assert result.exit_code == 0

    # THEN status will be set to COMPLETED
    analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(case_id=failed_analysis)
    assert analysis_obj.status == "completed"


def test_cancel_nonexistent(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        # GIVEN Trailblazer database with analyses and jobs
        trailblazer_context["trailblazer"].update_ongoing_analyses()

        # WHEN running cancel on non-existing entry
        result = cli_runner.invoke(cancel, ["123"], obj=trailblazer_context)

        # THEN command runs successfully
        assert result.exit_code == 0

        # THEN error log informs user that analysis does not exist
        assert "does not exist" in caplog.text


def test_cancel_not_running(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        # GIVEN an analysis that is NOT running
        failed_analysis = "crackpanda"
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id=failed_analysis
        )
        # WHEN trying to cancel analysis
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        result = cli_runner.invoke(cancel, [str(analysis_obj.id)], obj=trailblazer_context)

        # THEN command runs successfully
        assert result.exit_code == 0

        # THEN error log informs user that analysis cannot be cancelled as it is not running
        assert "is not running" in caplog.text


def test_cancel_ongoing(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        # GIVEN an analysis that is running
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id="blazinginsect"
        )

        # Analysis should have jobs that can be cancelled
        assert analysis_obj.failed_jobs

        # WHEN running cancel command
        result = cli_runner.invoke(cancel, [str(analysis_obj.id)], obj=trailblazer_context)

        # THEN command should run successfully
        assert result.exit_code == 0

        # THEN log should inform of successful cancellation
        assert "all ongoing jobs cancelled successfully" in caplog.text
        assert "Cancelling" in caplog.text

        # THEN job id from squeue output will be cancelled
        assert "690988" in caplog.text

        # THEN analysis status is set to cancelled
        assert "cancelled" in analysis_obj.comment
        assert analysis_obj.status == "canceled"


def test_delete_nonexisting(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        # GIVEN Trailblazer database with analyses and jobs
        trailblazer_context["trailblazer"].update_ongoing_analyses()

        # WHEN trying to delete analysis not in database
        cli_runner.invoke(delete, ["123"], obj=trailblazer_context)

        # THEN error log informs user that analysis is not found
        assert "Analysis not found" in caplog.text


def test_delete_ongoing_fail(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        # GIVEN Trailblazer database with analyses and jobs
        trailblazer_context["trailblazer"].update_ongoing_analyses()

        # GIVEN an analysis that is ongoing
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(case_id="escapedgoat")

        # WHEN trying to delete ongoing analysis without --force flag
        result = cli_runner.invoke(delete, [str(analysis_obj.id)], obj=trailblazer_context)

        # THEN command executes successfully
        assert result.exit_code == 0

        # THEN error log informs user that ongoing analysis cannot be deleted without --force flag
        assert "--force" in caplog.text

        # THEN analysis should not be cancelled
        assert analysis_obj.status != "canceled"


def test_delete_ongoing_force(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        # GIVEN Trailblazer database with analyses and jobs and an ongoing analysis
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(case_id="escapedgoat")

        # WHEN running command with --force flag
        result = cli_runner.invoke(
            delete, [str(analysis_obj.id), "--force"], obj=trailblazer_context
        )

        # THEN command runs successfully
        assert result.exit_code == 0

        # THEN log informs user that Trailblazer is deleting analysis
        assert "Deleting" in caplog.text


def test_user_not_in_database(cli_runner, trailblazer_context: Dict[str, MockStore], caplog):
    """Test user when user is not in the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("ERROR")

    # WHEN looking for a user that is not added
    cli_runner.invoke(user, ["not_in_db@disco.com"], obj=trailblazer_context)

    # THEN log should inform that user was not found
    assert "not found" in caplog.text


def test_user_in_database(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, user_email: str, username: str
):
    """Test user when user is in the database."""
    # GIVEN populated Trailblazer database
    caplog.set_level("INFO")

    # WHEN looking for a user that is added
    cli_runner.invoke(user, [user_email], obj=trailblazer_context)

    # THEN log informs the user about their full name
    assert username in caplog.text


def test_user_added(cli_runner, trailblazer_context: Dict[str, MockStore], caplog):
    """Test user when adding user."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN adding new user
    cli_runner.invoke(
        user, ["harriers@disco.com", "--name", "Harry DuBois"], obj=trailblazer_context
    )

    # THEN log should inform that user is added
    assert "New user added" in caplog.text


def test_users(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, user_email: str, username: str
):
    """Test getting users from the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN getting users
    cli_runner.invoke(get_users_from_db, ["--email", user_email], obj=trailblazer_context)

    # THEN log shows users
    assert username in caplog.text


def test_archive_user(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, user_email: str
):
    """Test archiving a user in the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN archiving user
    cli_runner.invoke(archive_user, [user_email], obj=trailblazer_context)

    # THEN log shows users as archived
    assert f"User archived: {user_email}" in caplog.text


def test_archive_user_when_already_archived(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, archived_user_email: str
):
    """Test archiving a user in the database when already archived."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN archiving user
    cli_runner.invoke(archive_user, [archived_user_email], obj=trailblazer_context)

    # THEN log shows users is already archived
    assert "has archive status: True" in caplog.text


def test_archive_user_when_non_existing_user(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, archived_user_email: str
):
    """Test archiving a user in the database when user does not exist."""
    # GIVEN populated Trailblazer database

    # GIVEN a user email that does not exist
    non_existing_email: str = "does-not.exist@none.com"

    # WHEN archiving user
    cli_runner.invoke(archive_user, [non_existing_email], obj=trailblazer_context)

    # THEN log shows users is not found
    assert f"User with email {non_existing_email} not found" in caplog.text


def test_unarchive_user_when_not_archived(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, user_email: str
):
    """Test unarchiving a user in the database which is not archived."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN unarchiving user
    cli_runner.invoke(unarchive_user, [user_email], obj=trailblazer_context)

    # THEN log shows users is not archived
    assert f"User with email {user_email} has archive status: False" in caplog.text


def test_unarchive_user(
    cli_runner, trailblazer_context: Dict[str, MockStore], caplog, archived_user_email: str
):
    """Test unarchiving a user in the database which is archived."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN unarchiving user
    cli_runner.invoke(unarchive_user, [archived_user_email], obj=trailblazer_context)

    # THEN log shows users as not archived
    assert f"User unarchived: {archived_user_email}" in caplog.text


def test_scan(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        # GIVEN populated Trailblazer database with pending analyses

        # GIVEN an analysis that is pending
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id="blazinginsect"
        )
        assert analysis_obj.status == "pending"

        # WHEN running trailblazer scan command
        cli_runner.invoke(scan, [], obj=trailblazer_context)
        assert "All analyses updated" in caplog.text
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id="blazinginsect"
        )

        # THEN the stats of analysis should be updated as expected
        assert analysis_obj.status == "running"


@pytest.mark.parametrize(
    "case_id, status",
    [
        ("blazinginsect", "running"),
        ("crackpanda", "failed"),
        ("fancymole", "completed"),
        ("happycow", "pending"),
    ],
)
def test_ls(cli_runner, trailblazer_context, caplog, case_id, status):
    # GIVEN populated Trailblazer database with pending analyses

    # Update analyses to their expected status
    trailblazer_context["trailblazer"].update_ongoing_analyses()

    # WHEN running ls command while filtering by status
    result = cli_runner.invoke(ls_cmd, ["--status", status], obj=trailblazer_context)

    # THEN command runs successfully with provided options
    assert result.exit_code == 0

    # THEN ls print info about cases with that status
    assert case_id in result.output
