from datetime import datetime
from typing import Callable

from sqlalchemy import desc
from sqlalchemy.orm import Query

from trailblazer.constants import JobType, TrailblazerStatus
from trailblazer.dto.analyses_request import AnalysesRequest
from trailblazer.store.base import BaseHandler
from trailblazer.store.filters.analyses_filters import (
    AnalysisFilter,
    apply_analysis_filter,
)
from trailblazer.store.filters.job_filters import JobFilter, apply_job_filters
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Analysis, Job, User


class ReadHandler(BaseHandler):
    """Class for reading items in the database."""

    def get_failed_jobs_stats(self, since_when: datetime = None) -> list[dict]:
        """Return the number of failed jobs per category (name)."""
        return self.get_nr_jobs_with_status_per_category(
            status=TrailblazerStatus.FAILED, since_when=since_when
        )

    def get_nr_jobs_with_status_per_category(
        self, status: str, since_when: datetime = None
    ) -> list[dict[str, str | int]]:
        """Return the number of jobs with status per category (name)."""
        filter_map: dict[Callable, str | bool | None] = {
            JobFilter.BY_STATUS: status,
            JobFilter.BY_SINCE_WHEN: since_when,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        categories = apply_job_filters(
            filters=filter_functions,
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
            AnalysisFilter.BY_COMMENT: comment,
            AnalysisFilter.BY_BEFORE_STARTED_AT: before,
            AnalysisFilter.BY_STATUS: status,
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
                AnalysisFilter.BY_CASE_ID,
                AnalysisFilter.BY_STARTED_AT,
                AnalysisFilter.BY_STATUS,
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
                filter_functions=[AnalysisFilter.BY_CASE_ID],
                case_id=case_id,
            )
            .order_by(desc(Analysis.started_at))
            .first()
        )

    def get_analyses_for_case(self, case_id: str) -> list[Analysis] | None:
        """Return all analyses for a case."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[AnalysisFilter.BY_CASE_ID],
            case_id=case_id,
        ).all()

    def get_analyses_with_statuses(self, statuses: list[str]) -> list[Analysis] | None:
        """Get analyses by statuses."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[AnalysisFilter.BY_STATUSES],
            statuses=statuses,
        ).all()

    def get_analysis_with_id(self, analysis_id: int) -> Analysis | None:
        """Get a single analysis by id."""
        return apply_analysis_filter(
            analyses=self.get_query(table=Analysis),
            filter_functions=[AnalysisFilter.BY_ENTRY_ID],
            analysis_id=analysis_id,
        ).first()

    def get_user(
        self,
        email: str = None,
        exclude_archived: bool = True,
    ) -> User:
        """Return user from the database."""
        filter_map: dict[Callable, str | bool | None] = {
            UserFilter.BY_CONTAINS_EMAIL: email,
            UserFilter.BY_IS_NOT_ARCHIVED: exclude_archived,
        }
        filter_functions: list[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        return apply_user_filter(
            filter_functions=filter_functions,
            users=self.get_query(table=User),
            email=email,
        ).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return apply_user_filter(
            filter_functions=[UserFilter.BY_ID],
            users=self.get_query(table=User),
            id=user_id,
        ).first()

    def get_users(
        self,
        name: str = None,
        email: str = None,
        exclude_archived: bool = True,
    ) -> list[User]:
        """Return users from the database."""
        filter_map: dict[Callable, str | bool | None] = {
            UserFilter.BY_CONTAINS_EMAIL: email,
            UserFilter.BY_CONTAINS_NAME: name,
            UserFilter.BY_IS_NOT_ARCHIVED: exclude_archived,
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

    def get_latest_failed_job_for_analysis(self, analysis_id: str) -> Job | None:
        filters: list[Callable] = [
            JobFilter.BY_ANALYSIS_ID,
            JobFilter.BY_STATUS,
            JobFilter.SORT_BY_STARTED_AT,
        ]
        return apply_job_filters(
            filters=filters,
            jobs=self.get_query(Job),
            analysis_id=analysis_id,
            status=TrailblazerStatus.FAILED,
        ).first()

    def get_ongoing_upload_jobs(self) -> list[Job]:
        ongoing_statuses: list[str] = list(TrailblazerStatus.ongoing_statuses())
        return apply_job_filters(
            filters=[JobFilter.BY_TYPE, JobFilter.BY_STATUSES],
            jobs=self.get_query(Job),
            job_type=JobType.UPLOAD,
            statuses=ongoing_statuses,
        ).all()

    def get_job_by_id(self, job_id: int) -> Job | None:
        return apply_job_filters(
            filters=[JobFilter.BY_ID],
            jobs=self.get_query(Job),
            job_id=job_id,
        ).first()

    def get_analyses_by_order_id(self, order_id: int) -> list[Analysis]:
        return apply_analysis_filter(
            analyses=self.get_query(Analysis),
            filter_functions=[AnalysisFilter.BY_ORDER_ID],
            order_id=order_id,
        ).all()

    def get_paginated_analyses(self, request: AnalysesRequest) -> tuple[list[Analysis], int]:
        analyses: Query = self._filter_analyses(request)
        total_count: int = analyses.count()
        page: Query = self._paginate_analyses(analyses=analyses, request=request)
        return page.all(), total_count

    def _filter_analyses(self, request: AnalysesRequest) -> Query:
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

    def _paginate_analyses(self, analyses: Query, request: AnalysesRequest) -> Query:
        return apply_analysis_filter(
            filter_functions=[AnalysisFilter.PAGINATION],
            analyses=analyses,
            page=request.page,
            page_size=request.page_size,
        )
