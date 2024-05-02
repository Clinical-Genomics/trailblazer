import os
from dependency_injector import containers, providers

from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.clients.google_api_client.google_api_client import GoogleAPIClient
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.store.store import Store


class Container(containers.DeclarativeContainer):
    slurm_host: str | None = os.environ.get("ANALYSIS_HOST")
    oauth_client_id: str = os.environ.get("GOOGLE_CLIENT_ID")
    oauth_client_secret: str = os.environ.get("GOOGLE_CLIENT_SECRET")
    oauth_redirect_uri: str = os.environ.get("GOOGLE_REDIRECT_URI")
    google_oauth_base_url: str = os.environ.get("GOOGLE_OAUTH_BASE_URL")
    encryption_key: str = os.environ.get("ENCRYPTION_KEY")
    google_api_base_url: str = os.environ.get("GOOGLE_API_BASE_URL")

    google_api_client = GoogleAPIClient(google_api_base_url)

    google_oauth_client = providers.Singleton(
        GoogleOAuthClient,
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        redirect_uri=oauth_redirect_uri,
        oauth_base_url=google_oauth_base_url,
    )

    store = providers.Singleton(Store)
    slurm_client = providers.Singleton(SlurmCLIClient, host=slurm_host)
    slurm_service = providers.Singleton(SlurmCLIService, client=slurm_client)

    job_service = providers.Factory(JobService, store=store, slurm_service=slurm_service)
    analysis_service = providers.Factory(AnalysisService, store=store)

    encryption_service = providers.Singleton(EncryptionService, secret_key=encryption_key)

    auth_service = providers.Singleton(
        AuthenticationService,
        google_oauth_client=google_oauth_client,
        google_api_client=google_api_client,
        encryption_service=encryption_service,
        store=store,
    )
