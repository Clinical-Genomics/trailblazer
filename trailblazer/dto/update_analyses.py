from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus


class AnalysisUpdate(BaseModel):
    id: int

    comment: str | None = None
    delivered: bool | None = None
    is_visible: bool | None = None
    status: TrailblazerStatus | None = None


class UpdateAnalyses(BaseModel):
    analyses: list[AnalysisUpdate]
