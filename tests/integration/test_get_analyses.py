from http import HTTPStatus
from flask.testing import FlaskClient
from trailblazer.constants import Pipeline, TrailblazerPriority, TrailblazerStatus

from trailblazer.store.models import Analysis


def test_get_analyses(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses

    # WHEN retrieving all analyses
    response = client.get(f"/api/v1/analyses?pageSize={len(analyses)}")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses
    assert len(response.json["analyses"]) == len(analyses)


def test_get_analyses_sorted_by_ticket_id(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses

    # WHEN retrieving analyses sorted by ticket id
    response = client.get(
        f"/api/v1/analyses?pageSize={len(analyses)}&sortField=ticket_id&sortOrder=asc"
    )

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses
    assert len(response.json["analyses"]) == len(analyses)

    # THEN the analyses should be sorted by the ticket id
    ticket_ids = [analysis["ticket_id"] for analysis in response.json["analyses"]]
    assert ticket_ids == sorted(ticket_ids)


def test_get_analyses_filtered_by_single_status(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses with different statuses

    # WHEN retrieving completed analyses
    response = client.get("/api/v1/analyses?status[]=completed")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses with the status completed
    completed_analyses = [
        analysis for analysis in analyses if analysis.status == TrailblazerStatus.COMPLETED
    ]
    assert len(response.json["analyses"]) == len(completed_analyses)


def test_get_analyses_filtered_by_multiple_statuses(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses with different statuses

    # WHEN retrieving analyses with either the status error or failed
    response = client.get(
        f"/api/v1/analyses?pageSize={len(analyses)}&status[]=error&status[]=failed"
    )

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses with the status completed or failed
    completed_or_failed_analyses = [
        analysis
        for analysis in analyses
        if analysis.status in [TrailblazerStatus.ERROR, TrailblazerStatus.FAILED]
    ]
    assert len(response.json["analyses"]) == len(completed_or_failed_analyses)


def test_get_analyses_filter_by_multiple_criteria(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses with different statuses

    # WHEN retrieving failed analyses with high priority
    high_prio: str = TrailblazerPriority.HIGH
    failed_status: str = TrailblazerStatus.FAILED
    response = client.get(f"/api/v1/analyses?status[]={failed_status}&priority[]={high_prio}")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all failed analyses with high priority
    failed_high_prio = [
        analysis
        for analysis in analyses
        if analysis.status == failed_status and analysis.priority == high_prio
    ]
    assert len(response.json["analyses"]) == len(failed_high_prio)


def test_get_analyses_without_comments(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses with and without comments

    # WHEN retrieving all analyses without comments
    response = client.get(f"/api/v1/analyses?pageSize={len(analyses)}&comment[]=")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return all analyses without comments
    analyses_without_comments = [analysis for analysis in analyses if not analysis.comment]
    assert len(response.json["analyses"]) == len(analyses_without_comments)


def test_get_analyses_by_pipeline(client: FlaskClient, analyses: list[Analysis]):
    # GIVEN analyses with different pipelines

    # WHEN retrieving all mip analyses
    response = client.get("/api/v1/analyses?pipeline=mip-dna")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should only return mip analyses
    assert all(a["data_analysis"] == Pipeline.MIP_DNA.lower() for a in response.json["analyses"])
