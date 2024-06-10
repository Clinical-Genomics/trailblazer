from trailblazer.clients.slurm_api_client.dto.job_response import SlurmJobResponse
from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmAPIClient
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_api_service.utils import create_job_info_dto
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmAPIService(SlurmService):
    def __init__(self, client: SlurmAPIClient):
        self.client = client

    def get_job(self, job_id: int) -> SlurmJobInfo:
        job_response: SlurmJobResponse = self.client.get_job(job_id)
        return create_job_info_dto(job_response)

    def get_jobs(self, job_ids: list[int]) -> list[SlurmJobInfo]:
        jobs: list[SlurmJobInfo] = []
        for job_id in job_ids:
            job: SlurmJobInfo | None = self.get_job(job_id)
            if job:
                jobs.append(job)
        return jobs
