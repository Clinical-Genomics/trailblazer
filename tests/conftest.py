# -*- coding: utf-8 -*-
import pytest

from functools import partial
from click.testing import CliRunner
import ruamel.yaml

from trailblazer.cli import base
from trailblazer.store import Store


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, base)


@pytest.yield_fixture(scope="function")
def store():
    _store = Store(uri="sqlite://")
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
