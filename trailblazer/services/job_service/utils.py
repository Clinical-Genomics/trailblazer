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
        [job_ids.append(int(job_id)) for job_id in row]
    return job_ids


def get_status(jobs: list[Job]) -> TrailblazerStatus:
    if has_same_status(jobs):
        return get_single_status(jobs)
    is_running: bool = is_analysis_ongoing(jobs)
    is_failed: bool = is_analysis_failed(jobs)

    if is_failed and is_running:
        return TrailblazerStatus.ERROR

    if is_failed and not is_running:
        return TrailblazerStatus.FAILED

    if is_running:
        return TrailblazerStatus.RUNNING

    return TrailblazerStatus.CANCELLED


def has_same_status(jobs: list[Job]) -> bool:
    if not jobs:
        return False
    first_status = jobs[0].status
    return all(job.status == first_status for job in jobs)


def get_single_status(jobs: list[Job]) -> SlurmJobStatus:
    single_status: str = jobs[0].status
    return (
        TrailblazerStatus.FAILED
        if single_status == SlurmJobStatus.TIME_OUT
        else TrailblazerStatus[single_status.upper()]
    )


def is_analysis_ongoing(jobs: list[Job]) -> bool:
    run_statuses = SlurmJobStatus.ongoing_statuses()
    return any(job.status in run_statuses for job in jobs)


def is_analysis_failed(jobs: list[Job]) -> bool:
    fail_statuses = SlurmJobStatus.fail_statuses()
    return any(job.status in fail_statuses for job in jobs)


def get_progress(jobs: list[Job]) -> float:
    total_jobs: int = len(jobs)
    if total_jobs == 0:
        return 0.0
    completed_jobs: int = len([job for job in jobs if job.status == SlurmJobStatus.COMPLETED])
    return completed_jobs / total_jobs
