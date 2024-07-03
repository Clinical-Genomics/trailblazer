from datetime import datetime
from trailblazer.clients.slurm_api_client.dto.common import SlurmAPIJobInfo
from trailblazer.clients.slurm_api_client.dto.job_response import SlurmJobResponse
from trailblazer.constants import TrailblazerStatus
from trailblazer.services.slurm.dtos import SlurmJobInfo


def create_job_info_dto(job_response: SlurmJobResponse) -> SlurmJobInfo:
    job: SlurmAPIJobInfo = job_response.jobs[0]
    elapsed: int | None = get_job_elapsed_time(job)
    start_time: datetime | None = get_job_start_time(job)
    status: TrailblazerStatus | None = get_job_state(job)

    return SlurmJobInfo(
        slurm_id=job.job_id,
        status=status,
        name=job.name,
        started_at=start_time,
        elapsed=elapsed,
    )


def get_job_elapsed_time(job: SlurmAPIJobInfo) -> int:
    return job.accrue_time.number if job.accrue_time and job.accrue_time.set else 0


def get_job_start_time(job: SlurmAPIJobInfo) -> datetime | None:
    if job.start_time is None:
        return None
    return datetime.fromtimestamp(job.start_time.number)


def get_job_state(job: SlurmAPIJobInfo) -> TrailblazerStatus | None:
    return TrailblazerStatus[job.job_state[0]] if job.job_state else None
