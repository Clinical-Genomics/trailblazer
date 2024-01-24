from trailblazer.services.slurm.cli.utils import cancel_slurm_job
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmCLIService(SlurmService):
    def __init__(self, analysis_host: str | None = None):
        self.analysis_host = analysis_host

    def cancel_job(self, job_id: str) -> None:
        cancel_slurm_job(slurm_id=job_id, analysis_host=self.analysis_host)
