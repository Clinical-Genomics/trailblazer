import pytest


@pytest.fixture(scope="session")
def squeue_stream_pending_job() -> str:
    """Return a squeue output stream."""
    return """JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME
690990,gatk_genotypegvcfs6,PENDING,10:00:00,0:00,2020-10-22T11:42:00"""


@pytest.fixture(scope="session")
def squeue_stream_pending_job_not_started() -> str:
    """Return a squeue output stream for a ot started job."""
    return """JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME
690990,gatk_genotypegvcfs6,PENDING,10:00:00,0:00,N/A"""
