from typing import List

from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import apply_user_filter, UserFilter
from trailblazer.store.models import User, Analysis


def test_add_pending_analysis(raw_analyses: List[dict], store: MockStore, user_email: str):
    """Test adding a new analysis to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=Analysis).first()

    # GIVEN an unprocessed raw analysis
    analysis: dict = raw_analyses[0]

    # WHEN adding a new analysis
    new_analysis: Analysis = store.add_pending_analysis(
        case_id=analysis.get("family"),
        config_path=analysis.get("config_path"),
        email=user_email,
        out_dir=analysis.get("out_dir"),
        priority=analysis.get("priority"),
        type=analysis.get("type"),
    )

    # THEN it should be stored in the database
    stored_analysis: Analysis = store.get_analysis(
        case_id=analysis.get("family"),
        started_at=new_analysis.started_at,
        status=analysis.get("status"),
    )
    assert new_analysis
    assert stored_analysis == new_analysis


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
