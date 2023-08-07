"""Model SLURM output."""
from datetime import datetime
from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, validator

from trailblazer.constants import SlurmJobStatus, SlurmSqueueHeader
from trailblazer.exc import MissingSqueueOutput
from trailblazer.utils.datetime import (
    convert_days_to_minutes,
    convert_timestamp_to_minutes,
    get_datetime_from_timestamp,
)


class SqueueJob(BaseModel):
    """Model job meta data from squeue output."""

    id: int = Field(..., alias=SlurmSqueueHeader.JOBID.value)
    step: str = Field(..., alias=SlurmSqueueHeader.NAME.value)
    status: SlurmJobStatus = Field(..., alias=SlurmSqueueHeader.STATE.value)
    time_limit: str = Field(..., alias=SlurmSqueueHeader.TIME_LIMIT.value)
    time_elapsed: int = Field(..., alias=SlurmSqueueHeader.TIME.value)
    started_at: Optional[datetime] = Field(..., alias=SlurmSqueueHeader.START_TIME.value)

    @validator("status", always=True, pre=True)
    def convert_status_to_lower_case(cls, value: str) -> str:
        """Convert string to lower case."""
        return value.lower()

    @validator("time_elapsed", always=True, pre=True)
    def convert_time_elapsed_to_minutes(cls, value: str) -> int:
        """Convert squeue timestamp string into minutes."""
        raw_time_elapsed: str = value
        if not raw_time_elapsed or not isinstance(raw_time_elapsed, str):
            return 0
        timestamps: List[str] = []
        if "-" in raw_time_elapsed:
            timestamps: List[str] = raw_time_elapsed.split("-")
        day_nr: int = int(timestamps[0]) if timestamps else 0
        raw_timestamp: str = timestamps[1] if timestamps else raw_time_elapsed
        time_elapsed: datetime = get_datetime_from_timestamp(
            timestamp=raw_timestamp, datetime_formats=["%M:%S", "%H:%M:%S"]
        )
        return convert_timestamp_to_minutes(timestamp=time_elapsed) + convert_days_to_minutes(
            days_nr=day_nr
        )

    @validator("started_at", always=True, pre=True)
    def convert_started_at_to_datetime(cls, value: str) -> Optional[datetime]:
        """Convert started to datetime if string is in datetime format."""
        raw_started: str = value
        if isinstance(raw_started, str) and raw_started not in {"N/A"}:
            return datetime.strptime(raw_started, "%Y-%m-%dT%H:%M:%S")


class SqueueResult(BaseModel):
    """Model used to parse SLURM squeue output."""

    jobs: List[SqueueJob]
    jobs_status_distribution: Optional[Dict[str, float]]

    @validator("jobs_status_distribution", always=True)
    def set_jobs_status_distribution(
        cls, _: Optional[List[SqueueJob]], values: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """Set the fraction for each status present in the squeue jobs.
        Example {PENDING:0.33, RUNNING:0.33, FAILED: 0.33}."""
        jobs: List[SqueueJob] = values["jobs"]
        if not jobs:
            raise MissingSqueueOutput("No squeue output")
        status_distribution: Dict[str, float] = {}
        job_statuses: List[str] = [job.status for job in jobs]
        for job_status in set(job_statuses):
            status_distribution[job_status] = round(job_statuses.count(job_status) / len(jobs), 2)
        return status_distribution
