from datetime import datetime

from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.filters.job_filters import filter_jobs_by_status, filter_jobs_by_since_when
from trailblazer.store.models import Job


def test_filter_jobs_by_since_when(job_store: MockStore, timestamp_yesterday: datetime):
    """Test return jobs started after the given date."""
    # GIVEN a store containing jobs

    # WHEN retrieving a job by date
    jobs: Query = filter_jobs_by_since_when(
        jobs=job_store.get_query(table=Job), since_when=timestamp_yesterday
    )

    # ASSERT that the jobs is a query
    assert isinstance(jobs, Query)

    # THEN the jobs should have benn started after the given date
    for job in jobs:
        assert job.started_at > timestamp_yesterday


def test_filter_jobs_by_since_when_with_current_date(job_store: MockStore, timestamp_now: datetime):
    """Test return jobs started before the given date."""
    # GIVEN a store containing jobs

    # WHEN retrieving a job by date
    jobs: Query = filter_jobs_by_since_when(
        jobs=job_store.get_query(table=Job), since_when=timestamp_now
    )

    # ASSERT that no jobs are returned
    assert not jobs.count()


def test_filter_jobs_by_status(job_store: MockStore):
    """Test return jobs by status."""
    # GIVEN a store containing jobs

    # WHEN retrieving a job by status
    jobs: Query = filter_jobs_by_status(
        jobs=job_store.get_query(table=Job), status=TrailblazerStatus.COMPLETED
    )

    # ASSERT that the jobs is a query
    assert isinstance(jobs, Query)

    # THEN the jobs attribute status should match the original
    assert jobs[0].status == TrailblazerStatus.COMPLETED
