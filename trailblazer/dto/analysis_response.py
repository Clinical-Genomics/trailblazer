from datetime import datetime
from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus, WorkflowManager


class User(BaseModel):
    avatar: str | None = None
    created_at: datetime | None = None
    email: str | None = None
    id: int
    is_archived: bool | None = False
    name: str | None = None


class Job(BaseModel):
    analysis_id: int
    context: str | None = None
    elapsed: int
    id: int
    name: str
    slurm_id: int
    started_at: datetime | None = None
    status: str


class AnalysisResponse(BaseModel):
    id: int
    case_id: str
    version: str | None = None
    logged_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: TrailblazerStatus
    priority: str
    out_dir: str | None = None
    config_path: str | None = None
    comment: str | None = None
    is_deleted: bool = False
    is_visible: bool = True
    type: str | None = None
    user_id: int | None = None
    progress: float
    data_analysis: str | None = None
    ticket_id: str | None = None
    uploaded_at: datetime | None = None
    workflow_manager: WorkflowManager
    user: User | None = None
    latest_failed_job: Job | None = None
