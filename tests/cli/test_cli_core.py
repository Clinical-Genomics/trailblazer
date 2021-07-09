# -*- coding: utf-8 -*-
import pytest

import trailblazer
from trailblazer.cli import base
from trailblazer.cli.core import cancel, delete, ls_cmd, scan, set_analysis_completed, user


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


def test_user_not_in_database(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        # GIVEN populated Trailblazer database

        # WHEN looking for a user that is not added
        cli_runner.invoke(user, ["harriers@disco.com"], obj=trailblazer_context)

        # THEN log should inform that user not found
        assert "not found" in caplog.text


def test_user_in_database(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        # GIVEN populated Trailblazer database

        # WHEN looking for a user that is added
        cli_runner.invoke(user, ["paul.anderson@magnolia.com"], obj=trailblazer_context)

        # THEN log informs the user about their full name
        assert "Anderson" in caplog.text


def test_user_added(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        # GIVEN populated Trailblazer database

        # WHEN adding new user
        cli_runner.invoke(
            user, ["harriers@disco.com", "--name", "Harry DuBois"], obj=trailblazer_context
        )

        # THEN log should inform that user is added
        assert "New user added" in caplog.text


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
