import base64
from datetime import datetime
import os
import pytest
import requests_mock

from trailblazer.clients.authentication_client.google_oauth_client import OAuthClient
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.constants import TrailblazerStatus
from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService

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
def job_service(analysis_store: Store):
    slurm_client = SlurmCLIClient("host")
    slurm_service = SlurmCLIService(slurm_client)
    return JobService(slurm_service=slurm_service, store=analysis_store)


@pytest.fixture
def encryption_service() -> EncryptionService:
    key: bytes = os.urandom(32)
    secret_key: str = base64.b64encode(key).decode()
    return EncryptionService(secret_key)


@pytest.fixture
def oauth_client() -> OAuthClient:
    return OAuthClient(
        client_id="client_id",
        client_secret="client_secret",
        redirect_uri="redirect_uri",
    )


@pytest.fixture
def authentication_service(
    encryption_service: EncryptionService,
    oauth_client: OAuthClient,
    store: Store,
) -> AuthenticationService:
    return AuthenticationService(
        encryption_service=encryption_service,
        store=store,
        oauth_client=oauth_client,
    )


@pytest.fixture
def oauth_response() -> dict:
    return {
        "access_token": "access_token",
        "token_type": "token_type",
        "expires_in": 3600,
        "refresh_token": "refresh_token",
        "scope": "scope",
    }


@pytest.fixture
def mock_request():
    with requests_mock.Mocker() as mock:
        yield mock
