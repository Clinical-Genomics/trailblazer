import pytest


@pytest.fixture(scope="session", name="squeue_stream_pending_job")
def fixture_squeue_stream_pending_job() -> str:
    """Return a squeue output stream."""
    return """id,step,status,time_limit,time_elapsed,started
690990,gatk_genotypegvcfs6,PENDING,10:00:00,0:00,2020-10-22T11:42:00"""


@pytest.fixture(scope="session", name="squeue_stream_completed_job")
def fixture_squeue_stream_completed_job() -> str:
    """Return a squeue output stream."""
    return """id,step,status,time_limit,time_elapsed,started
690994,gatk_genotypegvcfs2,COMPLETED,10:00:00,1:01:52,2020-10-22T11:43:33
702463,bwa_mem_ACC3218A1,COMPLETED,1-06:00:00,1-1:28:12,2020-10-27T23:06:34"""
