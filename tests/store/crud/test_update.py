from datetime import datetime

from tests.mocks.store_mock import MockStore
from trailblazer.store.models import Info


def test_set_latest_update_date(store: MockStore):
    """Test setting the info table latest updated date."""

    # GIVEN a store which is empty apart from the initialized info entry
    assert store._get_query(table=Info).first().updated_at is None

    # WHEN setting the last updated date
    store.set_latest_update_date()
    info: Info = store._get_query(table=Info).first()

    # THEN it should update info entry with the current date
    assert isinstance(info.updated_at, datetime)
