import subprocess
from trailblazer.services.slurm.slurm_service import SlurmService


class SlurmCLIService(SlurmService):
    def __init__(self, analysis_host: str | None = None):
        self.analysis_host = analysis_host

    def cancel_job(self, job_id: str) -> None:
        scancel_commands: list[str] = ["scancel", job_id]
        if self.analysis_host:
            scancel_commands = ["ssh", self.analysis_host] + scancel_commands
        subprocess.Popen(scancel_commands)
