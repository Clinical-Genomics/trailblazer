import datetime as dt
from pathlib import Path

import pytest

from trailblazer.constants import (
    TOWER_TIMESTAMP_FORMAT,
    TOWER_TIMESTAMP_FORMAT_EXTENDED,
)

TOWER_RESPONSE_DIR: Path = Path("tests", "fixtures", "tower")
TOWER_ID: str = "1m759EPcbjuK7n"


class TowerResponseFile:
    PENDING: Path = Path(TOWER_RESPONSE_DIR, "tower_workflow_pending.json")
    RUNNING: Path = Path(TOWER_RESPONSE_DIR, "tower_workflow_running.json")
    COMPLETED: Path = Path(TOWER_RESPONSE_DIR, "tower_workflow_completed.json")
    EMPTY: Path = Path(TOWER_RESPONSE_DIR, "tower_workflow_empty.json")


class TowerTaskResponseFile:
    PENDING: Path = Path(TOWER_RESPONSE_DIR, "tower_tasks_pending.json")
    RUNNING: Path = Path(TOWER_RESPONSE_DIR, "tower_tasks_running.json")
    COMPLETED: Path = Path(TOWER_RESPONSE_DIR, "tower_tasks_completed.json")
    EMPTY: Path = Path(TOWER_RESPONSE_DIR, "tower_tasks_empty.json")


class CaseId:
    PENDING: str = "cuddlyhen_pending"
    RUNNING: str = "cuddlyhen"
    COMPLETED: str = "cuddlyhen_completed"


@pytest.fixture(scope="session")
def tower_config_file() -> str:
    """Return the path of a config yaml file with a NF Tower id."""
    return Path("tests", "fixtures", "case", "cuddlyhen_tower_id.yaml").as_posix()


@pytest.fixture(scope="session")
def tower_task_response_pending() -> Path:
    """Return an NF Tower task response for a pending case."""
    return TowerTaskResponseFile.PENDING


@pytest.fixture
def created_at() -> dt.datetime:
    """Returns a created at date."""
    return dt.datetime.strptime("2023-04-04T08:11:24Z", TOWER_TIMESTAMP_FORMAT)


@pytest.fixture
def last_updated() -> dt.datetime:
    """Returns a last updated date."""
    return dt.datetime.strptime("2023-06-20T08:01:57.661819Z", TOWER_TIMESTAMP_FORMAT_EXTENDED)


@pytest.fixture
def tower_task_duration() -> int:
    """Returns the duration of a NF Tower task."""
    return 4
