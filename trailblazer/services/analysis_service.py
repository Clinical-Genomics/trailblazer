from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Query
from trailblazer.dto.analyses_request import AnalysesRequest
from trailblazer.dto.analyses_response import AnalysesResponse
from trailblazer.store.models import Analysis, Job
from trailblazer.store.store import Store

from sqlalchemy import or_, and_


class AnalysisService:
    def __init__(self, store: Store):
        self.store = store

    def get_analyses(self, query: AnalysesRequest) -> AnalysesResponse:
        analyses: Query = self.store.get_analyses_query_by_search_term_and_is_visible(
            search_term=query.search,
            is_visible=query.is_visible,
        )

        if query.sort_field:
            column = getattr(Analysis, query.sort_field)
            order_function = asc if query.sort_order == "asc" else desc
            analyses = analyses.order_by(order_function(column))

        filter_criteria = []
        for filter_key, values in query.filters.items():
            if filter_key == "comment" and values == [""]:
                filter_criteria.append(or_(Analysis.comment.is_(None), Analysis.comment == ""))
            else:
                filter_criteria.append(getattr(Analysis, filter_key).in_(values))

        if filter_criteria:
            analyses = analyses.filter(and_(*filter_criteria))

        total: int = analyses.count()
        query_page: Query = self.store.paginate_query(
            query=analyses, page=query.page, per_page=query.per_page
        )
        response_data = []

        for analysis in query_page.all():
            analysis_data = analysis.to_dict()
            analysis_data["user"] = analysis.user.to_dict() if analysis.user else None
            failed_job: Job | None = self.store.get_latest_failed_job_for_analysis(analysis.id)
            analysis_data["failed_job"] = failed_job.to_dict() if failed_job else None
            response_data.append(analysis_data)

        return AnalysesResponse(analyses=response_data, total_count=total)
