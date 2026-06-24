from pydantic import BaseModel

from trailblazer.constants import TrailblazerStatus


class AnalysisUpdateRequest(BaseModel):
    # TODO: Add hold_delivery boolean field
    comment: str | None = None
    is_delivered: bool | None = None
    is_visible: bool | None = None
    status: TrailblazerStatus | None = None
