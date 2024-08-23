from requests_mock import Mocker
from trailblazer.clients.tower.tower_client import TowerAPIClient


def test_empty_tasks_response_is_accepted(
    tower_client: TowerAPIClient,
    tower_empty_task_response: dict,
    mock_request: Mocker,
):
    # GIVEN a workflow response without tasks
    mock_request.get("https://tower/workflow/1/tasks", json=tower_empty_task_response)

    # WHEN fetching the tasks for a workflow
    response = tower_client.get_tasks(workflow_id="1")

    # THEN the response should not contain any tasks
    assert response.tasks == []

    # THEN the response should have a total of 0 tasks
    assert response.total == 0


def test_running_tasks_response_is_accepted(
    tower_client: TowerAPIClient,
    tower_running_tasks_response: dict,
    mock_request: Mocker,
):
    # GIVEN a workflow response with running tasks
    mock_request.get("https://tower/workflow/1/tasks", json=tower_running_tasks_response)

    # WHEN fetching the tasks for a workflow
    response = tower_client.get_tasks(workflow_id="1")

    # THEN the response should contain running tasks
    assert response.tasks

    # THEN the response should have a total of tasks
    assert response.total


def test_completed_tasks_response_is_accepted(
    tower_client: TowerAPIClient,
    tower_completed_tasks_response: dict,
    mock_request: Mocker,
):
    # GIVEN a workflow response with completed tasks
    mock_request.get("https://tower/workflow/1/tasks", json=tower_completed_tasks_response)

    # WHEN fetching the tasks for a workflow
    response = tower_client.get_tasks(workflow_id="1")

    # THEN the response should contain completed tasks
    assert response.tasks

    # THEN the response should have a total of tasks
    assert response.total
