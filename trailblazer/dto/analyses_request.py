from enum import StrEnum
from pydantic import BaseModel, Field

from trailblazer.constants import (
    TrailblazerPriority,
    TrailblazerStatus,
    TrailblazerTypes,
)
from trailblazer.dto.common import SortOrder


class AnalysisSortField(StrEnum):
    CASE_ID: str = "case_id"
    TICKET_ID: str = "ticket_id"
    STARTED_AT: str = "started_at"
    STATUS: str = "status"
    UPLOADED_AT: str = "uploaded_at"


class AnalysesRequest(BaseModel):
    workflow: str = ""
    search: str | None = None
    page_size: int = Field(alias="pageSize", default=250)
    page: int = 1
    sort_field: AnalysisSortField = Field(alias="sortField", default=AnalysisSortField.STARTED_AT)
    sort_order: SortOrder = Field(alias="sortOrder", default=SortOrder.DESC)
    status: list[TrailblazerStatus] = []
    priority: list[TrailblazerPriority] = []
    type: list[TrailblazerTypes] = []
    has_comment: bool | None = Field(alias="hasComment", default=None)
    order_id: int | None = Field(alias="orderId", default=None)
    case_id: str | None = None
    delivered: bool | None = None
    include_hidden: bool | None = Field(alias="includeHidden", default=None)
