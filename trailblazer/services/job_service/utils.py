from pathlib import Path
from trailblazer.constants import FileFormat
from trailblazer.io.controller import ReadFile


def get_slurm_job_ids(job_id_file: Path) -> list[int]:
    content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=job_id_file
    )
    job_ids: list[int] = []
    for row in content.values():
        [job_ids.append(job_id) for job_id in row]
    return job_ids
