from pydantic import BaseModel

from trailblazer.constants import JobType


class CreateJobRequest(BaseModel):
    name: str
    job_type: JobType | None = JobType.ANALYSIS
    slurm_id: int
