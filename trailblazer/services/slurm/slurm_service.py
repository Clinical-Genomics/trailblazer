from abc import ABC, abstractmethod

from trailblazer.constants import TrailblazerStatus


class SlurmService(ABC):
    @abstractmethod
    def get_job(self, job_id: str) -> None:
        pass
