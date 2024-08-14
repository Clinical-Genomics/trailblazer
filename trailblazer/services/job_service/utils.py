from pathlib import Path
from trailblazer.constants import FileFormat, JobType, SlurmJobStatus, TrailblazerStatus
from trailblazer.io.controller import ReadFile
from trailblazer.store.models import Analysis, Job


def get_tower_workflow_id(analysis: Analysis) -> str:
    file = Path(analysis.config_path)
    content: dict = ReadFile.get_content_from_file(file_format=FileFormat.YAML, file_path=file)
    return content.get(analysis.case_id)[-1]


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
    analysis_jobs: list[Job] = _get_analysis_jobs(jobs)
    completed_jobs: list[Job] = _get_completed_jobs(analysis_jobs)

    total_count: int = len(analysis_jobs)
    completed_count: int = len(completed_jobs)

    return 0.0 if total_count == 0 else completed_count / total_count


def _get_analysis_jobs(jobs: list[Job]) -> list[Job]:
    return [job for job in jobs if job.job_type == JobType.ANALYSIS]


def _get_completed_jobs(jobs: list[Job]) -> list[Job]:
    return [job for job in jobs if job.status == SlurmJobStatus.COMPLETED]
