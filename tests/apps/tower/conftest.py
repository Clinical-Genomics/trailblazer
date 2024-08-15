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
