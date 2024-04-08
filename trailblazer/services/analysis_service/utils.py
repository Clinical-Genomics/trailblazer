from trailblazer.constants import TrailblazerStatus
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.analysis_response import AnalysisResponse
from trailblazer.dto.summaries_response import Summary
from trailblazer.store.models import Analysis


def get_status_counts(analyses: list[Analysis]) -> dict[TrailblazerStatus, int]:
    """Returns the amount of analyses with each status."""
    delivered: int = 0
    status_counts: dict = {status: 0 for status in TrailblazerStatus}
    for analysis in analyses:
        if analysis.delivery:
            delivered += 1
        else:
            status_counts[analysis.status] += 1
    status_counts["delivered"] = delivered
    return status_counts


def create_summary(analyses: list[Analysis], order_id: int) -> Summary:
    total: int = len(analyses)
    status_counts: dict[TrailblazerStatus, int] = get_status_counts(analyses)
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
