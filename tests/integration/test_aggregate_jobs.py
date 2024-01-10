from http import HTTPStatus
from flask.testing import FlaskClient
from trailblazer.constants import TrailblazerStatus
from trailblazer.dto import FailedJobsRequest

from trailblazer.store.models import Analysis


def test_get_aggregated_jobs(client: FlaskClient, analysis_with_failed_job: Analysis):
    # GIVEN a valid request to aggregate failed jobs a month back
    request = FailedJobsRequest(days_back=31)
    data: str = request.model_dump_json()

    # WHEN retrieving statistics for the failed jobs
    response = client.get("/api/v1/aggregate/jobs", data=data, content_type="application/json")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it returns the correct number of failed jobs
    failed_jobs_count: int = sum(job["count"] for job in response.json["jobs"])
    assert failed_jobs_count == 1
