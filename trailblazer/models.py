from pydantic import BaseModel, Field


class Config(BaseModel):
    """Initialize bse settings."""

    database: str = Field("sqlite:///:memory:", Alias="database")
    root: str = Field(..., Alias="root")
