from datetime import datetime
import logging

from trailblazer.constants import TrailblazerStatus, WorkflowManager
from trailblazer.dto import CreateJobRequest, FailedJobsRequest, FailedJobsResponse, JobResponse
from trailblazer.exceptions import JobServiceError, NoJobsError
from trailblazer.services.job_service.mappers import (
    create_failed_jobs_response,
    create_job_response,
)
from trailblazer.services.job_service.utils import (
    get_progress,
    get_status,
)
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store
from trailblazer.utils.datetime import get_date_number_of_days_ago

LOG = logging.getLogger(__name__)


class JobService:
    def __init__(self, store: Store, slurm_service: SlurmService, tower_service: TowerAPIService):
        self.store = store
        self.slurm_service = slurm_service
        self.tower_service = tower_service

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
                self.slurm_service.update_jobs(analysis_id)
            if analysis.workflow_manager == WorkflowManager.TOWER:
                self.tower_service.update_jobs(analysis_id)
        except Exception as error:
            LOG.error(f"Failed to update jobs {analysis.case_id} - {analysis.id}: {error}")
            raise JobServiceError from error

    def get_analysis_status(self, analysis_id: int) -> TrailblazerStatus:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)

        if analysis.status == TrailblazerStatus.CANCELLED:
            return TrailblazerStatus.CANCELLED

        if not analysis.jobs:
            raise NoJobsError(f"No jobs found for analysis {analysis_id}")

        if analysis.workflow_manager == WorkflowManager.TOWER:
            return self.tower_service.get_status(analysis_id)

        return get_status(analysis.jobs)

    def get_analysis_progression(self, analysis_id: int) -> float:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        return get_progress(analysis.jobs)

    def cancel_jobs(self, analysis_id: int) -> None:
        analysis: int = self.store.get_analysis_with_id(analysis_id)

        if analysis.workflow_manager == WorkflowManager.SLURM:
            self.slurm_service.cancel_jobs(analysis_id)
        if analysis.workflow_manager == WorkflowManager.TOWER:
            self.tower_service.cancel_jobs(analysis_id)
