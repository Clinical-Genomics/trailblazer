from trailblazer.clients.tower.models import TowerTasksResponse
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import TOWER_WORKFLOW_STATUS, TrailblazerStatus
from trailblazer.services.tower.error_handler import handle_errors
from trailblazer.services.tower.utils import create_job_from_tower_task
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store


class TowerAPIService:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, client: TowerAPIClient, store: Store) -> None:
        self.client = client
        self.store = store

    @handle_errors
    def update_jobs(self, analysis_id: int) -> list[Job]:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        response: TowerTasksResponse = self.client.get_tasks(analysis.tower_workflow_id)
        jobs: list[Job] = [create_job_from_tower_task(task) for task in response.get_tasks()]
        self.store.replace_jobs(analysis_id=analysis_id, jobs=jobs)

    @handle_errors
    def cancel_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        self.client.cancel_workflow(analysis.tower_workflow_id)
        self.update_jobs(analysis_id)

    @handle_errors
    def get_status(self, analysis_id: int) -> TrailblazerStatus:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        response = self.client.get_workflow(analysis.tower_workflow_id)
        status = TOWER_WORKFLOW_STATUS.get(response.workflow.status, TrailblazerStatus.ERROR)
        if status == TrailblazerStatus.COMPLETED:
            return TrailblazerStatus.QC
        return status
