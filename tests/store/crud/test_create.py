from typing import List

from tests.mocks.store_mock import MockStore
from trailblazer.store.models import Analysis


def test_add_pending_analysis(raw_analyses: List[dict], store: MockStore, user_email: str):
    """Test adding a new analysis to the database."""
    # GIVEN an empty database
    assert not store.get_query(table=Analysis).first()

    # GIVEN an unprocessed raw analysis
    analysis: dict = raw_analyses[0]

    # WHEN adding a new analysis
    new_analysis: Analysis = store.add_pending_analysis(
        case_id=analysis.get("family"),
        config_path=analysis.get("config_path"),
        email=user_email,
        out_dir=analysis.get("out_dir"),
        priority=analysis.get("priority"),
        type=analysis.get("type"),
    )

    # THEN it should be stored in the database
    stored_analysis: Analysis = store.get_analysis(
        case_id=analysis.get("family"),
        started_at=new_analysis.started_at,
        status=analysis.get("status"),
    )
    assert new_analysis and stored_analysis
    assert stored_analysis == new_analysis
