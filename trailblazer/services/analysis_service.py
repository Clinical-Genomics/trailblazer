from trailblazer.dto import (
    AnalysesRequest,
    AnalysisUpdateRequest,
    AnalysesResponse,
    AnalysisResponse,
)
from trailblazer.exc import MissingAnalysis
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store


class AnalysisService:
    def __init__(self, store: Store):
        self.store = store

    def get_analyses(self, query: AnalysesRequest) -> AnalysesResponse:
        analyses, total_analysis_count = self.store.get_filtered_sorted_paginated_analyses(query)
        return self.create_analyses_response(
            analyses=analyses, total_analysis_count=total_analysis_count
        )

    def get_analysis(self, analysis_id: int) -> AnalysisResponse:
        if not (analysis := self.store.get_analysis_with_id(analysis_id)):
            raise MissingAnalysis(f"Analysis with id {analysis_id} not found")
        return self.create_analysis_response(analysis)

    def update_analysis(self, analysis_id: int, update: AnalysisUpdateRequest) -> AnalysisResponse:
        analysis: Analysis = self.store.update_analysis(
            analysis_id=analysis_id,
            comment=update.comment,
            status=update.status,
            is_visible=update.is_visible,
        )
        return self.create_analysis_response(analysis)

    def create_analysis_response(self, analysis: Analysis) -> AnalysisResponse:
        analysis_data: dict = analysis.to_dict()
        analysis_data["jobs"] = [job.to_dict() for job in analysis.jobs]
        analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
        return AnalysisResponse(**analysis_data)

    def create_analyses_response(
        self, analyses: list[Analysis], total_analysis_count: int
    ) -> AnalysesResponse:
        response_data: list[dict] = []
        for analysis in analyses:
            analysis_data = analysis.to_dict()
            analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
            failed_job: Job = self.store.get_latest_failed_job_for_analysis(analysis.id)
            analysis_data["failed_job"] = failed_job.to_dict() if failed_job else None
            response_data.append(analysis_data)
        return AnalysesResponse(analyses=response_data, total_count=total_analysis_count)
