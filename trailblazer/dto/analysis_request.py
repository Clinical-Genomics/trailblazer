from pydantic import BaseModel

from trailblazer.constants import TrailblazerPriority, TrailblazerStatus, TrailblazerTypes


class AnalysisRequest(BaseModel):
    search: str | None = None
    pageSize: int | None = 250
    page: int | None = 1
    sortField: str | None = "started_at"
    sortOrder: str | None = "desc"
    status: list[TrailblazerStatus] | None = []
    priority: list[TrailblazerPriority] | None = []
    type: list[TrailblazerTypes] | None = []
    comment: list[str] | None = []
