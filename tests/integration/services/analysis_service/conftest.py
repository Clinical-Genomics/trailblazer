from unittest.mock import MagicMock
import pytest

from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmAPIClient
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.job_service.job_service import JobService
from trailblazer.services.slurm.slurm_api_service.slurm_api_service import SlurmAPIService
from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.store import Store


@pytest.fixture
def analysis_service(analysis_store: Store) -> AnalysisService:
    slurm_client = MagicMock(spec=SlurmAPIClient)
    tower_client = MagicMock(spec=TowerAPIClient)

    slurm_service = SlurmAPIService(store=analysis_store, client=slurm_client)
    tower_service = TowerAPIService(store=analysis_store, client=tower_client)

    job_service = JobService(
        store=analysis_store,
        slurm_service=slurm_service,
        tower_service=tower_service,
    )

    return AnalysisService(
        store=analysis_store,
        job_service=job_service,
    )
