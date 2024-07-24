from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import User


def test_add_user(store: MockStore, user_email: str, username: str):
    """Test adding a user to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=User).first()

    # WHEN adding a new user
    new_user: User = store.add_user(name=username, email=user_email, abbreviation="abb")

    # THEN it should be stored in the database
    user: User = apply_user_filter(
        filter_functions=[UserFilter.BY_EMAIL],
        users=store.get_query(table=User),
        email=user_email,
    ).first()
    assert new_user
    assert user == new_user
