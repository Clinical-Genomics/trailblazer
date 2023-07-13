from typing import List

from tests.mocks.store_mock import MockStore
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


def test_update_analysis_jobs(sample_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Test jobs are successfully updated."""

    # GIVEN an analysis without failed jobs
    analysis: Analysis = sample_store.get_latest_analysis(case_id=case_id)
    assert not analysis.failed_jobs

    # WHEN jobs are updated
    sample_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

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
