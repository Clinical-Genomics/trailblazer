"""Code for talking to tower Open API"""
import logging
import os
from typing import List, Tuple

import requests
from requests.exceptions import ConnectionError, HTTPError, MissingSchema

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
        self.headers: dict = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.tower_access_token,
        }
        self.params: List[Tuple] = [
            ("workspaceId", self.workspace_id),
        ]

    def build_url(self, endpoint: str) -> str:
        """Build an url to query tower."""
        return self.tower_api_endpoint + endpoint

    def send_request(self, url: str) -> dict:
        """Sends a request to the server and returns the response."""
        try:
            LOG.info(f"Using Tower API with the following url:{url}")
            response = requests.get(
                url,
                headers=self.headers,
                params=self.params,
                verify=True,
            )
            if response.status_code == 404:
                LOG.info("Request failed for url %s\n", url)
                response.raise_for_status()
        except (MissingSchema, HTTPError, ConnectionError) as error:
            LOG.info("Request failed for url %s: Error: %s\n", url, error)
            return {}

        return response.json()

    def requirements_provided(self) -> bool:
        """Return True if required variables are not empty."""
        if self.tower_api_endpoint is None or self.tower_api_endpoint == "":
            LOG.info("Error: no endpoint specified for Tower Open API request.")
            return False
        if self.tower_access_token is None or self.tower_access_token == "":
            LOG.info("Error: no access token specified for Tower Open API request.")
            return False
        if self.workspace_id is None or self.workspace_id == "":
            LOG.info("Error: no workspace specified for Tower Open API request.")
            return False
        return True

    @property
    def tasks(self) -> dict:
        """ """
        if self.requirements_provided():
            url = self.build_url(endpoint=self.tasks_endpoint)
            return self.send_request(url=url)

    @property
    def workflow(self) -> dict:
        """ """
        if self.requirements_provided():
            url = self.build_url(endpoint=self.workflow_endpoint)
            return self.send_request(url=url)
