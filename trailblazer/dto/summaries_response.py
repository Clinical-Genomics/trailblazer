from pydantic import BaseModel


class Summary(BaseModel):
    order_id: int
    total: int

    cancelled: int
    completed: int
    delivered: int
    failed: int
    running: int


class SummariesResponse(BaseModel):
    summaries: list[Summary]
