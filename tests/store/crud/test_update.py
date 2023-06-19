from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.user_filters import apply_user_filter, UserFilter
from trailblazer.store.models import User


def test_add_user(store: MockStore, user_email: str, username: str):
    """Test adding a user."""
    # GIVEN an empty database
    assert store.get_query(table=User).first() is None

    # WHEN adding a new user
    new_user: User = store.add_user(name=username, email=user_email)

    # THEN it should be stored in the database
    user: User = apply_user_filter(
        filter_functions=[UserFilter.FILTER_BY_EMAIL],
        users=store.get_query(table=User),
        email=user_email,
    ).first()
    assert user == new_user
