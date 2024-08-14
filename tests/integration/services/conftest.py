import base64
from datetime import datetime, timedelta
import os
import pytest
from requests_mock import Mocker
from sqlalchemy.orm import Session


from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.clients.google_api_client.google_api_client import GoogleAPIClient
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.constants import (
    PRIORITY_OPTIONS,
    TYPES,
    JobType,
    TrailblazerStatus,
    WorkflowManager,
)
from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService

from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis, Job
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
def google_oauth_client(google_oauth_response: dict, mock_request: Mocker) -> GoogleOAuthClient:
    oauth_base_url = "https://oauth2.googleapis.com/token"
    mock_request.post(oauth_base_url, json=google_oauth_response)

    return GoogleOAuthClient(
        client_id="client_id",
        client_secret="client_secret",
        redirect_uri="redirect_uri",
        oauth_base_url=oauth_base_url,
    )


@pytest.fixture
def google_user_info_response(user_email: str) -> dict:
    return {"email": f"{user_email}"}


@pytest.fixture
def google_api_client(mock_request: Mocker, google_user_info_response: dict) -> GoogleAPIClient:
    base_url = "https://www.googleapis.com"
    user_info_endpoint = f"{base_url}/oauth2/v1/userinfo"
    mock_request.get(user_info_endpoint, json=google_user_info_response)
    return GoogleAPIClient("https://www.googleapis.com")


@pytest.fixture
def authentication_service(
    encryption_service: EncryptionService,
    google_oauth_client: GoogleOAuthClient,
    google_api_client: GoogleAPIClient,
    user_store: Store,
) -> AuthenticationService:
    return AuthenticationService(
        encryption_service=encryption_service,
        store=user_store,
        google_oauth_client=google_oauth_client,
        google_api_client=google_api_client,
    )


@pytest.fixture
def google_oauth_response() -> dict:
    return {
        "access_token": "access_token",
        "token_type": "token_type",
        "expires_in": 3600,
        "refresh_token": "refresh_token",
        "scope": "scope",
        "id_token": "id_token",
    }


@pytest.fixture
def mock_request():
    with Mocker() as mock:
        yield mock
