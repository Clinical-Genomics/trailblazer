from typing import List, Optional

from tests.mocks.store_mock import MockStore
from trailblazer.apps.slurm.api import get_squeue_result
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, User


def test_update_analysis_jobs(analysis_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Test jobs are successfully updated."""

    # GIVEN an analysis with no jobs
    analysis: Analysis = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN there should be jobs
    assert analysis.jobs


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
    assert not analysis.jobs

    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # WHEN updating the analysis
    analysis_store.update_analysis_jobs_from_slurm_jobs(
        analysis=analysis, squeue_result=squeue_result
    )
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_id=analysis.family, started_at=analysis.started_at, status=TrailblazerStatus.PENDING
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.jobs


def test_update_case_analyses_as_deleted(analysis_store: MockStore, ongoing_analysis_case_id: str):
    """Test marking case analyses as deleted."""
    # GIVEN case id for a case with analyses that are not deleted
    analyses: Optional[List[Analysis]] = analysis_store.get_analyses_for_case(
        case_id=ongoing_analysis_case_id
    )
    for analysis in analyses:
        assert not analysis.is_deleted

    # WHEN marking analyses as deleted
    analysis_store.update_case_analyses_as_deleted(case_id=ongoing_analysis_case_id)
    analyses: Optional[List[Analysis]] = analysis_store.get_analyses_for_case(
        case_id=ongoing_analysis_case_id
    )

    # THEN analyses are marked as deleted
    for analysis in analyses:
        assert analysis.is_deleted


def test_update_case_analyses_as_deleted_with_non_existing_case(
    analysis_store: MockStore, case_id_not_in_db: str
):
    """Test marking case analyses as deleted."""
    # GIVEN case id for that do not exist

    # WHEN marking analyses as deleted
    analyses: Optional[List[Analysis]] = analysis_store.update_case_analyses_as_deleted(
        case_id=case_id_not_in_db
    )

    # THEN no analyses are returned
    assert not analyses


def test_update_analysis_status_with_failed(analysis_store: MockStore, case_id: str):
    """Test setting analysis to failed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status != TrailblazerStatus.FAILED

    # WHEN setting analysis to failed
    analysis_store.update_analysis_status(case_id=analysis.family, status=TrailblazerStatus.FAILED)

    # THEN the analysis status should be updated to failed
    assert analysis.status == TrailblazerStatus.FAILED


def test_update_analysis_status_to_completed(analysis_store: MockStore, case_id: str):
    """Test setting analysis to completed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status != TrailblazerStatus.COMPLETED

    # WHEN setting analysis to completed
    analysis_store.update_analysis_status_to_completed(analysis_id=analysis.id)

    # THEN the analysis status should be updated to completed
    assert analysis.status == TrailblazerStatus.COMPLETED
