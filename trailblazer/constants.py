COMPLETED_STATUS = "completed"
FAILED_STATUS = "failed"
ONGOING_STATUSES = ("pending", "running", "error")
STARTED_STATUSES = ["completed", "failed", "pending", "running", "error"]
SLURM_NORMAL_CATEGORIES = ("completed", "running", "pending")
SLURM_FAILED_CATEGORIES = ("failed", "cancelled", "timeout")
SLURM_ACTIVE_CATEGORIES = ("running", "pending")

STATUS_OPTIONS = ("pending", "running", "completed", "failed", "error", "canceled")
JOB_STATUS_OPTIONS = SLURM_NORMAL_CATEGORIES + SLURM_FAILED_CATEGORIES
PRIORITY_OPTIONS = ("low", "normal", "high")
TYPES = ("wes", "wgs", "rna", "tgs", "other")
