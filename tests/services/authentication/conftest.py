import pytest

from trailblazer.services.authentication_service.models import (
    DecodingResponse,
    RealmAccess,
    TokenResponseModel,
)


@pytest.fixture
def realm_access() -> RealmAccess:
    return RealmAccess(roles=["cg-employee"])


@pytest.fixture
def token_response() -> TokenResponseModel:
    return TokenResponseModel(
        access_token="access_token",
        expires_in=3600,
        id_token="id_token",
        not_before_policy=0,
        refresh_expires_in=3600,
        refresh_token="refresh_token",
        scope="email profile",
        session_state="session-state",
        token_type="Bearer",
    )


@pytest.fixture
def decode_token_response(realm_access) -> DecodingResponse:
    return DecodingResponse(
        exp=1672531199,
        iat=1672531199,
        auth_time=1672531199,
        jti="unique-jti",
        iss="https://issuer.example.com",
        sub="subject-id",
        typ="Bearer",
        azp="client-id",
        sid="session-id",
        acr="1",
        allowed_origins=["https://allowed.example.com"],
        realm_access=realm_access,
        scope="email profile",
        email_verified=True,
        name="John Doe",
        preferred_username="johndoe",
        given_name="John",
        family_name="Doe",
        email="johndoe@example.com",
    )
