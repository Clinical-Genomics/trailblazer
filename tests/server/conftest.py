# -*- coding: utf-8 -*-
import pytest

from trailblazer.server.app import app as flask_app


@pytest.fixture
def app():
    return flask_app
