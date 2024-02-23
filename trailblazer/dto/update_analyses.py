from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus


class AnalysisUpdate(BaseModel):
    id: int
    status: TrailblazerStatus | None = None
    comment: str | None = None
    is_visible: bool | None = None


class UpdateAnalyses(BaseModel):
    analyses: list[AnalysisUpdate]
