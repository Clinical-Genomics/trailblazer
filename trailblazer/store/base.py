from dataclasses import dataclass
from typing import Callable, Type

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Query, Session
from trailblazer.dto.analysis_request import AnalysisRequest

from trailblazer.store.database import get_session
from trailblazer.store.filters.analyses_filters import (
    AnalysisFilter,
    apply_analysis_filter,
)
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

    def get_analyses_query_by_search(
        self,
        search_term: str | None = "",
        is_visible: bool = False,
    ) -> Query:
        """Return analyses by search term qnd is visible."""
        filter_map: dict[Callable, str | bool] | None = {
            AnalysisFilter.FILTER_BY_IS_VISIBLE: is_visible,
            AnalysisFilter.FILTER_BY_SEARCH_TERM: search_term,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        analyses: Query = apply_analysis_filter(
            filter_functions=filter_functions,
            analyses=self.get_query(Analysis),
            search_term=search_term,
        )
        return analyses

    def filter(self, analyses: Query, query: AnalysisRequest) -> Query:
        if query.status:
            analyses = analyses.filter(Analysis.status.in_(query.status))
        if query.priority:
            analyses = analyses.filter(Analysis.priority.in_(query.priority))
        if query.type:
            analyses = analyses.filter(Analysis.type.in_(query.type))
        if query.comment:
            analyses = analyses.filter(or_(Analysis.comment.is_(None), Analysis.comment == ""))
        return analyses

    def sort(self, analyses: Query, query: AnalysisRequest) -> Query:
        if query.sort_field:
            column = getattr(Analysis, query.sort_field)
            order_function = asc if query.sort_order == "asc" else desc
            analyses = analyses.order_by(order_function(column))
        return analyses

    def paginate(self, analyses: Query, query: AnalysisRequest) -> Query:
        return analyses.limit(query.page_size).offset((query.page - 1) * query.page_size)

    def get_filtered_sorted_paginated_analyses(
        self, query: AnalysisRequest
    ) -> tuple[list[Analysis], int]:
        analyses: Query = self.get_analyses_query_by_search(query.search)

        analyses = self.filter(analyses, query)
        analyses = self.sort(analyses, query)
        total: int = analyses.count()
        query_page = self.paginate(analyses, query)
        return query_page.all(), total
