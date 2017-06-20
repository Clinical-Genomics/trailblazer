# -*- coding: utf-8 -*-
from functools import partial

from click.testing import CliRunner
import pytest
import ruamel.yaml

from trailblazer.cli import base
from trailblazer.mip import sacct, files as files_api
from trailblazer.log import LogAnalysis
from trailblazer.store import Store


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, base)


@pytest.fixture(scope='session')
def files():
    return {
        'config': 'tests/fixtures/family/family_config.yaml',
        'sampleinfo': 'tests/fixtures/family/family_qc_sample_info.yaml',
        'qcmetrics': 'tests/fixtures/family/family_qc_metrics.yaml',
        'sacct': 'tests/fixtures/family/mip.pl_2017-06-17T12:11:42.log.status',
    }


@pytest.fixture(scope='session')
def files_raw(files):
    return {
        'config': ruamel.yaml.safe_load(open(files['config'])),
        'sampleinfo': ruamel.yaml.safe_load(open(files['sampleinfo'])),
        'qcmetrics': ruamel.yaml.safe_load(open(files['qcmetrics'])),
        'sacct': list(open(files['sacct'])),
    }


@pytest.fixture(scope='session')
def files_data(files_raw):
    return {
        'config': files_api.parse_config(files_raw['config']),
        'sampleinfo': files_api.parse_sampleinfo(files_raw['sampleinfo']),
        'qcmetrics': files_api.parse_qcmetrics(files_raw['qcmetrics']),
        'sacct': sacct.parse_sacct(files_raw['sacct']),
    }


@pytest.yield_fixture(scope='function')
def store():
    _store = Store(uri='sqlite://')
    _store.setup()
    yield _store
    _store.drop_all()


@pytest.fixture
def log_analysis(store):
    _log_analysis = LogAnalysis(store)
    return _log_analysis
