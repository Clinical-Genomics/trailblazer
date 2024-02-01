from trailblazer.apps.slurm.models import SqueueJob
from trailblazer.services.slurm.dtos import SlurmJobInfo


def create_job_info_dto(job: SqueueJob) -> SlurmJobInfo:
    return SlurmJobInfo(
        name=job.step,
        slurm_id=job.id,
        status=job.status,
        started_at=job.started_at,
        elapsed=job.time_elapsed,
    )
