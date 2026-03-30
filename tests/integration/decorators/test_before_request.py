from unittest.mock import create_autospec

import pytest
from flask import Flask, g
from flask.testing import FlaskClient
from pytest_mock import MockerFixture
from werkzeug.test import TestResponse

from trailblazer.server.api import blueprint
from trailblazer.server.wiring import setup_dependency_injection
from trailblazer.services.user_verification_service.user_verification_service import (
    UserVerificationService,
)
from trailblazer.store.models import User

container = setup_dependency_injection()


@pytest.fixture
def before_request_app():
    app = Flask("test_app")
    app.config["TESTING"] = True

    @blueprint.route("/test-before-request")
    def test_endpoint():
        return f"Current user: {g.current_user.name}", 200

    app.register_blueprint(blueprint)

    return app


@pytest.fixture
def client(before_request_app: Flask) -> FlaskClient:
    return before_request_app.test_client()


def test_before_request_with_authorization_header(client: FlaskClient, mocker: MockerFixture):
    valid_authorization = "Bearer eyauth123"

    user_verification_service: UserVerificationService = create_autospec(UserVerificationService)
    user_verification_service.verify_user = lambda authorization_header: (
        User(name="Logged In") if authorization_header == valid_authorization else None
    )

    with container.user_verification_service.override(user_verification_service):
        response: TestResponse = client.get(
            "/api/v1/test-before-request", headers={"Authorization": valid_authorization}
        )
        assert response.status_code == 200
        assert response.text == "Current user: Logged In"
