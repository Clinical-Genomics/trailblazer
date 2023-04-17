"""API for executors."""

import logging
from typing import List

from trailblazer.constants import TOWER_STATUS, TrailblazerStatus
from trailblazer.store.utils.tower import (
    TowerProcess,
    TowerTask,
    TowerTaskResponse,
    TowerWorkflowResponse,
)
from trailblazer.store.utils.tower_client import TowerApiClient

LOG = logging.getLogger(__name__)


class ExecutorAPI:
    """Handles communication between executors and trailblazer."""

    pass


class TowerAPI(ExecutorAPI):
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, executor_id: str, dry_run: bool = False):
        self.executor_id: str = executor_id
        self.dry_run: bool = dry_run
        self._tower_client = None
        self._response = None
        self._tasks_response = None

    @property
    def tower_client(self) -> TowerApiClient:
        """Returns a NF Tower client."""
        if not self._tower_client:
            self._tower_client = TowerApiClient(workflow_id=self.executor_id)
        return self._tower_client

    @property
    def response(self) -> TowerWorkflowResponse:
        """Returns a workflow response containing general information about an analysis."""
        if not self._response:
            self._response = self.tower_client.workflow
        return self._response

    @property
    def tasks_response(self) -> TowerTaskResponse:
        """Returns a tasks response containing information about jobs submitted as part of an analysis.
        A task response does not include all jobs that will be run as part of an analysis.
        It only includes jobs that have been submitted a at given time that could be either
        pending, running, completed or failed."""
        if not self._tasks_response:
            self._tasks_response = self.tower_client.tasks
        return self._tasks_response

    @property
    def status(self) -> str:
        """Returns the status of an analysis (also called workflow in NF Tower)."""
        return TOWER_STATUS.get(self.response.workflow.status, TrailblazerStatus.ERROR.value)

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
        """Returns processes. Processes are steps in a pipeline that might or might not be executed by a given analysis.
        A process can also have more than one corresponding job (task).
        For example, a process could be a 'fastqc' step that could be run multiple times depending on
        how many input files are given."""
        return [TowerProcess(**process) for process in self.response.progress.processesProgress]

    @property
    def tasks(self) -> List[TowerTask]:
        """Returns tasks. Tasks correspond to jobs that have been submitted at a given point regardless of their
        status."""
        return [task["task"] for task in self.tasks_response.tasks]

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
