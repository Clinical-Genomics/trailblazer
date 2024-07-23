import logging

from trailblazer.clients.tower.models import TowerTaskResponse
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.services.tower.dtos import TowerJobInfo
from trailblazer.services.tower.utils import create_job_dto


LOG = logging.getLogger(__name__)


class TowerAPIService:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, tower_client: TowerAPIClient) -> None:
        self.tower_client = tower_client
        self.dry_run: bool = False

    def get_jobs(self, workflow_id: str) -> list[TowerJobInfo]:
        response: TowerTaskResponse = self.tower_client.get_tasks(workflow_id)
        return [create_job_dto(task) for task in response.tasks]

    def cancel_workflow(self, workflow_id: str) -> None:
        self.tower_client.cancel_workflow(workflow_id)
