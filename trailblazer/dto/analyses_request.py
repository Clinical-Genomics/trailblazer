from pydantic import BaseModel, Field

from trailblazer.constants import (
    TrailblazerPriority,
    TrailblazerStatus,
    TrailblazerTypes,
)


class AnalysesRequest(BaseModel):
    workflow: str = ""
    search: str | None = None
    page_size: int = Field(alias="pageSize", default=250)
    page: int = 1
    sort_field: str = Field(alias="sortField", default="started_at")
    sort_order: str = Field(alias="sortOrder", default="desc")
    status: list[TrailblazerStatus] = []
    priority: list[TrailblazerPriority] = []
    type: list[TrailblazerTypes] = []
    has_comment: bool | None = Field(alias="hasComment", default=None)
    order_id: int | None = Field(alias="orderId", default=None)
    case_id: str | None = None
