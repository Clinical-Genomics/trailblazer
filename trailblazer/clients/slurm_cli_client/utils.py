import subprocess

from trailblazer.constants import CharacterFormat, FileFormat
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadStream
from trailblazer.clients.slurm_cli_client.models import SqueueResult


def cancel_slurm_job(slurm_id: int, analysis_host: str | None = None) -> None:
    """Cancel SLURM job by SLURM job id."""
    scancel_commands: list[str] = ["scancel", str(slurm_id)]
    if analysis_host:
        scancel_commands = ["ssh", analysis_host] + scancel_commands
    subprocess.Popen(scancel_commands)


def get_slurm_queue(job_ids: list[int], analysis_host: str | None = None) -> SqueueResult:
    """Return squeue output from ongoing analyses in SLURM."""
    job_ids: str = ",".join(map(str, job_ids))
    queue_output: str = get_slurm_queue_output(job_ids=job_ids, analysis_host=analysis_host)
    return get_squeue_result(queue_output)


def get_slurm_queue_output(job_ids: str, analysis_host: str | None = None) -> str:
    """Return squeue output from ongoing analyses in SLURM."""
    squeue_commands: list[str] = [
        "squeue",
        "--jobs",
        job_ids,
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
