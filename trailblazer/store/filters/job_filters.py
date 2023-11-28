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


def filter_jobs_by_analysis_id(jobs: Query, analysis_id: str, **kwargs) -> Query:
    """Filter jobs with matching analysis id."""
    return jobs.filter(Job.analysis_id == analysis_id)


def sort_jobs_by_started_at(jobs: Query, **kwargs) -> Query:
    """Sort jobs by start date."""
    return jobs.order_by(Job.started_at.desc())


class JobFilter(Enum):
    """Define Job filter functions."""

    FILTER_BY_SINCE_WHEN: Callable = filter_jobs_by_since_when
    FILTER_BY_STATUS: Callable = filter_jobs_by_status
    FILTER_BY_ANALYSIS_ID: Callable = filter_jobs_by_analysis_id
    SORT_BY_STARTED_AT: Callable = sort_jobs_by_started_at


def apply_job_filter(
    jobs: Query,
    filter_functions: list[Callable],
    since_when: datetime | None = None,
    status: str | None = None,
    analysis_id: str | None = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filter_functions:
        jobs: Query = function(
            jobs=jobs,
            since_when=since_when,
            status=status,
            analysis_id=analysis_id,
        )
    return jobs
