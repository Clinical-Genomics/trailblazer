from datetime import datetime
from enum import Enum
from typing import Callable

from sqlalchemy.orm import Query

from trailblazer.store.models import Job


def filter_jobs_by_since_when(jobs: Query, since_when: datetime, **kwargs) -> Query:
    """Filter jobs before the supplied date."""
    return jobs.filter(Job.started_at > since_when)


def filter_jobs_by_status(jobs: Query, status: str, **kwargs) -> Query:
    """Filter jobs with matching status."""
    return jobs.filter(Job.status == status)


def filter_jobs_by_statuses(jobs: Query, statuses: list[str], **kwargs) -> Query:
    return jobs.filter(Job.status.in_(statuses))


def filter_jobs_by_analysis_id(jobs: Query, analysis_id: str, **kwargs) -> Query:
    """Filter jobs with matching analysis id."""
    return jobs.filter(Job.analysis_id == analysis_id)


def sort_jobs_by_started_at(jobs: Query, **kwargs) -> Query:
    """Sort jobs by start date."""
    return jobs.order_by(Job.started_at.desc())


def filter_jobs_by_id(jobs: Query, job_id: int, **kwargs) -> Query:
    """Filter jobs with matching id."""
    return jobs.filter(Job.id == job_id)


def filter_by_job_type(jobs: Query, job_type: str, **kwargs):
    return jobs.filter(Job.job_type == job_type)


class JobFilter(Enum):
    """Define Job filter functions."""

    BY_SINCE_WHEN: Callable = filter_jobs_by_since_when
    BY_STATUS: Callable = filter_jobs_by_status
    BY_STATUSES: Callable = filter_jobs_by_statuses
    BY_ANALYSIS_ID: Callable = filter_jobs_by_analysis_id
    BY_ID: Callable = filter_jobs_by_id
    BY_TYPE: Callable = filter_by_job_type
    SORT_BY_STARTED_AT: Callable = sort_jobs_by_started_at


def apply_job_filters(
    jobs: Query,
    filters: list[Callable],
    since_when: datetime | None = None,
    status: str | None = None,
    statuses: list[str] | None = None,
    analysis_id: str | None = None,
    job_id: int | None = None,
    job_type: str | None = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filters:
        jobs: Query = function(
            jobs=jobs,
            since_when=since_when,
            status=status,
            statuses=statuses,
            analysis_id=analysis_id,
            job_id=job_id,
            job_type=job_type,
        )
    return jobs
