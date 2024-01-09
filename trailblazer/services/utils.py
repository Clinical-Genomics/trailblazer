from trailblazer.dto.failed_jobs_response import FailedJobsResponse
from trailblazer.store.models import Job


def create_jobs_response(failed_job_statistics: list[dict]) -> FailedJobsResponse:
    return FailedJobsResponse(jobs=failed_job_statistics)
