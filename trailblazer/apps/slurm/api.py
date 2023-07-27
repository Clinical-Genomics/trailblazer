from typing import List, Dict, Optional, Callable

from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import FileFormat, SlurmJobStatus, TrailblazerStatus
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadStream
from trailblazer.apps.slurm.utils import formatters


def get_squeue_result(squeue_response: str) -> SqueueResult:
    """Return SqueueResult object from squeue response.
    Raises:
        TrailblazerError: when no entries were returned by squeue command.
    """
    if not squeue_response:
        raise EmptySqueueError("No jobs found in SLURM registry")
    squeue_response_content: List[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_response,
        read_to_dict=True,
    )
    return SqueueResult(jobs=squeue_response_content)


def reformat_squeue_result_job_step(data_analysis: str, job_step: str) -> str:
    """Standardise job step string according to data analysis."""
    formatter: Callable = formatters.formatter_map.get(data_analysis, formatters.reformat_undefined)
    return formatter(job_step=job_step)


def get_current_analysis_status(jobs_status_distribution: dict) -> Optional[str]:
    """Return current analysis status based on jobs status distribution."""
    is_ongoing: bool = bool(
        jobs_status_distribution.get(SlurmJobStatus.RUNNING)
        or jobs_status_distribution.get(SlurmJobStatus.PENDING)
    )

    analysis_status_map: Dict[str, Optional[str]] = {
        SlurmJobStatus.FAILED: TrailblazerStatus.ERROR if is_ongoing else TrailblazerStatus.FAILED,
        SlurmJobStatus.TIME_OUT: TrailblazerStatus.ERROR
        if is_ongoing
        else TrailblazerStatus.FAILED,
        SlurmJobStatus.COMPLETED: TrailblazerStatus.COMPLETED
        if jobs_status_distribution.get(SlurmJobStatus.COMPLETED) == 1
        else None,
        SlurmJobStatus.PENDING: TrailblazerStatus.PENDING
        if jobs_status_distribution.get(SlurmJobStatus.PENDING) == 1
        else None,
        SlurmJobStatus.RUNNING: TrailblazerStatus.RUNNING,
        SlurmJobStatus.CANCELLED: None if is_ongoing else TrailblazerStatus.CANCELLED,
    }

    for status in [
        SlurmJobStatus.FAILED,
        SlurmJobStatus.TIME_OUT,
        SlurmJobStatus.COMPLETED,
        SlurmJobStatus.PENDING,
        SlurmJobStatus.RUNNING,
        SlurmJobStatus.CANCELLED,
    ]:
        if status in jobs_status_distribution and analysis_status_map[status]:
            return analysis_status_map[status]
