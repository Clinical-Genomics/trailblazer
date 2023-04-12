"""API for executors."""

import logging
from typing import List

from trailblazer.constants import TOWER_STATUS, TrailblazerStatus
from trailblazer.store.utils.tower import TowerProcess, TowerTask
from trailblazer.store.utils.tower_client import TowerApiClient

LOG = logging.getLogger(__name__)


class ExecutorAPI:
    """Handles communication between executors and trailblazer."""

    pass


class TowerAPI(ExecutorAPI):
    """Handles communication with tower."""

    def __init__(self, executor_id: str, dry_run: bool = False):
        self.executor_id: str = executor_id
        self.dry_run: bool = dry_run

    @property
    def tower_client(self) -> TowerApiClient:
        """Returns a NF Tower client."""
        return TowerApiClient(workflow_id=self.executor_id)

    @property
    def response(self) -> dict:
        """Returns a workflow response dictionary."""
        return self.response or self.tower_client.workflow

    @property
    def tasks_response(self) -> dict:
        """Returns a tasks response dictionary."""
        return self.tasks_response or self.tower_client.tasks

    @property
    def status(self) -> str:
        """Returns the status of a workflow."""
        return TOWER_STATUS.get(self.response["workflow"]["status"], TrailblazerStatus.ERROR.value)

    @property
    def is_pending(self) -> bool:
        """Returns True if workflow has not started running. Otherwise returns False."""
        return self.status == TrailblazerStatus.PENDING.value

    @property
    def is_complete(self) -> bool:
        """Returns True if workflow has completed. Otherwise returns False."""
        return self.status == TrailblazerStatus.COMPLETED.value

    @property
    def processes(self) -> List[TowerProcess]:
        """Returns processes."""
        return [
            TowerProcess(**process) for process in self.response["progress"]["processesProgress"]
        ]

    @property
    def tasks(self) -> List[TowerTask]:
        """Returns tasks."""
        return [TowerTask(**task["task"]) for task in self.tasks_response["tasks"]]

    @property
    def total_jobs(self) -> int:
        """Returns the total number of jobs for a workflow."""
        return len(self.processes)

    @property
    def succeeded_jobs(self) -> int:
        """Returns the number of succeeded jobs for a workflow."""
        return sum(process.is_complete for process in self.processes)

    @property
    def progress(self) -> int:
        """Returns the progress percentage of a workflow.
        Note this number is not accurate since that exact number of
        processes to be run is unknown."""
        if self.is_complete:
            return 100
        elif self.is_pending:
            return 0
        else:
            return int(self.succeeded_jobs * 100.0 / self.total_jobs)

    def get_jobs(self, analysis_id: int) -> List[dict]:
        """Returns a list of jobs associated to a workflow."""
        return [self._get_job(task=task, analysis_id=analysis_id) for task in self.tasks]

    def _get_job(self, task: TowerTask, analysis_id: int) -> dict:
        """Format a job with required information."""
        return dict(
            analysis_id=analysis_id,
            slurm_id=task.nativeId,
            name=task.process,
            status=task.status,
            started_at=task.start,
            elapsed=int(task.duration / 60),
        )
