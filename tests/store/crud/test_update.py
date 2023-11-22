import subprocess
from datetime import datetime

import pytest

from tests.apps.tower.conftest import CaseId
from tests.mocks.store_mock import MockStore
from tests.mocks.tower_mock import MockTowerAPI
from trailblazer.apps.slurm.api import get_squeue_result
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.apps.tower.api import TowerAPI
from trailblazer.constants import CharacterFormat, TrailblazerStatus, WorkflowManager
from trailblazer.exc import MissingAnalysis, TrailblazerError
from trailblazer.io.controller import ReadFile
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, User

FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH: str = "trailblazer.store.crud.update.get_slurm_squeue_output"


def test_update_analysis_jobs(analysis_store: MockStore, tower_jobs: list[dict], case_id: str):
    """Test jobs are successfully updated."""

    # GIVEN an analysis with no jobs
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN there should be jobs
    assert analysis.jobs


def test_update_user_is_archived(user_store: MockStore, user_email: str):
    """Test updating user is archived attribute."""
    # GIVE a database and a not archived user
    user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()
    assert not user.is_archived

    # WHEN updating a user archive status
    user_store.update_user_is_archived(user=user, archive=True)

    archived_user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()

    # THEN user should be recorded as archived in the database
    assert archived_user


@pytest.mark.parametrize(
    "case_id, status",
    [
        ("blazinginsect", TrailblazerStatus.RUNNING),
        ("crackpanda", TrailblazerStatus.FAILED),
        ("daringpidgeon", TrailblazerStatus.ERROR),
        ("escapedgoat", TrailblazerStatus.PENDING),
        ("fancymole", TrailblazerStatus.COMPLETED),
        ("happycow", TrailblazerStatus.PENDING),
        ("lateraligator", TrailblazerStatus.FAILED),
        ("liberatedunicorn", TrailblazerStatus.ERROR),
        ("nicemice", TrailblazerStatus.COMPLETED),
        ("rarekitten", TrailblazerStatus.CANCELLED),
        ("trueferret", TrailblazerStatus.RUNNING),
    ],
)
def test_update_run_status(
    analysis_store: MockStore,
    case_id: str,
    status: str,
    mocker,
    slurm_squeue_output: dict[str, str],
):
    """Test updating an analysis status."""
    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(["cat", slurm_squeue_output.get(case_id)]).decode(
            CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8
        ),
    )

    # GIVEN an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN the database is updated once
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is updated
    assert analysis.status == status

    # WHEN the database is updated a second time
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is unchanged, and no database errors were raised
    assert analysis.status == status


def test_update_ongoing_analyses(analysis_store: MockStore, ongoing_analysis_case_id: str):
    """Test all ongoing analysis statuses are updated."""
    # GIVEN an analysis store and analysis status
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )
    assert analysis.status == TrailblazerStatus.PENDING

    # WHEN updating ongoing analyses
    analysis_store.update_ongoing_analyses()

    # THEN status should have been updated
    assert analysis.status == TrailblazerStatus.ERROR


def test_update_ongoing_analyses_with_not_ongoing_analysis(
    analysis_store: MockStore, ongoing_analysis_case_id: str
):
    """Test all ongoing analysis statuses are updated on not ongoing analysis-"""
    # GIVEN an analysis store and analysis status
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )
    # GIVEN a completed analysis
    analysis.status = TrailblazerStatus.COMPLETED

    # WHEN updating ongoing analyses
    analysis_store.update_ongoing_analyses()

    # THEN the status should be COMPLETED
    assert analysis.status == TrailblazerStatus.COMPLETED


def test_update_ongoing_analyseswhen_bad_call(
    analysis_store: MockStore, caplog, ongoing_analysis_case_id: str
):
    """Test all ongoing analysis statuses are updated when exception is raised."""
    caplog.set_level("INFO")
    # GIVEN an analysis store and analysis status
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )
    # GIVEN an analysis that is deleted
    del analysis.id

    # WHEN updating ongoing analyses
    with pytest.raises(KeyError):
        analysis_store.update_ongoing_analyses()

        # THEN error should be raised
        assert f"Failed to update {analysis.family} - {analysis.id}" in caplog.text


def test_update_analysis_jobs_from_slurm_jobs(analysis_store: MockStore, squeue_stream_jobs: str):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.jobs

    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # WHEN updating the analysis
    analysis_store.update_analysis_jobs_from_slurm_jobs(
        analysis=analysis, squeue_result=squeue_result
    )
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_id=analysis.family, started_at=analysis.started_at, status=TrailblazerStatus.PENDING
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.jobs


