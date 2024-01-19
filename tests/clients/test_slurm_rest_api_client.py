from requests_mock import Mocker
from trailblazer.clients.slurm_api_client.dto import SlurmJobsResponse
from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmApiClient


def test_get_slurm_jobs(client: SlurmApiClient, mock_request: Mocker, jobs_response: dict):
    # GIVEN a mocked jobs response
    mock_request.get(f"{client.base_url}/slurmV0040/jobs", json=jobs_response)

    # WHEN retrieving the jobs
    jobs_response: SlurmJobsResponse = client.get_jobs()

    # THEN the jobs are deserialized without error
    assert jobs_response
