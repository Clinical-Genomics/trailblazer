from pydantic import BaseModel


class SlurmError(BaseModel):
    description: str | None = None
    error_number: int | None = None
    error: str | None = None
    source: str | None = None


class SlurmWarning(BaseModel):
    description: str | None = None
    source: str | None = None
