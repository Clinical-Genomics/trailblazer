from pathlib import Path
import subprocess
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.constants import CharacterFormat, FileFormat
from trailblazer.exc import EmptySqueueError
from trailblazer.io.controller import ReadFile, ReadStream


def get_job_ids(job_ids_file: Path) -> str:
    job_ids_file_content: dict[str, list[str]] = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=job_ids_file
    )
    job_ids: list[str] = []
    for slurm_job_ids in job_ids_file_content.values():
        [job_ids.append(str(job_id)) for job_id in slurm_job_ids]
    return ",".join(job_ids)

def parse_slurm_queue(squeue_response: str) -> SqueueResult:
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


def get_slurm_squeue_output(job_ids, analysis_host: str | None = None) -> str:
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
