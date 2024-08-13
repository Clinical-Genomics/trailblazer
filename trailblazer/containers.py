import os
from dependency_injector import containers, providers

from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.clients.google_api_client.google_api_client import GoogleAPIClient
from trailblazer.clients.slurm_api_client.slurm_api_client import SlurmAPIClient
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.clients.tower.tower_client import TowerAPIClient
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.slurm_api_service.slurm_api_service import SlurmAPIService
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.services.tower.tower_api_service import TowerAPIService
from trailblazer.store.store import Store


class Container(containers.DeclarativeContainer):
    slurm_host: str | None = os.environ.get("ANALYSIS_HOST")
    oauth_client_id: str | None = os.environ.get("GOOGLE_CLIENT_ID")
    oauth_client_secret: str | None = os.environ.get("GOOGLE_CLIENT_SECRET")
    oauth_redirect_uri: str | None = os.environ.get("GOOGLE_REDIRECT_URI")
    google_oauth_base_url: str | None = os.environ.get("GOOGLE_OAUTH_BASE_URL")
    encryption_key: str | None = os.environ.get("ENCRYPTION_KEY")
    google_api_base_url: str | None = os.environ.get("GOOGLE_API_BASE_URL")
    slurm_jwt_token: str | None = os.environ.get("SLURM_JWT")
    slurm_user_name: str | None = os.environ.get("SLURM_USER_NAME")
    slurm_base_url: str | None = os.environ.get("SLURM_BASE_URL")
    tower_base_url: str | None = os.environ.get("TOWER_API_ENDPOINT")
    tower_access_token: str | None = os.environ.get("TOWER_ACCESS_TOKEN")
    tower_workspace_id: str | None = os.environ.get("TOWER_WORKSPACE_ID")

    google_api_client = GoogleAPIClient(google_api_base_url)

    google_oauth_client = providers.Singleton(
        GoogleOAuthClient,
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        redirect_uri=oauth_redirect_uri,
        oauth_base_url=google_oauth_base_url,
    )

    store = providers.Singleton(Store)

    if slurm_base_url and slurm_jwt_token and slurm_user_name:
        slurm_client = providers.Singleton(
            SlurmAPIClient,
            base_url=slurm_base_url,
            access_token=slurm_jwt_token,
            user_name=slurm_user_name,
        )
        slurm_service = providers.Singleton(SlurmAPIService, client=slurm_client)
    else:
        slurm_client = providers.Singleton(SlurmCLIClient, host=slurm_host)
        slurm_service = providers.Singleton(SlurmCLIService, client=slurm_client, store=store)

    tower_client = providers.Singleton(
        TowerAPIClient,
        base_url=tower_base_url,
        access_token=tower_access_token,
        workspace_id=tower_workspace_id,
    )

    tower_service = providers.Singleton(
        TowerAPIService,
        client=tower_client,
        store=store,
    )

    job_service = providers.Factory(
        JobService,
        store=store,
        slurm_service=slurm_service,
        tower_service=tower_service,
    )
    analysis_service = providers.Factory(AnalysisService, store=store, job_service=job_service)

    encryption_service = providers.Singleton(EncryptionService, secret_key=encryption_key)

    auth_service = providers.Singleton(
        AuthenticationService,
        google_oauth_client=google_oauth_client,
        google_api_client=google_api_client,
        encryption_service=encryption_service,
        store=store,
    )
