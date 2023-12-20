from http import HTTPStatus
from flask.testing import FlaskClient
from trailblazer.constants import TrailblazerStatus

from trailblazer.store.models import Analysis


def test_get_analyses(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN some analyses

    # WHEN retrieving all analyses
    response = client.get("/api/v1/analyses")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses
    assert len(response.json["analyses"]) == len(analyses)


def test_get_analyses_sorted_by_ticket_id(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN some analyses

    # WHEN requesting the analysis
    response = client.get("/api/v1/analyses?sortField=ticket_id&sortOrder=asc")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses
    assert len(response.json["analyses"]) == len(analyses)

    # THEN the analyses should be sorted by the ticket id
    ticket_ids = [analysis["ticket_id"] for analysis in response.json["analyses"]]
    assert ticket_ids == sorted(ticket_ids)


def test_get_analyses_filtered_by_status(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN an analysis

    # WHEN requesting the analysis
    response = client.get("/api/v1/analyses?status%5B%5D=completed")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses with the status completed
    completed_analyses = [a for a in analyses if a.status == TrailblazerStatus.COMPLETED]
    assert len(response.json["analyses"]) == len(completed_analyses)
