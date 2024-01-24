from trailblazer.clients.slurm_cli_client.utils import cancel_slurm_job


class SlurmCLIClient:
    def __init__(self, analysis_host: str):
        self.analysis_host = analysis_host

    def cancel_job(self, job_id: str) -> None:
        cancel_slurm_job(slurm_id=job_id, analysis_host=self.analysis_host)
