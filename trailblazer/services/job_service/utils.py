from trailblazer.dto.failed_jobs_response import FailedJobsResponse
from trailblazer.dto.job_response import JobResponse
from trailblazer.store.models import Job


def create_job_response(job: Job) -> JobResponse:
    return JobResponse(
        slurm_id=job.slurm_id, analysis_id=job.analysis_id, status=job.status, id=job.id
    )


def create_failed_jobs_response(failed_job_statistics: list[dict]) -> FailedJobsResponse:
    return FailedJobsResponse(jobs=failed_job_statistics)
