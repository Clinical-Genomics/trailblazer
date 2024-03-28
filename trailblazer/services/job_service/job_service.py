from datetime import datetime
import logging

from trailblazer.constants import TrailblazerStatus
from trailblazer.dto import CreateJobRequest, FailedJobsRequest, FailedJobsResponse, JobResponse
from trailblazer.services.job_service.mappers import (
    create_failed_jobs_response,
    create_job_response,
    slurm_info_to_job,
)
from trailblazer.services.job_service.utils import get_progression, get_slurm_job_ids, get_status
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store
from trailblazer.utils.datetime import get_date_number_of_days_ago

LOG = logging.getLogger(__name__)


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
            LOG.info(f"Updating upload job {job.id}")
            updated_job: SlurmJobInfo = self.slurm_service.get_job_info(job.slurm_id)
            self.store.update_job(job_id=job.id, job_info=updated_job)

    def update_analysis_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        self.store.delete_analysis_jobs(analysis_id)
        slurm_ids: list[int] = get_slurm_job_ids(analysis.config_path)
        jobs: list[Job] = []
        for slurm_id in slurm_ids:
            job_info: SlurmJobInfo = self.slurm_service.get_job_info(slurm_id)
            job: Job = slurm_info_to_job(job_info)
            jobs.append(job)
        self.store.add_jobs(analysis_id=analysis_id, jobs=jobs)

    def get_analysis_status(self, analysis_id: int) -> TrailblazerStatus:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        return get_status(analysis.jobs)

    def get_analysis_progression(self, analysis_id: int) -> float:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        return get_progression(analysis.jobs)
