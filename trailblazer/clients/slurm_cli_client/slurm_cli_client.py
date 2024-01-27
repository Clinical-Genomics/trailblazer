from trailblazer.apps.slurm.api import get_slurm_queue
from trailblazer.apps.slurm.models import SqueueResult, SqueueJob
from trailblazer.clients.slurm_cli_client.utils import create_job_info_dto
from trailblazer.services.slurm.dtos import JobInfoDto


class SlurmCLIClient:
    def __init__(self, host: str):
        self.host = host

    def get_job(self, job_id: str) -> JobInfoDto:
        queue: SqueueResult = get_slurm_queue(job_ids=[job_id], analysis_host=self.host)
        job: SqueueJob = queue.jobs[0]
        return create_job_info_dto(job)
