from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

from trailblazer.constants import TrailblazerPriority, TrailblazerStatus, TrailblazerTypes, Workflow
from trailblazer.dto.common import SortOrder


class AnalysisSortField(StrEnum):
    CASE_ID: str = "case_id"
    TICKET_ID: str = "ticket_id"
    STARTED_AT: str = "started_at"
    STATUS: str = "status"
    UPLOADED_AT: str = "uploaded_at"


class AnalysesRequest(BaseModel):
    workflow: str = ""
    workflows: list[Workflow] = []
    exclude_workflow: list[Workflow] = Field(alias="excludeWorkflow", default=[])
    search: str | None = None
    page_size: int | None = Field(alias="pageSize", default=None)
    page: int = 1
    sort_field: AnalysisSortField = Field(alias="sortField", default=AnalysisSortField.STARTED_AT)
    sort_order: SortOrder = Field(alias="sortOrder", default=SortOrder.DESC)
    status: list[TrailblazerStatus] = []
    priority: list[TrailblazerPriority] = []
    type: list[TrailblazerTypes] = []
    has_comment: bool | None = Field(alias="hasComment", default=None)
    hold_delivery: bool | None = Field(alias="holdDelivery", default=None)
    order_id: int | None = Field(alias="orderId", default=None)
    case_id: str | None = None
    delivered: bool | None = None
    include_hidden: bool | None = Field(alias="includeHidden", default=None)

    @field_validator("workflows", mode="before")
    @classmethod
    def normalize_workflows(cls, value):
        if isinstance(value, list):
            return [item.upper() if isinstance(item, str) else item for item in value]
        return value

    @model_validator(mode="after")
    def validate_workflow_filters(self):
        if self.workflow and self.workflows:
            raise ValueError("Use either workflow or workflows[], not both")
        return self
