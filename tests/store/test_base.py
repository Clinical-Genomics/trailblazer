from datetime import datetime

from sqlalchemy.orm import Query

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus, Workflow
from trailblazer.store.models import Analysis, Info, Job


def test_info_query(info_store: MockStore):
    """Test base model table query."""

    # GIVEN a store

    # WHEN getting an object using the query
    info: Info = info_store.get_query(table=Info).first()

    # THEN it should return an Info object with a default "created_at" date
    assert isinstance(info.created_at, datetime)


def test_get_job_query_with_name_and_count_labels(job_store: MockStore):
    """Test Job query with labels and a count."""

    # GIVEN a job store

    # WHEN getting an object using the query
    category: Query = job_store.get_job_query_with_name_and_count_labels()

    # THEN it should return an Job object with a name and count
    assert isinstance(category, Query)

    # WHEN reading the database
    category = category.first()

    # THEN the returned object should have a name and count attribute
    assert category.name == "0"

    assert category.count == job_store.get_query(table=Job).count()


def test_get_analyses_query_by_search_term_and_is_visible(analysis_store: MockStore):
    """Test return analyses query by search term and is visible"""

    # GIVEN a store
    analyses_query: Query = analysis_store.get_query(table=Analysis)

    # WHEN getting an object using the query
    analyses: Query = analysis_store.get_analyses_query_by_search(
        search_term=TrailblazerStatus.PENDING, analyses=analyses_query
    )

    # THEN it should return a query
    assert isinstance(analyses, Query)

    # THEN it should return an object with the search term
    assert analyses.first().status == TrailblazerStatus.PENDING


def test_get_balsamic_analysis_filter(
    analysis_store: MockStore, mip_dna_case_id: str, balsamic_case_id: str, balsamic_qc_case_id: str
):
    """Tests that balsamic filtering included balsamic-qc and other related balsamic workflows."""

    # GIVEN a store

    # WHEN getting analyses filtered on balsamic
    analyses: list[Analysis] = analysis_store.get_analyses_query_by_workflow(
        Workflow.BALSAMIC.lower()
    ).all()

    # THEN the balsamic and balsamic-qc case should be included in the response
    analyses_case_ids: list[str] = [analysis.case_id for analysis in analyses]
    assert balsamic_case_id in analyses_case_ids and balsamic_qc_case_id in analyses_case_ids

    # THEN the MIP-DNA case should have been filtered out
    assert mip_dna_case_id not in analyses_case_ids
