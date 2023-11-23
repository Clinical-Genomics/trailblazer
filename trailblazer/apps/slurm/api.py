import subprocess
from pathlib import Path
from typing import Callable

from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.apps.slurm.utils import formatters
from trailblazer.constants import (
    CharacterFormat,
    FileFormat,
    SlurmJobStatus,
    TrailblazerStatus,
)
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadFile, ReadStream


def _get_squeue_jobs_flag_input(slurm_job_id_file_content: dict[str, list[str]]) -> str:
    """Return a string of comma separated SLURM job ids to be used as input for squeue jobs flag."""
    job_ids: list[str] = []
    for slurm_job_ids in slurm_job_id_file_content.values():
        [job_ids.append(str(job_id)) for job_id in slurm_job_ids]
    return ",".join(job_ids)


def cancel_slurm_job(slurm_id: int, analysis_host: str | None = None) -> None:
    """Cancel SLURM job by SLURM job id."""
    scancel_commands: list[str] = ["scancel", str(slurm_id)]
    if analysis_host:
        scancel_commands = ["ssh", analysis_host] + scancel_commands
    subprocess.Popen(scancel_commands)


def get_slurm_squeue_output(slurm_job_id_file: Path, analysis_host: str | None = None) -> str:
    """Return squeue output from ongoing analyses in SLURM."""
    slurm_job_id_file_content: dict[str, list[str]] = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=slurm_job_id_file
    )
    slurm_jobs: str = _get_squeue_jobs_flag_input(
        slurm_job_id_file_content=slurm_job_id_file_content
    )
    squeue_commands: list[str] = [
        "squeue",
        "--jobs",
        slurm_jobs,
        "--states=all",
        "--format",
        "%A,%j,%T,%l,%M,%S",
    ]
    if analysis_host:
        squeue_commands = ["ssh", analysis_host] + squeue_commands
        return (
            subprocess.check_output(
                squeue_commands,
                universal_newlines=True,
            )
            .decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8)
            .strip()
            .replace("//n", "/n")
        )
    return subprocess.check_output(squeue_commands).decode(
        CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8
    )


def get_squeue_result(squeue_response: str) -> SqueueResult:
    """Return SqueueResult object from squeue response.
    Raises:
        TrailblazerError: when no entries were returned by squeue command.
    """
    if not squeue_response:
        raise EmptySqueueError("No jobs found in SLURM registry")
    squeue_response_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_response,
        read_to_dict=True,
    )
    return SqueueResult(jobs=squeue_response_content)


def reformat_squeue_result_job_step(data_analysis: str, job_step: str) -> str:
    """Standardise job step string according to data analysis."""
    formatter: Callable = formatters.formatter_map.get(data_analysis, formatters.reformat_undefined)
    return formatter(job_step=job_step)


def _get_analysis_single_status(jobs_status_distribution: dict[str, float]) -> str:
    """Return true if only one status in jobs statuses."""
    if len(jobs_status_distribution) == 1:
        single_status: str = jobs_status_distribution.popitem()[0]
        return (
            TrailblazerStatus.FAILED
            if single_status == SlurmJobStatus.TIME_OUT
            else TrailblazerStatus[single_status.upper()]
        )


def _is_analysis_failed(jobs_status_distribution: dict[str, float]) -> bool:
    """Return true if any job was broken."""
    return any(
        broken_status in jobs_status_distribution
        for broken_status in [SlurmJobStatus.FAILED, SlurmJobStatus.TIME_OUT]
    )


def _is_analysis_ongoing(jobs_status_distribution: dict[str, float]) -> bool:
    """Return True if analysis is still ongoing."""
    return any(
        ongoing_status in jobs_status_distribution
        for ongoing_status in TrailblazerStatus.ongoing_statuses()
    )


def get_current_analysis_status(jobs_status_distribution: dict[str, float]) -> str:
    """Return current analysis status based on jobs status distribution."""
    single_analysis_status: str | None = _get_analysis_single_status(
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
