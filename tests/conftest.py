# -*- coding: utf-8 -*-
import pytest
import subprocess

from functools import partial
from click.testing import CliRunner
import ruamel.yaml

from trailblazer.cli import base
from trailblazer.store import Store


class MockStore(Store):
    """Instance of TrailblazerAPI that mimics expected SLURM output"""

    @staticmethod
    def query_slurm(job_id_file: str, case_id: str) -> bytes:
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
    def cancel_slurm_job(slurm_id: int) -> None:
        return


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
        store.add(store.Analysis(**analysis_data))
    store.commit()
    yield store


@pytest.fixture()
def trailblazer_context(sample_store):
    return {"trailblazer": sample_store}
