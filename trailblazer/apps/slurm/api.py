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


def _get_analysis_single_status(jobs_status_distribution: Dict[str, float]) -> str:
    """Return true if only one status in jobs statuses."""
    if len(jobs_status_distribution) == 1:
        single_status: str = jobs_status_distribution.popitem()[0]
        return (
            TrailblazerStatus.FAILED
            if single_status == SlurmJobStatus.TIME_OUT
            else TrailblazerStatus[single_status.upper()]
        )


def _is_analysis_failed(jobs_status_distribution: Dict[str, float]) -> bool:
    """Return true if any job was broken."""
    broken_statuses: List[str] = [SlurmJobStatus.FAILED, SlurmJobStatus.TIME_OUT]
    for broken_status in broken_statuses:
        if jobs_status_distribution.get(broken_status):
            return True


def _is_analysis_ongoing(jobs_status_distribution: Dict[str, float]) -> bool:
    """Return True if analysis is still ongoing."""
    return bool(
        jobs_status_distribution.get(SlurmJobStatus.RUNNING)
        or jobs_status_distribution.get(SlurmJobStatus.PENDING)
    )


def get_current_analysis_status(jobs_status_distribution: Dict[str, float]) -> str:
    """Return current analysis status based on jobs status distribution."""
    single_analysis_status: Optional[str] = _get_analysis_single_status(
        jobs_status_distribution=jobs_status_distribution
    )
    if single_analysis_status:
        return single_analysis_status
    is_analysis_ongoing: bool = _is_analysis_ongoing(
        jobs_status_distribution=jobs_status_distribution
    )
    is_analysis_failed: bool = _is_analysis_failed(
        jobs_status_distribution=jobs_status_distribution
    )
    if is_analysis_failed:
        return TrailblazerStatus.ERROR if is_analysis_ongoing else TrailblazerStatus.FAILED
    if is_analysis_ongoing:
        return TrailblazerStatus.RUNNING
    return TrailblazerStatus.CANCELLED
