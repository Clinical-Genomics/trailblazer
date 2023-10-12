from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional

from sqlalchemy.orm import Query

from trailblazer.constants import TrailblazerStatus
from trailblazer.store.models import Analysis


def filter_analyses_by_id(analyses: Query, analysis_id: int, **kwargs) -> Query:
    """Filter analyses by database entry id."""
    return analyses.filter(Analysis.id == analysis_id)


def filter_analyses_by_case_id(analyses: Query, case_id: str, **kwargs) -> Query:
    """Filter analyses by case id."""
    return analyses.filter(Analysis.family == case_id)


def filter_analyses_by_started_at(analyses: Query, started_at: datetime, **kwargs) -> Query:
    """Filter analyses by when it started."""
    return analyses.filter(Analysis.started_at == started_at)


def filter_analyses_by_status(analyses: Query, status: TrailblazerStatus, **kwargs) -> Query:
    """Filter analyses by status."""
    return analyses.filter(Analysis.status == status)


def filter_analyses_by_statuses(analyses: Query, statuses: List[str], **kwargs) -> Query:
    """Filter analyses by statuses."""
    return analyses.filter(Analysis.status.in_(statuses))


class AnalysisFilter(Enum):
    """Define Analysis filter functions."""

    FILTER_BY_ID: Callable = filter_analyses_by_id
    FILTER_BY_CASE_ID: Callable = filter_analyses_by_case_id
    FILTER_BY_STARTED_AT: Callable = filter_analyses_by_started_at
    FILTER_BY_STATUS: Callable = filter_analyses_by_status
    FILTER_BY_STATUSES: Callable = filter_analyses_by_statuses


def apply_analysis_filter(
    analyses: Query,
    filter_functions: List[Callable],
    analysis_id: Optional[int] = None,
    case_id: Optional[str] = None,
    started_at: Optional[datetime] = None,
    status: Optional[str] = None,
    statuses: Optional[List[str]] = [],
) -> Query:
    """Apply filtering functions and return filtered results."""
    for function in filter_functions:
        analyses: Query = function(
            analyses=analyses,
            analysis_id=analysis_id,
            case_id=case_id,
            started_at=started_at,
            status=status,
            statuses=statuses,
        )
    return analyses
