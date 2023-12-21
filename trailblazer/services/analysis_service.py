from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Query
from trailblazer.dto.analyses_request import AnalysisRequest
from trailblazer.dto.analyses_response import AnalysisResponse
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store

from sqlalchemy import or_, and_


class AnalysisService:
    def __init__(self, store: Store):
        self.store = store

    def get_analyses(self, query: AnalysisRequest) -> AnalysisResponse:
        analyses, count = self.store.get_filtered_sorted_paginated_analyses(query)
        response: AnalysisResponse = self._format_response(analyses=analyses, total=count)
        return response

    def _format_response(self, analyses: list[Analysis], total: int) -> AnalysisResponse:
        response_data = []
        for analysis in analyses:
            analysis_data = analysis.to_dict()
            analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
            failed_job = self.store.get_latest_failed_job_for_analysis(analysis.id)
            analysis_data["failed_job"] = failed_job.to_dict() if failed_job else None
            response_data.append(analysis_data)
        return AnalysisResponse(analyses=response_data, total_count=total)
