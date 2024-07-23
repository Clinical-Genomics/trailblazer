from trailblazer.dto.failed_jobs_response import FailedJobsResponse
from trailblazer.dto.job_response import JobResponse
from trailblazer.services.slurm.dtos import SlurmJobInfo
from trailblazer.services.tower.dtos import TowerJobInfo
from trailblazer.store.models import Job


def create_job_response(job: Job) -> JobResponse:
    return JobResponse(
        slurm_id=job.slurm_id, analysis_id=job.analysis_id, status=job.status, id=job.id
    )


def create_failed_jobs_response(failed_job_statistics: list[dict]) -> FailedJobsResponse:
    return FailedJobsResponse(jobs=failed_job_statistics)


def slurm_info_to_job(slurm_job_info: SlurmJobInfo) -> Job:
    return Job(
        slurm_id=slurm_job_info.slurm_id,
        name=slurm_job_info.name,
        status=slurm_job_info.status,
        elapsed=slurm_job_info.elapsed,
        started_at=slurm_job_info.started_at,
    )


def tower_info_to_job(tower_job_info: TowerJobInfo) -> Job:
    return Job(
        slurm_id=tower_job_info.job_id,
        name=tower_job_info.name,
        status=tower_job_info.status,
        elapsed=tower_job_info.elapsed,
        started_at=tower_job_info.started_at,
    )
