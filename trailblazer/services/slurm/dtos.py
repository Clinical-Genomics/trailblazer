from datetime import datetime
from pydantic import BaseModel

from trailblazer.constants import SlurmJobStatus


class SlurmJobInfo(BaseModel):
    slurm_id: int
    name: str
    status: SlurmJobStatus
    started_at: datetime
    elapsed: int
