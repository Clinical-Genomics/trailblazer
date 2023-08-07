from enum import Enum
from typing import Callable, List, Optional

from sqlalchemy.orm import Query

from trailblazer.store.models import Analysis


def filter_analyses_by_id(analyses: Query, analysis_id: int, **kwargs) -> Query:
    """Filter analyses by database entry id."""
    return analyses.filter(Analysis.id == analysis_id)


class AnalysisFilter(Enum):
    """Define Analysis filter functions."""

    FILTER_BY_ID: Callable = filter_analyses_by_id


def apply_analysis_filter(
    analyses: Query,
    filter_functions: List[Callable],
    analysis_id: Optional[int] = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filter_functions:
        analyses: Query = function(
            analyses=analyses,
            analysis_id=analysis_id,
        )
    return analyses
