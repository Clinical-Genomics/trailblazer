# -*- coding: utf-8 -*-
import datetime as dt
import subprocess
from functools import partial
from json import JSONDecodeError
from pathlib import Path
from typing import Any, List

import pytest
import ruamel.yaml
from click.testing import CliRunner

from trailblazer.cli import base
from trailblazer.constants import TOWER_TIMESPAM_FORMAT
from trailblazer.io.json import read_json
from trailblazer.store import Store
from trailblazer.store.utils.executors import TowerAPI
from trailblazer.store.utils.tower import TowerTask


class MockStore(Store):
    """Instance of TrailblazerAPI that mimics expected SLURM output"""

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str, ssh: bool) -> bytes:
        slurm_dict = {
            "blazinginsect": "tests/fixtures/sacct/blazinginsect_sacct",  # running
            "crackpanda": "tests/fixtures/sacct/crackpanda_sacct",  # failed
            "daringpidgeon": "tests/fixtures/sacct/daringpidgeon_sacct",  # failed
            "emptydinosaur": "tests/fixtures/sacct/emptydinosaur_sacct",  # failed
            "escapedgoat": "tests/fixtures/sacct/escapegoat_sacct",  # pending
            "fancymole": "tests/fixtures/sacct/fancymole_sacct",  # completed
            "happycow": "tests/fixtures/sacct/happycow_sacct",  # pending
            "lateraligator": "tests/fixtures/sacct/lateraligator_sacct",  # failed
            "liberatedunicorn": "tests/fixtures/sacct/liberatedunicorn_sacct",  # error
            "nicemice": "tests/fixtures/sacct/nicemice_sacct",  # completed
            "rarekitten": "tests/fixtures/sacct/rarekitten_sacct",  # canceled
            "trueferret": "tests/fixtures/sacct/trueferret_sacct",  # running
        }
        return subprocess.check_output(["cat", slurm_dict.get(case_id)])

    @staticmethod
    def cancel_slurm_job(slurm_id: int, ssh: bool = False) -> None:
        return

    @staticmethod
    def query_tower(config_file: str, case_id: str) -> TowerAPI:
        """Return a mocked tower api."""
        configs = {
            "cuddlyhen": {
                "workflow_response_file": TowerResponseFile.RUNNING,
                "tasks_response_file": TowerTaskResponseFile.RUNNING,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
            "cuddlyhen_pending": {
                "workflow_response_file": TowerResponseFile.PENDING,
                "tasks_response_file": TowerTaskResponseFile.PENDING,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
            "cuddlyhen_completed": {
                "workflow_response_file": TowerResponseFile.COMPLETED,
                "tasks_response_file": TowerTaskResponseFile.COMPLETED,
                "tower_id": TOWER_ID,
                "analysis_id": 1,
            },
        }
        case = configs.get(case_id)
        tower_api = MockTowerAPI(executor_id=case.get("tower_id"))
        tower_api.mock_query(response_file=case.get("workflow_response_file"))
        tower_api.mock_tasks_query(response_file=case.get("tasks_response_file"))
        return tower_api


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, base)


@pytest.yield_fixture(scope="function")
def store():
    """Empty Trailblazer database"""
    _store = MockStore(uri="sqlite://")
    _store.setup()
    yield _store
    _store.drop_all()


@pytest.yield_fixture(scope="function")
def sample_store(store):
    """A sample Trailblazer database populated with pending analyses"""
    sample_data = ruamel.yaml.safe_load(open("tests/fixtures/sample-data.yaml"))
    for user_data in sample_data["users"]:
        store.add_user(user_data["name"], user_data["email"])
    for analysis_data in sample_data["analyses"]:
        analysis_data["case_id"] = analysis_data["family"]
        analysis_data["user"] = store.user(analysis_data["user"])
        store.add(store.Analysis(**analysis_data))
    store.commit()
    yield store


@pytest.fixture(scope="function")
def trailblazer_context(sample_store):
    """Trailblazer context to be used in CLI"""
    return {"trailblazer": sample_store}


@pytest.fixture(name="timestamp_now")
def fixture_timestamp_now() -> dt.datetime:
    """Return a time stamp of today's date in date time format."""
    return dt.datetime.now()


TOWER_RESPONSE_DIR = Path("tests", "fixtures", "tower")
TOWER_ID = "1m759EPcbjuK7n"

JOB_LIST_PENDING = [
    dict(
        analysis_id=1,
        slurm_id="4611827",
        name="NFCORE_RNAFUSION:RNAFUSION:INPUT_CHECK:SAMPLESHEET_CHECK",
        started_at=dt.datetime.strptime("2023-04-04T08:11:27Z", TOWER_TIMESPAM_FORMAT),
        elapsed=63,
        status="completed",
    ),
    dict(
        analysis_id=1,
        slurm_id="4611829",
        name="NFCORE_RNAFUSION:RNAFUSION:PIZZLY_WORKFLOW:KALLISTO_QUANT",
        started_at=None,
        elapsed=0,
        status="pending",
    ),
    dict(
        analysis_id=1,
        slurm_id="4611828",
        name="NFCORE_RNAFUSION:RNAFUSION:FASTQC",
        started_at=None,
        elapsed=0,
        status="pending",
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


class MockTowerAPI(TowerAPI):
    """Instance of TowerAPI that mimics expected Tower output."""

    @property
    def response(self) -> dict:
        return self.mock_response or None

    @property
    def tasks_response(self) -> dict:
        return self.mock_tasks_response or None

    def mock_query(self, response_file: Path) -> Any:
        try:
            self.mock_response = read_json(response_file)
        except JSONDecodeError:
            self.mock_response = {}
        return self.mock_response

    def mock_tasks_query(self, response_file: Path) -> Any:
        try:
            self.mock_tasks_response = read_json(response_file)
        except JSONDecodeError:
            self.mock_tasks_response = {}
        return self.mock_tasks_response


@pytest.fixture(name="tower_id")
def fixture_tower_id() -> str:
    """Return a tower id."""
    return TOWER_ID


@pytest.fixture(name="tower_config_file")
def fixture_tower_config_file() -> str:
    """Return the path of a config yaml file with a tower id."""
    return Path("tests", "fixtures", "case", "cuddlyhen_tower_id.yaml").as_posix()


@pytest.fixture(name="tower_task")
def fixture_tower_task() -> TowerTask:
    """Return a Tower Task."""
    return TowerTask(task=read_json(TowerTaskResponseFile.RUNNING)["tasks"][0]["task"])


@pytest.fixture(name="tower_empty_task")
def fixture_tower_empty_task() -> TowerTask:
    """Return an empty Tower Task."""
    return TowerTask(task=read_json(TowerTaskResponseFile.EMPTY))


@pytest.fixture(name="analysis_id")
def fixture_analysis_id() -> str:
    """Return an analysis id."""
    return 1


@pytest.fixture(name="jobs_list")
def fixture_jobs_list() -> List[dict]:
    """Return a list of Tower Jobs."""
    return JOB_LIST_PENDING


@pytest.fixture(name="tower_case_id")
def fixture_tower_case_id() -> str:
    """Return a tower case ID."""
    return "cuddlyhen"
