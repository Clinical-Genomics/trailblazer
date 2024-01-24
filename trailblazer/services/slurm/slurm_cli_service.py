from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmCLIService(SlurmService):
    def __init__(self, client: SlurmCLIClient):
        self.client = client

    def cancel_job(self, job_id: str) -> None:
        self.client.cancel_job(job_id)
