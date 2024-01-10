import datetime
from typing import Generator
from unittest.mock import patch
import uuid

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from trailblazer.constants import (
    PIPELINES,
    PRIORITY_OPTIONS,
    TYPES,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.server.app import app
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store


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
        case_id="case_id",
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
def analyses() -> list[Analysis]:
    """Analyses with different statuses, priorities, types, and pipelines."""
    analyses: list[Analysis] = []
    for priority in PRIORITY_OPTIONS:
        for type in TYPES:
            for status in TrailblazerStatus.statuses():
                for pipeline in PIPELINES:
                    analysis = Analysis(
                        config_path="config_path",
                        data_analysis=pipeline,
                        case_id="case_id",
                        out_dir="out_dir",
                        priority=priority,
                        started_at=datetime.datetime.now(),
                        status=status,
                        ticket_id=str(uuid.uuid4()),
                        type=type,
                        workflow_manager=WorkflowManager.SLURM,
                        is_visible=True,
                    )
                    analyses.append(analysis)
                analysis.comment = "comment"  # Ensure some analyses have a comment
    session: Session = get_session()
    session.add_all(analyses)
    return analyses


@pytest.fixture
def analysis_with_failed_job() -> Analysis:
    analysis = Analysis(
        config_path="config_path",
        data_analysis="data_analysis",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.datetime.now(),
        status=TrailblazerStatus.FAILED,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.SLURM,
        is_visible=True,
    )

    failed_job = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=1,
        status=TrailblazerStatus.FAILED,
        started_at=datetime.datetime.now(),
        elapsed=1,
    )
    running_job = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=1,
        status=TrailblazerStatus.RUNNING,
        started_at=datetime.datetime.now(),
        elapsed=1,
    )
    analysis.jobs.append(failed_job)
    analysis.jobs.append(running_job)
    session = get_session()
    session.add_all([analysis, failed_job, running_job])
    session.commit()


@pytest.fixture
def non_existing_analysis_id() -> str:
    return "00"
