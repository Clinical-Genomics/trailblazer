from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import (
    filter_users_by_email,
    filter_users_by_contains_email,
    filter_users_by_contains_name,
    filter_users_by_is_not_archived,
)
from trailblazer.store.models import User
from tests.store.utils.store_helper import StoreHelpers


def test_filter_users_by_email(user_store: MockStore, user_email: str):
    """Test return user by email."""
    # GIVEN a store containing a user

    # WHEN retrieving a user by email
    users: Query = filter_users_by_email(users=user_store.get_query(table=User), email=user_email)

    # ASSERT that the users is a query
    assert isinstance(users, Query)

    # THEN the users attribute email should match the original
    assert users[0].email == user_email


def test_filter_users_by_contains_email(user_store: MockStore, user_email: str):
    """Test return user by email when using an incomplete email."""
    # GIVEN a store containing a user

    # WHEN retrieving a user by email
    users: Query = filter_users_by_contains_email(
        users=user_store.get_query(table=User), email=user_email[4]
    )

    # ASSERT that the users is a query
    assert isinstance(users, Query)

    # THEN the users attribute email should match the original
    assert users[0].email == user_email


def test_filter_users_by_contains_name(user_store: MockStore, username: str):
    """Test return user which contains name."""
    # GIVEN a store containing a user

    # WHEN retrieving a user by name
    users: Query = filter_users_by_contains_name(
        users=user_store.get_query(table=User), name=username
    )

    # THEN the users is a query
    assert isinstance(users, Query)

    # THEN the users attribute name should match the original
    assert users[0].name == username


def test_filter_users_by_not_archived(user_store: MockStore, username: str):
    """Test return user which contains name and is not archived."""
    # GIVEN a store containing a not archived user and an archived user
    StoreHelpers.add_user(name="New User", email="new.user@magnolia.com", is_archived=True)

    # WHEN retrieving a not archived user by name
    users: Query = filter_users_by_is_not_archived(
        users=user_store.get_query(table=User), name=username
    )

    # THEN the users is a query
    assert isinstance(users, Query)

    # THEN only one user should be returned
    assert users.count() == 1

    # THEN the users attribute name should match the original
    assert users[0].name == username
