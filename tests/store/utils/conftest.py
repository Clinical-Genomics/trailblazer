import datetime as dt
from pathlib import Path
from typing import List

import pytest

from trailblazer.constants import TOWER_TIMESPAM_FORMAT, TrailblazerStatus
from trailblazer.io.json import read_json
from trailblazer.store.utils.tower import TowerTask

TOWER_RESPONSE_DIR: Path = Path("tests", "fixtures", "tower")
TOWER_ID: str = "1m759EPcbjuK7n"
JOB_LIST_PENDING: List[dict] = [
    dict(
        analysis_id=1,
        slurm_id="4611827",
        name="NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK",
        started_at=dt.datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESPAM_FORMAT),
        elapsed=63,
        status=TrailblazerStatus.COMPLETED.value,
    ),
    dict(
        analysis_id=1,
        slurm_id="4611829",
        name="NFCORE_RNAFUSION:RNAFUSION:PIZZLY_WORKFLOW:KALLISTO_QUANT",
        started_at=None,
        elapsed=0,
        status=TrailblazerStatus.PENDING.value,
    ),
    dict(
        analysis_id=1,
        slurm_id="4611828",
        name="NFCORE_RNAFUSION:RNAFUSION:FASTQC",
        started_at=None,
        elapsed=0,
        status=TrailblazerStatus.PENDING.value,
    ),
]


class TowerResponseFile:
    PENDING: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_workflow_pending")
    RUNNING: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_workflow_running")
    COMPLETED: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_workflow_completed")
    EMPTY: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_workflow_empty")


class TowerTaskResponseFile:
    PENDING: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_tasks_pending")
    RUNNING: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_tasks_running")
    COMPLETED: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_tasks_completed")
    EMPTY: Path = Path(TOWER_RESPONSE_DIR, "cuddlyhen_tasks_empty")


@pytest.fixture(name="tower_id")
def fixture_tower_id() -> str:
    """Return a NF Tower id."""
    return TOWER_ID


@pytest.fixture(name="tower_config_file")
def fixture_tower_config_file() -> str:
    """Return the path of a config yaml file with a NF Tower id."""
    return Path("tests", "../fixtures", "case", "cuddlyhen_tower_id.yaml").as_posix()


@pytest.fixture(name="tower_task")
def fixture_tower_task() -> TowerTask:
    """Return a NF Tower task."""
    return TowerTask(task=read_json(TowerTaskResponseFile.RUNNING)["tasks"][0]["task"])


@pytest.fixture(name="tower_empty_task")
def fixture_tower_empty_task() -> TowerTask:
    """Return an empty NF Tower task."""
    return TowerTask(task=read_json(TowerTaskResponseFile.EMPTY))


@pytest.fixture(name="analysis_id")
def fixture_analysis_id() -> int:
    """Return an analysis id."""
    return 1
