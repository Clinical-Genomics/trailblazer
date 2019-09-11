# -*- coding: utf-8 -*-
import pytest

from trailblazer.pipeline import sacct
from trailblazer.pipeline import start


@pytest.fixture(scope='session')
def failed_sacct_jobs():
    with open('tests/fixtures/sacct/failed.log.status') as stream:
        sacct_jobs = sacct.parse_sacct(stream)
    return sacct_jobs


@pytest.fixture(scope='session')
def mip_cli():
    _mip_cli = start.PipelineCli(script='test/fake_mip.pl', pipeline='rd_dna')
    return _mip_cli
