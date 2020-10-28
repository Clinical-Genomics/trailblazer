# -*- coding: utf-8 -*-
import trailblazer
from trailblazer.cli import base
from trailblazer.cli.core import ls_cmd, delete, cancel, scan, user
import pytest


def test_base(cli_runner):
    # GIVEN the cli
    # WHEN asking for the version
    result = cli_runner.invoke(base, ["--version"])
    # THEN it should print the name and version of the tool only
    assert trailblazer.__title__ in result.output
    assert trailblazer.__version__ in result.output


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
        #
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(case_id="escapedgoat")

        result = cli_runner.invoke(
            delete, [str(analysis_obj.id), "--force"], obj=trailblazer_context
        )
        assert result.exit_code == 0
        assert "Deleting" in caplog.text


def test_user_not_in_database(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        cli_runner.invoke(user, ["harriers@disco.com"], obj=trailblazer_context)
        assert "not found" in caplog.text


def test_user_in_database(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        cli_runner.invoke(user, ["paul.anderson@magnolia.com"], obj=trailblazer_context)
        assert "Anderson" in caplog.text


def test_user_added(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        cli_runner.invoke(
            user, ["harriers@disco.com", "--name", "Harry DuBois"], obj=trailblazer_context
        )
        assert "New user added" in caplog.text


def test_scan(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id="blazinginsect"
        )
        assert analysis_obj.status == "pending"

        cli_runner.invoke(scan, [], obj=trailblazer_context)
        assert "Analyses updated" in caplog.text
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id="blazinginsect"
        )
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
    trailblazer_context["trailblazer"].update_ongoing_analyses()
    result = cli_runner.invoke(ls_cmd, ["--status", status], obj=trailblazer_context)
    assert result.exit_code == 0
    assert case_id in result.output
