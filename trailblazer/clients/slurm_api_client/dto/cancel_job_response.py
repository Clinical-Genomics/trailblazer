from pydantic import BaseModel

from trailblazer.clients.slurm_api_client.dto.common import SlurmError, SlurmWarning


class SlurmCancelJobResponse(BaseModel):
    errors: list[SlurmError] | None
    warnings: list[SlurmWarning] | None
