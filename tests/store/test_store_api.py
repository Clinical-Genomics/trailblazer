from tests.mocks.store_mock import MockStore
from trailblazer.store.database import get_tables


def test_setup_db(store: MockStore):
    """Test store contains tables."""

    # GIVEN a store which is already setup

    # THEN it should contain tables
    assert get_tables()
