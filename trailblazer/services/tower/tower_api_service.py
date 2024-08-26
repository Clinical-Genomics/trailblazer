from trailblazer.clients.tower.models import TowerTasksResponse
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import TOWER_WORKFLOW_STATUS, TrailblazerStatus
from trailblazer.services.tower.utils import create_job_from_tower_task, get_tower_workflow_id
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store


class TowerAPIService:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, client: TowerAPIClient, store: Store) -> None:
        self.client = client
        self.store = store

    def update_jobs(self, analysis_id: int) -> list[Job]:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        workflow_id: str = get_tower_workflow_id(analysis)
        response: TowerTasksResponse = self.client.get_tasks(workflow_id)
        jobs: list[Job] = [create_job_from_tower_task(task) for task in response.get_tasks()]
        self.store.replace_jobs(analysis_id=analysis_id, jobs=jobs)

    def cancel_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        workflow_id: str = get_tower_workflow_id(analysis)
        self.client.cancel_workflow(workflow_id)
        self.update_jobs(analysis_id)

    def get_status(self, analysis_id: int) -> TrailblazerStatus:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        workflow_id: str = get_tower_workflow_id(analysis)
        response = self.client.get_workflow(workflow_id)
        status = TOWER_WORKFLOW_STATUS.get(response.workflow.status, TrailblazerStatus.ERROR)
        if status == TrailblazerStatus.COMPLETED:
            return TrailblazerStatus.QC
        return status
