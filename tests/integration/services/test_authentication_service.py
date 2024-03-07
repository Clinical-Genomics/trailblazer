from requests_mock import Mocker

from trailblazer.services.authentication_service.authentication_service import AuthenticationService


def test_exchange_code(authentication_service: AuthenticationService):
    # WHEN exchanging the authorization code
    response = authentication_service.authenticate("auth_code")

    # THEN an access token is returned
    assert response.access_token
