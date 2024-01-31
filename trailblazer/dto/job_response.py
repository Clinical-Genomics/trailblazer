from pydantic import BaseModel

from trailblazer.constants import SlurmJobStatus


class JobResponse(BaseModel):
    id: int
    slurm_id: int
    analysis_id: int
    status: SlurmJobStatus
