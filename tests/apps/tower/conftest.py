import datetime as dt
from pathlib import Path

import pytest

from trailblazer.constants import TOWER_TIMESTAMP_FORMAT

TOWER_RESPONSE_DIR: Path = Path("tests", "fixtures", "tower")
TOWER_ID: str = "1m759EPcbjuK7n"


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


class CaseIDs:
    PENDING: str = "cuddlyhen_pending"
    RUNNING: str = "cuddlyhen"
    COMPLETED: str = "cuddlyhen_completed"


@pytest.fixture(name="tower_id")
def fixture_tower_id() -> str:
    """Return a NF Tower id."""
    return TOWER_ID


@pytest.fixture(name="tower_config_file")
def fixture_tower_config_file() -> str:
    """Return the path of a config yaml file with a NF Tower id."""
    return Path("tests", "fixtures", "case", "cuddlyhen_tower_id.yaml").as_posix()


@pytest.fixture(name="tower_task_response_pending")
def fixture_tower_task_response_pending() -> Path:
    """Return an NF Tower task response for a pending case."""
    return TowerTaskResponseFile.PENDING


@pytest.fixture(name="tower_task_response_running")
def fixture_tower_task_response_running() -> Path:
    """Return an NF Tower task response for a running case."""
    return TowerTaskResponseFile.RUNNING


@pytest.fixture(name="created_at")
def fixture_created_at() -> dt.datetime:
    """Returns a created at date."""
    return dt.datetime.strptime("2023-04-04T08:11:24Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="last_updated")
def fixture_last_updated() -> dt.datetime:
    """Returns a last updated date."""
    return dt.datetime.strptime("2023-04-04T08:11:28Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture(name="tower_task_duration")
def fixture_tower_task_duration() -> int:
    """Returns the duration of a NF Tower task."""
    return 3798
