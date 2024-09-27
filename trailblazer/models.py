from pydantic import BaseModel, Field


class Config(BaseModel):
    """Initialize base settings."""

    database_url: str = Field("sqlite:///:memory:")
    tower_base_url: str = Field("a_tower_endpoint_url")
    tower_access_token: str = Field("a_tower_access_token")
