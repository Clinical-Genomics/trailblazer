from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.filters.job_filters import filter_jobs_by_status
from trailblazer.store.models import Job


def test_filter_jobs_by_status(job_store: MockStore, user_email: str):
    """Test return jobs by status."""
    # GIVEN a store containing jobs

    # WHEN retrieving a job by status
    jobs: Query = filter_jobs_by_status(
        jobs=job_store.get_query(table=Job), status=TrailblazerStatus.COMPLETED.value
    )

    # ASSERT that the jobs is a query
    assert isinstance(jobs, Query)

    # THEN the jobs attribute status should match the original
    assert jobs[0].status == TrailblazerStatus.COMPLETED.value
