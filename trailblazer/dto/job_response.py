from pydantic import BaseModel

from trailblazer.constants import JobType, SlurmJobStatus


class JobResponse(BaseModel):
    id: int
    slurm_id: int
    analysis_id: int
    status: SlurmJobStatus
