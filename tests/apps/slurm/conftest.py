import pytest


@pytest.fixture(scope="session", name="squeue_stream_pending_job")
def fixture_squeue_stream_pending_job() -> str:
    """Return a squeue output stream."""
    return """id,step,status,time_limit,time_elapsed,started
690990,gatk_genotypegvcfs6,PENDING,10:00:00,0:00,2020-10-22T11:42:00"""
