import pytest

from trailblazer.clients.tower.models import TowerWorkflowResponse
from trailblazer.constants import TrailblazerStatus, WorkflowManager
from trailblazer.exceptions import NoJobsError
from trailblazer.services.job_service import JobService
from trailblazer.store.models import Analysis


def test_job_progression_completed(job_service: JobService, analysis_with_completed_jobs: Analysis):
    # GIVEN an analysis with completed jobs

    # WHEN getting the analysis progression
    progression = job_service.get_analysis_progression(analysis_with_completed_jobs.id)

    # THEN the progression is 100%
    assert progression == 1.0


def test_job_progression_ongoing(job_service: JobService, analysis_with_running_jobs: Analysis):
    # GIVEN an analysis with ongoing jobs

    # WHEN getting the analysis progression
    progression = job_service.get_analysis_progression(analysis_with_running_jobs.id)

    # THEN the progression is less than 100%
    assert progression < 1.0


def test_job_progression_without_jobs(job_service: JobService, analysis_without_jobs: Analysis):
    # GIVEN an analysis without jobs

    # WHEN getting the analysis progression
    progression = job_service.get_analysis_progression(analysis_without_jobs.id)

    # THEN the progression is 0%
    assert progression == 0.0


def test_analysis_status_when_completed_jobs(
    job_service: JobService,
    analysis_with_completed_jobs: Analysis,
):
    # GIVEN an analysis with completed jobs

    # WHEN getting the analysis status
    status = job_service.get_analysis_status(analysis_with_completed_jobs.id)

    # THEN the status is completed
    assert status == TrailblazerStatus.COMPLETED


def test_analysis_status_when_running_jobs(
    job_service: JobService,
    analysis_with_running_jobs: Analysis,
):
    # GIVEN an analysis with running jobs

    # WHEN getting the analysis status
    status = job_service.get_analysis_status(analysis_with_running_jobs.id)

    # THEN the status is running
    assert status == TrailblazerStatus.RUNNING


def test_fetch_pending_status_for_tower_without_jobs(
    job_service: JobService,
    tower_response_submitted: TowerWorkflowResponse,
):
    """
    Verify that a Tower-managed analysis with no associated jobs returns a PENDING status
    when Tower reports the workflow as submitted.
    """
    # GIVEN a Tower analysis with workflow manager nf_tower and without jobs
    analysis: Analysis = job_service.store.get_query(Analysis).first()
    analysis.workflow_manager = WorkflowManager.TOWER
    assert not analysis.jobs

    # GIVEN a simulated response from tower with the return status being submitted
    job_service.tower_service.client.get_workflow.return_value = tower_response_submitted

    # WHEN fetching the analysis status
    status: TrailblazerStatus = job_service.get_analysis_status(analysis.id)

    # THEN the analysis status should be PENDING
    assert status == TrailblazerStatus.PENDING


def test_no_jobs_error_for_slurm_analysis(job_service: JobService, analysis_without_jobs: Analysis):
    """
    Ensure that a NoJobsError is raised for a SLURM analysis with no associated jobs.
    """
    # GIVEN an analysis without any associated jobs
    # WHEN fetching the analysis status
    # THEN a NoJobsError should be raised
    with pytest.raises(NoJobsError):
        job_service.get_analysis_status(analysis_without_jobs.id)
