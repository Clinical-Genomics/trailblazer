from pydantic import BaseModel


class Workblock(BaseModel):
    id: str
    name: str
    color: str
    workflows: list[str]


class WorkblockConfigurationResponse(BaseModel):
    version: int
    workblocks: list[Workblock]
