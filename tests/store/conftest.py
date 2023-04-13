# -*- coding: utf-8 -*-
import datetime as dt
from typing import List

import pytest

from tests.store.utils.conftest import CaseIDs
from trailblazer.constants import TOWER_TIMESTAMP_FORMAT, TrailblazerStatus


@pytest.fixture(name="timestamp_now")
def fixture_timestamp_now() -> dt.datetime:
    """Return a time stamp of today's date in date time format."""
    return dt.datetime.now()


@pytest.fixture(name="analysis_id")
def fixture_analysis_id() -> int:
    """Return an analysis id."""
    return 1


@pytest.fixture(name="started_at")
def fixture_started_at() -> dt.datetime:
    """Returns a started at date."""
    return dt.datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="created_at")
def fixture_created_at() -> dt.datetime:
    """Returns a created at date."""
    return dt.datetime.strptime("2023-04-04T08:11:24Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="last_updated")
def fixture_last_updated() -> dt.datetime:
    """Returns a last updated date."""
    return dt.datetime.strptime("2023-04-04T08:11:28Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="duration")
def fixture_duration() -> int:
    """Returns the duration of a task."""
    return 3798


@pytest.fixture(name="slurm_id")
def fixture_slurm_id() -> str:
    """Returns a slurm id."""
    return "4611827"


@pytest.fixture(name="task_name")
def fixture_task_name() -> str:
    """Returns a task name."""
    return "NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK"


@pytest.fixture(name="jobs_list")
def fixture_jobs_list(analysis_id, started_at, slurm_id, task_name) -> List[dict]:
    """Return a list of Tower Jobs."""
    return [
        dict(
            analysis_id=analysis_id,
            slurm_id=slurm_id,
            name=task_name,
            started_at=started_at,
            elapsed=63,
            status=TrailblazerStatus.COMPLETED.value,
        ),
        dict(
            analysis_id=analysis_id,
            slurm_id="4611829",
            name="NFCORE_RNAFUSION:RNAFUSION:PIZZLY_WORKFLOW:KALLISTO_QUANT",
            started_at=None,
            elapsed=0,
            status=TrailblazerStatus.PENDING.value,
        ),
        dict(
            analysis_id=analysis_id,
            slurm_id="4611828",
            name="NFCORE_RNAFUSION:RNAFUSION:FASTQC",
            started_at=None,
            elapsed=0,
            status=TrailblazerStatus.PENDING.value,
        ),
    ]


@pytest.fixture(name="case_id")
def fixture_case_id() -> str:
    """Return a case ID."""
    return CaseIDs.RUNNING
