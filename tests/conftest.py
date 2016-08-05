# -*- coding: utf-8 -*-
from functools import partial

from alchy import Manager
from click.testing import CliRunner
import pytest

from analysis.cli import root
from analysis.store import Model


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, root)


@pytest.fixture
def cust_root():
    return {
        'path': 'tests/fixtures/mip/cust001',
        'cases': ['famCompleted', 'famStarted'],
    }


@pytest.fixture
def analysis_started():
    """Return info about analysis which has only just started."""
    return {
        'root': ("tests/fixtures/mip/cust001/famStarted/analysis/genomes/"
                 "famStarted"),
        'family_id': 'famStarted',
    }


@pytest.fixture
def analysis_failed():
    """Return info about analysis which has only just started."""
    return {
        'root': ("tests/fixtures/mip/cust003/famErrored/analysis/exomes/"
                 "famErrored"),
        'family_id': 'famErrored',
    }


@pytest.fixture
def analysis_multi():
    """Return info about analysis which has been started twice."""
    return {
        'root': ("tests/fixtures/mip-shell/cust002/famMulti/analysis/"
                 "genomes/famMulti"),
        'family_id': 'famMulti',
        'latest_sacct': 'Sacct_famMulti.1.stdout.txt',
    }


@pytest.yield_fixture(scope='function')
def sacct_failed(analysis_failed):
    filename = "Sacct_{}.0.stdout.txt".format(analysis_failed['family_id'])
    path = "{}/bwa/info/{}".format(analysis_failed['root'], filename)
    with open(path, 'r') as stream:
        yield stream


@pytest.yield_fixture(scope='function')
def manager():
    config = dict(SQLALCHEMY_DATABASE_URI='sqlite://')
    _manager = Manager(config=config, Model=Model)
    _manager.create_all()
    yield _manager
    _manager.drop_all()
