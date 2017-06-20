# -*- coding: utf-8 -*-
import pytest

from trailblazer.mip import sacct
from trailblazer.mip import start


@pytest.fixture(scope='session')
def failed_sacct_jobs():
    with open('tests/fixtures/sacct/failed.log.status') as stream:
        sacct_jobs = sacct.parse_sacct(stream)
    return sacct_jobs


@pytest.fixture(scope='session')
def mip_cli():
    _mip_cli = start.MipCli(script='test/fake_mip.pl')
    return _mip_cli
