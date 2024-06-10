from pydantic import BaseModel


class SlurmError(BaseModel):
    description: str | None = None
    error_number: int | None = None
    error: str | None = None
    source: str | None = None


class SlurmWarning(BaseModel):
    description: str | None = None
    source: str | None = None


class NumberWithFlags(BaseModel):
    set: bool | None = None
    infinite: bool | None = None
    number: int | None = None


class SlurmAPIJobInfo(BaseModel):
    accrue_time: NumberWithFlags | None = None
    job_id: int | None = None
    job_state: list[str] | None = None
    name: str | None = None
    start_time: NumberWithFlags | None = None
