import pytest
import requests_mock

from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmApiClient


@pytest.fixture
def client() -> SlurmApiClient:
    return SlurmApiClient(
        base_url="https://slurm.example.com",
        access_token="access_token",
        user_name="user_name",
    )


@pytest.fixture
def mock_request():
    with requests_mock.Mocker() as mock:
        yield mock


@pytest.fixture
def jobs_response() -> dict:
    return {"jobs": [{"name": "job 1"}, {"name": "job 2"}]}
