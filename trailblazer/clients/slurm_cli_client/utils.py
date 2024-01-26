from trailblazer.apps.slurm.models import SqueueJob
from trailblazer.services.slurm.dtos import JobDto


def create_job_dto(job: SqueueJob) -> JobDto:
    return JobDto(
        job_name=job.step,
        slurm_id=job.id,
        status=job.status,
        started_at=job.started_at,
        elapsed=job.time_elapsed,
    )
