from pydantic import BaseModel

from trailblazer.clients.common import SlurmError, SlurmWarning


class SlurmCancelJobResponse(BaseModel):
    errors: list[SlurmError] | None
    warnings: list[SlurmWarning] | None
