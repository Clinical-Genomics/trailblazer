from pydantic import BaseModel, Field


class Config(BaseModel):
    """Initialize base settings."""

    database_url: str | None = Field("sqlite:///:memory:")
