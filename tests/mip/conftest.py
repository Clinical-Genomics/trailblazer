
import pytest

from trailblazer.mip import sacct


@pytest.fixture(scope='session')
def failed_sacct_jobs():
    with open('tests/fixtures/sacct/failed.log.status') as stream:
        sacct_jobs = sacct.parse_sacct(stream)
    return sacct_jobs
