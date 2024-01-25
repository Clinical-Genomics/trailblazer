from flask.testing import FlaskClient
from http import HTTPStatus
from trailblazer.dto.create_job_request import CreateJobRequest

from trailblazer.store.models import Analysis

TYPE_JSON = "application/json"


def test_add_job_to_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # GIVEN a valid request to add a job to the analysis
    create_job_request = CreateJobRequest(name="job", slurm_id="12345")
    data: str = create_job_request.model_dump_json()

    # WHEN sending the request
    response = client.post(
        f"/api/v1/analyses/{analysis.id}/jobs", data=data, content_type=TYPE_JSON
    )

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.CREATED

    # THEN it should return the job
    assert response.json["name"] == create_job_request.name
