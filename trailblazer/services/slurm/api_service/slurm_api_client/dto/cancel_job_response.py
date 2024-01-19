from pydantic import BaseModel

from trailblazer.services.slurm.api_service.slurm_api_client.dto.common import (
    SlurmError,
    SlurmWarning,
)


class SlurmCancelJobResponse(BaseModel):
    errors: list[SlurmError] | None
    warnings: list[SlurmWarning] | None
