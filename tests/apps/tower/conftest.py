import datetime as dt
from pathlib import Path

import pytest

from trailblazer.constants import TOWER_TIMESTAMP_FORMAT

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


class CaseIDs:
    PENDING: str = "cuddlyhen_pending"
    RUNNING: str = "cuddlyhen"
    COMPLETED: str = "cuddlyhen_completed"


@pytest.fixture(name="tower_id", scope="session")
def fixture_tower_id() -> str:
    """Return a NF Tower id."""
    return TOWER_ID


@pytest.fixture(name="tower_config_file", scope="session")
def fixture_tower_config_file() -> str:
    """Return the path of a config yaml file with a NF Tower id."""
    return Path("tests", "fixtures", "case", "cuddlyhen_tower_id.yaml").as_posix()


@pytest.fixture(name="tower_task_response_pending", scope="session")
def fixture_tower_task_response_pending() -> Path:
    """Return an NF Tower task response for a pending case."""
    return TowerTaskResponseFile.PENDING


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
    return 4
