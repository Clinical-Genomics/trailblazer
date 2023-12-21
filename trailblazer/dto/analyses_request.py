from typing import Any
from pydantic import BaseModel, Field, root_validator, validator


class AnalysesRequest(BaseModel):
    per_page: int = Field(default=100, alias="pageSize")
    page: int = Field(default=1)
    search: str | None = Field(default=None, alias="query")
    is_visible: bool | None = Field(default=False, alias="isVisible")
    sort_field: str | None = Field(default="started_at", alias="sortField")
    sort_order: str | None = Field(default=None, alias="sortOrder")
    filters: dict[str, list[Any]] = {}

    class Config:
        allow_population_by_field_name = True
        extra = "allow"

    @validator("filters", pre=True, always=True)
    def extract_filters(cls, v, values, **kwargs):
        return {
            key[:-2]: value if isinstance(value, list) else [value]
            for key, value in values.items()
            if key.endswith("[]")
        }

    @root_validator(pre=True)
    def handle_all_args(cls, values):
        return {k: v for k, v in values.items() if not k.endswith("[]")}
