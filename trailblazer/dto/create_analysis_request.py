from pydantic import BaseModel

from trailblazer.constants import JobType, TrailblazerPriority, TrailblazerTypes, WorkflowManager


class CreateAnalysisRequest(BaseModel):
    case_id: str
    email: str | None = None
    config_path: str
    out_dir: str
    priority: TrailblazerPriority
    data_analysis: TrailblazerTypes | None = None
    ticket_id: str | None = None
    workflow_manager: WorkflowManager | None = None
