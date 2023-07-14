from typing import List

from trailblazer.apps.slurm.models import SqueueJob
from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadStream


def test_instantiate_squeue_job(squeue_stream: str):
    """
    Tests squeue output against a pydantic model
    """
    # GIVEN a csv squeue stream

    csv_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_stream,
        read_to_dict=True,
    )
    for job in csv_content:
        # WHEN instantiating a SqueueJob object
        squeue_job: SqueueJob = SqueueJob(**job)

        # THEN assert that it was successfully created
        assert isinstance(squeue_job, SqueueJob)
