from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus


class AnalysisUpdateRequest(BaseModel):
    is_visible: bool | None = None
    comment: str | None = None
    status: TrailblazerStatus | None = None
