from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock
import pytest
from sqlalchemy.orm import Session


from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TYPES,
    JobType,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Job
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
    tower_client = MagicMock(spec=TowerAPIClient)
    return TowerAPIService(client=tower_client, store=store)


@pytest.fixture
def slurm_service(slurm_completed_job_info) -> SlurmService:
    """Slurm service reporting all jobs as completed."""
    service = SlurmCLIService(client=Mock(), store=Mock())
    service.get_job = Mock(return_value=slurm_completed_job_info)
    service.update_jobs = Mock(return_value=[slurm_completed_job_info])
    return service


@pytest.fixture
def job_service(
    analysis_store: Store,
    slurm_service: SlurmService,
    tower_service: TowerAPIService,
) -> JobService:
    return JobService(
        store=analysis_store,
        slurm_service=slurm_service,
        tower_service=tower_service,
    )


@pytest.fixture
def job_service_mock():
    return MagicMock(spec=JobService)


@pytest.fixture
def analysis(analysis_store: Store) -> Analysis:
    analysis = Analysis(
        config_path="config_path",
        workflow="workflow",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.now() - timedelta(weeks=1),
        status=TrailblazerStatus.RUNNING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.SLURM,
        is_visible=True,
        order_id=1,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def analysis_with_running_jobs(analysis_store: Store, analysis: Analysis) -> Analysis:
    analysis_job_1 = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=1,
        status=TrailblazerStatus.RUNNING,
        started_at=datetime.now(),
        elapsed=100,
        job_type=JobType.ANALYSIS,
    )
    analysis_job_2 = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=2,
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.now(),
        elapsed=1,
        job_type=JobType.ANALYSIS,
    )
    session: Session = get_session()
    session.add_all([analysis_job_1, analysis_job_2])
    session.commit()
    return analysis


@pytest.fixture
def analysis_with_completed_jobs(analysis_store: Store, analysis: Analysis) -> Analysis:
    analysis_job_1 = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=1,
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.now(),
        elapsed=100,
        job_type=JobType.ANALYSIS,
    )
    analysis_job_2 = Job(
        analysis_id=analysis.id,
        name="name",
        slurm_id=2,
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.now(),
        elapsed=1,
        job_type=JobType.ANALYSIS,
    )
    session: Session = get_session()
    session.add_all([analysis_job_1, analysis_job_2])
    session.commit()
    return analysis


@pytest.fixture
def analysis_without_jobs(analysis_store: Store):
    analysis = Analysis(
        config_path="config_path",
        workflow="workflow",
        case_id="case_id",
        out_dir="out_dir",
        priority=PRIORITY_OPTIONS[0],
        started_at=datetime.now() - timedelta(weeks=1),
        status=TrailblazerStatus.RUNNING,
        ticket_id="ticket_id",
        type=TYPES[0],
        workflow_manager=WorkflowManager.SLURM,
        is_visible=True,
        order_id=1,
    )
    session: Session = get_session()
    session.add(analysis)
    session.commit()
    return analysis


@pytest.fixture
def analysis_service(analysis_store: Store, job_service_mock: JobService) -> AnalysisService:
    return AnalysisService(store=analysis_store, job_service=job_service_mock)
