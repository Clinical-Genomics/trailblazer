from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import User


def test_add_user(user_store: MockStore, user_email: str, username: str):
    """Test adding a user to the database."""
    # GIVEN an empty database
    assert not user_store.get_query(table=User).first()

    # WHEN adding a new user
    new_user: User = user_store.add_user(name=username, email=user_email)

    # THEN it should be stored in the database
    user: User = apply_user_filter(
        filter_functions=[UserFilter.BY_EMAIL],
        users=user_store.get_query(table=User),
        email=user_email,
    ).first()
    assert new_user
    assert user == new_user
