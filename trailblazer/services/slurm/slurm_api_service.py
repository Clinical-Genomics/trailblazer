from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmApiClient
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmAPIService(SlurmService):
    def __init__(self, slurm_client: SlurmApiClient):
        self.slurm_client = slurm_client

    def cancel_job(self, job_id: str) -> None:
        self.slurm_client.cancel_job(job_id)
    
    