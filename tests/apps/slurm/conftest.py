import pytest


@pytest.fixture(scope="session")
def squeue_stream_pending_job() -> str:
    """Return a squeue output stream."""
    return """690990,gatk_genotypegvcfs6,PENDING,10:00:00,00:00:00,2020-10-22T11:42:00"""


@pytest.fixture(scope="session")
def squeue_stream_pending_job_not_started() -> str:
    """Return a squeue output stream for a not started job."""
    return """690990,gatk_genotypegvcfs6,PENDING,10:00:00,00:00:00,2020-10-22T11:42:00"""
