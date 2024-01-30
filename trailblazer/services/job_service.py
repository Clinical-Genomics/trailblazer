from datetime import datetime

from trailblazer.dto import CreateJobRequest, FailedJobsRequest, FailedJobsResponse, JobResponse
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.services.utils import create_job_response, create_failed_jobs_response
from trailblazer.store.models import Job
from trailblazer.store.store import Store
from trailblazer.utils.datetime import get_date_number_of_days_ago


class JobService:
    def __init__(self, store: Store, slurm_service: SlurmService):
        self.store = store
        self.slurm_service = slurm_service

    def get_failed_jobs(self, request: FailedJobsRequest) -> FailedJobsResponse:
        time_window: datetime = get_date_number_of_days_ago(request.days_back)
        failed_jobs: list[dict] = self.store.get_failed_jobs_stats(time_window)
        return create_failed_jobs_response(failed_jobs)

    def add_job(self, analysis_id: int, data: CreateJobRequest) -> JobResponse:
        job: Job = self.store.add_job(analysis_id=analysis_id, job_request=data)
        return create_job_response(job)

    def update_upload_jobs(self) -> None:
        jobs: list[Job] = self.store.get_ongoing_upload_jobs()
        for job in jobs:
            updated_job: SlurmJobInfo = self.slurm_service.get_job_info(job.slurm_id)
            self.store.update_job(job_id=job.id, job_info=updated_job)
