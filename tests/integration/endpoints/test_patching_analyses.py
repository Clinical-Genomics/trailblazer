import json
from http import HTTPStatus
from unittest.mock import ANY, Mock, create_autospec

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from trailblazer.containers import Container
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.server import api
from trailblazer.server.wiring import setup_dependency_injection
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis, User
from trailblazer.store.store import Store

container: Container = setup_dependency_injection()


def test_patch_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # GIVEN a valid request to pach the analysis
    update = AnalysisUpdate(id=analysis.id, comment="new_comment")
    request = UpdateAnalyses(analyses=[update])
    data: str = request.model_dump_json()

    # WHEN patching the analysis
    response = client.patch("/api/v1/analyses", data=data, content_type="application/json")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN it should return the analysis
    assert response.json["analyses"]


def test_patch_analysis_email_provided(client: FlaskClient, mocker: MockerFixture):
    # GIVEN an analysis update
    analysis_update = {
        "analyses": [{"id": 0}],
        "email": "fun@cg.se",
    }
    status_db: Store = create_autospec(Store)
    user = User(
        email="fun@cg.se",
        abbreviation="fc",
        name="Mr. Fun CG",
        google_id="0",
        refresh_token="abc123",
    )
    status_db.get_user_by_email_strict = Mock(return_value=user)

    mocker.patch.object(api, "store", status_db)
    analysis_service = create_autospec(AnalysisService)
    with container.analysis_service.override(analysis_service):
        # WHEN patching an analysis
        response = client.patch(
            "/api/v1/analyses", data=json.dumps(analysis_update), content_type="application/json"
        )

    # THEN the correct user should have been used to update the analysis
    analysis_service.update_analyses.assert_called_once_with(data=ANY, user=user)


def test_patch_analysis_nonexistent_email(client: FlaskClient):
    pass
