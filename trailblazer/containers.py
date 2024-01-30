import os
from dependency_injector import containers, providers

from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.services.analysis_service import AnalysisService
from trailblazer.services.job_service import JobService
from trailblazer.services.slurm.slurm_cli_service.slurm_cli_service import SlurmCLIService
from trailblazer.store.store import Store


class Container(containers.DeclarativeContainer):
    slurm_host: str | None = os.environ.get("ANALYSIS_HOST")

    store = providers.Singleton(Store)
    slurm_client = providers.Singleton(SlurmCLIClient, host=slurm_host)
    slurm_service = providers.Singleton(SlurmCLIService, client=slurm_client)

    job_service = providers.Factory(JobService, store=store, slurm_service=slurm_service)
    analysis_service = providers.Factory(AnalysisService, store=store)
