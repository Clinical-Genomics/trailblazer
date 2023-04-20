"""Module for Tower Open API."""

import logging
import os
from typing import List, Tuple

import requests
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.apps.tower.models import (
    TowerProcess,
    TowerTask,
    TowerTaskResponse,
    TowerWorkflowResponse,
)
from trailblazer.constants import TOWER_STATUS, TrailblazerStatus

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

    @property
    def headers(self) -> dict:
        """Return headers required for an NF Tower API call.
        Accept and Authorization fields are mandatory."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.tower_access_token}",
        }

    @property
    def request_params(self) -> List[Tuple]:
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

    @property
    def meets_requirements(self) -> bool:
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


class TowerAPI:
    """Class communicating with NF tower regarding a given analysis (workflow)."""

    def __init__(self, workflow_id: str, dry_run: bool = False):
        self.workflow_id: str = workflow_id
        self.dry_run: bool = dry_run
        self._tower_client = None
        self._response = None
        self._tasks_response = None

    @property
    def tower_client(self) -> TowerApiClient:
        """Returns a NF Tower client."""
        if not self._tower_client:
            self._tower_client = TowerApiClient(workflow_id=self.workflow_id)
        return self._tower_client

    @property
    def response(self) -> TowerWorkflowResponse:
        """Returns a workflow response containing general information about an analysis."""
        if not self._response:
            self._response = self.tower_client.workflow
        return self._response

    @property
    def tasks_response(self) -> TowerTaskResponse:
        """Returns a tasks response containing information about jobs submitted as part of an analysis.
        A task response does not include all jobs that will be run as part of an analysis.
        It only includes jobs that have been submitted a at given time that could be either
        pending, running, completed or failed."""
        if not self._tasks_response:
            self._tasks_response = self.tower_client.tasks
        return self._tasks_response

    @property
    def status(self) -> str:
        """Returns the status of an analysis (also called workflow in NF Tower)."""
        return TOWER_STATUS.get(self.response.workflow.status, TrailblazerStatus.ERROR.value)

    @property
    def is_pending(self) -> bool:
        """Returns True if workflow has not started running. Otherwise returns False."""
        return self.status == TrailblazerStatus.PENDING.value

    @property
    def is_complete(self) -> bool:
        """Returns True if workflow has completed. Otherwise returns False."""
        return self.status == TrailblazerStatus.COMPLETED.value

    @property
    def processes(self) -> List[TowerProcess]:
        """Returns processes. Processes are steps in a pipeline that might or might not be executed by a given analysis.
        A process can also have more than one corresponding job (task).
        For example, a process could be a 'fastqc' step that could be run multiple times depending on
        how many input files are given."""
        return [TowerProcess(**process) for process in self.response.progress.processesProgress]

    @property
    def tasks(self) -> List[TowerTask]:
        """Returns tasks. Tasks correspond to jobs that have been submitted at a given point regardless of their
        status."""
        return [task["task"] for task in self.tasks_response.tasks]

    @property
    def total_jobs(self) -> int:
        """Returns the total number of jobs for a workflow."""
        return len(self.processes)

    @property
    def succeeded_jobs(self) -> int:
        """Returns the number of succeeded jobs for a workflow."""
        return sum(process.is_complete for process in self.processes)

    @property
    def progress(self) -> int:
        """Returns the progress percentage of a workflow.
        Note this number is not accurate since that exact number of
        processes to be run is unknown."""
        if self.is_complete:
            return 100
        elif self.is_pending or self.total_jobs == 0:
            return 0
        else:
            return int(self.succeeded_jobs * 100.0 / self.total_jobs)

    def get_jobs(self, analysis_id: int) -> List[dict]:
        """Returns a list of jobs associated to a workflow."""
        return [self._get_job(task=task, analysis_id=analysis_id) for task in self.tasks]

    def _get_job(self, task: TowerTask, analysis_id: int) -> dict:
        """Format a job with required information."""
        return dict(
            analysis_id=analysis_id,
            slurm_id=task.nativeId,
            name=task.process,
            status=task.status,
            started_at=task.start,
            elapsed=int(task.duration / 60),
        )
