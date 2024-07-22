"""Module for Tower Open API."""

import logging
import os
from pathlib import Path

import requests
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.clients.tower.models import (
    TowerProcess,
    TowerTask,
    TowerTaskResponse,
    TowerWorkflowResponse,
)
from trailblazer.constants import TOWER_WORKFLOW_STATUS, FileFormat, TrailblazerStatus
from trailblazer.exc import TowerRequirementsError, TrailblazerError
from trailblazer.io.controller import ReadFile

LOG = logging.getLogger(__name__)


class TowerApiClient:
    """A class handling requests and responses to and from the Tower Open APIs.
    Endpoints are defined in https://tower.nf/openapi/."""

    def __init__(self, workflow_id: str):
        self.workflow_id: str = workflow_id
        self.workspace_id: str = os.environ.get("TOWER_WORKSPACE_ID", None)
        self.tower_access_token: str = os.environ.get("TOWER_ACCESS_TOKEN", None)
        self.tower_api_endpoint: str = os.environ.get("TOWER_API_ENDPOINT", None)
        self.workflow_endpoint: str = f"workflow/{self.workflow_id}"
        self.tasks_endpoint: str = f"{self.workflow_endpoint}/tasks"
        self.cancel_endpoint: str = f"{self.workflow_endpoint}/cancel"

    @property
    def headers(self) -> dict:
        """Return headers required for an NF Tower API call.
        Accept and Authorization fields are mandatory."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.tower_access_token}",
        }

    @property
    def request_params(self) -> list[tuple]:
        """Return required parameters for an NF Tower API call.
        Workspace ID is mandatory."""
        return [
            ("workspaceId", self.workspace_id),
        ]

    def build_url(self, endpoint: str) -> str:
        """Build an url to query tower."""
        return self.tower_api_endpoint + endpoint

    def send_request(self, url: str) -> dict:
        """Sends a request to the server and returns the response. NF Tower API calls follow the next schema:
        curl -X GET "<URL>?workspaceId=<WORKSPACE_ID>" \
        -H "Accept: application/json"  \
        -H "Authorization: Bearer <TOWER_ACCESS_TOKEN>
        """
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=self.request_params,
                verify=True,
            )
            if response.status_code == 404:
                LOG.info("Request failed for url %s\n", url)
                response.raise_for_status()
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.info("Request failed for url %s: Error: %s\n", url, error)
            return {}

        return response.json()

    def post_request(self, url: str, data: dict = {}) -> None:
        """Send data via POST request and return response."""
        try:
            response = requests.post(
                url, headers=self.headers, params=self.request_params, json=data
            )
            if response.status_code in {404, 400}:
                LOG.info(f"POST request failed for url {url}\n with message {str(response)}")
                response.raise_for_status()
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.error(f"Request failed for url {url}: Error: {error}\n")
            raise TrailblazerError

    @property
    def meets_requirements(self) -> bool:
        """Return True if required variables are not empty."""
        requirement_map: list[tuple[str, str]] = [
            (self.tower_api_endpoint, "Error: no endpoint specified for Tower Open API request."),
            (
                self.tower_access_token,
                "Error: no access token specified for Tower Open API request.",
            ),
            (self.workspace_id, "Error: no workspace specified for Tower Open API request."),
        ]
        for requirement, error_msg in requirement_map:
            if not requirement:
                LOG.info(error_msg)
                return False
        return True

    @property
    def tasks(self) -> TowerTaskResponse:
        """Return a tasks response with information about submitted jobs."""
        if self.meets_requirements:
            url = self.build_url(endpoint=self.tasks_endpoint)
            return TowerTaskResponse(**self.send_request(url=url))

    @property
    def workflow(self) -> TowerWorkflowResponse:
        """Return a workflow response with general information about the analysis."""
        if self.meets_requirements:
            url = self.build_url(endpoint=self.workflow_endpoint)
            return TowerWorkflowResponse(**self.send_request(url=url))

    def send_cancel_request(self) -> None:
        """Send a POST request to cancel a workflow."""
        if self.meets_requirements:
            url: str = self.build_url(endpoint=self.cancel_endpoint)
            self.post_request(url=url)
