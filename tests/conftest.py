# -*- coding: utf-8 -*-
import datetime as dt
import subprocess
from functools import partial
from pathlib import Path
from typing import Any

import pytest
import ruamel.yaml
from click.testing import CliRunner
from ruamel.yaml import safe_load

from trailblazer.cli import base
from trailblazer.io.json import read_json
from trailblazer.store import Store
from trailblazer.store.executors import TowerAPI


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


class MockTowerAPI(TowerAPI):
    """Instance of TowerAPI that mimics expected Tower output."""

    @property
    def response(self) -> dict:
        return self.mock_response or None

    def mock_query(self, response_file: Path) -> Any:
        self.mock_response = read_json(response_file)
        return self.mock_response


@pytest.fixture(name="tower_config_file")
def fixture_tower_config_file() -> str:
    """Return the path of a config yaml file with a tower id."""
    return Path("tests", "fixtures", "case", "cuddlyhen_tower_id.yaml").as_posix()


class TowerResponseFile:
    PENDING: str = Path("tests", "fixtures", "tower", "cuddlyhen_workflow_pending").as_posix()
    RUNNING: str = Path("tests", "fixtures", "tower", "cuddlyhen_workflow_running").as_posix()
    COMPLETED: str = Path("tests", "fixtures", "tower", "cuddlyhen_workflow_completed").as_posix()
