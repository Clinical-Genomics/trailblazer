from trailblazer.dto import AnalysisResponse, FailedJobsResponse
from trailblazer.dto.analyses_response import AnalysesResponse, UpdateAnalysesResponse
from trailblazer.dto.job_response import JobResponse
from trailblazer.store.models import Analysis, Job


def create_failed_jobs_response(failed_job_statistics: list[dict]) -> FailedJobsResponse:
    return FailedJobsResponse(jobs=failed_job_statistics)


def create_analysis_response(analysis: Analysis) -> AnalysisResponse:
    analysis_data: dict = analysis.to_dict()
    analysis_data["jobs"] = [job.to_dict() for job in analysis.analysis_jobs]
    analysis_data["upload_jobs"] = [job.to_dict() for job in analysis.upload_jobs]
    analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
    return AnalysisResponse.model_validate(analysis_data)


def create_job_response(job: Job) -> JobResponse:
    return JobResponse(
        slurm_id=job.slurm_id, analysis_id=job.analysis_id, status=job.status, id=job.id
    )


def create_update_analyses_response(analyses: list[Analysis]) -> UpdateAnalysesResponse:
    response_data: list[dict] = []
    for analysis in analyses:
        analysis_data = analysis.to_dict()
        response_data.append(analysis_data)
    return UpdateAnalysesResponse(analyses=response_data)
