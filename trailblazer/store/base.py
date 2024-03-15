from dataclasses import dataclass
from typing import Type

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Query, Session

from trailblazer.dto import AnalysesRequest
from trailblazer.store.database import get_session
from trailblazer.store.filters.analyses_filters import AnalysisFilter, apply_analysis_filter
from trailblazer.store.models import Analysis, Job, Model


@dataclass
class BaseHandler:
    """All models in one base class."""

    def get_query(self, table: Type[Model]) -> Query:
        """Return a query for the given table."""
        session: Session = get_session()
        return session.query(table)

    def get_job_query_with_name_and_count_labels(self) -> Query:
        """Return a Job query with a name label and a count with a label."""
        session: Session = get_session()
        return session.query(
            Job.name.label("name"),
            func.count(Job.id).label("count"),
        )

    def filter_analyses_by_request(self, analyses_request: AnalysesRequest) -> Query:
        """Apply filtering and sorting of analyses based on request."""
        filters: list[AnalysisFilter] = [
            AnalysisFilter.BY_WORKFLOW,
            AnalysisFilter.BY_HAS_COMMENT,
            AnalysisFilter.BY_ORDER_ID,
            AnalysisFilter.BY_PRIORITIES,
            AnalysisFilter.BY_STATUSES,
            AnalysisFilter.BY_TYPES,
            AnalysisFilter.BY_CASE_ID,
            AnalysisFilter.BY_SEARCH_TERM,
            AnalysisFilter.BY_IS_VISIBLE,
        ]
        return apply_analysis_filter(
            filter_functions=filters,
            analyses=self.get_query(Analysis),
            has_comment=analyses_request.has_comment,
            order_id=analyses_request.order_id,
            priorities=analyses_request.priority,
            statuses=analyses_request.status,
            types=analyses_request.type,
            case_id=analyses_request.case_id,
            workflow=analyses_request.workflow,
            search_term=analyses_request.search,
        )

    def sort_analyses(self, analyses: Query, query: AnalysesRequest) -> Query:
        if query.sort_field:
            column = getattr(Analysis, query.sort_field)
            if query.sort_order == "asc":
                analyses = analyses.order_by(asc(column))
            else:
                analyses = analyses.order_by(desc(column))
        return analyses

    def paginate_analyses(self, analyses: Query, query: AnalysesRequest) -> Query:
        return analyses.limit(query.page_size).offset((query.page - 1) * query.page_size)

    def get_analyses(self, request: AnalysesRequest) -> tuple[list[Analysis], int]:
        analyses = self.filter_analyses_by_request(request)
        analyses = self.sort_analyses(analyses=analyses, query=request)
        total_count: int = analyses.count()
        query_page: Query = self.paginate_analyses(analyses=analyses, query=request)
        return query_page.all(), total_count
