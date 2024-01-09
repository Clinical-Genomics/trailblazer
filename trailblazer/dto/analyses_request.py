from pydantic import BaseModel, Field

from trailblazer.constants import TrailblazerPriority, TrailblazerStatus, TrailblazerTypes


class AnalysesRequest(BaseModel):
    pipeline: str | None = ""
    search: str | None = None
    page_size: int | None = Field(alias="pageSize", default=250)
    page: int | None = 1
    sort_field: str | None = Field(alias="sortField", default="started_at")
    sort_order: str | None = Field(alias="sortOrder", default="desc")
    status: list[TrailblazerStatus] | None = []
    priority: list[TrailblazerPriority] | None = []
    type: list[TrailblazerTypes] | None = []
    comment: list[str] | None = []
