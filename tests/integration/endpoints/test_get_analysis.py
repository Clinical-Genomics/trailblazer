from flask.testing import FlaskClient
from http import HTTPStatus

from trailblazer.store.models import Analysis


def test_get_existing_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # WHEN requesting the analysis
    response = client.get(f"/api/v1/analyses/{analysis.id}")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return the analysis
    assert response.json["id"] == analysis.id


def test_get_non_existing_analysis(client: FlaskClient, non_existing_analysis_id: str):
    # GIVEN a non existing analysis id

    # WHEN requesting the analysis
    response = client.get(f"/api/v1/analyses/{non_existing_analysis_id}")

    # THEN no analysis is found
    assert response.status_code == HTTPStatus.NOT_FOUND
