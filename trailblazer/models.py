from pydantic import BaseModel, Field


class Config(BaseModel):
    """Initialize base settings."""

    database_url: str = Field("sqlite:///:memory:")
