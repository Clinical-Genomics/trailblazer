# -*- coding: utf-8 -*-
import datetime as dt
from functools import partial
from pathlib import Path
from typing import List

import pytest
import ruamel.yaml
from click.testing import CliRunner

from tests.mocks.store_mock import MockStore
from trailblazer.cli import base
from trailblazer.constants import TOWER_TIMESPAM_FORMAT
from trailblazer.io.json import read_json
from trailblazer.store.utils.tower import TowerTask


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
def fixture_analysis_id() -> int:
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
