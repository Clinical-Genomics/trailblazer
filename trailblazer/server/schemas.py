from pydantic import BaseModel


class AnalysisUpdate(BaseModel):
    is_visible: bool | None = None
    comment: str | None = None
    status: str | None = None
