import requests

from trailblazer.clients.slurm_api_client.dto import (
    SlurmCancelJobResponse,
    SlurmJobResponse,
    SlurmJobsResponse,
)


class SlurmApiClient:
    def __init__(self, base_url: str, access_token: str, user_name: str) -> None:
        self.base_url = base_url
        self.headers = {"X-SLURM-USER-NAME": user_name, "X-SLURM-USER-TOKEN": access_token}

    def get_job(self, job_id: str) -> SlurmJobResponse:
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/job/{job_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmJobResponse.model_validate(response.json())

    def get_jobs(self) -> SlurmJobsResponse:
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/jobs"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmJobsResponse.model_validate(response.json())

    def cancel_job(self, job_id: str) -> SlurmCancelJobResponse:
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/job/{job_id}"
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmCancelJobResponse.model_validate(response.json())
