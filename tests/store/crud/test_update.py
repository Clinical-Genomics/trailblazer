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
