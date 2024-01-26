from pydantic import BaseModel


class JobDto(BaseModel):
    slurm_id: int
    name: str
    status: str
    started_at: str
    elapsed: int
