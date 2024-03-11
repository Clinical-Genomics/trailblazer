from requests_mock import Mocker

from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.store.models import User


def test_exchange_code(authentication_service: AuthenticationService, user_email: str):
    # GIVEN an authentication service

    # WHEN exchanging the authorization code
    token: str = authentication_service.authenticate("auth_code")

    # THEN an access token is returned
    assert token

    # THEN the refresh token is stored on the user
    user: User = authentication_service.store.get_user(user_email)
    assert user.refresh_token
