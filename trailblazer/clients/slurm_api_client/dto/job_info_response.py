from pydantic import BaseModel

from trailblazer.clients.slurm_api_client.dtos.common import SlurmError, SlurmJobInfo, SlurmWarning


class SlurmJobInfoResponse(BaseModel):
    jobs: list[SlurmJobInfo]
    errors: list[SlurmError] | None
    warnings: list[SlurmWarning] | None
