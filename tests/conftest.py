# -*- coding: utf-8 -*-
import pytest
import subprocess

from functools import partial
from click.testing import CliRunner
import ruamel.yaml

from trailblazer.cli import base
from trailblazer.store import Store


class MockStore(Store):
    @staticmethod
    def query_slurm(job_id_file: str, case_id: str) -> bytes:
        slurm_dict = {
            "blazinginsect": "tests/fixtures/sacct/blazinginsect_sacct",
            "crackpanda": "tests/fixtures/sacct/crackpanda_sacct",
            "escapegoat": "tests/fixtures/sacct/escapegoat_sacct",
            "lateraligator": "tests/fixtures/sacct/lateraligator_sacct",
            "nicemice": "tests/fixtures/sacct/nicemice_sacct",
        }
        return subprocess.check_output(["cat", slurm_dict.get(case_id)])


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, base)


@pytest.yield_fixture(scope="function")
def store():
    _store = MockStore(uri="sqlite://")
    _store.setup()
    yield _store
    _store.drop_all()


@pytest.yield_fixture(scope="function")
def sample_store(store):
    sample_data = ruamel.yaml.safe_load(open("tests/fixtures/sample-data.yaml"))
    for user_data in sample_data["users"]:
        store.add_user(user_data["name"], user_data["email"])
    for analysis_data in sample_data["analyses"]:
        analysis_data["case_id"] = analysis_data["family"]
        analysis_data["user"] = store.user(analysis_data["user"])
        failed_jobs = analysis_data.get("failed_jobs", [])
        analysis_data["failed_jobs"] = [store.Job(**job_data) for job_data in failed_jobs]
        store.add(store.Analysis(**analysis_data))
    store.commit()
    yield store
