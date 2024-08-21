import json
import pytest
import requests_mock

from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmAPIClient
from trailblazer.clients.tower.tower_client import TowerAPIClient


@pytest.fixture
def slurm_client() -> SlurmAPIClient:
    return SlurmAPIClient(
        base_url="https://slurm.example.com",
        access_token="access_token",
        user_name="user_name",
    )


@pytest.fixture
def tower_client():
    return TowerAPIClient(
        base_url="https://tower/",
        access_token="token",
        workspace_id="workspace_id",
    )


@pytest.fixture
def mock_request():
    with requests_mock.Mocker() as mock:
        yield mock


@pytest.fixture
def jobs_response() -> dict:
    return {"jobs": [{"name": "job 1"}, {"name": "job 2"}]}


@pytest.fixture
def tower_empty_task_response() -> dict:
    return {"tasks": [], "total": 0}


@pytest.fixture
def tower_running_tasks_response() -> dict:
    with open("tests/fixtures/tower/tower_tasks_running.json") as file:
        return json.load(file)


@pytest.fixture
def tower_completed_tasks_response() -> dict:
    with open("tests/fixtures/tower/tower_tasks_completed.json") as file:
        return json.load(file)
