from trailblazer.services.slurm.api_service.slurm_api_client.slurm_api_client import SlurmAPIClient


class SlurmAPIService:
    def __init__(self, slurm_client: SlurmAPIClient) -> None:
        self.slurm_client = slurm_client
