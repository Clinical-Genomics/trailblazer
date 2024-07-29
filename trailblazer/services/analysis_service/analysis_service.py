import logging
from trailblazer.constants import TrailblazerStatus, WorkflowManager
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
    get_upload_date,
)
from trailblazer.services.job_service.job_service import JobService
from trailblazer.store.models import Analysis, Job, User
from trailblazer.store.store import Store

LOG = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, store: Store, job_service: JobService):
        self.store = store
        self.job_service = job_service

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

    def update_uploading_analyses(self):
        self.job_service.update_upload_jobs()
        analyses: list[Analysis] = self.store.get_analyses_being_uploaded()
        for analysis in analyses:
            if upload_date := get_upload_date(analysis):
                self.store.update_analysis_upload_date(
                    analysis_id=analysis.id, uploaded_at=upload_date
                )

    def update_ongoing_analyses(self) -> None:
        analyses: list[Analysis] = self.store.get_ongoing_analyses()
        for analysis in analyses:
            try:
                self.update_analysis_meta_data(analysis)
            except Exception as error:
                self.store.update_analysis_status(analysis.id, TrailblazerStatus.ERROR)
                LOG.error(f"Failed to update analysis {analysis.id}: {error}")

    def update_analysis_meta_data(self, analysis: Analysis):
        """Update the jobs, progress and status of an analysis."""
        self.job_service.update_jobs(analysis.id)

        if analysis.workflow_manager == WorkflowManager.TOWER:
            return

        self._update_progress(analysis.id)
        self._update_status(analysis.id)

    def _update_status(self, analysis_id: int) -> None:
        status: TrailblazerStatus = self.job_service.get_analysis_status(analysis_id)
        self.store.update_analysis_status(analysis_id=analysis_id, status=status)

    def _update_progress(self, analysis_id: int) -> None:
        progress: float = self.job_service.get_analysis_progression(analysis_id)
        self.store.update_analysis_progress(analysis_id=analysis_id, progress=progress)

    def get_summaries(self, request_data: SummariesRequest) -> SummariesResponse:
        summaries: list[Summary] = []
        for order_id in request_data.order_ids:
            analyses: list[Analysis] = self.store.get_latest_analyses_for_order(order_id)
            summary: Summary = create_summary(analyses=analyses, order_id=order_id)
            summaries.append(summary)
        return SummariesResponse(summaries=summaries)
