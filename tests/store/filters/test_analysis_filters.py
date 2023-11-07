import datetime

from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.store.filters.analyses_filters import (
    filter_analyses_by_before_started_at,
    filter_analyses_by_case_id,
    filter_analyses_by_comment,
    filter_analyses_by_entry_id,
    filter_analyses_by_is_visible,
    filter_analyses_by_search_term,
    filter_analyses_by_started_at,
    filter_analyses_by_status,
    filter_analyses_by_statuses,
)
from trailblazer.store.models import Analysis


def test_filter_analyses_by_id(analysis_store: MockStore):
    """Test return analysis by id when existing."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving an analysis by id
    analysis: Query = filter_analyses_by_entry_id(
        analyses=analysis_store.get_query(table=Analysis), analysis_id=existing_analysis.id
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()


def test_filter_analyses_by_case_id(analysis_store: MockStore):
    """Test return analysis by case id when existing."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving an analysis by case id
    analysis: Query = filter_analyses_by_case_id(
        analyses=analysis_store.get_query(table=Analysis), case_id=existing_analysis.family
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()


def test_filter_analyses_by_comment(analysis_store: MockStore, analysis_comment: str):
    """Test return analysis by comment when containing string."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # GIVEN a comment
    existing_analysis.comment = analysis_comment

    # WHEN retrieving an analysis by comment
    analysis: Query = filter_analyses_by_comment(
        analyses=analysis_store.get_query(table=Analysis), comment=existing_analysis.comment
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()


def test_filter_analyses_by_comment_when_not_matching(analysis_store: MockStore):
    """Test return analysis by comment when not containing string."""
    # GIVEN a store containing analyses

    # GIVEN a comment that does not exist in the database

    # WHEN retrieving an analysis by comment
    analysis: Query = filter_analyses_by_comment(
        analyses=analysis_store.get_query(table=Analysis), comment="Does not exist."
    )

    # THEN no analysis is returned
    assert not analysis.first()


def test_filter_analyses_by_is_visible(analysis_store: MockStore):
    """Test return analysis when is visible is true."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # GIVEN a visible analysis
    existing_analysis.is_visible = True

    # WHEN retrieving analyses by is visible
    analyses: Query = filter_analyses_by_is_visible(
        analyses=analysis_store.get_query(table=Analysis)
    )

    # THEN the analyses is a query
    assert isinstance(analyses, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analyses.first()


def test_filter_analyses_by_is_visible_when_false(analysis_store: MockStore):
    """Test return analysis when is visible is false."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # GIVEN a hidden analysis
    existing_analysis.is_visible = False

    # WHEN retrieving analyses by is visible
    analyses: Query = filter_analyses_by_is_visible(
        analyses=analysis_store.get_query(table=Analysis)
    )

    # THEN the analyses is a query
    assert isinstance(analyses, Query)

    # THEN the existing analysis should not be returned
    for analysis in analyses:
        assert existing_analysis != analysis


def test_filter_analyses_by_search_term_in_comment(
    analysis_store: MockStore, analysis_comment: str
):
    """Test return analysis when search term matches comment."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # GIVEN a a comment
    existing_analysis.comment = analysis_comment

    # WHEN retrieving analyses by search term
    analyses: Query = filter_analyses_by_search_term(
        analyses=analysis_store.get_query(table=Analysis), search_term=analysis_comment
    )

    # THEN the analysis is a query
    assert isinstance(analyses, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analyses.first()


def test_filter_analyses_by_search_term_in_data_analysis(analysis_store: MockStore):
    """Test return analysis when search term matches data analysis."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving analyses by search term
    analyses: Query = filter_analyses_by_search_term(
        analyses=analysis_store.get_query(table=Analysis),
        search_term=existing_analysis.data_analysis,
    )

    # THEN the analysis is a query
    assert isinstance(analyses, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analyses.first()


def test_filter_analyses_by_search_term_in_case(analysis_store: MockStore):
    """Test return analysis when search term matches case."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving analyses by search term
    analyses: Query = filter_analyses_by_search_term(
        analyses=analysis_store.get_query(table=Analysis), search_term=existing_analysis.family
    )

    # THEN the analysis is a query
    assert isinstance(analyses, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analyses.first()


def test_filter_analyses_by_search_term_in_status(analysis_store: MockStore):
    """Test return analysis when search term matches status."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving analyses by search term
    analyses: Query = filter_analyses_by_search_term(
        analyses=analysis_store.get_query(table=Analysis), search_term=existing_analysis.status
    )

    # THEN the analyses is a query
    assert isinstance(analyses, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analyses.first()


def test_filter_analyses_by_search_term_when_not_matching(analysis_store: MockStore):
    """Test return analysis when search term does not match."""
    # GIVEN a store containing analyses
    analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving analyses by search term
    analyses: Query = filter_analyses_by_search_term(
        analyses=analysis_store.get_query(table=Analysis),
        search_term="does not exist",
    )
    # THEN the analyses is a query
    assert isinstance(analyses, Query)

    # THEN the no analysis is returned
    assert not analyses.first()


def test_filter_analyses_by_started_at(analysis_store: MockStore):
    """Test return analysis by started at when existing."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving an analysis by when it was started
    analysis: Query = filter_analyses_by_started_at(
        analyses=analysis_store.get_query(table=Analysis), started_at=existing_analysis.started_at
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()


def test_filter_analyses_by_before_started_at(analysis_store: MockStore, timestamp_now: datetime):
    """Test return analysis with a started at before supplied date when existing."""
    # GIVEN a store containing analyses

    # WHEN retrieving an analysis before supplied date
    analysis: Query = filter_analyses_by_before_started_at(
        analyses=analysis_store.get_query(table=Analysis), started_at=timestamp_now
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should return an analysis before than supplied date
    assert analysis.first().started_at < timestamp_now


def test_filter_analyses_by_before_started_at_when_after_supplied_date(
    analysis_store: MockStore, timestamp_old: datetime
):
    """Test return analysis with a started at after supplied date when existing."""
    # GIVEN a store containing analyses

    # WHEN retrieving an analysis by when it was started
    analysis: Query = filter_analyses_by_before_started_at(
        analyses=analysis_store.get_query(table=Analysis), started_at=timestamp_old
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN no analysis is returned
    assert not analysis.first()


def test_filter_analyses_by_status(analysis_store: MockStore):
    """Test return analysis by status when existing."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving an analysis by status
    analysis: Query = filter_analyses_by_status(
        analyses=analysis_store.get_query(table=Analysis), status=existing_analysis.status
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()


def test_filter_analyses_by_statuses(analysis_store: MockStore):
    """Test return analyses by statuses when existing."""
    # GIVEN a store containing analyses
    existing_analysis: Analysis = analysis_store.get_query(table=Analysis).first()

    # WHEN retrieving an analysis by status
    analysis: Query = filter_analyses_by_statuses(
        analyses=analysis_store.get_query(table=Analysis), statuses=[existing_analysis.status]
    )

    # THEN that the analysis is a query
    assert isinstance(analysis, Query)

    # THEN the analysis should match the original
    assert existing_analysis == analysis.first()
