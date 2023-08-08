from typing import List

from tests.mocks.store_mock import MockStore
from trailblazer.apps.slurm.api import get_squeue_result
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.filters.user_filters import apply_user_filter, UserFilter
from trailblazer.store.models import User, Analysis


def test_update_analysis_jobs(analysis_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Test jobs are successfully updated."""

    # GIVEN an analysis without failed jobs
    analysis: Analysis = analysis_store.get_latest_analysis(case_id=case_id)
    assert not analysis.failed_jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN there should be jobs
    assert analysis.failed_jobs


def test_update_user_is_archived(user_store: MockStore, user_email: str):
    """Test updating user is archived attribute."""
    # GIVE a database and a not archived user
    user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()
    assert not user.is_archived

    # WHEN updating a user archive status
    user_store.update_user_is_archived(user=user, archive=True)

    archived_user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()

    # THEN user should be recorded as archived in the database
    assert archived_user


def test_update_analysis_jobs_from_slurm_jobs(analysis_store: MockStore, squeue_stream_jobs: str):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.failed_jobs

    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # WHEN updating the analysis
    analysis_store.update_analysis_jobs_from_slurm_jobs(
        analysis=analysis, squeue_result=squeue_result
    )
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_id=analysis.family, started_at=analysis.started_at, status=TrailblazerStatus.PENDING
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.failed_jobs
