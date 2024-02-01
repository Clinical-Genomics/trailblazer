from pydantic import BaseModel

from trailblazer.constants import JobType, TrailblazerPriority, TrailblazerTypes, WorkflowManager


class CreateAnalysisRequest(BaseModel):
    case_id: str
    email: str | None = None
    type: JobType | None = JobType.ANALYSIS
    config_path: str
    out_dir: str
    priority: TrailblazerPriority
    data_analysis: TrailblazerTypes
    ticket_id: str | None = None
    workflow_manager: WorkflowManager | None = None
