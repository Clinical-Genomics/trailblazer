from typing import Self

from pydantic import BaseModel, model_validator

from trailblazer.constants import TrailblazerPriority, TrailblazerTypes, WorkflowManager


class CreateAnalysisRequest(BaseModel):
    case_id: str
    config_path: str | None = None
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

    @model_validator(mode="after")
    def check_config_path_set_for_slurm_workflow_manager(self) -> Self:
        if (self.workflow_manager == WorkflowManager.SLURM) and (not self.config_path):
            raise ValueError("config_path needs to be set when SLURM is workflow manager")
        return self
