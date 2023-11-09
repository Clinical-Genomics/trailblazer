from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Type, Union

from sqlalchemy import func
from sqlalchemy.orm import Query

from trailblazer.store.filters.analyses_filters import (
    AnalysisFilter,
    apply_analysis_filter,
)
from trailblazer.store.models import Analysis, Job, Model


@dataclass
class BaseHandler:
    """All models in one base class."""

    def __init__(self):
        pass

    def setup(self):
        self.create_all()

    def get_query(self, table: Type[Model]) -> Query:
        """Return a query for the given table."""
        return self.query(table)

    def get_job_query_with_name_and_count_labels(self) -> Query:
        """Return a Job query with a name label and a count with a label."""
        return self.session.query(
            Job.name.label("name"),
            func.count(Job.id).label("count"),
        )

    def get_analyses_query_by_search_term_and_is_visible(
        self,
        search_term: Optional[str] = None,
        is_visible: bool = False,
    ) -> Query:
        """Return analyses by search term qnd is visible."""
        if not search_term and not is_visible:
            return
        filter_map: Dict[Callable, Optional[Union[str, bool]]] = {
            AnalysisFilter.FILTER_BY_IS_VISIBLE: is_visible,
            AnalysisFilter.FILTER_BY_SEARCH_TERM: search_term,
        }
        filter_functions: List[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        analyses: Query = apply_analysis_filter(
            filter_functions=filter_functions,
            analyses=self.get_query(table=Analysis),
            search_term=search_term,
        )
        return analyses.order_by(Analysis.started_at.desc())
