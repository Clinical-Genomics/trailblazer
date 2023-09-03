from pydantic import BaseModel, Field


class Config(BaseModel):
    """Initialize bse settings."""

    database_url: str = Field("sqlite:///:memory:", Alias="database")
    hpc_analysis_root_dir: str = Field(..., Alias="root")
    service_account: str
    service_account_auth_file: str
    api_host: str = Field(..., Alias="host")
