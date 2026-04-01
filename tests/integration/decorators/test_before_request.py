from unittest.mock import create_autospec

import pytest
from flask import g
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from trailblazer.containers import Container
from trailblazer.server.api import before_request
from trailblazer.server.app import app
from trailblazer.server.wiring import setup_dependency_injection
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


def test_before_request_with_authorization_header(client: FlaskClient):
    # GIVEN a valid authorization token
    valid_authorization = "Bearer eyauth123"

    # GIVEN a user verification service that returns a user for the valid token
    user_verification_service: UserVerificationService = create_autospec(UserVerificationService)
    user_verification_service.verify_user = lambda authorization_header: (
        User(name="Logged In") if authorization_header == valid_authorization else None
    )

    # WHEN an endpoint decorated with before_request is called
    with container.user_verification_service.override(user_verification_service):
        response: TestResponse = client.get(
            "/test-before-request", headers={"Authorization": valid_authorization}
        )
        # THEN the current user was available in that endpoint
        assert response.text == "Current user: Logged In"
