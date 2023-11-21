import subprocess
from datetime import datetime

import pytest
from click.testing import CliRunner

import trailblazer
from tests.mocks.store_mock import MockStore
from trailblazer.cli.core import (
    add_user_to_db,
    archive_user,
    base,
    cancel,
    delete,
    get_user_from_db,
    get_users_from_db,
    ls_cmd,
    scan,
    set_analysis_completed,
    set_analysis_status,
    unarchive_user,
)
from trailblazer.constants import CharacterFormat, SlurmJobStatus, TrailblazerStatus
from trailblazer.store.models import Analysis

FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH: str = "trailblazer.store.crud.update.get_slurm_squeue_output"


def test_base(cli_runner):
    # GIVEN the cli

    # WHEN asking for the version
    result = cli_runner.invoke(base, ["--version"])

    # THEN it should print the name and version of the tool only
    assert trailblazer.__title__ in result.output
    assert trailblazer.__version__ in result.output


def test_set_analysis_completed(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    failed_analysis_case_id: str,
    process_exit_success: int,
):
    """Test setting an analysis to status complete."""
    # GIVEN an analysis with status failed
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=failed_analysis_case_id
    )

    # Make sure status is not "completed"
    assert analysis.status != TrailblazerStatus.COMPLETED

    # WHEN running command
    result = cli_runner.invoke(set_analysis_completed, [str(analysis.id)], obj=trailblazer_context)

    # THEN command runs successfully
    assert result.exit_code == process_exit_success

    # THEN status will be set to "complete"
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=failed_analysis_case_id
    )
    assert analysis.status == TrailblazerStatus.COMPLETED


def test_set_analysis_status(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    failed_analysis_case_id: str,
    process_exit_success: int,
):
    """Test that the latest analysis status is updated for a given case id."""

    # GIVEN an analysis with status failed
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=failed_analysis_case_id
    )

    # Make sure status is not "qc"
    assert analysis.status != TrailblazerStatus.QC

    # WHEN running command
    result = cli_runner.invoke(
        set_analysis_status, ["--status", "qc", failed_analysis_case_id], obj=trailblazer_context
    )

    # THEN command runs successfully
    assert result.exit_code == process_exit_success

    # THEN status will be set to "qc
    analysis = trailblazer_db.get_latest_analysis_for_case(case_id=failed_analysis_case_id)
    assert analysis.status == TrailblazerStatus.QC


def test_set_analysis_status_error(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    failed_analysis_case_id: str,
):
    """Test that setting the status to a non-accepted value raises an error."""

    # GIVEN an analysis with status failed

    # WHEN running command
    result = cli_runner.invoke(
        set_analysis_status,
        ["--status", "non_existing_status", failed_analysis_case_id],
        obj=trailblazer_context,
    )

    # THEN an error should be raised
    assert result.exit_code != 0
    assert "Invalid status" in caplog.text


def test_cancel_non_existent_analysis_id(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    process_exit_success: int,
):
    """Test cancelling an analysis using a non existing analysis id."""
    caplog.set_level("ERROR")

    # GIVEN Trailblazer database with analyses and jobs
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    trailblazer_db.update_ongoing_analyses()

    # WHEN running cancel on non-existing entry
    result = cli_runner.invoke(cancel, ["123"], obj=trailblazer_context)

    # THEN command runs successfully
    assert result.exit_code == process_exit_success

    # THEN error log informs user that analysis does not exist
    assert "does not exist" in caplog.text


def test_cancel_not_running(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    failed_analysis_case_id: str,
    mocker,
    process_exit_success: int,
    slurm_squeue_output: dict[str, str],
):
    """Test cancelling an analysis, which is not running."""
    caplog.set_level("ERROR")

    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(
            ["cat", slurm_squeue_output.get(failed_analysis_case_id)]
        ).decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8),
    )

    # GIVEN an analysis that is NOT running
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=failed_analysis_case_id
    )
    trailblazer_db.update_ongoing_analyses()

    # WHEN trying to cancel analysis
    result = cli_runner.invoke(cancel, [str(analysis.id)], obj=trailblazer_context)

    # THEN command runs successfully
    assert result.exit_code == process_exit_success

    # THEN error log informs user that analysis cannot be cancelled as it is not running
    assert "is not running" in caplog.text


