import requests

from trailblazer.clients.slurm_api_client.dto import (
    SlurmCancelJobResponse,
    SlurmJobInfoResponse,
    SlurmJobsInfoResponse,
)


class SlurmApiClient:
    def __init__(self, base_url: str, access_token: str, user_name: str) -> None:
        self.base_url = base_url
        self.headers = {"X-SLURM-USER-NAME": user_name, "X-SLURM-USER-TOKEN": access_token}

    def get_job(self, job_id: str) -> SlurmJobInfoResponse:
        endpoint: str = f"{self.base_url}/slurmV0040/job/{job_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmJobInfoResponse.model_validate(response.json())

    def get_jobs(self) -> SlurmJobsInfoResponse:
        endpoint: str = f"{self.base_url}/slurmV0040/jobs"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmJobsInfoResponse.model_validate(response.json())

    def cancel_job(self, job_id: str) -> SlurmCancelJobResponse:
        endpoint: str = f"{self.base_url}/slurmV0040/job/{job_id}"
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmCancelJobResponse.model_validate(response.json())
