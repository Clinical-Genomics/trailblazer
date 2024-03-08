from flask.testing import FlaskClient
from http import HTTPStatus
from trailblazer.dto.create_job_request import CreateJobRequest

from trailblazer.store.models import Analysis
from trailblazer.store.store import Store

TYPE_JSON = "application/json"


def test_add_job_to_analysis(client: FlaskClient, analysis: Analysis, store: Store):
    # GIVEN an analysis
    analysis_id: int = analysis.id

    # GIVEN a valid request to add a job to the analysis
    create_job_request = CreateJobRequest(slurm_id=123)
    data: str = create_job_request.model_dump_json()

    # WHEN sending the request
    response = client.post(
        f"/api/v1/analysis/{analysis_id}/jobs", data=data, content_type=TYPE_JSON
    )

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.CREATED

    # THEN it should return the job
    assert response.json["slurm_id"] == create_job_request.slurm_id

    # THEN the job was persisted
    assert store.get_analysis_with_id(analysis_id).jobs
