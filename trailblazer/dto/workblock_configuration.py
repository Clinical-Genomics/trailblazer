from datetime import datetime

from pydantic import BaseModel


class Workblock(BaseModel):
    id: str
    name: str
    color: str
    workflows: list[str]


class WorkblockConfigurationResponse(BaseModel):
    version: int
    workblocks: list[Workblock]
    updated_by: str | None = None
    updated_at: datetime | None = None
