from pydantic import BaseModel


class SlurmJobInfo(BaseModel):
    slurm_id: int
    name: str
    status: str
    started_at: str
    elapsed: int
