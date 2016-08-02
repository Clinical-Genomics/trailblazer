# -*- coding: utf-8 -*-
from functools import partial

from alchy import Manager
from click.testing import CliRunner
from path import path
import pytest

from housekeeper.cli import root
from housekeeper.store import Model, get_manager
from housekeeper.initiate import setup


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def invoke_cli(cli_runner):
    return partial(cli_runner.invoke, root)


@pytest.fixture
def pedigree():
    return dict(
        checksum='13c366da11437d46e66dfe33cd8cb884d9c1488e',
        path='tests/fixtures/mip/cust003/16074/genomes/16074/16074_pedigree.txt'
    )


@pytest.yield_fixture(scope='function')
def mip_output():
    mip_out = path('tests/fixtures/mip')
    yield mip_out
    mod_qcmetrics = mip_out.joinpath("cust003/16074/analysis/genomes/16074/"
                                     "16074_qcmetrics.mod.yaml")
    mod_qcmetrics.remove_p()


@pytest.yield_fixture(scope='function')
def manager():
    config = dict(SQLALCHEMY_DATABASE_URI='sqlite://')
    _manager = Manager(config=config, Model=Model)
    _manager.create_all()
    yield _manager
    _manager.drop_all()


@pytest.yield_fixture(scope='function')
def setup_tmp(tmpdir):
    tmp_path = path(tmpdir)
    tmp_path.joinpath('analyses').makedirs_p()
    db_path = tmp_path.joinpath('store.sqlite3')
    uri = "sqlite:///{}".format(db_path)
    manager = get_manager(uri)
    setup(tmp_path, uri=uri)
    data = dict(uri=uri, path=str(db_path), manager=manager)
    yield data
    manager.drop_all()
