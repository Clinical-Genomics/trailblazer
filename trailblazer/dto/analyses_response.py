from datetime import date, datetime

from pydantic import BaseModel


class Job(BaseModel):
    analysis_id: int
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
    delivered_by: str | None = None
    delivered_date: date | None = None
    is_delivered: bool | None = None
    workflow: str | None = None
    failed_job: Job | None = None
    id: int
    is_visible: bool = True
    logged_at: datetime | None = None
    order_id: int | None = None
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


class AnalysesResponse(BaseModel):
    analyses: list[Analysis]
    total_count: int


class UpdateAnalysesResponse(BaseModel):
    analyses: list[Analysis]
