from datetime import datetime

from trailblazer.constants import TrailblazerStatus
from trailblazer.dto import FailedJobsRequest, FailedJobsResponse
from trailblazer.dto.create_job_request import CreateJobRequest
from trailblazer.dto.job_response import JobResponse
from trailblazer.services.utils import create_job_response, create_jobs_response
from trailblazer.store.models import Job
from trailblazer.store.store import Store
from trailblazer.utils.datetime import get_date_number_of_days_ago


class JobService:
    def __init__(self, store: Store):
        self.store = store

    def get_failed_jobs(self, request: FailedJobsRequest) -> FailedJobsResponse:
        time_window: datetime = get_date_number_of_days_ago(request.days_back)
        failed_jobs: list[dict] = self.store.get_nr_jobs_with_status_per_category(
            status=TrailblazerStatus.FAILED, since_when=time_window
        )
        return create_jobs_response(failed_jobs)

    def add_job(self, analysis_id: int, data: CreateJobRequest) -> JobResponse:
        job: Job = self.store.add_job(analysis_id=analysis_id, job_request=data)
        return create_job_response(job)
