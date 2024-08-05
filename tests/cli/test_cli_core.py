import subprocess
from datetime import datetime

import pytest
from click.testing import CliRunner

import trailblazer
from tests.mocks.store_mock import MockStore
from trailblazer.cli.core import (
    add_user,
    archive_user,
    base,
    cancel,
    delete,
    get_user_from_db,
    get_users_from_db,
    ls_cmd,
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
        add_user,
        ["harriers@disco.com", "--name", "Harry DuBois", "--abbreviation", "HD"],
        obj=trailblazer_context,
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
    cli_runner.invoke(add_user, [user_email, "--name", username], obj=trailblazer_context)

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
