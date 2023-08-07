from datetime import datetime
from typing import Callable, List, Dict, Union, Optional

from trailblazer.store.base import BaseHandler_2
from trailblazer.store.filters.job_filters import JobFilter, apply_job_filter
from trailblazer.store.filters.analyses_filters import AnalysisFilter, apply_analysis_filter
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import Job, User, Analysis


class ReadHandler(BaseHandler_2):
    """Class for reading items in the database."""

    def get_nr_jobs_with_status_per_category(
        self, status: str, since_when: datetime = None
    ) -> List[Dict[str, Union[str, int]]]:
        """Return the number of jobs with status per category (name)."""
        filter_map: Dict[Callable, Optional[Union[str, bool]]] = {
            JobFilter.FILTER_BY_STATUS: status,
            JobFilter.FILTER_BY_SINCE_WHEN: since_when,
        }
        filter_functions: List[Callable] = [
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

    def get_analysis_with_id(self, analysis_id: int) -> Optional[Analysis]:
        """Get a single analysis by id."""
        return apply_analysis_filter(
            filter_functions=[AnalysisFilter.FILTER_BY_ID],
            analyses=self.get_query(table=Analysis),
            analysis_id=analysis_id,
        ).first()

    def get_user(
        self,
        email: str = None,
        exclude_archived: bool = True,
    ) -> User:
        """Return user from the database."""
        filter_map: Dict[Callable, Optional[Union[str, bool]]] = {
            UserFilter.FILTER_BY_CONTAINS_EMAIL: email,
            UserFilter.FILTER_BY_IS_NOT_ARCHIVED: exclude_archived,
        }
        filter_functions: List[Callable] = [
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
    ) -> List[User]:
        """Return users from the database."""
        filter_map: Dict[Callable, Optional[Union[str, bool]]] = {
            UserFilter.FILTER_BY_CONTAINS_EMAIL: email,
            UserFilter.FILTER_BY_CONTAINS_NAME: name,
            UserFilter.FILTER_BY_IS_NOT_ARCHIVED: exclude_archived,
        }
        filter_functions: List[Callable] = [
            function for function, supplied_arg in filter_map.items() if supplied_arg
        ]
        return apply_user_filter(
            filter_functions=filter_functions,
            users=self.get_query(table=User),
            email=email,
            name=name,
        ).all()
