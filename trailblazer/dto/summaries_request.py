from pydantic import BaseModel


class SummariesRequest(BaseModel):
    order_ids: list[int]
