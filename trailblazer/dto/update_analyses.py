from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus


class AnalysisUpdate(BaseModel):
    analysis_id: int
    status: TrailblazerStatus | None = None
    comment: str | None = None
    is_visible: bool | None = None


class UpdateAnalyses(BaseModel):
    analyses: list[AnalysisUpdate]
