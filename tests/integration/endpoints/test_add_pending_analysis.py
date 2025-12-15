import json
from http import HTTPStatus

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from trailblazer.store.models import Analysis
from trailblazer.store.store import Store

TYPE_JSON = "application/json"


def test_adding_analysis(client: FlaskClient, store: Store):
    # GIVEN a valid request to add an analysis
    data: str = json.dumps(
        {
            "case_id": "case_id",
            "config_path": "config_path",
            "order_id": 123,
            "out_dir": "out_dir",
            "priority": "normal",
            "ticket": "ticket_id",
            "tower_workflow_id": None,
            "type": "wgs",
            "workflow": "wgs",
        }
    )

    # WHEN sending the request
    response: TestResponse = client.post(
        "/api/v1/add-pending-analysis", data=data, content_type=TYPE_JSON
    )

    # THEN it gives a success response with json contents
    assert response.status_code == HTTPStatus.CREATED
    assert response.json

    # THEN the analysis was persisted
    analysis_id = int(response.json["id"])
    assert store.get_analysis_with_id(analysis_id)


def test_adding_analysis_without_config_path(client: FlaskClient, store: Store):
    # GIVEN a request to add an analysis with tower as workflow manager and no config_path
    data: str = json.dumps(
        {
            "case_id": "case_id",
            "config_path": None,
            "order_id": 123,
            "out_dir": "out_dir",
            "priority": "normal",
            "ticket": "ticket_id",
            "tower_workflow_id": None,
            "type": "wgs",
            "workflow": "wgs",
            "workflow_manager": "nf_tower",
        }
    )

    # WHEN sending the request
    response: TestResponse = client.post(
        "/api/v1/add-pending-analysis", data=data, content_type=TYPE_JSON
    )

    # THEN it gives a success response with json contents
    assert response.status_code == HTTPStatus.CREATED
    assert response.json

    # THEN the analysis was persisted without a config_path
    analysis_id = int(response.json["id"])
    analysis: Analysis = store.get_analysis_with_id(analysis_id)
    assert analysis.config_path is None


def test_adding_analysis_without_config_path_and_slurm_workflow_manager_fails(
    client: FlaskClient,
):
    # GIVEN a request to add an analysis with slurm as workflow manager and no config_path
    data: str = json.dumps(
        {
            "case_id": "case_id",
            "email": None,
            "is_hidden": None,
            "order_id": 123,
            "out_dir": "out_dir",
            "priority": "normal",
            "ticket": "ticket_id",
            "tower_workflow_id": None,
            "type": "wgs",
            "workflow": "wgs",
            "workflow_manager": "slurm",
        }
    )

    # WHEN sending the request
    response: TestResponse = client.post(
        "/api/v1/add-pending-analysis", data=data, content_type=TYPE_JSON
    )

    # THEN an error response is returned
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json
    assert response.json["error"]
