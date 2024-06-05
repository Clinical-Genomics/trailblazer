from pydantic import BaseModel

from trailblazer.clients.slurm_api_client.dto.common import (
    SlurmError,
    SlurmAPIJobInfo,
    SlurmWarning,
)


class SlurmJobResponse(BaseModel):
    jobs: list[SlurmAPIJobInfo]
    errors: list[SlurmError] | None = None
    warnings: list[SlurmWarning] | None = None
