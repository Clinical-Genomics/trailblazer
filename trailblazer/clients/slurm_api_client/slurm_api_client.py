import logging
from pydantic import ValidationError
import requests

from trailblazer.clients.slurm_api_client.dto import SlurmJobResponse
from trailblazer.clients.slurm_api_client.error_handler import handle_errors
from trailblazer.exc import ResponseDeserializationError, SlurmAPIClientError


LOG = logging.getLogger(__name__)


class SlurmAPIClient:
    def __init__(self, base_url: str, access_token: str, user_name: str) -> None:
        self.base_url = base_url
        self.headers = {"X-SLURM-USER-NAME": user_name, "X-SLURM-USER-TOKEN": access_token}

    @handle_errors
    def get_job(self, job_id: str) -> SlurmJobResponse:
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/job/{job_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return SlurmJobResponse.model_validate(response.json())

    @handle_errors
    def cancel_job(self, job_id: str) -> None:
        endpoint: str = f"{self.base_url}/slurm/v0.0.40/job/{job_id}"
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()
