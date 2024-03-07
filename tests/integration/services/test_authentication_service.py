from requests_mock import Mocker

from trailblazer.services.authentication_service.authentication_service import AuthenticationService


def test_exchange_code(
    authentication_service: AuthenticationService,
    oauth_response: dict,
    mock_request: Mocker,
):
    # GIVEN a mocked oauth response
    mock_request.post("https://oauth2.googleapis.com/token", json=oauth_response)

    # WHEN exchanging the authorization code
    response = authentication_service.exchange_code("auth_code")

    # THEN the access token is returned
    assert response.access_token == oauth_response["access_token"]