def test_update_case_analyses_as_deleted(analysis_store: MockStore, ongoing_analysis_case_id: str):
    """Test marking case analyses as deleted."""
    # GIVEN case id for a case with analyses that are not deleted
    analyses: list[Analysis] | None = analysis_store.get_analyses_for_case(
        case_id=ongoing_analysis_case_id
    )
    for analysis in analyses:
        assert not analysis.is_deleted

    # WHEN marking analyses as deleted
    analysis_store.update_case_analyses_as_deleted(case_id=ongoing_analysis_case_id)
    analyses: list[Analysis] | None = analysis_store.get_analyses_for_case(
        case_id=ongoing_analysis_case_id
    )

    # THEN analyses are marked as deleted
    for analysis in analyses:
        assert analysis.is_deleted


def test_update_case_analyses_as_deleted_with_non_existing_case(
    analysis_store: MockStore, case_id_not_in_db: str
):
    """Test marking case analyses as deleted."""
    # GIVEN case id for that do not exist

    # WHEN marking analyses as deleted
    analyses: list[Analysis] | None = analysis_store.update_case_analyses_as_deleted(
        case_id=case_id_not_in_db
    )

    # THEN no analyses are returned
    assert not analyses


def test_cancel_ongoing_slurm_analysis(
    analysis_store: MockStore, caplog, mocker, ongoing_analysis_case_id: str, tower_jobs: list[dict]
):
    """Test all ongoing analysis jobs are cancelled."""

    # GIVEN SLURM scancel output for an analysis
    mocker.patch("trailblazer.store.crud.update.cancel_slurm_job", return_value=None)

    caplog.set_level("INFO")

    # GIVEN an ongoing analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(
        case_id=ongoing_analysis_case_id
    )

    # Analysis should have jobs that can be cancelled
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])
    assert analysis.jobs

    # WHEN running cancel ongoing analysis
    analysis_store.cancel_ongoing_analysis(analysis_id=analysis.id)

    # THEN log should inform of successful cancellation
    assert "Cancelling job" in caplog.text
    assert "cancelled successfully!" in caplog.text

    # THEN comment should be added
    assert "Analysis cancelled manually by" in analysis.comment

    # THEN analysis status should be updated
    assert TrailblazerStatus.CANCELLED == analysis.status


def test_cancel_ongoing_tower_analysis(
    analysis_store: MockStore, caplog, mocker, case_id: str, tower_id: str
):
    # GIVEN TOWER cancel output
    mocker.patch.object(TowerAPI, "cancel", return_value=None)

    # GIVEN a workflow id
    mocker.patch.object(ReadFile, "get_content_from_file")
    ReadFile.get_content_from_file.return_value = {case_id: [tower_id]}

    # GIVEN Tower requirements are meet
    mocker.patch(
        "trailblazer.apps.tower.api._validate_tower_api_client_requirements", return_value=True
    )

    caplog.set_level("INFO")

    # GIVEN an ongoing analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN running cancel ongoing analysis
    analysis_store.cancel_ongoing_analysis(analysis_id=analysis.id)

    # THEN log should inform of successful cancellation
    assert f"Cancelling Tower workflow for {case_id}" in caplog.text
    assert "cancelled successfully!" in caplog.text

    # THEN comment should be added
    assert "Analysis cancelled manually by" in analysis.comment


def test_cancel_ongoing_analysis_when_no_analysis(
    analysis_id_does_not_exist: int, analysis_store: MockStore, caplog, tower_jobs: list[dict]
):
    """Test exception is raised if analysis id does not exist."""
    caplog.set_level("INFO")

    # GIVEN an non-existing analysis

    # WHEN running cancel ongoing analysis
    with pytest.raises(MissingAnalysis):
        analysis_store.cancel_ongoing_analysis(analysis_id=analysis_id_does_not_exist)

        # THEN exception should be raised


def test_cancel_ongoing_analysis_when_no_ongoing_analysis(
    analysis_store: MockStore,
    caplog,
    failed_analysis_case_id: str,
    tower_jobs: list[dict],
):
    """Test exception is raised if analysis status is not ongoing."""
    caplog.set_level("INFO")

    # GIVEN a failed analysis
    analysis_store.update_ongoing_analyses()
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(
        case_id=failed_analysis_case_id
    )

    # GIVEN a cancelled status
    analysis.status = TrailblazerStatus.CANCELLED

    # WHEN running cancel ongoing analysis
    with pytest.raises(TrailblazerError):
        analysis_store.cancel_ongoing_analysis(analysis_id=analysis.id)

        # THEN exception should be raised


def test_update_analysis_status_with_failed(analysis_store: MockStore, case_id: str):
    """Test setting analysis to failed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status != TrailblazerStatus.FAILED

    # WHEN setting analysis to failed
    analysis_store.update_analysis_status(case_id=analysis.family, status=TrailblazerStatus.FAILED)

    # THEN the analysis status should be updated to failed
    assert analysis.status == TrailblazerStatus.FAILED


def test_update_analysis_status_to_completed(analysis_store: MockStore, case_id: str):
    """Test setting analysis to completed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status != TrailblazerStatus.COMPLETED

    # WHEN setting analysis to completed
    analysis_store.update_analysis_status_to_completed(analysis_id=analysis.id)

    # THEN the analysis status should be updated to completed
    assert analysis.status == TrailblazerStatus.COMPLETED


