import json
from http import HTTPStatus

from flask.testing import FlaskClient

from trailblazer.constants import TrailblazerStatus
from trailblazer.dto import AnalysisUpdateRequest
from trailblazer.store.models import Analysis

TYPE_JSON = "application/json"


def test_update_analysis_status(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis with a pending status

    # GIVEN a valid request to set the status to completed
    request = AnalysisUpdateRequest(status=TrailblazerStatus.COMPLETED)
    data: str = request.model_dump_json()

    # WHEN updating the analysis to be completed
    response = client.put(f"/api/v1/analyses/{analysis.id}", data=data, content_type=TYPE_JSON)

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return the analysis
    assert response.json["id"] == analysis.id

    # THEN it should have the new status
    assert response.json["status"] == TrailblazerStatus.COMPLETED


def test_update_analysis_comment(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # GIVEN a valid request to set the comment
    new_comment = "new comment"
    request = AnalysisUpdateRequest(comment=new_comment)
    data: str = request.model_dump_json()

    # WHEN updating the analysis with a comment
    response = client.put(f"/api/v1/analyses/{analysis.id}", data=data, content_type=TYPE_JSON)

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it returns the analysis
    assert response.json["id"] == analysis.id

    # THEN it has the new comment
    assert response.json["comment"] == new_comment


def test_update_analysis_visibility(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis tagged as visible

    # GIVEN a valid request to set the visibility
    request = AnalysisUpdateRequest(is_visible=False)
    data: str = request.model_dump_json()

    # WHEN updating the analysis with a comment
    response = client.put(f"/api/v1/analyses/{analysis.id}", data=data, content_type=TYPE_JSON)

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it returns the analysis
    assert response.json["id"] == analysis.id

    # THEN it has the new visibility
    assert response.json["is_visible"] is False


def test_update_analysis_invalid_request(client: FlaskClient, analysis: Analysis):
    # GIVEN an invalid request
    data: str = json.dumps({"status": "invalid_status"})

    # WHEN updating the analysis with an invalid request
    response = client.put(f"/api/v1/analyses/{analysis.id}", data=data, content_type=TYPE_JSON)

    # THEN it gives a bad request response
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_comment_on_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN a valid request to delete a comment
    data: str = json.dumps({"comment": ""})

    # WHEN sending the request
    response = client.put(f"/api/v1/analyses/{analysis.id}", data=data, content_type=TYPE_JSON)

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it returns the analysis without a comment
    assert response.json["comment"] == ""