def test_cancel_with_ongoing_analysis(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    mocker,
    ongoing_analysis_case_id: str,
    slurm_squeue_output: dict[str, str],
    process_exit_success: int,
):
    """Test all ongoing analysis jobs are cancelled."""
    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(
            ["cat", slurm_squeue_output.get(ongoing_analysis_case_id)]
        ).decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8),
    )

    # GIVEN SLURM scancel output for an analysis
    mocker.patch("trailblazer.store.crud.update.cancel_slurm_job", return_value=None)

    caplog.set_level("INFO")

    # GIVEN an ongoing analysis
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    trailblazer_db.update_ongoing_analyses()
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )

    # Analysis should have jobs that can be cancelled
    assert analysis.jobs

    # WHEN running cancel command
    result = cli_runner.invoke(cancel, [str(analysis.id)], obj=trailblazer_context)

    # THEN command should run successfully
    assert result.exit_code == process_exit_success

    # THEN log should inform of successful cancellation
    assert "cancelled successfully" in caplog.text
    assert "Cancelling" in caplog.text

    # THEN job id from squeue output will be cancelled
    assert f"{analysis.jobs[3].slurm_id}" in caplog.text

    # THEN analysis status is set to cancelled
    assert SlurmJobStatus.CANCELLED in analysis.comment
    assert analysis.status == TrailblazerStatus.CANCELLED


def test_delete_nonexisting(
    cli_runner: CliRunner, trailblazer_context: dict[str, MockStore], caplog
):
    with caplog.at_level("ERROR"):
        # GIVEN Trailblazer database with analyses and jobs
        trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
        trailblazer_db.update_ongoing_analyses()

        # WHEN trying to delete analysis not in database
        cli_runner.invoke(delete, ["123"], obj=trailblazer_context)

        # THEN error log informs user that analysis is not found
        assert "Analysis not found" in caplog.text


def test_delete_ongoing_fail(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    ongoing_analysis_case_id: str,
    process_exit_success: int,
):
    """Test deleting an ongoing analysis without using the force flag."""
    caplog.set_level("ERROR")

    # GIVEN Trailblazer database with analyses and jobs
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    trailblazer_db.update_ongoing_analyses()

    # GIVEN an analysis that is ongoing
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )

    # WHEN trying to delete ongoing analysis without --force flag
    result = cli_runner.invoke(delete, [str(analysis.id)], obj=trailblazer_context)

    # THEN command executes successfully
    assert result.exit_code == process_exit_success

    # THEN error log informs user that ongoing analysis cannot be deleted without --force flag
    assert "--force" in caplog.text

    # THEN analysis should not be cancelled
    assert analysis.status != TrailblazerStatus.CANCELLED


def test_delete_ongoing_force(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    ongoing_analysis_case_id,
    process_exit_success: int,
):
    caplog.set_level("INFO")

    # GIVEN Trailblazer database with analyses and jobs and an ongoing analysis
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    trailblazer_db.update_ongoing_analyses()
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )

    # WHEN running command with --force flag
    result = cli_runner.invoke(delete, [str(analysis.id), "--force"], obj=trailblazer_context)

    # THEN command runs successfully
    assert result.exit_code == process_exit_success

    # THEN log informs user that Trailblazer is deleting analysis
    assert "Deleting" in caplog.text

    # THEN the analysis should have been deleted from the database
    assert not trailblazer_db.get_latest_analysis_for_case(case_id=analysis.family)


def test_get_user_not_in_database(
    cli_runner: CliRunner, trailblazer_context: dict[str, MockStore], caplog
):
    """Test getting user when user is not in the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("ERROR")

    # WHEN looking for a user that is not added
    cli_runner.invoke(get_user_from_db, ["not_in_db@disco.com"], obj=trailblazer_context)

    # THEN log should inform that user was not found
    assert "not found" in caplog.text


def test_get_user_in_database(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    user_email: str,
    username: str,
):
    """Test getting user when user is in the database."""
    # GIVEN populated Trailblazer database
    caplog.set_level("INFO")

    # WHEN looking for a user that is added
    cli_runner.invoke(get_user_from_db, [user_email], obj=trailblazer_context)

    # THEN log informs the user about their full name
    assert username in caplog.text


def test_add_user(cli_runner: CliRunner, trailblazer_context: dict[str, MockStore], caplog):
    """Test adding a user to the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN adding new user
    cli_runner.invoke(
        add_user_to_db, ["harriers@disco.com", "--name", "Harry DuBois"], obj=trailblazer_context
    )

    # THEN log should inform that user is added
    assert "New user added" in caplog.text


