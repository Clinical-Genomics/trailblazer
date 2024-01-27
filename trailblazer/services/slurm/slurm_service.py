from abc import ABC, abstractmethod

from trailblazer.services.slurm.dtos import JobInfoDto


class SlurmService(ABC):
    @abstractmethod
    def get_job_info(self, job_id: str) -> JobInfoDto:
        pass
