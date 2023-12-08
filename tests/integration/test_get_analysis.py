from flask.testing import FlaskClient
from http import HTTPStatus

from trailblazer.store.models import Analysis


def test_get_existing_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # WHEN requesting the analysis
    response = client.get(f"/api/v1/analyses/{analysis.id}")

    # THEN it should return the analysiss
    assert response.status_code == HTTPStatus.OK
