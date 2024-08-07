from trailblazer.clients.tower.models import TowerTaskResponse
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.services.tower.utils import create_job_dto, get_tower_workflow_id
from trailblazer.store.models import Job
from trailblazer.store.store import Store


class TowerAPIService:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, client: TowerAPIClient, store: Store) -> None:
        self.client = client
        self.store = store

    def get_jobs(self, analysis_id: int) -> list[Job]:
        analysis = self.store.get_analysis_with_id(analysis_id)
        workflow_id: str = get_tower_workflow_id(analysis)
        response: TowerTaskResponse = self.client.get_tasks(workflow_id)
        return [create_job_dto(task) for task in response.get_tasks()]

    def cancel_workflow(self, workflow_id: str) -> None:
        self.client.cancel_workflow(workflow_id)
