from trailblazer.apps.slurm.api import cancel_slurm_job


class SlurmCLIClient:
    def __init__(self, slurm_host: str):
        self.host = slurm_host

    def cancel_job(self, job_id: str):
        cancel_slurm_job(slurm_id=job_id, analysis_host=self.host)
