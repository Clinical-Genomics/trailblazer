from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.analysis_response import AnalysisResponse
from trailblazer.dto.summaries_response import Summary
from trailblazer.store.models import Analysis


def get_status_count(analyses: list[Analysis], status: TrailblazerStatus) -> int:
    return len([a for a in analyses if a.status == status])


def get_delivered_count(analyses: list[Analysis]) -> int:
    return len([analysis for analysis in analyses if analysis.delivery])


def create_summary(analyses: list[Analysis], order_id: int) -> Summary:
    total: int = len(analyses)
    completed: int = get_status_count(analyses=analyses, status=TrailblazerStatus.COMPLETED)
    delivered: int = get_delivered_count(analyses)
    completed -= delivered
    running: int = get_status_count(analyses=analyses, status=TrailblazerStatus.RUNNING)
    cancelled: int = get_status_count(analyses=analyses, status=TrailblazerStatus.CANCELLED)
    failed = get_status_count(analyses=analyses, status=TrailblazerStatus.FAILED)
    return Summary(
        order_id=order_id,
        total=total,
        delivered=delivered,
        running=running,
        cancelled=cancelled,
        failed=failed,
        completed=completed,
    )


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
