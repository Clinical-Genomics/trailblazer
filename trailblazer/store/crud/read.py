from datetime import datetime
from typing import Callable

from sqlalchemy import desc
from sqlalchemy.orm import Query

from trailblazer.constants import TrailblazerStatus
from trailblazer.store.base import BaseHandler
from trailblazer.store.filters.analyses_filters import (
    AnalysisFilter,
    apply_analysis_filter,
)
from trailblazer.store.filters.job_filters import JobFilter, apply_job_filter
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, Job, User


class ReadHandler(BaseHandler):
    """Class for reading items in the database."""

    def get_nr_jobs_with_status_per_category(
        self, status: str, since_when: datetime = None
    ) -> list[dict[str, str | int]]:
        """Return the number of jobs with status per category (name)."""
        filter_map: dict[Callable, str | bool | None] = {
            JobFilter.FILTER_BY_STATUS: status,
            JobFilter.FILTER_BY_SINCE_WHEN: since_when,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        categories = apply_job_filter(
            filter_functions=filter_functions,
            jobs=self.get_job_query_with_name_and_count_labels(),
            since_when=since_when,
            status=status,
        )
        categories = categories.group_by(Job.name).all()
        return [{"name": category.name, "count": category.count} for category in categories]

    def get_analyses_by_status_started_at_and_comment(
        self,
        before: datetime | None = None,
        comment: str | None = None,
        status: str | None = None,
    ) -> list[Analysis] | None:
        """Return analyses meeting supplied arguments."""
        if not before and not comment and not status:
            return
        filter_map: dict[Callable, str | datetime | TrailblazerStatus | None] = {
            AnalysisFilter.FILTER_BY_COMMENT: comment,
            AnalysisFilter.FILTER_BY_BEFORE_STARTED_AT: before,
            AnalysisFilter.FILTER_BY_STATUS: status,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        analyses: Query = apply_analysis_filter(
            filter_functions=filter_functions,
            analyses=self.get_query(table=Analysis),
            comment=comment,
            started_at=before,
            status=status,
        )
        return analyses.order_by(desc(Analysis.started_at)).all()

    def get_analysis(self, case_id: str, started_at: datetime, status: str) -> Analysis | None:
        """Return the latest analysis for supplied parameters."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[
                AnalysisFilter.FILTER_BY_CASE_ID,
                AnalysisFilter.FILTER_BY_STARTED_AT,
                AnalysisFilter.FILTER_BY_STATUS,
            ],
            case_id=case_id,
            started_at=started_at,
            status=status,
        ).first()

    def get_latest_analysis_for_case(self, case_id: str) -> Analysis | None:
        """Return the latest analysis for a case."""
        return (
            apply_analysis_filter(
                analyses=self.get_query(table=Analysis),
                filter_functions=[
                    AnalysisFilter.FILTER_BY_CASE_ID,
                ],
                case_id=case_id,
            )
            .order_by(desc(Analysis.started_at))
            .first()
        )

    def get_analyses_for_case(self, case_id: str) -> list[Analysis] | None:
        """Return all analyses for a case."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[
                AnalysisFilter.FILTER_BY_CASE_ID,
            ],
            case_id=case_id,
        ).all()

    def get_analyses_with_statuses(self, statuses: list[str]) -> list[Analysis] | None:
        """Get analyses by statuses."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[AnalysisFilter.FILTER_BY_STATUSES],
            statuses=statuses,
        ).all()

    def get_analysis_with_id(self, analysis_id: int) -> Analysis | None:
        """Get a single analysis by id."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[AnalysisFilter.FILTER_BY_ENTRY_ID],
            analysis_id=analysis_id,
        ).first()

    def get_user(
        self,
        email: str = None,
        exclude_archived: bool = True,
    ) -> User:
        """Return user from the database."""
        filter_map: dict[Callable, str | bool | None] = {
            UserFilter.FILTER_BY_CONTAINS_EMAIL: email,
            UserFilter.FILTER_BY_IS_NOT_ARCHIVED: exclude_archived,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        return apply_user_filter(
            filter_functions=filter_functions,
            users=self.get_query(table=User),
            email=email,
        ).first()

    def get_users(
        self,
        name: str = None,
        email: str = None,
        exclude_archived: bool = True,
    ) -> list[User]:
        """Return users from the database."""
        filter_map: dict[Callable, str | bool | None] = {
            UserFilter.FILTER_BY_CONTAINS_EMAIL: email,
            UserFilter.FILTER_BY_CONTAINS_NAME: name,
            UserFilter.FILTER_BY_IS_NOT_ARCHIVED: exclude_archived,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        return apply_user_filter(
            filter_functions=filter_functions,
            users=self.get_query(table=User),
            email=email,
            name=name,
        ).all()
