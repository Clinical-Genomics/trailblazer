"""Module for Tower Open API."""

import logging
from pathlib import Path

from trailblazer.clients.tower.models import (
    TowerProcess,
    TowerTask,
    TowerTaskResponse,
    TowerWorkflowResponse,
)
from trailblazer.clients.tower.tower_client import TowerApiClient
from trailblazer.constants import TOWER_WORKFLOW_STATUS, FileFormat, TrailblazerStatus
from trailblazer.exc import TowerRequirementsError
from trailblazer.io.controller import ReadFile


LOG = logging.getLogger(__name__)


class TowerAPIService:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, tower_client: TowerApiClient, dry_run: bool = False) -> None:
        self.dry_run: bool = dry_run
        self.tower_client = tower_client
 
    @property
    def response(self) -> TowerWorkflowResponse:
        """Returns a workflow response containing general information about an analysis."""
        if not self._response:
            self._response = self.tower_client.get_workflow
        return self._response

    @property
    def tasks_response(self) -> TowerTaskResponse:
        """Returns a tasks response containing information about jobs submitted as part of an analysis.
        A task response does not include all jobs that will be run as part of an analysis.
        It only includes jobs that have been submitted a at given time that could be either
        pending, running, completed or failed."""
        if not self._tasks_response:
            self._tasks_response = self.tower_client.get_tasks
        return self._tasks_response

    @property
    def status(self) -> str:
        """Returns the status of an analysis (also called workflow in NF Tower)."""
        status: str = TOWER_WORKFLOW_STATUS.get(
            self.response.workflow.status, TrailblazerStatus.ERROR
        )

        # If the whole workflow (analysis) is completed set it as QC instead of COMPLETE
        if status == TrailblazerStatus.COMPLETED:
            return TrailblazerStatus.QC
        return status

    @property
    def is_pending(self) -> bool:
        """Returns True if workflow has not started running. Otherwise returns False."""
        return self.status == TrailblazerStatus.PENDING

    @property
    def is_complete(self) -> bool:
        """Returns True if workflow has completed. Otherwise returns False."""
        return self.status == TrailblazerStatus.QC

    @property
    def processes(self) -> list[TowerProcess]:
        """Returns processes. Processes are steps in a workflow that might or might not be executed by a given analysis.
        A process can also have more than one corresponding job (task).
        For example, a process could be a 'fastqc' step that could be run multiple times depending on
        how many input files are given."""
        return [TowerProcess(**process) for process in self.response.progress.processesProgress]

    @property
    def tasks(self) -> list[TowerTask]:
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
    def progress(self) -> float:
        """Returns the progress fraction of a workflow.
        Note this number is not accurate since that exact number of
        processes to be run is unknown."""
        if self.is_complete:
            return 1
        elif self.is_pending or self.total_jobs == 0:
            return 0
        else:
            return round(float(self.succeeded_jobs) / self.total_jobs, 2)

    def get_jobs(self, analysis_id: int) -> list[dict]:
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

    def cancel(self) -> None:
        """Cancel a workflow."""
        self.tower_client.cancel_workflow()
