"""Module for Tower Open API."""

import logging
import os
from pathlib import Path

import requests
from requests import ConnectionError, HTTPError
from requests.exceptions import MissingSchema

from trailblazer.apps.tower.models import (
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
        status: str = TOWER_WORKFLOW_STATUS.get(
            self.response.workflow.status, TrailblazerStatus.ERROR.value
        )

        # If the whole workflow (analysis) is completed set it as QC instead of COMPLETE
        if status == TrailblazerStatus.COMPLETED:
            return TrailblazerStatus.QC
        return status

    @property
    def is_pending(self) -> bool:
        """Returns True if workflow has not started running. Otherwise returns False."""
        return self.status == TrailblazerStatus.PENDING

    @property
    def is_complete(self) -> bool:
        """Returns True if workflow has completed. Otherwise returns False."""
        return self.status == TrailblazerStatus.QC

    @property
    def processes(self) -> list[TowerProcess]:
        """Returns processes. Processes are steps in a pipeline that might or might not be executed by a given analysis.
        A process can also have more than one corresponding job (task).
        For example, a process could be a 'fastqc' step that could be run multiple times depending on
        how many input files are given."""
        return [TowerProcess(**process) for process in self.response.progress.processesProgress]

    @property
    def tasks(self) -> list[TowerTask]:
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
    def progress(self) -> float:
        """Returns the progress fraction of a workflow.
        Note this number is not accurate since that exact number of
        processes to be run is unknown."""
        if self.is_complete:
            return 1
        elif self.is_pending or self.total_jobs == 0:
            return 0
        else:
            return round(float(self.succeeded_jobs) / self.total_jobs, 2)

    def get_jobs(self, analysis_id: int) -> list[dict]:
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

    def cancel(self) -> None:
        """Cancel a workflow."""
        self.tower_client.send_cancel_request()


def _validate_tower_api_client_requirements(tower_api: TowerAPI) -> bool:
    """Raises:
    TowerRequirementsError when failing meeting Tower mandatory requirement"""
    if not tower_api.tower_client.meets_requirements:
        raise TowerRequirementsError("Could not initialize Tower API due to missing requirements")
    return True


def get_tower_api(config_file_path: str, case_id: str) -> TowerAPI | None:
    """Return Tower API. Currently only one tower ID is supported."""
    workflow_id: int = ReadFile.get_content_from_file(
        file_format=FileFormat.YAML, file_path=Path(config_file_path)
    ).get(case_id)[-1]
    tower_api = TowerAPI(workflow_id=str(workflow_id))
    if _validate_tower_api_client_requirements(tower_api=tower_api):
        return tower_api
