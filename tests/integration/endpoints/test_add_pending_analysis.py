from http import HTTPStatus

from flask.testing import FlaskClient

from trailblazer.constants import TrailblazerPriority, TrailblazerTypes
from trailblazer.dto.create_analysis_request import CreateAnalysisRequest
from trailblazer.store.store import Store

TYPE_JSON = "application/json"


def test_adding_analysis(client: FlaskClient, store: Store):
    # GIVEN a valid request to add an analysis
    create_analysis_request = CreateAnalysisRequest(
        case_id="case_id",
        config_path="config_path",
        workflow=TrailblazerTypes.WGS,
        priority=TrailblazerPriority.NORMAL,
        out_dir="out_dir",
        ticket="ticket_id",
        type=TrailblazerTypes.WGS,
        order_id=123,
    )
    data: str = create_analysis_request.model_dump_json()

    # WHEN sending the request
    response = client.post("/api/v1/add-pending-analysis", data=data, content_type=TYPE_JSON)

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.CREATED

    # THEN the analysis was persisted
    analysis_id = int(response.json["id"])
    assert store.get_analysis_with_id(analysis_id)
