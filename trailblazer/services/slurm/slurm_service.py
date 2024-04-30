from abc import ABC, abstractmethod

from trailblazer.services.slurm.dtos import SlurmJobInfo


class SlurmService(ABC):
    @abstractmethod
    def get_job(self, job_id: int) -> SlurmJobInfo:
        pass

    @abstractmethod
    def get_jobs(self, job_ids: list[int]) -> list[SlurmJobInfo]:
        pass
