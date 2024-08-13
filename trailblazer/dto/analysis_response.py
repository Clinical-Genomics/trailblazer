from datetime import date, datetime

from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus, WorkflowManager


class User(BaseModel):
    created_at: datetime | None = None
    email: str | None = None
    id: int
    is_archived: bool | None = False
    name: str | None = None
    abbreviation: str | None = None


class Job(BaseModel):
    analysis_id: int
    context: str | None = None
    elapsed: int | None = None
    id: int
    name: str | None = None
    slurm_id: int
    started_at: datetime | None = None
    status: str


class AnalysisResponse(BaseModel):
    id: int
    case_id: str
    comment: str | None = None
    completed_at: datetime | None = None
    config_path: str | None = None
    delivered_by: str | None = None
    delivered_date: date | None = None
    is_visible: bool = True
    is_delivered: bool
    jobs: list[Job] = []
    latest_failed_job: Job | None = None
    logged_at: datetime | None = None
    order_id: int | None = None
    out_dir: str | None = None
    priority: str
    progress: float
    started_at: datetime | None = None
    status: TrailblazerStatus
    ticket_id: str | None = None
    type: str | None = None
    upload_jobs: list[Job] = []
    uploaded_at: datetime | None = None
    user_id: int | None = None
    user: User | None = None
    version: str | None = None
    workflow: str | None = None
    workflow_manager: WorkflowManager
