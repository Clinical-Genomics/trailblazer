from enum import Enum
from typing import Dict

COMPLETED_STATUS = "completed"
FAILED_STATUS = "failed"
ONGOING_STATUSES = ("pending", "running", "error", "completing")
ONE_MONTH_IN_DAYS: int = 31
PRIORITY_OPTIONS = ("low", "normal", "high", "express", "maintenance")
SLURM_ACTIVE_CATEGORIES = ("running", "pending", "completing")
SLURM_FAILED_CATEGORIES = ("failed", "cancelled", "timeout")
SLURM_NORMAL_CATEGORIES = ("completed", "running", "pending", "completing")
JOB_STATUS_OPTIONS = SLURM_NORMAL_CATEGORIES + SLURM_FAILED_CATEGORIES
STARTED_STATUSES = ["completed", "failed", "pending", "running", "error", "completing"]
TYPES = ("other", "rna", "tgs", "wes", "wgs", "wts")


class FileFormat(str, Enum):
    JSON: str = "json"
    YAML: str = "yaml"


class FileExtension(str, Enum):
    JSON: str = ".json"
    YAML: str = ".yaml"


class WorkflowManager(Enum):
    """Supported task managers."""

    SLURM: str = "slurm"
    TOWER: str = "nf_tower"

    @classmethod
    def list(cls):
        return [task.value for task in cls]


class TrailblazerStatus(Enum):
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
    "ABORTED": TrailblazerStatus.FAILED.value,
    "CACHED": TrailblazerStatus.COMPLETED.value,
    "CANCELLED": TrailblazerStatus.FAILED.value,
    "COMPLETED": TrailblazerStatus.COMPLETED.value,
    "FAILED": TrailblazerStatus.FAILED.value,
    "NEW": TrailblazerStatus.PENDING.value,
    "RUNNING": TrailblazerStatus.RUNNING.value,
    "SUBMITTED": TrailblazerStatus.PENDING.value,
    "SUCCEEDED": TrailblazerStatus.COMPLETED.value,
    "UNKNOWN": TrailblazerStatus.FAILED.value,
}


TOWER_PROCESS_STATUS: Dict[str, str] = {
    "submitted": TrailblazerStatus.PENDING.value,
    "pending": TrailblazerStatus.PENDING.value,
    "running": TrailblazerStatus.RUNNING.value,
    "cached": TrailblazerStatus.COMPLETED.value,
    "succeeded": TrailblazerStatus.COMPLETED.value,
    "failed": TrailblazerStatus.FAILED.value,
}

TOWER_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TOWER_TIMESTAMP_FORMAT_ALTERNATIVE = "%Y-%m-%dT%H:%M:%S.%fZ"

STATUS_OPTIONS = tuple(TrailblazerStatus.list())
