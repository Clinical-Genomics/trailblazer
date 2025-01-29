from pydantic import BaseModel

from trailblazer.constants import TrailblazerPriority, TrailblazerTypes, WorkflowManager


class CreateAnalysisRequest(BaseModel):
    case_id: str
    config_path: str
    email: str | None = None
    is_hidden: bool | None = None
    order_id: int | None = None
    out_dir: str
    priority: TrailblazerPriority
    ticket: str | None = None
    tower_workflow_id: str | None = None
    type: TrailblazerTypes
    workflow: str | None = None
    workflow_manager: WorkflowManager | None = None
