"""Model SLURM output."""
from typing import List, Optional

from pydantic import BaseModel, validator
from dateutil.parser import parse as parse_datestr


class SqueueJob(BaseModel):
    """Model job meta data from squeue output."""

    id: int
    step: str
    status: str
    time_limit: str
    time_elapsed: int
    started: str

    @validator("time_elapsed", always=True, pre=True)
    def convert_time_elapsed_to_min(cls, value: str) -> Optional[int]:
        elapsed_string: str = value
        if not elapsed_string or not isinstance(elapsed_string, str):
            return 0
        days = 0
        if "-" in elapsed_string:
            days = int(elapsed_string.split("-")[0])
            elapsed_string = elapsed_string.split("-")[1]
        split_timestamp = elapsed_string.split(":")
        if len(split_timestamp) < 3:
            split_timestamp = list("0" * (3 - len(split_timestamp))) + split_timestamp
        return int(
            (parse_datestr(":".join(split_timestamp)) - parse_datestr("0:0:0")).seconds / 60
            + days * 24 * 60
        )


class SqueueResult(BaseModel):
    """This model is used to parse SLURM squeue output."""

    jobs: List[SqueueJob]
