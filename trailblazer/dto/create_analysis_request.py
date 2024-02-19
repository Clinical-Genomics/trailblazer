from pydantic import BaseModel

from trailblazer.constants import TrailblazerPriority, TrailblazerTypes, WorkflowManager


class CreateAnalysisRequest(BaseModel):
    case_id: str
    email: str | None = None
    config_path: str
    out_dir: str
    order_id: int | None = None
    priority: TrailblazerPriority
    workflow: str | None = None
    ticket: str | None = None
    type: TrailblazerTypes
    workflow_manager: WorkflowManager | None = None
