"""API for executors."""

import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd
from ruamel.yaml import safe_load

from trailblazer.constants import PROCESS_STATUS, TOWER_STATUS, TrailblazerStatus
from trailblazer.store import models
from trailblazer.store.models import Job

LOG = logging.getLogger(__name__)


class TowerProcess:
    """Class for Tower Process."""

    def __init__(self, process: dict):
        self.process: dict = process

    @property
    def name(self) -> str:
        return self.process.get("process")

    @property
    def status(self) -> str:
        for status_flag in PROCESS_STATUS.keys():
            if self.process.get(status_flag, 0):
                return PROCESS_STATUS.get(status_flag)
        return TrailblazerStatus.ERROR

    @property
    def date_created(self) -> str:
        return self.process.get("dateCreated")

    @property
    def last_updated(self) -> str:
        return self.process.get("lastUpdated")

    @property
    def time_since_creation(self) -> str:
        """Returns time elapsed from creation to last update."""
        pass  # TODO: self.last_update - self.date_created

    @property
    def is_complete(self) -> bool:
        """Returns if the process succeded."""
        if self.status == TrailblazerStatus.COMPLETED.value:
            return True
        else:
            return False


class TowerTask:
    """Class for Tower Task."""

    def __init__(self, task: dict):
        self.task: dict = task

    @property
    def name(self) -> str:
        return self.task.get("process")

    @property
    def slurm_id(self) -> str:
        return self.task.get("nativeId", None)

    @property
    def status(self) -> str:
        return TOWER_STATUS.get(self.task.get("status"))

    @property
    def date_created(self) -> str:
        return self.task.get("dateCreated")

    @property
    def last_updated(self) -> str:
        return self.task.get("lastUpdated")

    @property
    def start(self) -> str:
        return None if self.task.get("start") == "null" else self.task.get("start")

    @property
    def duration(self) -> str:
        """Returns duration in seconds."""
        return self.task.get("duration")

    @property
    def is_complete(self) -> bool:
        """Returns if the process succeded."""
        return self.status == TrailblazerStatus.COMPLETED.value


class ExecutorAPI:
    """Handles communication between executors and trailblazer."""

    def __init__(self, id_file: Path, dry_run: Optional[bool] = False):
        self.id_file: Path = id_file
        self.dry_run: bool = dry_run


class TowerAPI(ExecutorAPI):
    """Handles communication with tower."""

    @property
    def executor_id(self) -> int:
        """Returns executor id"""
        id_dict = safe_load(open(self.id_file))
        return id_dict.get(next(iter(id_dict)))[0]

    @property
    def response(self) -> dict:
        """Returns a response dictionary."""
        return self.query()

    @property
    def status(self) -> str:
        """Returns the status of a workflow."""
        return TOWER_STATUS.get(self.response["workflow"]["status"])

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
            TowerProcess(process=process)
            for process in self.response["progress"]["processesProgress"]
        ]

    @property
    def tasks(self) -> List[TowerTask]:
        """Returns tasks."""
        return [TowerTask(task=task["task"]) for task in self.tasks_response["tasks"]]

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

    # def get_jobs(self, analysis_id: str) -> List[Job]:
    #     """Returns a list of jobs associated to a workflow."""
    #     return [
    #         self._get_job(process=process, analysis_id=analysis_id) for process in self.processes
    #     ]
    #
    # def _get_job(self, process: TowerProcess, analysis_id: str) -> dict:
    #     """Format a job with required information."""
    #     return models.Job(
    #         analysis_id=analysis_id,
    #         name=process.name,
    #         status=process.status,
    #         started_at=process.date_created,
    #         elapsed=process.time_since_creation,
    #     )

    def get_jobs(self, analysis_id: str) -> List[Job]:
        """Returns a list of jobs associated to a workflow."""
        return [self._get_job(task=task, analysis_id=analysis_id) for task in self.tasks]

    def _get_job(self, task: TowerTask, analysis_id: str) -> Job:
        """Format a job with required information."""
        return models.Job(
            analysis_id=analysis_id,
            slurm_id=task.slurm_id,
            name=task.name,
            status=task.status,
            started_at=task.start,
            elapsed=task.duration / 60,
        )

    def query(self) -> dict:
        """Query tower."""
        pass


class SlurmAPI(ExecutorAPI):
    pass
