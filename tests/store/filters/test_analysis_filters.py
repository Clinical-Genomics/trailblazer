from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.analyses_filters import filter_analyses_by_id
from trailblazer.store.models import Analysis


def test_filter_analyses_by_id(analysis_store: MockStore):
    """Test return analysis by id when existing."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving an analysis by id
    analysis: Query = filter_analyses_by_id(
        analyses=analysis_store.get_query(table=Analysis), analysis_id=existing_analysis.id
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()
