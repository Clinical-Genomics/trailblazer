import requests

from trailblazer.clients.job_info_response import JobInfoResponse


class SlurmRestApiClient:
    def __init__(self, base_url: str, access_token: str, user_name: str) -> None:
        self.base_url = base_url
        self.headers = {"X-SLURM-USER-NAME": user_name, "X-SLURM-USER-TOKEN": access_token}

    def get_job_info(self, job_id: str) -> JobInfoResponse:
        endpoint: str = f"{self.base_url}/slurmV0040GetJob/{job_id}"
        response = requests.get(endpoint, headers=self.headers)
        return JobInfoResponse.model_validate(response.json())
