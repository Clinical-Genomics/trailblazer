"""Model SLURM output."""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

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
    started_at: datetime | None = Field(None, alias=SlurmSqueueHeader.START_TIME.value)

    @field_validator("status", mode="before")
    @classmethod
    def convert_status_to_lower_case(cls, raw_status: str) -> str:
        """Convert string to lower case."""
        return raw_status.lower()

    @field_validator("time_elapsed", mode="before")
    @classmethod
    def convert_time_elapsed_to_minutes(cls, raw_time_elapsed: str) -> int:
        """Convert squeue timestamp string into minutes."""
        if not raw_time_elapsed or not isinstance(raw_time_elapsed, str):
            return 0
        timestamps: list[str] = []
        if "-" in raw_time_elapsed:
            timestamps: list[str] = raw_time_elapsed.split("-")
        day_nr: int = int(timestamps[0]) if timestamps else 0
        raw_timestamp: str = timestamps[1] if timestamps else raw_time_elapsed
        time_elapsed: datetime = get_datetime_from_timestamp(
            timestamp=raw_timestamp, datetime_formats=["%M:%S", "%H:%M:%S"]
        )
        return convert_timestamp_to_minutes(timestamp=time_elapsed) + convert_days_to_minutes(
            days_nr=day_nr
        )

    @field_validator("started_at", mode="before")
    @classmethod
    def convert_started_at_to_datetime(cls, raw_started: str) -> datetime | None:
        """Convert started to datetime if string is in datetime format."""
        if isinstance(raw_started, str) and raw_started not in {"N/A"}:
            return datetime.strptime(raw_started, "%Y-%m-%dT%H:%M:%S")


class SqueueResult(BaseModel):
    """Model used to parse SLURM squeue output."""

    jobs: list[SqueueJob]
    jobs_status_distribution: dict[str, float] | None = None

    @model_validator(mode="after")
    def set_jobs_status_distribution(self):
        """Set the fraction for each status present in the squeue jobs.
        Example {PENDING:0.33, RUNNING:0.33, FAILED: 0.33}."""
        if not self.jobs:
            raise MissingSqueueOutput("No squeue output")
        job_statuses: list[str] = [job.status for job in self.jobs]
        self.jobs_status_distribution = {
            job_status: round(job_statuses.count(job_status) / len(self.jobs), 2)
            for job_status in set(job_statuses)
        }
