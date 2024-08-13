from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.store.models import Job


def create_job(job_dto: SlurmJobInfo) -> Job:
    return Job(
        slurm_id=job_dto.slurm_id,
        status=job_dto.status,
        name=job_dto.name,
        started_at=job_dto.started_at,
        elapsed=job_dto.elapsed,
    )
