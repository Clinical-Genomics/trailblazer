from pathlib import Path

import pytest

from trailblazer.io.json import read_json
from trailblazer.store.utils.tower import TowerTask

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


@pytest.fixture(name="tower_task")
def fixture_tower_task() -> TowerTask:
    """Return a NF Tower task."""
    return TowerTask(**read_json(TowerTaskResponseFile.RUNNING)["tasks"][0]["task"])


@pytest.fixture(name="tower_task_response_pending")
def fixture_tower_task_response_pending() -> Path:
    """Return an NF Tower task response for a pending case."""
    return TowerTaskResponseFile.PENDING


@pytest.fixture(name="tower_task_response_running")
def fixture_tower_task_response_running() -> Path:
    """Return an NF Tower task response for a running case."""
    return TowerTaskResponseFile.RUNNING


# @pytest.fixture(name="tower_empty_task")
# def fixture_tower_empty_task() -> TowerTask:
#     """Return an empty NF Tower task."""
#     return TowerTask(task=read_json(TowerTaskResponseFile.EMPTY))
