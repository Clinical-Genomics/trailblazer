from datetime import datetime
from typing import List, Dict

from trailblazer.apps.slurm.models import SqueueJob, SqueueResult
from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadStream


def test_instantiate_squeue_job(squeue_stream_pending_job: str):
    """
    Tests squeue row output against a pydantic model
    """
    # GIVEN a csv squeue stream

    csv_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN it was successfully created
        assert isinstance(squeue_job, SqueueJob)


def test_squeue_job_convert_time_elapse(squeue_stream_jobs: str):
    """Tests SqueueJob convert time elapsed validator."""
    # GIVEN a csv squeue stream

    csv_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_jobs,
        read_to_dict=True,
    )
    expected_time_elapsed: Dict[int, int] = {
        0: 61,
        1: 1528,
        2: 5,
        3: 0,
        4: 0,
    }
    for index, job in enumerate(csv_content):
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN the time elapse should be in min
        assert squeue_job.time_elapsed == expected_time_elapsed[index]


def test_instantiate_squeue_result(squeue_stream_pending_job: str):
    """
    Tests squeue output against a pydantic model
    """
    # GIVEN a csv squeue stream

    csv_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )

    # WHEN instantiating a SqueueJob object
    squeue_result: SqueueResult = SqueueResult(jobs=csv_content)

    # THEN it should be successfully created
    assert isinstance(squeue_result, SqueueResult)


def test_convert_status_to_lower_case(squeue_stream_pending_job: str):
    """
    Tests converting status to lower case."""
    # GIVEN a csv squeue stream

    csv_content: List[dict] = ReadStream.get_content_from_stream(
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
    """
    Tests converting started to datetime."""
    # GIVEN a csv squeue stream

    csv_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream_pending_job,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN started is a datetime object
        assert isinstance(squeue_job.started, datetime)
