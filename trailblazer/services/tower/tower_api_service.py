import logging

from trailblazer.clients.tower.models import (
    TowerProcess,
    TowerTask,
    TowerTaskResponse,
    TowerWorkflow,
    TowerWorkflowResponse,
)
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import TOWER_WORKFLOW_STATUS, TrailblazerStatus


LOG = logging.getLogger(__name__)


class TowerAPIService:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, tower_client: TowerAPIClient, dry_run: bool = False) -> None:
        self.dry_run: bool = dry_run
        self.tower_client = tower_client

    def get_jobs(self):
        pass
