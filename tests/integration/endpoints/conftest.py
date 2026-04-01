from typing import Generator
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from trailblazer.server.app import app
from trailblazer.store.store import Store


@pytest.fixture
def flask_app(user_store: Store):
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture
def client(flask_app: Flask) -> Generator[FlaskClient, None, None]:
    # Bypass authentication
    with patch.object(flask_app, "before_request_funcs", new={}):
        yield flask_app.test_client()
