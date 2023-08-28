import datetime
from typing import List, Optional

import pytest

from tests.apps.tower.conftest import CaseName
from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.models import Analysis


def test_setup_db(store: MockStore):
    """Test store contains tables."""

    # GIVEN a store which is already setup

    # THEN it should contain tables
    assert store.engine.table_names()


def test_update_analysis_from_slurm_run_status(analysis_store: MockStore, squeue_stream_jobs: str):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.jobs

    # WHEN updating the analysis
    analysis_store.update_analysis_from_slurm_run_status(analysis_id=analysis.id)
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_name=analysis.family,
        started_at=analysis.started_at,
        status=TrailblazerStatus.RUNNING,
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.jobs


def test_set_analysis_uploaded(analysis_store: MockStore, timestamp_now: datetime, case_name):
    """Test setting analysis uploaded at for an analysis."""

    # GIVEN a store with an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_name=case_name)

    # WHEN setting an analysis uploaded at
    analysis_store.set_analysis_uploaded(case_id=analysis.family, uploaded_at=timestamp_now)

    # THEN the column uploaded_at should be updated
    assert analysis.uploaded_at == timestamp_now


def test_set_analysis_failed(analysis_store: MockStore, case_name: str):
    """Test setting analysis to failed for an analysis."""

    # GIVEN a store with an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_name=case_name)

    # WHEN setting analysis to failed
    analysis_store.set_analysis_status(case_id=analysis.family, status=TrailblazerStatus.FAILED)

    # THEN the analysis status should be updated to failed.
    assert analysis.status == TrailblazerStatus.FAILED


def test_add_comment(analysis_store: MockStore, case_name: str):
    """Test adding comment to an analysis object."""

    # GIVEN a store with an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_name=case_name)
    comment: str = "test comment"

    # WHEN adding a comment
    analysis_store.add_comment(case_id=analysis.family, comment=comment)

    # THEN a comment should have been added
    assert analysis.comment == comment


@pytest.mark.parametrize(
    "case_name, status",
    [
        ("blazinginsect", TrailblazerStatus.RUNNING),
        ("crackpanda", TrailblazerStatus.FAILED),
        ("daringpidgeon", TrailblazerStatus.ERROR),
        ("emptydinosaur", TrailblazerStatus.ERROR),
        ("escapedgoat", TrailblazerStatus.PENDING),
        ("fancymole", TrailblazerStatus.COMPLETED),
        ("happycow", TrailblazerStatus.PENDING),
        ("lateraligator", TrailblazerStatus.FAILED),
        ("liberatedunicorn", TrailblazerStatus.ERROR),
        ("nicemice", TrailblazerStatus.COMPLETED),
        ("rarekitten", TrailblazerStatus.CANCELLED),
        ("trueferret", TrailblazerStatus.RUNNING),
    ],
)
def test_update_run_status(analysis_store: MockStore, case_name: str, status: str):
    """Test updating an analysis status."""
    # GIVEN an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_name=case_name)

    # WHEN database is updated once
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is updated
    assert analysis.status == status

    # WHEN database is updated a second time
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is unchanged, and no database errors were raised
    assert analysis.status == status


def test_mark_analyses_deleted(analysis_store: MockStore, ongoing_analysis_case_name: str):
    """Test marking an ongoing analysis as deleted."""
    # GIVEN case name for a case that is not deleted
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(
        case_name=ongoing_analysis_case_name
    )
    assert not analysis.is_deleted

    # WHEN marking analysis as deleted
    analysis_store.mark_analyses_deleted(case_id=ongoing_analysis_case_name)
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(
        case_name=ongoing_analysis_case_name
    )

    # THEN analysis is marked deleted
    assert analysis.is_deleted


def test_update_tower_jobs(analysis_store: MockStore, tower_jobs: List[dict], case_name: str):
    """Assess that jobs are successfully updated when using NF Tower."""

    # GIVEN an analysis without failed jobs
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_name=case_name)
    assert not analysis.jobs

    # WHEN analysis jobs are deleted
    analysis_store.delete_analysis_jobs(analysis=analysis)

    # THEN analysis object should have no failed jobs
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN jobs should be updated
    assert len(analysis.jobs) == 2


@pytest.mark.parametrize(
    "case_name, status, progress",
    [
        (CaseName.RUNNING, TrailblazerStatus.RUNNING, 0.15),
        (CaseName.PENDING, TrailblazerStatus.PENDING, 0),
        (CaseName.COMPLETED, TrailblazerStatus.QC, 1),
    ],
)
def test_update_tower_run_status(
    analysis_store: MockStore, case_name: str, status: str, progress: int
):
    """Assess that an analysis status is successfully updated when using NF Tower."""

    # GIVEN an analysis with pending status
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_name=case_name)
    assert analysis.status == TrailblazerStatus.PENDING

    # WHEN database is updated once
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is updated
    assert analysis.status == status
    assert analysis.progress == progress

    # WHEN database is updated a second time
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is unchanged, and no database errors were raised
    assert analysis.status == status
    assert analysis.progress == progress
