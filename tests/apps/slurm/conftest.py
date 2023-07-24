import pytest


@pytest.fixture(scope="session", name="squeue_stream_pending_job")
def fixture_squeue_stream_pending_job() -> bytes:
    """Return a squeue output stream."""
    return """JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME
690990,gatk_genotypegvcfs6,PENDING,10:00:00,0:00,2020-10-22T11:42:00""".encode(
        "utf-8"
    )


@pytest.fixture(scope="session", name="squeue_stream_pending_job_not_started")
def fixture_squeue_stream_pending_job_not_started() -> bytes:
    """Return a squeue output stream for a noot started job."""
    return """JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME
690990,gatk_genotypegvcfs6,PENDING,10:00:00,0:00,N/A""".encode(
        "utf-8"
    )
