from pydantic import BaseModel
from datetime import datetime


class FailedJob(BaseModel):
    analysis_id: int
    context: str | None = None
    elapsed: int
    id: int
    name: str
    slurm_id: int
    started_at: datetime | None = None
    status: str


class Analysis(BaseModel):
    case_id: str
    comment: str | None = None
    completed_at: datetime | None = None
    config_path: str | None = None
    data_analysis: str | None = None
    failed_job: FailedJob | None = None
    id: int
    is_deleted: bool = False
    is_visible: bool = True
    logged_at: datetime | None = None
    out_dir: str | None = None
    priority: str | None = None
    progress: float = 0.0
    started_at: datetime | None = None
    status: str | None = None
    ticket_id: str | None = None
    type: str | None = None
    uploaded_at: datetime | None = None
    user_id: int | None = None
    version: str | None = None
    workflow_manager: str


class AnalysisResponse(BaseModel):
    analyses: list[Analysis]
    total_count: int
