from http import HTTPStatus

from flask.testing import FlaskClient

from trailblazer.store.models import Analysis


def test_get_summaries(client: FlaskClient, analysis: Analysis):
    # GIVEN an order with an analysis
    order_id: int = analysis.order_id

    # WHEN requesting a summary for the analyses in the order
    response = client.get(f"/api/v1/summary?orderIds={order_id}")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK


def test_get_summaries_lastest_date(
    client: FlaskClient,
    analysis: Analysis,
    analyses: list[Analysis],
    order_id_with_multiple_analyses: int,
):
    # GIVEN an order with multiple analyses for the same case

    # WHEN requesting a summary for the analyses in the order
    response = client.get(f"/api/v1/summary?orderIds={order_id_with_multiple_analyses}")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK
    assert response.json["summaries"][0]["total"] == 1
