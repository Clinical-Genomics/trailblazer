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
TYPES = ("wes", "wgs", "rna", "tgs", "other")
