"""Model SLURM output."""
from datetime import datetime
from typing import List, Dict, Optional, Any

from pydantic import BaseModel, validator

from trailblazer.utils.datetime import convert_days_to_min, convert_timestamp_to_min


class SqueueJob(BaseModel):
    """Model job meta data from squeue output."""

    id: int
    step: str
    status: str
    time_limit: str
    time_elapsed: int
    started: Optional[datetime] = None

    @validator("status", always=True, pre=True)
    def convert_status_to_lower_case(cls, value: str) -> str:
        """Convert string to lower case."""
        return value.lower()

    @validator("time_elapsed", always=True, pre=True)
    def convert_time_elapsed_to_min(cls, value: str) -> int:
        """Convert squeue timestamp string into number of minutes."""
        raw_time_elapsed: str = value
        if not raw_time_elapsed or not isinstance(raw_time_elapsed, str):
            return 0
        timestamps: List[str] = []
        if "-" in raw_time_elapsed:
            timestamps: List[str] = raw_time_elapsed.split("-")
        day_nr: int = int(timestamps[0]) if timestamps else 0
        raw_timestamp: str = timestamps[1] if timestamps else raw_time_elapsed
        time_format_map: Dict[int, str] = {
            1: "%M:%S",
            2: "%H:%M:%S",
        }
        delimiter_nr: int = raw_time_elapsed.count(":")
        time_elapsed: datetime = datetime.strptime(raw_timestamp, time_format_map[delimiter_nr])
        return convert_timestamp_to_min(timestamp=time_elapsed) + convert_days_to_min(
            days_nr=day_nr
        )

    @validator("started", always=True)
    def convert_started_to_date(cls, value: str) -> datetime:
        """Convert started to datetime object."""
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value


class SqueueResult(BaseModel):
    """This model is used to parse SLURM squeue output."""

    jobs: List[SqueueJob]
    jobs_status_distribution: Optional[Dict[str, float]]

    @validator("jobs_status_distribution", always=True)
    def set_jobs_status_distribution(
        cls, _: Optional[List[SqueueJob]], values: Dict[str, Any]
    ) -> Dict[str, float]:
        """Set the job status distribution."""
        jobs: List[SqueueJob] = values["jobs"]
        status_distribution: Dict[str, float] = {}
        for job in jobs:
            status_distribution[job.status] = status_distribution.get(job.status, 0) + 1
        for status in status_distribution:
            status_distribution[status] = round(status_distribution[status] / len(jobs), 2)
            return status_distribution
