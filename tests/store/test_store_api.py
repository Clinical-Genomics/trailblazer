from tests.mocks.store_mock import MockStore


def test_setup_db(store: MockStore):
    """Test store contains tables."""

    # GIVEN a store which is already setup

    # THEN it should contain tables
    assert store.engine.table_names()
