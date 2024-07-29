from datetime import datetime
from enum import Enum
from typing import Callable

import sqlalchemy
from sqlalchemy import Subquery, func, select
from sqlalchemy.orm import Query

from trailblazer.constants import TrailblazerStatus, Workflow
from trailblazer.dto.analyses_request import AnalysisSortField
from trailblazer.dto.common import SortOrder
from trailblazer.store.database import get_session
from trailblazer.store.models import Analysis


def filter_analyses_by_comment(analyses: Query, comment: str, **kwargs) -> Query:
    """Filter analyses that contain the string given in 'comment'."""
    return analyses.filter(Analysis.comment.ilike(f"%{comment}%"))


def filter_analyses_by_case_id(analyses: Query, case_id: str | None, **kwargs) -> Query:
    """Filter analyses by case id."""
    if case_id is None:
        return analyses
    return analyses.filter(Analysis.case_id == case_id)


def filter_analyses_by_entry_id(analyses: Query, analysis_id: int, **kwargs) -> Query:
    """Filter analyses by database entry id."""
    return analyses.filter(Analysis.id == analysis_id)


def filter_analyses_by_is_visible(analyses: Query, show_hidden: bool | None, **kwargs) -> Query:
    return analyses if show_hidden else analyses.filter(Analysis.is_visible.is_(True))


def filter_analyses_by_order_id(analyses: Query, order_id: int | None, **kwargs) -> Query:
    if order_id is None:
        return analyses
    return analyses.filter(Analysis.order_id == order_id)


