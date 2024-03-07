from dataclasses import dataclass
from typing import Type

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Query, Session

from trailblazer.constants import Workflow
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

    def get_analyses_query_by_search(self, analyses: Query, search_term: str) -> Query:
        """Return analyses by search term."""
        if search_term:
            analyses: Query = apply_analysis_filter(
                filter_functions=[AnalysisFilter.BY_SEARCH_TERM],
                analyses=analyses,
                search_term=search_term,
            )
        return analyses

    def get_analyses_query_by_workflow(self, workflow: str) -> Query:
        """Return analyses by workflow."""
        analyses: Query = self.get_query(Analysis)
        # Group existing variants of balsamic
        balsamic_workflow: str = Workflow.BALSAMIC.lower()
        if workflow == balsamic_workflow:
            analyses = analyses.filter(Analysis.workflow.startswith(balsamic_workflow))
        elif workflow:
            analyses = analyses.filter(Analysis.workflow == workflow)
        return analyses

    def get_filtered_analyses(self, analyses: Query, query: AnalysesRequest) -> Query:
        filters: list[AnalysisFilter] = []
        if query.comment:
            filters.append(AnalysisFilter.BY_EMPTY_COMMENT)
        if query.order_id is not None:
            filters.append(AnalysisFilter.BY_ORDER_ID)
        if query.priority:
            filters.append(AnalysisFilter.BY_PRIORITIES)
        if query.status:
            filters.append(AnalysisFilter.BY_STATUSES)
        if query.type:
            filters.append(AnalysisFilter.BY_TYPES)
        if query.case_id:
            filters.append(AnalysisFilter.BY_CASE_ID)

        return apply_analysis_filter(
            filter_functions=filters,
            analyses=analyses,
            comment=query.comment,
            order_id=query.order_id,
            priorities=query.priority,
            statuses=query.status,
            types=query.type,
            case_id=query.case_id,
        )

    def get_visible_analyses(self, analyses: Query) -> Query:
        return apply_analysis_filter(
            filter_functions=[AnalysisFilter.BY_IS_VISIBLE],
            analyses=analyses,
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

    def get_filtered_sorted_paginated_analyses(
        self, query: AnalysesRequest
    ) -> tuple[list[Analysis], int]:
        analyses: Query = self.get_analyses_query_by_workflow(query.workflow)
        analyses = self.get_filtered_analyses(analyses=analyses, query=query)
        analyses = self.get_analyses_query_by_search(analyses=analyses, search_term=query.search)
        analyses = self.sort_analyses(analyses=analyses, query=query)

        if not query.search:
            analyses = self.get_visible_analyses(analyses)

        total_analyses_count: int = analyses.count()
        query_page: Query = self.paginate_analyses(analyses=analyses, query=query)
        return query_page.all(), total_analyses_count
