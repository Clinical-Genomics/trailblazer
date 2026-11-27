from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from trailblazer.constants import WORKFLOWS


class Workblock(BaseModel):
    id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    workflows: list[str] = Field(min_length=1)

    @field_validator("id", "name", mode="before")
    @classmethod
    def trim_spaces(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("workflows")
    @classmethod
    def validate_workflows(cls, workflows: list[str]) -> list[str]:
        normalized = [workflow.strip().lower() for workflow in workflows]

        for workflow in normalized:
            if workflow not in WORKFLOWS:
                raise ValueError(f"Unsupported workflow: {workflow}")

        return normalized


class WorkblockConfigurationResponse(BaseModel):
    version: int
    workblocks: list[Workblock]
    updated_by: str | None = None
    updated_at: datetime | None = None


class WorkblockConfigurationRequest(BaseModel):
    version: int = Field(strict=True, ge=1)
    workblocks: list[Workblock] = Field(min_length=1, max_length=5)

    @model_validator(mode="after")
    def validate_unique_assignments(self):
        ids = set()
        workflows = set()

        for workblock in self.workblocks:
            if workblock.id in ids:
                raise ValueError(f"Duplicate workblock ID: {workblock.id}")
            ids.add(workblock.id)

            for workflow in workblock.workflows:
                if workflow in workflows:
                    raise ValueError(f"Workflow assigned more than once: {workflow}")
                workflows.add(workflow)

        return self
