from tests.mocks.store_mock import MockStore
from trailblazer.apps.slurm.api import get_squeue_result
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.store.filters.user_filters import apply_user_filter, UserFilter
from trailblazer.store.models import User, Analysis


def test_add_user(store: MockStore, user_email: str, username: str):
    """Test adding a user to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=User).first()

    # WHEN adding a new user
    new_user: User = store.add_user(name=username, email=user_email)

    # THEN it should be stored in the database
    user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=store.get_query(table=User),
        email=user_email,
    ).first()
    assert new_user
    assert user == new_user


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


def test_update_slurm_jobs_2(analysis_store: MockStore, squeue_stream_jobs: str):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.failed_jobs

    squeue_result: SqueueResult = get_squeue_result(squeue_response=squeue_stream_jobs)

    # WHEN updating the analysis
    analysis_store.update_slurm_jobs(analysis=analysis, squeue_result=squeue_result)
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_id=analysis.family, started_at=analysis.started_at, status="pending"
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.failed_jobs
