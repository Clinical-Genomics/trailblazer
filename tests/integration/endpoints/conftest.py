from typing import Generator
from unittest.mock import patch
from flask import Flask
from flask.testing import FlaskClient
import pytest
import requests_mock

from trailblazer.clients.authentication_client.dtos.tokens_response import TokensResponse
from trailblazer.server.app import app
from trailblazer.server.wiring import setup_dependency_injection
from trailblazer.store.store import Store
from trailblazer.containers import Container


@pytest.fixture(autouse=True)
def container() -> Container:
    container: Container = setup_dependency_injection()
    return container


@pytest.fixture
def flask_app(store: Store):
    yield app


@pytest.fixture
def client(flask_app: Flask) -> Generator[FlaskClient, None, None]:
    # Bypass authentication
    with patch.object(flask_app, "before_request_funcs", new={}):
        yield flask_app.test_client()


@pytest.fixture
def oauth_response() -> dict:
    return {
        "access_token": "access_token",
        "token_type": "token_type",
        "expires_in": 3600,
        "refresh_token": "refresh_token",
        "scope": "scope",
    }


@pytest.fixture
def mock_request():
    with requests_mock.Mocker() as mock:
        yield mock
