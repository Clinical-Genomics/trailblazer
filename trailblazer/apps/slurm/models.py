"""Model SLURM output."""
from typing import List

from pydantic import BaseModel


class SqueueJob(BaseModel):
    """Model job meta data from squeue output."""

    id: int
    step: str
    status: str
    time_limit: str
    time_elapsed: str
    started: str


class SqueueResult(BaseModel):
    """This model is used to parse SLURM squeue output."""

    jobs: List[SqueueJob]
