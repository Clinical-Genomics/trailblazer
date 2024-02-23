from flask.testing import FlaskClient
from http import HTTPStatus

from trailblazer.store.models import Analysis


def test_get_summaries(client: FlaskClient, analysis: Analysis):
    # GIVEN an order with an analysis
    order_id: int = analysis.order_id

    # WHEN requesting a summary for the analyses in the order
    response = client.get(f"/api/v1/summary?orderIds={order_id}")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK
