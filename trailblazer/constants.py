from enum import Enum

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


class TrailblazerStatus(Enum):
    """Trailblazer allowed status."""

    PENDING: str = "pending"
    RUNNING: str = "running"
    COMPLETED: str = "completed"
    FAILED: str = "failed"
    ERROR: str = "error"
    CANCELLED: str = "cancelled"
    COMPLETING: str = "completing"


TOWER_STATUS = dict(
    SUBMITTED=TrailblazerStatus.PENDING.value,
    RUNNING=TrailblazerStatus.RUNNING.value,
    SUCCEEDED=TrailblazerStatus.COMPLETED.value,
    FAILED=TrailblazerStatus.FAILED.value,
    CANCELLED=TrailblazerStatus.CANCELLED.value,
    COMPLETED=TrailblazerStatus.COMPLETED.value,
)

PROCESS_STATUS = dict(
    submitted=TrailblazerStatus.PENDING.value,
    pending=TrailblazerStatus.PENDING.value,
    running=TrailblazerStatus.RUNNING.value,
    cached=TrailblazerStatus.COMPLETED.value,
    succeeded=TrailblazerStatus.COMPLETED.value,
    failed=TrailblazerStatus.FAILED.value,
)

TOWER_TIMESPAM_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
