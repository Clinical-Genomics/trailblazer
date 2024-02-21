from trailblazer.dto.job_response import JobResponse
from trailblazer.store.models import Job


def create_job_response(job: Job) -> JobResponse:
    return JobResponse(
        slurm_id=job.slurm_id, analysis_id=job.analysis_id, status=job.status, id=job.id
    )
