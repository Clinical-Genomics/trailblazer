from datetime import datetime
from unittest.mock import MagicMock, Mock
import pytest
from sqlalchemy.orm import Session


from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import (
    TrailblazerPriority,
    TrailblazerStatus,
    TrailblazerTypes,
    Workflow,
    WorkflowManager,
)
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis
from trailblazer.store.store import Store


@pytest.fixture
def slurm_completed_job_info() -> SlurmJobInfo:
    return SlurmJobInfo(
        slurm_id=690994,
        name="job",
        status="completed",
        elapsed=1000,
        started_at="2020-10-22T11:43:33",
    )


@pytest.fixture
def tower_service(store: Store) -> TowerAPIService:
    tower_client = TowerAPIClient(
        base_url="https://tower",
        access_token="token",
        workspace_id="workspace_id",
    )
    return TowerAPIService(client=tower_client, store=store)


@pytest.fixture
def slurm_service(slurm_completed_job_info) -> SlurmService:
    """Slurm service reporting all jobs as completed."""
    service = SlurmCLIService(client=Mock())
    service.get_job = Mock(return_value=slurm_completed_job_info)
    service.update_jobs = Mock(return_value=[slurm_completed_job_info])
    return service


@pytest.fixture
def job_service(
    store: Store,
    slurm_service: SlurmService,
    tower_service: TowerAPIService,
    slurm_job_ids,
    mocker,
) -> JobService:
    mocker.patch(
        "trailblazer.services.job_service.job_service.get_slurm_job_ids", return_value=slurm_job_ids
    )
    return JobService(store=store, slurm_service=slurm_service, tower_service=tower_service)


@pytest.fixture
def job_service_mock():
    return MagicMock(spec=JobService)


@pytest.fixture
def running_analysis(analysis_store: Store) -> Analysis:
    analysis = Analysis(
        config_path="config_path",
        workflow=Workflow.BALSAMIC,
        case_id="case_id",
        out_dir="out_dir",
        order_id=1,
        priority=TrailblazerPriority.NORMAL,
        started_at=datetime.now(),
        status=TrailblazerStatus.RUNNING,
        ticket_id="ticket",
        type=TrailblazerTypes.WGS,
        workflow_manager=WorkflowManager.SLURM,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def analysis_service(analysis_store: Store, job_service_mock: JobService) -> AnalysisService:
    return AnalysisService(store=analysis_store, job_service=job_service_mock)
