from trailblazer.clients.slurm_api_client.dto.job_response import SlurmJobResponse
from trailblazer.clients.tower.models import TowerTasksResponse, TowerWorkflowResponse
from trailblazer.constants import TrailblazerStatus
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis


def test_updating_tower_analysis(
    analysis_service: AnalysisService,
    tower_analysis: Analysis,
    tower_tasks_response: TowerTasksResponse,
    tower_workflow_response: TowerWorkflowResponse,
):

    # GIVEN an analysis started with tower without any job entries but running tasks
    analysis_service.job_service.tower_service.client.get_tasks.return_value = tower_tasks_response
    analysis_service.job_service.tower_service.client.get_workflow.return_value = (
        tower_workflow_response
    )

    # WHEN updating the tower analysis
    analysis_service.update_analysis_meta_data(tower_analysis.id)

    # THEN job entries have been created for the analysis
    assert tower_analysis.jobs

    # THEN the status of the analysis is running
    assert tower_analysis.status == TrailblazerStatus.RUNNING

    # THEN the progress of the analysis is updated
    assert tower_analysis.progress > 0


def test_updating_slurm_analysis(
    analysis_service: AnalysisService,
    slurm_analysis: Analysis,
    slurm_job_response: SlurmJobResponse,
):

    # GIVEN an analysis started with slurm without any job entries but running jobs
    analysis_service.job_service.slurm_service.client.get_job.return_value = slurm_job_response

    # WHEN updating the slurm analysis
    analysis_service.update_analysis_meta_data(slurm_analysis.id)

    # THEN job entries have been created for the analysis
    assert slurm_analysis.jobs

    # THEN the status of the analysis is running
    assert slurm_analysis.status == TrailblazerStatus.COMPLETED

    # THEN the progress of the analysis is updated
    assert slurm_analysis.progress > 0