def test_add_user_when_already_exists(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    user_email: str,
    username: str,
):
    """Test adding a user to the database when the user already exists."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN adding new user
    cli_runner.invoke(add_user_to_db, [user_email, "--name", username], obj=trailblazer_context)

    # THEN log should inform that user is added
    assert f"User with email {user_email} found" in caplog.text


def test_users(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    user_email: str,
    username: str,
):
    """Test getting users from the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN getting users
    cli_runner.invoke(get_users_from_db, ["--email", user_email], obj=trailblazer_context)

    # THEN log shows users
    assert username in caplog.text


def test_archive_user(
    cli_runner: CliRunner, trailblazer_context: dict[str, MockStore], caplog, user_email: str
):
    """Test archiving a user in the database."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN archiving user
    cli_runner.invoke(archive_user, [user_email], obj=trailblazer_context)

    # THEN log shows users as archived
    assert f"User archived: {user_email}" in caplog.text


def test_archive_user_when_already_archived(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    archived_user_email: str,
):
    """Test archiving a user in the database when already archived."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN archiving user
    cli_runner.invoke(archive_user, [archived_user_email], obj=trailblazer_context)

    # THEN log shows users is already archived
    assert "has archive status: True" in caplog.text


def test_archive_user_when_non_existing_user(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    archived_user_email: str,
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
    cli_runner: CliRunner, trailblazer_context: dict[str, MockStore], caplog, user_email: str
):
    """Test unarchiving a user in the database which is not archived."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN unarchiving user
    cli_runner.invoke(unarchive_user, [user_email], obj=trailblazer_context)

    # THEN log shows users is not archived
    assert f"User with email {user_email} has archive status: False" in caplog.text


def test_unarchive_user(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    archived_user_email: str,
):
    """Test unarchiving a user in the database which is archived."""
    # GIVEN populated Trailblazer database

    caplog.set_level("INFO")

    # WHEN unarchiving user
    cli_runner.invoke(unarchive_user, [archived_user_email], obj=trailblazer_context)

    # THEN log shows users as not archived
    assert f"User unarchived: {archived_user_email}" in caplog.text


def test_scan(
    cli_runner: CliRunner,
    trailblazer_context: dict[str, MockStore],
    caplog,
    mocker,
    ongoing_analysis_case_id: str,
    slurm_squeue_output: dict[str, str],
):
    """Test scanning for analyses and updating analysis status."""
    caplog.set_level("INFO")

    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(
            ["cat", slurm_squeue_output.get(ongoing_analysis_case_id)]
        ).decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8),
    )

    # GIVEN populated Trailblazer database with pending analyses

    # GIVEN an analysis that is pending
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )
    assert analysis.status == TrailblazerStatus.PENDING

    # WHEN running trailblazer scan command
    cli_runner.invoke(scan, [], obj=trailblazer_context)

    # THEN log that analyses are updated
    assert "All analyses updated" in caplog.text
    analysis: Analysis | None = trailblazer_db.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )

    # THEN the status of analysis should be updated
    assert analysis.status == TrailblazerStatus.RUNNING


@pytest.mark.parametrize(
    "case_id, status",
    [
        ("blazinginsect", TrailblazerStatus.RUNNING),
        ("crackpanda", TrailblazerStatus.FAILED),
        ("fancymole", TrailblazerStatus.COMPLETED),
        ("happycow", TrailblazerStatus.PENDING),
    ],
)
def test_ls(
    case_id: str,
    cli_runner: CliRunner,
    mocker,
    process_exit_success: int,
    slurm_squeue_output: dict[str, str],
    status: str,
    timestamp_now: datetime,
    trailblazer_context: dict[str, MockStore],
):
    """Test the Trailblazer ls CLI command using different cases and statuses."""
    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(["cat", slurm_squeue_output.get(case_id)]).decode(
            CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8
        ),
    )
    # GIVEN a populated Trailblazer database with pending analyses
    trailblazer_db: MockStore = trailblazer_context["trailblazer_db"]

    # Update analyses to their expected status
    trailblazer_db.update_ongoing_analyses()

    # WHEN running ls command while filtering by status
    result = cli_runner.invoke(
        ls_cmd, ["--status", status, "--before", str(timestamp_now.date())], obj=trailblazer_context
    )

    # THEN command runs successfully with provided options
    assert result.exit_code == process_exit_success

    # THEN ls print info about cases with that status
    assert case_id in result.output
