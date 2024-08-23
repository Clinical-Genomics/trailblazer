from trailblazer.apps.slurm.models import SqueueJob, SqueueResult
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.clients.slurm_cli_client.utils import create_job_info_dto
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_api_service.mappers import create_job
from trailblazer.services.slurm.slurm_service import SlurmService
from trailblazer.services.slurm.utils import get_slurm_job_ids
from trailblazer.store.models import Analysis
from trailblazer.store.store import Store


class SlurmCLIService(SlurmService):
    def __init__(self, client: SlurmCLIClient, store: Store):
        self.client = client
        self.store = store

    def get_job(self, job_id: int) -> SlurmJobInfo:
        queue: SqueueResult = self.client.get_slurm_queue([job_id])
        job: SqueueJob = queue.jobs[0]
        return create_job_info_dto(job)

    def update_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        job_ids: list[int] = get_slurm_job_ids(analysis.config_path)
        queue: SqueueResult = self.client.get_slurm_queue(job_ids)
        dtos = [create_job_info_dto(job) for job in queue.jobs]
        jobs = [create_job(dto) for dto in dtos]
        self.store.replace_jobs(analysis_id=analysis_id, jobs=jobs)

    def cancel_jobs(self, analysis_id: int) -> None:
        analysis: Analysis = self.store.get_analysis_with_id(analysis_id)
        job_ids: list[int] = get_slurm_job_ids(analysis.config_path)
        for job_id in job_ids:
            self.client.cancel_job(job_id)
        self.update_jobs(analysis_id)
