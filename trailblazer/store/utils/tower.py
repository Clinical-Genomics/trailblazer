from datetime import datetime
from typing import Optional

from trailblazer.constants import (
    PROCESS_STATUS,
    TOWER_STATUS,
    TOWER_TIMESPAM_FORMAT,
    TrailblazerStatus,
)


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
    def date_created(self) -> datetime:
        return datetime.strptime(self.process.get("dateCreated"), TOWER_TIMESPAM_FORMAT)

    @property
    def last_updated(self) -> datetime:
        return datetime.strptime(self.process.get("lastUpdated"), TOWER_TIMESPAM_FORMAT)

    @property
    def time_since_creation(self) -> str:
        """Returns time elapsed from creation to last update."""
        pass  # TODO: self.last_update - self.date_created

    @property
    def is_complete(self) -> bool:
        """Returns if the process succeded."""
        return self.status == TrailblazerStatus.COMPLETED.value


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
    def date_created(self) -> datetime:
        return datetime.strptime(self.task.get("dateCreated"), TOWER_TIMESPAM_FORMAT)

    @property
    def last_updated(self) -> datetime:
        return datetime.strptime(self.task.get("lastUpdated"), TOWER_TIMESPAM_FORMAT)

    @property
    def start(self) -> Optional[datetime]:
        start = self.task.get("start")
        if start == "null" or start is None:
            return None
        else:
            return datetime.strptime(start, TOWER_TIMESPAM_FORMAT)

    @property
    def duration(self) -> str:
        """Returns duration in seconds."""
        return self.task.get("duration", 0) or 0

    @property
    def is_complete(self) -> bool:
        """Returns if the process succeded."""
        return self.status == TrailblazerStatus.COMPLETED.value
