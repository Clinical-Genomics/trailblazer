from datetime import date
from typing import Callable, List, Dict, Union, Optional
import sqlalchemy as sqa

from trailblazer.store.base import BaseHandler_2
from trailblazer.store.filters.user_filters import UserFilter, apply_user_filter
from trailblazer.store.models import User


class ReadHandler(BaseHandler_2):
    """Class for reading items in the database."""

    def get_nr_of_failed_jobs_per_category(
        self, since_when: date = None
    ) -> List[Dict[str, Union[str, int]]]:
        """Return the number of failed jobs per category (name)."""

        categories = self.session.query(
            self.Job.name.label("name"),
            sqa.func.count(self.Job.id).label("count"),
        ).filter(self.Job.status == "failed")

        if since_when:
            categories = categories.filter(self.Job.started_at > since_when)

        categories = categories.group_by(self.Job.name).all()

        return [{"name": category.name, "count": category.count} for category in categories]

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
