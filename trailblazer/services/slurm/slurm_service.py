from abc import ABC, abstractmethod

from trailblazer.services.slurm.dtos import SlurmJobInfo


class SlurmService(ABC):
    @abstractmethod
    def get_job(self, job_id: int) -> SlurmJobInfo:
        pass

    @abstractmethod
    def update_jobs(self, analysis_id: int) -> None:
        pass

    @abstractmethod
    def cancel_jobs(self, analysis_id: int) -> None:
        pass
