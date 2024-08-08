from trailblazer.clients.tower.models import TowerTasksResponse
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.services.tower.utils import create_job_from_dto, get_tower_workflow_id
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
        jobs: list[Job] = [create_job_from_dto(task) for task in response.get_tasks()]
        self.store.replace_jobs(analysis_id=analysis_id, jobs=jobs)

    def cancel_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        workflow_id: str = get_tower_workflow_id(analysis)
        self.client.cancel_workflow(workflow_id)
