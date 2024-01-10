from trailblazer.dto import AnalysisResponse, FailedJobsResponse
from trailblazer.store.models import Analysis


def create_jobs_response(failed_job_statistics: list[dict]) -> FailedJobsResponse:
    return FailedJobsResponse(jobs=failed_job_statistics)


def create_analysis_response(analysis: Analysis) -> AnalysisResponse:
    analysis_data: dict = analysis.to_dict()
    analysis_data["jobs"] = [job.to_dict() for job in analysis.jobs]
    analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
    return AnalysisResponse.model_validate(analysis_data)
