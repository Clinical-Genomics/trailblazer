from abc import ABC, abstractmethod

from trailblazer.constants import TrailblazerStatus

class SlurmService(ABC):

    @abstractmethod
    def cancel_job(self, job_id: str) -> None:
        pass

    @abstractmethod
    def get_progress(self, job_ids: list[str]) -> float:
        pass
    
    @abstractmethod
    def get_status(self, job_ids: list[str]) -> TrailblazerStatus:
        pass