def filter_analyses_by_search_term(analyses: Query, search_term: str | None, **kwargs) -> Query:
    """Filter analyses by search term using multiple fields."""
    if not search_term:
        return analyses
    return analyses.filter(
        sqlalchemy.or_(
            Analysis.case_id.ilike(f"%{search_term}%"),
            Analysis.status.ilike(f"%{search_term}%"),
            Analysis.workflow.ilike(f"%{search_term}%"),
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


def filter_analyses_by_statuses(analyses: Query, statuses: list[str] | None, **kwargs) -> Query:
    return analyses.filter(Analysis.status.in_(statuses)) if statuses else analyses


def filter_analyses_by_priorites(analyses: Query, priorities: list[str] | None, **kwargs) -> Query:
    return analyses.filter(Analysis.priority.in_(priorities)) if priorities else analyses


def filter_analyses_by_types(analyses: Query, types: list[str] | None, **kwargs) -> Query:
    return analyses.filter(Analysis.type.in_(types)) if types else analyses


def filter_analyses_by_has_comment(analyses: Query, has_comment: bool | None, **kwargs) -> Query:
    if has_comment is None:
        return analyses
    if has_comment:
        return analyses.filter(
            sqlalchemy.and_(Analysis.comment.isnot(None), Analysis.comment != "")
        )
    return analyses.filter(sqlalchemy.or_(Analysis.comment.is_(None), Analysis.comment == ""))


def filter_analyses_by_delivered(analyses: Query, delivered: bool | None, **kwargs) -> Query:
    if delivered is True:
        return analyses.filter(Analysis.delivery != None)
    elif delivered is False:
        return analyses.filter(Analysis.delivery == None)
    return analyses


def filter_analyses_by_workflow(analyses: Query, workflow: Workflow, **kwargs) -> Query:
    """Filter analyses by workflow."""
    balsamic_workflow: str = Workflow.BALSAMIC.lower()
    if workflow == balsamic_workflow:
        analyses = analyses.filter(Analysis.workflow.startswith(balsamic_workflow))
    elif workflow:
        analyses = analyses.filter(Analysis.workflow == workflow)
    return analyses


def filter_analyses_by_latest_per_case(analyses: Query, **kwargs) -> Query:
    """Return only the latest analyses per case.

    Constructs a query which reads as:
        SELECT
            *
        FROM
            Analysis
        JOIN
            (SELECT
                case_id, MAX(started_at) started_at
            FROM
                analyses
            GROUP BY
                case_id) latest_started_analyses
        USING (case_id, started_at)
    """

    provided_analyses = analyses.subquery()
    session = get_session()
    latest_date_per_case: Subquery = (
        session.query(
            provided_analyses.columns.case_id,
            func.max(provided_analyses.columns.started_at).label("max_started_at"),
        )
        .group_by(provided_analyses.columns.case_id)
        .subquery()
    )
    latest_analysis_per_case: Query = analyses.join(
        latest_date_per_case,
        (Analysis.case_id == latest_date_per_case.c.case_id)
        & (Analysis.started_at == latest_date_per_case.c.max_started_at),
    )

    return latest_analysis_per_case


def sort_analyses(
    analyses: Query, sort_field: AnalysisSortField, sort_order: SortOrder, **kwargs
) -> Query:
    if not sort_field or not sort_order:
        return analyses
    column = getattr(Analysis, sort_field)
    if sort_order == SortOrder.ASC:
        return analyses.order_by(sqlalchemy.asc(column))
    return analyses.order_by(sqlalchemy.desc(column))


def paginate_analyses(analyses: Query, page: int, page_size: int, **kwargs) -> Query:
    if not page or not page_size:
        return analyses
    return analyses.limit(page_size).offset((page - 1) * page_size)


def exclude_rsync_analyses(analyses: Query, **kwargs) -> Query:
    return analyses.filter(Analysis.workflow != Workflow.RSYNC)


def get_not_uploaded_analyses(analyses: Query, **kwargs) -> Query:
    return analyses.filter(Analysis.uploaded_at == None)


def get_completed_analyses(analyses: Query, **kwargs) -> Query:
    return analyses.filter(Analysis.status == TrailblazerStatus.COMPLETED)


class AnalysisFilter(Enum):
    """Define Analysis filter functions."""

    BY_BEFORE_STARTED_AT: Callable = filter_analyses_by_before_started_at
    BY_CASE_ID: Callable = filter_analyses_by_case_id
    BY_COMMENT: Callable = filter_analyses_by_comment
    BY_HAS_COMMENT: Callable = filter_analyses_by_has_comment
    BY_ENTRY_ID: Callable = filter_analyses_by_entry_id
    BY_SEARCH_TERM: Callable = filter_analyses_by_search_term
    BY_IS_VISIBLE: Callable = filter_analyses_by_is_visible
    BY_ORDER_ID: Callable = filter_analyses_by_order_id
    BY_PRIORITIES: Callable = filter_analyses_by_priorites
    BY_STARTED_AT: Callable = filter_analyses_by_started_at
    BY_STATUS: Callable = filter_analyses_by_status
    BY_STATUSES: Callable = filter_analyses_by_statuses
    BY_TYPES: Callable = filter_analyses_by_types
    BY_DELIVERED: Callable = filter_analyses_by_delivered
    BY_NOT_UPLOADED: Callable = get_not_uploaded_analyses
    BY_COMPLETED: Callable = get_completed_analyses
    BY_WORKFLOW: Callable = filter_analyses_by_workflow
    BY_LATEST_PER_CASE: Callable = filter_analyses_by_latest_per_case
    EXCLUDE_RSYNC: Callable = exclude_rsync_analyses
    SORTING: Callable = sort_analyses
    PAGINATION: Callable = paginate_analyses


def apply_analysis_filter(
    analyses: Query,
    filter_functions: list[Callable],
    analysis_id: int | None = None,
    case_id: str | None = None,
    comment: str | None = None,
    order_id: int | None = None,
    priorities: list[str] | None = None,
    search_term: str | None = None,
    started_at: datetime | None = None,
    status: str | None = None,
    statuses: list[str] | None = None,
    types: list[str] | None = None,
    delivered: bool | None = None,
    workflow: str | None = None,
    has_comment: bool | None = None,
    show_hidden: bool | None = None,
    page: int | None = None,
    page_size: int | None = None,
    sort_field: AnalysisSortField | None = None,
    sort_order: SortOrder | None = None,
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
            order_id=order_id,
            priorities=priorities,
            search_term=search_term,
            started_at=started_at,
            status=status,
            statuses=statuses,
            types=types,
            delivered=delivered,
            workflow=workflow,
            has_comment=has_comment,
            show_hidden=show_hidden,
            page=page,
            page_size=page_size,
            sort_field=sort_field,
            sort_order=sort_order,
        )
    return analyses
