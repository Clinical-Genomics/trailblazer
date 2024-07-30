from datetime import datetime, timedelta
from trailblazer.constants import SlurmJobStatus, TrailblazerStatus, Workflow
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.analysis_response import AnalysisResponse
from trailblazer.dto.summaries_response import StatusSummary, Summary
from trailblazer.store.models import Analysis
from trailblazer.store.models import Job


def get_status_counts(analyses: list[Analysis]) -> dict[TrailblazerStatus, StatusSummary]:
    """Returns the number of analyses with each status."""
    delivered: int = 0
    delivered_cases: list[str] = []
    status_counts: dict = {status: StatusSummary() for status in TrailblazerStatus}
    for analysis in analyses:
        if analysis.delivery:
            delivered += 1
            delivered_cases.append(analysis.case_id)
        else:
            status_counts[analysis.status].count += 1
            status_counts[analysis.status].case_ids.append(analysis.case_id)
    status_counts["delivered"] = StatusSummary(count=delivered, case_ids=delivered_cases)
    return status_counts


def create_summary(analyses: list[Analysis], order_id: int) -> Summary:
    total: int = len(analyses)
    status_counts: dict[TrailblazerStatus, StatusSummary] = get_status_counts(analyses)
    return Summary(order_id=order_id, total=total, **status_counts)


def create_analysis_response(analysis: Analysis) -> AnalysisResponse:
    analysis_data: dict = analysis.to_dict()
    analysis_data["jobs"] = [job.to_dict() for job in analysis.analysis_jobs]
    analysis_data["upload_jobs"] = [job.to_dict() for job in analysis.upload_jobs]
    analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
    return AnalysisResponse.model_validate(analysis_data)


def create_update_analyses_response(analyses: list[Analysis]) -> UpdateAnalysesResponse:
    response_data: list[dict] = []
    for analysis in analyses:
        analysis_data = analysis.to_dict()
        response_data.append(analysis_data)
    return UpdateAnalysesResponse(analyses=response_data)


def get_upload_date(analysis: Analysis) -> datetime | None:
    completed_job: Job | None = _get_completed_job(analysis.upload_jobs)
    if not completed_job:
        return
    return _get_completed_at_date(completed_job)


def _get_completed_job(jobs: list[Job]) -> Job | None:
    for job in jobs:
        if _is_completed_job(job):
            return job


def _is_completed_job(job: Job):
    return job.status == SlurmJobStatus.COMPLETED and job.started_at and job.elapsed is not None


def _get_completed_at_date(job: Job) -> datetime:
    return job.started_at + timedelta(seconds=job.elapsed)
