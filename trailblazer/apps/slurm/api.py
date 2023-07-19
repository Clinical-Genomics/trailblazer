from typing import List, Dict, Optional

from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import FileFormat, SlurmJobStatus, TrailblazerStatus
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadStream
from trailblazer.apps.slurm.utils import formatters


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


def reformat_squeue_result_job_step(data_analysis: str, job_step: str) -> str:
    """Standardise job step string according to data anlaysis."""
    formatter_func = formatters.formatter_map.get(data_analysis, formatters.reformat_undefined)
    return formatter_func(job_step=job_step)


def get_current_analysis_status(status_distribution: dict) -> Optional[str]:
    """Return current analysis status based on status distribution."""
    is_ongoing: bool = bool(
        status_distribution.get(SlurmJobStatus.RUNNING.value)
        or status_distribution.get(SlurmJobStatus.PENDING.value)
    )

    analysis_status_map: Dict[str, Optional[str]] = {
        SlurmJobStatus.FAILED.value: TrailblazerStatus.ERROR.value
        if is_ongoing
        else TrailblazerStatus.FAILED.value,
        SlurmJobStatus.TIME_OUT.value: TrailblazerStatus.ERROR.value
        if is_ongoing
        else TrailblazerStatus.FAILED.value,
        SlurmJobStatus.COMPLETED.value: TrailblazerStatus.COMPLETED.value
        if status_distribution.get(SlurmJobStatus.COMPLETED.value) == 1
        else None,
        SlurmJobStatus.PENDING.value: TrailblazerStatus.PENDING.value
        if status_distribution.get(SlurmJobStatus.PENDING.value) == 1
        else None,
        SlurmJobStatus.RUNNING.value: TrailblazerStatus.RUNNING.value,
        SlurmJobStatus.CANCELLED.value: None if is_ongoing else TrailblazerStatus.CANCELLED.value,
    }

    for status in [
        SlurmJobStatus.FAILED.value,
        SlurmJobStatus.TIME_OUT.value,
        SlurmJobStatus.COMPLETED.value,
        SlurmJobStatus.PENDING.value,
        SlurmJobStatus.RUNNING.value,
        SlurmJobStatus.CANCELLED.value,
    ]:
        if status in status_distribution and analysis_status_map[status]:
            return analysis_status_map[status]
