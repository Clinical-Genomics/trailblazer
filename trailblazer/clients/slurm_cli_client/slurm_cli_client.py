from trailblazer.apps.slurm.api import cancel_slurm_job
from trailblazer.apps.slurm.models import SqueueResult
from trailblazer.clients.slurm_cli_client.utils import get_slurm_squeue_output, parse_slurm_queue


class SlurmCLIClient:
    def __init__(self, slurm_host: str):
        self.host = slurm_host

    def cancel_job(self, job_id: str):
        cancel_slurm_job(slurm_id=job_id, analysis_host=self.host)

    def get_queue(self, job_ids: str) -> SqueueResult:
        output: str = get_slurm_squeue_output(job_ids=job_ids, analysis_host=self.host)
        return parse_slurm_queue(output)
