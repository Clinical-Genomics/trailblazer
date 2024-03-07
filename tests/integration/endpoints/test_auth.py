from flask.testing import FlaskClient
from requests_mock import Mocker

from trailblazer.dto.authentication.code_exchange_request import CodeExchangeRequest


def test_authenticate_success(
    client: FlaskClient,
    mock_request: Mocker,
    oauth_response: dict,
):
    # GIVEN a mocked OAuth response
    mock_request.post("https://oauth2.googleapis.com/token", json=oauth_response)

    # GIVEN a valid request to authenticate
    request = CodeExchangeRequest(code="authorization_code")
    data: str = request.model_dump_json()

    # WHEN authenticating
    response = client.post("/api/v1/auth", data=data, content_type="application/json")

    # THEN it gives a success response
    assert response.status_code == 200
