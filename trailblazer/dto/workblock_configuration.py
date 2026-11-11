from datetime import datetime

from pydantic import BaseModel, Field


class Workblock(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    workflows: list[str] = Field(min_length=1)


class WorkblockConfigurationResponse(BaseModel):
    version: int
    workblocks: list[Workblock]
    updated_by: str | None = None
    updated_at: datetime | None = None


class WorkblockConfigurationRequest(BaseModel):
    version: int = Field(strict=True, ge=1)
    workblocks: list[Workblock] = Field(min_length=1, max_length=5)
