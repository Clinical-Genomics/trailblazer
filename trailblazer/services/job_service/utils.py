from pathlib import Path
from trailblazer.constants import FileFormat, SlurmJobStatus, TrailblazerStatus
from trailblazer.io.controller import ReadFile
from trailblazer.store.models import Job


def get_slurm_job_ids(job_id_file: str) -> list[int]:
    job_id_file_path = Path(job_id_file)
    content: dict = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=job_id_file_path
    )
    job_ids: list[int] = []
    for row in content.values():
        [job_ids.append(job_id) for job_id in row]
    return job_ids


def get_status(jobs: list[Job]) -> TrailblazerStatus:
    is_running: bool = has_running_jobs(jobs)
    is_failed: bool = has_failed_jobs(jobs)
    if is_failed and is_running:
        return TrailblazerStatus.ERROR
    if is_failed:
        return TrailblazerStatus.FAILED
    if is_running:
        return TrailblazerStatus.RUNNING
    return TrailblazerStatus.CANCELLED


def has_running_jobs(jobs: list[Job]) -> bool:
    run_statuses = SlurmJobStatus.ongoing_statuses()
    return any(job.status in run_statuses for job in jobs)


def has_failed_jobs(jobs: list[Job]) -> bool:
    fail_statuses = SlurmJobStatus.fail_statuses()
    return any(job.status in fail_statuses for job in jobs)


def get_progress(jobs: list[Job]) -> float:
    total_jobs: int = len(jobs)
    if total_jobs == 0:
        return 0.0
    completed_jobs: int = len([job for job in jobs if job.status == SlurmJobStatus.COMPLETED])
    return completed_jobs / total_jobs
