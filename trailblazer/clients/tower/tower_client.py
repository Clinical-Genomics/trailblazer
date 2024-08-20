import requests

from trailblazer.clients.tower.models import (
    TowerTasksResponse,
    TowerWorkflowResponse,
)
from trailblazer.clients.tower.utils import handle_client_errors


class TowerAPIClient:
    """A client consuming the Tower API. Endpoints are defined in https://tower.nf/openapi/."""

    def __init__(self, base_url: str, access_token: str, workspace_id: str):
        self.base_url = base_url
        self.request_params = [("workspaceId", workspace_id)]
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

    @handle_client_errors
    def get_tasks(self, workflow_id: str) -> TowerTasksResponse:
        url = f"{self.base_url}workflow/{workflow_id}/tasks"
        response = requests.get(url=url, headers=self.headers, params=self.request_params)
        response.raise_for_status()
        json = response.json()
        return TowerTasksResponse.model_validate(json)

    @handle_client_errors
    def get_workflow(self, workflow_id: str) -> TowerWorkflowResponse:
        url = f"{self.base_url}workflow/{workflow_id}"
        response = requests.get(url=url, headers=self.headers, params=self.request_params)
        response.raise_for_status()
        json = response.json()
        return TowerWorkflowResponse.model_validate(json)

    @handle_client_errors
    def cancel_workflow(self, workflow_id: str) -> None:
        url = f"{self.base_url}workflow/{workflow_id}/cancel"
        response = requests.post(url=url, headers=self.headers, params=self.request_params, json={})
        response.raise_for_status()
