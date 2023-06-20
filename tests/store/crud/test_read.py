from tests.mocks.store_mock import MockStore
from trailblazer.store.models import User


def test_get_users(user_store: MockStore, user_email: str, username: str):
    """Test getting a user."""
    # GIVEN a database with a user

    # WHEN getting users
    users: User = user_store.get_users(name=username, email=user_email)

    # THEN the user should be returned
    assert users[0].email == user_email


def test_get_users_no_username(user_store: MockStore, user_email: str):
    """Test getting a user."""
    # GIVEN a database with a user

    # WHEN getting users
    users: User = user_store.get_users(email=user_email)

    # THEN the user should be returned
    assert users[0].email == user_email