def test_update_analysis_uploaded_at(
    analysis_store: MockStore, timestamp_now: datetime, case_id: str
):
    """Test setting analysis uploaded at for an analysis."""
    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN setting an analysis uploaded at
    analysis_store.update_analysis_uploaded_at(case_id=analysis.family, uploaded_at=timestamp_now)

    # THEN uploaded at should be updated
    assert analysis.uploaded_at == timestamp_now


def test_update_analysis_comment(analysis_store: MockStore, case_id: str):
    """Test adding comment to an analysis."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    comment: str = "test comment"

    # WHEN adding a comment
    analysis_store.update_analysis_comment(case_id=analysis.family, comment=comment)

    # THEN a comment should have been added
    assert analysis.comment == comment


def test_update_analysis_comment_when_existing(analysis_store: MockStore, case_id: str):
    """Test adding comment to an analysis when a comment already exists."""

    # GIVEN a store with an analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    first_comment: str = "One"
    second_comment: str = "Second"

    # WHEN adding a comment
    analysis_store.update_analysis_comment(case_id=analysis.family, comment=first_comment)
    analysis_store.update_analysis_comment(case_id=analysis.family, comment=second_comment)

    # THEN comments should have been added
    assert analysis.comment == f"{first_comment} {second_comment}"


def test_update_analysis_from_slurm_run_status(
    analysis_store: MockStore,
    mocker,
    ongoing_analysis_case_id: str,
    slurm_squeue_output: dict[str, str],
):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.jobs

    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        "trailblazer.store.crud.update.get_slurm_squeue_output",
        return_value=subprocess.check_output(
            ["cat", slurm_squeue_output.get(ongoing_analysis_case_id)]
        ).decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8),
    )

    # WHEN updating the analysis
    analysis_store.update_analysis_from_slurm_output(
        analysis_id=analysis.id, analysis_host="a_host"
    )
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_id=analysis.family, started_at=analysis.started_at, status=TrailblazerStatus.RUNNING
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.jobs


def test_update_tower_jobs(analysis_store: MockStore, tower_jobs: list[dict], case_id: str):
    """Assess that jobs are successfully updated when using NF Tower."""

    # GIVEN an analysis without jobs
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN analysis jobs are deleted
    analysis_store.delete_analysis_jobs(analysis=analysis)

    # THEN the analysis object should have no jobs
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN jobs should be updated
    assert len(analysis.jobs) == 2


@pytest.mark.parametrize(
    "case_id, status, progress",
    [
        (CaseId.RUNNING, TrailblazerStatus.RUNNING, 0.15),
        (CaseId.PENDING, TrailblazerStatus.PENDING, 0),
        (CaseId.COMPLETED, TrailblazerStatus.QC, 1),
    ],
)
def test_update_run_status_using_tower(
    analysis_store: MockStore,
    case_id: str,
    status: str,
    progress: int,
    mocker,
    tower_case_config: dict[str, dict],
):
    """Assess that an analysis status is successfully updated when using NF Tower."""

    # GIVEN Tower API response for an analysis
    raw_case: dict = tower_case_config.get(case_id)
    tower_api = MockTowerAPI(workflow_id=raw_case.get("tower_id"))
    tower_api.mock_query(response_file=raw_case.get("workflow_response_file"))
    tower_api.mock_tasks_query(response_file=raw_case.get("tasks_response_file"))
    mocker.patch("trailblazer.store.crud.update.get_tower_api", return_value=tower_api)

    # GIVEN an analysis with pending status
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status == TrailblazerStatus.PENDING
    assert analysis.workflow_manager == WorkflowManager.TOWER

    # WHEN the database is updated once
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is updated
    assert analysis.status == status
    assert analysis.progress == progress

    # WHEN the database is updated a second time
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is unchanged, and no database errors were raised
    assert analysis.status == status
    assert analysis.progress == progress


def test_update_analysis_with_comment(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis without a comment
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    analysis.comment = ""

    # WHEN updating the analysis with a comment
    analysis_store.update_analysis(analysis_id=analysis.id, comment="test")

    # THEN the comment should be set
    assert analysis.comment == "test"


def test_update_analysis_status(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis with a non failed status
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    assert analysis.status != "failed"

    # WHEN giving the analysis a status
    analysis_store.update_analysis(analysis_id=analysis.id, status="failed")

    # THEN the status should be set
    assert analysis.status == "failed"


def test_update_analysis_visibility(analysis_store: MockStore, case_id: str):
    # GIVEN an analysis which is not visible
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id)
    analysis.is_visible = False

    # WHEN making the analysis visible
    analysis_store.update_analysis(analysis_id=analysis.id, is_visible=True)

    # THEN the analysis should be visible
    assert analysis.is_visible
