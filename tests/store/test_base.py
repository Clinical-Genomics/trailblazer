from datetime import datetime

from tests.mocks.store_mock import MockStore
from trailblazer.store.models import Info


def test_info_query(info_store: MockStore):
    """Test base model table query."""

    # GIVEN a store

    # WHEN getting an object using the query
    info: Info = info_store.get_query(table=Info).first()

    # THEN it should return an Info object with a default "created_at" date
    assert isinstance(info.created_at, datetime)
