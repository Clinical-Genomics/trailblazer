from pydantic import BaseModel


class StatusSummary(BaseModel):
    count: int = 0
    case_ids: list[str] = []


class Summary(BaseModel):
    order_id: int
    total: int

    cancelled: StatusSummary
    completed: StatusSummary
    delivered: StatusSummary
    failed: StatusSummary
    running: StatusSummary


class SummariesResponse(BaseModel):
    summaries: list[Summary]
