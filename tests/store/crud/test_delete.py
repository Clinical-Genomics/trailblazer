import pytest

from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.exc import MissingAnalysis, TrailblazerError
from trailblazer.store.models import Analysis


def test_delete_analysis_jobs(analysis_store: MockStore, tower_jobs: list[dict], case_id: str):
    """Test jobs are successfully deleted."""

    # GIVEN an analysis without failed jobs
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    assert analysis.jobs

    # WHEN jobs are deleted
    analysis_store.delete_analysis_jobs(analysis=analysis)

    # THEN analysis object should have no jobs
    assert not analysis.jobs


def test_delete_analysis(analysis_store: MockStore, case_id: str):
    """Test analysis is successfully deleted."""

    # GIVEN a not ongoing analysis
    analysis_store.update_analysis_status(case_id=case_id, status=TrailblazerStatus.CANCELLED)
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN deleting analysis
    analysis_store.delete_analysis(analysis_id=analysis.id)

    # THEN analysis object should be deleted
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert not analysis


def test_delete_analysis_with_force(analysis_store: MockStore, case_id: str):
    """Test analysis is successfully deleted when deleting an ongoing analysis."""

    # GIVEN an ongoing analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status in TrailblazerStatus.ongoing_statuses()

    # WHEN deleting analysis
    analysis_store.delete_analysis(analysis_id=analysis.id, force=True)

    # THEN analysis object should be deleted
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert not analysis


def test_delete_analysis_with_non_existing_analysis(
    analysis_store: MockStore, analysis_id_does_not_exist: str
):
    """Test analysis is successfully deleted when missing analysis."""

    # GIVEN a non-existing analysis

    # WHEN deleting analysis
    with pytest.raises(MissingAnalysis):
        analysis_store.delete_analysis(analysis_id=analysis_id_does_not_exist)

    # THEN error should be raised


def test_delete_analysis_with_ongoing_analysis_no_force(analysis_store: MockStore, case_id: str):
    """Test analysis is not deleted when deleting an ongoing analysis without force."""

    # GIVEN an ongoing analysis
    analysis: Analysis | None = analysis_store.get_latest_analysis_for_case(case_id=case_id)
    assert analysis.status in TrailblazerStatus.ongoing_statuses()

    # WHEN deleting analysis
    with pytest.raises(TrailblazerError):
        analysis_store.delete_analysis(analysis_id=analysis.id)

    # THEN error should be raised
