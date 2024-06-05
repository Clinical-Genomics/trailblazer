import logging
import requests

from trailblazer.clients.slurm_api_client.dto import (
    SlurmJobResponse,
    SlurmJobsResponse,
)
from trailblazer.exc import SlurmAPIClientError


LOG = logging.getLogger(__name__)

class SlurmAPIClient:
    def __init__(self, base_url: str, access_token: str, user_name: str) -> None:
        self.base_url = base_url
        self.headers = {"X-SLURM-USER-NAME": user_name, "X-SLURM-USER-TOKEN": access_token}

    def get_job(self, job_id: str) -> SlurmJobResponse:
        LOG.info(f"Getting job {job_id}")
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/job/{job_id}"
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            LOG.error(f"Error getting job {job_id}: {e.response.text}")
            LOG.error(f"Response: {response.content}")
            raise SlurmAPIClientError(e)
        LOG.debug(f"Response: {response.json()}")
        return SlurmJobResponse.model_validate(response.json())

    def get_jobs(self) -> SlurmJobsResponse:
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/jobs"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmJobsResponse.model_validate(response.json())
