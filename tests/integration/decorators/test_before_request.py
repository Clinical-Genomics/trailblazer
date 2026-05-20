from collections.abc import Callable
from http import HTTPStatus
from unittest.mock import create_autospec

import pytest
from flask import g
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from trailblazer.containers import Container
from trailblazer.server.api import before_request
from trailblazer.server.app import app
from trailblazer.server.wiring import setup_dependency_injection
from trailblazer.services.user_verification_service.exc import UserTokenVerificationError
from trailblazer.services.user_verification_service.user_verification_service import (
    UserVerificationService,
)
from trailblazer.store.models import User

container: Container = setup_dependency_injection()

app.before_request(before_request)


@app.route("/test-before-request")
def before_request_endpoint():
    return f"Current user: {g.current_user.name}", 200


@pytest.fixture
def client() -> FlaskClient:
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def valid_tokens():
    return ["Bearer valid_authorization", "Bearer valid_on_behalf_of"]


@pytest.fixture
def mock_verify_user(valid_tokens: list[str]) -> Callable[..., User]:
    def verify_user(authorization_header: str) -> User:
        if authorization_header in valid_tokens:
            return User(name="Logged In")
        else:
            raise UserTokenVerificationError(f"Invalid token: {authorization_header}")

    return verify_user


@pytest.mark.parametrize(
    "headers",
    [
        {"Authorization": "Bearer valid_authorization"},
        {
            "Authorization": "Bearer valid_authorization",
            "X-On-Behalf-Of": "Bearer valid_on_behalf_of",
        },
    ],
    ids=["Only authorization set", "Both authorization and on-behalf-of set"],
)
def test_authorization_succeeds(
    client: FlaskClient, headers: dict[str, str], mock_verify_user: Callable
):
    # GIVEN a user verification service that returns a user for a valid token
    user_verification_service: UserVerificationService = create_autospec(UserVerificationService)
    user_verification_service.verify_user = mock_verify_user

    # WHEN an endpoint decorated with before_request is called
    with container.user_verification_service.override(user_verification_service):
        response: TestResponse = client.get("/test-before-request", headers=headers)
        # THEN the current user was available in that endpoint
        assert response.text == "Current user: Logged In"


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer some_invalid_token"},
        {
            "Authorization": "Bearer valid_authorization",
            "X-On-Behalf-Of": "Bearer some_invalid_token",
        },
        {
            "Authorization": "Bearer some_invalid_token",
            "X-On-Behalf-Of": "Bearer valid_on_behalf_of",
        },
    ],
    ids=[
        "No headers",
        "Invalid authorization",
        "Valid authorization, invalid on-behalf-of",
        "Invalid autorization, valid on-behalf-of",
    ],
)
def test_authorization_fails(
    client: FlaskClient, headers: dict[str, str], mock_verify_user: Callable
):
    # GIVEN a user verification service that raises an error for an invalid token
    user_verification_service: UserVerificationService = create_autospec(UserVerificationService)
    user_verification_service.verify_user = mock_verify_user

    # WHEN an endpoint decorated with before_request is called
    with container.user_verification_service.override(user_verification_service):
        response: TestResponse = client.get("/test-before-request", headers=headers)
        # THEN the request is not authorized
        assert response.status_code == HTTPStatus.UNAUTHORIZED
