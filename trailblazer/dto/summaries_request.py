from typing_extensions import Annotated
from pydantic import BaseModel, BeforeValidator, Field, ValidationInfo


def parse_order_ids(v: str) -> list[str]:
    return v[0].split(",") if v else []


class SummariesRequest(BaseModel):
    order_ids: Annotated[list[int], BeforeValidator(parse_order_ids)] = Field(alias="orderIds")
