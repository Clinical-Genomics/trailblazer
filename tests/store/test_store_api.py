import subprocess
from typing import Dict, List, Optional

import pytest

from tests.apps.tower.conftest import CaseId
from tests.mocks.store_mock import MockStore
from trailblazer.constants import CharacterFormat, TrailblazerStatus
from trailblazer.store.models import Analysis

FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH: str = "trailblazer.store.crud.update.get_slurm_squeue_output"


def test_setup_db(store: MockStore):
    """Test store contains tables."""

    # GIVEN a store which is already setup

    # THEN it should contain tables
    assert store.engine.table_names()


def test_update_analysis_from_slurm_run_status(
    analysis_store: MockStore,
    squeue_stream_jobs: str,
    mocker,
    ongoing_analysis_case_id: str,
    slurm_squeue_output: Dict[str, str],
):
    """Test updating analysis jobs when given squeue results."""
    # GIVEN an analysis and a squeue stream
    analysis: Analysis = analysis_store.get_query(table=Analysis).first()
    assert not analysis.jobs

    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(
            ["cat", slurm_squeue_output.get(ongoing_analysis_case_id)]
        ).decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8),
    )

    # WHEN updating the analysis
    analysis_store.update_analysis_from_slurm_output(
        analysis_id=analysis.id, analysis_host="a_host"
    )
    updated_analysis: Analysis = analysis_store.get_analysis(
        case_id=analysis.family, started_at=analysis.started_at, status=TrailblazerStatus.RUNNING
    )

    # THEN it should update the analysis jobs
    assert updated_analysis.jobs


@pytest.mark.parametrize(
    "case_id, status",
    [
        ("blazinginsect", TrailblazerStatus.RUNNING),
        ("crackpanda", TrailblazerStatus.FAILED),
        ("daringpidgeon", TrailblazerStatus.ERROR),
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
def test_update_run_status(
    analysis_store: MockStore,
    case_id: str,
    status: str,
    mocker,
    slurm_squeue_output: Dict[str, str],
):
    """Test updating an analysis status."""
    # GIVEN SLURM squeue output for an analysis
    mocker.patch(
        FUNC_GET_SLURM_SQUEUE_OUTPUT_PATH,
        return_value=subprocess.check_output(["cat", slurm_squeue_output.get(case_id)]).decode(
            CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8
        ),
    )

    # GIVEN an analysis
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_id=case_id)

    # WHEN database is updated once
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN analysis status is updated
    assert analysis.status == status

    # WHEN database is updated a second time
    analysis_store.update_run_status(analysis_id=analysis.id)

    # THEN the status is unchanged, and no database errors were raised
    assert analysis.status == status


def test_update_tower_jobs(analysis_store: MockStore, tower_jobs: List[dict], case_id: str):
    """Assess that jobs are successfully updated when using NF Tower."""

    # GIVEN an analysis without failed jobs
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_id=case_id)
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
    "case_id, status, progress",
    [
        (CaseId.RUNNING, TrailblazerStatus.RUNNING, 0.15),
        (CaseId.PENDING, TrailblazerStatus.PENDING, 0),
        (CaseId.COMPLETED, TrailblazerStatus.QC, 1),
    ],
)
def test_update_tower_run_status(
    analysis_store: MockStore, case_id: str, status: str, progress: int
):
    """Assess that an analysis status is successfully updated when using NF Tower."""

    # GIVEN an analysis with pending status
    analysis: Optional[Analysis] = analysis_store.get_latest_analysis_for_case(case_id=case_id)
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
