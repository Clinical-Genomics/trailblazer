from dataclasses import dataclass
from typing import Type

from sqlalchemy import asc, desc, func, or_
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

    def get_analyses_query_by_search(self, analyses: Query, search_term: str) -> Query:
        """Return analyses by search term."""
        if search_term:
            analyses: Query = apply_analysis_filter(
                filter_functions=[AnalysisFilter.FILTER_BY_SEARCH_TERM],
                analyses=analyses,
                search_term=search_term,
            )
        return analyses

    def get_analyses_query_by_pipeline(self, pipeline: str) -> Query:
        """Return analyses by pipeline."""
        analyses: Query = self.get_query(Analysis)
        # Group existing variants of balsamic
        if pipeline == "balsamic":
            analyses = analyses.filter(Analysis.data_analysis.like("%balsamic%"))
        if pipeline:
            analyses = analyses.filter(Analysis.data_analysis == pipeline)
        return analyses.filter(Analysis.is_visible.is_(True))

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
        analyses: Query = self.get_analyses_query_by_pipeline(query.pipeline)
        analyses = self.filter(analyses, query)
        analyses = self.get_analyses_query_by_search(analyses=analyses, search_term=query.search)
        analyses = self.sort(analyses=analyses, query=query)
        total: int = analyses.count()
        query_page = self.paginate(analyses, query)
        return query_page.all(), total
