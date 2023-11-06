from enum import Enum
from typing import Dict, List, Tuple

ONE_MONTH_IN_DAYS: int = 31
HOURS_IN_DAY: int = 24
MINUTES_PER_HOUR: int = 60
SECONDS_PER_MINUTE: int = 60
PRIORITY_OPTIONS: Tuple = ("low", "normal", "high", "express", "maintenance")
TRAILBLAZER_TIME_STAMP: str = "%Y-%m-%d"
TOWER_TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
TOWER_TIMESTAMP_FORMAT_EXTENDED: str = "%Y-%m-%dT%H:%M:%S.%fZ"
TYPES: Tuple = ("other", "rna", "tgs", "wes", "wgs", "wts")


class FileFormat(str, Enum):
    CSV: str = "csv"
    JSON: str = "json"
    YAML: str = "yaml"


class FileExtension(str, Enum):
    CSV: str = ".csv"
    JSON: str = ".json"
    YAML: str = ".yaml"


class WorkflowManager(Enum):
    """Supported task managers."""

    SLURM: str = "slurm"
    TOWER: str = "nf_tower"

    @classmethod
    def list(cls) -> List:
        return [task.value for task in cls]


class Pipeline(str, Enum):
    """Analysis pipeline names."""

    BALSAMIC: str = "BALSAMIC"
    MIP_DNA: str = "MIP-DNA"
    MIP_RNA: str = "MIP-RNA"
    SARS_COV_2: str = "SARS-COV-2"


class SlurmSqueueHeader(str, Enum):
    """SLURM squeue output headers."""

    JOBID: str = "JOBID"
    NAME: str = "NAME"
    START_TIME: str = "START_TIME"
    STATE: str = "STATE"
    TIME: str = "TIME"
    TIME_LIMIT: str = "TIME_LIMIT"


class SlurmJobStatus(str, Enum):
    """SLURM allowed status."""

    CANCELLED: str = "cancelled"
    COMPLETED: str = "completed"
    COMPLETING: str = "completing"
    FAILED: str = "failed"
    PENDING: str = "pending"
    RUNNING: str = "running"
    TIME_OUT: str = "timeout"

    @classmethod
    def statuses(cls) -> Tuple:
        return tuple(status.value for status in cls)

    @classmethod
    def ongoing_statuses(cls) -> Tuple:
        return cls.PENDING.value, cls.RUNNING.value, cls.COMPLETING.value


class CharacterFormat(str, Enum):
    """Define character encoding/decoding to use."""

    UNICODE_TRANSFORMATION_FORMAT_8: str = "utf-8"


class TrailblazerStatus(str, Enum):
    """Trailblazer allowed status."""

    CANCELLED: str = "cancelled"
    COMPLETED: str = "completed"
    COMPLETING: str = "completing"
    ERROR: str = "error"
    FAILED: str = "failed"
    PENDING: str = "pending"
    QC: str = "qc"
    RUNNING: str = "running"

    @classmethod
    def statuses(cls) -> Tuple:
        return tuple(status.value for status in cls)

    @classmethod
    def ongoing_statuses(cls) -> Tuple[str, str, str, str]:
        return cls.PENDING.value, cls.RUNNING.value, cls.COMPLETING.value, cls.ERROR.value


class TrailblazerStatusColor(str, Enum):
    """Trailblazer status colors."""

    COMPLETED: str = "green"
    DEFAULT: str = "white"
    FAILED: str = "red"
    PENDING: str = "yellow"
    RUNNING: str = "blue"


TOWER_WORKFLOW_STATUS: Dict[str, str] = {
    "ABORTED": TrailblazerStatus.FAILED,
    "CACHED": TrailblazerStatus.COMPLETED,
    "CANCELLED": TrailblazerStatus.CANCELLED,
    "COMPLETED": TrailblazerStatus.COMPLETED,
    "FAILED": TrailblazerStatus.FAILED,
    "NEW": TrailblazerStatus.PENDING,
    "RUNNING": TrailblazerStatus.RUNNING,
    "SUBMITTED": TrailblazerStatus.PENDING,
    "SUCCEEDED": TrailblazerStatus.COMPLETED,
    "UNKNOWN": TrailblazerStatus.FAILED,
}


TOWER_PROCESS_STATUS: Dict[str, str] = {
    "submitted": TrailblazerStatus.PENDING,
    "pending": TrailblazerStatus.PENDING,
    "running": TrailblazerStatus.RUNNING,
    "cached": TrailblazerStatus.COMPLETED,
    "succeeded": TrailblazerStatus.COMPLETED,
    "failed": TrailblazerStatus.FAILED,
}


TOWER_TASK_STATUS: Dict[str, str] = {
    "ABORTED": SlurmJobStatus.FAILED,
    "CACHED": SlurmJobStatus.COMPLETED,
    "CANCELLED": SlurmJobStatus.CANCELLED,
    "COMPLETED": SlurmJobStatus.COMPLETED,
    "FAILED": SlurmJobStatus.FAILED,
    "NEW": SlurmJobStatus.PENDING,
    "RUNNING": SlurmJobStatus.RUNNING,
    "SUBMITTED": SlurmJobStatus.PENDING,
    "SUCCEEDED": SlurmJobStatus.COMPLETED,
    "UNKNOWN": SlurmJobStatus.FAILED,
}
