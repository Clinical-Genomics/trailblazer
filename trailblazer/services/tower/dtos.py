from datetime import datetime
from pydantic import BaseModel

from trailblazer.constants import SlurmJobStatus


class TowerJobInfo(BaseModel):
    job_id: int
    name: str | None = None
    status: SlurmJobStatus
    started_at: datetime | None = None
    elapsed: int | None = None
