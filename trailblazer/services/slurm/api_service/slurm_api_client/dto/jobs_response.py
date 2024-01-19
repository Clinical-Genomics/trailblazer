from pydantic import BaseModel

from trailblazer.services.slurm.api_service.slurm_api_client.dto.common import (
    SlurmError,
    SlurmJobInfo,
    SlurmWarning,
)


class SlurmJobsResponse(BaseModel):
    jobs: list[SlurmJobInfo]
    errors: list[SlurmError] | None = None
    warnings: list[SlurmWarning] | None = None
