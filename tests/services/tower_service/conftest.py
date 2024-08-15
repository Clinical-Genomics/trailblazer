from datetime import datetime, timedelta
from pathlib import Path
import pytest
from sqlalchemy.orm import Session

from trailblazer.clients.tower.models import TaskWrapper, TowerTask, TowerTasksResponse
from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TYPES,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis
from trailblazer.store.store import Store


@pytest.fixture
def tower_analysis(analysis_store: Store, tmp_path) -> Analysis:
    case_id = "case_id"
    config_path: Path = tmp_path / "tower.yaml"
    config_path.write_text(f"case_id: {case_id}")

    analysis = Analysis(
        config_path=str(config_path),
        workflow="workflow",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.now() - timedelta(weeks=1),
        status=TrailblazerStatus.RUNNING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.TOWER,
        is_visible=True,
        order_id=1,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def tower_tasks_response():
    task = TowerTask(
        process="example_process",
        name="example_task",
        status="COMPLETED",
        nativeId="1234",
        dateCreated=datetime.now(),
        lastUpdated=datetime.now(),
        start=datetime.now(),
        module=["example_module"],
    )

    task_wrapper = TaskWrapper(task=task)
    return TowerTasksResponse(tasks=[task_wrapper], total=1)
