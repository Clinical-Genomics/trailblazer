import os
from dependency_injector import containers, providers

from trailblazer.clients.authentication_client.google_oauth_client import GoogleOAuthClient
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.services.analysis_service.analysis_service import AnalysisService
from trailblazer.services.authentication_service.authentication_service import AuthenticationService
from trailblazer.services.encryption_service.encryption_service import EncryptionService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.store.store import Store


class Container(containers.DeclarativeContainer):
    slurm_host: str | None = os.environ.get("ANALYSIS_HOST")
    google_client_id: str = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret: str = os.environ.get("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = os.environ.get("GOOGLE_REDIRECT_URI")

    oauth_client = providers.Singleton(GoogleOAuthClient)

    store = providers.Singleton(Store)
    slurm_client = providers.Singleton(SlurmCLIClient, host=slurm_host)
    slurm_service = providers.Singleton(SlurmCLIService, client=slurm_client)

    job_service = providers.Factory(JobService, store=store, slurm_service=slurm_service)
    analysis_service = providers.Factory(AnalysisService, store=store)

    encryption_service = providers.Singleton(EncryptionService)
    authentication_service = providers.Singleton(
        AuthenticationService,
        authentication_client=oauth_client,
        encryption_service=encryption_service,
        store=store,
    )
