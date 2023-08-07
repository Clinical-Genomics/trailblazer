from enum import Enum
from typing import Dict

COMPLETED_STATUS = "completed"
FAILED_STATUS = "failed"
HOURS_IN_DAY: int = 24
MINUTES_PER_HOUR: int = 60
ONGOING_STATUSES = ("pending", "running", "error", "completing")
ONE_MONTH_IN_DAYS: int = 31
PRIORITY_OPTIONS = ("low", "normal", "high", "express", "maintenance")
SECONDS_PER_MINUTE: int = 60
SLURM_ACTIVE_CATEGORIES = ("running", "pending", "completing")
SLURM_FAILED_CATEGORIES = ("failed", "cancelled", "timeout")
SLURM_NORMAL_CATEGORIES = ("completed", "running", "pending", "completing")
JOB_STATUS_OPTIONS = SLURM_NORMAL_CATEGORIES + SLURM_FAILED_CATEGORIES
STARTED_STATUSES = ["completed", "failed", "pending", "running", "error", "completing"]
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

TOWER_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TOWER_TIMESTAMP_FORMAT_ALTERNATIVE = "%Y-%m-%dT%H:%M:%S.%fZ"

STATUS_OPTIONS = tuple(TrailblazerStatus.list())
