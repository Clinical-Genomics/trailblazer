import json
from http import HTTPStatus
from unittest.mock import ANY, Mock, create_autospec

from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from tests.typed_mock import TypedMock, create_typed_mock
from trailblazer.containers import Container
from trailblazer.dto import analyses_response
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.update_analyses import AnalysisUpdate, UpdateAnalyses
from trailblazer.exc import UserNotFoundError
from trailblazer.server import api
from trailblazer.store.models import User
from trailblazer.store.store import Store

from trailblazer.server.wiring import setup_dependency_injection
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.store.models import Analysis

container: Container = setup_dependency_injection()


def test_patch_analysis(client: FlaskClient, analysis: Analysis):
    # GIVEN an analysis

    # GIVEN a valid request to patch the analysis
    request = {"analyses": [{"id": analysis.id, "comment": "new_comment"}]}
    data: str = json.dumps(request)

    analysis_service: TypedMock[AnalysisService] = create_typed_mock(AnalysisService)
    mock_response = UpdateAnalysesResponse(
        analyses=[
            analyses_response.Analysis(
                id=analysis.id, case_id=analysis.case_id, workflow_manager=analysis.workflow_manager
            )
        ]
    )
    analysis_service.as_type.update_analyses = Mock(return_value=mock_response)

    # WHEN patching the analysis
    with container.analysis_service.override(analysis_service.as_type):
        response = client.patch("/api/v1/analyses", data=data, content_type="application/json")

    # THEN it gives a success response
    assert response.status_code == HTTPStatus.OK

    # THEN the analysis service should have been called to update the provided analysis
    analysis_service.as_mock.update_analyses.assert_called_once_with(
        data=UpdateAnalyses(analyses=[AnalysisUpdate(id=analysis.id, comment="new_comment")]),
        user=None,
    )


def test_patch_analysis_signature_provided(client: FlaskClient, mocker: MockerFixture):
    # GIVEN an analysis update
    analysis_update = {
        "analyses": [{"id": 0}],
        "signature": "CG",
    }
    status_db: Store = create_autospec(Store)
    user = User(
        email="fun@cg.se",
        abbreviation="CG",
        name="Mr. Fun CG",
        google_id="0",
        refresh_token="abc123",
    )
    status_db.get_user_by_signature_strict = Mock(return_value=user)

    mocker.patch.object(api, "store", status_db)
    analysis_service = create_autospec(AnalysisService)
    with container.analysis_service.override(analysis_service):
        # WHEN patching an analysis
        client.patch(
            "/api/v1/analyses", data=json.dumps(analysis_update), content_type="application/json"
        )

    # THEN the correct user should have been used to update the analysis
    analysis_service.update_analyses.assert_called_once_with(data=ANY, user=user)


def test_patch_analysis_nonexistent_signature(client: FlaskClient, mocker: MockerFixture):
    # GIVEN an analysis update with a signature that doesn't correspond to a user in the database
    analysis_update = {
        "analyses": [{"id": 0}],
        "signature": "NOT_A_USER",
    }
    status_db: Store = create_autospec(Store)
    status_db.get_user_by_signature_strict = Mock(side_effect=UserNotFoundError("User not found"))

    mocker.patch.object(api, "store", status_db)

    # WHEN patching an analysis
    response = client.patch(
        "/api/v1/analyses", data=json.dumps(analysis_update), content_type="application/json"
    )
    # THEN a bad request response is returned
    assert response.status_code == HTTPStatus.BAD_REQUEST
