from datetime import datetime

from trailblazer.apps.slurm.models import SqueueJob, SqueueResult
from trailblazer.constants import FileFormat, SlurmJobStatus
from trailblazer.io.controller import ReadStream

LONG_RUNNING_JOB: int = 1528
MEDIUM_RUNNING_JOOB: int = 61
SHORT_RUNNING_JOB: int = 5


def test_instantiate_squeue_result(squeue_stream_pending_job: str):
    """Tests squeue output against a pydantic model."""
    # GIVEN a csv squeue stream

    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )

    # WHEN instantiating a SqueueJob object
    squeue_result: SqueueResult = SqueueResult(jobs=csv_content)

    # THEN it should be successfully created
    assert isinstance(squeue_result, SqueueResult)


def test_instantiate_squeue_job(squeue_stream_pending_job: str):
    """Tests squeue row output against a pydantic model."""
    # GIVEN a csv squeue stream

    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN it was successfully created
        assert isinstance(squeue_job, SqueueJob)


def test_squeue_job_convert_time_elapse_to_minutes(squeue_stream_jobs: str):
    """Tests SqueueJob convert time elapsed to minutes validator."""
    # GIVEN a csv squeue stream

    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_jobs,
        read_to_dict=True,
    )
    expected_time_elapsed: dict[int, int] = {
        0: MEDIUM_RUNNING_JOOB,
        1: LONG_RUNNING_JOB,
        2: SHORT_RUNNING_JOB,
        3: 0,
        4: 0,
    }
    for index, job in enumerate(csv_content):
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN the time elapsed should be in min
        assert squeue_job.time_elapsed == expected_time_elapsed[index]


def test_convert_status_to_lower_case(squeue_stream_pending_job: str):
    """Tests converting status to lower case."""
    # GIVEN a csv squeue stream

    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN status is in lower case
        assert squeue_job.status.islower()


def test_convert_started_to_datetime(squeue_stream_pending_job: str):
    """Tests converting started to datetime."""
    # GIVEN a csv squeue stream

    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN started at is a datetime object
        assert isinstance(squeue_job.started_at, datetime)


def test_convert_started_to_datetime_no_datetime_format(squeue_stream_pending_job_not_started: str):
    """Tests converting started to datetime when started is not in datetime format."""
    # GIVEN a csv squeue stream

    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job_not_started,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN started at is not initialized
        assert not squeue_job.started_at


def test_set_jobs_status_distribution(squeue_stream_pending_job: str):
    """Tests set job status distribution from jobs status."""
    # GIVEN a csv squeue stream
    csv_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )

    # WHEN instantiating a SqueueResult object
    squeue_result: SqueueResult = SqueueResult(jobs=csv_content)

    # THEN a job status distribution should be returned
    assert squeue_result.jobs_status_distribution == {SlurmJobStatus.PENDING: 1}
