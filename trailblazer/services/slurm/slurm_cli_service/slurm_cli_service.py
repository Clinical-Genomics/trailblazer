from trailblazer.apps.slurm.models import SqueueJob, SqueueResult
from trailblazer.clients.slurm_cli_client.slurm_cli_client import SlurmCLIClient
from trailblazer.clients.slurm_cli_client.utils import create_job_info_dto
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmCLIService(SlurmService):
    def __init__(self, client: SlurmCLIClient):
        self.client = client

    def get_job(self, job_id: int) -> SlurmJobInfo:
        queue: SqueueResult = self.client.get_slurm_queue([job_id])
        job: SqueueJob = queue.jobs[0]
        return create_job_info_dto(job)

    def get_jobs(self, job_ids: list[int]) -> list[SlurmJobInfo]:
        queue: SqueueResult = self.client.get_slurm_queue(job_ids)
        return [create_job_info_dto(job) for job in queue.jobs]
