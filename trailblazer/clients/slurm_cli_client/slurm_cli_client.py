from trailblazer.apps.slurm.api import cancel_slurm_job, get_slurm_queue
from trailblazer.apps.slurm.models import SqueueResult


class SlurmCLIClient:
    def __init__(self, host: str):
        self.host = host

    def get_slurm_queue(self, job_ids: list[int]) -> SqueueResult:
        return get_slurm_queue(job_ids=job_ids, analysis_host=self.host)

    def cancel_job(self, job_id: int) -> None:
        cancel_slurm_job(slurm_id=job_id, analysis_host=self.host)
