import datetime
import subprocess
from pathlib import Path
from typing import Dict, List

import pytest

from tests.apps.tower.conftest import CaseIDs
from tests.mocks.store_mock import MockStore
from trailblazer.constants import TrailblazerStatus
from trailblazer.store.models import Analysis


def test_setup_db(store: MockStore):
    """Test store contains tables."""

    # GIVEN a store which is already setup

    # THEN it should contain tables
    assert store.engine.table_names()


def test_update_analysis_from_slurm_run_status(
    analysis_store: MockStore,
    squeue_stream_jobs: str,
    mocker,
    ongoing_analysis_case_name: str,
    slurm_squeue_output: Dict[str, Path],
):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.jobs

    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        "trailblazer.store.crud.update.get_slurm_squeue_output",
        return_value=subprocess.check_output(
            ["cat", slurm_squeue_output.get(ongoing_analysis_case_name)]
        ).decode("utf-8"),
    )

    # WHEN updating the analysis
    analysis_store.update_analysis_from_slurm_run_status(analysis_id=analysis.id)
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_name=analysis.family,
        started_at=analysis.started_at,
        status=TrailblazerStatus.RUNNING,
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.jobs


def test_set_analysis_uploaded(analysis_store: MockStore, timestamp_now: datetime):
    """Test setting analysis uploaded at for an analysis."""

    # GIVEN a store with an analysis
    analysis_obj: Analysis = analysis_store.analyses().first()
    uploaded_at: datetime = timestamp_now

    # WHEN setting an analysis uploaded at
    analysis_store.set_analysis_uploaded(case_id=analysis_obj.family, uploaded_at=uploaded_at)

    # THEN the column uploaded_at should be updated
    assert analysis_obj.uploaded_at == uploaded_at


def test_set_analysis_failed(analysis_store: MockStore):
    """Test setting analysis to failed for an analysis."""

    # GIVEN a store with an analysis
    analysis_obj: Analysis = analysis_store.analyses().first()

    # WHEN setting analysis to failed
    analysis_store.set_analysis_status(case_id=analysis_obj.family, status="failed")

    # THEN the column status should be updated with failed.
    assert analysis_obj.status == "failed"


def test_add_comment(analysis_store: MockStore):
    """Test adding comment to an analysis object."""

    # GIVEN a store with an analysis
    analysis_obj: Analysis = analysis_store.analyses().first()
    comment: str = "test comment"

    # WHEN adding a comment
    analysis_store.add_comment(case_id=analysis_obj.family, comment=comment)

    # THEN a comment should have been added
    assert analysis_obj.comment == comment


@pytest.mark.parametrize(
    "case_id, status",
    [
        ("blazinginsect", "running"),
        ("crackpanda", "failed"),
        ("daringpidgeon", "error"),
        ("escapedgoat", "pending"),
        ("fancymole", "completed"),
        ("happycow", "pending"),
        ("lateraligator", "failed"),
        ("liberatedunicorn", "error"),
        ("nicemice", "completed"),
        ("rarekitten", "canceled"),
        ("trueferret", "running"),
    ],
)
def test_update(
    analysis_store: MockStore, case_id, status, mocker, slurm_squeue_output: Dict[str, Path]
):
    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        "trailblazer.store.crud.update.get_slurm_squeue_output",
        return_value=subprocess.check_output(["cat", slurm_squeue_output.get(case_id)]).decode(
            "utf-8"
        ),
    )

    # GIVEN an analysis
    analysis_obj = analysis_store.get_latest_analysis(case_id)

    # WHEN database is updated once
    analysis_store.update_run_status(analysis_obj.id)

    # THEN analysis status is changed to what is expected
    assert analysis_obj.status == status

    # WHEN database is updated a second time
    analysis_store.update_run_status(analysis_obj.id)

    # THEN the status is still what is expected, and no database errors were raised
    assert analysis_obj.status == status


def test_mark_analyses_deleted(analysis_store: MockStore):
    # GIVEN case_id for a case that is not deleted
    case_id = "liberatedunicorn"
    analysis_obj = analysis_store.get_latest_analysis(case_id)
    assert not analysis_obj.is_deleted

    # WHEN running command
    analysis_store.mark_analyses_deleted(case_id=case_id)
    analysis_obj = analysis_store.get_latest_analysis(case_id)

    # THEN analysis is marked deleted
    assert analysis_obj.is_deleted


def test_update_tower_jobs(analysis_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Assess that jobs are successfully updated when using NF Tower."""

    # GIVEN an analysis without failed jobs
    analysis: Analysis = analysis_store.get_latest_analysis(case_id=case_id)
    assert not analysis.jobs

    # WHEN analysis jobs are deleted
    analysis_store.delete_analysis_jobs(analysis=analysis)

    # THEN analysis object should have no failed jobs
    assert not analysis.jobs

    # WHEN jobs are updated
    analysis_store.update_analysis_jobs(analysis=analysis, jobs=tower_jobs[:2])

    # THEN failed jobs should be updated
    assert len(analysis.jobs) == 2


@pytest.mark.parametrize(
    "case_id, status, progress",
    [
        (CaseIDs.RUNNING, TrailblazerStatus.RUNNING, 0.15),
        (CaseIDs.PENDING, TrailblazerStatus.PENDING, 0),
        (CaseIDs.COMPLETED, TrailblazerStatus.QC, 1),
    ],
)
def test_update_tower_run_status(
    analysis_store: MockStore, case_id: str, status: str, progress: int
):
    """Assess that an analysis status is successfully updated when using NF Tower."""

    # GIVEN an analysis with pending status
    analysis: Analysis = analysis_store.get_latest_analysis(case_id=case_id)
    assert analysis.status == TrailblazerStatus.PENDING

    # WHEN database is updated once
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is changed to what is expected
    assert analysis.status == status
    assert analysis.progress == progress

    # WHEN database is updated a second time
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is still as before, and no database errors were raised
    assert analysis.status == status
    assert analysis.progress == progress
