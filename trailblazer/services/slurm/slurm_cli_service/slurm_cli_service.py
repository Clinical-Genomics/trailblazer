from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.services.slurm.dtos import JobDto
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmCLIService(SlurmService):
    def __init__(self, client: SlurmCLIClient):
        self.client = client

    def get_job(self, job_id: str) -> JobDto:
        return self.client.get_job(job_id)
