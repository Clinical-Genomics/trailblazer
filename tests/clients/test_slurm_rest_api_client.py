from requests_mock import Mocker
from trailblazer.clients.slurm_api_client.dto import SlurmJobsResponse
from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmAPIClient


def test_get_slurm_jobs(client: SlurmAPIClient, mock_request: Mocker, jobs_response: dict):
    # GIVEN a mocked jobs response
    mock_request.get(f"{client.base_url}/slurm/v0.0.40/job/1", json=jobs_response)

    # WHEN retrieving the jobs
    jobs_response: SlurmJobsResponse = client.get_job("1")

    # THEN the jobs are deserialized without error
    assert jobs_response
