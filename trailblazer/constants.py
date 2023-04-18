from enum import Enum
from typing import Dict

COMPLETED_STATUS = "completed"
FAILED_STATUS = "failed"
ONGOING_STATUSES = ("pending", "running", "error", "completing")
STARTED_STATUSES = ["completed", "failed", "pending", "running", "error", "completing"]
SLURM_NORMAL_CATEGORIES = ("completed", "running", "pending", "completing")
SLURM_FAILED_CATEGORIES = ("failed", "cancelled", "timeout")
SLURM_ACTIVE_CATEGORIES = ("running", "pending", "completing")

STATUS_OPTIONS = ("pending", "running", "completed", "failed", "error", "canceled", "completing")
JOB_STATUS_OPTIONS = SLURM_NORMAL_CATEGORIES + SLURM_FAILED_CATEGORIES
PRIORITY_OPTIONS = ("low", "normal", "high", "express", "maintenance")
TYPES = ("other", "rna", "tgs", "wes", "wgs", "wts")


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


TOWER_STATUS: Dict[str, str] = {
    "SUBMITTED": TrailblazerStatus.PENDING.value,
    "RUNNING": TrailblazerStatus.RUNNING.value,
    "SUCCEEDED": TrailblazerStatus.COMPLETED.value,
    "FAILED": TrailblazerStatus.FAILED.value,
    "CANCELLED": TrailblazerStatus.CANCELLED.value,
    "COMPLETED": TrailblazerStatus.COMPLETED.value,
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
