from requests_mock import Mocker

from trailblazer.dto.authentication.access_token_response import AccessToken
from trailblazer.services.authentication_service.authentication_service import AuthenticationService


def test_exchange_code(authentication_service: AuthenticationService):
    # GIVEN an authentication service

    # WHEN exchanging the authorization code
    response: AccessToken = authentication_service.authenticate("auth_code")

    # THEN an access token is returned
    assert response.access_token
