from requests_mock import Mocker

from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.encryption_service.encryption_service import EncryptionService
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


def test_refresh_access_token(
    authentication_service: AuthenticationService,
    encryption_service: EncryptionService,
    user_email: str,
):
    # GIVEN an encrypted refresh token
    encrypted_refresh_token: str = encryption_service.encrypt("refresh_token")

    # GIVEN an existing user with the refresh token
    user: User = authentication_service.store.get_user(user_email)
    user.refresh_token = encrypted_refresh_token

    # WHEN refreshing the token
    token: str = authentication_service.refresh_token(user.id)

    # THEN a token is returned
    assert token
