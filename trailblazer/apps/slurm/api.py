from typing import List

from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import FileFormat
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadStream


def get_squeue_result(squeue_response: str) -> SqueueResult:
    """Return SqueueResult object from squeue response.
    Raises:
        TrailblazerError: when no entries were returned by squeue command"""
    if not squeue_response:
        raise EmptySqueueError("No jobs found in SLURM registry")
    squeue_response_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_response,
        read_to_dict=True,
    )
    return SqueueResult(jobs=squeue_response_content)
