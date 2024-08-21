import datetime
import uuid

import pytest
from sqlalchemy.orm import Session

from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TYPES,
    WORKFLOWS,
    JobType,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Job


@pytest.fixture
def order_id_with_multiple_analyses() -> int:
    return 1


@pytest.fixture
def analysis(order_id_with_multiple_analyses) -> Analysis:
    analysis = Analysis(
        config_path="config_path",
        workflow="workflow",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.datetime.now() - datetime.timedelta(weeks=1),
        status=TrailblazerStatus.PENDING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.SLURM,
        is_visible=True,
        order_id=order_id_with_multiple_analyses,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    session.add(analysis)
    session.commit()

    analysis_job_1 = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=1,
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.datetime.now(),
        elapsed=1,
        job_type=JobType.ANALYSIS,
    )
    analysis_job_2 = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=2,
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.datetime.now(),
        elapsed=1,
        job_type=JobType.ANALYSIS,
    )
    upload_job = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=2,
        status=TrailblazerStatus.RUNNING,
        started_at=datetime.datetime.now(),
        elapsed=1,
        job_type=JobType.UPLOAD,
    )
    session.add_all([analysis_job_1, analysis_job_2, upload_job])
    session.commit()
    return analysis


@pytest.fixture
def analyses() -> list[Analysis]:
    """Analyses with different statuses, priorities, types, and workflows."""
    analyses: list[Analysis] = []
    for priority in PRIORITY_OPTIONS:
        for type in TYPES:
            for status in TrailblazerStatus.statuses():
                for workflow in WORKFLOWS:
                    analysis = Analysis(
                        config_path="config_path",
                        workflow=workflow,
                        case_id="case_id",
                        out_dir="out_dir",
                        priority=priority,
                        started_at=datetime.datetime.now(),
                        status=status,
                        ticket_id=str(uuid.uuid4()),
                        type=type,
                        workflow_manager=WorkflowManager.SLURM,
                        is_visible=True,
                        order_id=len(analyses),
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
        workflow="workflow",
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
