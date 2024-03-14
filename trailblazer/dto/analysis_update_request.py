from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus


class AnalysisUpdateRequest(BaseModel):
    comment: str | None = None
    is_delivered: bool | None = None
    is_visible: bool | None = None
    status: TrailblazerStatus | None = None
