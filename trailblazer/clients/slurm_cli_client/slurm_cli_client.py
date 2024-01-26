from trailblazer.services.slurm.dtos import JobDto


class SlurmCLIClient:
    def __init__(self, host: str):
        self.host = host

    def get_job(self, job_id: str) -> JobDto:
        pass
