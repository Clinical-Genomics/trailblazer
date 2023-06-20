from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import filter_users_by_email
from trailblazer.store.models import User


def test_filter_users_by_email(user_store: MockStore, user_email: str):
    """Test return bed by name."""
    # GIVEN a store containing a user

    # WHEN retrieving a user by email
    users: Query = filter_users_by_email(users=user_store.get_query(table=User), email=user_email)

    # ASSERT that the users is a query
    assert isinstance(users, Query)

    # THEN users should be returned
    assert users

    # THEN the users attribute email should match the original
    assert users[0].email == user_email
