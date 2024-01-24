from abc import ABC, abstractmethod


class SlurmService(ABC):
    @abstractmethod
    def cancel_job(self, job_id: str) -> None:
        pass
