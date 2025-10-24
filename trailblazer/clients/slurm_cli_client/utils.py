import subprocess

from trailblazer.clients.slurm_cli_client.models import SqueueResult
from trailblazer.constants import CharacterFormat, FileFormat
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadStream


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
    sacct_commands: list[str] = [
        "sacct",
        "--jobs",
        job_ids,
        "--format",
        "JobID%10,JobName%50,State%12,Timelimit%12,Elapsed%12,Submit%20",
        "--parsable2",
        "--delimiter=,",
        "--noheader",
    ]
    if analysis_host:
        sacct_commands = ["ssh", analysis_host] + sacct_commands
        output = (
            subprocess.check_output(
                sacct_commands,
                universal_newlines=True,
            )
            .decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8)
            .strip()
            .replace("//n", "/n")
        )
    else:
        output = (
            subprocess.check_output(sacct_commands)
            .decode(CharacterFormat.UNICODE_TRANSFORMATION_FORMAT_8)
            .strip()
        )

    squeue_headers = "JOBID,NAME,STATE,TIME_LIMIT,TIME,START_TIME"
    return squeue_headers + "\n" + output if output else squeue_headers


def get_squeue_result(squeue_response: str) -> SqueueResult:
    """Return SqueueResult object from squeue response.
    Raises:
        TrailblazerError: when no entries were returned by squeue command.
    """
    if not squeue_response or squeue_response.count("\n") <= 1:
        raise EmptySqueueError("No jobs found in SLURM registry")
    squeue_response_content: list[dict] = ReadStream.get_content_from_stream(
        file_format=FileFormat.CSV,
        stream=squeue_response,
        read_to_dict=True,
    )
    return SqueueResult(jobs=squeue_response_content)
