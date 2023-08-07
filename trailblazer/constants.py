from enum import Enum
from typing import Dict

ONE_MONTH_IN_DAYS: int = 31
HOURS_IN_DAY: int = 24
MINUTES_PER_HOUR: int = 60
SECONDS_PER_MINUTE: int = 60
PRIORITY_OPTIONS = ("low", "normal", "high", "express", "maintenance")
TOWER_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TOWER_TIMESTAMP_FORMAT_ALTERNATIVE = "%Y-%m-%dT%H:%M:%S.%fZ"
TYPES = ("other", "rna", "tgs", "wes", "wgs", "wts")


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
    def list(cls):
        return [task.value for task in cls]


class Pipeline(str, Enum):
    """Analysis pipeline names"""

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
    FAILED: str = "failed"
    PENDING: str = "pending"
    RUNNING: str = "running"
    TIME_OUT: str = "timeout"

    @classmethod
    def list(cls):
        return [status.value for status in cls]


class TrailblazerStatus(str, Enum):
    """Trailblazer allowed status."""

    PENDING: str = "pending"
    RUNNING: str = "running"
    COMPLETED: str = "completed"
    FAILED: str = "failed"
    ERROR: str = "error"
    CANCELLED: str = "canceled"
    COMPLETING: str = "completing"
    QC: str = "qc"

    @classmethod
    def list(cls):
        return [status.value for status in cls]


TOWER_STATUS: Dict[str, str] = {
    "ABORTED": TrailblazerStatus.FAILED,
    "CACHED": TrailblazerStatus.COMPLETED,
    "CANCELLED": TrailblazerStatus.FAILED,
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

STATUS_OPTIONS = tuple(TrailblazerStatus.list())
ONGOING_STATUSES = (
    TrailblazerStatus.PENDING,
    TrailblazerStatus.RUNNING,
    TrailblazerStatus.COMPLETING,
    TrailblazerStatus.ERROR,
)
JOB_STATUS_OPTIONS = tuple(SlurmJobStatus.list())
SLURM_ACTIVE_CATEGORIES = (
    SlurmJobStatus.PENDING,
    SlurmJobStatus.RUNNING,
    SlurmJobStatus.COMPLETING,
)
