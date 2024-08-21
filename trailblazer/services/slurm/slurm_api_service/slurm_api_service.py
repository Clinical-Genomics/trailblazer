from trailblazer.clients.slurm_api_client.dto.job_response import SlurmJobResponse
from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmAPIClient
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_api_service.mappers import create_job
from trailblazer.services.slurm.slurm_api_service.utils import create_job_info_dto
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.services.slurm.utils import get_slurm_job_ids
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store


class SlurmAPIService(SlurmService):
    def __init__(self, client: SlurmAPIClient, store: Store):
        self.client = client
        self.store = store

    def get_job(self, job_id: int) -> SlurmJobInfo:
        job_response: SlurmJobResponse = self.client.get_job(job_id)
        return create_job_info_dto(job_response)

    def update_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        job_ids: list[int] = get_slurm_job_ids(analysis.config_path)

        dtos: list[SlurmJobInfo] = []
        for job_id in job_ids:
            if job := self.get_job(job_id):
                dtos.append(job)

        jobs: list[Job] = [create_job(dto) for dto in dtos]
        self.store.replace_jobs(analysis_id=analysis_id, jobs=jobs)

    def cancel_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        jobs: list[Job] = analysis.jobs

        for job in jobs:
            self.client.cancel_job(job.slurm_id)
        self.update_jobs(analysis_id)
