from datetime import datetime
from enum import Enum
from typing import Callable

import sqlalchemy
from sqlalchemy.orm import Query

from trailblazer.constants import TrailblazerStatus
from trailblazer.store.models import Analysis


def filter_analyses_by_comment(analyses: Query, comment: str, **kwargs) -> Query:
    """Filter analyses that contain the string given in 'comment'."""
    return analyses.filter(Analysis.comment.ilike(f"%{comment}%"))


def filter_analyses_by_case_id(analyses: Query, case_id: str, **kwargs) -> Query:
    """Filter analyses by case id."""
    return analyses.filter(Analysis.case_id == case_id)


def filter_analyses_by_entry_id(analyses: Query, analysis_id: int, **kwargs) -> Query:
    """Filter analyses by database entry id."""
    return analyses.filter(Analysis.id == analysis_id)


def filter_analyses_by_is_visible(analyses: Query, **kwargs) -> Query:
    """Filter analyses by case when is visible is true."""
    return analyses.filter(Analysis.is_visible.is_(True))


def filter_analyses_by_search_term(analyses: Query, search_term: str, **kwargs) -> Query:
    """Filter analyses by search term using multiple fields."""
    return analyses.filter(
        sqlalchemy.or_(
            Analysis.case_id.ilike(f"%{search_term}%"),
            Analysis.status.ilike(f"%{search_term}%"),
            Analysis.data_analysis.ilike(f"%{search_term}%"),
            Analysis.comment.ilike(f"%{search_term}%"),
        )
    )


def filter_analyses_by_started_at(analyses: Query, started_at: datetime, **kwargs) -> Query:
    """Filter analyses by when it started."""
    return analyses.filter(Analysis.started_at == started_at)


def filter_analyses_by_before_started_at(analyses: Query, started_at: datetime, **kwargs) -> Query:
    """Filter analyses by ifK it started before the supplied date."""
    return analyses.filter(Analysis.started_at < started_at)


def filter_analyses_by_status(analyses: Query, status: TrailblazerStatus, **kwargs) -> Query:
    """Filter analyses by status."""
    return analyses.filter(Analysis.status == status)


def filter_analyses_by_statuses(analyses: Query, statuses: list[str], **kwargs) -> Query:
    """Filter analyses by statuses."""
    return analyses.filter(Analysis.status.in_(statuses))


def filter_analyses_by_priorites(analyses: Query, priorities: list[str], **kwargs) -> Query:
    """Filter analyses by priorities."""
    return analyses.filter(Analysis.priority.in_(priorities))


def filter_analyses_by_types(analyses: Query, types: list[str], **kwargs) -> Query:
    """Filter analyses by types."""
    return analyses.filter(Analysis.type.in_(types))


def filter_analyses_by_empty_comment(analyses: Query, **kwargs) -> Query:
    return analyses.filter(sqlalchemy.or_(Analysis.comment.is_(None), Analysis.comment == ""))


class AnalysisFilter(Enum):
    """Define Analysis filter functions."""

    FILTER_BY_BEFORE_STARTED_AT: Callable = filter_analyses_by_before_started_at
    FILTER_BY_CASE_ID: Callable = filter_analyses_by_case_id
    FILTER_BY_COMMENT: Callable = filter_analyses_by_comment
    FILTER_BY_EMPTY_COMMENT: Callable = filter_analyses_by_empty_comment
    FILTER_BY_ENTRY_ID: Callable = filter_analyses_by_entry_id
    FILTER_BY_SEARCH_TERM: Callable = filter_analyses_by_search_term
    FILTER_BY_IS_VISIBLE: Callable = filter_analyses_by_is_visible
    FILTER_BY_PRIORITIES: Callable = filter_analyses_by_priorites
    FILTER_BY_STARTED_AT: Callable = filter_analyses_by_started_at
    FILTER_BY_STATUS: Callable = filter_analyses_by_status
    FILTER_BY_STATUSES: Callable = filter_analyses_by_statuses
    FILTER_BY_TYPES: Callable = filter_analyses_by_types


def apply_analysis_filter(
    analyses: Query,
    filter_functions: list[Callable],
    analysis_id: int | None = None,
    case_id: str | None = None,
    search_term: str | None = None,
    comment: str | None = None,
    started_at: datetime | None = None,
    status: str | None = None,
    statuses: list[str] | None = None,
    priorities: list[str] | None = None,
    types: list[str] | None = None,
) -> Query:
    """Apply filtering functions and return filtered results."""
    if statuses is None:
        statuses = []
    for function in filter_functions:
        analyses: Query = function(
            analyses=analyses,
            analysis_id=analysis_id,
            case_id=case_id,
            comment=comment,
            search_term=search_term,
            started_at=started_at,
            status=status,
            statuses=statuses,
            priorities=priorities,
            types=types,
        )
    return analyses
