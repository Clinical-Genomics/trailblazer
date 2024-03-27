from trailblazer.constants import Workflow
from trailblazer.dto import (
    AnalysesRequest,
    AnalysesResponse,
    AnalysisResponse,
    AnalysisUpdateRequest,
    CreateAnalysisRequest,
)
from trailblazer.dto.analyses_response import UpdateAnalysesResponse
from trailblazer.dto.summaries_request import SummariesRequest
from trailblazer.dto.summaries_response import SummariesResponse, Summary
from trailblazer.dto.update_analyses import UpdateAnalyses
from trailblazer.exc import MissingAnalysis
from trailblazer.services.analysis_service.utils import (
    create_analysis_response,
    create_summary,
    create_update_analyses_response,
)
from trailblazer.store.models import Analysis, Job, User
from trailblazer.store.store import Store


class AnalysisService:
    def __init__(self, store: Store):
        self.store = store

    def get_analyses(self, request: AnalysesRequest) -> AnalysesResponse:
        analyses, total_count = self.store.get_paginated_analyses(request)
        return self.create_analyses_response(analyses=analyses, total_count=total_count)

    def get_analysis(self, analysis_id: int) -> AnalysisResponse:
        if not (analysis := self.store.get_analysis_with_id(analysis_id)):
            raise MissingAnalysis(f"Analysis with id: {analysis_id} not found")
        return create_analysis_response(analysis)

    def update_analysis(
        self, analysis_id: int, update: AnalysisUpdateRequest, user: User | None = None
    ) -> AnalysisResponse:
        analysis: Analysis = self.store.update_analysis(
            analysis_id=analysis_id,
            comment=update.comment,
            is_delivered=update.is_delivered,
            status=update.status,
            is_visible=update.is_visible,
            user=user,
        )
        return create_analysis_response(analysis)

    def update_analyses(
        self, data: UpdateAnalyses, user: User | None = None
    ) -> UpdateAnalysesResponse:
        analyses: list[Analysis] = self.store.update_analyses(data=data, user=user)
        return create_update_analyses_response(analyses)

    def add_pending_analysis(self, request_data: CreateAnalysisRequest) -> AnalysisResponse:
        analysis: Analysis = self.store.add_pending_analysis(request_data)
        return create_analysis_response(analysis)

    def create_analyses_response(
        self, analyses: list[Analysis], total_count: int
    ) -> AnalysesResponse:
        response_data: list[dict] = []
        for analysis in analyses:
            analysis_data = analysis.to_dict()
            failed_job: Job = self.store.get_latest_failed_job_for_analysis(analysis.id)
            analysis_data["failed_job"] = failed_job.to_dict() if failed_job else None
            response_data.append(analysis_data)
        return AnalysesResponse(analyses=response_data, total_count=total_count)

    def update_ongoing_analyses(self) -> None:
        self.store.update_ongoing_analyses()

    def get_summaries(self, request_data: SummariesRequest) -> SummariesResponse:
        summaries: list[Summary] = []
        for order_id in request_data.order_ids:
            analyses: list[Analysis] = self.store.get_latest_analyses_for_order(order_id)
            analyses_without_rsync: list[Analysis] = [
                analysis for analysis in analyses if analysis.workflow != Workflow.RSYNC
            ]
            summary: Summary = create_summary(analyses=analyses_without_rsync, order_id=order_id)
            summaries.append(summary)
        return SummariesResponse(summaries=summaries)
