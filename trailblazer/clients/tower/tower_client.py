import logging
import requests
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.clients.tower.models import (
    TowerTaskResponse,
    TowerWorkflowResponse,
)
from trailblazer.exc import TrailblazerError

LOG = logging.getLogger(__name__)


class TowerApiClient:
    """A client consuming the Tower API. Endpoints are defined in https://tower.nf/openapi/."""

    def __init__(self, base_url: str, access_token: str, workspace_id: str):
        self.base_url = base_url
        self.access_token = access_token
        self.workspace_id = workspace_id

    @property
    def headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    @property
    def request_params(self) -> list[tuple]:
        return [("workspaceId", self.workspace_id)]

    def build_url(self, endpoint: str) -> str:
        return self.base_url + endpoint

    def send_request(self, url: str) -> dict:
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=self.request_params,
                verify=True,
            )
            if response.status_code == 404:
                LOG.error(f"Request failed for url {url}")
                response.raise_for_status()
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.error(f"Request failed for url {url}: Error: {error}")
            return {}

        return response.json()

    def post_request(self, url: str, data: dict = {}) -> None:
        """Send data via POST request and return response."""
        try:
            response = requests.post(
                url, headers=self.headers, params=self.request_params, json=data
            )
            if response.status_code in {404, 400}:
                LOG.error(f"POST request failed for url {url}\n with message {str(response)}")
                response.raise_for_status()
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.error(f"Request failed for url {url}: Error: {error}\n")
            raise TrailblazerError

    @property
    def tasks(self) -> TowerTaskResponse:
        """Return a tasks response with information about submitted jobs."""
        url = self.build_url(endpoint=self.tasks_endpoint)
        return TowerTaskResponse(**self.send_request(url=url))

    @property
    def workflow(self) -> TowerWorkflowResponse:
        """Return a workflow response with general information about the analysis."""
        url = self.build_url(endpoint=self.workflow_endpoint)
        return TowerWorkflowResponse(**self.send_request(url=url))

    def send_cancel_request(self) -> None:
        """Send a POST request to cancel a workflow."""
        url: str = self.build_url(endpoint=self.cancel_endpoint)
        self.post_request(url=url)
