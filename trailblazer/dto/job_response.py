from pydantic import BaseModel

from trailblazer.constants import JobType


class JobResponse(BaseModel):
    slurm_id: int
    analysis_id: int
