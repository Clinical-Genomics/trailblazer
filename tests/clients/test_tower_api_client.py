from requests_mock import Mocker
from trailblazer.clients.tower.tower_client import TowerAPIClient


def test_tower_api_client_empty_task_response(
    tower_client: TowerAPIClient,
    tower_empty_task_response: dict,
    mock_request: Mocker,
):
    # GIVEN a workflow response without tasks
    mock_request.get("https://tower/workflow/1/tasks", json=tower_empty_task_response)

    # WHEN fetching the tasks for a workflow
    response = tower_client.get_tasks(workflow_id="1")

    # THEN the response should be empty
    assert response.tasks == []
    assert response.total == 0
