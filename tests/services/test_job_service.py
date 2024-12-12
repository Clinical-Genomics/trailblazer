import pytest

from trailblazer.clients.tower.models import TowerWorkflowResponse
from trailblazer.constants import TrailblazerStatus, TowerStatus
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


def test_tower_analysis_status_pending_no_jobs(
    job_service: JobService,
    tower_analysis_without_jobs_and_pending: Analysis,
    tower_workflow_response: TowerWorkflowResponse,
    ## Add the analysis store fixture
):

    ### Inject the analysis store into the job service
    ### assert your created analysis is there

    ### do the test...
    # GIVEN a Tower analysis with no jobs and a SUBMITTED status
    job_service.tower_service.client.get_workflow.return_value = tower_workflow_response
    # set the job service store to the analysis store in the conftest
    # Simulate a SUBMITTED workflow status from Tower
    tower_workflow_response.workflow.status = TowerStatus.SUBMITTED

    # WHEN fetching the analysis status
    status = job_service.get_analysis_status(tower_analysis_without_jobs_and_pending.id)

    # THEN the analysis status should be PENDING
    assert status == TrailblazerStatus.PENDING


def test_no_jobs_error_for_slurm_analysis(job_service: JobService, analysis_without_jobs: Analysis):
    # GIVEN an analysis without any associated jobs
    # WHEN fetching the analysis status
    # THEN a NoJobsError should be raised
    with pytest.raises(NoJobsError):
        job_service.get_analysis_status(analysis_without_jobs.id)
