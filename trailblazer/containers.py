import os
from dependency_injector import containers, providers

from trailblazer.clients.authentication.keycloak_client import KeycloakClient
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
from trailblazer.services.user_service.service import UserService

from trailblazer.store.store import Store


class Container(containers.DeclarativeContainer):
    slurm_host: str | None = os.environ.get("ANALYSIS_HOST")
    encryption_key: str | None = os.environ.get("ENCRYPTION_KEY")
    slurm_jwt_token: str | None = os.environ.get("SLURM_JWT")
    slurm_user_name: str | None = os.environ.get("SLURM_USER_NAME")
    slurm_base_url: str | None = os.environ.get("SLURM_BASE_URL")
    tower_base_url: str | None = os.environ.get("TOWER_API_ENDPOINT")
    tower_access_token: str | None = os.environ.get("TOWER_ACCESS_TOKEN")
    tower_workspace_id: str | None = os.environ.get("TOWER_WORKSPACE_ID")
    keycloak_client_id: str | None = os.environ.get("KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: str | None = os.environ.get("KEYCLOAK_CLIENT_SECRET")
    keycloak_server_url: str | None = os.environ.get("KEYCLOAK_SERVER_URL")
    keycloak_realm_name: str | None = os.environ.get("KEYCLOAK_REALM_NAME")
    keycloak_redirect_uri: str | None = os.environ.get("KEYCLOAK_REDIRECT_URI", "/")

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

    user_service = providers.Singleton(
        UserService,
        store=store,
    )

    keycloak_client = providers.Singleton(
        KeycloakClient,
        client_id=keycloak_client_id,
        client_secret_key=keycloak_client_secret,
        realm_name=keycloak_realm_name,
        redirect_uri=keycloak_redirect_uri,
        server_url=keycloak_server_url,
    )

    auth_service = providers.Singleton(
        AuthenticationService,
        user_service=user_service,
        keycloak_client=keycloak_client,
        redirect_uri=keycloak_redirect_uri,
    )
