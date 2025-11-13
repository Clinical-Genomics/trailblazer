import base64
from datetime import datetime
import os
import pytest
from requests_mock import Mocker


from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import (
    TrailblazerStatus,
)
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService

from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.store import Store


@pytest.fixture
def upload_job_info() -> SlurmJobInfo:
    return SlurmJobInfo(
        slurm_id=123,
        name="upload",
        status=TrailblazerStatus.COMPLETED,
        started_at=datetime.now(),
        elapsed=100,
    )


@pytest.fixture
def tower_service(analysis_store: Store) -> TowerAPIService:
    tower_client = TowerAPIClient(
        base_url="https://tower",
        access_token="token",
        workspace_id="workspace_id",
    )
    return TowerAPIService(client=tower_client, store=analysis_store)


@pytest.fixture
def slurm_service(analysis_store: Store) -> SlurmCLIService:
    slurm_client = SlurmCLIClient("host")
    return SlurmCLIService(client=slurm_client, store=analysis_store)


@pytest.fixture
def job_service(
    analysis_store: Store,
    slurm_service: SlurmCLIService,
    tower_service: TowerAPIService,
) -> JobService:
    return JobService(
        slurm_service=slurm_service,
        tower_service=tower_service,
        store=analysis_store,
    )


@pytest.fixture
def encryption_service() -> EncryptionService:
    key: bytes = os.urandom(32)
    secret_key: str = base64.b64encode(key).decode()
    return EncryptionService(secret_key)


@pytest.fixture
def mock_request():
    with Mocker() as mock:
        yield mock
