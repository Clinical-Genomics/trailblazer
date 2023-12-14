import datetime
from typing import Generator
from unittest.mock import patch
from flask import Flask
from flask.testing import FlaskClient
import pytest
from sqlalchemy.orm import Session

from trailblazer.server.app import app
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis
from trailblazer.store.store import Store
from trailblazer.constants import PRIORITY_OPTIONS, TYPES, TrailblazerStatus, WorkflowManager


@pytest.fixture
def flask_app(store: Store):
    yield app


@pytest.fixture
def client(flask_app: Flask) -> Generator[FlaskClient, None, None]:
    # Bypass authentication
    with patch.object(flask_app, "before_request_funcs", new={}):
        yield flask_app.test_client()


@pytest.fixture
def analysis() -> Analysis:
    analysis = Analysis(
        config_path="config_path",
        data_analysis="data_analysis",
        family="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.datetime.now(),
        status=TrailblazerStatus.PENDING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.SLURM,
        is_visible=True,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def non_existing_analysis_id() -> str:
    return "00"
