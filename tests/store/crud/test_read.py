from typing import List

from tests.mocks.store_mock import MockStore
from trailblazer.store.models import User
from tests.store.utils.store_helper import StoreHelpers


def test_get_users(user_store: MockStore, user_email: str, username: str):
    """Test getting a user with username and email."""
    # GIVEN a database with a user

    # WHEN getting users
    users: List[User] = user_store.get_users(name=username, email=user_email)

    # THEN the user should be returned
    assert users[0].email == user_email


def test_get_users_including_archived(user_store: MockStore, user_email: str, username: str):
    """Test getting a user with username and email which are archived."""
    # GIVEN a database with a user and an archived user
    StoreHelpers.add_user(
        name=username, email="old.user@magnolia.com", store=user_store, is_archived=True
    )

    # WHEN getting users
    users: List[User] = user_store.get_users(name=username, exclude_archived=False)

    # THEN the two users should be returned
    assert len(users) == 2


def test_get_users_no_username(user_store: MockStore, user_email: str):
    """Test getting a user by email."""
    # GIVEN a database with a user

    # WHEN getting users
    users: List[User] = user_store.get_users(email=user_email)

    # THEN the user should be returned
    assert users[0].email == user_email
