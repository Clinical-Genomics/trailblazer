from datetime import datetime
import logging

from trailblazer.constants import TrailblazerStatus, WorkflowManager
from trailblazer.dto import CreateJobRequest, FailedJobsRequest, FailedJobsResponse, JobResponse
from trailblazer.exceptions import JobServiceError, NoJobsError
from trailblazer.services.job_service.mappers import (
    create_failed_jobs_response,
    create_job_response,
    slurm_info_to_job,
)
from trailblazer.services.job_service.utils import get_progress, get_slurm_job_ids, get_status
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
            updated_job: SlurmJobInfo = self.slurm_service.get_job(job.slurm_id)
            self.store.update_job(job_id=job.id, job_info=updated_job)

    def update_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        try:
            if analysis.workflow_manager == WorkflowManager.SLURM:
                self._update_slurm_jobs(analysis_id)
            if analysis.workflow_manager == WorkflowManager.TOWER:
                self.store.update_tower_run_status(analysis_id)
        except Exception as error:
            LOG.error(f"Failed to update jobs {analysis.case_id} - {analysis.id}: {error}")
            raise JobServiceError from error

    def _update_slurm_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        slurm_ids: list[int] = get_slurm_job_ids(analysis.config_path)
        slurm_jobs: list[SlurmJobInfo] = self.slurm_service.get_jobs(slurm_ids)
        jobs: list[Job] = [slurm_info_to_job(job_info) for job_info in slurm_jobs]
        self.store.replace_jobs(analysis_id=analysis_id, jobs=jobs)

    def get_analysis_status(self, analysis_id: int) -> TrailblazerStatus:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)

        if not analysis.jobs:
            raise NoJobsError(f"No jobs found for analysis {analysis_id}")

        return get_status(analysis.jobs)

    def get_analysis_progression(self, analysis_id: int) -> float:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        return get_progress(analysis.jobs)
