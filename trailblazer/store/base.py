from dataclasses import dataclass
from typing import Type

from sqlalchemy import func
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

    def filter_analyses_by_request(self, request: AnalysesRequest) -> Query:
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
            AnalysisFilter.SORTING,
        ]
        return apply_analysis_filter(
            filter_functions=filters,
            analyses=self.get_query(Analysis),
            has_comment=request.has_comment,
            order_id=request.order_id,
            priorities=request.priority,
            statuses=request.status,
            types=request.type,
            case_id=request.case_id,
            workflow=request.workflow,
            search_term=request.search,
            is_visible=not request.search,
            sort_field=request.sort_field,
            sort_order=request.sort_order,
        )

    def paginate_analyses(self, analyses: Query, query: AnalysesRequest) -> Query:
        return apply_analysis_filter(
            filter_functions=[AnalysisFilter.PAGINATION],
            analyses=analyses,
            page=query.page,
            page_size=query.page_size,
        )

    def get_analyses(self, request: AnalysesRequest) -> tuple[list[Analysis], int]:
        analyses: Query = self.filter_analyses_by_request(request)
        total_count: int = analyses.count()
        page: Query = self.paginate_analyses(analyses=analyses, query=request)
        return page.all(), total_count
