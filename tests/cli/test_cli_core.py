# -*- coding: utf-8 -*-
import trailblazer
from trailblazer.cli import base
from trailblazer.cli.core import ls_cmd, delete, get, cancel, scan, user
import pytest


def test_base(cli_runner):
    # GIVEN the cli
    # WHEN asking for the version
    result = cli_runner.invoke(base, ["--version"])
    # THEN it should print the name and version of the tool only
    assert trailblazer.__title__ in result.output
    assert trailblazer.__version__ in result.output


def test_get_dummy_comment(cli_runner, trailblazer_context):
    """Test get with a argument that should yield no results"""
    # GIVEN the cli
    # WHEN running get with a comment
    result = cli_runner.invoke(get, ["-c", "dummy-comment"], obj=trailblazer_context)
    # THEN all analyses containing that comment should be listed
    assert not result.output


def test_get_expected_comment(cli_runner, trailblazer_context):
    """Test get with a argument that should yield no results"""
    # GIVEN the cli
    # WHEN running get with a comment
    failed_comment = "failed steps"
    trailblazer_context["trailblazer"].update_ongoing_analyses()
    result = cli_runner.invoke(get, ["-c", failed_comment], obj=trailblazer_context)
    # THEN all analyses containing that comment should be listed
    assert failed_comment in result.output


def test_cancel_nonexistent(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        result = cli_runner.invoke(cancel, ["123"], obj=trailblazer_context)
        assert result.exit_code == 0
        assert "does not exist" in caplog.text


def test_cancel_not_running(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        failed_analysis = "crackpanda"
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id=failed_analysis
        )
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        result = cli_runner.invoke(cancel, [str(analysis_obj.id)], obj=trailblazer_context)
        assert result.exit_code == 0
        assert "is not running" in caplog.text


def test_cancel_ongoing(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(
            case_id="blazinginsect"
        )
        assert analysis_obj.failed_jobs

        result = cli_runner.invoke(cancel, [str(analysis_obj.id)], obj=trailblazer_context)
        assert result.exit_code == 0
        assert "all ongoing jobs cancelled successfully" in caplog.text
        assert "Cancelling" in caplog.text
        assert analysis_obj.status == "canceled"


def test_delete_nonexisting(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        cli_runner.invoke(delete, ["123"], obj=trailblazer_context)
        assert "Analysis not found" in caplog.text


def test_delete_ongoing_fail(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("ERROR"):
        trailblazer_context["trailblazer"].update_ongoing_analyses()
        analysis_obj = trailblazer_context["trailblazer"].get_latest_analysis(case_id="escapedgoat")

        result = cli_runner.invoke(delete, [str(analysis_obj.id)], obj=trailblazer_context)
        assert result.exit_code == 0
        assert "--force" in caplog.text
        assert analysis_obj.status != "canceled"


def test_delete_ongoing_force(cli_runner, trailblazer_context, caplog):
    with caplog.at_level("INFO"):
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
